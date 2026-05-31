from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55d_selector_repair_partial_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7FF55D_SELECTOR_REPAIR_PARTIAL_DRYRUN_20260531.md"
PRIMARY_LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"]


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


def score_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["control_margin"] = (0.80 - pd.to_numeric(out["control_ratio_premay_max"], errors="coerce")).clip(lower=0)
    out["score_repair"] = (
        10.0
        + out["control_margin"].fillna(0) * 10.0
        + pd.to_numeric(out["premay_positive_split_count"], errors="coerce").fillna(0)
        + out["lag_ok"].astype(str).str.lower().isin(["true", "1"]).astype(float)
        + out["robust_ok"].astype(str).str.lower().isin(["true", "1"]).astype(float)
        + pd.to_numeric(out["cost5_recent_oriented"], errors="coerce").fillna(0).clip(lower=0) * 1000.0
    )
    return out.sort_values(["score_repair", "blueprint_id"], ascending=[False, True])


def select_with_caps(candidates: pd.DataFrame, max_rows: int = 64) -> pd.DataFrame:
    selected: list[dict[str, Any]] = []
    label_counts = {label: 0 for label in PRIMARY_LABELS}
    family_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    used_blueprints: set[str] = set()

    def can_add(row: pd.Series, strict_label_quota: bool) -> bool:
        if row["blueprint_id"] in used_blueprints:
            return False
        label = str(row["label_family"])
        family = str(row["semantic_pair"])
        motif = str(row["motif"])
        next_total = len(selected) + 1
        if next_total > max_rows:
            return False
        if family_counts.get(family, 0) + 1 > max(1, int(0.30 * max_rows)):
            return False
        if motif_counts.get(motif, 0) + 1 > max(1, int(0.30 * max_rows)):
            return False
        if strict_label_quota and label_counts.get(label, 0) >= 4:
            return False
        return True

    # First satisfy the A7FF-55 primary label quota where possible.
    for label in PRIMARY_LABELS:
        pool = candidates[candidates["label_family"].eq(label)]
        for _, row in pool.iterrows():
            if can_add(row, strict_label_quota=True):
                selected.append(row.to_dict())
                label_counts[label] += 1
                family_counts[str(row["semantic_pair"])] = family_counts.get(str(row["semantic_pair"]), 0) + 1
                motif_counts[str(row["motif"])] = motif_counts.get(str(row["motif"]), 0) + 1
                used_blueprints.add(str(row["blueprint_id"]))
            if label_counts[label] >= 4:
                break

    # Then add diverse remaining primary-label rows.
    for _, row in candidates.iterrows():
        if can_add(row, strict_label_quota=False):
            selected.append(row.to_dict())
            label = str(row["label_family"])
            label_counts[label] = label_counts.get(label, 0) + 1
            family_counts[str(row["semantic_pair"])] = family_counts.get(str(row["semantic_pair"]), 0) + 1
            motif_counts[str(row["motif"])] = motif_counts.get(str(row["motif"]), 0) + 1
            used_blueprints.add(str(row["blueprint_id"]))
        if len(selected) >= max_rows:
            break
    return pd.DataFrame(selected)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55 = read_json(REPO / "runtime" / "a7ff55_selector_repair_contract" / "a7ff55_manifest.json")
    if m55.get("decision") != "PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        raise SystemExit(f"A7FF-55 is not ready: {m55.get('decision')}")

    sources = [
        ("S00", REPO / "runtime" / "a7ff53e_numeric_response_execution_s00" / "a7ff53e_s00_label_response_metrics.csv"),
        ("S01P", REPO / "runtime" / "a7ff55d_selector_repair_inputs_s01p" / "a7ff55d_s01p_label_response_metrics.csv"),
    ]
    frames = []
    source_rows = []
    for shard, path in sources:
        df = read_csv(path)
        if not df.empty:
            df["source_shard"] = shard
            frames.append(df)
        source_rows.append({"source_shard": shard, "path": str(path.relative_to(REPO)), "rows": int(len(df)), "available": not df.empty})
    source_audit = pd.DataFrame(source_rows)
    response = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    response.to_csv(RUNTIME / "a7ff55d_available_response_compact.csv", index=False)
    source_audit.to_csv(RUNTIME / "a7ff55d_source_audit.csv", index=False)

    candidates = response[
        response["label_family"].isin(PRIMARY_LABELS)
        & response["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)
        & (pd.to_numeric(response["control_ratio_premay_max"], errors="coerce") < 0.80)
    ].copy()
    candidates = score_rows(candidates) if not candidates.empty else candidates
    selected = select_with_caps(candidates, max_rows=64) if not candidates.empty else pd.DataFrame()

    label_summary = selected.groupby("label_family").size().reset_index(name="selected_count") if not selected.empty else pd.DataFrame(columns=["label_family", "selected_count"])
    family_summary = selected.groupby("semantic_pair").size().reset_index(name="selected_count") if not selected.empty else pd.DataFrame(columns=["semantic_pair", "selected_count"])
    motif_summary = selected.groupby("motif").size().reset_index(name="selected_count") if not selected.empty else pd.DataFrame(columns=["motif", "selected_count"])
    candidates.to_csv(RUNTIME / "a7ff55d_primary_label_candidate_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff55d_repaired_selected_queue.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ff55d_selected_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ff55d_selected_family_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ff55d_selected_motif_summary.csv", index=False)

    label_counts = dict(zip(label_summary["label_family"], label_summary["selected_count"])) if not label_summary.empty else {}
    min_primary = min([int(label_counts.get(label, 0)) for label in PRIMARY_LABELS], default=0)
    top_family_share = float(family_summary["selected_count"].max() / family_summary["selected_count"].sum()) if not family_summary.empty else 0.0
    top_motif_share = float(motif_summary["selected_count"].max() / motif_summary["selected_count"].sum()) if not motif_summary.empty else 0.0
    blockers: list[str] = []
    if len(source_audit[source_audit["available"]]) < 2:
        blockers.append("insufficient_available_response_sources")
    if len(selected) < 12:
        blockers.append("selected_queue_below_primary_min_12")
    if min_primary < 4:
        blockers.append("primary_label_quota_not_met")
    if family_summary["semantic_pair"].nunique() < 2:
        blockers.append("partial_scope_family_count_below_2")
    if top_family_share > 0.30:
        blockers.append("top_family_share_above_0p30")
    if top_motif_share > 0.30:
        blockers.append("top_motif_share_above_0p30")
    # This is a partial dryrun by design: it cannot authorize replay until all primary shards are rebuilt.
    blockers.append("partial_scope_not_replay_authorizing")
    decision = "HOLD_A7FF55D_PARTIAL_SELECTOR_DRYRUN_REQUIRES_FULL_INPUT_REBUILD"

    manifest = {
        "stage": "A7FF-55D",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "available_response_sources": int(source_audit["available"].sum()),
        "response_rows": int(len(response)),
        "primary_label_candidate_rows": int(len(candidates)),
        "selected_rows": int(len(selected)),
        "selected_label_counts": label_counts,
        "selected_family_count": int(family_summary["semantic_pair"].nunique()) if not family_summary.empty else 0,
        "selected_motif_count": int(motif_summary["motif"].nunique()) if not motif_summary.empty else 0,
        "top_family_share": top_family_share,
        "top_motif_share": top_motif_share,
        "executes_selector_dryrun": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_full_input_rebuild": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55d_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55D SELECTOR REPAIR PARTIAL DRYRUN

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55D tests the repaired selector target on currently available primary-label response rows. It is partial by design because full S01-S06 primary-label compact inputs were not retained. It does not authorize replay or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Source Audit

{md_table(source_audit, 20)}

## Selected Label Summary

{md_table(label_summary, 20)}

## Selected Family Summary

{md_table(family_summary, 20)}

## Selected Motif Summary

{md_table(motif_summary, 20)}

## Boundary

```text
selector dryrun executed: true
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
