from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff47_portfolio_microreplay"
REPORT = REPO / "reports" / "CRYPTO_A7FF47_PORTFOLIO_MICROREPLAY_20260531.md"

A7FF46_MANIFEST = REPO / "runtime" / "a7ff46_candidate_freeze" / "a7ff46_manifest.json"
A7FF46_POOL = REPO / "runtime" / "a7ff46_candidate_freeze" / "a7ff46_frozen_candidate_pool.csv"
A7FF45_METRICS = REPO / "runtime" / "a7ff45_bounded_deep_replay" / "a7ff45_label_response_metrics.csv"


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

    f46 = read_json(A7FF46_MANIFEST)
    if not f46.get("authorizes_a7ff47_portfolio_microreplay"):
        raise SystemExit(f"A7FF-46 does not authorize A7FF-47: {f46.get('decision')}")

    frozen = read_csv(A7FF46_POOL)
    metrics = read_csv(A7FF45_METRICS)
    if frozen.empty or metrics.empty:
        raise SystemExit("A7FF-46 frozen pool or A7FF-45 metrics are empty")

    blueprints = set(frozen["blueprint_id"].astype(str))
    focus = metrics.loc[metrics["blueprint_id"].astype(str).isin(blueprints)].copy()
    for col in [
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "cost5_recent_oriented",
        "cost2_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "robust_median_tstat_floor",
        "train_2024_tstat",
        "validation_2025H1_tstat",
        "test_2025H2_tstat",
        "recent_oos_2026JanApr_tstat",
    ]:
        focus[col] = num(focus, col)
    focus["is_numeric_clue"] = focus["decision"].astype(str).str.contains("NUMERIC_CLUE", regex=False)
    focus["control_strict"] = focus["control_ratio_premay_max"].lt(0.80)
    focus["cost10_positive"] = focus["cost10_recent_oriented"].gt(0)
    focus["lag_positive"] = focus["one_bar_lag_recent_oriented"].gt(0)
    focus["robust_positive"] = focus["robust_min_tstat_floor"].gt(0)
    focus["strict_label_translation"] = (
        focus["is_numeric_clue"]
        & focus["control_strict"]
        & focus["cost10_positive"]
        & focus["lag_positive"]
        & focus["robust_positive"]
        & ~focus["label_family"].astype(str).eq("L7_ranked_future_return")
    )
    focus["non_l5_strict_translation"] = focus["strict_label_translation"] & ~focus["label_family"].astype(str).eq(
        "L5_vol_adjusted_return"
    )
    focus.to_csv(RUNTIME / "a7ff47_label_translation_map.csv", index=False)

    label_summary = (
        focus.groupby("label_family", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            numeric_clues=("is_numeric_clue", "sum"),
            strict_translations=("strict_label_translation", "sum"),
            non_l5_strict_translations=("non_l5_strict_translation", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_cost10=("cost10_recent_oriented", "min"),
            max_cost10=("cost10_recent_oriented", "max"),
            min_robust_floor=("robust_min_tstat_floor", "min"),
        )
        .reset_index()
        .sort_values("strict_translations", ascending=False)
    )
    label_summary.to_csv(RUNTIME / "a7ff47_label_translation_summary.csv", index=False)

    family_label_summary = (
        focus.groupby(["semantic_pair", "label_family"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            strict_translations=("strict_label_translation", "sum"),
            non_l5_strict_translations=("non_l5_strict_translation", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_cost10=("cost10_recent_oriented", "min"),
            max_cost10=("cost10_recent_oriented", "max"),
        )
        .reset_index()
    )
    family_label_summary.to_csv(RUNTIME / "a7ff47_family_label_summary.csv", index=False)

    strict_non_l5 = focus.loc[focus["non_l5_strict_translation"]].copy()
    strict_l5 = focus.loc[focus["strict_label_translation"] & focus["label_family"].astype(str).eq("L5_vol_adjusted_return")].copy()
    strict_non_l5.to_csv(RUNTIME / "a7ff47_non_l5_translation_candidates.csv", index=False)
    strict_l5.to_csv(RUNTIME / "a7ff47_l5_confirmed_candidates.csv", index=False)

    pseudo_book = (
        focus.loc[focus["strict_label_translation"]]
        .groupby(["semantic_pair", "label_family"], dropna=False)
        .agg(
            candidate_count=("blueprint_id", "nunique"),
            median_cost10=("cost10_recent_oriented", "median"),
            median_control=("control_ratio_premay_max", "median"),
            median_robust_floor=("robust_min_tstat_floor", "median"),
        )
        .reset_index()
        if not focus.empty
        else pd.DataFrame()
    )
    pseudo_book.to_csv(RUNTIME / "a7ff47_pseudo_book_proxy.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(strict_non_l5) < 2:
        blockers.append("non_l5_translation_candidates_below_2")
    if strict_non_l5["semantic_pair"].nunique() < 2 if not strict_non_l5.empty else True:
        blockers.append("non_l5_translation_family_count_below_2")
    if len(strict_l5) >= 7:
        warnings.append("l5_vol_adjusted_label_dominates")

    decision = (
        "PASS_A7FF47_PORTFOLIO_MICROREPLAY_LABEL_TRANSLATION_READY_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF47_LABEL_TRANSLATION_FAIL_L5_ONLY"
    )
    manifest = {
        "stage": "A7FF-47",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff46_decision": f46.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "frozen_blueprints": int(len(blueprints)),
        "label_metric_rows": int(len(focus)),
        "strict_label_translation_rows": int(focus["strict_label_translation"].sum()),
        "strict_l5_rows": int(len(strict_l5)),
        "strict_non_l5_rows": int(len(strict_non_l5)),
        "strict_non_l5_family_count": int(strict_non_l5["semantic_pair"].nunique()) if not strict_non_l5.empty else 0,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7ff48": False if blockers else True,
    }
    write_json(RUNTIME / "a7ff47_manifest.json", manifest)
    write_json(RUNTIME / "a7ff47_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-47 PORTFOLIO MICROREPLAY / LABEL TRANSLATION

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-47 checks whether the frozen A7FF-46 L5 clues translate to non-L5 labels. It does not run generation, numeric probe, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Label Translation Summary

{md_table(label_summary)}

## Family Label Summary

{md_table(family_label_summary)}

## Non-L5 Translation Candidates

{md_table(strict_non_l5)}

## L5 Confirmed Candidates

{md_table(strict_l5)}

## Pseudo Book Proxy

{md_table(pseudo_book)}

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
