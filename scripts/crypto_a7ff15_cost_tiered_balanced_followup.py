from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff15_cost_tiered_balanced_followup"
REPORT = REPO / "reports" / "CRYPTO_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_20260530.md"

A7FF14_MANIFEST = REPO / "runtime" / "a7ff14_label_balanced_selector_repair" / "a7ff14_manifest.json"
A7FF14_QUEUE = REPO / "runtime" / "a7ff14_label_balanced_selector_repair" / "a7ff14_label_balanced_selected_queue.csv"

LABEL_ORDER = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
]

TARGET_TOTAL = 160
MIN_ACCEPTABLE_TOTAL = 144
LABEL_QUOTA = 40
SEMANTIC_CAP = 48
MOTIF_CAP = 48
SKELETON_CAP = 12
BLUEPRINT_ROW_CAP = 2


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def load_shard_frames(suffix: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    pattern = REPO / "runtime" / "a7ff12_company_numeric_probe_shard_*" / f"a7ff12s*_{suffix}.csv"
    for path in sorted(glob.glob(str(pattern))):
        p = Path(path)
        shard = p.parent.name.rsplit("_", 1)[-1]
        df = pd.read_csv(p)
        df.insert(0, "shard", shard)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def assign_cost_tier(df: pd.DataFrame) -> pd.Series:
    strict = (
        (df["control_ratio_premay_max"] < 0.80)
        & (df["cost10_recent_oriented"] > 0)
        & (df["robust_min_tstat_floor"] > 0)
    )
    cost5 = (
        ~strict
        & (df["control_ratio_premay_max"] < 0.90)
        & (df["cost5_recent_oriented"] > 0)
        & (df["robust_min_tstat_floor"] > 0)
    )
    out = pd.Series("cost2_numeric_diagnostic", index=df.index)
    out.loc[cost5] = "cost5_followup"
    out.loc[strict] = "strict_cost10"
    return out


def cost_tier_rank(tier: str) -> int:
    return {"strict_cost10": 3, "cost5_followup": 2, "cost2_numeric_diagnostic": 1}.get(str(tier), 0)


def build_candidate_pool() -> pd.DataFrame:
    responses = load_shard_frames("label_response_metrics")
    mats = load_shard_frames("materialization_metrics")
    if responses.empty:
        raise SystemExit("missing A7FF-12 label response metrics")
    if mats.empty:
        raise SystemExit("missing A7FF-12 materialization metrics")

    for col in ["lag_ok", "robust_ok", "premay_all_positive"]:
        responses[col] = bool_series(responses[col])

    pool = responses[
        responses["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)
        & responses["label_family"].isin(LABEL_ORDER)
        & responses["premay_all_positive"]
        & responses["lag_ok"]
        & responses["robust_ok"]
        & (responses["control_ratio_premay_max"] < 1.0)
        & (responses["cost2_recent_oriented"] > 0)
    ].copy()

    mat_cols = ["shard", "blueprint_id", "skeleton_key", "finite_share", "nonzero_share"]
    pool = pool.merge(mats[mat_cols], on=["shard", "blueprint_id"], how="left")
    pool["cost_tier"] = assign_cost_tier(pool)
    pool["cost_tier_rank"] = pool["cost_tier"].map(cost_tier_rank).astype(int)
    pool["followup_score"] = (
        4.0 * pool["cost_tier_rank"].astype(float)
        + 3.0 * (1.0 - pool["control_ratio_premay_max"].clip(upper=1.0))
        + pool["premay_positive_split_count"].astype(float)
        + pool["robust_min_tstat_floor"].clip(lower=0.0)
        + pool["cost2_recent_oriented"].clip(lower=0.0) * 1000.0
        + pool["cost5_recent_oriented"].clip(lower=0.0) * 500.0
        + pool["cost10_recent_oriented"].clip(lower=0.0) * 250.0
    )
    return pool


def select_followup(pool: pd.DataFrame) -> pd.DataFrame:
    selected_rows: list[dict[str, Any]] = []
    label_counts: dict[str, int] = {}
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    blueprint_counts: dict[str, int] = {}

    for label in LABEL_ORDER:
        sub = pool[pool["label_family"].eq(label)].sort_values(
            [
                "cost_tier_rank",
                "followup_score",
                "control_ratio_premay_max",
                "cost10_recent_oriented",
                "robust_min_tstat_floor",
            ],
            ascending=[False, False, True, False, False],
        )
        for _, row in sub.iterrows():
            if label_counts.get(label, 0) >= LABEL_QUOTA:
                break
            bp = str(row["blueprint_id"])
            sem = str(row["semantic_pair"])
            motif = str(row["motif"])
            skel = str(row.get("skeleton_key", ""))
            if blueprint_counts.get(bp, 0) >= BLUEPRINT_ROW_CAP:
                continue
            if semantic_counts.get(sem, 0) >= SEMANTIC_CAP:
                continue
            if motif_counts.get(motif, 0) >= MOTIF_CAP:
                continue
            if skeleton_counts.get(skel, 0) >= SKELETON_CAP:
                continue
            payload = row.to_dict()
            payload["followup_rank"] = len(selected_rows) + 1
            selected_rows.append(payload)
            label_counts[label] = label_counts.get(label, 0) + 1
            semantic_counts[sem] = semantic_counts.get(sem, 0) + 1
            motif_counts[motif] = motif_counts.get(motif, 0) + 1
            skeleton_counts[skel] = skeleton_counts.get(skel, 0) + 1
            blueprint_counts[bp] = blueprint_counts.get(bp, 0) + 1
            if len(selected_rows) >= TARGET_TOTAL:
                break
    return pd.DataFrame(selected_rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff14 = read_json(A7FF14_MANIFEST)
    a7ff14_queue = pd.read_csv(A7FF14_QUEUE) if A7FF14_QUEUE.exists() else pd.DataFrame()
    pool = build_candidate_pool()
    selected = select_followup(pool)

    candidate_label_summary = (
        pool.groupby(["label_family", "label_horizon_h", "cost_tier"], dropna=False)
        .agg(
            candidate_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost2=("cost2_recent_oriented", "median"),
            median_cost5=("cost5_recent_oriented", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["label_family", "label_horizon_h", "cost_tier"])
    )
    selected_label_summary = (
        selected.groupby(["label_family", "label_horizon_h", "cost_tier"], dropna=False)
        .agg(
            selected_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost2=("cost2_recent_oriented", "median"),
            median_cost5=("cost5_recent_oriented", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["label_family", "label_horizon_h", "cost_tier"])
        if not selected.empty
        else pd.DataFrame()
    )
    selected_semantic_summary = (
        selected.groupby("semantic_pair", dropna=False)
        .agg(
            selected_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("selected_rows", ascending=False)
        if not selected.empty
        else pd.DataFrame()
    )
    selected_motif_summary = (
        selected.groupby("motif", dropna=False)
        .agg(selected_rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values("selected_rows", ascending=False)
        if not selected.empty
        else pd.DataFrame()
    )
    selected_blueprint_summary = (
        selected.groupby("blueprint_id", dropna=False)
        .agg(
            selected_rows=("blueprint_id", "count"),
            label_families=("label_family", "nunique"),
            horizons=("label_horizon_h", "nunique"),
            best_cost_tier_rank=("cost_tier_rank", "max"),
            max_followup_score=("followup_score", "max"),
            expression=("expression", "first"),
            semantic_pair=("semantic_pair", "first"),
            motif=("motif", "first"),
            skeleton_key=("skeleton_key", "first"),
        )
        .reset_index()
        .sort_values(["best_cost_tier_rank", "max_followup_score"], ascending=[False, False])
        if not selected.empty
        else pd.DataFrame()
    )

    selected_count = int(len(selected))
    unique_blueprints = int(selected["blueprint_id"].nunique()) if not selected.empty else 0
    label_families = int(selected["label_family"].nunique()) if not selected.empty else 0
    top_label_share = float(selected["label_family"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    top_semantic_share = float(selected["semantic_pair"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    top_motif_share = float(selected["motif"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    strict_rows = int(selected["cost_tier"].eq("strict_cost10").sum()) if not selected.empty else 0
    cost5_or_better_rows = int(selected["cost_tier"].isin(["strict_cost10", "cost5_followup"]).sum()) if not selected.empty else 0
    l3_strict_rows = int(
        selected[selected["label_family"].eq("L3_liquidity_tier_relative_return")]["cost_tier"].eq("strict_cost10").sum()
    ) if not selected.empty else 0

    warnings: list[str] = []
    if l3_strict_rows == 0:
        warnings.append("L3_liquidity_tier_relative_return_has_no_strict_cost10_rows")
    if cost5_or_better_rows < 64:
        warnings.append("cost5_or_better_rows_below_64")

    pass_ready = (
        selected_count >= MIN_ACCEPTABLE_TOTAL
        and label_families == len(LABEL_ORDER)
        and top_label_share <= 0.27
        and top_semantic_share <= 0.35
        and top_motif_share <= 0.35
        and unique_blueprints >= 80
        and strict_rows >= 30
    )
    decision = (
        "PASS_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_READY_FOR_A7FF16_WITH_L3_COST_WARNING"
        if pass_ready and warnings
        else "PASS_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_READY_FOR_A7FF16"
        if pass_ready
        else "HOLD_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_INSUFFICIENT"
    )

    manifest = {
        "stage": "A7FF-15-COST-TIERED-BALANCED-FOLLOWUP",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff14_decision": a7ff14.get("decision", ""),
        "input_candidate_rows": int(len(pool)),
        "input_unique_blueprints": int(pool["blueprint_id"].nunique()) if not pool.empty else 0,
        "a7ff14_selected_rows": int(len(a7ff14_queue)),
        "target_total": TARGET_TOTAL,
        "min_acceptable_total": MIN_ACCEPTABLE_TOTAL,
        "label_quota": LABEL_QUOTA,
        "selected_rows": selected_count,
        "selected_unique_blueprints": unique_blueprints,
        "selected_label_families": label_families,
        "selected_top_label_share": top_label_share,
        "selected_top_semantic_share": top_semantic_share,
        "selected_top_motif_share": top_motif_share,
        "selected_strict_cost10_rows": strict_rows,
        "selected_cost5_or_better_rows": cost5_or_better_rows,
        "l3_strict_cost10_rows": l3_strict_rows,
        "warnings": warnings,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff16_cost_tiered_numeric_followup": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    pool.to_csv(RUNTIME / "a7ff15_cost_tiered_candidate_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff15_cost_tiered_selected_queue.csv", index=False)
    candidate_label_summary.to_csv(RUNTIME / "a7ff15_candidate_label_cost_tier_summary.csv", index=False)
    selected_label_summary.to_csv(RUNTIME / "a7ff15_selected_label_cost_tier_summary.csv", index=False)
    selected_semantic_summary.to_csv(RUNTIME / "a7ff15_selected_semantic_summary.csv", index=False)
    selected_motif_summary.to_csv(RUNTIME / "a7ff15_selected_motif_summary.csv", index=False)
    selected_blueprint_summary.to_csv(RUNTIME / "a7ff15_selected_blueprint_summary.csv", index=False)
    write_json(RUNTIME / "a7ff15_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ff15_experiment_record.json",
        {
            "stage": manifest["stage"],
            "decision": decision,
            "source": {
                "a7ff14_manifest": str(A7FF14_MANIFEST.relative_to(REPO)),
                "a7ff14_queue": str(A7FF14_QUEUE.relative_to(REPO)),
                "a7ff12_shards": "runtime/a7ff12_company_numeric_probe_shard_*",
            },
            "authorization": {
                "a7ff16_cost_tiered_numeric_followup": manifest["authorizes_a7ff16_cost_tiered_numeric_followup"],
                "search": False,
                "alpha_proof": False,
                "shadow_paper_live": False,
            },
        },
    )

    report = f"""# CRYPTO A7FF-15 COST-TIERED BALANCED FOLLOWUP

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-15 expands the A7FF-14 balanced selector repair into a cost-tiered follow-up queue. It uses the existing A7FF-12 numeric clue surface and does not generate formulas, execute replay, run search, use May, or authorize alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Candidate Label / Cost Tier Surface

{md_table(candidate_label_summary, 80)}

## Selected Label / Cost Tier Surface

{md_table(selected_label_summary, 80)}

## Selected Semantic Surface

{md_table(selected_semantic_summary, 40)}

## Selected Motif Surface

{md_table(selected_motif_summary, 40)}

## Selected Blueprint Surface

{md_table(selected_blueprint_summary[["blueprint_id", "selected_rows", "label_families", "horizons", "best_cost_tier_rank", "semantic_pair", "motif"]], 80)}

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
