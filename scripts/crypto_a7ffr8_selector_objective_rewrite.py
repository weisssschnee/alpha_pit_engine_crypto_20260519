from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffr8_selector_objective_rewrite"
REPORT = REPO / "reports" / "CRYPTO_A7FFR8_SELECTOR_OBJECTIVE_REWRITE_20260531.md"

A7FF42_MANIFEST = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_manifest.json"
A7FF42_STRICT = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_control_strict_non_l7_clues.csv"
A7FF42_SELECTED = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_selected_forensic.csv"
A7FF42_QUEUE = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_family_balanced_queue.csv"


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


def num(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([float("nan")] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def add_scores(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["control_ratio_premay_max"] = num(out, "control_ratio_premay_max")
    out["label_horizon_h"] = num(out, "label_horizon_h")
    out["response_proxy_score"] = (
        num(out, "validation_2025H1_tstat").abs().fillna(0.0)
        + num(out, "test_2025H2_tstat").abs().fillna(0.0)
        + num(out, "recent_oos_2026JanApr_tstat").abs().fillna(0.0)
    )
    out["cost10_recent_oriented"] = num(out, "cost10_recent_oriented")
    out["cost5_recent_oriented"] = num(out, "cost5_recent_oriented")
    out["cost2_recent_oriented"] = num(out, "cost2_recent_oriented")
    out["robust_median_tstat_floor"] = num(out, "robust_median_tstat_floor")
    out["robust_min_tstat_floor"] = num(out, "robust_min_tstat_floor")
    out["selector_risk_penalty"] = 2.0 * out["control_ratio_premay_max"].fillna(1.0)
    out["cost10_bonus"] = out["cost10_recent_oriented"].clip(lower=0).fillna(0.0) * 10.0
    out["robust_bonus"] = out["robust_median_tstat_floor"].abs().fillna(0.0)
    out["current_like_score"] = out["response_proxy_score"] + out["cost10_bonus"] + out["robust_bonus"] - out["selector_risk_penalty"]
    out["control_first_score"] = -out["control_ratio_premay_max"].fillna(1.0) + 0.05 * out["response_proxy_score"]
    out["family_retention_score"] = out["response_proxy_score"] - out["selector_risk_penalty"] + 0.25 * out["robust_bonus"]
    return out


def unique_take(frame: pd.DataFrame, n: int, score_col: str) -> pd.DataFrame:
    if frame.empty or n <= 0:
        return frame.head(0).copy()
    out = []
    used_skeletons: set[str] = set()
    sorted_frame = frame.sort_values(score_col, ascending=False).copy()
    for _, row in sorted_frame.iterrows():
        skel = str(row.get("skeleton_key", ""))
        if skel and skel in used_skeletons:
            continue
        out.append(row)
        if skel:
            used_skeletons.add(skel)
        if len(out) >= n:
            break
    if len(out) < n:
        used_ids = {str(r["blueprint_id"]) for r in out}
        for _, row in sorted_frame.iterrows():
            if str(row["blueprint_id"]) in used_ids:
                continue
            out.append(row)
            if len(out) >= n:
                break
    return pd.DataFrame(out).head(n).copy()


def select_family_balanced(strict: pd.DataFrame, n: int, score_col: str, min_per_family: int = 2) -> pd.DataFrame:
    families = strict["semantic_pair"].dropna().astype(str).unique().tolist()
    pieces = []
    for family in families:
        take = unique_take(strict[strict["semantic_pair"].astype(str).eq(family)], min_per_family, score_col)
        if not take.empty:
            pieces.append(take)
    selected = pd.concat(pieces, ignore_index=True) if pieces else strict.head(0).copy()
    if len(selected) < n:
        used = set(selected["blueprint_id"].astype(str))
        extra = unique_take(strict[~strict["blueprint_id"].astype(str).isin(used)], n - len(selected), score_col)
        selected = pd.concat([selected, extra], ignore_index=True)
    return selected.drop_duplicates("blueprint_id").head(n).copy()


def select_label_balanced(strict: pd.DataFrame, n: int, score_col: str) -> pd.DataFrame:
    labels = strict["label_family"].dropna().astype(str).unique().tolist()
    per_label = max(1, n // max(1, len(labels)))
    pieces = []
    for label in labels:
        pieces.append(unique_take(strict[strict["label_family"].astype(str).eq(label)], per_label, score_col))
    selected = pd.concat(pieces, ignore_index=True) if pieces else strict.head(0).copy()
    if len(selected) < n:
        used = set(selected["blueprint_id"].astype(str))
        selected = pd.concat([selected, unique_take(strict[~strict["blueprint_id"].astype(str).isin(used)], n - len(selected), score_col)], ignore_index=True)
    return selected.drop_duplicates("blueprint_id").head(n).copy()


def select_marginal_diversity(strict: pd.DataFrame, n: int) -> pd.DataFrame:
    selected_rows = []
    used_families: set[str] = set()
    used_motifs: set[str] = set()
    used_skeletons: set[str] = set()
    pool = strict.sort_values("family_retention_score", ascending=False).copy()
    while len(selected_rows) < n and not pool.empty:
        best_idx = None
        best_score = None
        for idx, row in pool.iterrows():
            fam = str(row.get("semantic_pair", ""))
            motif = str(row.get("motif", ""))
            skel = str(row.get("skeleton_key", ""))
            diversity_bonus = 0.0
            if fam not in used_families:
                diversity_bonus += 4.0
            if motif not in used_motifs:
                diversity_bonus += 1.5
            if skel not in used_skeletons:
                diversity_bonus += 1.0
            score = float(row.get("family_retention_score", 0.0)) + diversity_bonus
            if best_score is None or score > best_score:
                best_score = score
                best_idx = idx
        if best_idx is None:
            break
        row = pool.loc[best_idx]
        selected_rows.append(row)
        used_families.add(str(row.get("semantic_pair", "")))
        used_motifs.add(str(row.get("motif", "")))
        used_skeletons.add(str(row.get("skeleton_key", "")))
        pool = pool.drop(index=best_idx)
    return pd.DataFrame(selected_rows).head(n).copy()


def summarize_selection(name: str, selected: pd.DataFrame) -> dict[str, Any]:
    if selected.empty:
        return {
            "selector": name,
            "selected_count": 0,
            "selected_clean_family_count": 0,
            "top_family_share": 0.0,
            "median_control_ratio": None,
            "max_control_ratio": None,
            "non_l7_count": 0,
            "cost10_positive_count": 0,
            "label_count": 0,
            "motif_count": 0,
            "skeleton_count": 0,
        }
    family_counts = selected["semantic_pair"].value_counts()
    return {
        "selector": name,
        "selected_count": int(len(selected)),
        "selected_clean_family_count": int(selected["semantic_pair"].nunique()),
        "top_family_share": float(family_counts.iloc[0] / len(selected)),
        "median_control_ratio": float(selected["control_ratio_premay_max"].median()),
        "max_control_ratio": float(selected["control_ratio_premay_max"].max()),
        "non_l7_count": int((~selected["label_family"].astype(str).eq("L7_ranked_future_return")).sum()),
        "cost10_positive_count": int((selected["cost10_recent_oriented"].fillna(-1) > 0).sum()),
        "label_count": int(selected["label_family"].nunique()),
        "motif_count": int(selected["motif"].nunique()),
        "skeleton_count": int(selected["skeleton_key"].nunique()) if "skeleton_key" in selected.columns else 0,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f42 = read_json(A7FF42_MANIFEST)
    if f42.get("decision") != "HOLD_A7FF42_FAMILY_BALANCED_NUMERIC_SELECTED_TOO_THIN":
        raise SystemExit(f"A7FF-42 state not expected for R8: {f42.get('decision')}")

    strict = add_scores(read_csv(A7FF42_STRICT))
    selected_current = add_scores(read_csv(A7FF42_SELECTED))
    queue = read_csv(A7FF42_QUEUE)
    if strict.empty:
        raise SystemExit("A7FF-42 strict clue pool is empty")

    current_strict = selected_current[selected_current.get("a7ff42_role", pd.Series(dtype=str)).astype(str).eq("selected_control_strict_non_l7")].copy()

    family_attr = (
        strict.groupby("semantic_pair", dropna=False)
        .agg(
            strict_clue_rows=("blueprint_id", "count"),
            strict_blueprints=("blueprint_id", "nunique"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_response_proxy=("response_proxy_score", "median"),
            max_response_proxy=("response_proxy_score", "max"),
            median_current_like_score=("current_like_score", "median"),
            max_current_like_score=("current_like_score", "max"),
            median_cost10=("cost10_recent_oriented", "median"),
            cost10_positive_share=("cost10_recent_oriented", lambda s: float((pd.to_numeric(s, errors="coerce") > 0).mean())),
        )
        .reset_index()
    )
    selected_attr = (
        current_strict.groupby("semantic_pair", dropna=False)
        .agg(current_selected_rows=("blueprint_id", "count"), current_selected_blueprints=("blueprint_id", "nunique"))
        .reset_index()
    )
    family_attr = family_attr.merge(selected_attr, on="semantic_pair", how="left")
    family_attr[["current_selected_rows", "current_selected_blueprints"]] = family_attr[["current_selected_rows", "current_selected_blueprints"]].fillna(0).astype(int)
    family_attr["selected_share_of_blueprints"] = family_attr["current_selected_blueprints"] / family_attr["strict_blueprints"].clip(lower=1)
    family_attr["suppression_reason"] = "not_suppressed"
    family_attr.loc[(family_attr["strict_blueprints"].ge(4)) & family_attr["current_selected_blueprints"].eq(0), "suppression_reason"] = "selector_objective_omitted_available_family"
    family_attr.loc[family_attr["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "suppression_reason"] = "reference_family_capped_or_over_penalized"
    family_attr = family_attr.sort_values(["current_selected_blueprints", "strict_blueprints"], ascending=[True, False])
    family_attr.to_csv(RUNTIME / "a7ffr8a_score_component_by_family.csv", index=False)

    queue_family = (
        queue.groupby(["a7ff42_queue_role", "semantic_pair"], dropna=False)
        .agg(queue_rows=("blueprint_id", "count"), queue_motifs=("motif", "nunique"), queue_skeletons=("skeleton_key", "nunique"))
        .reset_index()
    )
    queue_family.to_csv(RUNTIME / "a7ffr8a_input_queue_by_family.csv", index=False)

    selector_outputs: dict[str, pd.DataFrame] = {
        "S0_current_selector_strict_subset": current_strict,
        "S1_label_balanced": select_label_balanced(strict, 12, "family_retention_score"),
        "S2_family_balanced": select_family_balanced(strict, 12, "family_retention_score", min_per_family=3),
        "S3_family_balanced_cost_tiered": select_family_balanced(strict[strict["cost10_recent_oriented"].fillna(-1) > 0], 12, "family_retention_score", min_per_family=2),
        "S4_marginal_diversity": select_marginal_diversity(strict, 12),
        "S5_equal_family_topk": select_family_balanced(strict, 12, "response_proxy_score", min_per_family=4),
        "S6_control_ratio_first": select_family_balanced(strict.sort_values("control_ratio_premay_max"), 12, "control_first_score", min_per_family=3),
    }

    ablation_rows = []
    selected_dist_rows = []
    repaired_candidates = []
    for name, sel in selector_outputs.items():
        sel = sel.copy()
        sel["selector"] = name
        ablation_rows.append(summarize_selection(name, sel))
        if not sel.empty:
            dist = sel.groupby(["selector", "semantic_pair"], dropna=False).size().reset_index(name="selected_rows")
            selected_dist_rows.append(dist)
        if name in {"S2_family_balanced", "S4_marginal_diversity", "S6_control_ratio_first"}:
            repaired_candidates.append(sel)
        sel.to_csv(RUNTIME / f"a7ffr8b_{name}.csv", index=False)

    ablation = pd.DataFrame(ablation_rows).sort_values(["selected_clean_family_count", "selected_count"], ascending=[False, False])
    ablation.to_csv(RUNTIME / "a7ffr8b_selector_ablation_summary.csv", index=False)
    selected_dist = pd.concat(selected_dist_rows, ignore_index=True) if selected_dist_rows else pd.DataFrame()
    selected_dist.to_csv(RUNTIME / "a7ffr8b_selected_family_distribution.csv", index=False)

    repaired_pool = pd.concat(repaired_candidates, ignore_index=True).drop_duplicates("blueprint_id") if repaired_candidates else strict.head(0).copy()
    repaired_pool = add_scores(repaired_pool)
    repaired = select_marginal_diversity(repaired_pool, 12)
    # Enforce a final family-retention pass.
    if repaired["semantic_pair"].nunique() < 3:
        repaired = select_family_balanced(repaired_pool, 12, "family_retention_score", min_per_family=3)
    repaired["a7ffr8c_role"] = "repaired_selector_dry_selected"
    repaired.to_csv(RUNTIME / "a7ffr8c_repaired_selected_queue.csv", index=False)

    retention = (
        repaired.groupby("semantic_pair", dropna=False)
        .agg(
            selected_rows=("blueprint_id", "count"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            median_family_retention_score=("family_retention_score", "median"),
        )
        .reset_index()
        .sort_values("selected_rows", ascending=False)
    )
    retention.to_csv(RUNTIME / "a7ffr8c_family_retention_audit.csv", index=False)

    selector_policy = {
        "hard_gates": {
            "non_l7_only": True,
            "primary_control_ratio_lt": 0.80,
            "absolute_control_ratio_lt": 1.00,
            "materialized_required": True,
            "may_usage_allowed": False,
        },
        "quota": {
            "min_selected_count": 6,
            "min_clean_family_count": 2,
            "preferred_clean_family_count": 3,
            "max_single_family_share": 0.50,
            "funding_basis_family_cap": 0.50,
        },
        "objective": {
            "use_standalone_score_only": False,
            "use_family_retention_score": True,
            "use_marginal_diversity_bonus": True,
            "use_control_ratio_penalty": True,
            "use_cost10_as_secondary_not_primary": True,
        },
        "authorization": {
            "authorizes_numeric_confirmation": True,
            "authorizes_search": False,
            "authorizes_alpha_proof": False,
        },
    }
    write_json(RUNTIME / "a7ffr8c_selector_repair_policy.json", selector_policy)

    repaired_count = int(len(repaired))
    repaired_family_count = int(repaired["semantic_pair"].nunique()) if not repaired.empty else 0
    repaired_top_share = float(repaired["semantic_pair"].value_counts().iloc[0] / len(repaired)) if not repaired.empty else 0.0
    repaired_max_control = float(repaired["control_ratio_premay_max"].max()) if not repaired.empty else None
    repaired_median_control = float(repaired["control_ratio_premay_max"].median()) if not repaired.empty else None
    blockers: list[str] = []
    warnings: list[str] = []
    if repaired_count < 6:
        blockers.append("repaired_selected_count_below_6")
    if repaired_family_count < 2:
        blockers.append("repaired_clean_family_count_below_2")
    if repaired_max_control is not None and repaired_max_control >= 1.0:
        blockers.append("repaired_control_ratio_max_ge_1")
    if repaired_median_control is not None and repaired_median_control >= 0.8:
        blockers.append("repaired_control_ratio_median_ge_0p8")
    if repaired_top_share > 0.50:
        warnings.append("repaired_top_family_share_above_0p50")
    if repaired_family_count >= 3:
        warnings.append("repaired_selector_retains_3_families_dry_only")

    decision = (
        "PASS_A7FFR8_SELECTOR_REPAIR_READY_FOR_A7FF43_NUMERIC_CONFIRMATION_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FFR8_SELECTOR_REPAIR_POLICY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-R8",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff42_decision": f42.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "strict_input_rows": int(len(strict)),
        "strict_input_family_count": int(strict["semantic_pair"].nunique()),
        "current_selected_strict_rows": int(len(current_strict)),
        "current_selected_strict_family_count": int(current_strict["semantic_pair"].nunique()) if not current_strict.empty else 0,
        "repaired_selected_count": repaired_count,
        "repaired_selected_family_count": repaired_family_count,
        "repaired_top_family_share": repaired_top_share,
        "repaired_control_ratio_max": repaired_max_control,
        "repaired_control_ratio_median": repaired_median_control,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff43_numeric_confirmation": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffr8_manifest.json", manifest)
    write_json(RUNTIME / "a7ffr8_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-R8 SELECTOR OBJECTIVE REWRITE

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-R8 diagnoses why A7FF-42 has a 3-family control-strict non-L7 clue surface but a single-family selected queue. It performs selector attribution, portfolio proxy ablation, and a dry family-retention selector repair. No numeric probe or search is executed.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## R8A Selector Objective Attribution

{md_table(family_attr)}

## R8B Selector Ablation Summary

{md_table(ablation)}

## R8B Selected Family Distribution

{md_table(selected_dist)}

## R8C Repaired Selected Queue

{md_table(repaired)}

## R8C Family Retention Audit

{md_table(retention)}

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
