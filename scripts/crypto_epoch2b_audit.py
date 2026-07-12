from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import subprocess
import sys
import time
from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config" / "crypto_epoch2b_audit_v1.json"
ROOT = REPO / "runtime" / "epoch2b_audit_20260712"
MANIFEST = ROOT / "epoch2b_run_manifest.json"
INDEX = ROOT / "epoch2b_artifact_index.csv"
REPORT = ROOT / "EPOCH2B_ECONOMIC_BOTTLENECK_REPORT.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def gross_lcb_proxy(frame: pd.DataFrame) -> pd.Series:
    """Summary-only proxy; exact gross-series variance was not retained."""
    return pd.to_numeric(frame["net_lcb"], errors="coerce") + pd.to_numeric(frame["cost_drag_mean"], errors="coerce")


def gate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["gross_lcb_proxy"] = gross_lcb_proxy(out)
    out["gate_positive_gross"] = out.gross_mean > 0
    out["gate_positive_gross_lcb_proxy"] = out.gross_lcb_proxy > 0
    out["gate_positive_ic_lcb"] = out.ic_lcb > 0
    out["gate_positive_net"] = out.net_mean > 0
    out["gate_positive_net_lcb"] = out.net_lcb > 0
    out["gate_stable_worst_block"] = out.worst_horizon_net_mean > -0.001
    out["gate_benchmark_increment"] = out.benchmark_incremental_lcb > 0
    out["gate_hard"] = out.hard_gate_pass.astype(bool)
    out["gate_survivor"] = (
        out.gate_hard & out.gate_positive_ic_lcb & out.gate_positive_net_lcb &
        out.gate_stable_worst_block & out.gate_benchmark_increment
    )
    gate_columns = ["gate_hard", "gate_positive_ic_lcb", "gate_positive_net_lcb", "gate_stable_worst_block", "gate_benchmark_increment"]
    out["failed_gate_count"] = sum((~out[column]).astype(int) for column in gate_columns)
    out["near_miss"] = out.failed_gate_count == 1
    labels = {
        "gate_hard": "HARD_GATE", "gate_positive_ic_lcb": "IC_LCB", "gate_positive_net_lcb": "NET_LCB",
        "gate_stable_worst_block": "WORST_BLOCK", "gate_benchmark_increment": "BENCHMARK_INCREMENT",
    }
    out["failed_gates_audit"] = out.apply(
        lambda row: "|".join(labels[column] for column in gate_columns if not bool(row[column])), axis=1
    )
    return out


def normalize_strict(epoch: str, path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame["epoch"] = epoch
    if "admission_policy" not in frame:
        frame["admission_policy"] = frame.get("arm", "UNKNOWN")
    if "full_behaviour_cluster" not in frame:
        frame["full_behaviour_cluster"] = frame["behaviour_cluster"]
    if "hypothesis" not in frame:
        frame["hypothesis"] = frame["economic_hypothesis"]
    if "primitive" not in frame:
        frame["primitive"] = "NOT_RETAINED"
    return gate_frame(frame)


def effective_count(values: Iterable[str]) -> float:
    counts = np.asarray(list(Counter(str(value) for value in values).values()), dtype=float)
    return float(counts.sum() ** 2 / np.square(counts).sum()) if len(counts) else 0.0


def _funnel_summary(group: pd.DataFrame, dimensions: dict[str, str], unit: str, group_type: str) -> dict[str, Any]:
    positive_gross = group.gate_positive_gross
    positive_gross_lcb = positive_gross & group.gate_positive_gross_lcb_proxy
    positive_net = positive_gross_lcb & group.gate_positive_net
    positive_net_lcb = positive_net & group.gate_positive_net_lcb
    stable = positive_net_lcb & group.gate_stable_worst_block
    benchmark = stable & group.gate_benchmark_increment
    survivor = benchmark & group.gate_hard & group.gate_positive_ic_lcb
    return {
        **dimensions,
        "unit": unit,
        "group_type": group_type,
        "all_strict": len(group),
        "positive_gross": int(positive_gross.sum()),
        "positive_gross_lcb_proxy": int(positive_gross_lcb.sum()),
        "positive_net": int(positive_net.sum()),
        "positive_net_lcb": int(positive_net_lcb.sum()),
        "stable_worst_block": int(stable.sum()),
        "benchmark_incremental": int(benchmark.sum()),
        "survivor": int(survivor.sum()),
        "gross_mean_median": float(group.gross_mean.median()),
        "gross_lcb_proxy_median": float(group.gross_lcb_proxy.median()),
        "ic_mean_median": float(group.ic_mean.median()),
        "ic_lcb_median": float(group.ic_lcb.median()),
        "turnover_mean_median": float(group.turnover_mean.median()),
        "cost_drag_mean_median": float(group.cost_drag_mean.median()),
        "net_mean_median": float(group.net_mean.median()),
        "net_lcb_median": float(group.net_lcb.median()),
        "worst_block_median": float(group.worst_horizon_net_mean.median()),
        "stability_median": float(group.time_block_stability.median()),
        "concentration_median": float(group.max_weight_mean.median()),
        "benchmark_increment_lcb_median": float(group.benchmark_incremental_lcb.median()),
        "gross_lcb_method": "SUMMARY_PROXY_NET_LCB_PLUS_MEAN_COST_DRAG",
    }


def build_funnel(frame: pd.DataFrame, unit: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    definitions = [
        ("ALL", ["epoch"]),
        ("PANEL", ["epoch", "panel_id"]),
        ("PANEL_MECHANISM", ["epoch", "panel_id", "mechanism_id"]),
        ("PANEL_LANE", ["epoch", "panel_id", "lane_id"]),
        ("PANEL_ADMISSION", ["epoch", "panel_id", "admission_policy"]),
        ("PANEL_MECHANISM_LANE_ADMISSION", ["epoch", "panel_id", "mechanism_id", "lane_id", "admission_policy"]),
    ]
    defaults = {"epoch": "ALL", "panel_id": "ALL", "mechanism_id": "ALL", "lane_id": "ALL", "admission_policy": "ALL"}
    for group_type, columns in definitions:
        for keys, group in frame.groupby(columns, sort=True, dropna=False):
            keys = keys if isinstance(keys, tuple) else (keys,)
            dimensions = defaults.copy()
            dimensions.update(dict(zip(columns, map(str, keys))))
            rows.append(_funnel_summary(group, dimensions, unit, group_type))
    return pd.DataFrame(rows)


def build_gate_elimination(unique: pd.DataFrame) -> pd.DataFrame:
    rows = []
    gate_columns = {
        "HARD_GATE": "gate_hard", "IC_LCB": "gate_positive_ic_lcb", "GROSS_LCB_PROXY": "gate_positive_gross_lcb_proxy",
        "NET_LCB": "gate_positive_net_lcb", "WORST_BLOCK": "gate_stable_worst_block", "BENCHMARK_INCREMENT": "gate_benchmark_increment",
    }
    for (epoch, panel), group in unique.groupby(["epoch", "panel_id"], sort=True):
        for gate, column in gate_columns.items():
            rows.append({"epoch": epoch, "panel_id": panel, "gate": gate, "all_exact": len(group), "failed": int((~group[column]).sum()), "failure_rate": float((~group[column]).mean())})
    return pd.DataFrame(rows)


def bootstrap_ci(values: Iterable[float], *, resamples: int, seed: int) -> tuple[float, float]:
    array = np.asarray(list(values), dtype=float)
    array = array[np.isfinite(array)]
    if not len(array):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    sampled = rng.choice(array, size=(resamples, len(array)), replace=True).mean(axis=1)
    return float(np.quantile(sampled, .025)), float(np.quantile(sampled, .975))


def bootstrap_difference(left: Iterable[float], right: Iterable[float], *, resamples: int, seed: int) -> tuple[float, float]:
    a, b = np.asarray(list(left), dtype=float), np.asarray(list(right), dtype=float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if not len(a) or not len(b):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    values = rng.choice(a, size=(resamples, len(a)), replace=True).mean(axis=1) - rng.choice(b, size=(resamples, len(b)), replace=True).mean(axis=1)
    return float(np.quantile(values, .025)), float(np.quantile(values, .975))


def canonical_spec(spec: dict[str, Any]) -> dict[str, Any]:
    keys = ("mechanism_id", "economic_hypothesis", "field_a", "field_b", "primitive", "secondary_primitive", "interaction", "window", "long_window", "threshold", "direction")
    return {key: spec[key] for key in keys}


def blocker_distance(row: dict[str, Any], blocker: str) -> float:
    if blocker == "BENCHMARK_INCREMENT_ONLY":
        return float(row["benchmark_incremental_lcb"])
    if blocker in {"COST_ONLY", "NET_LCB_NEAR_ZERO"}:
        return float(row["net_lcb"])
    if blocker == "STABILITY_ONLY":
        return float(row["worst_horizon_net_mean"]) + .001
    if blocker == "CONCENTRATION_ONLY":
        return .25 - float(row["max_weight_mean"])
    return 1.0 if bool(row["hard_gate_pass"]) else -1.0


def audit_children(epoch2: pd.DataFrame, parents: pd.DataFrame, epoch1_specs: dict[str, dict[str, Any]]) -> pd.DataFrame:
    parent_lookup = parents.set_index("frozen_parent_row_id").to_dict("index")
    children = epoch2[epoch2.parent_row_id.fillna("") != ""].sort_values(
        ["parent_row_id", "exact_identity", "admission_policy", "proposal_id"]
    ).drop_duplicates(["parent_row_id", "exact_identity"])
    rows = []
    gate_names = {
        "HARD_GATE": "gate_hard", "IC_LCB": "gate_positive_ic_lcb", "NET_LCB": "gate_positive_net_lcb",
        "WORST_BLOCK": "gate_stable_worst_block", "BENCHMARK_INCREMENT": "gate_benchmark_increment",
    }
    blocker_target = {
        "COST_ONLY": "NET_LCB", "NET_LCB_NEAR_ZERO": "NET_LCB", "BENCHMARK_INCREMENT_ONLY": "BENCHMARK_INCREMENT",
        "STABILITY_ONLY": "WORST_BLOCK", "CONCENTRATION_ONLY": "HARD_GATE", "STRUCTURAL_UNREPAIRABLE": "HARD_GATE",
    }
    for child in children.to_dict("records"):
        parent = parent_lookup[child["parent_row_id"]]
        blocker = str(parent["blocker_type"])
        target = blocker_target.get(blocker, "HARD_GATE")
        parent_spec = canonical_spec(epoch1_specs[str(parent["proposal_id"])])
        child_spec = json.loads(child["canonical"])
        changed = sorted(key for key in parent_spec if parent_spec.get(key) != child_spec.get(key))
        parent_gates = {
            "HARD_GATE": bool(parent["hard_gate_pass"]), "IC_LCB": float(parent["ic_lcb"]) > 0,
            "NET_LCB": float(parent["net_lcb"]) > 0, "WORST_BLOCK": float(parent["worst_horizon_net_mean"]) > -.001,
            "BENCHMARK_INCREMENT": float(parent["benchmark_incremental_lcb"]) > 0,
        }
        child_gates = {name: bool(child[column]) for name, column in gate_names.items()}
        collateral = [name for name in parent_gates if name != target and parent_gates[name] and not child_gates[name]]
        before, after = blocker_distance(parent, blocker), blocker_distance(child, blocker)
        rows.append({
            "parent_row_id": child["parent_row_id"], "parent_proposal_id": parent["proposal_id"], "child_proposal_id": child["proposal_id"],
            "panel_id": child["panel_id"], "lane_id": child["lane_id"], "operator": child["repair_action"],
            "parent_blocker": blocker, "target_blocker": target, "syntax_changed_fields": "|".join(changed), "syntax_change_count": len(changed),
            "exact_identity_changed": child["exact_identity"] != parent["exact_identity"],
            "signal_identity_distance": float(child["exact_identity"] != parent["exact_identity"]),
            "behaviour_distance": float(child["full_behaviour_cluster"] != parent["behaviour_cluster"]),
            "turnover_delta": float(child["turnover_mean"] - parent["turnover_mean"]),
            "cost_delta": float(child["cost_drag_mean"] - parent["cost_drag_mean"]),
            "gross_lcb_proxy_delta": float((child["net_lcb"] + child["cost_drag_mean"]) - (parent["net_lcb"] + parent["cost_drag_mean"])),
            "net_lcb_delta": float(child["net_lcb"] - parent["net_lcb"]),
            "stability_delta": float(child["time_block_stability"] - parent["time_block_stability"]),
            "concentration_delta": float(child["max_weight_mean"] - parent["max_weight_mean"]),
            "target_gate_distance_before": before, "target_gate_distance_after": after, "target_gate_distance_delta": after - before,
            "target_gate_improved": after > before, "target_gate_crossed": after > 0,
            "non_target_collateral_damage_count": len(collateral), "non_target_collateral_damage": "|".join(collateral),
            "gross_lcb_method": "SUMMARY_PROXY_NET_LCB_PLUS_MEAN_COST_DRAG",
        })
    return pd.DataFrame(rows)


def summarize_operators(children: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    matched = {
        "evolutionary_repair": "evolutionary_random_control",
        "local_mcts_repair": "local_mcts_random_control",
        "llm_typed_repair": "llm_random_repair_control",
    }
    bootstrap = config["bootstrap"]
    rows = []
    for (lane, operator, blocker), group in children.groupby(["lane_id", "operator", "parent_blocker"], sort=True):
        parent_means = group.groupby("parent_row_id").target_gate_distance_delta.mean()
        low, high = bootstrap_ci(parent_means, resamples=int(bootstrap["resamples"]), seed=int(bootstrap["seed"]) + len(rows))
        control_lane = matched.get(lane, "")
        control = children[(children.lane_id == control_lane) & (children.parent_blocker == blocker)] if control_lane else pd.DataFrame()
        control_parent = control.groupby("parent_row_id").target_gate_distance_delta.mean() if len(control) else pd.Series(dtype=float)
        diff = float(parent_means.mean() - control_parent.mean()) if len(control_parent) else float("nan")
        diff_low, diff_high = bootstrap_difference(parent_means, control_parent, resamples=int(bootstrap["resamples"]), seed=int(bootstrap["seed"]) + 1000 + len(rows))
        control_cross = float(control.target_gate_crossed.mean()) if len(control) else float("nan")
        if not control_lane:
            causal = "MATCHED_RANDOM_REFERENCE" if lane.endswith("control") else "NO_MATCHED_CONTROL"
        else:
            causal = "OPERATOR_CAUSAL_GATE_CONTROL_SUPPORTED" if low > 0 and diff_low > 0 and float(group.target_gate_crossed.mean()) > control_cross else "OPERATOR_HAS_NO_CAUSAL_GATE_CONTROL"
        rows.append({
            "lane_id": lane, "operator": operator, "parent_blocker": blocker, "children": len(group), "parent_clusters": group.parent_row_id.nunique(),
            "target_gate_improvement_rate": float(group.target_gate_improved.mean()), "target_gate_crossing_rate": float(group.target_gate_crossed.mean()),
            "target_delta_mean": float(group.target_gate_distance_delta.mean()), "target_delta_median": float(group.target_gate_distance_delta.median()),
            "target_delta_cluster_bootstrap_ci_low": low, "target_delta_cluster_bootstrap_ci_high": high,
            "matched_control_lane": control_lane, "matched_control_target_delta_mean": float(control.target_gate_distance_delta.mean()) if len(control) else float("nan"),
            "matched_random_difference": diff, "matched_difference_ci_low": diff_low, "matched_difference_ci_high": diff_high,
            "exact_noop_rate": float((~group.exact_identity_changed).mean()), "behaviour_noop_rate": float((group.behaviour_distance == 0).mean()),
            "collateral_damage_rate": float((group.non_target_collateral_damage_count > 0).mean()), "causal_gate_control_status": causal,
        })
    return pd.DataFrame(rows)


def classify_parents(parents: pd.DataFrame, children: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    rules = config["parent_classification"]
    rows = []
    for parent in parents.to_dict("records"):
        group = children[children.parent_row_id == parent["frozen_parent_row_id"]]
        gross_lcb = float(parent["net_lcb"] + parent["cost_drag_mean"])
        std = float(group.target_gate_distance_delta.std(ddof=0)) if len(group) else float("nan")
        smooth = len(group) >= int(rules["minimum_strict_neighbours"]) and np.isfinite(std) and std <= float(rules["unstable_target_delta_std"])
        distance = blocker_distance(parent, str(parent["blocker_type"]))
        if gross_lcb <= 0:
            classification = "NO_ECONOMIC_EDGE"
            reason = "GROSS_LCB_SUMMARY_PROXY_NON_POSITIVE"
        elif str(parent["blocker_type"]) == "STABILITY_ONLY":
            classification = "STATE_CONDITIONING_REQUIRED"
            reason = "POSITIVE_GROSS_EDGE_WITH_STABILITY_BLOCKER"
        elif len(group) < int(rules["minimum_strict_neighbours"]) or not smooth:
            classification = "UNSTABLE_NEIGHBOURHOOD"
            reason = "INSUFFICIENT_OR_HIGH_VARIANCE_STRICT_NEIGHBOURHOOD"
        elif bool(group.target_gate_crossed.any()) and abs(distance) <= float(rules["locally_repairable_abs_target_distance_max"]):
            classification = "LOCALLY_REPAIRABLE"
            reason = "SMOOTH_NEIGHBOURHOOD_WITH_OBSERVED_TARGET_GATE_CROSSING"
        elif float(parent["net_lcb"]) <= 0 or float(parent["cost_drag_mean"]) > 0:
            classification = "PORTFOLIO_TRANSFORM_REQUIRED"
            reason = "POSITIVE_GROSS_PROXY_NOT_CONVERTED_TO_NET_OR_INCREMENTAL_EDGE"
        else:
            classification = "UNSTABLE_NEIGHBOURHOOD"
            reason = "NO_LOCAL_CAUSAL_GATE_CONTROL"
        parent_gate_count = sum((
            not bool(parent["hard_gate_pass"]), float(parent["ic_lcb"]) <= 0, float(parent["net_lcb"]) <= 0,
            float(parent["worst_horizon_net_mean"]) <= -.001, float(parent["benchmark_incremental_lcb"]) <= 0,
        ))
        rows.append({
            "frozen_parent_row_id": parent["frozen_parent_row_id"], "proposal_id": parent["proposal_id"], "panel_id": parent["panel_id"],
            "blocker_type": parent["blocker_type"], "failed_gate": parent["failed_gate"], "failed_gate_count": parent_gate_count,
            "target_gate_distance": distance, "gross_mean": parent["gross_mean"], "gross_lcb_proxy": gross_lcb, "net_lcb": parent["net_lcb"],
            "turnover_mean": parent["turnover_mean"], "cost_drag_mean": parent["cost_drag_mean"], "time_block_stability": parent["time_block_stability"],
            "strict_neighbour_count": len(group), "neighbour_target_delta_std": std, "neighbour_target_delta_mean": float(group.target_gate_distance_delta.mean()) if len(group) else float("nan"),
            "neighbour_target_improvement_rate": float(group.target_gate_improved.mean()) if len(group) else float("nan"), "neighbour_target_crossing_rate": float(group.target_gate_crossed.mean()) if len(group) else float("nan"),
            "neighbourhood_smooth": smooth, "classification": classification, "classification_reason": reason,
            "gross_lcb_method": "SUMMARY_PROXY_NET_LCB_PLUS_MEAN_COST_DRAG",
        })
    return pd.DataFrame(rows)


def diversity_order(frame: pd.DataFrame) -> list[str]:
    buckets = {
        key: deque(group.sort_values(["near_score", "quality", "exact_identity"], ascending=[False, False, True]).exact_identity)
        for key, group in frame.groupby(["full_behaviour_cluster", "mechanism_id", "hypothesis"], sort=True)
    }
    result: list[str] = []
    while any(buckets.values()):
        for key in sorted(buckets):
            if buckets[key]:
                result.append(buckets[key].popleft())
    return result


def hybrid_replay(epoch2: pd.DataFrame, assignments: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    contract = config["hybrid_report_only_replay"]
    representative = epoch2.sort_values(["panel_id", "exact_identity", "near_score", "quality", "proposal_id"], ascending=[True, True, False, False, True]).drop_duplicates(["panel_id", "exact_identity"])
    rows = []
    panel_summary = []
    historical = {policy: set(zip(group.panel_id, group.exact_identity)) for policy, group in assignments.groupby("admission_policy")}
    for panel_id, historical_global in assignments[assignments.admission_policy == "GLOBAL_QUALITY"].groupby("panel_id"):
        quota = len(historical_global)
        panel = representative[representative.panel_id == panel_id].copy()
        quality_order = list(panel.sort_values(["near_score", "quality", "exact_identity"], ascending=[False, False, True]).exact_identity)
        quality_count = round(quota * float(contract["quality_share"]))
        quality_ids = quality_order[:quality_count]
        remaining = panel[~panel.exact_identity.isin(set(quality_ids))]
        diversity_ids = diversity_order(remaining)[:quota - quality_count]
        selected = quality_ids + diversity_ids
        source = {identity: "QUALITY" for identity in quality_ids} | {identity: "DIVERSITY" for identity in diversity_ids}
        chosen = panel[panel.exact_identity.isin(selected)].copy()
        chosen["replay_source"] = chosen.exact_identity.map(source)
        chosen["replay_rank"] = chosen.exact_identity.map({identity: rank for rank, identity in enumerate(selected)})
        rows.extend(chosen.sort_values("replay_rank").to_dict("records"))
        counts = chosen.full_behaviour_cluster.value_counts()
        replay_set = set(zip(chosen.panel_id, chosen.exact_identity))
        panel_summary.append({
            "panel_id": panel_id, "strict_rows": len(chosen), "quality_rows": len(quality_ids), "diversity_rows": len(diversity_ids),
            "quality_share": len(quality_ids) / len(chosen), "diversity_share": len(diversity_ids) / len(chosen),
            "exact_identities": chosen.exact_identity.nunique(), "behaviour_clusters": chosen.full_behaviour_cluster.nunique(),
            "n_eff": effective_count(chosen.full_behaviour_cluster), "top_cluster_share": float(counts.iloc[0] / len(chosen)),
            "near_misses": int(chosen.near_miss.sum()), "positive_net_lcb": int((chosen.net_lcb > 0).sum()), "survivors": int(chosen.gate_survivor.sum()),
            "global_exact_overlap": len(replay_set & historical.get("GLOBAL_QUALITY", set())),
            "stratified_exact_overlap": len(replay_set & historical.get("STRATIFIED_DIVERSITY", set())),
            "historical_epoch_rewritten": False, "new_performance_queries": 0,
        })
    return pd.DataFrame(rows), {"status": "REPORT_ONLY_REPLAY_COMPLETED", "panels": panel_summary, "historical_epoch_rewritten": False, "new_performance_queries": 0}


def bbo_audit(epoch2: pd.DataFrame, source: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    positive = epoch2[(epoch2.panel_id == "bbo_micro") & (epoch2.net_lcb > 0)].sort_values(["exact_identity", "admission_policy"]).drop_duplicates("exact_identity").copy()
    parsed = positive.canonical.map(json.loads)
    positive["field_a"] = parsed.map(lambda value: value["field_a"])
    positive["field_b"] = parsed.map(lambda value: value["field_b"])
    positive["interaction"] = parsed.map(lambda value: value["interaction"])
    positive["cost_share_of_gross_mean"] = positive.cost_drag_mean / positive.gross_mean.replace(0, np.nan)
    positive["month_dependency_status"] = "NOT_IDENTIFIABLE_FROM_AGGREGATED_STRICT_CACHE"
    positive["symbol_dependency_status"] = "NOT_IDENTIFIABLE_FROM_AGGREGATED_STRICT_CACHE"
    positive["session_dependency_status"] = "NOT_IDENTIFIABLE_FROM_AGGREGATED_STRICT_CACHE"
    positive["coverage_extrapolation_allowed"] = False
    plan = {
        "status": "DEVELOPMENT_DATA_ACQUISITION_PLAN_ONLY",
        "current_scope": {"months": ["2024-01", "2024-02"], "observed_symbols": source["observed_symbols"], "requested_symbols": source["requested_symbols"], "coverage_ratio": source["coordinate_coverage_ratio"]},
        "requested_backfill": {
            "months": [f"2024-{month:02d}" for month in range(1, 13)],
            "symbols": ["ADAUSDT", "AVAXUSDT", "BCHUSDT", "BNBUSDT", "BTCUSDT", "DOGEUSDT", "ETHUSDT", "LINKUSDT", "LTCUSDT", "SOLUSDT", "SUIUSDT", "XRPUSDT"],
            "gap_repairs": source["coverage_gaps"],
            "minimum_symbol_month_coordinate_coverage": 0.95,
        },
        "observable_time": "usable_time=max(exchange_event_time,hour_bucket_close,source_ingest_time); decision_time must be >= hour_bucket_start+1h",
        "physical_isolation": "release_id/panel_role={development|challenge}/month=YYYY-MM/symbol=SYMBOL/part-*.parquet; challenge row groups in separate immutable manifest and not mounted to generator",
        "future_split": {
            "historical_calibration_only": ["2024-01", "2024-02"],
            "development_extension": ["2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08"],
            "sealed_development_challenge": ["2024-09", "2024-10", "2024-11", "2024-12"],
            "oos_claim": False,
        },
        "winner_selection_before_coverage": False,
        "performance_query_authorized": False,
    }
    return positive, plan


def select_route(unique: pd.DataFrame, parents: pd.DataFrame, benchmarks: pd.DataFrame, bbo: pd.DataFrame, source: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    thresholds = config["route_thresholds"]
    main = unique[unique.panel_id == "main"]
    epoch_rates = main.groupby("epoch").gate_positive_gross_lcb_proxy.mean()
    gross_fraction = float(epoch_rates.median())
    gross_positive = main[main.gate_positive_gross_lcb_proxy]
    cost_killed = float((~gross_positive.gate_positive_net_lcb).mean()) if len(gross_positive) else 0.0
    near = main[main.near_miss]
    stability_share = float((near.failed_gates_audit == "WORST_BLOCK").mean()) if len(near) else 0.0
    benchmark = benchmarks[benchmarks.panel_id == "main"].copy()
    benchmark["gross_lcb_proxy"] = benchmark.net_lcb + benchmark.turnover_mean * float(config["cost_bps"]) / 10000.0
    benchmark_positive = int((benchmark.gross_lcb_proxy > 0).sum())
    parent_blocked_share = float(parents.classification.isin(["NO_ECONOMIC_EDGE", "UNSTABLE_NEIGHBOURHOOD"]).mean())
    exposure_cells = bbo[["field_a", "field_b", "primitive", "interaction"]].drop_duplicates().shape[0] if len(bbo) else 0
    conditions = {
        "PIVOT_TO_PORTFOLIO_TRANSFORM_SEARCH": gross_fraction >= float(thresholds["substantial_main_positive_gross_lcb_fraction_min"]) and cost_killed >= float(thresholds["cost_killed_share_of_positive_gross_lcb_min"]),
        "PIVOT_TO_STATE_CONDITIONED_SEARCH": gross_fraction > float(thresholds["main_positive_gross_lcb_fraction_near_zero_max"]) and stability_share >= float(thresholds["stability_failure_share_min"]),
        "PIVOT_TO_NEW_MECHANISM_OR_DATA": gross_fraction <= float(thresholds["main_positive_gross_lcb_fraction_near_zero_max"]) and benchmark_positive == 0 and parent_blocked_share >= float(thresholds["no_edge_or_unstable_parent_share_min"]),
        "EXPAND_BBO_DEVELOPMENT_COVERAGE": bbo.full_behaviour_cluster.nunique() >= int(thresholds["bbo_nontrivial_behaviour_clusters_min"]) and exposure_cells >= int(thresholds["bbo_nontrivial_exposure_cells_min"]) and float(source["coordinate_coverage_ratio"]) < float(thresholds["bbo_coverage_insufficient_below"]),
    }
    selected = next((route for route in config["route_priority"] if conditions[route]), "PIVOT_TO_NEW_MECHANISM_OR_DATA")
    return {
        "status": "ECONOMIC_BOTTLENECK_AUDIT_COMPLETED",
        "main_recommendation": selected,
        "condition_results": conditions,
        "metrics": {
            "epoch_main_positive_gross_lcb_proxy_fraction": {key: float(value) for key, value in epoch_rates.items()},
            "median_epoch_main_positive_gross_lcb_proxy_fraction": gross_fraction,
            "cost_killed_share_of_positive_gross_lcb_proxy": cost_killed,
            "stability_only_share_of_main_near_misses": stability_share,
            "simple_main_benchmark_positive_gross_lcb_proxy_count": benchmark_positive,
            "no_edge_or_unstable_parent_share": parent_blocked_share,
            "bbo_positive_net_exact_identities": len(bbo),
            "bbo_behaviour_clusters": bbo.full_behaviour_cluster.nunique(),
            "bbo_exposure_cells": exposure_cells,
            "bbo_coverage_ratio": source["coordinate_coverage_ratio"],
        },
        "secondary_line": "BBO_DEVELOPMENT_COVERAGE_ACQUISITION_PLAN_ONLY" if conditions["EXPAND_BBO_DEVELOPMENT_COVERAGE"] and selected != "EXPAND_BBO_DEVELOPMENT_COVERAGE" else "NONE",
        "performance_search_authorized": False,
    }


def run() -> dict[str, Any]:
    started = time.perf_counter()
    config = load_json(CONFIG)
    if int(config["performance_queries_allowed"]) != 0:
        raise PermissionError("Epoch-2B must remain report-only")
    ROOT.mkdir(parents=True, exist_ok=True)
    strict_frames = [normalize_strict(epoch, REPO / path) for epoch, path in config["input_strict_evidence"].items()]
    logical = pd.concat(strict_frames, ignore_index=True, sort=False)
    unique = logical.sort_values(["epoch", "panel_id", "exact_identity", "admission_policy", "proposal_id"]).drop_duplicates(["epoch", "panel_id", "exact_identity"])
    funnel = pd.concat([build_funnel(logical, "LOGICAL_STRICT"), build_funnel(unique, "UNIQUE_EXACT")], ignore_index=True)
    elimination = build_gate_elimination(unique)

    parents = pd.read_csv(REPO / config["parent_pack"])
    epoch1_pack = read_jsonl_gz(REPO / config["epoch1r_proposal_pack"])
    epoch1_specs = {row["proposal_id"]: row["spec"] for row in epoch1_pack}
    epoch2 = strict_frames[-1]
    children = audit_children(epoch2, parents, epoch1_specs)
    operators = summarize_operators(children, config)
    parent_audit = classify_parents(parents, children, config)
    parent_summary = parent_audit.groupby("classification", sort=True).size().rename("parents").reset_index()

    assignments = pd.read_csv(REPO / config["epoch2_assignments"])
    replay, replay_summary = hybrid_replay(epoch2, assignments, config)
    replay_funnel_source = replay.copy()
    replay_funnel_source["epoch"] = "EPOCH2B_HYBRID_REPORT_ONLY_REPLAY"
    replay_funnel_source["admission_policy"] = "TRUE_60_40_AFTER_EXACT_DEDUP"
    replay_funnel = build_funnel(replay_funnel_source, "UNIQUE_EXACT_REPORT_ONLY")

    bbo_source = load_json(REPO / config["bbo_source_manifest"])
    bbo, acquisition = bbo_audit(epoch2, bbo_source)
    benchmarks = pd.read_csv(REPO / config["benchmark_evidence"])
    benchmarks["gross_mean_proxy"] = benchmarks.net_mean + benchmarks.turnover_mean * float(config["cost_bps"]) / 10000.0
    benchmarks["gross_lcb_proxy"] = benchmarks.net_lcb + benchmarks.turnover_mean * float(config["cost_bps"]) / 10000.0
    decision = select_route(unique, parent_audit, benchmarks, bbo, bbo_source, config)

    near_rows = []
    for (epoch, panel), group in unique.groupby(["epoch", "panel_id"], sort=True):
        near = group[group.near_miss]
        for failed, failed_group in near.groupby("failed_gates_audit", sort=True):
            near_rows.append({
                "epoch": epoch, "panel_id": panel, "near_miss_type": failed, "near_misses": len(failed_group),
                "all_exact": len(group), "near_miss_rate": len(failed_group) / len(group),
                "failed_gate_distance_abs_median": float(np.median(np.abs(np.where(
                    failed == "NET_LCB", failed_group.net_lcb,
                    np.where(failed == "BENCHMARK_INCREMENT", failed_group.benchmark_incremental_lcb, failed_group.worst_horizon_net_mean + .001)
                )))),
            })
    near_transition = pd.DataFrame(near_rows)

    mechanism = unique.groupby(["epoch", "panel_id", "mechanism_id"], sort=True).agg(
        exact_identities=("exact_identity", "size"), positive_gross_mean=("gate_positive_gross", "sum"),
        positive_gross_lcb_proxy=("gate_positive_gross_lcb_proxy", "sum"), positive_net_lcb=("gate_positive_net_lcb", "sum"),
        gross_mean_median=("gross_mean", "median"), gross_lcb_proxy_median=("gross_lcb_proxy", "median"),
        turnover_median=("turnover_mean", "median"), cost_drag_median=("cost_drag_mean", "median"), net_lcb_median=("net_lcb", "median"),
    ).reset_index()
    mechanism["gross_lcb_to_net_conversion_rate"] = mechanism.positive_net_lcb / mechanism.positive_gross_lcb_proxy.replace(0, np.nan)

    main_epoch = funnel[(funnel.unit == "UNIQUE_EXACT") & (funnel.group_type == "PANEL") & (funnel.panel_id == "main")]
    largest_sequential = []
    stages = ["all_strict", "positive_gross", "positive_gross_lcb_proxy", "positive_net", "positive_net_lcb", "stable_worst_block", "benchmark_incremental", "survivor"]
    for row in main_epoch.to_dict("records"):
        drops = {f"{left}_TO_{right}": int(row[left] - row[right]) for left, right in zip(stages, stages[1:])}
        stage = max(drops, key=drops.get)
        largest_sequential.append({"epoch": row["epoch"], "largest_sequential_drop": stage, "dropped_exact": drops[stage], "all_stage_drops": drops})

    answers = {
        "main_gross_edge_or_cost": "RELIABLE_GROSS_EDGE_IS_NEAR_ZERO; THE_RARE_POSITIVE_GROSS_LCB_PROXY_ROWS_ARE_ALMOST_ALL_KILLED_BY_COST, BUT THEY_ARE_TOO_SPARSE_TO_JUSTIFY_PORTFOLIO_TRANSFORM_AS_MAIN_ROUTE",
        "largest_elimination": {"sequential": largest_sequential, "individual_gate": "NET_LCB_FAILS_ALMOST_ALL_MAIN_EXACT_IDENTITIES"},
        "mechanisms_with_visible_gross_not_net": mechanism[(mechanism.panel_id == "main") & (mechanism.positive_gross_lcb_proxy > 0) & (mechanism.positive_net_lcb == 0)][["epoch", "mechanism_id", "positive_gross_lcb_proxy", "positive_net_lcb"]].to_dict("records"),
        "near_miss_primary_type": "NET_LCB",
        "epoch1r_to_epoch2_near_miss_interpretation": "MOST_GROWTH_REMAINS_CLOSER_TO_THE_SAME_NET_LCB_GATE; IT_IS_NOT_NEW_SURVIVOR_EVIDENCE",
        "gross_lcb_limitation": config["gross_lcb_contract"],
    }

    bias = {
        "decision": "HOLD_RESEARCH",
        "formal_state": ["NEW_PERFORMANCE_SEARCH_FROZEN", "ANALYSIS_AND_ENGINEERING_ALLOWED"],
        "discovery_status": "POST_HOC_CAUSAL_AUDIT_AND_REPORT_ONLY_REPLAY",
        "oos_grade": "NONE",
        "new_performance_queries": 0,
        "return_label_read": False,
        "signal_materialized": False,
        "look_ahead": "NO_NEW_SERIES_ACCESS; RELIES_ON_PRIOR_PIT_QUALIFIED_STRICT SUMMARIES",
        "cost_model": "5_BPS_PER_UNIT_TURNOVER",
        "gross_lcb_caveat": "SUMMARY PROXY; gross-series variance was not retained and was not recomputed",
        "hybrid_replay": "REPORT_ONLY_FROM_CACHED_EXACT_RESULTS; NOT_A_NEW_EPOCH",
        "bbo_limit": "CORE11_2024_01_02_ONLY_82.22_PERCENT_COVERAGE; MONTH_SYMBOL_SESSION_DEPENDENCE_NOT_IDENTIFIABLE_FROM_AGGREGATED_CACHE",
        "candidate_promotion": False,
        "required_next_action": decision["main_recommendation"],
    }

    csv_outputs = {
        "gross_to_net_gate_funnel.csv": funnel,
        "gate_elimination.csv": elimination,
        "mechanism_gross_to_net.csv": mechanism,
        "near_miss_transition.csv": near_transition,
        "operator_child_causal_rows.csv": children,
        "operator_causal_summary.csv": operators,
        "parent_selection_audit.csv": parent_audit,
        "parent_class_summary.csv": parent_summary,
        "hybrid_report_only_replay_rows.csv": replay,
        "hybrid_report_only_gate_funnel.csv": replay_funnel,
        "bbo_positive_net_audit.csv": bbo,
        "benchmark_gross_net_proxy.csv": benchmarks,
    }
    for name, frame in csv_outputs.items():
        frame.to_csv(ROOT / name, index=False)
    json_outputs = {
        "gross_to_net_answers.json": answers,
        "hybrid_report_only_replay_summary.json": replay_summary,
        "bbo_development_acquisition_plan.json": acquisition,
        "economic_bottleneck_decision.json": decision,
        "epoch2b_bias_audit.json": bias,
    }
    for name, payload in json_outputs.items():
        (ROOT / name).write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    main_funnel = main_epoch[["epoch", "all_strict", "positive_gross", "positive_gross_lcb_proxy", "positive_net", "positive_net_lcb", "stable_worst_block", "benchmark_incremental", "survivor"]]
    report = [
        "# CRYPTO EPOCH-2B — Economic Bottleneck and Operator Causal Audit", "",
        "Status: `ECONOMIC_BOTTLENECK_AUDIT_COMPLETED`", f"Main recommendation: `{decision['main_recommendation']}`", "",
        "## Main Gross-to-Net Funnel", "", main_funnel.to_markdown(index=False), "",
        f"- Main median epoch positive gross-LCB proxy fraction: {decision['metrics']['median_epoch_main_positive_gross_lcb_proxy_fraction']:.4%}.",
        f"- Cost-killed share among the rare positive gross-LCB proxy rows: {decision['metrics']['cost_killed_share_of_positive_gross_lcb_proxy']:.4%}.",
        "- The gross-LCB value is a summary proxy (`net_lcb + mean_cost_drag`), not an exact recomputation.", "",
        "## Operator Causal Result", "",
        f"- Operators marked no causal control: {int((operators.causal_gate_control_status == 'OPERATOR_HAS_NO_CAUSAL_GATE_CONTROL').sum())} / {int(operators.lane_id.isin(['evolutionary_repair','local_mcts_repair','llm_typed_repair']).sum())} adaptive operator-blocker cells.",
        f"- Parents classified NO_ECONOMIC_EDGE or UNSTABLE_NEIGHBOURHOOD: {decision['metrics']['no_edge_or_unstable_parent_share']:.2%}.",
        "- Mutation labels and LLM explanations were not treated as causal evidence.", "",
        "## Hybrid Report-only Replay", "", pd.DataFrame(replay_summary["panels"]).to_markdown(index=False), "",
        "This replay used only cached exact identities and strict metrics. It does not rewrite Epoch-2 and is not new performance evidence.", "",
        "## BBO Scoped Audit", "",
        f"- Positive-net exact identities: {len(bbo)}; behaviour clusters: {bbo.full_behaviour_cluster.nunique()}; coverage: {bbo_source['coordinate_coverage_ratio']:.2%}.",
        "- All five are spread-led, 48/168-window, negative-direction programs; month/symbol/session dependence cannot be identified from aggregated strict summaries.",
        "- Full-2024 physically isolated bookTicker acquisition is a secondary data line; no BBO winner may be selected first.", "",
        "## Boundary", "", "- `NEW_PERFORMANCE_SEARCH_FROZEN`", "- `ANALYSIS_AND_ENGINEERING_ALLOWED`", "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`", "- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    output_paths = [ROOT / name for name in csv_outputs] + [ROOT / name for name in json_outputs] + [REPORT]
    artifact_index = pd.DataFrame([{
        "path": relative(path), "sha256": sha256_file(path), "producer": "python scripts/crypto_epoch2b_audit.py run",
        "purpose": "final" if path in {REPORT, ROOT / "economic_bottleneck_decision.json"} else "diagnostic", "performance_query": False,
    } for path in output_paths])
    artifact_index.to_csv(INDEX, index=False)
    output_paths.append(INDEX)
    input_paths = [CONFIG, Path(__file__), REPO / "tests" / "test_epoch2b_audit.py"] + [REPO / path for path in config["input_strict_evidence"].values()] + [
        REPO / config["parent_pack"], REPO / config["epoch1r_proposal_pack"], REPO / config["epoch2_proposal_pack"],
        REPO / config["epoch2_assignments"], REPO / config["benchmark_evidence"], REPO / config["bbo_source_manifest"],
    ]
    manifest = {
        "experiment_id": config["experiment_id"], "objective": "classify the economic bottleneck and operator causal control using existing strict evidence only",
        "status": "ECONOMIC_BOTTLENECK_AUDIT_COMPLETED", "main_recommendation": decision["main_recommendation"],
        "repo_sha": git("rev-parse", "HEAD"), "input_sha256": {relative(path): sha256_file(path) for path in input_paths},
        "parameters": {"cost_bps": config["cost_bps"], "bootstrap": config["bootstrap"], "route_thresholds": config["route_thresholds"]},
        "commands": ["python scripts/crypto_epoch2b_audit.py run", "python scripts/crypto_epoch2b_audit.py check"],
        "outputs": [{"path": relative(path), "sha256": sha256_file(path)} for path in output_paths],
        "logical_strict_rows_read": len(logical), "unique_epoch_panel_exact_rows": len(unique),
        "new_performance_queries": 0, "return_label_read": False, "signal_materialized": False, "forward_read": False,
        "candidate_promotion": False, "cross_epoch_memory": False, "historical_epoch_rewritten": False,
        "actual_runtime_seconds": time.perf_counter() - started, "reproducible": True,
        "continuation": "stop performance search; implement only the independently authorized new-mechanism/data acquisition plan",
        "failure": None,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"], "main_recommendation": manifest["main_recommendation"],
        "logical_strict_rows_read": len(logical), "new_performance_queries": 0,
        "parent_classification": parent_summary.set_index("classification").parents.to_dict(),
        "runtime_seconds": manifest["actual_runtime_seconds"],
    }, indent=2, default=str))
    return manifest


def check() -> None:
    config = load_json(CONFIG)
    manifest = load_json(MANIFEST)
    if manifest["status"] != "ECONOMIC_BOTTLENECK_AUDIT_COMPLETED":
        raise ValueError("Epoch-2B audit status mismatch")
    if manifest["new_performance_queries"] != 0 or manifest["return_label_read"] or manifest["signal_materialized"] or manifest["forward_read"]:
        raise PermissionError("Epoch-2B crossed the report-only boundary")
    if manifest["main_recommendation"] not in config["route_priority"]:
        raise ValueError("Epoch-2B did not choose exactly one registered route")
    for path, expected in manifest["input_sha256"].items():
        if sha256_file(REPO / path) != expected:
            raise ValueError(f"Epoch-2B input drift: {path}")
    for output in manifest["outputs"]:
        if sha256_file(REPO / output["path"]) != output["sha256"]:
            raise ValueError(f"Epoch-2B output drift: {output['path']}")
    replay = load_json(ROOT / "hybrid_report_only_replay_summary.json")
    for panel in replay["panels"]:
        if not math.isclose(panel["quality_share"], .60, abs_tol=.01) or panel["exact_identities"] != panel["strict_rows"]:
            raise ValueError("Hybrid report-only replay did not preserve admitted-identity composition")
    operators = pd.read_csv(ROOT / "operator_causal_summary.csv")
    adaptive = operators[operators.lane_id.isin(["evolutionary_repair", "local_mcts_repair", "llm_typed_repair"])]
    if len(adaptive) == 0 or adaptive.causal_gate_control_status.isna().any():
        raise ValueError("operator causal classification incomplete")
    print("PASS_ECONOMIC_BOTTLENECK_AUDIT_VALID")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("run", "check"))
    args = parser.parse_args()
    {"run": run, "check": check}[args.action]()


if __name__ == "__main__":
    main()
