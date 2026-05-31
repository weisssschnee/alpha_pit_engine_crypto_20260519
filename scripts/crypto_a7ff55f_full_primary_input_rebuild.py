from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55f_full_primary_input_rebuild"
REPORT = REPO / "reports" / "CRYPTO_A7FF55F_FULL_PRIMARY_INPUT_REBUILD_20260531.md"
PRIMARY_LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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


def source_specs() -> list[tuple[str, Path]]:
    specs: list[tuple[str, Path]] = [
        ("S00", REPO / "runtime" / "a7ff53e_numeric_response_execution_s00" / "a7ff53e_s00_label_response_metrics.csv"),
        ("S01P", REPO / "runtime" / "a7ff55d_selector_repair_inputs_s01p" / "a7ff55d_s01p_label_response_metrics.csv"),
    ]
    for directory in sorted((REPO / "runtime").glob("a7ff55f_selector_repair_inputs_s??p??")):
        shard = directory.name.replace("a7ff55f_selector_repair_inputs_", "").upper()
        path = directory / f"a7ff55f_{shard.lower()}_label_response_metrics.csv"
        specs.append((shard, path))
    return specs


def score_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    for col in [
        "control_ratio_premay_max",
        "premay_positive_split_count",
        "cost5_recent_oriented",
        "robust_median_tstat_floor",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out["control_margin"] = (0.80 - out["control_ratio_premay_max"]).clip(lower=0)
    out["score_repair"] = (
        10.0
        + out["control_margin"].fillna(0) * 15.0
        + out["premay_positive_split_count"].fillna(0)
        + out["lag_ok"].astype(str).str.lower().isin(["true", "1"]).astype(float)
        + out["robust_ok"].astype(str).str.lower().isin(["true", "1"]).astype(float)
        + out["cost5_recent_oriented"].fillna(0).clip(lower=0) * 1000.0
        + out["robust_median_tstat_floor"].fillna(0).clip(lower=0)
    )
    return out.sort_values(["score_repair", "control_ratio_premay_max", "blueprint_id"], ascending=[False, True, True])


def cap_limit(max_rows: int, share: float) -> int:
    return max(1, int(max_rows * share))


def select_with_caps(candidates: pd.DataFrame, max_rows: int = 64) -> pd.DataFrame:
    selected: list[dict[str, Any]] = []
    label_counts = {label: 0 for label in PRIMARY_LABELS}
    family_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    used_blueprints: set[str] = set()
    family_limit = cap_limit(max_rows, 0.30)
    motif_limit = cap_limit(max_rows, 0.30)
    label_limit = cap_limit(max_rows, 0.35)

    def add_row(row: pd.Series) -> bool:
        blueprint_id = str(row["blueprint_id"])
        label = str(row["label_family"])
        family = str(row["semantic_pair"])
        motif = str(row["motif"])
        if blueprint_id in used_blueprints or len(selected) >= max_rows:
            return False
        if label_counts.get(label, 0) >= label_limit:
            return False
        if family_counts.get(family, 0) >= family_limit:
            return False
        if motif_counts.get(motif, 0) >= motif_limit:
            return False
        selected.append(row.to_dict())
        used_blueprints.add(blueprint_id)
        label_counts[label] = label_counts.get(label, 0) + 1
        family_counts[family] = family_counts.get(family, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        return True

    # First fill the three primary-label quotas.
    for label in PRIMARY_LABELS:
        for _, row in candidates[candidates["label_family"].eq(label)].iterrows():
            add_row(row)
            if label_counts.get(label, 0) >= 4:
                break

    # Then fill remaining slots with the same hard caps.
    for _, row in candidates.iterrows():
        add_row(row)
        if len(selected) >= max_rows:
            break
    return pd.DataFrame(selected)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55 = read_json(REPO / "runtime" / "a7ff55_selector_repair_contract" / "a7ff55_manifest.json")
    if m55.get("decision") != "PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        raise SystemExit(f"A7FF-55 is not ready: {m55.get('decision')}")

    frames = []
    source_rows = []
    for shard, path in source_specs():
        df = read_csv(path)
        available = not df.empty
        if available:
            df["source_shard"] = shard
            frames.append(df)
        clue_count = int(df["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False).sum()) if available and "decision" in df.columns else 0
        selected_path = path.with_name(path.name.replace("label_response_metrics", "selected_portfolio_queue"))
        selected_rows = len(read_csv(selected_path)) if selected_path.exists() else 0
        source_rows.append(
            {
                "source_shard": shard,
                "path": str(path.relative_to(REPO)),
                "rows": int(len(df)),
                "numeric_clue_rows": clue_count,
                "selected_portfolio_rows": int(selected_rows),
                "available": available,
            }
        )
    source_audit = pd.DataFrame(source_rows)
    response = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    response.to_csv(RUNTIME / "a7ff55f_available_primary_response_compact.csv", index=False)
    source_audit.to_csv(RUNTIME / "a7ff55f_source_audit.csv", index=False)

    if response.empty:
        candidates = pd.DataFrame()
    else:
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
    candidate_family_summary = candidates.groupby(["label_family", "semantic_pair"]).size().reset_index(name="candidate_rows") if not candidates.empty else pd.DataFrame(columns=["label_family", "semantic_pair", "candidate_rows"])

    candidates.to_csv(RUNTIME / "a7ff55f_primary_label_candidate_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff55f_repaired_selected_queue.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ff55f_selected_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ff55f_selected_family_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ff55f_selected_motif_summary.csv", index=False)
    candidate_family_summary.to_csv(RUNTIME / "a7ff55f_candidate_family_summary.csv", index=False)

    label_counts = dict(zip(label_summary["label_family"], label_summary["selected_count"])) if not label_summary.empty else {}
    min_primary = min([int(label_counts.get(label, 0)) for label in PRIMARY_LABELS], default=0)
    top_family_share = float(family_summary["selected_count"].max() / family_summary["selected_count"].sum()) if not family_summary.empty else 0.0
    top_motif_share = float(motif_summary["selected_count"].max() / motif_summary["selected_count"].sum()) if not motif_summary.empty else 0.0
    top_label_share = float(label_summary["selected_count"].max() / label_summary["selected_count"].sum()) if not label_summary.empty else 0.0

    blockers: list[str] = []
    if int(source_audit["available"].sum()) < 10:
        blockers.append("insufficient_primary_input_sources")
    if len(selected) < 12:
        blockers.append("selected_queue_below_primary_min_12")
    if min_primary < 4:
        blockers.append("primary_label_quota_not_met")
    if family_summary["semantic_pair"].nunique() < 3:
        blockers.append("selected_family_count_below_3")
    if motif_summary["motif"].nunique() < 4:
        blockers.append("selected_motif_count_below_4")
    if top_family_share > 0.30:
        blockers.append("top_family_share_above_0p30")
    if top_motif_share > 0.30:
        blockers.append("top_motif_share_above_0p30")
    if top_label_share > 0.35:
        blockers.append("top_label_share_above_0p35")

    decision = "PASS_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_READY_NO_REPLAY_AUTH" if not blockers else "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED"
    next_allowed = "A7FF-56 replay-preflight contract drafting only" if not blockers else "A7FF-55R selector/field-family repair contract"

    manifest = {
        "stage": "A7FF-55F",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "available_response_sources": int(source_audit["available"].sum()),
        "response_rows": int(len(response)),
        "primary_label_candidate_rows": int(len(candidates)),
        "selected_rows": int(len(selected)),
        "selected_label_counts": {str(k): int(v) for k, v in label_counts.items()},
        "selected_family_count": int(family_summary["semantic_pair"].nunique()) if not family_summary.empty else 0,
        "selected_motif_count": int(motif_summary["motif"].nunique()) if not motif_summary.empty else 0,
        "top_family_share": top_family_share,
        "top_motif_share": top_motif_share,
        "top_label_share": top_label_share,
        "executes_selector_dryrun": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_next_contract": not bool(blockers),
        "next_allowed": next_allowed,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55f_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55F FULL PRIMARY INPUT REBUILD

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55F consolidates the rebuilt primary-label response inputs into one selector-repair dryrun. It does not execute replay or search. The detailed S02-S06 micro-shard artifacts may be compacted into `runtime/a7ff55f_full_primary_input_rebuild/a7ff55f_available_primary_response_compact.csv` and omitted from long-term version control.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Source Audit

{md_table(source_audit, 80)}

## Selected Label Summary

{md_table(label_summary, 20)}

## Selected Family Summary

{md_table(family_summary, 40)}

## Selected Motif Summary

{md_table(motif_summary, 40)}

## Candidate Family Summary

{md_table(candidate_family_summary.sort_values("candidate_rows", ascending=False), 60)}

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
