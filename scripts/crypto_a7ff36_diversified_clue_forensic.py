from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff36_diversified_clue_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF36_DIVERSIFIED_CLUE_FORENSIC_20260530.md"

A7FF35_MANIFEST = REPO / "runtime" / "a7ff35_diversified_numeric_preflight" / "a7ff35_manifest.json"
A7FF35_SELECTED = REPO / "runtime" / "a7ff35_diversified_numeric_preflight" / "a7ff35_selected_portfolio_queue.csv"
A7FF35_FAMILY = REPO / "runtime" / "a7ff35_diversified_numeric_preflight" / "a7ff35_family_materialization_summary.csv"
A7FF35_DECISIONS = REPO / "runtime" / "a7ff35_diversified_numeric_preflight" / "a7ff35_decision_counts.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f35 = read_json(A7FF35_MANIFEST)
    if not f35.get("authorizes_a7ff36_forensic_or_repair"):
        raise SystemExit(f"A7FF-35 does not authorize A7FF-36: {f35.get('decision')}")

    selected = read_csv(A7FF35_SELECTED)
    family = read_csv(A7FF35_FAMILY)
    decisions = read_csv(A7FF35_DECISIONS)

    if selected.empty:
        raise SystemExit("A7FF-35 selected queue is empty")

    selected = selected.copy()
    selected["is_rank_label_only"] = selected["label_family"].astype(str).eq("L7_ranked_future_return")
    selected["is_non_l7"] = ~selected["is_rank_label_only"]
    selected["control_ratio_premay_max"] = pd.to_numeric(selected["control_ratio_premay_max"], errors="coerce")
    selected["control_warning"] = selected["control_ratio_premay_max"].ge(0.80)
    selected["control_block"] = selected["control_ratio_premay_max"].ge(1.00)
    selected["forensic_decision"] = "KEEP_DIAGNOSTIC"
    selected.loc[selected["is_rank_label_only"], "forensic_decision"] = "HOLD_RANK_LABEL_DIAGNOSTIC_ONLY"
    selected.loc[selected["control_warning"] & selected["is_non_l7"], "forensic_decision"] = "KEEP_WITH_CONTROL_WARNING"
    selected.loc[selected["control_block"], "forensic_decision"] = "REJECT_CONTROL_DOMINATED"
    selected.to_csv(RUNTIME / "a7ff36_selected_clue_forensic.csv", index=False)

    family = family.copy()
    if not family.empty:
        family["activity_ok"] = pd.to_numeric(family["activity_ok"], errors="coerce").fillna(0)
        family["rows"] = pd.to_numeric(family["rows"], errors="coerce").fillna(0)
        family["activity_rate"] = family["activity_ok"] / family["rows"].replace(0, pd.NA)
        family["family_forensic_decision"] = "KEEP_FOR_DEEP_REPLAY_CONTRACT"
        family.loc[family["activity_ok"].eq(0), "family_forensic_decision"] = "REPAIR_OR_EXCLUDE_NO_ACTIVITY"
        family.loc[family["activity_ok"].gt(0) & family["activity_rate"].lt(0.75), "family_forensic_decision"] = "REPAIR_LOW_ACTIVITY_BEFORE_EXPANSION"
    family.to_csv(RUNTIME / "a7ff36_family_activity_forensic.csv", index=False)

    non_l7 = selected[selected["is_non_l7"] & ~selected["control_block"]].copy()
    non_l7_family_count = int(non_l7["semantic_pair"].nunique()) if "semantic_pair" in non_l7.columns else 0
    rank_only_count = int(selected["is_rank_label_only"].sum())
    control_warning_count = int((selected["control_warning"] & selected["is_non_l7"]).sum())
    control_block_count = int(selected["control_block"].sum())
    no_activity_families = family[family["family_forensic_decision"].astype(str).str.contains("NO_ACTIVITY", na=False)]["family_id"].tolist() if not family.empty else []

    repair = pd.DataFrame(
        [
            {
                "item": "rank_label_selected_rows",
                "action": "exclude_from_deep_replay_contract",
                "reason": "L7 ranked-return remains diagnostic-only",
                "count": rank_only_count,
            },
            {
                "item": "control_warning_non_l7_rows",
                "action": "keep_only_with_control_margin_audit",
                "reason": "0.80 <= control_ratio < 1.00 is warning, not promotion",
                "count": control_warning_count,
            },
            {
                "item": "no_activity_families",
                "action": "repair_or_exclude_before_expansion",
                "reason": "family materialization has zero activity in diversified preflight",
                "count": len(no_activity_families),
            },
            {
                "item": "non_l7_clue_rows",
                "action": "allow_deep_replay_contract_only",
                "reason": "non-L7 diversified clues exist but remain bounded preflight evidence",
                "count": int(len(non_l7)),
            },
        ]
    )
    repair.to_csv(RUNTIME / "a7ff36_repair_actions.csv", index=False)

    decision_counts = decisions.copy()
    decision_counts.to_csv(RUNTIME / "a7ff36_source_decision_counts.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(non_l7) < 3:
        blockers.append("non_l7_selected_clues_below_3")
    if non_l7_family_count < 3:
        blockers.append("non_l7_selected_family_count_below_3")
    if control_block_count:
        blockers.append("selected_control_dominated_rows_present")
    if rank_only_count:
        warnings.append("selected_queue_contains_rank_label_diagnostic_rows")
    if control_warning_count:
        warnings.append("non_l7_selected_control_warning_rows_present")
    if no_activity_families:
        warnings.append("family_no_activity_requires_repair_or_exclusion")

    decision = "PASS_A7FF36_DIVERSIFIED_CLUES_READY_FOR_DEEP_REPLAY_CONTRACT_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF36_DIVERSIFIED_CLUE_FORENSIC_BLOCKED"
    manifest = {
        "stage": "A7FF-36",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff35_decision": f35.get("decision"),
        "selected_count": int(len(selected)),
        "selected_non_l7_count": int(len(non_l7)),
        "selected_rank_label_only_count": rank_only_count,
        "selected_non_l7_family_count": non_l7_family_count,
        "selected_control_warning_count": control_warning_count,
        "selected_control_block_count": control_block_count,
        "no_activity_families": no_activity_families,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff37_deep_replay_contract": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff36_manifest.json", manifest)
    write_json(RUNTIME / "a7ff36_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-36 DIVERSIFIED CLUE FORENSIC

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-36 audits the A7FF-35 diversified numeric preflight. It separates non-L7 clues from ranked-label diagnostics, flags control-margin warnings, and identifies no-activity families. It does not run replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Selected Clue Forensic

{md_table(selected)}

## Family Activity Forensic

{md_table(family)}

## Repair Actions

{md_table(repair)}

## Decision Counts

{md_table(decision_counts)}

## Boundary

```text
deep replay contract authorized: {str(not blockers).lower()}
replay executed: false
search executed: false
May used: false
rank-label-only rows cannot promote
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
