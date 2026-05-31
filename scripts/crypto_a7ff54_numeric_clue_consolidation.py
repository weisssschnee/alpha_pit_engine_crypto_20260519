from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff54_numeric_clue_consolidation"
REPORT = REPO / "reports" / "CRYPTO_A7FF54_NUMERIC_CLUE_CONSOLIDATION_20260531.md"
SOURCE = REPO / "runtime" / "a7ff53e_numeric_response_summary"
PRIMARY_LABELS = {"L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    source_manifest = read_json(SOURCE / "a7ff53e_manifest.json")
    if source_manifest.get("decision") != "PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH":
        raise SystemExit(f"A7FF-53E summary is not ready: {source_manifest.get('decision')}")

    shard_summary = read_csv(SOURCE / "a7ff53e_shard_summary.csv")
    decision_summary = read_csv(SOURCE / "a7ff53e_decision_summary.csv")
    family_summary = read_csv(SOURCE / "a7ff53e_family_decision_summary.csv")
    selected = read_csv(SOURCE / "a7ff53e_selected_portfolio_queue_compact.csv")

    clue_rows = family_summary[family_summary["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)].copy()
    selected_label = (
        selected.groupby(["label_family"], dropna=False).size().reset_index(name="selected_count")
        if not selected.empty
        else pd.DataFrame(columns=["label_family", "selected_count"])
    )
    selected_family_label = (
        selected.groupby(["semantic_pair", "label_family"], dropna=False).size().reset_index(name="selected_count")
        if not selected.empty
        else pd.DataFrame(columns=["semantic_pair", "label_family", "selected_count"])
    )
    selected_motif = (
        selected.groupby(["motif"], dropna=False).size().reset_index(name="selected_count")
        if not selected.empty
        else pd.DataFrame(columns=["motif", "selected_count"])
    )
    selected_primary = selected[selected["label_family"].isin(PRIMARY_LABELS)].copy() if not selected.empty else pd.DataFrame()
    selected_non_l7 = selected[selected["label_family"].ne("L7_ranked_future_return")].copy() if not selected.empty else pd.DataFrame()
    selected_l5 = selected[selected["label_family"].eq("L5_vol_adjusted_return")].copy() if not selected.empty else pd.DataFrame()

    policy = {
        "stage": "A7FF-54",
        "source": "A7FF-53E",
        "clue_consolidation": {
            "numeric_clue_rows": int(source_manifest.get("non_l7_numeric_clue_rows", 0)),
            "families_with_non_l7_clues": int(source_manifest.get("families_with_non_l7_clues", 0)),
            "selected_portfolio_queue_count": int(source_manifest.get("selected_portfolio_queue_count", 0)),
        },
        "blocked_replay_conditions": {
            "selected_primary_L0_L1_L3_count": "must be > 0 before replay preflight",
            "selected_L5_only_non_L7": "not replay-authorizing",
            "selected_L7_only": "diagnostic only",
        },
        "next_allowed": {
            "A7FF-55": "selector repair contract to force primary label representation and family/motif caps",
        },
        "not_authorized": ["replay", "formula search", "large search", "alpha proof", "shadow/paper/live"],
    }
    write_json(RUNTIME / "a7ff54_replay_preflight_policy.json", policy)

    clue_rows.to_csv(RUNTIME / "a7ff54_numeric_clue_family_rows.csv", index=False)
    selected_label.to_csv(RUNTIME / "a7ff54_selected_label_distribution.csv", index=False)
    selected_family_label.to_csv(RUNTIME / "a7ff54_selected_family_label_distribution.csv", index=False)
    selected_motif.to_csv(RUNTIME / "a7ff54_selected_motif_distribution.csv", index=False)

    blockers: list[str] = []
    if len(selected_primary) == 0:
        blockers.append("selected_queue_has_no_L0_L1_L3_primary_label_rows")
    if len(selected_non_l7) > 0 and len(selected_l5) == len(selected_non_l7):
        blockers.append("selected_non_l7_rows_are_L5_only")
    top_family_share = (
        float(selected_family_label.groupby("semantic_pair")["selected_count"].sum().max() / selected_family_label["selected_count"].sum())
        if not selected_family_label.empty and selected_family_label["selected_count"].sum() > 0
        else 0.0
    )
    top_motif_share = (
        float(selected_motif["selected_count"].max() / selected_motif["selected_count"].sum())
        if not selected_motif.empty and selected_motif["selected_count"].sum() > 0
        else 0.0
    )
    if top_family_share > 0.35:
        blockers.append("selected_top_family_share_above_0p35")
    if top_motif_share > 0.35:
        blockers.append("selected_top_motif_share_above_0p35")
    decision = "HOLD_A7FF54_SELECTED_QUEUE_LABEL_REPAIR_REQUIRED_NO_REPLAY_AUTH" if blockers else "PASS_A7FF54_CLUE_CONSOLIDATION_READY_FOR_REPLAY_PREFLIGHT_CONTRACT"

    manifest = {
        "stage": "A7FF-54",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_a7ff53e_decision": source_manifest.get("decision"),
        "numeric_clue_rows": int(source_manifest.get("non_l7_numeric_clue_rows", 0)),
        "rank_label_diagnostic_clue_rows": int(source_manifest.get("rank_label_diagnostic_clue_rows", 0)),
        "selected_portfolio_queue_count": int(source_manifest.get("selected_portfolio_queue_count", 0)),
        "selected_primary_L0_L1_L3_count": int(len(selected_primary)),
        "selected_non_l7_count": int(len(selected_non_l7)),
        "selected_l5_count": int(len(selected_l5)),
        "families_with_non_l7_clues": int(source_manifest.get("families_with_non_l7_clues", 0)),
        "top_selected_family_share": top_family_share,
        "top_selected_motif_share": top_motif_share,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7ff55_selector_repair_contract": True,
    }
    write_json(RUNTIME / "a7ff54_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-54 NUMERIC CLUE CONSOLIDATION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-54 consolidates A7FF-53E numeric response clues and selected queue evidence. It does not run replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Shard Summary

{md_table(shard_summary, 20)}

## Numeric Clue Rows By Family

{md_table(clue_rows, 80)}

## Selected Label Distribution

{md_table(selected_label, 30)}

## Selected Family / Label Distribution

{md_table(selected_family_label, 80)}

## Selected Motif Distribution

{md_table(selected_motif.sort_values("selected_count", ascending=False), 80)}

## Replay-Preflight Policy

```json
{json.dumps(policy, indent=2, sort_keys=True)}
```

## Boundary

```text
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
