from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff44_deep_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF44_DEEP_FORENSIC_20260531.md"

A7FF43_MANIFEST = REPO / "runtime" / "a7ff43_repaired_selector_numeric_confirmation" / "a7ff43_manifest.json"
A7FF43_CONFIRMED = REPO / "runtime" / "a7ff43_repaired_selector_numeric_confirmation" / "a7ff43_confirmed_repaired_rows.csv"
A7FF43_FAMILY = REPO / "runtime" / "a7ff43_repaired_selector_numeric_confirmation" / "a7ff43_family_confirmation.csv"


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


def classify_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["semantic_pair"] = out["semantic_pair_r8"].astype(str)
    out["motif"] = out["motif_r8"].astype(str)
    out["confirmed_control_ratio"] = num(out, "confirmed_control_ratio")
    for col in [
        "cost2_recent_oriented_confirmed",
        "cost5_recent_oriented_confirmed",
        "cost10_recent_oriented_confirmed",
        "one_bar_lag_recent_oriented_confirmed",
        "robust_min_tstat_floor_confirmed",
        "robust_median_tstat_floor_confirmed",
        "train_2024_tstat_confirmed",
        "validation_2025H1_tstat_confirmed",
        "test_2025H2_tstat_confirmed",
        "recent_oos_2026JanApr_tstat_confirmed",
        "train_2024_positive_rate_confirmed",
        "validation_2025H1_positive_rate_confirmed",
        "test_2025H2_positive_rate_confirmed",
        "recent_oos_2026JanApr_positive_rate_confirmed",
    ]:
        out[col] = num(out, col)
    out["is_reference_family"] = out["semantic_pair"].eq(REFERENCE_FAMILY)
    out["is_regime_family"] = out["semantic_pair"].eq("regime_state|price_return_like")
    out["is_funding_basis_family"] = out["semantic_pair"].eq("funding_like|basis_premium_like")
    out["cost10_positive"] = out["cost10_recent_oriented_confirmed"].gt(0)
    out["lag_positive"] = out["one_bar_lag_recent_oriented_confirmed"].gt(0)
    out["robust_floor_positive"] = out["robust_min_tstat_floor_confirmed"].gt(0)
    out["all_confirmed"] = out["confirmed_ok"].astype(str).str.lower().eq("true")
    tstat_cols = [
        "train_2024_tstat_confirmed",
        "validation_2025H1_tstat_confirmed",
        "test_2025H2_tstat_confirmed",
        "recent_oos_2026JanApr_tstat_confirmed",
    ]
    out["same_sign_tstat_splits"] = out[tstat_cols].apply(
        lambda r: int((r.dropna() > 0).all() or (r.dropna() < 0).all()), axis=1
    )
    out["min_abs_split_tstat"] = out[tstat_cols].abs().min(axis=1)
    out["forensic_role"] = "candidate_for_bounded_deep_replay"
    out.loc[out["is_reference_family"], "forensic_role"] = "reference_family_capped_diagnostic"
    out.loc[out["is_regime_family"], "forensic_role"] = "regime_singleton_candidate_needs_confirmation"
    out.loc[~out["cost10_positive"], "forensic_role"] = "cost10_fragile_hold"
    out.loc[~out["robust_floor_positive"], "forensic_role"] = "robust_floor_fragile_hold"
    out.loc[~out["all_confirmed"], "forensic_role"] = "not_confirmed_hold"
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f43 = read_json(A7FF43_MANIFEST)
    if not f43.get("authorizes_a7ff44_deep_forensic"):
        raise SystemExit(f"A7FF-43 does not authorize A7FF-44: {f43.get('decision')}")

    rows = classify_rows(read_csv(A7FF43_CONFIRMED))
    family_confirmation = read_csv(A7FF43_FAMILY)
    if rows.empty:
        raise SystemExit("A7FF-43 confirmed rows are empty")

    rows.to_csv(RUNTIME / "a7ff44_row_forensic.csv", index=False)

    family_forensic = (
        rows.groupby("semantic_pair", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            horizons=("label_horizon_h", "nunique"),
            confirmed_rows=("all_confirmed", "sum"),
            cost10_positive_rows=("cost10_positive", "sum"),
            lag_positive_rows=("lag_positive", "sum"),
            robust_floor_positive_rows=("robust_floor_positive", "sum"),
            same_sign_tstat_rows=("same_sign_tstat_splits", "sum"),
            median_control_ratio=("confirmed_control_ratio", "median"),
            max_control_ratio=("confirmed_control_ratio", "max"),
            min_abs_split_tstat=("min_abs_split_tstat", "min"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    family_forensic["family_status"] = "candidate_family"
    family_forensic.loc[family_forensic["semantic_pair"].eq(REFERENCE_FAMILY), "family_status"] = "reference_family_cap_required"
    family_forensic.loc[
        family_forensic["semantic_pair"].eq("regime_state|price_return_like") & family_forensic["rows"].lt(2),
        "family_status",
    ] = "singleton_family_needs_more_evidence"
    family_forensic.to_csv(RUNTIME / "a7ff44_family_forensic.csv", index=False)

    concentration = pd.DataFrame(
        [
            {
                "metric": "top_family_share",
                "value": float(rows["semantic_pair"].value_counts().iloc[0] / len(rows)),
                "threshold": 0.60,
                "pass": bool(rows["semantic_pair"].value_counts().iloc[0] / len(rows) <= 0.60),
            },
            {
                "metric": "reference_family_share",
                "value": float(rows["is_reference_family"].mean()),
                "threshold": 0.50,
                "pass": bool(rows["is_reference_family"].mean() <= 0.50),
            },
            {
                "metric": "non_reference_family_count",
                "value": int(rows.loc[~rows["is_reference_family"], "semantic_pair"].nunique()),
                "threshold": 2,
                "pass": bool(rows.loc[~rows["is_reference_family"], "semantic_pair"].nunique() >= 2),
            },
            {
                "metric": "candidate_for_bounded_deep_replay_rows",
                "value": int(rows["forensic_role"].eq("candidate_for_bounded_deep_replay").sum()),
                "threshold": 4,
                "pass": bool(rows["forensic_role"].eq("candidate_for_bounded_deep_replay").sum() >= 4),
            },
        ]
    )
    concentration.to_csv(RUNTIME / "a7ff44_concentration_audit.csv", index=False)

    next_queue = rows[
        rows["forensic_role"].isin(
            ["candidate_for_bounded_deep_replay", "regime_singleton_candidate_needs_confirmation"]
        )
    ].copy()
    next_queue = next_queue.sort_values(["is_regime_family", "confirmed_control_ratio"], ascending=[False, True])
    next_queue.to_csv(RUNTIME / "a7ff44_bounded_deep_replay_queue.csv", index=False)
    bounded_queue_family_count = int(next_queue["semantic_pair"].nunique()) if not next_queue.empty else 0

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-45_bounded_deep_replay",
                "status": "authorized" if bounded_queue_family_count >= 2 else "not_authorized",
                "reason": "requires bounded replay queue to retain at least 2 non-reference/non-fragile families",
            },
            {
                "route": "A7FF-R9_reference_regime_repair",
                "status": "required",
                "reason": "basis self-pair is capped and regime singleton is not replay-eligible; repair before bounded replay",
            },
            {
                "route": "formula_search",
                "status": "blocked",
                "reason": "A7FF-44 is forensic only and does not authorize search",
            },
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff44_next_actions.csv", index=False)

    blockers: list[str] = []
    warnings: list[str] = []
    if not bool(concentration.loc[concentration["metric"].eq("top_family_share"), "pass"].iloc[0]):
        blockers.append("top_family_share_above_0p60")
    if not bool(concentration.loc[concentration["metric"].eq("non_reference_family_count"), "pass"].iloc[0]):
        blockers.append("non_reference_family_count_below_2")
    if rows["forensic_role"].eq("candidate_for_bounded_deep_replay").sum() < 4:
        blockers.append("bounded_deep_candidate_rows_below_4")
    if bounded_queue_family_count < 2:
        blockers.append("bounded_deep_replay_queue_family_count_below_2")
    if rows["is_reference_family"].mean() >= 0.50:
        warnings.append("reference_family_at_cap")
    if rows["is_regime_family"].sum() == 1:
        warnings.append("regime_family_singleton")

    decision = (
        "PASS_A7FF44_DEEP_FORENSIC_READY_FOR_A7FF45_BOUNDED_DEEP_REPLAY_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF44_DEEP_FORENSIC_CONCENTRATION_OR_BREADTH_FAIL"
    )
    manifest = {
        "stage": "A7FF-44",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff43_decision": f43.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "confirmed_rows": int(len(rows)),
        "confirmed_family_count": int(rows["semantic_pair"].nunique()),
        "reference_family_rows": int(rows["is_reference_family"].sum()),
        "non_reference_family_count": int(rows.loc[~rows["is_reference_family"], "semantic_pair"].nunique()),
        "bounded_deep_replay_queue_count": int(len(next_queue)),
        "bounded_deep_replay_queue_family_count": bounded_queue_family_count,
        "candidate_for_bounded_deep_replay_rows": int(rows["forensic_role"].eq("candidate_for_bounded_deep_replay").sum()),
        "regime_singleton_rows": int(rows["forensic_role"].eq("regime_singleton_candidate_needs_confirmation").sum()),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff45_bounded_deep_replay": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff44_manifest.json", manifest)
    write_json(RUNTIME / "a7ff44_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-44 DEEP FORENSIC

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-44 audits the 12 A7FF-43 repaired-selector confirmed rows. It separates promotable non-reference candidates from capped reference-family diagnostics and singleton regime evidence. It does not run numeric probe or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Confirmation From A7FF-43

{md_table(family_confirmation)}

## Row Forensic

{md_table(rows)}

## Family Forensic

{md_table(family_forensic)}

## Concentration Audit

{md_table(concentration)}

## Bounded Deep Replay Queue

{md_table(next_queue)}

## Next Actions

{md_table(next_actions)}

## Boundary

```text
numeric probe executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
