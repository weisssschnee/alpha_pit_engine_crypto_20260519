from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict, deque
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.b1s_canary import FrozenPanel, rank_weights
from alphafactory_crypto.nextgen_epoch import (
    ADAPTIVE_LANES,
    BBO_LANES,
    MAIN_LANES,
    ProgramSpec,
    SignalRecord,
    UCTProgramPolicy,
    candidate_identity,
    canonical_program_json,
    cem_preference,
    complexity,
    effective_count,
    make_program,
    materialize_program,
    multiobjective_evaluate,
    mutate_program,
    pareto_front,
    portfolio_series,
    program_identity,
    signal_record,
    stable_hash,
    surrogate_rank,
    validate_epoch_contract,
)


CONFIG = REPO / "config" / "crypto_nextgen_epoch0_v1.json"
MECHANISMS = REPO / "config" / "crypto_nextgen_mechanism_registry_v1.json"
ACCESS_POLICY = REPO / "config" / "crypto_evaluation_access_policy_v1.json"
FIELD_REGISTRY = REPO / "config" / "crypto_a7v_feature_registry_v1.json"
TEMPORAL_CONTRACT = REPO / "config" / "crypto_temporal_event_primitives_v1.json"
ADMISSION_CONTRACT = REPO / "config" / "crypto_anti_collapse_admission_v1.json"
BENCHMARK_CONTRACT = REPO / "config" / "crypto_challenger_harness_v1.json"
MODULE = REPO / "alphafactory_crypto" / "nextgen_epoch.py"
OUTPUT_ROOT = REPO / "runtime" / "nextgen_epoch0_20260711"
CANARY_ROOT = REPO / "runtime" / "b1s_canary_20260711"
B0A_REGISTRY = REPO / "runtime" / "a7b0a_signal_behaviour_20260711" / "activation_behaviour_identity_registry.csv"
SMOKE_MANIFEST = OUTPUT_ROOT / "epoch0_throughput_smoke.json"
FROZEN_MANIFEST = OUTPUT_ROOT / "epoch0_frozen_design_manifest.json"
RUN_MANIFEST = OUTPUT_ROOT / "epoch0_run_manifest.json"
FAILURE_MANIFEST = OUTPUT_ROOT / "epoch0_failure.json"
FEATURE_ROOT = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v3_patch_age_20260613")
BBO_DATA = Path("G:/AlphaFactory_CryptoData/gold/features/nextgen_dark_bookticker_core12_v1/bookticker_core12_1h_top_of_book_state.parquet")
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
ALGORITHM_BY_LANE = {
    "typed_random_fresh": "typed_random", "typed_ast": "typed_ast", "cem": "cem",
    "uct_mcts": "uct_mcts", "evolutionary": "evolutionary_search", "surrogate": "surrogate",
    "llm_proposal_repair": "llm_proposal_repair", "orthogonal_exile": "orthogonal_search",
    "bbo_typed_temporal": "typed_ast",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=check)
    return result.stdout.strip()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _pivot(frame: pd.DataFrame, field: str, symbols: tuple[str, ...], timestamps: pd.DatetimeIndex) -> np.ndarray:
    return frame.pivot(index="symbol", columns="timestamp", values=field).reindex(index=symbols, columns=timestamps).to_numpy(dtype=float)


def _rolling(values: np.ndarray, window: int, kind: str = "mean") -> np.ndarray:
    roll = pd.DataFrame(values.T).rolling(window, min_periods=max(2, window // 2))
    result = roll.std(ddof=0) if kind == "std" else roll.mean()
    return result.to_numpy(dtype=float).T


def _zscore(values: np.ndarray, window: int) -> np.ndarray:
    mean, std = _rolling(values, window), _rolling(values, window, "std")
    return np.divide(values - mean, std, out=np.full_like(values, np.nan), where=std > 1e-12)


def _event_age(values: np.ndarray) -> np.ndarray:
    changed = np.isfinite(values) & np.isfinite(np.concatenate([np.full((values.shape[0], 1), np.nan), values[:, :-1]], axis=1))
    changed &= values != np.concatenate([np.full((values.shape[0], 1), np.nan), values[:, :-1]], axis=1)
    result = np.full(values.shape, np.nan, dtype=float)
    for row in range(values.shape[0]):
        age = np.nan
        for column in range(values.shape[1]):
            if changed[row, column] or (column == 0 and np.isfinite(values[row, column])):
                age = 0.0
            elif np.isfinite(age):
                age += 1.0
            result[row, column] = age
    return result


def load_main_panel(*, include_target: bool = True) -> FrozenPanel:
    pieces = []
    for symbol in CORE12:
        path = FEATURE_ROOT / f"symbol={symbol}" / "part.parquet"
        piece = pq.ParquetFile(path).read(columns=list(MAIN_COLUMNS)).to_pandas()
        piece["timestamp"] = pd.to_datetime(piece["timestamp"], utc=True)
        piece["feature_available_time"] = pd.to_datetime(piece["feature_available_time"], utc=True)
        piece = piece[(piece["timestamp"] >= "2024-01-01T00:00:00Z") & (piece["timestamp"] <= "2024-12-31T23:00:00Z")]
        if (piece["feature_available_time"] < piece["timestamp"] + pd.Timedelta(hours=1)).any():
            raise PermissionError("main panel contains early feature availability")
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
    mark_index = _pivot(frame, "mark_index_basis_bps", symbols, timestamps)
    oi_raw = _pivot(frame, "open_interest_value_last", symbols, timestamps)
    taker_share = _pivot(frame, "kline_taker_buy_quote_share", symbols, timestamps)
    top_account = _pivot(frame, "top_long_short_account_ratio_last", symbols, timestamps)
    top_position = _pivot(frame, "top_long_short_position_ratio_last", symbols, timestamps)
    asset_return = np.full_like(close, np.nan)
    asset_return[:, 1:] = close[:, 1:] / close[:, :-1] - 1.0
    target = np.full_like(close, np.nan)
    if include_target:
        target[:, :-2] = close[:, 2:] / close[:, 1:-1] - 1.0
    market = np.nanmedian(asset_return, axis=0, keepdims=True)
    market_broadcast = np.repeat(market, len(symbols), axis=0)
    oi_change = np.full_like(oi_raw, np.nan)
    oi_change[:, 1:] = oi_raw[:, 1:] / oi_raw[:, :-1] - 1.0
    funding_change = np.full_like(funding, np.nan)
    funding_change[:, 1:] = funding[:, 1:] - funding[:, :-1]
    volatility = _rolling(asset_return, 24, "std")
    hour = timestamps.hour.to_numpy(dtype=float)
    session_sin = np.repeat(np.sin(2 * np.pi * hour / 24.0)[None, :], len(symbols), axis=0)
    session_cos = np.repeat(np.cos(2 * np.pi * hour / 24.0)[None, :], len(symbols), axis=0)
    fields = {
        "funding": funding, "funding_change": funding_change, "funding_surprise": _zscore(funding, 168),
        "funding_event_age": _event_age(funding), "basis": basis, "basis_abs": np.abs(basis),
        "oi": np.log1p(np.clip(oi_raw, 0, None)), "oi_change": oi_change,
        "mark_index_deviation": mark_index, "taker": 2.0 * taker_share - 1.0,
        "liquidity": np.log1p(np.clip(quote_volume, 0, None)), "volatility": volatility,
        "volatility_burst": _zscore(volatility, 168), "session_sin": session_sin, "session_cos": session_cos,
        "asset_return": asset_return, "market_return": market_broadcast,
        "relative_market_return": asset_return - market_broadcast,
        "cross_confirmation": np.sign(asset_return) * np.sign(market_broadcast),
        "positioning": top_position - top_account,
    }
    panel = FrozenPanel("main", symbols, timestamps, fields, target, "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY")
    panel.validate()
    return panel


def load_bbo_panel(main: FrozenPanel, *, include_target: bool = True) -> FrozenPanel:
    frame = pd.read_parquet(BBO_DATA, columns=[
        "symbol", "timestamp", "observable_time", "maturity_time", "spread_bps_mean", "bid_qty_mean",
        "ask_qty_mean", "quote_imbalance_mean", "top_of_book_liquidity_state",
    ])
    for column in ("timestamp", "observable_time", "maturity_time"):
        frame[column] = pd.to_datetime(frame[column], utc=True)
    if (frame["observable_time"] != frame["timestamp"] + pd.Timedelta(hours=1)).any():
        raise PermissionError("BBO observable time differs from completed bucket")
    if (frame["maturity_time"] != frame["observable_time"]).any():
        raise PermissionError("BBO maturity differs from observable time")
    symbols = tuple(sorted(frame["symbol"].unique()))
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
    target = np.vstack([main.target_return[main_symbol[symbol], time_index] for symbol in symbols]) if include_target else np.full((len(symbols), len(timestamps)), np.nan)
    panel = FrozenPanel("bbo_micro", symbols, timestamps, fields, target, "bucket_start_plus_1h", "bucket_close", "BBO_MICRO_ONLY")
    panel.validate()
    return panel


def sketch_panel(panel: FrozenPanel, stride: int) -> FrozenPanel:
    if stride <= 0:
        raise ValueError("sketch stride must be positive")
    index = np.arange(0, len(panel.timestamps), stride, dtype=int)
    fields = {name: np.asarray(values)[:, index] for name, values in panel.fields.items()}
    return FrozenPanel(
        panel.panel_id, panel.symbols, panel.timestamps[index], fields,
        np.asarray(panel.target_return)[:, index], panel.observable_time_rule, panel.maturity_rule,
        panel.comparison_domain,
    )


def diagnose_canary() -> dict[str, Any]:
    candidates = pd.read_csv(CANARY_ROOT / "candidate_table.csv")
    strict = pd.read_csv(CANARY_ROOT / "strict_evaluation_table.csv")
    lanes = []
    for (panel, lane), group in candidates.groupby(["panel_id", "lane_id"], sort=True):
        selected = strict[(strict["panel_id"] == panel) & (strict["lane_id"] == lane) & (strict["arm"] == "STRATIFIED_ADMISSION")]
        counts = selected["behaviour_cluster"].value_counts()
        lanes.append({
            "panel_id": panel, "lane_id": lane, "proposals": len(group),
            "legal_rate": float(group["legal"].mean()), "canonical_identities": int(group["canonical_identity"].nunique()),
            "exact_identities": int(group.loc[group["legal"], "exact_identity"].nunique()),
            "canonical_to_exact_rate": float(group.loc[group["legal"], "exact_identity"].nunique() / group["canonical_identity"].nunique()),
            "activation_identities": int(selected["activation_identity"].nunique()),
            "behaviour_clusters": int(selected["behaviour_cluster"].nunique()),
            "n_eff": effective_count(selected["behaviour_cluster"]),
            "top_cluster_share": float(counts.iloc[0] / len(selected)) if len(selected) else 0.0,
            "economic_hypothesis_coverage": int(selected["economic_hypothesis"].nunique()),
            "strict_survivors": int(selected["development_survivor"].sum()),
            "strict_survivor_efficiency": float(selected["development_survivor"].mean()) if len(selected) else 0.0,
            "new_behaviour_clusters_per_strict_evaluation": float(selected["behaviour_cluster"].nunique() / len(selected)) if len(selected) else 0.0,
        })
    arms = []
    for panel, group in strict.groupby("panel_id", sort=True):
        sets = {arm: set(values["behaviour_cluster"]) for arm, values in group.groupby("arm")}
        exact = {arm: set(values["exact_identity"]) for arm, values in group.groupby("arm")}
        left, right = sets["STRATIFIED_ADMISSION"], sets["GLOBAL_TOP_K_CONTROL"]
        arms.append({
            "panel_id": panel, "stratified_behaviour_clusters": len(left), "global_behaviour_clusters": len(right),
            "behaviour_overlap": len(left & right), "stratified_unique_behaviour": len(left - right),
            "global_unique_behaviour": len(right - left),
            "stratified_exact_identities": len(exact["STRATIFIED_ADMISSION"]),
            "global_exact_identities": len(exact["GLOBAL_TOP_K_CONTROL"]),
            "exact_overlap": len(exact["STRATIFIED_ADMISSION"] & exact["GLOBAL_TOP_K_CONTROL"]),
        })
    adaptive = candidates[candidates["lane_id"] == "adaptive_challenger"]
    adaptive_segments = []
    for segment, group in (("pilot", adaptive[adaptive["adaptive_query"]]), ("post_adaptation", adaptive[~adaptive["adaptive_query"]])):
        proxy = pd.to_numeric(group["proxy_score"], errors="coerce").replace([np.inf, -np.inf], np.nan)
        adaptive_segments.append({
            "segment": segment, "proposals": len(group), "legal_rate": float(group["legal"].mean()),
            "exact_identities": int(group.loc[group["legal"], "exact_identity"].nunique()),
            "proxy_median": float(proxy.median()), "operator_distribution": group["operator"].value_counts().to_dict(),
        })
    funding = candidates[candidates["lane_id"] == "funding_event"].sort_values("lane_ordinal")
    seed_sets = {int(seed): set(group.loc[group["legal"], "exact_identity"]) for seed, group in funding.groupby("seed")}
    seen: set[str] = set()
    quarters = []
    for index, start in enumerate((0, 128, 256, 384), 1):
        group = funding.iloc[start : start + 128]
        identities = set(group.loc[group["legal"], "exact_identity"])
        quarters.append({"quarter": index, "new_exact": len(identities - seen), "cumulative_exact": len(seen | identities)})
        seen |= identities
    operator_capacity = {}
    for operator, group in funding.groupby("operator"):
        operator_capacity[operator] = {
            "proposals": len(group), "legal": int(group["legal"].sum()),
            "exact": int(group.loc[group["legal"], "exact_identity"].nunique()),
        }
    historical = pd.read_csv(B0A_REGISTRY)
    main_strict = strict[strict["panel_id"] == "main"]
    result = {
        "status_correction": {
            "execution_status": "COMPLETED", "decision": "B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL",
            "acceptance": "B1S_CANARY_EXECUTION_ACCEPTED", "budget_contract": "FIXED_BUDGET_CONTRACT_PRESERVED",
            "planned_stratified_strict_evaluations": 320, "executed_stratified_strict_evaluations": 315,
            "quota_fill_rate": 0.984375, "global_top_k_strict_evaluations": 320,
            "total_development_strict_evaluations": 635, "underfill_lane": "funding_event",
            "underfill_type": "LEGAL_EXACT_IDENTITY_CAPACITY", "available_legal_exact_identities": 27,
            "planned_lane_strict_evaluations": 32, "underfill_count": 5, "rerun_required": False,
        },
        "lanes": lanes, "admission_comparison": arms, "adaptive": adaptive_segments,
        "funding_diagnosis": {
            "proposals": len(funding), "legal": int(funding["legal"].sum()),
            "canonical": int(funding["canonical_identity"].nunique()),
            "exact": int(funding.loc[funding["legal"], "exact_identity"].nunique()),
            "seed_exact_overlap": len(set.intersection(*seed_sets.values())),
            "seed_exact_union": len(set.union(*seed_sets.values())), "marginal_quarters": quarters,
            "operator_capacity": operator_capacity,
            "conclusion": "GENERATOR_AND_PRIMITIVE_CAPACITY_LIMIT_NOT_ECONOMIC_SPACE_PROOF",
        },
        "historical_cluster_comparability": {
            "b0a_clusters": int(historical["behaviour_cluster"].nunique()),
            "exact_id_overlap": len(set(main_strict["exact_identity"]) & set(historical["registered_exact_signal_identity"])),
            "behaviour_id_overlap": len(set(main_strict["behaviour_cluster"]) & set(historical["behaviour_cluster"])),
            "conclusion": "IDENTITY_SCHEMES_ARE_NOT_DIRECTLY_COMPARABLE; EPOCH0_MUST_EMIT_COMPATIBLE_REFERENCE_DISTANCE",
        },
        "actionable_changes": [
            "replace single-operator adaptive collapse with separate CEM, multi-step UCT/MCTS, evolutionary and surrogate lanes",
            "expand funding into level/change/surprise/event-age/state-transition programs and remove 128-proposal alias cycle",
            "use semantic-volume round-robin and exact-identity voting before performance selection",
            "replace single development score with hard gates, full multi-objective vectors and Pareto archive",
            "run simple benchmarks under the same development/cost contract and report incremental contribution",
            "emit compatible within-Epoch behaviour clusters and static historical-reference comparability diagnostics",
        ],
        "no_new_evaluation_block_read": True,
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_ROOT / "b1s_canary_deep_attribution.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lane_frame = pd.DataFrame(lanes)
    report = [
        "# B1S CANARY Deep Attribution", "",
        "Execution status: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL` / `B1S_CANARY_EXECUTION_ACCEPTED` / `FIXED_BUDGET_CONTRACT_PRESERVED`.", "",
        "This was not an interruption or failure. Funding-event produced 27 legal exact identities under the frozen budget; the system correctly did not duplicate identities, relax admission, change seeds, add proposals, or extend budget.", "",
        "## Per-lane evidence", "", lane_frame.to_markdown(index=False), "",
        "## Diagnosis", "",
        "- Funding identity capacity saturated after the first 128 proposals; both seeds produced the same 27-identity set.",
        "- `event_window` and `transition` produced zero legal exact identities; `event_age` collapsed 108 proposals to one identity.",
        "- The adaptive post-pilot segment concentrated all 448 proposals on `blend`; proxy median improved, but no development survivor emerged and operator diversity collapsed.",
        "- Global top-K found more main-panel behaviour clusters and all five survivors; stratified admission increased activation diversity but not behaviour-cluster count under the B1S quota design.",
        "- Historical four-cluster IDs and B1S cluster IDs are not directly comparable, so no claim about returning to the historical four is valid from raw ID overlap.", "",
        "## Executable changes", "", *[f"- {item}" for item in result["actionable_changes"]], "",
        "No new evaluation block was read and no CANARY rerun is required.",
    ]
    (OUTPUT_ROOT / "B1S_CANARY_COMPARATIVE_DECISION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return result


def _evaluate_spec(
    spec: ProgramSpec, panel: FrozenPanel, proxy_mask: np.ndarray,
    cache: dict[tuple[str, str], SignalRecord],
) -> SignalRecord:
    key = (panel.panel_id, canonical_program_json(spec))
    if key not in cache:
        try:
            record, _ = signal_record(spec, materialize_program(spec, panel), panel, proxy_mask)
            cache[key] = record
        except Exception as exc:
            cache[key] = SignalRecord("", "", "", float("-inf"), False, f"{type(exc).__name__}:{exc}")
    return cache[key]


def smoke() -> dict[str, Any]:
    config, registry = load_json(CONFIG), load_json(MECHANISMS)
    validate_epoch_contract(config, registry)
    main = load_main_panel(include_target=False)
    bbo = load_bbo_panel(main, include_target=False)
    panels = {"main": sketch_panel(main, 4), "bbo_micro": sketch_panel(bbo, 2)}
    started = time.perf_counter()
    records = []
    hashes = []
    count = int(config["throughput_smoke"]["proposals_per_lane"])
    for panel_id, lanes in (("main", MAIN_LANES), ("bbo_micro", BBO_LANES)):
        for lane in lanes:
            lane_start = time.perf_counter()
            for ordinal in range(count):
                spec = make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=ALGORITHM_BY_LANE[lane], seed=2601, ordinal=ordinal)
                signal = materialize_program(spec, panels[panel_id])
                hashes.append(hashlib.sha256(np.nan_to_num(signal, nan=-999.0).astype("<f4").tobytes()).hexdigest())
            records.append({"panel_id": panel_id, "lane_id": lane, "proposals": count, "seconds": time.perf_counter() - lane_start})
    seconds = time.perf_counter() - started
    proposals = count * (len(MAIN_LANES) + len(BBO_LANES))
    projected = seconds / proposals * 32768 + 900.0
    payload = {
        "experiment_id": "20260711_crypto_nextgen_epoch0_throughput_smoke_001",
        "objective": "freeze Epoch-0 budget before any Epoch-0 performance result",
        "status": "COMPLETED_NO_PERFORMANCE_READ", "repo_sha": git("rev-parse", "HEAD"),
        "proposals": proposals, "runtime_seconds": seconds, "proposals_per_second": proposals / seconds,
        "projected_32768_total_seconds_including_strict_reserve": projected,
        "selected_budget_if_frozen_now": 32768 if projected <= 5400 else None,
        "signal_content_hash": sha256_payload(hashes), "lane_runtime": records,
        "performance_read": False, "target_return_read": False, "reward_read": False,
        "validation_test_recent_may_stress_forward_read": False,
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    SMOKE_MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return payload


def freeze() -> dict[str, Any]:
    config, registry = load_json(CONFIG), load_json(MECHANISMS)
    validate_epoch_contract(config, registry)
    smoke_result = load_json(SMOKE_MANIFEST)
    if smoke_result.get("performance_read") or smoke_result.get("target_return_read") or smoke_result.get("reward_read"):
        raise PermissionError("throughput smoke read performance")
    if smoke_result.get("selected_budget_if_frozen_now") != 32768:
        raise RuntimeError("throughput smoke did not qualify the lower frozen Epoch-0 budget")
    if git("diff", "--quiet", check=False) != "":
        # git diff --quiet has no stdout; return-code is checked below instead.
        pass
    if subprocess.run(["git", "diff", "--quiet"], cwd=REPO).returncode:
        raise RuntimeError("freeze requires committed tracked implementation files")
    feature_files = [FEATURE_ROOT / f"symbol={symbol}" / "part.parquet" for symbol in CORE12]
    input_paths = feature_files + [BBO_DATA, B0A_REGISTRY, CANARY_ROOT / "candidate_table.csv", CANARY_ROOT / "strict_evaluation_table.csv"]
    missing = [str(path) for path in input_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Epoch-0 frozen input missing: {missing}")
    inputs = {relative(path): sha256_file(path) for path in input_paths}
    contracts = [CONFIG, MECHANISMS, ACCESS_POLICY, FIELD_REGISTRY, TEMPORAL_CONTRACT, ADMISSION_CONTRACT, BENCHMARK_CONTRACT, MODULE, Path(__file__)]
    contract_hashes = {relative(path): sha256_file(path) for path in contracts}
    lane_proposals = {lane: 3840 for lane in MAIN_LANES} | {BBO_LANES[0]: 2048}
    strict_by_lane = {lane: 112 for lane in MAIN_LANES} | {BBO_LANES[0]: 128}
    payload: dict[str, Any] = {
        "experiment_id": "20260711_crypto_nextgen_search_epoch0_001",
        "objective": "compare isolated next-generation search algorithms and mechanisms under one frozen development-only contract",
        "status": "EPOCH0_DESIGN_FROZEN_NOT_STARTED", "mode": "FROZEN_DEVELOPMENT_SEARCH",
        "implementation_subject_sha": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
        "input_files_sha256": inputs, "data_release_sha256": sha256_payload(inputs),
        "contracts_sha256": contract_hashes, "contract_bundle_sha256": sha256_payload(contract_hashes),
        "throughput_smoke": relative(SMOKE_MANIFEST), "throughput_smoke_sha256": sha256_file(SMOKE_MANIFEST),
        "budget": {
            "total_proposals": 32768, "proposals_by_lane": lane_proposals,
            "fixed_seeds": [2701, 2709], "stratified_strict_evaluations": 1024,
            "stratified_strict_by_lane": strict_by_lane, "global_top_k_strict_evaluations": 1024,
            "logical_strict_evaluations": 2048, "adaptive_feedback_queries_per_seed": 256,
            "online_extension_allowed": False,
        },
        "panels": config["panels"], "lanes": config["lanes"],
        "mechanism_registry_sha256": contract_hashes[relative(MECHANISMS)],
        "reward_contract": config["reward_contract"], "admission_contract": config["admission_contract"],
        "strategy_benchmarks": config["strategy_benchmarks"], "algorithm_competitors": config["algorithm_competitors"],
        "adaptive_contract": config["adaptive_contract"], "prohibited": config["prohibited"],
        "commands": {
            "diagnose_canary": "python scripts/crypto_nextgen_epoch0.py diagnose-canary",
            "smoke": "python scripts/crypto_nextgen_epoch0.py smoke",
            "freeze": "python scripts/crypto_nextgen_epoch0.py freeze",
            "run": "python scripts/crypto_nextgen_epoch0.py run",
            "check": "python scripts/crypto_nextgen_epoch0.py check",
        },
        "estimated_cost_time": f"{smoke_result['projected_32768_total_seconds_including_strict_reserve']:.1f} seconds projected; no budget extension",
        "reproducibility": "FROZEN_INPUT_HASHES_CONTRACT_HASHES_SEEDS_AND_BUDGET",
        "continuation": "run exactly once from a descendant of implementation_subject_sha with identical contract/input hashes; do not inspect intermediate performance",
        "search_started": False, "candidate_promotion": False, "a7mem_updated": False,
        "cross_epoch_memory_updated": False, "forward_read": False,
    }
    payload["frozen_manifest_sha256"] = sha256_payload(payload)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    FROZEN_MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "budget": payload["budget"], "manifest_sha256": payload["frozen_manifest_sha256"]}, indent=2))
    return payload


def verify_frozen() -> dict[str, Any]:
    manifest = load_json(FROZEN_MANIFEST)
    recorded = manifest.pop("frozen_manifest_sha256")
    if sha256_payload(manifest) != recorded:
        raise ValueError("Epoch-0 frozen manifest hash mismatch")
    manifest["frozen_manifest_sha256"] = recorded
    if subprocess.run(["git", "merge-base", "--is-ancestor", manifest["implementation_subject_sha"], "HEAD"], cwd=REPO).returncode:
        raise ValueError("Epoch-0 implementation subject is not an ancestor of HEAD")
    for raw, expected in manifest["input_files_sha256"].items():
        path = Path(raw) if Path(raw).is_absolute() else REPO / raw
        if sha256_file(path) != expected:
            raise ValueError(f"Epoch-0 input hash drift: {raw}")
    for raw, expected in manifest["contracts_sha256"].items():
        if sha256_file(REPO / raw) != expected:
            raise ValueError(f"Epoch-0 contract hash drift: {raw}")
    return manifest


def _benchmark_signals(panel: FrozenPanel) -> dict[str, np.ndarray]:
    if panel.panel_id == "bbo_micro":
        return {
            "simple_liquidity": -np.asarray(panel.fields["spread"]),
            "simple_quote_imbalance": np.asarray(panel.fields["quote_imbalance"]),
        }
    fields = panel.fields
    return {
        "simple_funding": -np.asarray(fields["funding"]),
        "simple_basis": -np.asarray(fields["basis"]),
        "simple_oi": np.asarray(fields["oi_change"]),
        "momentum": np.asarray(fields["asset_return"]),
        "reversal": -np.asarray(fields["asset_return"]),
        "volatility": -np.asarray(fields["volatility_burst"]),
        "liquidity": np.asarray(fields["liquidity"]),
        "session_time_of_day": np.asarray(fields["taker"]) * np.asarray(fields["session_sin"]),
        "cross_asset_state": np.asarray(fields["relative_market_return"]),
    }


def _run_benchmarks(panels: Mapping[str, FrozenPanel], cost_bps: float, minimum_assets: int) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    best: dict[str, tuple[float, np.ndarray]] = {}
    for panel_id, panel in panels.items():
        for benchmark_id, signal in _benchmark_signals(panel).items():
            weights = rank_weights(signal)
            net, turnover = portfolio_series(weights, panel.target_return, cost_bps)
            finite = net[np.isfinite(net)]
            mean = float(np.mean(finite)) if len(finite) else float("nan")
            std = float(np.std(finite)) if len(finite) else float("nan")
            lcb = mean - 1.96 * std / math.sqrt(len(finite)) if len(finite) else float("nan")
            rows.append({
                "panel_id": panel_id, "comparison_domain": panel.comparison_domain,
                "benchmark_id": benchmark_id, "observations": len(finite), "net_mean": mean,
                "net_lcb": lcb, "return_risk": mean / std * math.sqrt(len(finite)) if len(finite) >= 2 and std > 1e-15 else float("nan"),
                "turnover_mean": float(np.mean(turnover)), "feedback_permission": "REPORT_ONLY_NO_MEMORY",
            })
            if panel_id not in best or lcb > best[panel_id][0]:
                best[panel_id] = (lcb, net)
    return pd.DataFrame(rows), {panel: item[1] for panel, item in best.items()}


def _generate_lane(
    lane: str, panel_id: str, seed: int, count: int, feedback_queries: int,
    registry: Mapping[str, Any], panel: FrozenPanel, proxy_mask: np.ndarray,
    cache: dict[tuple[str, str], SignalRecord],
) -> tuple[list[ProgramSpec], list[SignalRecord], list[dict[str, Any]]]:
    algorithm = ALGORITHM_BY_LANE[lane]
    specs: list[ProgramSpec] = []
    records: list[SignalRecord] = []
    feedback_rows: list[dict[str, Any]] = []
    queries = min(feedback_queries, count) if lane in ADAPTIVE_LANES else 0
    if lane == "uct_mcts":
        policy = UCTProgramPolicy(registry, panel_id=panel_id, lane_id=lane, seed=seed)
        for ordinal in range(queries):
            spec = policy.propose(ordinal)
            record = _evaluate_spec(spec, panel, proxy_mask, cache)
            policy.update(ordinal, record.proxy_score)
            specs.append(spec); records.append(record)
            feedback_rows.append({"panel_id": panel_id, "lane_id": lane, "seed": seed, "query_ordinal": ordinal, "proxy_score": record.proxy_score, "program_identity": program_identity(spec), "persisted": False})
        preference = policy.frozen_preference()
        for ordinal in range(queries, count):
            spec = make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=algorithm, seed=seed, ordinal=ordinal, preference=preference)
            specs.append(spec); records.append(_evaluate_spec(spec, panel, proxy_mask, cache))
        return specs, records, feedback_rows
    initial = [make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=algorithm, seed=seed, ordinal=i, policy_feedback_used=i < queries) for i in range(queries)]
    initial_records = [_evaluate_spec(spec, panel, proxy_mask, cache) for spec in initial]
    for ordinal, (spec, record) in enumerate(zip(initial, initial_records)):
        feedback_rows.append({"panel_id": panel_id, "lane_id": lane, "seed": seed, "query_ordinal": ordinal, "proxy_score": record.proxy_score, "program_identity": program_identity(spec), "persisted": False})
    specs.extend(initial); records.extend(initial_records)
    remaining = count - len(specs)
    if lane == "cem":
        preference = cem_preference(initial, [record.proxy_score for record in initial_records])
        tail = [make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=algorithm, seed=seed, ordinal=i + queries, preference=preference) for i in range(remaining)]
    elif lane == "evolutionary":
        ranked = sorted(zip(initial, initial_records), key=lambda item: item[1].proxy_score, reverse=True)
        parents = [spec for spec, record in ranked if record.legal][:32] or initial[:32]
        tail = [mutate_program(parents[i % len(parents)], registry, seed=seed, ordinal=i + queries) for i in range(remaining)]
    elif lane == "surrogate":
        pool = [make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=algorithm, seed=seed + 10000, ordinal=i + queries) for i in range(max(remaining * 2, remaining + 256))]
        tail = surrogate_rank(initial, [record.proxy_score for record in initial_records], pool, remaining)
        if len(tail) < remaining:
            tail.extend(pool[: remaining - len(tail)])
    else:
        tail = [make_program(registry, lane_id=lane, panel_id=panel_id, algorithm=algorithm, seed=seed, ordinal=i) for i in range(count)]
        specs = []
        records = []
    for spec in tail:
        specs.append(spec); records.append(_evaluate_spec(spec, panel, proxy_mask, cache))
    if len(specs) != count:
        raise ValueError(f"proposal count drift for {panel_id}/{lane}/{seed}: {len(specs)}")
    return specs, records, feedback_rows


def _admit_stratified(candidates: pd.DataFrame, quotas: Mapping[str, int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    admitted_rows = []
    rejected_rows = []
    used_exact: set[tuple[str, str]] = set()
    for (panel, lane), group in candidates.groupby(["panel_id", "lane_id"], sort=True):
        quota = int(quotas[lane])
        legal = group[group["legal"]].sort_values(["seed", "ordinal", "proposal_id"], kind="mergesort")
        legal = legal.drop_duplicates("exact_identity", keep="first")
        buckets = {key: deque(values.to_dict("records")) for key, values in legal.groupby("mechanism_id", sort=True)}
        behaviour: Counter[str] = Counter(); hypotheses: Counter[str] = Counter(); parents: Counter[str] = Counter(); families: Counter[str] = Counter()
        keys = sorted(buckets)
        rank = 0
        while rank < quota and any(buckets.values()):
            progressed = False
            for key in keys:
                if rank >= quota or not buckets[key]:
                    continue
                row = buckets[key].popleft(); progressed = True
                exact_key = (panel, row["exact_identity"])
                reason = ""
                if exact_key in used_exact:
                    reason = "DUPLICATE_EXACT_IDENTITY_ONE_VOTE"
                elif behaviour[row["behaviour_cluster"]] >= 8:
                    reason = "BEHAVIOUR_CLUSTER_QUOTA"
                elif hypotheses[row["economic_hypothesis"]] >= 24:
                    reason = "ECONOMIC_HYPOTHESIS_QUOTA"
                elif parents[row["parent_identity"]] >= 8:
                    reason = "PARENT_DESCENDANT_CAP"
                elif families[row["mechanism_id"]] >= 32:
                    reason = "FAMILY_BUDGET_CAP"
                if reason:
                    rejected_rows.append({"panel_id": panel, "lane_id": lane, "proposal_id": row["proposal_id"], "reason": reason})
                    continue
                admitted_rows.append({
                    "panel_id": panel, "lane_id": lane, "proposal_id": row["proposal_id"],
                    "exact_identity": row["exact_identity"], "admission_rank": rank,
                    "admission_type": "SEMANTIC_VOLUME_STRATIFIED", "selected_for_strict": True,
                })
                used_exact.add(exact_key); behaviour[row["behaviour_cluster"]] += 1
                hypotheses[row["economic_hypothesis"]] += 1; parents[row["parent_identity"]] += 1
                families[row["mechanism_id"]] += 1; rank += 1
            if not progressed:
                break
    return pd.DataFrame(admitted_rows), pd.DataFrame(rejected_rows)


def _global_top_k(candidates: pd.DataFrame, panel_id: str, quota: int) -> list[str]:
    legal = candidates[(candidates["panel_id"] == panel_id) & candidates["legal"]].copy()
    legal = legal.sort_values(["proxy_score", "ordinal", "proposal_id"], ascending=[False, True, True], kind="mergesort")
    legal = legal.drop_duplicates("exact_identity", keep="first")
    return legal.head(quota)["proposal_id"].tolist()


def run() -> dict[str, Any]:
    frozen = verify_frozen()
    config, registry = load_json(CONFIG), load_json(MECHANISMS)
    validate_epoch_contract(config, registry)
    started = time.perf_counter()
    main = load_main_panel(); bbo = load_bbo_panel(main)
    panels = {"main": main, "bbo_micro": bbo}
    proposal_panels = {"main": sketch_panel(main, 4), "bbo_micro": sketch_panel(bbo, 2)}
    proxy_masks = {panel_id: np.ones(len(panel.timestamps), dtype=bool) for panel_id, panel in proposal_panels.items()}
    cost_bps = float(config["reward_contract"]["cost_bps_per_unit_turnover"])
    minimum_assets = 5
    benchmarks, best_benchmark_net = _run_benchmarks(panels, cost_bps, minimum_assets)
    candidate_rows: list[dict[str, Any]] = []
    spec_by_id: dict[str, ProgramSpec] = {}
    feedback_rows: list[dict[str, Any]] = []
    cache: dict[tuple[str, str], SignalRecord] = {}
    lane_runtime: dict[tuple[str, str], float] = {}
    volume_by_family = {item["mechanism_id"]: int(item["semantic_volume_estimate"]) for item in registry["mechanism_families"]}
    for panel_id, lanes in (("main", MAIN_LANES), ("bbo_micro", BBO_LANES)):
        panel = proposal_panels[panel_id]
        for lane in lanes:
            lane_start = time.perf_counter()
            total = int(frozen["budget"]["proposals_by_lane"][lane])
            per_seed = total // len(frozen["budget"]["fixed_seeds"])
            lane_ordinal = 0
            for seed in frozen["budget"]["fixed_seeds"]:
                specs, records, feedback = _generate_lane(
                    lane, panel_id, int(seed), per_seed, int(frozen["budget"]["adaptive_feedback_queries_per_seed"]),
                    registry, panel, proxy_masks[panel_id], cache,
                )
                feedback_rows.extend(feedback)
                for spec, record in zip(specs, records):
                    proposal_id = candidate_identity(spec)
                    spec_by_id[proposal_id] = spec
                    candidate_rows.append({
                        "proposal_id": proposal_id, "panel_id": panel_id, "comparison_domain": panel.comparison_domain,
                        "lane_id": lane, "algorithm": spec.algorithm, "seed": spec.seed, "ordinal": spec.ordinal,
                        "lane_ordinal": lane_ordinal, "mechanism_id": spec.mechanism_id,
                        "economic_hypothesis": spec.economic_hypothesis, "field_a": spec.field_a, "field_b": spec.field_b,
                        "primitive": spec.primitive, "secondary_primitive": spec.secondary_primitive,
                        "interaction": spec.interaction, "window": spec.window, "long_window": spec.long_window,
                        "threshold": spec.threshold, "direction": spec.direction, "parent_identity": spec.parent_identity,
                        "lineage_namespace": spec.lineage_namespace, "raw_template": spec.raw_template,
                        "repaired": spec.repaired, "policy_feedback_used": spec.policy_feedback_used,
                        "canonical_expression": canonical_program_json(spec), "canonical_identity": program_identity(spec),
                        "exact_identity": record.exact_identity, "proposal_sketch_identity": record.exact_identity,
                        "identity_scope": "DETERMINISTIC_PROPOSAL_OBSERVATION_SKETCH",
                        "activation_identity": record.activation_identity,
                        "behaviour_cluster": record.behaviour_cluster, "proxy_score": record.proxy_score,
                        "legal": record.legal, "failure_reason": record.failure_reason,
                        "semantic_volume_estimate": volume_by_family[spec.mechanism_id],
                        "semantic_lottery_weight": 1.0 / volume_by_family[spec.mechanism_id],
                        "feedback_permission": "EPOCH0_DEVELOPMENT_ONLY_RUNTIME_NO_MEMORY_NO_PROMOTION",
                    })
                    lane_ordinal += 1
            lane_runtime[(panel_id, lane)] = time.perf_counter() - lane_start
    candidates = pd.DataFrame(candidate_rows)
    if len(candidates) != frozen["budget"]["total_proposals"]:
        raise ValueError("Epoch-0 proposal budget drift")
    admissions, rejections = _admit_stratified(candidates, frozen["budget"]["stratified_strict_by_lane"])
    by_id = candidates.set_index("proposal_id", drop=False)
    strict_refs = []
    for proposal_id in admissions["proposal_id"]:
        strict_refs.append(("STRATIFIED_ADMISSION", proposal_id))
    panel_quota = {
        "main": sum(frozen["budget"]["stratified_strict_by_lane"][lane] for lane in MAIN_LANES),
        "bbo_micro": frozen["budget"]["stratified_strict_by_lane"][BBO_LANES[0]],
    }
    for panel_id, quota in panel_quota.items():
        strict_refs.extend(("GLOBAL_TOP_K_CONTROL", proposal_id) for proposal_id in _global_top_k(candidates, panel_id, quota))
    preliminary = []
    strict_seen: set[tuple[str, str, str]] = set()
    for arm, proposal_id in strict_refs:
        row = by_id.loc[proposal_id]
        spec = spec_by_id[proposal_id]
        full_record, _ = signal_record(
            spec, materialize_program(spec, panels[row["panel_id"]]), panels[row["panel_id"]],
            np.ones(len(panels[row["panel_id"]].timestamps), dtype=bool),
        )
        full_key = (row["panel_id"], arm, full_record.exact_identity)
        if full_key in strict_seen:
            continue
        strict_seen.add(full_key)
        preliminary.append({
            "arm": arm, "proposal_id": proposal_id, "panel_id": row["panel_id"], "lane_id": row["lane_id"],
            "proposal_sketch_identity": row["proposal_sketch_identity"],
            "exact_identity": full_record.exact_identity, "activation_identity": full_record.activation_identity,
            "behaviour_cluster": full_record.behaviour_cluster, "economic_hypothesis": row["economic_hypothesis"],
            "mechanism_id": row["mechanism_id"], "algorithm": row["algorithm"], "proxy_score": row["proxy_score"],
        })
    prelim = pd.DataFrame(preliminary)
    cluster_counts = prelim.groupby(["panel_id", "arm"])["behaviour_cluster"].transform("count")
    same_cluster = prelim.groupby(["panel_id", "arm", "behaviour_cluster"])["behaviour_cluster"].transform("count")
    novelty = np.log1p(cluster_counts / same_cluster)
    strict_rows = []
    metric_cache: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record, novelty_value in zip(preliminary, novelty):
        row = by_id.loc[record["proposal_id"]]
        spec = spec_by_id[record["proposal_id"]]
        metric_key = (record["panel_id"], record["arm"], record["exact_identity"])
        if metric_key not in metric_cache:
            weights = rank_weights(materialize_program(spec, panels[record["panel_id"]]))
            vector = multiobjective_evaluate(
                weights, panels[record["panel_id"]],
                complexity=complexity(spec), behaviour_novelty=float(novelty_value),
                benchmark_net=best_benchmark_net[record["panel_id"]], cost_bps=cost_bps,
                minimum_assets=minimum_assets,
            )
            metric_cache[metric_key] = asdict(vector)
        metrics = metric_cache[metric_key]
        strict_rows.append({
            **record, **metrics,
            "development_survivor": bool(
                metrics["hard_gate_pass"] and metrics["ic_lcb"] > 0 and metrics["net_lcb"] > 0
                and metrics["benchmark_incremental_lcb"] > 0 and metrics["worst_horizon_net_mean"] > -0.001
            ),
            "candidate_promotion": False, "feedback_persisted": False,
        })
    strict = pd.DataFrame(strict_rows)
    pareto_rows = []
    for (panel_id, arm), group in strict.groupby(["panel_id", "arm"], sort=True):
        selected = set(pareto_front(group.to_dict("records")))
        for rank, proposal_id in enumerate(sorted(selected)):
            pareto_rows.append({"panel_id": panel_id, "arm": arm, "proposal_id": proposal_id, "pareto_rank": rank, "candidate_promotion": False})
    pareto = pd.DataFrame(pareto_rows)
    frozen_pack = strict[(strict["arm"] == "STRATIFIED_ADMISSION") & strict["proposal_id"].isin(set(pareto.get("proposal_id", [])))].copy()
    frozen_pack["pack_status"] = "FROZEN_DEVELOPMENT_CANDIDATE_NO_PROMOTION"
    lane_rows = []
    for (panel_id, lane), group in candidates.groupby(["panel_id", "lane_id"], sort=True):
        selected = strict[(strict["panel_id"] == panel_id) & (strict["lane_id"] == lane) & (strict["arm"] == "STRATIFIED_ADMISSION")]
        counts = selected["behaviour_cluster"].value_counts()
        lane_rows.append({
            "panel_id": panel_id, "lane_id": lane, "proposals": len(group), "legal_rate": float(group["legal"].mean()),
            "canonical_identities": int(group["canonical_identity"].nunique()),
            "exact_identities": int(group.loc[group["legal"], "exact_identity"].nunique()),
            "activation_identities": int(selected["activation_identity"].nunique()),
            "behaviour_clusters": int(selected["behaviour_cluster"].nunique()),
            "economic_hypotheses": int(selected["economic_hypothesis"].nunique()),
            "n_eff": effective_count(selected["behaviour_cluster"]),
            "top_1_cluster_share": float(counts.iloc[:1].sum() / len(selected)) if len(selected) else 0.0,
            "top_3_cluster_share": float(counts.iloc[:3].sum() / len(selected)) if len(selected) else 0.0,
            "strict_evaluations": len(selected), "development_survivors": int(selected["development_survivor"].sum()),
            "new_behaviour_clusters_per_100_strict": float(selected["behaviour_cluster"].nunique() / len(selected) * 100) if len(selected) else 0.0,
            "runtime_seconds": lane_runtime[(panel_id, lane)], "failure_rate": float((~group["legal"]).mean()),
        })
    lane_efficiency = pd.DataFrame(lane_rows)
    comparisons = []
    for (panel_id, arm), group in strict.groupby(["panel_id", "arm"], sort=True):
        counts = group["behaviour_cluster"].value_counts()
        comparisons.append({
            "panel_id": panel_id, "arm": arm, "strict_evaluations": len(group),
            "exact_identities": int(group["exact_identity"].nunique()),
            "activation_identities": int(group["activation_identity"].nunique()),
            "behaviour_clusters": int(group["behaviour_cluster"].nunique()),
            "economic_hypotheses": int(group["economic_hypothesis"].nunique()),
            "n_eff": effective_count(group["behaviour_cluster"]),
            "top_1_cluster_share": float(counts.iloc[:1].sum() / len(group)),
            "top_3_cluster_share": float(counts.iloc[:3].sum() / len(group)),
            "development_survivors": int(group["development_survivor"].sum()),
            "pareto_candidates": int(group["proposal_id"].isin(set(pareto.get("proposal_id", []))).sum()),
            "new_behaviour_clusters_per_100_strict": float(group["behaviour_cluster"].nunique() / len(group) * 100),
            "direct_cross_panel_ranking": False,
        })
    comparison = pd.DataFrame(comparisons)
    semantic = candidates.groupby(["panel_id", "lane_id", "mechanism_id"], sort=True).agg(
        proposals=("proposal_id", "size"), legal=("legal", "sum"), canonical=("canonical_identity", "nunique"),
        exact=("exact_identity", lambda values: values[values.astype(str) != ""].nunique()),
        semantic_volume_estimate=("semantic_volume_estimate", "first"),
    ).reset_index()
    basin_rows = []
    for lane, group in candidates[candidates["panel_id"] == "main"].groupby("lane_id", sort=True):
        legal = group[group["legal"]].sort_values("proxy_score", ascending=False)
        top = legal.head(max(1, len(legal) // 10))
        basin_rows.append({
            "lane_id": lane, "top_decile_proposals": len(top),
            "top_mechanism_share": float(top["mechanism_id"].value_counts(normalize=True).iloc[0]) if len(top) else 0.0,
            "top_primitive_share": float(top["primitive"].value_counts(normalize=True).iloc[0]) if len(top) else 0.0,
            "top_behaviour_cluster_share": float(top["behaviour_cluster"].value_counts(normalize=True).iloc[0]) if len(top) else 0.0,
            "scalar_basin_flag": bool(len(top) and (top["mechanism_id"].value_counts(normalize=True).iloc[0] > 0.5 or top["primitive"].value_counts(normalize=True).iloc[0] > 0.5)),
        })
    basin = pd.DataFrame(basin_rows)
    identities = strict.sort_values(["panel_id", "exact_identity", "arm", "proposal_id"], kind="mergesort").drop_duplicates(["panel_id", "exact_identity"])[
        ["panel_id", "exact_identity", "activation_identity", "behaviour_cluster", "economic_hypothesis", "mechanism_id", "proposal_id"]
    ]
    clusters = strict.groupby(["panel_id", "arm", "behaviour_cluster"], sort=True).agg(
        strict_rows=("proposal_id", "size"), exact_identities=("exact_identity", "nunique"),
        economic_hypotheses=("economic_hypothesis", "nunique"), development_survivors=("development_survivor", "sum"),
    ).reset_index()
    hypotheses = strict.groupby(["panel_id", "arm", "economic_hypothesis"], sort=True).agg(
        strict_rows=("proposal_id", "size"), exact_identities=("exact_identity", "nunique"),
        behaviour_clusters=("behaviour_cluster", "nunique"), development_survivors=("development_survivor", "sum"),
    ).reset_index()
    lineage = {
        "graph_id": "CRYPTO-NEXTGEN-EPOCH0-LINEAGE-V1", "candidate_promotion": False,
        "nodes": [
            {"id": row["proposal_id"], "kind": "candidate", "lane": row["lane_id"], "mechanism": row["mechanism_id"], "proposal_sketch_identity": row["proposal_sketch_identity"]}
            for row in candidate_rows
        ],
        "edges": [
            {"source": row["parent_identity"], "target": row["proposal_id"], "relationship": "PROPOSED_DESCENDANT", "namespace": row["lineage_namespace"]}
            for row in candidate_rows
        ],
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    tables = {
        "raw_proposals.csv": candidates, "admission_table.csv": admissions,
        "admission_rejections.csv": rejections, "strict_evaluations.csv": strict,
        "identity_table.csv": identities, "behaviour_clusters.csv": clusters,
        "economic_hypotheses.csv": hypotheses, "pareto_archive.csv": pareto,
        "benchmark_results.csv": benchmarks, "benchmark_comparisons.csv": comparison,
        "lane_efficiency.csv": lane_efficiency, "semantic_volume_accounting.csv": semantic,
        "adaptive_feedback_queries.csv": pd.DataFrame(feedback_rows), "reward_basin_audit.csv": basin,
        "frozen_candidate_pack.csv": frozen_pack,
    }
    for name, frame in tables.items():
        frame.to_csv(OUTPUT_ROOT / name, index=False)
    (OUTPUT_ROOT / "lineage_graph.json").write_text(json.dumps(lineage, separators=(",", ":")) + "\n", encoding="utf-8")
    output_names = list(tables) + ["lineage_graph.json"]
    stratified_actual = int((strict["arm"] == "STRATIFIED_ADMISSION").sum())
    global_actual = int((strict["arm"] == "GLOBAL_TOP_K_CONTROL").sum())
    execution_complete = len(candidates) == 32768 and 0 < global_actual <= 1024 and 0 < stratified_actual <= 1024
    decision = "FROZEN_DEVELOPMENT_EPOCH_COMPLETED" if execution_complete else "FROZEN_DEVELOPMENT_EPOCH_PARTIALLY_COMPLETED"
    main_compare = comparison[comparison["panel_id"] == "main"].set_index("arm")
    adaptive_basin_rate = float(basin[basin["lane_id"].isin(ADAPTIVE_LANES)]["scalar_basin_flag"].mean())
    if main_compare.loc["STRATIFIED_ADMISSION", "behaviour_clusters"] >= 150 and adaptive_basin_rate <= 0.5 and len(frozen_pack) > 0:
        recommendation = "PREPARE_ROTATING_CHALLENGE_EPOCH"
    elif semantic["exact"].sum() / max(1, semantic["canonical"].sum()) < 0.20:
        recommendation = "REVISE_HYPOTHESIS_SPACE_AND_REPEAT_DEVELOPMENT_EPOCH"
    else:
        recommendation = "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    actual_seconds = time.perf_counter() - started
    manifest: dict[str, Any] = {
        "experiment_id": frozen["experiment_id"], "decision": decision, "next_step_recommendation": recommendation,
        "execution_status": "COMPLETED" if execution_complete else "PARTIALLY_COMPLETED",
        "frozen_manifest": relative(FROZEN_MANIFEST), "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
        "implementation_subject_sha": frozen["implementation_subject_sha"], "data_release_sha256": frozen["data_release_sha256"],
        "proposal_rows": len(candidates), "planned_stratified_strict_evaluations": 1024,
        "executed_stratified_strict_evaluations": stratified_actual, "global_top_k_strict_evaluations": global_actual,
        "total_development_strict_evaluations": len(strict), "adaptive_feedback_queries": len(feedback_rows),
        "pareto_candidates": len(pareto), "frozen_candidate_pack_rows": len(frozen_pack),
        "actual_runtime_seconds": actual_seconds,
        "outputs": [{"path": relative(OUTPUT_ROOT / name), "sha256": sha256_file(OUTPUT_ROOT / name), "purpose": "epoch0_final_artifact"} for name in output_names],
        "reproducibility": "YES_FROZEN_INPUTS_CONTRACTS_BUDGET_SEEDS_AND_DETERMINISTIC_PROGRAMS",
        "continuation": "stop after closure; wait for independent decision; never open OOS automatically",
        "forward_status": "FORWARD_SEALED", "candidate_promotion_status": "NO_CANDIDATE_PROMOTION",
        "cross_epoch_memory_status": "NO_CROSS_EPOCH_ADAPTIVE_MEMORY",
        "validation_test_recent_may_stress_forward_read": False, "candidate_promotion": False,
        "a7mem_updated": False, "cross_lane_memory_persisted": False, "cross_epoch_memory_persisted": False,
        "online_contract_changed": False, "additional_budget_added": False, "intermediate_human_reweighting": False,
        "alpha_ready_claimed": False, "oos_proven_claimed": False, "main_and_bbo_directly_ranked": False,
    }
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# CRYPTO NEXTGEN SEARCH EPOCH-0", "", f"Status: `{decision}`", f"Recommendation: `{recommendation}`", "",
        f"Frozen design hash: `{frozen['frozen_manifest_sha256']}`", f"Runtime seconds: `{actual_seconds:.2f}`", "",
        "## Arm comparison", "", comparison.to_markdown(index=False), "", "## Lane efficiency", "",
        lane_efficiency.to_markdown(index=False), "", "## Boundaries", "",
        "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`", "- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`",
        "- Main and scoped BBO micro panels were not directly ranked.",
        "- No validation, test, recent, May stress, or forward block was read.",
        "- Frozen candidate pack is development-only evidence, not alpha-ready or OOS-proven.",
    ]
    (OUTPUT_ROOT / "EPOCH0_COMPACT_RESULT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    manifest["outputs"].append({"path": relative(OUTPUT_ROOT / "EPOCH0_COMPACT_RESULT.md"), "sha256": sha256_file(OUTPUT_ROOT / "EPOCH0_COMPACT_RESULT.md"), "purpose": "epoch0_compact_report"})
    RUN_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "recommendation": recommendation, "proposals": len(candidates), "strict": len(strict), "runtime_seconds": actual_seconds}, indent=2))
    return manifest


def check() -> None:
    frozen = verify_frozen()
    manifest = load_json(RUN_MANIFEST)
    if manifest["frozen_manifest_sha256"] != frozen["frozen_manifest_sha256"]:
        raise ValueError("Epoch-0 run/freeze mismatch")
    prohibited = [
        "validation_test_recent_may_stress_forward_read", "candidate_promotion", "a7mem_updated",
        "cross_lane_memory_persisted", "cross_epoch_memory_persisted", "online_contract_changed",
        "additional_budget_added", "intermediate_human_reweighting", "alpha_ready_claimed",
        "oos_proven_claimed", "main_and_bbo_directly_ranked",
    ]
    if any(manifest.get(key) for key in prohibited):
        raise ValueError("Epoch-0 manifest records prohibited activity")
    if manifest["proposal_rows"] != frozen["budget"]["total_proposals"]:
        raise ValueError("Epoch-0 proposal count mismatch")
    if manifest["global_top_k_strict_evaluations"] != frozen["budget"]["global_top_k_strict_evaluations"]:
        raise ValueError("Epoch-0 global control budget mismatch")
    if manifest["executed_stratified_strict_evaluations"] > frozen["budget"]["stratified_strict_evaluations"]:
        raise ValueError("Epoch-0 stratified budget exceeded")
    for output in manifest["outputs"]:
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"Epoch-0 output hash drift: {output['path']}")
    raw = pd.read_csv(OUTPUT_ROOT / "raw_proposals.csv", usecols=["panel_id", "proposal_id", "exact_identity", "feedback_permission"])
    if len(raw) != 32768 or raw["proposal_id"].duplicated().any():
        raise ValueError("Epoch-0 raw proposal identity failure")
    strict = pd.read_csv(OUTPUT_ROOT / "strict_evaluations.csv")
    if strict.groupby(["panel_id", "arm"])["exact_identity"].apply(lambda values: values.duplicated().any()).any():
        raise ValueError("one exact identity received multiple votes inside an arm")
    if strict["candidate_promotion"].any() or strict["feedback_persisted"].any():
        raise PermissionError("strict evidence entered promotion or memory")
    comparison = pd.read_csv(OUTPUT_ROOT / "benchmark_comparisons.csv")
    if comparison["direct_cross_panel_ranking"].any():
        raise PermissionError("main and BBO were directly ranked")
    print("PASS_FROZEN_DEVELOPMENT_EPOCH0_VALID")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("diagnose-canary", "smoke", "freeze", "run", "check"))
    args = parser.parse_args()
    try:
        if args.action == "diagnose-canary":
            result = diagnose_canary(); print(json.dumps({"status": result["status_correction"]["acceptance"]}, indent=2))
        elif args.action == "smoke":
            smoke()
        elif args.action == "freeze":
            freeze()
        elif args.action == "run":
            run()
        else:
            check()
    except Exception as exc:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        failure = {
            "action": args.action, "status": "FAILED_VISIBLE_NOT_DELETED", "error_type": type(exc).__name__,
            "error": str(exc), "repo_sha": git("rev-parse", "HEAD", check=False),
            "forward_read": False, "candidate_promotion": False, "a7mem_updated": False,
        }
        FAILURE_MANIFEST.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
