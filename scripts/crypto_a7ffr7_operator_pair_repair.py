from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffr7_operator_pair_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FFR7_OPERATOR_PAIR_REPAIR_20260530.md"

A7FF40_MANIFEST = REPO / "runtime" / "a7ff40_control_strict_followup" / "a7ff40_manifest.json"
A7FF40_STRICT = REPO / "runtime" / "a7ff40_control_strict_followup" / "a7ff40_control_strict_numeric_clues.csv"
A7FF40_SELECTED = REPO / "runtime" / "a7ff40_control_strict_followup" / "a7ff40_selected_forensic.csv"
A7FF40_SEED_POLICY = REPO / "runtime" / "a7ff40_control_strict_followup" / "a7ff40_seed_pattern_policy.csv"
A7FF40_QUEUE = REPO / "runtime" / "a7ff40_control_strict_followup" / "a7ff40_control_strict_followup_queue.csv"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"


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


def add_response_score(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["control_ratio_premay_max"] = num(out, "control_ratio_premay_max")
    out["response_proxy_score"] = (
        num(out, "recent_oos_2026JanApr_tstat").abs().fillna(0.0)
        + num(out, "validation_2025H1_tstat").abs().fillna(0.0)
        + num(out, "test_2025H2_tstat").abs().fillna(0.0)
    )
    out["robust_floor_abs"] = num(out, "robust_min_tstat_floor").abs().fillna(0.0)
    out["repair_score"] = (
        out["response_proxy_score"].fillna(0.0)
        + 0.5 * num(out, "robust_median_tstat_floor").abs().fillna(0.0)
        - 2.0 * out["control_ratio_premay_max"].fillna(1.0)
    )
    return out


def family_suppression(strict: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    strict = add_response_score(strict)
    selected = selected.copy()
    selected["control_ratio_premay_max"] = num(selected, "control_ratio_premay_max")
    selected["is_control_strict_non_l7_selected"] = (
        selected.get("a7ff40_forensic_role", pd.Series(dtype=str)).astype(str).eq("control_strict_non_l7_selected")
    )

    strict_family = (
        strict.groupby("semantic_pair", dropna=False)
        .agg(
            strict_clue_rows=("blueprint_id", "count"),
            strict_blueprints=("blueprint_id", "nunique"),
            strict_motifs=("motif", "nunique"),
            strict_labels=("label_family", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_repair_score=("repair_score", "max"),
            median_repair_score=("repair_score", "median"),
        )
        .reset_index()
    )
    selected_family = (
        selected[selected["is_control_strict_non_l7_selected"]]
        .groupby("semantic_pair", dropna=False)
        .agg(
            selected_strict_rows=("blueprint_id", "count"),
            selected_strict_blueprints=("blueprint_id", "nunique"),
            selected_strict_motifs=("motif", "nunique"),
            selected_min_control_ratio=("control_ratio_premay_max", "min"),
        )
        .reset_index()
    )
    out = strict_family.merge(selected_family, on="semantic_pair", how="left")
    for col in ["selected_strict_rows", "selected_strict_blueprints", "selected_strict_motifs"]:
        out[col] = out[col].fillna(0).astype(int)
    out["selected_share_of_strict_blueprints"] = out["selected_strict_blueprints"] / out["strict_blueprints"].clip(lower=1)
    out["suppression_reason"] = "not_suppressed"
    out.loc[(out["strict_blueprints"].ge(2)) & out["selected_strict_blueprints"].eq(0), "suppression_reason"] = "strict_clues_exist_but_selector_omitted_family"
    out.loc[out["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "suppression_reason"] = "reference_family_should_be_capped_not_promoted"
    out.loc[out["semantic_pair"].eq("regime_state|price_return_like") & out["selected_strict_blueprints"].eq(0), "suppression_reason"] = "regime_family_needs_family_quota_repair"
    out = out.sort_values(["strict_blueprints", "max_repair_score"], ascending=[False, False])
    return out


def build_repaired_dry_queue(strict: pd.DataFrame) -> pd.DataFrame:
    strict = add_response_score(strict)
    strict = strict.sort_values(["repair_score", "response_proxy_score"], ascending=[False, False])
    quotas = {
        "funding_like|basis_premium_like": 4,
        "regime_state|price_return_like": 4,
        "basis_premium_like|basis_premium_like": 2,
    }
    parts: list[pd.DataFrame] = []
    for semantic_pair, quota in quotas.items():
        family = strict[strict["semantic_pair"].eq(semantic_pair)].copy()
        if family.empty:
            continue
        chosen: list[pd.DataFrame] = []
        used_skeletons: set[str] = set()
        for _, row in family.iterrows():
            skeleton = str(row.get("skeleton_key", ""))
            if skeleton and skeleton in used_skeletons:
                continue
            chosen.append(pd.DataFrame([row]))
            if skeleton:
                used_skeletons.add(skeleton)
            if len(chosen) >= quota:
                break
        if len(chosen) < quota:
            used_ids = {str(x.iloc[0]["blueprint_id"]) for x in chosen} if chosen else set()
            extra = family[~family["blueprint_id"].astype(str).isin(used_ids)].head(quota - len(chosen))
            if not extra.empty:
                chosen.append(extra)
        if chosen:
            out = pd.concat(chosen, ignore_index=True).head(quota)
            out["a7ffr7_repair_role"] = "family_quota_selected"
            if semantic_pair == "basis_premium_like|basis_premium_like":
                out["a7ffr7_repair_role"] = "reference_cap_selected"
            parts.append(out)
    queue = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=strict.columns)
    queue = queue.drop_duplicates("blueprint_id")
    queue["a7ffr7_selected_rank"] = range(1, len(queue) + 1)
    return queue


def operator_pair_policy(strict: pd.DataFrame, suppression: pd.DataFrame, seed_policy: pd.DataFrame) -> pd.DataFrame:
    strict = add_response_score(strict)
    policy = (
        strict.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            strict_clue_rows=("blueprint_id", "count"),
            strict_blueprints=("blueprint_id", "nunique"),
            label_count=("label_family", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_repair_score=("repair_score", "max"),
        )
        .reset_index()
        .sort_values(["semantic_pair", "strict_blueprints", "max_repair_score"], ascending=[True, False, False])
    )
    policy["repaired_role"] = "candidate_pair"
    policy.loc[policy["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "repaired_role"] = "reference_pair_capped"
    policy.loc[policy["semantic_pair"].eq("regime_state|price_return_like"), "repaired_role"] = "selector_quota_required"
    policy["a7ff42_quota_hint"] = 0.0
    policy.loc[policy["semantic_pair"].eq("funding_like|basis_premium_like"), "a7ff42_quota_hint"] = 0.40
    policy.loc[policy["semantic_pair"].eq("regime_state|price_return_like"), "a7ff42_quota_hint"] = 0.35
    policy.loc[policy["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "a7ff42_quota_hint"] = 0.15
    policy["promotion_boundary"] = "numeric_followup_only_no_search"
    policy.loc[policy["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "promotion_boundary"] = "diagnostic_reference_only_until_non_self_pair_confirms"
    return policy


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f40 = read_json(A7FF40_MANIFEST)
    if f40.get("decision") != "HOLD_A7FF40_CONTROL_STRICT_SINGLE_FAMILY_OR_SELECTED_TOO_THIN":
        raise SystemExit(f"A7FF-40 state not expected for R7: {f40.get('decision')}")

    strict = read_csv(A7FF40_STRICT)
    selected = read_csv(A7FF40_SELECTED)
    seed_policy = read_csv(A7FF40_SEED_POLICY)
    queue40 = read_csv(A7FF40_QUEUE)
    company = read_csv(A7FF33_COMPANY)
    if strict.empty:
        raise SystemExit("A7FF-40 strict clue table is empty")

    strict = strict.merge(
        company[["blueprint_id", "skeleton_key", "production_key", "primary_field", "secondary_field", "primary_transform", "secondary_transform"]],
        on="blueprint_id",
        how="left",
        suffixes=("", "_company"),
    )
    suppression = family_suppression(strict, selected)
    repaired_queue = build_repaired_dry_queue(strict)
    policy = operator_pair_policy(strict, suppression, seed_policy)

    suppression.to_csv(RUNTIME / "a7ffr7_family_suppression_audit.csv", index=False)
    repaired_queue.to_csv(RUNTIME / "a7ffr7_repaired_dry_selected_queue.csv", index=False)
    policy.to_csv(RUNTIME / "a7ffr7_operator_pair_policy.csv", index=False)

    queue_contrast = (
        queue40.groupby(["a7ff40_queue_role", "semantic_pair"], dropna=False)
        .agg(queue_count=("blueprint_id", "count"), motif_count=("motif", "nunique"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
        .sort_values("queue_count", ascending=False)
    )
    queue_contrast.to_csv(RUNTIME / "a7ffr7_input_queue_contrast.csv", index=False)

    dry_family_count = int(repaired_queue["semantic_pair"].nunique()) if not repaired_queue.empty else 0
    dry_count = int(len(repaired_queue))
    dry_non_l7_count = int((~repaired_queue["label_family"].astype(str).eq("L7_ranked_future_return")).sum()) if not repaired_queue.empty else 0
    dry_control_strict_count = int((pd.to_numeric(repaired_queue["control_ratio_premay_max"], errors="coerce") < 0.80).sum()) if not repaired_queue.empty else 0
    omitted_families = suppression[suppression["suppression_reason"].astype(str).str.contains("omitted|quota", regex=True)]

    blockers: list[str] = []
    warnings: list[str] = []
    if dry_count < 8:
        blockers.append("repaired_dry_queue_below_8")
    if dry_family_count < 3:
        blockers.append("repaired_dry_queue_family_count_below_3")
    if dry_non_l7_count != dry_count or dry_control_strict_count != dry_count:
        blockers.append("repaired_dry_queue_contains_non_strict_or_l7_rows")
    if not omitted_families.empty:
        warnings.append("a7ff40_selector_omitted_control_strict_families")
    if "basis_premium_like|basis_premium_like" in set(repaired_queue["semantic_pair"].astype(str)):
        warnings.append("basis_reference_present_keep_capped")

    decision = (
        "PASS_A7FFR7_OPERATOR_PAIR_REPAIR_READY_FOR_A7FF42_FAMILY_BALANCED_NUMERIC_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FFR7_OPERATOR_PAIR_REPAIR_DRY_QUEUE_WEAK"
    )
    manifest = {
        "stage": "A7FF-R7",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff40_decision": f40.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "strict_input_rows": int(len(strict)),
        "strict_input_family_count": int(strict["semantic_pair"].nunique()),
        "a7ff40_selected_control_strict_non_l7_count": int(f40.get("selected_control_strict_non_l7_count", 0) or 0),
        "a7ff40_selected_control_strict_non_l7_family_count": int(f40.get("selected_control_strict_non_l7_family_count", 0) or 0),
        "repaired_dry_queue_count": dry_count,
        "repaired_dry_queue_family_count": dry_family_count,
        "repaired_dry_queue_non_l7_count": dry_non_l7_count,
        "repaired_dry_queue_control_strict_count": dry_control_strict_count,
        "suppressed_family_count": int(len(omitted_families)),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff42_family_balanced_numeric": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffr7_manifest.json", manifest)
    write_json(RUNTIME / "a7ffr7_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-R7 OPERATOR-PAIR REPAIR

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-R7 audits why A7FF-40 found 165 control-strict non-L7 clue rows across 3 families, while the selected queue kept only one clean family. It does not run numeric replay or search. It repairs the selector/operator-pair policy as a family-balanced dry queue.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Suppression Audit

{md_table(suppression)}

## Repaired Dry Selected Queue

{md_table(repaired_queue)}

## Operator Pair Policy

{md_table(policy)}

## Input Queue Contrast

{md_table(queue_contrast)}

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
