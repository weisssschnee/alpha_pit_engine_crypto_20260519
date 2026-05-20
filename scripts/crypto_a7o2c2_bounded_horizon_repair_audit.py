from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR
from crypto_a7o_search_space_and_fold_replay import DRY_GENERATED_PER_CELL
from crypto_a7o2c_semantic_uniqueness_audit import (
    MIN_FOLD_EFFECTIVE_SAMPLE_RATE,
    economic_uniqueness,
    fold_feasibility,
    generate_cell_candidate_rows,
    horizon_distribution,
    load_cells_with_fields,
    semantic_uniqueness,
    stable_file_hash,
    utc_now,
    write_json,
    write_markdown_table,
)


DATE_TAG = "20260520"
STAGE_ID = os.environ.get("A7O_REPAIR_STAGE", "A7O2C2")
STAGE_SLUG = os.environ.get("A7O_REPAIR_SLUG", "a7o2c2_bounded_horizon_semantic_repair")
REPORT_PREFIX = os.environ.get("A7O_REPAIR_REPORT_PREFIX", "CRYPTO_A7O2C2_BOUNDED_HORIZON_REPAIR_AUDIT")
DECISION_PREFIX = os.environ.get("A7O_REPAIR_DECISION_PREFIX", "CRYPTO_A7O2C2_L1_AUTHORIZATION_REVIEW")
REPORT_TITLE = os.environ.get("A7O_REPAIR_REPORT_TITLE", "Crypto A7O-2C2 Bounded-Horizon Semantic Repair Audit")
DECISION_TITLE = os.environ.get("A7O_REPAIR_DECISION_TITLE", "Crypto A7O-2C2 Bounded-Horizon Repair Decision")
PASS_DECISION = f"PASS_{STAGE_ID}_READY_FOR_A7O2D_AUTHORIZATION"
HOLD_DECISION = f"HOLD_{STAGE_ID}_SEMANTIC_OR_HORIZON_FEASIBILITY_FAIL"
A7O2C2_DIR = RUNTIME_DIR / STAGE_SLUG


def write_decision_record(path: Path, decision: str, blockers: list[str]) -> None:
    authorization = decision == PASS_DECISION
    lines = [
        f"# {DECISION_TITLE}",
        "",
        f"- decision: `{decision}`",
        f"- authorizes_l1_execution: `{False}`",
        f"- ready_for_a7o2d_authorization_record: `{authorization}`",
        "- authorizes_l2_execution: `False`",
        "- authorizes_l3_execution: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{blockers}`",
        "",
        f"{STAGE_ID} audits a generator repair. It may only make L1 ready for a separate A7O-2D authorization record; it does not authorize L1 by itself.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    A7O2C2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    cells = load_cells_with_fields()
    candidates = generate_cell_candidate_rows(cells)
    semantic = semantic_uniqueness(candidates)
    horizon = horizon_distribution(candidates)
    economic = economic_uniqueness(candidates, cells)
    folds = fold_feasibility(candidates)

    sample = candidates.sort_values(["cell_id", "ordinal"]).groupby("cell_id").head(2).copy()
    sample = sample[
        [
            "cell_id",
            "ordinal",
            "hypothesis_family",
            "feature_family_set",
            "operator_motif",
            "temporal_horizon_class",
            "normalization_scope",
            "residualization_target",
            "regime_fold_target",
            "expression",
            "bucketed_expression",
            "max_window",
            "horizon_bucket",
        ]
    ]

    gate_rows: list[dict[str, Any]] = []
    for group, frame in [("semantic", semantic), ("horizon", horizon), ("economic", economic)]:
        for _, row in frame.iterrows():
            gate_rows.append(
                {
                    "group": group,
                    "gate": row["metric"],
                    "pass": bool(row["pass"]),
                    "value": row["value"],
                    "threshold": row["threshold"],
                }
            )
    for _, row in folds.iterrows():
        gate_rows.append(
            {
                "group": "fold_feasibility",
                "gate": f"{row['fold_id']}_p05_effective_sample_rate",
                "pass": bool(row["pass"]),
                "value": row["p05_effective_sample_rate"],
                "threshold": MIN_FOLD_EFFECTIVE_SAMPLE_RATE,
            }
        )
    gate_df = pd.DataFrame(gate_rows)
    blockers = gate_df.loc[~gate_df["pass"], "gate"].astype(str).tolist()
    decision = PASS_DECISION if not blockers else HOLD_DECISION

    paths = {
        "candidate_sample": A7O2C2_DIR / f"{STAGE_SLUG}_sample_generated_semantic_keys.csv",
        "semantic_uniqueness": A7O2C2_DIR / f"{STAGE_SLUG}_effective_uniqueness.csv",
        "horizon_distribution": A7O2C2_DIR / f"{STAGE_SLUG}_horizon_parameter_distribution.csv",
        "economic_uniqueness": A7O2C2_DIR / f"{STAGE_SLUG}_economic_motif_uniqueness.csv",
        "fold_feasibility": A7O2C2_DIR / f"{STAGE_SLUG}_fold_coverage_feasibility.csv",
        "gate_summary": A7O2C2_DIR / f"{STAGE_SLUG}_gate_summary.csv",
        "manifest": A7O2C2_DIR / f"{STAGE_SLUG}_manifest.json",
    }
    sample.to_csv(paths["candidate_sample"], index=False)
    semantic.to_csv(paths["semantic_uniqueness"], index=False)
    horizon.to_csv(paths["horizon_distribution"], index=False)
    economic.to_csv(paths["economic_uniqueness"], index=False)
    folds.to_csv(paths["fold_feasibility"], index=False)
    gate_df.to_csv(paths["gate_summary"], index=False)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "executes_large_backtest": False,
        "authorizes_l1_execution": False,
        "ready_for_a7o2d_authorization_record": decision == PASS_DECISION,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "input": {
            "dry_generated_per_cell": DRY_GENERATED_PER_CELL,
            "bounded_window_repair_module": "scripts/crypto_a7o_search_space_and_fold_replay.py",
        },
        "blockers": blockers,
        "semantic_summary": semantic.to_dict(orient="records"),
        "horizon_summary": horizon.to_dict(orient="records"),
        "economic_summary": economic.to_dict(orient="records"),
        "fold_feasibility_min_p05": float(folds["p05_effective_sample_rate"].min()),
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
        "outputs": {k: str(v) for k, v in paths.items() if k != "manifest"},
    }
    manifest["stable_manifest_hash"] = stable_file_hash([v for k, v in paths.items() if k != "manifest"])
    write_json(paths["manifest"], manifest)

    report = [
        f"# {REPORT_TITLE}",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- executes_large_backtest: `False`",
        "- authorizes_l1_execution: `False`",
        f"- ready_for_a7o2d_authorization_record: `{decision == PASS_DECISION}`",
        f"- blockers: `{blockers}`",
        "",
        "## Effective Uniqueness",
        "",
        write_markdown_table(semantic),
        "## Horizon Parameter Distribution",
        "",
        write_markdown_table(horizon),
        "## Economic Motif Uniqueness",
        "",
        write_markdown_table(economic),
        "## Fold Coverage Feasibility",
        "",
        write_markdown_table(folds, 50),
        "## Decision",
        "",
        f"{STAGE_ID} does not authorize L1. If it passes, a separate A7O-2D authorization record is still required.",
    ]
    report_path = REPORT_DIR / f"{REPORT_PREFIX}_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    decision_path = REPORT_DIR / f"{DECISION_PREFIX}_{DATE_TAG}.md"
    write_decision_record(decision_path, decision, blockers)

    print(
        json.dumps(
            {
                "decision": decision,
                "blockers": blockers,
                "authorizes_l1_execution": False,
                "ready_for_a7o2d_authorization_record": decision == PASS_DECISION,
                "manifest": str(paths["manifest"]),
                "report": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
