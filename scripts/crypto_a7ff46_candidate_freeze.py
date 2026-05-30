from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff46_candidate_freeze"
REPORT = REPO / "reports" / "CRYPTO_A7FF46_CANDIDATE_FREEZE_20260531.md"

A7FF45_MANIFEST = REPO / "runtime" / "a7ff45_bounded_deep_replay" / "a7ff45_manifest.json"
A7FF45_ROWS = REPO / "runtime" / "a7ff45_bounded_deep_replay" / "a7ff45_confirmed_bounded_rows.csv"
A7FF45_FAMILY = REPO / "runtime" / "a7ff45_bounded_deep_replay" / "a7ff45_family_confirmation.csv"


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

    f45 = read_json(A7FF45_MANIFEST)
    if not f45.get("authorizes_a7ff46_candidate_freeze"):
        raise SystemExit(f"A7FF-45 does not authorize A7FF-46: {f45.get('decision')}")

    rows = read_csv(A7FF45_ROWS)
    family = read_csv(A7FF45_FAMILY)
    if rows.empty:
        raise SystemExit("A7FF-45 confirmed rows are empty")

    rows["confirmed_control_ratio"] = num(rows, "confirmed_control_ratio")
    rows["cost10_recent_oriented_confirmed"] = num(rows, "cost10_recent_oriented_confirmed")
    rows["robust_min_tstat_floor_confirmed"] = num(rows, "robust_min_tstat_floor_confirmed")
    rows["one_bar_lag_recent_oriented_confirmed"] = num(rows, "one_bar_lag_recent_oriented_confirmed")
    rows["freeze_status"] = "bounded_replay_confirmed_clue"
    rows["promotion_boundary"] = "research_clue_only_no_alpha_proof"
    rows["allowed_next_use"] = "portfolio_microreplay_and_label_diversification_audit"
    rows["forbidden_next_use"] = "formula_search_or_live_promotion"

    freeze_cols = [
        "blueprint_id",
        "expression_r9",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "confirmed_control_ratio",
        "cost10_recent_oriented_confirmed",
        "one_bar_lag_recent_oriented_confirmed",
        "robust_min_tstat_floor_confirmed",
        "confirmed_ok",
        "freeze_status",
        "promotion_boundary",
        "allowed_next_use",
        "forbidden_next_use",
    ]
    for col in freeze_cols:
        if col not in rows.columns:
            rows[col] = pd.NA
    frozen = rows[freeze_cols].copy()
    frozen.to_csv(RUNTIME / "a7ff46_frozen_candidate_pool.csv", index=False)

    family_freeze = (
        frozen.groupby("semantic_pair", dropna=False)
        .agg(
            frozen_rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            max_control_ratio=("confirmed_control_ratio", "max"),
            min_cost10=("cost10_recent_oriented_confirmed", "min"),
            min_robust_floor=("robust_min_tstat_floor_confirmed", "min"),
        )
        .reset_index()
        .sort_values("frozen_rows", ascending=False)
    )
    family_freeze.to_csv(RUNTIME / "a7ff46_family_freeze_summary.csv", index=False)

    authorization = {
        "authorized": {
            "A7FF-47": "portfolio microreplay / label diversification audit on frozen 7-row pool",
            "A7PM maintenance": "source-of-truth refresh",
        },
        "not_authorized": {
            "formula_search": "frozen clues are not alpha candidates",
            "large_search": "not authorized",
            "alpha_proof": "not authorized",
            "shadow_paper_live": "not authorized",
        },
    }
    write_json(RUNTIME / "a7ff46_authorization_matrix.json", authorization)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(frozen) < 7:
        blockers.append("frozen_candidate_rows_below_7")
    if frozen["semantic_pair"].nunique() < 2:
        blockers.append("frozen_family_count_below_2")
    if not frozen["label_family"].nunique() >= 2:
        warnings.append("single_label_family_L5_vol_adjusted_only")
    if frozen["confirmed_control_ratio"].max() >= 0.80:
        blockers.append("frozen_control_ratio_max_ge_0p80")
    if (frozen["cost10_recent_oriented_confirmed"] <= 0).any():
        blockers.append("frozen_cost10_nonpositive_rows_present")
    if (frozen["robust_min_tstat_floor_confirmed"] <= 0).any():
        blockers.append("frozen_robust_floor_nonpositive_rows_present")

    decision = (
        "PASS_A7FF46_CANDIDATE_FREEZE_READY_FOR_A7FF47_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF46_CANDIDATE_FREEZE_FAILED"
    )
    manifest = {
        "stage": "A7FF-46",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff45_decision": f45.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "frozen_candidate_rows": int(len(frozen)),
        "frozen_family_count": int(frozen["semantic_pair"].nunique()),
        "frozen_label_family_count": int(frozen["label_family"].nunique()),
        "max_control_ratio": float(frozen["confirmed_control_ratio"].max()),
        "min_cost10": float(frozen["cost10_recent_oriented_confirmed"].min()),
        "min_robust_floor": float(frozen["robust_min_tstat_floor_confirmed"].min()),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff47_portfolio_microreplay": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff46_manifest.json", manifest)
    write_json(RUNTIME / "a7ff46_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-46 CANDIDATE FREEZE

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-46 freezes the A7FF-45 bounded replay confirmed rows as research clues only. They are not alpha candidates and do not authorize formula search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Frozen Candidate Pool

{md_table(frozen)}

## Family Freeze Summary

{md_table(family_freeze)}

## A7FF-45 Family Confirmation

{md_table(family)}

## Authorization Matrix

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

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
