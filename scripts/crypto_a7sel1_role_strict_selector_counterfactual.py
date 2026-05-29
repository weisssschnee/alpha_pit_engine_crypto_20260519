from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7sel1_role_strict_selector_counterfactual"
REPORT = REPO / "reports" / "CRYPTO_A7SEL1_ROLE_STRICT_SELECTOR_COUNTERFACTUAL_20260529.md"

A7POOL0 = REPO / "runtime" / "a7pool0_alpha_eligible_pool" / "a7pool0_manifest.json"
POOL = REPO / "runtime" / "a7pool0_alpha_eligible_pool" / "a7pool0_generated_pool.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def empty_outputs(reason: str, pool0: dict[str, Any]) -> dict[str, Any]:
    empty = pd.DataFrame()
    empty.to_csv(RUNTIME / "a7sel1_selector_trace.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_selected_queue.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_role_audit.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_control_dominance_audit.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_label_family_distribution.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_signal_vector_diversity.csv", index=False)
    empty.to_csv(RUNTIME / "a7sel1_stress_summary.csv", index=False)
    return {
        "stage": "A7SEL-1",
        "generated_at": now_utc(),
        "decision": "HOLD_A7SEL1_NOT_RUN_A7POOL0_NOT_READY",
        "blockers": [reason],
        "upstream_a7pool0_decision": pool0.get("decision", "MISSING"),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may_in_selector_score": False,
        "uses_may_for_post_selection_stress_summary": False,
        "selected_count": 0,
        "selected_stress_clean_candidates": 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pool0 = read_json(A7POOL0)
    if not pool0.get("authorizes_a7sel1"):
        manifest = empty_outputs("a7pool0_not_authorized", pool0)
        write_json(RUNTIME / "a7sel1_manifest.json", manifest)
        report_lines = [
            "# CRYPTO A7SEL-1 ROLE-STRICT SELECTOR COUNTERFACTUAL",
            "",
            f"Generated: {manifest['generated_at']}",
            "",
            "## Decision",
            "",
            f"`{manifest['decision']}`",
            "",
            "A7SEL-1 was not run because A7POOL-0 did not authorize selector continuation.",
            "",
            "## Manifest",
            "",
            "```json",
            json.dumps(manifest, indent=2, sort_keys=True),
            "```",
        ]
        REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    pool = pd.read_csv(POOL)
    trace = pool.copy()
    trace["role_strict_pass"] = trace["candidate_role"].isin(["ordinary_alpha_valid", "role_mixed_allowed"]) & ~trace["role_violation"].astype(bool)
    trace["control_ratio"] = pd.to_numeric(trace["control_ratio_premay_max"], errors="coerce")
    trace["control_clean"] = trace["control_ratio"] < 1.0
    trace["non_l7_label_evidence"] = trace["label_evidence_family"].astype(str).ne("L7_ranked_future_return")
    trace["a7sel1_score_no_may"] = (
        (1.0 - trace["control_ratio"].clip(upper=1.0)).fillna(0.0)
        + trace["role_strict_pass"].astype(float)
        + trace["non_l7_label_evidence"].astype(float)
    )
    queue = trace[trace["role_strict_pass"] & trace["control_clean"] & trace["non_l7_label_evidence"]].sort_values(
        ["a7sel1_score_no_may", "candidate_id"], ascending=[False, True]
    )
    selected_rows = []
    used_skeletons: set[str] = set()
    for _, row in queue.iterrows():
        skeleton = str(row.get("skeleton_key", ""))
        if skeleton in used_skeletons:
            continue
        selected_rows.append(row)
        used_skeletons.add(skeleton)
        if len(selected_rows) >= 4:
            break
    selected = pd.DataFrame(selected_rows)
    role_audit = selected[["candidate_id", "candidate_role", "role_violation", "role_strict_pass"]] if not selected.empty else pd.DataFrame()
    control_audit = selected[["candidate_id", "control_ratio", "control_clean"]] if not selected.empty else pd.DataFrame()
    label_dist = selected[["candidate_id", "label_evidence_family", "label_evidence_horizon_h", "non_l7_label_evidence"]] if not selected.empty else pd.DataFrame()
    diversity = pd.DataFrame(
        [
            {
                "selected_count": int(len(selected)),
                "selected_skeletons": int(selected["skeleton_key"].nunique()) if not selected.empty else 0,
                "top_skeleton_share": float(selected["skeleton_key"].value_counts(normalize=True).max()) if not selected.empty else 0.0,
                "selected_field_families": int(selected["field_family"].nunique()) if not selected.empty else 0,
                "top_field_family_share": float(selected["field_family"].value_counts(normalize=True).max()) if not selected.empty else 0.0,
            }
        ]
    )
    stress = pd.DataFrame(
        [
            {
                "selected_count": int(len(selected)),
                "stress_observed_count": 0,
                "selected_stress_clean_candidates": 0,
                "stress_status": "not_observed_no_replay_executed",
            }
        ]
    )
    blockers: list[str] = []
    if len(selected) < 4:
        blockers.append("selected_count_lt_4")
    if not selected.empty and int(selected["skeleton_key"].nunique()) < min(len(selected), 4):
        blockers.append("selected_skeleton_diversity_low")
    if not selected.empty and bool((~selected["role_strict_pass"]).any()):
        blockers.append("role_violation_selected")
    if not selected.empty and bool((~selected["control_clean"]).any()):
        blockers.append("control_dominated_selected")
    if not selected.empty and not bool(selected["non_l7_label_evidence"].any()):
        blockers.append("selected_non_l7_label_evidence_zero")
    blockers.append("selected_stress_clean_candidates_unobserved_without_replay")
    decision = "HOLD_A7SEL1_ROLE_STRICT_COUNTERFACTUAL_NOT_PROMOTABLE"

    trace.to_csv(RUNTIME / "a7sel1_selector_trace.csv", index=False)
    selected.to_csv(RUNTIME / "a7sel1_selected_queue.csv", index=False)
    role_audit.to_csv(RUNTIME / "a7sel1_role_audit.csv", index=False)
    control_audit.to_csv(RUNTIME / "a7sel1_control_dominance_audit.csv", index=False)
    label_dist.to_csv(RUNTIME / "a7sel1_label_family_distribution.csv", index=False)
    diversity.to_csv(RUNTIME / "a7sel1_signal_vector_diversity.csv", index=False)
    stress.to_csv(RUNTIME / "a7sel1_stress_summary.csv", index=False)

    manifest = {
        "stage": "A7SEL-1",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may_in_selector_score": False,
        "uses_may_for_post_selection_stress_summary": False,
        "input_candidate_count": int(len(trace)),
        "selected_count": int(len(selected)),
        "selected_stress_clean_candidates": 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7sel1_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SEL-1 ROLE-STRICT SELECTOR COUNTERFACTUAL",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SEL-1 applies a role-strict dry selector to the A7POOL-0 pool. It does not execute replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selected Queue",
        "",
        md_table(selected[["candidate_id", "expression", "field_family", "variant", "candidate_role", "control_ratio", "a7sel1_score_no_may"]] if not selected.empty else selected, 40),
        "",
        "## Stress Summary",
        "",
        md_table(stress, 10),
        "",
        "## Boundary",
        "",
        "```text",
        "No replay was executed, so stress-clean promotion cannot be claimed.",
        "No formula search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
