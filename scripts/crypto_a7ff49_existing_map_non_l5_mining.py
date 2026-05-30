from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff49_existing_map_non_l5_mining"
REPORT = REPO / "reports" / "CRYPTO_A7FF49_EXISTING_MAP_NON_L5_MINING_20260531.md"

A7FFR10_MANIFEST = REPO / "runtime" / "a7ffr10_label_feature_target_redesign" / "a7ffr10_manifest.json"
A7FF42_STRICT = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_control_strict_non_l7_clues.csv"

REFERENCE_FAMILY = "basis_premium_like|basis_premium_like"


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


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
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


def num(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([float("nan")] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r10 = read_json(A7FFR10_MANIFEST)
    if not r10.get("authorizes_a7ff49_existing_map_non_l5_mining"):
        raise SystemExit(f"A7FF-R10 does not authorize A7FF-49: {r10.get('decision')}")

    rows = read_csv(A7FF42_STRICT)
    if rows.empty:
        raise SystemExit("A7FF-42 strict map is empty")
    for col in [
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "robust_median_tstat_floor",
    ]:
        rows[col] = num(rows, col)

    rows["is_non_l5_target"] = ~rows["label_family"].astype(str).isin(["L5_vol_adjusted_return", "L7_ranked_future_return"])
    rows["is_reference_family"] = rows["semantic_pair"].astype(str).eq(REFERENCE_FAMILY)
    rows["strict_non_l5_candidate"] = (
        rows["is_non_l5_target"]
        & rows["control_ratio_premay_max"].lt(0.80)
        & rows["cost10_recent_oriented"].gt(0)
        & rows["one_bar_lag_recent_oriented"].gt(0)
        & rows["robust_min_tstat_floor"].gt(0)
        & rows["is_numeric_clue"].astype(str).str.lower().eq("true")
    )
    rows["candidate_role"] = "not_non_l5_candidate"
    rows.loc[rows["strict_non_l5_candidate"] & rows["is_reference_family"], "candidate_role"] = "reference_non_l5_diagnostic"
    rows.loc[rows["strict_non_l5_candidate"] & ~rows["is_reference_family"], "candidate_role"] = "non_reference_non_l5_candidate"

    candidates = rows.loc[rows["strict_non_l5_candidate"]].copy()
    non_reference = candidates.loc[~candidates["is_reference_family"]].copy()
    reference = candidates.loc[candidates["is_reference_family"]].copy()

    candidates.to_csv(RUNTIME / "a7ff49_strict_non_l5_candidates.csv", index=False)
    non_reference.to_csv(RUNTIME / "a7ff49_non_reference_non_l5_candidates.csv", index=False)
    reference.to_csv(RUNTIME / "a7ff49_reference_non_l5_diagnostics.csv", index=False)

    summary = (
        candidates.groupby(["candidate_role", "semantic_pair", "label_family"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            motifs=("motif", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_cost10=("cost10_recent_oriented", "min"),
            min_robust_floor=("robust_min_tstat_floor", "min"),
        )
        .reset_index()
        if not candidates.empty
        else pd.DataFrame()
    )
    summary.to_csv(RUNTIME / "a7ff49_non_l5_candidate_summary.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(non_reference) < 6:
        blockers.append("non_reference_non_l5_rows_below_6")
    if non_reference["semantic_pair"].nunique() < 2 if not non_reference.empty else True:
        blockers.append("non_reference_non_l5_family_count_below_2")
    if len(reference) > 0:
        warnings.append("non_l5_evidence_exists_only_as_reference_family")

    decision = (
        "PASS_A7FF49_EXISTING_MAP_NON_L5_CANDIDATES_READY_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF49_NO_NON_REFERENCE_NON_L5_CANDIDATES"
    )
    manifest = {
        "stage": "A7FF-49",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ffr10_decision": r10.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "strict_non_l5_rows": int(len(candidates)),
        "strict_non_l5_reference_rows": int(len(reference)),
        "strict_non_l5_non_reference_rows": int(len(non_reference)),
        "strict_non_l5_non_reference_family_count": int(non_reference["semantic_pair"].nunique()) if not non_reference.empty else 0,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_next_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff49_manifest.json", manifest)
    write_json(RUNTIME / "a7ff49_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-49 EXISTING-MAP NON-L5 MINING

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-49 mines existing numeric maps for strict non-L5 evidence. It does not generate formulas, run numeric probes, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Non-L5 Candidate Summary

{md_table(summary)}

## Non-Reference Non-L5 Candidates

{md_table(non_reference)}

## Reference Non-L5 Diagnostics

{md_table(reference)}

## Boundary

```text
generation executed: false
numeric probe executed: false
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
