from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r5e_sharded_numeric_summary"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R5E_SHARDED_NUMERIC_SUMMARY_20260531.md"


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
    shard_rows = []
    label_frames = []
    selected_frames = []
    for directory in sorted((REPO / "runtime").glob("a7ff55r5e_repaired_atlas_numeric_s??")):
        tag = directory.name.rsplit("_", 1)[-1]
        manifest = read_json(directory / f"a7ff55r5e_{tag}_decision_record.json")
        label = read_csv(directory / f"a7ff55r5e_{tag}_label_response_metrics.csv")
        selected = read_csv(directory / f"a7ff55r5e_{tag}_selected_portfolio_queue.csv")
        if not label.empty:
            label["source_shard"] = tag.upper()
            label_frames.append(label)
        if not selected.empty:
            selected["source_shard"] = tag.upper()
            selected_frames.append(selected)
        shard_rows.append(
            {
                "source_shard": tag.upper(),
                "decision": manifest.get("decision", "missing_manifest"),
                "input_blueprint_count": int(manifest.get("input_blueprint_count", 0) or 0),
                "label_response_rows": int(manifest.get("label_response_rows", len(label)) or 0),
                "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
                "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
                "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", len(selected)) or 0),
                "queue_offset": int(manifest.get("queue_offset", -1) or -1),
                "queue_limit": int(manifest.get("queue_limit", 0) or 0),
            }
        )
    shard_summary = pd.DataFrame(shard_rows).sort_values("queue_offset")
    labels = pd.concat(label_frames, ignore_index=True) if label_frames else pd.DataFrame()
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    clue_rows = labels[labels["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)].copy() if not labels.empty else pd.DataFrame()
    selected_family = (
        selected.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .size()
        .reset_index(name="selected_rows")
        .sort_values("selected_rows", ascending=False)
        if not selected.empty
        else pd.DataFrame(columns=["semantic_pair", "motif", "label_family", "selected_rows"])
    )
    clue_family = (
        clue_rows.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .size()
        .reset_index(name="clue_rows")
        .sort_values("clue_rows", ascending=False)
        if not clue_rows.empty
        else pd.DataFrame(columns=["semantic_pair", "motif", "label_family", "clue_rows"])
    )
    shard_summary.to_csv(RUNTIME / "a7ff55r5e_shard_summary.csv", index=False)
    labels.to_csv(RUNTIME / "a7ff55r5e_label_response_compact.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff55r5e_selected_queue_compact.csv", index=False)
    clue_family.to_csv(RUNTIME / "a7ff55r5e_clue_family_summary.csv", index=False)
    selected_family.to_csv(RUNTIME / "a7ff55r5e_selected_family_summary.csv", index=False)

    total_inputs = int(shard_summary["input_blueprint_count"].sum()) if not shard_summary.empty else 0
    total_clues = int(shard_summary["non_l7_numeric_clue_rows"].sum()) if not shard_summary.empty else 0
    total_selected = int(shard_summary["selected_portfolio_queue_count"].sum()) if not shard_summary.empty else 0
    blockers: list[str] = []
    if total_inputs < 350:
        blockers.append("sampled_input_rows_below_350")
    if total_clues < 12:
        blockers.append("non_l7_clue_rows_below_12")
    if total_selected < 8:
        blockers.append("selected_queue_rows_below_8")
    if selected["semantic_pair"].nunique() < 3 if not selected.empty else True:
        blockers.append("selected_semantic_pair_count_below_3")
    decision = "PASS_A7FF55R5E_SHARDED_NUMERIC_SAMPLE_READY_FOR_EXPANSION" if not blockers else "HOLD_A7FF55R5E_SHARDED_NUMERIC_WEAK_RESPONSE"
    manifest = {
        "stage": "A7FF-55R5E",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "shard_count": int(len(shard_summary)),
        "sampled_input_blueprints": total_inputs,
        "label_response_rows": int(len(labels)),
        "non_l7_numeric_clue_rows": total_clues,
        "selected_portfolio_queue_count": total_selected,
        "selected_semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "selected_motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "executes_numeric": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-55R6 numeric response forensic / atlas repair" if blockers else "A7FF-55R5F expanded sharded numeric execution",
    }
    write_json(RUNTIME / "a7ff55r5e_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-55R5E SHARDED NUMERIC SUMMARY

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R5E summarizes the completed repaired-atlas numeric shards. It is numeric-only and does not execute replay or search. Detailed shard runtime directories may be compacted into `runtime/a7ff55r5e_sharded_numeric_summary/a7ff55r5e_label_response_compact.csv` and omitted from long-term version control.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Shard Summary

{md_table(shard_summary, 80)}

## Clue Family Summary

{md_table(clue_family, 80)}

## Selected Family Summary

{md_table(selected_family, 80)}

## Boundary

```text
numeric execution: true
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
