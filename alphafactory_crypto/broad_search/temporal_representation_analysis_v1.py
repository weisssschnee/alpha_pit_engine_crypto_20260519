"""Final representation/economic attribution for the completed tournament."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from . import search_engine_v1 as engine
from .temporal_representation_tournament_v1 import (
    ARMS,
    BASELINE_PATH,
    OFFLINE_EVIDENCE_PATH,
)
from .temporal_targeted_deepening_v1 import (
    BASELINE_HIGH_QUALITY_MINIMUM_ROWS,
    _cluster_labels,
    _fingerprint_matrix,
    _realization_id,
    _stable_row_id,
)


DECISIONS = {
    "REPRESENTATION_SUCCESSOR_PASS",
    "REPRESENTATION_SUCCESSOR_PARTIAL",
    "CURRENT_TEMPORAL_SEMANTIC_BASIS_EXHAUSTED",
    "P1_SEMANTIC_BASIS_BOTTLENECK",
    "RESEARCH_INVALID",
}


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def _retained_ids(arm_root: Path) -> set[str]:
    checkpoint = sorted(
        (arm_root / "checkpoints").glob("checkpoint_[0-9][0-9][0-9]")
    )[-1]
    state = engine._read_json(checkpoint / "state.json")
    return {
        str(candidate_id)
        for policy in state["policies"].values()
        for candidate_id in dict(
            (policy.get("realization_v2_state") or {}).get("descendants") or {}
        )
    }


def _arm_summary(arm_root: Path) -> dict[str, Any]:
    final = engine._read_json(arm_root / "arm_final.json")
    ledger = pd.read_parquet(arm_root / "candidate_ledger.parquet")
    diagnostic = dict(final["basin_diagnostics"])
    clusters = diagnostic["economic_cluster_summary"]["thresholds"]
    return {
        "strict": len(ledger),
        "attempts": int(final["attempts"]),
        "matched_positive": int(ledger["matched_positive"].astype(bool).sum()),
        "matched_density": float(ledger["matched_positive"].astype(bool).mean()),
        "P1_P4": diagnostic["p1_vs_p4"],
        "P2_strict": int(
            (ledger["program_family_id"] == "P2_RECENT_CROWDING_EVENT_TO_RESPONSE").sum()
        ),
        "P3_strict": int(
            (ledger["program_family_id"] == "P3_FLOW_SHOCK_PERSISTENCE_TO_ABSORPTION").sum()
        ),
        "economic_clusters": {
            threshold: {
                "count": int(clusters[threshold]["economic_cluster_count"]),
                "new": int(clusters[threshold]["new_economic_cluster_count"]),
            }
            for threshold in ("0.95", "0.90", "0.85")
        },
        "HQ_basins_deepened": int(
            diagnostic["basin_realization_depth"]["high_quality_basins_deepened"]
        ),
        "new_HQ_concrete_realizations": int(
            diagnostic["basin_realization_depth"][
                "new_high_quality_concrete_realizations"
            ]
        ),
        "wide_concrete_realizations": sum(
            int(value["concrete_realization_count"])
            for value in diagnostic["p1_vs_p4"].values()
        ),
        "depth_increase": diagnostic["basin_realization_depth_increase"],
        "operation_attribution": diagnostic["evolution_operation_attribution"],
        "archive": final["archive_diagnostics"],
        "requested_operation_counts": final["requested_operation_counts"],
        "realized_operation_counts": final["realized_operation_counts"],
        "crossover_fallback_count": int(final["crossover_fallback_count"]),
    }


def _semantic_attribution(
    arm_root: Path,
    baseline_rows: Sequence[Mapping[str, Any]],
    baseline_realizations: set[str],
) -> list[dict[str, Any]]:
    frame = pd.read_parquet(arm_root / "candidate_ledger.parquet")
    retained = _retained_ids(arm_root)
    current_matched = [
        row for row in frame.to_dict("records") if bool(row.get("matched_positive"))
    ]
    combined = [
        {**dict(row), "_origin": "baseline"} for row in baseline_rows
    ] + [{**dict(row), "_origin": "current"} for row in current_matched]
    combined.sort(key=_stable_row_id)
    labels = _cluster_labels(_fingerprint_matrix(combined), 0.90)
    high_quality_candidate_ids: set[str] = set()
    for label in sorted(set(int(value) for value in labels)):
        cluster = [
            row
            for row, assigned in zip(combined, labels, strict=True)
            if int(assigned) == label
        ]
        if (
            sum(row["_origin"] == "baseline" for row in cluster)
            >= BASELINE_HIGH_QUALITY_MINIMUM_ROWS
        ):
            high_quality_candidate_ids.update(
                str(row.get("candidate_id") or "")
                for row in cluster
                if row["_origin"] == "current"
            )
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in frame.to_dict("records"):
        receipt = json.loads(str(row.get("receipt_json") or "{}"))
        edit = str(receipt.get("semantic_edit_type") or "unknown")
        grouped[edit].append({**row, "_receipt": receipt})
    output = []
    for edit, rows in sorted(grouped.items()):
        matched = [row for row in rows if bool(row.get("matched_positive"))]
        new_realizations = {
            _realization_id(row)
            for row in matched
            if _realization_id(row) not in baseline_realizations
        }
        high_quality_realizations = {
            _realization_id(row)
            for row in matched
            if str(row.get("candidate_id") or "") in high_quality_candidate_ids
        }
        enumerated = sum(
            int(row["_receipt"].get("enumerated_recombination_count") or 0)
            for row in rows
        )
        legal = sum(
            int(row["_receipt"].get("legal_child_count") or 0) for row in rows
        )
        output.append(
            {
                "semantic_edit": edit,
                "proposal_count": len(rows),
                "legal_compile_rate": (
                    legal / enumerated if enumerated else 1.0
                ),
                "basin_retained_count": sum(
                    str(row["candidate_id"]) in retained for row in rows
                ),
                "basin_retention_rate": sum(
                    str(row["candidate_id"]) in retained for row in rows
                )
                / max(1, len(rows)),
                "matched_positive": len(matched),
                "matched_density": len(matched) / max(1, len(rows)),
                "new_realization_count": len(new_realizations),
                "HQ_realization_count": len(high_quality_realizations),
                "new_HQ_realization_count": len(
                    high_quality_realizations - baseline_realizations
                ),
                "repair_size_mean": sum(
                    int(row["_receipt"].get("repair_size") or 0) for row in rows
                )
                / max(1, len(rows)),
            }
        )
    return output


def build_final_analysis(
    repo_root: Path,
    runtime_root: Path,
    *,
    decision: str,
    rationale: Sequence[str],
) -> dict[str, Any]:
    if decision not in DECISIONS:
        raise ValueError("unknown representation successor decision")
    root = repo_root.resolve()
    runtime = runtime_root.resolve()
    checker = engine._read_json(runtime / "independent_checker.json")
    if checker.get("status") != "PASS" and decision != "RESEARCH_INVALID":
        raise ValueError("non-invalid conclusion requires checker PASS")
    offline = engine._read_json(root / OFFLINE_EVIDENCE_PATH)
    baseline = engine._read_json(root / BASELINE_PATH)
    baseline_realizations = {
        _realization_id(row) for row in baseline["matched_positive_rows"]
    }
    arms = {
        arm: _arm_summary(runtime / "arms" / arm)
        for arm in ARMS
    }
    semantic = _semantic_attribution(
        runtime / "arms" / ARMS[1],
        baseline["matched_positive_rows"],
        baseline_realizations,
    )
    control = arms[ARMS[0]]
    successor = arms[ARMS[1]]
    core = {
        "schema_version": 1,
        "status": "FINAL_ANALYSIS_COMPLETE",
        "NEXT_DECISION": decision,
        "decision_rationale": list(rationale),
        "representation_closure": {
            "lossless_embedding": offline["lossless_embedding"],
            "legacy": offline["closure_benchmark"]["legacy_realization_v2"],
            "successor": offline["closure_benchmark"][
                "representation_successor"
            ],
            "P1_P4": offline["closure_benchmark"]["P1_P4"],
            "proposal_only_axis_coverage": offline["closure_benchmark"][
                "proposal_only_axis_coverage"
            ],
        },
        "economic_realization": arms,
        "economic_deltas_successor_minus_control": {
            "matched_positive": successor["matched_positive"]
            - control["matched_positive"],
            "matched_density": successor["matched_density"]
            - control["matched_density"],
            "HQ_basins_deepened": successor["HQ_basins_deepened"]
            - control["HQ_basins_deepened"],
            "new_HQ_concrete_realizations": successor[
                "new_HQ_concrete_realizations"
            ]
            - control["new_HQ_concrete_realizations"],
            "wide_concrete_realizations": successor[
                "wide_concrete_realizations"
            ]
            - control["wide_concrete_realizations"],
            "depth_increase": {
                key: int(successor["depth_increase"].get(key, 0))
                - int(control["depth_increase"].get(key, 0))
                for key in sorted(
                    set(successor["depth_increase"])
                    | set(control["depth_increase"])
                )
            },
        },
        "basin_retention": {
            arm: arms[arm]["archive"] for arm in ARMS
        },
        "semantic_module_attribution": semantic,
        "P1_vs_P4": {arm: arms[arm]["P1_P4"] for arm in ARMS},
        "canonical_checker": checker,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
        "automatic_next_run_started": False,
    }
    result = {**core, "final_analysis_sha256": _sha(core)}
    engine._write_json(runtime / "final_analysis.json", result)
    return result


__all__ = ["DECISIONS", "build_final_analysis"]
