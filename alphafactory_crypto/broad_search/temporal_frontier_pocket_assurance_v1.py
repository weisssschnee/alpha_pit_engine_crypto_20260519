"""Train-only anchor recovery and sparse/provenance diagnostics for pocket search."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from . import search_engine_v1 as engine
from .experiment_authority import resolve_search_economic_receipt
from .pair18m import PAIRED_DIAGNOSTIC_BLOCK_ROLE, evaluate_pair
from .panel18m import RawPanelStore
from .replay_v14_binance_target import BinanceTargetStore
from .temporal_frontier_pocket_v1 import ANCHORS, anchor_receipt, load_anchor_rows, rebuild_anchors
from .temporal_hypothesis_frontier_v1 import P5, P6
from .temporal_program_search_v1 import CONFIG_PATH, _limits
from .temporal_successor_v1 import verify_successor_market_inputs


BLOCK_PATH = "config/crypto_p1_g2_block_robust_ordering_v2.json"


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _shares(values: np.ndarray) -> dict[str, float]:
    ordered = np.sort(np.abs(np.asarray(values, dtype=float)))[::-1]
    total = float(ordered.sum())
    return {f"top_{n}_absolute_share": float(ordered[:n].sum() / total) if total else 0.0 for n in (1, 3, 5, 10)}


def _event_clusters(mask: np.ndarray) -> list[np.ndarray]:
    indexes = np.flatnonzero(mask)
    if not len(indexes):
        return []
    groups = np.split(indexes, np.flatnonzero(np.diff(indexes) > 1) + 1)
    return [value for value in groups if len(value)]


def _sleeve_net(paths: Mapping[str, Any]) -> dict[str, np.ndarray]:
    sleeves = dict(paths["sleeves"])
    return {
        name: np.asarray(sleeves[name]["net"], dtype=float)
        for name in ("primary_minus_left_control", "primary_minus_right_control")
    }


def _p5_diagnostic(store: BinanceTargetStore, candidate: Any, paths: Mapping[str, Any], blocks: list[Mapping[str, Any]]) -> dict[str, Any]:
    timestamps = np.asarray(paths["timestamp_ns"], dtype=np.int64)
    all_timestamps = np.asarray(store.timestamp_ns, dtype=np.int64)
    indexes = np.searchsorted(all_timestamps, timestamps)
    raw = np.asarray(store.field("trade_count_gt_1m")[:, indexes], dtype=float)
    finite = np.isfinite(raw)
    nonzero = finite & (np.abs(raw) > 0.0)
    event_hour = np.any(nonzero, axis=0)
    denominator = candidate.expression.inputs[1]
    from .expression import materialize_expression
    denominator_values = materialize_expression(
        denominator,
        registry=engine._WORKER_REGISTRY,
        field_reader=lambda field: np.asarray(store.field(field)[:, indexes], dtype=float),
    )
    denominator_differs = np.isfinite(denominator_values) & (np.abs(denominator_values) > 1.0e-12)
    states = np.sum(nonzero, axis=0)
    _, counts = np.unique(states, return_counts=True)
    probabilities = counts / max(int(counts.sum()), 1)
    entropy = float(-(probabilities * np.log2(probabilities)).sum())
    expanded = event_hour.copy()
    for lag in range(1, 73):
        expanded[lag:] |= event_hour[:-lag]
        expanded[:-lag] |= event_hour[lag:]
    nets = _sleeve_net(paths)
    timestamp_dt = pd.to_datetime(timestamps, utc=True)
    block_results = []
    all_event_destroyed = 0
    largest_cluster_destroyed = 0
    clusters = _event_clusters(event_hour)
    cluster_scores = []
    combined = np.nanmean(np.vstack(list(nets.values())), axis=0)
    for cluster in clusters:
        cluster_scores.append((float(np.nansum(np.abs(combined[cluster]))), cluster))
    largest = max(cluster_scores, key=lambda value: value[0])[1] if cluster_scores else np.array([], dtype=int)
    largest_mask = np.zeros(len(event_hour), dtype=bool)
    largest_mask[largest] = True
    for block in blocks:
        inside = np.asarray((timestamp_dt >= pd.Timestamp(block["start"])) & (timestamp_dt < pd.Timestamp(block["end_exclusive"])))
        metrics = {}
        event_ok = True
        cluster_ok = True
        for name, values in nets.items():
            base = float(np.nanmean(values[inside]))
            without_events = float(np.nanmean(values[inside & ~event_hour]))
            without_cluster = float(np.nanmean(values[inside & ~largest_mask]))
            metrics[name] = {"base_net_mean": base, "leave_all_event_hours_out_net_mean": without_events, "leave_largest_event_cluster_out_net_mean": without_cluster}
            event_ok &= without_events > 0.0
            cluster_ok &= without_cluster > 0.0
        if not event_ok:
            all_event_destroyed += 1
        if not cluster_ok:
            largest_cluster_destroyed += 1
        block_results.append({"block_id": block["block_id"], "event_hours": int((inside & event_hour).sum()), "expanded_event_hours": int((inside & expanded).sum()), "metrics": metrics})
    finite_combined = np.isfinite(combined)
    denominator_abs = float(np.nansum(np.abs(combined[finite_combined])))
    exact_share = float(np.nansum(np.abs(combined[event_hour])) / denominator_abs) if denominator_abs else 0.0
    expanded_share = float(np.nansum(np.abs(combined[expanded])) / denominator_abs) if denominator_abs else 0.0
    coordinate_fraction = float(nonzero.sum() / max(int(finite.sum()), 1))
    artifact = coordinate_fraction <= 0.001 and expanded_share >= 0.50 and max(all_event_destroyed, largest_cluster_destroyed) >= 2
    classification = "P5_SPARSE_FIELD_ARTIFACT_RISK" if artifact else "P5_RARE_EVENT_POCKET" if coordinate_fraction <= 0.01 or expanded_share >= 0.35 else "P5_STRUCTURAL_POCKET"
    return {
        "classification": classification,
        "raw_finite_coordinates": int(finite.sum()),
        "raw_nonzero_coordinates": int(nonzero.sum()),
        "raw_nonzero_fraction": coordinate_fraction,
        "nonzero_event_hours": int(event_hour.sum()),
        "nonzero_event_hour_fraction": float(event_hour.mean()),
        "state_unique_count": int(len(counts)),
        "state_entropy_bits": entropy,
        "denominator_nonzero_coordinates": int(denominator_differs.sum()),
        "denominator_differs_all_zero_fraction": float(denominator_differs.mean()),
        "matched_incremental_absolute_pnl_on_event_hours_share": exact_share,
        "matched_incremental_absolute_pnl_within_72h_event_share": expanded_share,
        "event_cluster_count": len(clusters),
        "leave_all_event_hours_out_destroyed_blocks": all_event_destroyed,
        "leave_largest_event_cluster_out_destroyed_blocks": largest_cluster_destroyed,
        "block_results": block_results,
    }


def _p6_diagnostic(store: BinanceTargetStore, candidate: Any, paths: Mapping[str, Any], blocks: list[Mapping[str, Any]]) -> dict[str, Any]:
    timestamps = np.asarray(paths["timestamp_ns"], dtype=np.int64)
    all_timestamps = np.asarray(store.timestamp_ns, dtype=np.int64)
    indexes = np.searchsorted(all_timestamps, timestamps)
    raw = np.asarray(store.field("bybit__funding_rate_mean")[:, indexes], dtype=float)
    finite = np.isfinite(raw)
    transition = np.any(np.diff(np.sign(np.nan_to_num(raw)), axis=1) != 0, axis=0)
    transition = np.r_[False, transition]
    primary = dict(paths["sleeves"]["primary"])
    asset = np.nansum(np.asarray(primary["asset_gross_contribution"], dtype=float), axis=1)
    symbols = list(paths["asset_ids"])
    ranked = sorted(zip(symbols, np.abs(asset)), key=lambda value: (-value[1], value[0]))
    total = float(sum(value for _, value in ranked))
    timestamp_dt = pd.to_datetime(timestamps, utc=True)
    coverage = []
    for block in blocks:
        inside = np.asarray((timestamp_dt >= pd.Timestamp(block["start"])) & (timestamp_dt < pd.Timestamp(block["end_exclusive"])))
        coverage.append({
            "block_id": block["block_id"],
            "finite_coordinate_fraction": float(finite[:, inside].mean()),
            "assets_with_any_coverage": int(np.any(finite[:, inside], axis=1).sum()),
            "transition_hours": int((transition & inside).sum()),
        })
    jumps = np.abs(np.diff(np.nanmedian(raw, axis=0)))
    finite_jumps = jumps[np.isfinite(jumps)]
    discontinuity = float(np.quantile(finite_jumps, 0.999)) if len(finite_jumps) else None
    return {
        "venue": "BYBIT",
        "field": "bybit__funding_rate_mean",
        "block_coverage": coverage,
        "transition_hours": int(transition.sum()),
        "transition_hour_fraction": float(transition.mean()),
        "source_discontinuity_abs_diff_q999": discontinuity,
        "asset_contribution_concentration": _shares(asset),
        "top_asset_contributors": [{"asset": symbol, "absolute_share": float(value / total) if total else 0.0} for symbol, value in ranked[:10]],
        "symbol_subset_dependence_top_5_absolute_share": float(sum(value for _, value in ranked[:5]) / total) if total else 0.0,
        "event_cluster_dependence_transition_hour_absolute_pnl_share": float(np.nansum(np.abs(np.asarray(primary["net"])[transition])) / max(float(np.nansum(np.abs(np.asarray(primary["net"])))), 1.0e-12)),
    }


def run_assurance(repo_root: Path, *, frontier_ledger: Path, output_path: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    market = verify_successor_market_inputs(root)
    ledger_sha = _file_sha(frontier_ledger)
    rows = load_anchor_rows(frontier_ledger)
    config = engine._read_json(root / CONFIG_PATH)
    economic = resolve_search_economic_receipt(root, str(config["source_authorities"]["economic_receipt_template"]))
    train = dict(economic["evidence_partition"]["train"])
    _, contracts, behavior, identities, _ = engine._load_v14_inputs(root, behavior_window=train)
    registry = engine.TypedExpressionRegistry(contracts, **_limits(config))
    candidates = rebuild_anchors(registry, rows)
    receipt = anchor_receipt(rows, candidates, ledger_sha256=ledger_sha)
    cache_root = root / str(identities["raw_cache"]["root"])
    target_root = root / str(economic["execution"]["target_cache_path"])
    store = BinanceTargetStore(RawPanelStore.open(cache_root), target_root)
    block_contract = engine._read_json(root / BLOCK_PATH)
    engine._worker_initialize(str(cache_root), engine._contracts_payload(contracts), behavior, str(train["start"]), str(train["end_exclusive"]), PAIRED_DIAGNOSTIC_BLOCK_ROLE, economic, True, block_contract, None, _limits(config))
    paths = {}
    evaluations = {}
    for family, candidate in candidates.items():
        evaluation = evaluate_pair(store=store, registry=registry, candidate=candidate, block_start=str(train["start"]), block_end=str(train["end_exclusive"]), block_role=PAIRED_DIAGNOSTIC_BLOCK_ROLE, behavior_contract=behavior, economic_receipt=economic, include_control_provenance=True, optimizer_block_contract=block_contract, include_paired_diagnostic_paths=True)
        if not bool(evaluation["matched_positive"]) or int(evaluation["block_robust_ordering"]["replicated_positive_block_count"]) != 3:
            raise RuntimeError(f"FRONTIER_ANCHOR_DETERMINISTIC_REPLAY_CHANGED:{family}")
        paths[family] = evaluation.pop("_paired_diagnostic_paths")
        evaluations[family] = {"candidate_id": candidate.candidate_id, "matched_positive": True, "search_reward": float(evaluation["search_reward"]), "pair_reward": float(evaluation["pair_reward"]), "replicated_positive_block_count": 3, "block_robust_ordering_sha256": _sha(evaluation["block_robust_ordering"])}
    p5 = _p5_diagnostic(store, candidates[P5], paths[P5], list(block_contract["blocks"]))
    p6 = _p6_diagnostic(store, candidates[P6], paths[P6], list(block_contract["blocks"]))
    core = {
        "schema_version": 1,
        "status": "FRONTIER_POCKET_PREAUTH_ASSURANCE_PASS",
        "market_preflight_sha256": _sha(market),
        "anchor_receipt": receipt,
        "deterministic_anchor_replays": evaluations,
        "p5_sparse_event_falsification": p5,
        "p6_field_and_provenance_assurance": p6,
        "live_initial_pockets": [P6] + ([] if p5["classification"] == "P5_SPARSE_FIELD_ARTIFACT_RISK" else [P5]),
        "new_strict": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    result = {**core, "assurance_receipt_sha256": _sha(core)}
    engine._write_json(output_path, result)
    return result


__all__ = ["run_assurance"]
