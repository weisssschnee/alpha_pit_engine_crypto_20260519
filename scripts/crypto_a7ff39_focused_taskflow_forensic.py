from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff39_focused_taskflow_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF39_FOCUSED_TASKFLOW_FORENSIC_20260530.md"

A7FF38_MANIFEST = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_manifest.json"
A7FF38_SELECTED = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_selected_portfolio_queue.csv"
A7FF38_DECISIONS = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_decision_counts.csv"
A7FF38_FAMILY = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_family_decision_summary.csv"
A7FF38_QUEUE_SUMMARY = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_queue_summary.csv"


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

    f38 = read_json(A7FF38_MANIFEST)
    if not f38.get("authorizes_a7ff39_focused_forensic"):
        raise SystemExit(f"A7FF-38 does not authorize A7FF-39: {f38.get('decision')}")

    selected = read_csv(A7FF38_SELECTED)
    decisions = read_csv(A7FF38_DECISIONS)
    family = read_csv(A7FF38_FAMILY)
    queue_summary = read_csv(A7FF38_QUEUE_SUMMARY)

    selected = selected.copy()
    selected["control_ratio_premay_max"] = pd.to_numeric(selected["control_ratio_premay_max"], errors="coerce")
    selected["is_rank_label"] = selected["label_family"].astype(str).eq("L7_ranked_future_return")
    selected["is_non_l7"] = ~selected["is_rank_label"]
    selected["control_bucket"] = "clean_lt_0p80"
    selected.loc[selected["control_ratio_premay_max"].ge(0.80), "control_bucket"] = "warning_0p80_to_1p00"
    selected.loc[selected["control_ratio_premay_max"].ge(1.00), "control_bucket"] = "blocked_ge_1p00"
    selected["forensic_decision"] = "candidate_for_followup"
    selected.loc[selected["is_rank_label"], "forensic_decision"] = "rank_label_diagnostic_only"
    selected.loc[selected["is_non_l7"] & selected["control_ratio_premay_max"].ge(0.80), "forensic_decision"] = "non_l7_control_warning"
    selected.loc[selected["control_ratio_premay_max"].ge(1.00), "forensic_decision"] = "control_dominated_reject"
    selected.to_csv(RUNTIME / "a7ff39_selected_forensic.csv", index=False)

    non_l7 = selected[selected["is_non_l7"]].copy()
    non_l7_clean = non_l7[non_l7["control_ratio_premay_max"].lt(0.80)].copy()
    rank_only = selected[selected["is_rank_label"]].copy()
    focus_summary = (
        selected.groupby(["semantic_pair", "is_non_l7", "control_bucket"], dropna=False)
        .agg(selected_count=("blueprint_id", "count"), max_control_ratio=("control_ratio_premay_max", "max"), mean_score_no_may=("score_no_may", "mean"))
        .reset_index()
        .sort_values(["is_non_l7", "selected_count"], ascending=[False, False])
    )
    focus_summary.to_csv(RUNTIME / "a7ff39_focus_summary.csv", index=False)

    family_health = family.copy()
    if not family_health.empty:
        family_health["is_clue"] = family_health["decision"].astype(str).str.contains("NUMERIC_CLUE|RANK_LABEL_DIAGNOSTIC", regex=True)
    family_health.to_csv(RUNTIME / "a7ff39_family_health.csv", index=False)

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-40_control_strict_focused_queue",
                "action": "build control-strict follow-up queue",
                "allowed_scope": "funding_dense clean variants plus small regime control-warning audit",
                "blocked_scope": "rank-label-only rows and control_ratio >= 1.0 rows",
            },
            {
                "route": "A7FF-40R_regime_control_repair",
                "action": "repair regime_state relative-value controls before expansion",
                "allowed_scope": "regime rows only as diagnostic until control ratio < 0.80",
                "blocked_scope": "promotion/search",
            },
            {
                "route": "A7FF-40B_basis_reference",
                "action": "keep basis safe_div as reference/diagnostic",
                "allowed_scope": "small reference rows only",
                "blocked_scope": "basis-root dominance",
            },
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff39_next_actions.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(non_l7_clean) < 2:
        blockers.append("control_clean_non_l7_selected_below_2")
    if non_l7_clean["semantic_pair"].nunique() < 1:
        blockers.append("control_clean_non_l7_family_count_below_1")
    if len(rank_only):
        warnings.append("selected_contains_rank_label_diagnostic_rows")
    if len(non_l7) and len(non_l7_clean) < len(non_l7):
        warnings.append("non_l7_selected_contains_control_warning_rows")
    if non_l7_clean["semantic_pair"].nunique() == 1:
        warnings.append("control_clean_non_l7_selected_single_family")

    decision = "PASS_A7FF39_FOCUSED_FORENSIC_READY_FOR_CONTROL_STRICT_FOLLOWUP_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF39_FOCUSED_FORENSIC_CONTROL_CLEAN_TOO_WEAK"
    manifest = {
        "stage": "A7FF-39",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff38_decision": f38.get("decision"),
        "selected_count": int(len(selected)),
        "selected_non_l7_count": int(len(non_l7)),
        "selected_non_l7_clean_count": int(len(non_l7_clean)),
        "selected_non_l7_clean_family_count": int(non_l7_clean["semantic_pair"].nunique()),
        "selected_rank_label_count": int(len(rank_only)),
        "non_l7_numeric_clue_rows": int(f38.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(f38.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff40_control_strict_followup": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff39_manifest.json", manifest)
    write_json(RUNTIME / "a7ff39_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-39 FOCUSED TASKFLOW FORENSIC

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-39 audits the larger A7FF-38 taskflow. The larger run produced more non-L7 clue rows, but selected clean non-L7 evidence is still concentrated in the funding-dense family. This authorizes only a control-strict follow-up, not search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Selected Forensic

{md_table(selected)}

## Focus Summary

{md_table(focus_summary)}

## Decision Counts

{md_table(decisions)}

## Family Health

{md_table(family_health)}

## Queue Summary

{md_table(queue_summary)}

## Next Actions

{md_table(next_actions)}

## Boundary

```text
control-strict follow-up authorized: {str(not blockers).lower()}
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
