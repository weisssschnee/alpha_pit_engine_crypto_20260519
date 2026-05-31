from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff53e_numeric_response_summary"
REPORT = REPO / "reports" / "CRYPTO_A7FF53E_NUMERIC_RESPONSE_SUMMARY_20260531.md"
SHARD_PREFIX = "a7ff53e_"


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


def shard_dirs() -> list[Path]:
    return sorted(REPO.glob("runtime/a7ff53e_numeric_response_execution_s[0-9][0-9]"))


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    decision_frames: list[pd.DataFrame] = []
    family_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    for directory in shard_dirs():
        shard = directory.name.rsplit("_", 1)[-1].upper()
        prefix = f"{SHARD_PREFIX}{shard.lower()}"
        manifest = read_json(directory / f"{prefix}_manifest.json")
        if not manifest:
            continue
        rows.append(
            {
                "shard": shard,
                "decision": manifest.get("decision", ""),
                "blockers": ";".join(manifest.get("blockers", [])),
                "input_blueprint_count": manifest.get("input_blueprint_count", 0),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", 0),
                "label_response_rows": manifest.get("label_response_rows", 0),
                "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", 0),
                "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", 0),
                "portfolio_queue_count": manifest.get("portfolio_queue_count", 0),
                "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", 0),
                "queue_offset": manifest.get("queue_offset", 0),
            }
        )
        decisions = read_csv(directory / f"{prefix}_decision_counts.csv")
        if not decisions.empty:
            decisions["shard"] = shard
            decision_frames.append(decisions)
        families = read_csv(directory / f"{prefix}_family_decision_summary.csv")
        if not families.empty:
            families["shard"] = shard
            family_frames.append(families)
        selected = read_csv(directory / f"{prefix}_selected_portfolio_queue.csv")
        if not selected.empty:
            selected["shard"] = shard
            selected_frames.append(selected)

    shard_summary = pd.DataFrame(rows).sort_values("shard")
    all_decisions = pd.concat(decision_frames, ignore_index=True) if decision_frames else pd.DataFrame()
    all_families = pd.concat(family_frames, ignore_index=True) if family_frames else pd.DataFrame()
    all_selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()

    decision_summary = (
        all_decisions.groupby(["decision", "label_family"], dropna=False)["count"].sum().reset_index()
        if not all_decisions.empty
        else pd.DataFrame(columns=["decision", "label_family", "count"])
    )
    family_summary = (
        all_families.groupby(["semantic_pair", "decision"], dropna=False)["count"].sum().reset_index()
        if not all_families.empty
        else pd.DataFrame(columns=["semantic_pair", "decision", "count"])
    )
    selected_summary = (
        all_selected.groupby(["semantic_pair", "label_family"], dropna=False).size().reset_index(name="selected_count")
        if not all_selected.empty and {"semantic_pair", "label_family"}.issubset(all_selected.columns)
        else pd.DataFrame(columns=["semantic_pair", "label_family", "selected_count"])
    )

    primary_shards = shard_summary[~shard_summary["blockers"].astype(str).str.contains("no_activity_ok_blueprints", na=False)]
    pass_shards = shard_summary[shard_summary["decision"].astype(str).str.startswith("PASS_")]
    non_l7_total = int(shard_summary["non_l7_numeric_clue_rows"].sum()) if not shard_summary.empty else 0
    selected_total = int(shard_summary["selected_portfolio_queue_count"].sum()) if not shard_summary.empty else 0
    families_with_non_l7 = int(
        all_families.loc[all_families["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False), "semantic_pair"].nunique()
    ) if not all_families.empty else 0
    blockers: list[str] = []
    if len(shard_summary) != 8:
        blockers.append("missing_shards")
    if non_l7_total <= 0:
        blockers.append("no_non_l7_numeric_clues")
    if families_with_non_l7 < 3:
        blockers.append("non_l7_clues_too_concentrated")
    if selected_total < 16:
        blockers.append("selected_portfolio_queue_too_small")
    if int((primary_shards["materialized_activity_ok_count"] == 0).sum()) > 0:
        blockers.append("primary_shard_activity_failure")
    decision = "PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY"

    shard_summary.to_csv(RUNTIME / "a7ff53e_shard_summary.csv", index=False)
    decision_summary.to_csv(RUNTIME / "a7ff53e_decision_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ff53e_family_decision_summary.csv", index=False)
    selected_summary.to_csv(RUNTIME / "a7ff53e_selected_summary.csv", index=False)
    if not all_selected.empty:
        keep_cols = [c for c in ["shard", "blueprint_id", "label_family", "label_horizon_h", "semantic_pair", "motif", "decision", "score_no_may"] if c in all_selected.columns]
        all_selected[keep_cols].to_csv(RUNTIME / "a7ff53e_selected_portfolio_queue_compact.csv", index=False)

    manifest = {
        "stage": "A7FF-53E",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "shard_count": int(len(shard_summary)),
        "pass_shard_count": int(len(pass_shards)),
        "input_blueprint_count": int(shard_summary["input_blueprint_count"].sum()) if not shard_summary.empty else 0,
        "materialized_activity_ok_count": int(shard_summary["materialized_activity_ok_count"].sum()) if not shard_summary.empty else 0,
        "label_response_rows": int(shard_summary["label_response_rows"].sum()) if not shard_summary.empty else 0,
        "non_l7_numeric_clue_rows": non_l7_total,
        "rank_label_diagnostic_clue_rows": int(shard_summary["rank_label_diagnostic_clue_rows"].sum()) if not shard_summary.empty else 0,
        "selected_portfolio_queue_count": selected_total,
        "families_with_non_l7_clues": families_with_non_l7,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff53e_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-53E NUMERIC RESPONSE SUMMARY

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-53E summarizes bounded numeric response shards over the A7FF-52E materialized sample. It is not replay, formula search, alpha proof, shadow, paper, or live authorization.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Shard Summary

{md_table(shard_summary, 20)}

## Decision Summary

{md_table(decision_summary.sort_values("count", ascending=False), 80)}

## Family Decision Summary

{md_table(family_summary.sort_values("count", ascending=False), 80)}

## Selected Queue Summary

{md_table(selected_summary.sort_values("selected_count", ascending=False), 80)}

## Boundary

```text
numeric response executed: true
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
