from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff21_external_confirmation_selector"
REPORT = REPO / "reports" / "CRYPTO_A7FF21_EXTERNAL_CONFIRMATION_SELECTOR_20260530.md"
A7FF20_MANIFEST = REPO / "runtime" / "a7ff20_confirmation_selector_triage" / "a7ff20_manifest.json"
A7FF19_AGG = REPO / "runtime" / "a7ff19_company_numeric_confirmation_aggregate"

LABEL_ORDER = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
]
TARGET_TOTAL = 64
LABEL_QUOTA = 16
SEMANTIC_CAP = 20
MOTIF_CAP = 20
SKELETON_CAP = 6
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


def cost_tier(row: pd.Series) -> str:
    if row["control_ratio_premay_max"] < 0.80 and row["cost10_recent_oriented"] > 0 and row["robust_min_tstat_floor"] > 0:
        return "strict_cost10"
    if row["control_ratio_premay_max"] < 0.90 and row["cost5_recent_oriented"] > 0 and row["robust_min_tstat_floor"] > 0:
        return "cost5_followup"
    return "cost2_numeric_diagnostic"


def tier_rank(tier: str) -> int:
    return {"strict_cost10": 3, "cost5_followup": 2, "cost2_numeric_diagnostic": 1}.get(str(tier), 0)


def load_materialization() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for i in range(2):
        sid = f"{i:02d}"
        p = REPO / "runtime" / f"a7ff19_company_numeric_confirmation_shard_{sid}" / f"a7ff19s{sid}_materialization_metrics.csv"
        if p.exists():
            df = pd.read_csv(p)
            df.insert(0, "shard", sid)
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def select_balanced(pool: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    label_counts: dict[str, int] = {}
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    blueprint_counts: dict[str, int] = {}
    for label in LABEL_ORDER:
        sub = pool[pool["label_family"].eq(label)].sort_values(
            ["tier_rank", "selector_score", "control_ratio_premay_max", "blueprint_id"],
            ascending=[False, False, True, True],
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
            payload["external_selector_rank"] = len(rows) + 1
            rows.append(payload)
            label_counts[label] = label_counts.get(label, 0) + 1
            semantic_counts[sem] = semantic_counts.get(sem, 0) + 1
            motif_counts[motif] = motif_counts.get(motif, 0) + 1
            skeleton_counts[skel] = skeleton_counts.get(skel, 0) + 1
            blueprint_counts[bp] = blueprint_counts.get(bp, 0) + 1
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff20 = read_json(A7FF20_MANIFEST)
    responses = pd.read_csv(A7FF19_AGG / "a7ff19_label_response_metrics_all_shards.csv")
    mats = load_materialization()
    if responses.empty:
        raise SystemExit("missing A7FF-19 response metrics")
    if mats.empty:
        raise SystemExit("missing A7FF-19 materialization metrics")
    responses["shard"] = responses["shard"].astype(str).str.zfill(2)
    mats["shard"] = mats["shard"].astype(str).str.zfill(2)

    pool = responses[
        responses["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)
        & responses["label_family"].isin(LABEL_ORDER)
        & (responses["control_ratio_premay_max"] < 1.0)
        & (responses["cost2_recent_oriented"] > 0)
    ].copy()
    pool = pool.merge(mats[["shard", "blueprint_id", "skeleton_key", "finite_share", "nonzero_share"]], on=["shard", "blueprint_id"], how="left")
    pool["cost_tier"] = pool.apply(cost_tier, axis=1)
    pool["tier_rank"] = pool["cost_tier"].map(tier_rank).astype(int)
    pool["selector_score"] = (
        4.0 * pool["tier_rank"].astype(float)
        + 3.0 * (1.0 - pool["control_ratio_premay_max"].clip(upper=1.0))
        + pool["premay_positive_split_count"].astype(float)
        + pool["robust_min_tstat_floor"].clip(lower=0.0)
        + pool["cost2_recent_oriented"].clip(lower=0.0) * 1000.0
        + pool["cost5_recent_oriented"].clip(lower=0.0) * 500.0
        + pool["cost10_recent_oriented"].clip(lower=0.0) * 250.0
    )
    selected = select_balanced(pool)

    candidate_label = (
        pool.groupby(["label_family", "cost_tier"], dropna=False)
        .agg(rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["label_family", "cost_tier"])
    )
    selected_label = (
        selected.groupby(["label_family", "cost_tier"], dropna=False)
        .agg(rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["label_family", "cost_tier"])
        if not selected.empty
        else pd.DataFrame()
    )
    selected_semantic = selected.groupby("semantic_pair", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False) if not selected.empty else pd.DataFrame()
    selected_motif = selected.groupby("motif", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False) if not selected.empty else pd.DataFrame()

    selected_rows = int(len(selected))
    selected_unique = int(selected["blueprint_id"].nunique()) if not selected.empty else 0
    top_label_share = float(selected["label_family"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    top_semantic_share = float(selected["semantic_pair"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    top_motif_share = float(selected["motif"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    strict_rows = int(selected["cost_tier"].eq("strict_cost10").sum()) if not selected.empty else 0
    cost5_rows = int(selected["cost_tier"].isin(["strict_cost10", "cost5_followup"]).sum()) if not selected.empty else 0
    pass_ready = (
        selected_rows == TARGET_TOTAL
        and selected["label_family"].nunique() == len(LABEL_ORDER)
        and top_label_share <= 0.26
        and top_semantic_share <= 0.35
        and top_motif_share <= 0.35
        and selected_unique >= 36
        and strict_rows >= 25
        and cost5_rows >= 60
    )
    warnings: list[str] = []
    if selected_unique < 40:
        warnings.append("selected_unique_blueprints_below_40")
    decision = (
        "PASS_A7FF21_EXTERNAL_CONFIRMATION_SELECTOR_READY_FOR_A7FF22_WITH_BLUEPRINT_DIVERSITY_WARNING"
        if pass_ready and warnings
        else "PASS_A7FF21_EXTERNAL_CONFIRMATION_SELECTOR_READY_FOR_A7FF22"
        if pass_ready
        else "HOLD_A7FF21_EXTERNAL_CONFIRMATION_SELECTOR_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-21-EXTERNAL-CONFIRMATION-SELECTOR",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff20_decision": a7ff20.get("decision", ""),
        "candidate_rows": int(len(pool)),
        "candidate_unique_blueprints": int(pool["blueprint_id"].nunique()) if not pool.empty else 0,
        "selected_rows": selected_rows,
        "selected_unique_blueprints": selected_unique,
        "selected_label_families": int(selected["label_family"].nunique()) if not selected.empty else 0,
        "selected_top_label_share": top_label_share,
        "selected_top_semantic_share": top_semantic_share,
        "selected_top_motif_share": top_motif_share,
        "selected_strict_cost10_rows": strict_rows,
        "selected_cost5_or_better_rows": cost5_rows,
        "warnings": warnings,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff22_expansion_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    pool.to_csv(RUNTIME / "a7ff21_external_candidate_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff21_external_confirmation_selected_queue.csv", index=False)
    candidate_label.to_csv(RUNTIME / "a7ff21_candidate_label_cost_tier_summary.csv", index=False)
    selected_label.to_csv(RUNTIME / "a7ff21_selected_label_cost_tier_summary.csv", index=False)
    selected_semantic.to_csv(RUNTIME / "a7ff21_selected_semantic_summary.csv", index=False)
    selected_motif.to_csv(RUNTIME / "a7ff21_selected_motif_summary.csv", index=False)
    write_json(RUNTIME / "a7ff21_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-21 EXTERNAL CONFIRMATION SELECTOR

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-21 applies the external label-balanced selector to the A7FF-19 confirmation numeric surface. It is a selector repair/confirmation stage, not generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Candidate Label / Cost Tier Summary

{md_table(candidate_label, 80)}

## Selected Label / Cost Tier Summary

{md_table(selected_label, 80)}

## Selected Semantic Summary

{md_table(selected_semantic, 40)}

## Selected Motif Summary

{md_table(selected_motif, 40)}

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
