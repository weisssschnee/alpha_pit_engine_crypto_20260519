from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


P5 = "P5_FLOW_PARTICIPATION_CONVICTION"
P6 = "P6_DERIVATIVE_CROWDING_RELATIVE_PRESSURE"


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest().upper()


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _spec(value: str) -> dict[str, Any]:
    return dict(json.loads(value)["generation_genes"]["mechanism_spec"])


def _motif_plan() -> list[dict[str, Any]]:
    return [
        {
            "family_id": P5, "motif_id": "FLOW_INTENSITY_CONVICTION",
            "parent_template_id": "FLOW_INTENSITY_CONVICTION",
            "hypothesis": "Aggressor imbalance relative to participation intensity separates directional conviction from sparse prints and exhaustion.",
            "payload_operators": ["SafeDiv", "SafeMul", "Residual", "ConditionGate"],
            "payload_modes": {"ConditionGate": ["SIGN_CONFIRMATION", "SIGN_DISAGREEMENT"]},
            "temporal_variants": [{}, {"primitive": "Persistence", "axis": "left"}, {"primitive": "Acceleration", "axis": "left"}, {"primitive": "EventWindow", "axis": "right"}],
            "condition_variants": [{"role": "OI_LEVEL", "operator": "StateModulation", "mode": "ABSOLUTE_MAGNITUDE"}],
        },
        {
            "family_id": P5, "motif_id": "FLOW_PRICE_ABSORPTION",
            "parent_template_id": "FLOW_PRICE_ABSORPTION",
            "hypothesis": "Persistent taker pressure with weak or strong price displacement distinguishes absorption from continuation.",
            "payload_operators": ["SafeDiv", "NormalizedDifference", "Residual"],
            "temporal_variants": [{}, {"primitive": "Acceleration", "axis": "left"}, {"primitive": "Persistence", "axis": "right"}, {"primitive": "MultiScaleRelation", "axis": "right"}],
            "condition_variants": [{"role": "TRADE_INTENSITY", "operator": "StateModulation", "mode": "ABSOLUTE_MAGNITUDE"}],
        },
        {
            "family_id": P5, "motif_id": "LARGE_TRADE_PRICE_RESPONSE",
            "parent_template_id": "LARGE_TRADE_PRICE_RESPONSE",
            "hypothesis": "Large-trade participation relative to price response identifies concentrated informed pressure or absorbed block flow.",
            "payload_operators": ["SafeDiv", "NormalizedDifference", "Residual"],
            "temporal_variants": [{}, {"primitive": "Persistence", "axis": "right"}, {"primitive": "EventWindow", "axis": "right"}],
            "condition_variants": [],
        },
        {
            "family_id": P6, "motif_id": "FUNDING_FLOW_CROWDING",
            "parent_template_id": "FUNDING_FLOW_CROWDING",
            "hypothesis": "Funding pressure relative to aggressor flow measures contemporaneous directional crowding and unwind risk.",
            "payload_operators": ["SafeDiv", "SafeMul", "Residual", "ConditionGate"],
            "payload_modes": {"ConditionGate": ["SIGN_CONFIRMATION", "SIGN_DISAGREEMENT"]},
            "temporal_variants": [{}, {"primitive": "Persistence", "axis": "left"}, {"primitive": "Transition", "axis": "left"}],
            "condition_variants": [{"role": "OI_LEVEL", "operator": "StateModulation", "mode": "ABSOLUTE_MAGNITUDE"}],
        },
        {
            "family_id": P6, "motif_id": "OI_FLOW_CONFIRMATION",
            "parent_template_id": "OI_FLOW_CONFIRMATION_V2",
            "hypothesis": "Flow crowding normalized by open-interest expansion distinguishes new leverage from inventory transfer.",
            "payload_operators": ["NormalizedDifference", "Residual", "RatioInteraction"],
            "temporal_variants": [{}, {"primitive": "Delta", "axis": "left"}, {"primitive": "MultiScaleRelation", "axis": "left"}],
            "condition_variants": [{"role": "FUNDING", "operator": "ConditionGate", "mode": "NEGATIVE"}],
        },
        {
            "family_id": P6, "motif_id": "BASIS_FLOW_DISLOCATION",
            "parent_template_id": "BASIS_FLOW_DISLOCATION",
            "hypothesis": "Basis dislocation relative to aggressor flow identifies derivatives pressure confirmed or rejected by carry.",
            "payload_operators": ["NormalizedDifference", "Residual", "RatioInteraction"],
            "temporal_variants": [{}, {"primitive": "MultiScaleRelation", "axis": "left"}, {"primitive": "Persistence", "axis": "right"}],
            "condition_variants": [{"role": "OI_LEVEL", "operator": "StateModulation", "mode": "ABSOLUTE_MAGNITUDE"}],
        },
        {
            "family_id": P6, "motif_id": "BASIS_OI_CROWDING",
            "parent_template_id": "BASIS_OI_CROWDING",
            "hypothesis": "Carry dislocation relative to open-interest participation measures crowded leverage demand.",
            "payload_operators": ["NormalizedDifference", "Residual", "RatioInteraction"],
            "temporal_variants": [{}, {"primitive": "MultiScaleRelation", "axis": "left"}, {"primitive": "Delta", "axis": "right"}],
            "condition_variants": [{"role": "FLOW_IMBALANCE", "operator": "ConditionGate", "mode": None}],
        },
        {
            "family_id": P6, "motif_id": "CROSS_VENUE_OI_FLOW_DISAGREEMENT",
            "parent_template_id": "CROSS_VENUE_OI_FLOW_DISAGREEMENT",
            "hypothesis": "Cross-venue open-interest disagreement relative to flow reveals venue-local leverage pressure.",
            "payload_operators": ["NormalizedDifference", "Residual"],
            "temporal_variants": [{}, {"primitive": "MultiScaleRelation", "axis": "left"}],
            "condition_variants": [{"role": "FUNDING", "operator": "StateModulation", "mode": "SIGN_ROUTING"}],
        },
    ]


def build(ledger: Path, manifest: Path, oi_queue: Path, regime_report: Path) -> dict[str, Any]:
    columns = ["candidate_spec_json", "search_reward", "matched_positive", "evaluation_partition"]
    frame = pd.read_parquet(ledger, columns=columns)
    partitions = sorted(set(frame["evaluation_partition"].astype(str)))
    if partitions != ["train"]:
        raise ValueError("frontier source-gap requires train-only mechanism evidence")
    stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"strict": 0, "positive_reward": 0, "matched_positive": 0, "reward_sum": 0.0})
    operator_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"strict": 0, "positive_reward": 0})
    condition_stats: dict[str, dict[str, Any]] = defaultdict(lambda: {"strict": 0, "positive_reward": 0})
    for row in frame.to_dict("records"):
        spec = _spec(str(row["candidate_spec_json"]))
        reward = float(row["search_reward"] or 0.0)
        template = str(spec["template_id"])
        local = stats[template]
        local["strict"] += 1; local["positive_reward"] += int(reward > 0); local["matched_positive"] += int(bool(row["matched_positive"])); local["reward_sum"] += reward
        op_key = f"{spec['payload_operator']}+{spec.get('condition_operator') or 'NONE'}"
        operator_stats[op_key]["strict"] += 1; operator_stats[op_key]["positive_reward"] += int(reward > 0)
        role = str(spec.get("condition_role") or "NONE")
        condition_stats[role]["strict"] += 1; condition_stats[role]["positive_reward"] += int(reward > 0)
    def rates(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {"key": key, **row, "positive_reward_density": row["positive_reward"] / max(1, row["strict"])}
            for key, row in sorted(values.items())
        ]
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    contracts = list(manifest_payload["contracts"])
    if not contracts or any(int(row["observable_lag_hours"]) < 0 for row in contracts):
        raise ValueError("frontier source-gap PIT contract is incomplete")
    plan = _motif_plan()
    raw_possible = sum(
        sum(len(row.get("payload_modes", {}).get(op, [None])) for op in row["payload_operators"])
        * (len(row["temporal_variants"]) + len(row.get("condition_variants", [])))
        for row in plan
    )
    core = {
        "schema_version": 1,
        "status": "TEMPORAL_HYPOTHESIS_FRONTIER_SOURCE_GAP_READY",
        "source_ledger": {"path": str(ledger), "rows": len(frame), "bytes": ledger.stat().st_size, "sha256": _file_sha(ledger)},
        "source_partitions": partitions,
        "historical_template_stats": rates(stats),
        "historical_operator_condition_stats": rates(operator_stats),
        "historical_condition_role_stats": rates(condition_stats),
        "historical_provenance": [
            {"kind": "OI_FUNDING_QUEUE", "path": str(oi_queue), "sha256": _file_sha(oi_queue)},
            {"kind": "REGIME_MECHANISM_AUDIT", "path": str(regime_report), "sha256": _file_sha(regime_report)},
        ],
        "pit_contract": {"manifest_path": str(manifest), "manifest_sha256": _file_sha(manifest), "contract_count": len(contracts), "all_lags_nonnegative": True},
        "mapping_authority": ["CROSS_SECTIONAL_RELATIVE", "SPARSE_EVENT_CARRY"],
        "matched_control_schemas": ["DUAL_AXIS_A_B_AB", "HIERARCHICAL_A_B_AB_ABC"],
        "raw_possible_combinations": raw_possible,
        "accepted_motif_plan": plan,
        "rejection_reasons": {
            "P1_POSITION_FIRST_SEMANTICS": "ARCHIVED_FAMILY_OVERLAP",
            "P4_SLOW_STATE_ROUTING": "ANCHOR_ONLY_NOT_FRONTIER",
            "FULL_CARTESIAN_PRODUCT": "BOUNDED_CATALOG_POLICY",
            "UNREGISTERED_PRIMITIVES": "NOT_REQUIRED_BY_SOURCE_GAP",
        },
        "historical_oos_used_as_adaptive_label": False,
        "validation_reads": 0, "oos_reads": 0, "holdout_reads": 0,
        "forward_reads": 0, "promotion_reads": 0, "sealed_reads": 0,
    }
    return {**core, "source_gap_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    payload = build(
        root / "runtime/crypto_search_mechanism_v2_3_20260802/candidate_ledger.parquet",
        root / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json",
        root / "runtime/a7mech3_oi_funding_lag_pass_reward_queue_20260703/a7source5_source_lag_survivor_reward_queue.csv",
        root / "reports/CRYPTO_A7REGIME2_MECHANISM_REGIME_AUDIT_20260612.md",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "raw_possible_combinations": payload["raw_possible_combinations"], "source_gap_sha256": payload["source_gap_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
