from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z8p_partial_viable_queue_authorization"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z8P_PARTIAL_VIABLE_QUEUE_AUTHORIZATION_20260529.md"
Z8_MANIFEST = REPO / "runtime" / "a7al2z8_response_guided_materialization_repair" / "a7al2z8_manifest.json"
Z8_SELECTED = REPO / "runtime" / "a7al2z8_response_guided_materialization_repair" / "a7al2z8_repaired_selected_candidates.csv"
Z8_FAMILY = REPO / "runtime" / "a7al2z8_response_guided_materialization_repair" / "a7al2z8_family_repair_summary.csv"
Z8_BLOCKERS = REPO / "runtime" / "a7al2z8_response_guided_materialization_repair" / "a7al2z8_repair_blocker_matrix.csv"


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

    z8 = read_json(Z8_MANIFEST)
    selected = pd.read_csv(Z8_SELECTED) if Z8_SELECTED.exists() else pd.DataFrame()
    family = pd.read_csv(Z8_FAMILY) if Z8_FAMILY.exists() else pd.DataFrame()
    blockers = pd.read_csv(Z8_BLOCKERS) if Z8_BLOCKERS.exists() else pd.DataFrame()
    selected_count = int(len(selected))
    family_count = int(selected["objective_family"].nunique()) if not selected.empty else 0
    selected_eval_fail = int(z8.get("selected_eval_failure_count", 999))
    selected_activity_fail = int(z8.get("selected_activity_failure_count", 999))
    authorized = selected_count >= 64 and family_count >= 4 and selected_eval_fail == 0 and selected_activity_fail == 0
    decision = (
        "PASS_A7AL2Z8P_PARTIAL_VIABLE_QUEUE_READY_FOR_Z9_DIAGNOSTIC"
        if authorized
        else "HOLD_A7AL2Z8P_PARTIAL_QUEUE_TOO_WEAK"
    )
    manifest = {
        "stage": "A7AL-2Z8P",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_authorization_only": True,
        "executes_replay": False,
        "executes_generation": False,
        "executes_training": False,
        "authorizes_a7al2z9_partial_numeric_diagnostic": authorized,
        "authorizes_full_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_z8_decision": z8.get("decision"),
        "selected_candidates": selected_count,
        "selected_family_count": family_count,
        "selected_eval_failure_count": selected_eval_fail,
        "selected_activity_failure_count": selected_activity_fail,
        "known_weak_families": "M0/M6/M7 materialization weak; excluded from full-family claim",
    }
    selected.to_csv(RUNTIME / "a7al2z8p_partial_viable_candidates.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z8p_source_family_summary.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z8p_source_blockers.csv", index=False)
    write_json(RUNTIME / "a7al2z8p_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z8p_authorization_matrix.json",
        {
            "A7AL-2Z8P": {"status": decision},
            "a7al2z9_partial_numeric_diagnostic": {"authorized": authorized},
            "full_replay": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z8P PARTIAL VIABLE QUEUE AUTHORIZATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "Z8P does not claim full-family materialization success. It authorizes a partial diagnostic on the viable materialized queue only.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Family Summary",
        "",
        md_table(family),
        "",
        "## Source Blockers",
        "",
        md_table(blockers, 80),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
