from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ac1r_representative_quarantine_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AC1R_REPRESENTATIVE_QUARANTINE_CONTRACT_20260529.md"

A7AC1_MANIFEST = REPO / "runtime" / "a7ac1_representative_forensic_execution" / "a7ac1_manifest.json"
A7AC1_AUDIT = REPO / "runtime" / "a7ac1_representative_forensic_execution" / "a7ac1_representative_forensic_audit.csv"
A7AC1_CONTROL = REPO / "runtime" / "a7ac1_representative_forensic_execution" / "a7ac1_control_dominance_by_split.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ac1 = read_json(A7AC1_MANIFEST)
    if not a7ac1.get("authorizes_a7ac1r_representative_quarantine_contract"):
        raise SystemExit("A7AC-1 does not authorize A7AC-1R")

    audit = pd.read_csv(A7AC1_AUDIT)
    control = pd.read_csv(A7AC1_CONTROL)
    blocked = audit[audit["decision"].eq("HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED")].copy()
    diagnostic = audit[~audit["decision"].eq("HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED")].copy()
    diagnostic = diagnostic.sort_values(
        ["max_control_ratio_by_split", "oriented_recent_spread"],
        ascending=[True, False],
    ).reset_index(drop=True)
    diagnostic.insert(0, "diagnostic_rank", range(1, len(diagnostic) + 1))

    warning_summary = (
        diagnostic.assign(warning_key=diagnostic["warnings"].fillna("none"))
        .groupby("warning_key", as_index=False)
        .agg(rows=("candidate_id", "count"), candidates=("candidate_id", "nunique"))
        .sort_values("rows", ascending=False)
    )
    blocked_summary = (
        blocked.assign(blocker_key=blocked["blockers"].fillna("none"))
        .groupby("blocker_key", as_index=False)
        .agg(rows=("candidate_id", "count"), candidates=("candidate_id", "nunique"))
        .sort_values("rows", ascending=False)
        if not blocked.empty
        else pd.DataFrame(columns=["blocker_key", "rows", "candidates"])
    )
    control_warning = control[
        control["control_warning_ge_0_80"].astype(str).str.lower().eq("true")
        | control["control_hard_hold_ge_1"].astype(str).str.lower().eq("true")
    ].copy()

    diagnostic_rows = int(len(diagnostic))
    diagnostic_candidates = int(diagnostic["candidate_id"].nunique()) if diagnostic_rows else 0
    diagnostic_clusters = int(diagnostic["return_corr_cluster"].nunique()) if diagnostic_rows else 0
    label_count = int(diagnostic["label_family"].nunique()) if diagnostic_rows else 0
    control_warning_rows = int(diagnostic["max_control_ratio_by_split"].ge(0.80).sum()) if diagnostic_rows else 0
    label_dominated = bool(label_count == 1 and diagnostic_rows > 0)

    warnings: list[str] = []
    if control_warning_rows:
        warnings.append("diagnostic_subset_has_control_warning_rows")
    if label_dominated:
        warnings.append("single_label_family_only")
    if diagnostic_candidates < diagnostic_rows:
        warnings.append("same_candidate_multi_horizon")

    authorizes_a7ac2 = diagnostic_rows >= 4 and diagnostic_clusters >= 4 and int(len(blocked)) > 0
    decision = (
        "PASS_A7AC1R_DIAGNOSTIC_SUBSET_FROZEN_READY_FOR_A7AC2_WITH_WARNINGS"
        if authorizes_a7ac2
        else "HOLD_A7AC1R_DIAGNOSTIC_SUBSET_TOO_WEAK"
    )
    manifest = {
        "stage": "A7AC-1R",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ac1_decision": a7ac1.get("decision"),
        "input_representative_rows": int(len(audit)),
        "blocked_rows": int(len(blocked)),
        "diagnostic_rows": diagnostic_rows,
        "diagnostic_candidates": diagnostic_candidates,
        "diagnostic_clusters": diagnostic_clusters,
        "diagnostic_label_families": label_count,
        "diagnostic_control_warning_rows": control_warning_rows,
        "warnings": warnings,
        "authorizes_a7ac2_label_diversification_contract": authorizes_a7ac2,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ac1r_representative_quarantine_contract",
        "objective": "Quarantine A7AC-1 blocked representatives and freeze a diagnostic-only subset.",
        "status": "completed",
        "mode": "light_contract",
        "inputs": {
            "a7ac1_manifest": str(A7AC1_MANIFEST),
            "a7ac1_audit": str(A7AC1_AUDIT),
            "a7ac1_control": str(A7AC1_CONTROL),
        },
        "parameters": {
            "blocked_decision": "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED",
            "minimum_diagnostic_rows": 4,
            "minimum_diagnostic_clusters": 4,
            "May_usage": "not used",
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": decision,
        "next_action": "A7AC-2 label-diversification and neutralization contract" if authorizes_a7ac2 else "HOLD",
    }

    diagnostic.to_csv(RUNTIME / "a7ac1r_diagnostic_representative_subset.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ac1r_quarantined_representatives.csv", index=False)
    warning_summary.to_csv(RUNTIME / "a7ac1r_warning_summary.csv", index=False)
    blocked_summary.to_csv(RUNTIME / "a7ac1r_blocker_summary.csv", index=False)
    control_warning.to_csv(RUNTIME / "a7ac1r_control_warning_rows.csv", index=False)
    write_json(RUNTIME / "a7ac1r_manifest.json", manifest)
    write_json(RUNTIME / "a7ac1r_experiment_record.json", experiment_record)
    write_json(
        RUNTIME / "a7ac1r_authorization_matrix.json",
        {
            "A7AC-1R": {"status": decision},
            "A7AC-2_label_diversification_and_neutralization_contract": {"authorized": authorizes_a7ac2},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AC-1R REPRESENTATIVE QUARANTINE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AC-1R quarantines A7AC-1 blocked representatives and freezes a diagnostic-only subset. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Diagnostic Representative Subset",
        "",
        md_table(diagnostic, 80),
        "",
        "## Quarantined Representatives",
        "",
        md_table(blocked, 80),
        "",
        "## Warning Summary",
        "",
        md_table(warning_summary),
        "",
        "## Blocker Summary",
        "",
        md_table(blocked_summary),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
