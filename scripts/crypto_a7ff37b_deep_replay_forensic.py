from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff37b_deep_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF37B_DEEP_REPLAY_FORENSIC_20260530.md"

A7FF37A_MANIFEST = REPO / "runtime" / "a7ff37a_bounded_deep_replay" / "a7ff37a_manifest.json"
A7FF37A_SELECTED = REPO / "runtime" / "a7ff37a_bounded_deep_replay" / "a7ff37a_selected_portfolio_queue.csv"
A7FF37A_DECISIONS = REPO / "runtime" / "a7ff37a_bounded_deep_replay" / "a7ff37a_decision_counts.csv"
A7FF37A_FAMILY = REPO / "runtime" / "a7ff37a_bounded_deep_replay" / "a7ff37a_family_decision_summary.csv"
A7FF37_QUEUE = REPO / "runtime" / "a7ff37_deep_replay_contract" / "a7ff37_deep_replay_queue.csv"


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

    f37a = read_json(A7FF37A_MANIFEST)
    if not str(f37a.get("decision", "")).startswith("PASS_"):
        raise SystemExit(f"A7FF-37A did not pass: {f37a.get('decision')}")

    selected = read_csv(A7FF37A_SELECTED)
    decisions = read_csv(A7FF37A_DECISIONS)
    family = read_csv(A7FF37A_FAMILY)
    queue = read_csv(A7FF37_QUEUE)

    selected = selected.copy()
    selected["control_ratio_premay_max"] = pd.to_numeric(selected.get("control_ratio_premay_max"), errors="coerce")
    selected["is_rank_label"] = selected["label_family"].astype(str).eq("L7_ranked_future_return")
    selected["is_non_l7"] = ~selected["is_rank_label"]
    selected["forensic_class"] = "non_l7_keep_for_focused_replay"
    selected.loc[selected["is_rank_label"], "forensic_class"] = "rank_label_diagnostic_only"
    selected.loc[selected["control_ratio_premay_max"].ge(0.80) & selected["is_non_l7"], "forensic_class"] = "non_l7_keep_with_control_warning"
    selected.to_csv(RUNTIME / "a7ff37b_selected_forensic.csv", index=False)

    non_l7_selected = selected[selected["is_non_l7"]].copy()
    rank_selected = selected[selected["is_rank_label"]].copy()
    family_focus = (
        selected.groupby(["semantic_pair", "is_non_l7"], dropna=False)
        .agg(
            selected_count=("blueprint_id", "count"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            mean_score_no_may=("score_no_may", "mean"),
        )
        .reset_index()
        .sort_values(["is_non_l7", "selected_count"], ascending=[False, False])
    )
    family_focus.to_csv(RUNTIME / "a7ff37b_family_focus.csv", index=False)

    actions = pd.DataFrame(
        [
            {
                "target": "funding_like|basis_premium_like",
                "action": "focus_deep_replay_expansion",
                "reason": "2 selected non-L7 clues; control ratios below 0.80 in A7FF-37A selected queue",
            },
            {
                "target": "regime_state|price_return_like",
                "action": "keep_with_control_margin_audit",
                "reason": "1 selected non-L7 clue but control ratio is warning range above 0.80",
            },
            {
                "target": "basis_premium_like|basis_premium_like",
                "action": "diagnostic_only_until_non_l7_selected",
                "reason": "basis safe_div selected only under L7 ranked label in A7FF-37A",
            },
            {
                "target": "D6_listing_latent_lifecycle",
                "action": "exclude_from_next_replay_until_activity_repair",
                "reason": "A7FF-36 found no activity for listing/latent family",
            },
        ]
    )
    actions.to_csv(RUNTIME / "a7ff37b_next_actions.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    non_l7_family_count = int(non_l7_selected["semantic_pair"].nunique()) if not non_l7_selected.empty else 0
    if len(non_l7_selected) < 3:
        blockers.append("selected_non_l7_count_below_3")
    if non_l7_family_count < 2:
        blockers.append("selected_non_l7_family_count_below_2")
    if len(rank_selected):
        warnings.append("selected_queue_contains_rank_label_diagnostic")
    if (non_l7_selected["control_ratio_premay_max"] >= 0.80).any():
        warnings.append("non_l7_control_warning_present")

    decision = "PASS_A7FF37B_FOCUSED_REPLAY_FOLLOWUP_READY_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF37B_DEEP_REPLAY_FORENSIC_BLOCKED"
    manifest = {
        "stage": "A7FF-37B",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff37a_decision": f37a.get("decision"),
        "input_queue_count": int(len(queue)),
        "selected_count": int(len(selected)),
        "selected_non_l7_count": int(len(non_l7_selected)),
        "selected_rank_label_count": int(len(rank_selected)),
        "selected_non_l7_family_count": non_l7_family_count,
        "non_l7_numeric_clue_rows": int(f37a.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(f37a.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff38_focused_replay_contract": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff37b_manifest.json", manifest)
    write_json(RUNTIME / "a7ff37b_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-37B DEEP REPLAY FORENSIC

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-37B summarizes A7FF-37A bounded deep replay. The result is not an alpha pass. It supports a focused replay follow-up around funding-dense and regime-relative-value clues, while keeping rank-label-only and no-activity families out of promotion.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Selected Forensic

{md_table(selected)}

## Family Focus

{md_table(family_focus)}

## Next Actions

{md_table(actions)}

## Decision Counts

{md_table(decisions)}

## Family Decision Summary

{md_table(family)}

## Boundary

```text
focused replay contract authorized: {str(not blockers).lower()}
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
