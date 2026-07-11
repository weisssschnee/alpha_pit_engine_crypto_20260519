from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.anti_collapse import AdmissionPolicy, CandidateEnvelope, admit
from alphafactory_crypto.b1s_canary import (
    BBO_LANES, MAIN_LANES, CandidateSpec, FrozenPanel, behaviour_cluster_identity,
    effective_cluster_count, evidence, generate_proposals, global_top_k, materialize,
    rank_weights, stable_id, stratified_strict_selection, strict_evaluate, validate_contract,
)


CONFIG = REPO / "config" / "crypto_b1s_canary_v1.json"
ACCESS_POLICY = REPO / "config" / "crypto_evaluation_access_policy_v1.json"
ADMISSION_CONTRACT = REPO / "config" / "crypto_anti_collapse_admission_v1.json"
BENCHMARK_CONTRACT = REPO / "config" / "crypto_challenger_harness_v1.json"
LANE_CONTRACT = REPO / "config" / "crypto_nextgen_dark_lanes_v1.json"
MODULE = REPO / "alphafactory_crypto" / "b1s_canary.py"
OUTPUT_ROOT = REPO / "runtime" / "b1s_canary_20260711"
FROZEN_MANIFEST = OUTPUT_ROOT / "b1s_frozen_run_manifest.json"
RUN_MANIFEST = OUTPUT_ROOT / "b1s_canary_manifest.json"
FAILURE_MANIFEST = OUTPUT_ROOT / "b1s_canary_failure.json"
FEATURE_ROOT = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v3_patch_age_20260613")
BBO_DATA = Path("G:/AlphaFactory_CryptoData/gold/features/nextgen_dark_bookticker_core12_v1/bookticker_core12_1h_top_of_book_state.parquet")
BOOKTICKER_MANIFEST = REPO / "runtime" / "nextgen_dark_20260711" / "pc1_bookticker_top_of_book_manifest.json"
CORE12 = (
    "ADAUSDT", "AVAXUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "DOGEUSDT",
    "ETHUSDT", "LINKUSDT", "LTCUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT",
)
MAIN_COLUMNS = (
    "symbol", "timestamp", "feature_available_time", "trade_close", "trade_quote_volume", "trade_count",
    "funding_rate", "mark_trade_basis_bps", "mark_index_basis_bps", "open_interest_value_last",
    "open_interest_value_mean", "kline_taker_buy_quote_share", "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last", "global_long_short_account_ratio_last",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def freeze() -> dict[str, Any]:
    config = load_json(CONFIG)
    validate_contract(config)
    if git("status", "--porcelain"):
        raise RuntimeError("freeze requires a clean committed implementation worktree")
    feature_files = [FEATURE_ROOT / f"symbol={symbol}" / "part.parquet" for symbol in CORE12]
    missing = [str(path) for path in feature_files if not path.exists()]
    if missing or not BBO_DATA.exists():
        raise FileNotFoundError(f"frozen panel input missing: {missing or BBO_DATA}")
    file_hashes = {relative(path): sha256_file(path) for path in feature_files}
    file_hashes[relative(BBO_DATA)] = sha256_file(BBO_DATA)
    contract_paths = [CONFIG, ACCESS_POLICY, ADMISSION_CONTRACT, BENCHMARK_CONTRACT, LANE_CONTRACT, MODULE, Path(__file__)]
    contracts = {relative(path): sha256_file(path) for path in contract_paths}
    payload: dict[str, Any] = {
        "experiment_id": "20260711_b1s_canary_001",
        "objective": "compare fixed stratified anti-collapse admission with equal-budget global-top-K inside development-only main and isolated BBO panels",
        "status": "FROZEN_NOT_STARTED",
        "mode": "CONTROLLED_CANARY_ONLY",
        "repo_sha": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "input_files_sha256": file_hashes,
        "data_release_sha256": sha256_payload(file_hashes),
        "contracts_sha256": contracts,
        "contract_bundle_sha256": sha256_payload(contracts),
        "capability_matrix": {
            "main_enabled": list(MAIN_LANES), "bbo_enabled": list(BBO_LANES),
            "liquidation": "DISABLED_NO_APPROVED_SOURCE", "force_order": "DISABLED_NO_APPROVED_SOURCE",
            "multi_level_depth": "DISABLED_NO_APPROVED_SOURCE", "bookticker": "SCOPED_BBO_QUALIFIED",
        },
        "panel_contracts": config["panels"],
        "lane_specs": {"main": list(MAIN_LANES), "bbo_micro": list(BBO_LANES)},
        "proposal_evaluation_budget": config["budget_per_lane"],
        "global_top_k_control": config["global_top_k_control"],
        "reward_contract": config["reward_contract"],
        "admission_contract": config["admission_contract"],
        "candidate_contract": config["candidate_contract"],
        "benchmark_contract": config["benchmark_contract"],
        "seeds": config["budget_per_lane"]["fixed_seeds"],
        "adaptive_challenger": config["adaptive_challenger"],
        "estimated_cost_time": "5-20 minutes on local workstation; fixed 5120 proposals, 640 logical strict evaluations",
        "commands": {
            "freeze": "python scripts/crypto_b1s_canary.py freeze",
            "run": "python scripts/crypto_b1s_canary.py run",
            "check": "python scripts/crypto_b1s_canary.py check",
        },
        "prohibited": config["prohibited"],
        "continuation": "resume only from this exact repo SHA and hash bundle; never add budget or read non-train epochs",
        "search_started": False,
        "forward_read": False,
        "candidate_promotion": False,
    }
    payload["frozen_manifest_sha256"] = sha256_payload(payload)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    FROZEN_MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "repo_sha": payload["repo_sha"], "manifest_sha256": payload["frozen_manifest_sha256"]}, indent=2))
    return payload


def verify_frozen() -> dict[str, Any]:
    manifest = load_json(FROZEN_MANIFEST)
    recorded = manifest.pop("frozen_manifest_sha256")
    if sha256_payload(manifest) != recorded:
        raise ValueError("frozen B1S manifest hash mismatch")
    manifest["frozen_manifest_sha256"] = recorded
    if git("rev-parse", "HEAD") != manifest["repo_sha"]:
        raise ValueError("repo SHA changed after B1S freeze")
    for raw, expected in manifest["input_files_sha256"].items():
        path = REPO / raw if not Path(raw).is_absolute() else Path(raw)
        if sha256_file(path) != expected:
            raise ValueError(f"B1S data input hash drift: {raw}")
    for raw, expected in manifest["contracts_sha256"].items():
        path = REPO / raw
        if sha256_file(path) != expected:
            raise ValueError(f"B1S contract hash drift: {raw}")
    return manifest


def _pivot(frame: pd.DataFrame, field: str, symbols: tuple[str, ...], timestamps: pd.DatetimeIndex) -> np.ndarray:
    return frame.pivot(index="symbol", columns="timestamp", values=field).reindex(index=symbols, columns=timestamps).to_numpy(dtype=float)


def _rolling(values: np.ndarray, window: int, kind: str) -> np.ndarray:
    roll = pd.DataFrame(values.T).rolling(window, min_periods=max(2, window // 2))
    result = roll.std(ddof=0) if kind == "std" else roll.mean()
    return result.to_numpy(dtype=float).T


def load_main_panel() -> FrozenPanel:
    pieces = []
    for symbol in CORE12:
        path = FEATURE_ROOT / f"symbol={symbol}" / "part.parquet"
        piece = pq.ParquetFile(path).read(columns=list(MAIN_COLUMNS)).to_pandas()
        piece["timestamp"] = pd.to_datetime(piece["timestamp"], utc=True)
        piece["feature_available_time"] = pd.to_datetime(piece["feature_available_time"], utc=True)
        piece = piece[(piece["timestamp"] >= "2024-01-01T00:00:00Z") & (piece["timestamp"] <= "2024-12-31T23:00:00Z")]
        if (piece["feature_available_time"] < piece["timestamp"] + pd.Timedelta(hours=1)).any():
            raise PermissionError("main panel contains an early feature availability time")
        pieces.append(piece)
    frame = pd.concat(pieces, ignore_index=True)
    if frame.duplicated(["symbol", "timestamp"]).any():
        raise ValueError("main panel duplicate coordinates")
    symbols = tuple(sorted(CORE12))
    timestamps = pd.date_range("2024-01-01", "2024-12-31 23:00", freq="h", tz="UTC")
    close = _pivot(frame, "trade_close", symbols, timestamps)
    quote_volume = _pivot(frame, "trade_quote_volume", symbols, timestamps)
    funding = _pivot(frame, "funding_rate", symbols, timestamps)
    basis = _pivot(frame, "mark_trade_basis_bps", symbols, timestamps)
    oi = _pivot(frame, "open_interest_value_last", symbols, timestamps)
    taker_share = _pivot(frame, "kline_taker_buy_quote_share", symbols, timestamps)
    top_account = _pivot(frame, "top_long_short_account_ratio_last", symbols, timestamps)
    top_position = _pivot(frame, "top_long_short_position_ratio_last", symbols, timestamps)
    asset_return = np.full_like(close, np.nan)
    asset_return[:, 1:] = close[:, 1:] / close[:, :-1] - 1.0
    target = np.full_like(close, np.nan)
    target[:, :-2] = close[:, 2:] / close[:, 1:-1] - 1.0
    market = np.nanmedian(asset_return, axis=0, keepdims=True)
    market_broadcast = np.repeat(market, len(symbols), axis=0)
    session_hour = timestamps.hour.to_numpy(dtype=float)
    session_sin = np.repeat(np.sin(2 * np.pi * session_hour / 24.0)[None, :], len(symbols), axis=0)
    session_cos = np.repeat(np.cos(2 * np.pi * session_hour / 24.0)[None, :], len(symbols), axis=0)
    oi_change = np.full_like(oi, np.nan)
    oi_change[:, 1:] = oi[:, 1:] / oi[:, :-1] - 1.0
    funding_change = np.full_like(funding, np.nan)
    funding_change[:, 1:] = funding[:, 1:] - funding[:, :-1]
    fields = {
        "funding": funding, "funding_abs": np.abs(funding), "funding_change": funding_change,
        "basis": basis, "basis_abs": np.abs(basis), "oi": np.log1p(np.clip(oi, 0, None)), "oi_change": oi_change,
        "liquidity": np.log1p(np.clip(quote_volume, 0, None)), "taker": 2.0 * taker_share - 1.0,
        "volatility": _rolling(asset_return, 24, "std"), "positioning": top_position - top_account,
        "session_sin": session_sin, "session_cos": session_cos, "asset_return": asset_return,
        "market_return": market_broadcast, "relative_market_return": asset_return - market_broadcast,
        "cross_confirmation": np.sign(asset_return) * np.sign(market_broadcast),
    }
    panel = FrozenPanel("main", symbols, timestamps, fields, target, "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY")
    panel.validate()
    return panel


def load_bbo_panel(main: FrozenPanel) -> FrozenPanel:
    frame = pd.read_parquet(BBO_DATA, columns=[
        "symbol", "timestamp", "observable_time", "maturity_time", "spread_bps_mean", "bid_qty_mean",
        "ask_qty_mean", "quote_imbalance_mean", "top_of_book_liquidity_state",
    ])
    for column in ("timestamp", "observable_time", "maturity_time"):
        frame[column] = pd.to_datetime(frame[column], utc=True)
    if (frame["observable_time"] != frame["timestamp"] + pd.Timedelta(hours=1)).any():
        raise PermissionError("BBO observable time is not bucket close")
    if (frame["maturity_time"] != frame["observable_time"]).any():
        raise PermissionError("BBO maturity differs from observable time")
    symbols = tuple(sorted(frame["symbol"].unique().tolist()))
    timestamps = pd.date_range("2024-01-01", "2024-02-29 23:00", freq="h", tz="UTC")
    fields = {
        "spread": _pivot(frame, "spread_bps_mean", symbols, timestamps),
        "bid_qty": _pivot(frame, "bid_qty_mean", symbols, timestamps),
        "ask_qty": _pivot(frame, "ask_qty_mean", symbols, timestamps),
        "quote_imbalance": _pivot(frame, "quote_imbalance_mean", symbols, timestamps),
        "top_of_book_liquidity": _pivot(frame, "top_of_book_liquidity_state", symbols, timestamps),
    }
    main_symbol = {symbol: index for index, symbol in enumerate(main.symbols)}
    time_index = main.timestamps.get_indexer(timestamps)
    target = np.vstack([main.target_return[main_symbol[symbol], time_index] for symbol in symbols])
    panel = FrozenPanel("bbo_micro", symbols, timestamps, fields, target, "bucket_start_plus_1h", "bucket_close", "BBO_MICRO_ONLY")
    panel.validate()
    return panel


def _proposal_row(spec: CandidateSpec, ev: Mapping[str, Any], lane_ordinal: int) -> dict[str, Any]:
    potential = stable_id("behaviour-potential", {"op": spec.operator, "window_bucket": min(spec.window, 48), "field": spec.field_a})
    return {
        **asdict_no_error(spec), "lane_ordinal": lane_ordinal,
        "canonical_identity": stable_id("canonical", spec.canonical_program),
        "exact_identity": ev["exact_identity"], "activation_identity": ev["activation_identity"],
        "proxy_score": ev["proxy_score"], "legal": ev["legal"], "failure_reason": ev["failure_reason"],
        "behaviour_potential": potential,
        "feedback_permission": "CANARY_RUNTIME_ONLY_NO_MEMORY_NO_PROMOTION",
    }


def asdict_no_error(spec: CandidateSpec) -> dict[str, Any]:
    return {key: value for key, value in spec.__dict__.items()}


def _evaluate_candidate(
    spec: CandidateSpec,
    panel: FrozenPanel,
    proxy_mask: np.ndarray,
    cache: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    key = (panel.panel_id, spec.canonical_program)
    if key not in cache:
        try:
            ev, _ = evidence(spec, materialize(spec, panel), panel, proxy_mask)
            cache[key] = {
                "exact_identity": ev.exact_identity, "activation_identity": ev.activation_identity,
                "proxy_score": ev.proxy_score, "legal": ev.legal, "failure_reason": ev.failure_reason,
            }
        except Exception as exc:
            cache[key] = {
                "exact_identity": "", "activation_identity": "", "proxy_score": float("-inf"),
                "legal": False, "failure_reason": f"{type(exc).__name__}:{exc}",
            }
    return cache[key]


def _admit_lane(rows: list[dict[str, Any]], config: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    legal = [row for row in rows if row["legal"]]
    representative: dict[str, dict[str, Any]] = {}
    for row in sorted(legal, key=lambda value: (value["lane_ordinal"], value["proposal_id"])):
        representative.setdefault(row["exact_identity"], row)
    envelopes = [CandidateEnvelope(
        row["proposal_id"], row["exact_identity"], row["behaviour_potential"], row["economic_hypothesis"],
        row["parent_identity"], row["family_id"], row["lane_id"], row["lane_ordinal"], True,
        f"b1s/{row['panel_id']}/{row['lane_id']}/runtime", "NONE",
    ) for row in representative.values()]
    admission = config["admission_contract"]
    result = admit(envelopes, AdmissionPolicy(
        64, int(admission["behaviour_potential_quota"]), int(admission["economic_hypothesis_quota"]),
        int(admission["parent_descendant_cap"]), int(admission["family_budget_cap"]),
        int(admission["fresh_budget_floor"]), True,
    ))
    by_id = {row["proposal_id"]: row for row in rows}
    admitted = [by_id[item.candidate_id] for item in result.admitted]
    rejected = [{"proposal_id": candidate_id, "reason": reason} for candidate_id, reason in result.rejected]
    return admitted, rejected


def _strict_row(
    spec: CandidateSpec,
    candidate: Mapping[str, Any],
    panel: FrozenPanel,
    arm: str,
    cache: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    key = (panel.panel_id, candidate["exact_identity"])
    reused = key in cache
    if not reused:
        weights = rank_weights(materialize(spec, panel))
        metrics = strict_evaluate(weights, panel)
        cache[key] = metrics | {"behaviour_cluster": behaviour_cluster_identity(weights, panel.timestamps)}
    result = dict(cache[key])
    return {
        "panel_id": panel.panel_id, "comparison_domain": panel.comparison_domain, "arm": arm,
        "lane_id": candidate["lane_id"], "proposal_id": candidate["proposal_id"],
        "exact_identity": candidate["exact_identity"], "activation_identity": candidate["activation_identity"],
        "behaviour_cluster": result.pop("behaviour_cluster"), "economic_hypothesis": candidate["economic_hypothesis"],
        "proxy_score": candidate["proxy_score"], "strict_cache_reused": reused, **result,
        "candidate_promotion": False, "feedback_persisted": False,
    }


def _cluster_table(strict: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (panel, arm, cluster), group in strict.groupby(["panel_id", "arm", "behaviour_cluster"], sort=True):
        rows.append({
            "panel_id": panel, "arm": arm, "behaviour_cluster": cluster, "strict_rows": len(group),
            "exact_identities": group["exact_identity"].nunique(),
            "economic_hypotheses": group["economic_hypothesis"].nunique(),
            "development_survivors": int(group["development_survivor"].sum()),
        })
    return pd.DataFrame(rows)


def _comparison(strict: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (panel, arm), group in strict.groupby(["panel_id", "arm"], sort=True):
        counts = group["behaviour_cluster"].value_counts()
        total = len(group)
        rows.append({
            "panel_id": panel, "arm": arm, "strict_evaluations": total,
            "canonical_exact_identities": group["exact_identity"].nunique(),
            "activation_identities": group["activation_identity"].nunique(),
            "behaviour_clusters": group["behaviour_cluster"].nunique(),
            "n_eff": effective_cluster_count(group["behaviour_cluster"]),
            "top_1_cluster_share": float(counts.iloc[:1].sum() / total),
            "top_3_cluster_share": float(counts.iloc[:3].sum() / total),
            "economic_hypothesis_coverage": group["economic_hypothesis"].nunique(),
            "new_behaviour_clusters_per_strict_evaluation": float(group["behaviour_cluster"].nunique() / total),
            "development_survivor_count": int(group["development_survivor"].sum()),
            "development_score_median": float(group["development_score"].median()),
            "direct_cross_panel_ranking_performed": False,
        })
    return pd.DataFrame(rows)


def run() -> dict[str, Any]:
    frozen = verify_frozen()
    config = load_json(CONFIG)
    validate_contract(config)
    started = time.perf_counter()
    main = load_main_panel()
    bbo = load_bbo_panel(main)
    panels = {"main": main, "bbo_micro": bbo}
    proxy_masks = {
        "main": np.arange(len(main.timestamps)) % 4 == 0,
        "bbo_micro": np.arange(len(bbo.timestamps)) % 2 == 0,
    }
    candidate_rows: list[dict[str, Any]] = []
    admission_rows: list[dict[str, Any]] = []
    adaptive_rows: list[dict[str, Any]] = []
    lane_runtime: dict[tuple[str, str], float] = {}
    materialization_cache: dict[tuple[str, str], dict[str, Any]] = {}
    spec_by_id: dict[str, CandidateSpec] = {}

    for panel_id, lanes in (("main", MAIN_LANES), ("bbo_micro", BBO_LANES)):
        panel = panels[panel_id]
        for lane in lanes:
            lane_start = time.perf_counter()
            specs: list[CandidateSpec] = []
            if lane == "adaptive_challenger":
                pilot = generate_proposals(panel_id, lane, 1701, 64, adaptive_query_count=64)
                pilot_scores: dict[str, list[float]] = defaultdict(list)
                for index, spec in enumerate(pilot):
                    ev = _evaluate_candidate(spec, panel, proxy_masks[panel_id], materialization_cache)
                    pilot_scores[spec.operator].append(float(ev["proxy_score"]))
                    adaptive_rows.append({
                        "query_ordinal": index, "algorithm": spec.algorithm, "proposal_id": spec.proposal_id,
                        "operator": spec.operator, "development_proxy": ev["proxy_score"],
                        "namespace": config["adaptive_challenger"]["namespace"], "persisted": False,
                    })
                preferred = sorted(
                    pilot_scores,
                    key=lambda op: (-float(np.mean([x for x in pilot_scores[op] if np.isfinite(x)])) if any(np.isfinite(pilot_scores[op])) else float("inf"), op),
                )[0]
                specs.extend(pilot)
                specs.extend(generate_proposals(panel_id, lane, 1701, 192, ordinal_offset=64, preferred_operator=preferred, adaptive_query_count=64))
                specs.extend(generate_proposals(panel_id, lane, 1709, 256, preferred_operator=preferred, adaptive_query_count=0))
            else:
                for seed in (1701, 1709):
                    specs.extend(generate_proposals(panel_id, lane, seed, 256))
            if len(specs) != 512:
                raise ValueError(f"proposal budget drift in {panel_id}/{lane}: {len(specs)}")
            lane_rows = []
            for lane_ordinal, spec in enumerate(specs):
                spec_by_id[spec.proposal_id] = spec
                ev = _evaluate_candidate(spec, panel, proxy_masks[panel_id], materialization_cache)
                row = _proposal_row(spec, ev, lane_ordinal)
                candidate_rows.append(row)
                lane_rows.append(row)
            admitted, rejected = _admit_lane(lane_rows, config)
            for rank, row in enumerate(admitted):
                admission_rows.append({
                    "panel_id": panel_id, "lane_id": lane, "proposal_id": row["proposal_id"],
                    "exact_identity": row["exact_identity"], "admission_rank": rank,
                    "admission_type": "STRATIFIED_ANTI_COLLAPSE", "selected_for_strict": False,
                })
            strict_ids = set(stratified_strict_selection(admitted, 32))
            for row in admission_rows[-len(admitted):]:
                row["selected_for_strict"] = row["proposal_id"] in strict_ids
            lane_runtime[(panel_id, lane)] = time.perf_counter() - lane_start

    candidates = pd.DataFrame(candidate_rows)
    admissions = pd.DataFrame(admission_rows)
    strict_rows: list[dict[str, Any]] = []
    strict_cache: dict[tuple[str, str], dict[str, Any]] = {}
    by_proposal = {row["proposal_id"]: row for row in candidate_rows}
    for row in admission_rows:
        if row["selected_for_strict"]:
            candidate = by_proposal[row["proposal_id"]]
            strict_rows.append(_strict_row(spec_by_id[row["proposal_id"]], candidate, panels[row["panel_id"]], "STRATIFIED_ADMISSION", strict_cache))
    for panel_id, quota in (("main", 288), ("bbo_micro", 32)):
        for proposal_id in global_top_k(candidate_rows, quota, panel_id=panel_id):
            candidate = by_proposal[proposal_id]
            strict_rows.append(_strict_row(spec_by_id[proposal_id], candidate, panels[panel_id], "GLOBAL_TOP_K_CONTROL", strict_cache))
    strict = pd.DataFrame(strict_rows)
    identities = (
        strict.sort_values(["panel_id", "exact_identity", "arm", "proposal_id"], kind="mergesort")
        .drop_duplicates(["panel_id", "exact_identity"])
        [["panel_id", "exact_identity", "activation_identity", "behaviour_cluster", "economic_hypothesis", "proposal_id", "lane_id"]]
    )
    clusters = _cluster_table(strict)
    comparison = _comparison(strict)
    lane_rows = []
    for (panel_id, lane), group in candidates.groupby(["panel_id", "lane_id"], sort=True):
        admitted = admissions[(admissions["panel_id"] == panel_id) & (admissions["lane_id"] == lane)]
        lane_rows.append({
            "panel_id": panel_id, "lane_id": lane, "proposals": len(group),
            "legal_candidates": int(group["legal"].sum()), "legal_candidate_rate": float(group["legal"].mean()),
            "canonical_identities": group["canonical_identity"].nunique(),
            "exact_identities": group.loc[group["legal"], "exact_identity"].nunique(),
            "stratified_admissions": len(admitted), "stratified_strict_evaluations": int(admitted["selected_for_strict"].sum()),
            "runtime_seconds": lane_runtime[(panel_id, lane)],
            "failure_rate": float((~group["legal"]).mean()),
        })
    lane_summary = pd.DataFrame(lane_rows)
    expected_strict = 32 * (len(MAIN_LANES) + len(BBO_LANES)) + 288 + 32
    incomplete_lanes = lane_summary[(lane_summary["proposals"] != 512) | (lane_summary["stratified_admissions"] != 64) | (lane_summary["stratified_strict_evaluations"] != 32)]
    decision = "B1S_CANARY_COMPLETED" if len(strict) == expected_strict and incomplete_lanes.empty and candidates["legal"].mean() > 0 else "B1S_CANARY_PARTIALLY_COMPLETED"
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(OUTPUT_ROOT / "candidate_table.csv", index=False)
    admissions.to_csv(OUTPUT_ROOT / "admission_table.csv", index=False)
    strict.to_csv(OUTPUT_ROOT / "strict_evaluation_table.csv", index=False)
    identities.to_csv(OUTPUT_ROOT / "identity_table.csv", index=False)
    clusters.to_csv(OUTPUT_ROOT / "cluster_table.csv", index=False)
    lane_summary.to_csv(OUTPUT_ROOT / "lane_summary.csv", index=False)
    comparison.to_csv(OUTPUT_ROOT / "stratified_vs_global_topk.csv", index=False)
    pd.DataFrame(adaptive_rows).to_csv(OUTPUT_ROOT / "adaptive_feedback_queries.csv", index=False)
    actual_seconds = time.perf_counter() - started
    outputs = [
        "candidate_table.csv", "admission_table.csv", "strict_evaluation_table.csv", "identity_table.csv",
        "cluster_table.csv", "lane_summary.csv", "stratified_vs_global_topk.csv", "adaptive_feedback_queries.csv",
    ]
    manifest: dict[str, Any] = {
        "experiment_id": frozen["experiment_id"], "decision": decision,
        "frozen_manifest": relative(FROZEN_MANIFEST), "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
        "repo_sha": frozen["repo_sha"], "data_release_sha256": frozen["data_release_sha256"],
        "proposal_rows": len(candidates), "legal_candidate_rate": float(candidates["legal"].mean()),
        "stratified_admissions": len(admissions), "stratified_strict_evaluations": int((strict["arm"] == "STRATIFIED_ADMISSION").sum()),
        "global_top_k_strict_evaluations": int((strict["arm"] == "GLOBAL_TOP_K_CONTROL").sum()),
        "logical_strict_evaluations": len(strict), "adaptive_feedback_queries": len(adaptive_rows),
        "main_and_bbo_directly_ranked": False, "actual_runtime_seconds": actual_seconds,
        "outputs": [{"path": relative(OUTPUT_ROOT / name), "sha256": sha256_file(OUTPUT_ROOT / name), "purpose": "final_canary_table"} for name in outputs],
        "reproducibility": "YES_FROZEN_INPUTS_AND_DETERMINISTIC_SEEDS",
        "continuation": "stop after closure; wait for independent frozen search epoch authorization",
        "formal_search_status": "FORMAL_SEARCH_FROZEN", "forward_status": "FORWARD_SEALED",
        "candidate_promotion": False, "a7mem_updated": False, "adaptive_cross_epoch_memory_updated": False,
        "validation_test_recent_stress_forward_read": False, "policy_or_elite_persisted": False,
        "online_budget_or_threshold_changed": False, "additional_budget_added": False,
        "alpha_ready_claimed": False, "deployable_claimed": False, "oos_proven_claimed": False,
    }
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# B1S CANARY Compact Result", "", f"Decision: `{decision}`", "",
        f"Frozen repo SHA: `{frozen['repo_sha']}`", f"Runtime seconds: `{actual_seconds:.2f}`", "",
        "Main and BBO micro results are separate comparison domains and were not directly ranked.", "",
        "## Lane Summary", "", lane_summary.to_markdown(index=False), "", "## Stratified vs Global Top-K", "",
        comparison.to_markdown(index=False), "", "## Frozen Boundaries", "",
        "- `FORMAL_SEARCH_FROZEN`", "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`",
        "- no A7MEM or cross-CANARY adaptive state persistence", "- BBO means top-of-book only, not multi-level depth",
    ]
    (OUTPUT_ROOT / "B1S_CANARY_COMPACT_RESULT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "proposals": len(candidates), "strict": len(strict), "runtime_seconds": actual_seconds}, indent=2))
    return manifest


def check() -> None:
    frozen = verify_frozen()
    manifest = load_json(RUN_MANIFEST)
    if manifest["frozen_manifest_sha256"] != frozen["frozen_manifest_sha256"]:
        raise ValueError("B1S run/freeze manifest mismatch")
    prohibited_true = [
        "candidate_promotion", "a7mem_updated", "adaptive_cross_epoch_memory_updated",
        "validation_test_recent_stress_forward_read", "policy_or_elite_persisted",
        "online_budget_or_threshold_changed", "additional_budget_added", "alpha_ready_claimed",
        "deployable_claimed", "oos_proven_claimed", "main_and_bbo_directly_ranked",
    ]
    if any(manifest.get(flag) for flag in prohibited_true):
        raise ValueError("B1S manifest records prohibited activity")
    if manifest["proposal_rows"] != 512 * 10 or manifest["stratified_admissions"] != 64 * 10:
        raise ValueError("B1S proposal/admission budget mismatch")
    if manifest["stratified_strict_evaluations"] != 32 * 10 or manifest["global_top_k_strict_evaluations"] != 320:
        raise ValueError("B1S strict evaluation budget mismatch")
    if manifest["adaptive_feedback_queries"] != 64:
        raise ValueError("B1S adaptive feedback query budget mismatch")
    for output in manifest["outputs"]:
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"B1S output hash drift: {output['path']}")
    comparison = pd.read_csv(OUTPUT_ROOT / "stratified_vs_global_topk.csv")
    if comparison["direct_cross_panel_ranking_performed"].any():
        raise PermissionError("B1S comparison table records cross-panel ranking")
    print("PASS_B1S_CANARY_FROZEN_OUTPUTS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["freeze", "run", "check"])
    args = parser.parse_args()
    try:
        if args.mode == "freeze":
            freeze()
        elif args.mode == "run":
            run()
        else:
            check()
    except Exception as exc:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        failure = {
            "experiment_id": "20260711_b1s_canary_001", "status": "FAILED_VISIBLE_NOT_DELETED",
            "mode": args.mode, "failure_stage": args.mode, "exception": f"{type(exc).__name__}: {exc}",
            "continuation": "inspect failure without adding budget or changing frozen contracts",
        }
        FAILURE_MANIFEST.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
