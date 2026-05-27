from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE_TAG = "20260527"
RUNTIME = REPO / "runtime" / "a7ar4_selector_adapter_smoke"
REPORT = REPO / "reports" / f"CRYPTO_A7AR4_SELECTOR_ADAPTER_SMOKE_{DATE_TAG}.md"

A7AR1_CANDIDATES = REPO / "runtime" / "a7ar1_formula_engine_adapter_smoke" / "a7ar1_generated_candidates.csv"
A7AR2_METRICS = REPO / "runtime" / "a7ar2_feature_algebra_parity_smoke" / "a7ar2_candidate_eval_metrics.csv"
A7AR2_CONTROLS = REPO / "runtime" / "a7ar2_feature_algebra_parity_smoke" / "a7ar2_control_eval_audit.csv"
A7AR2_FIELD_CONTRACT = REPO / "runtime" / "a7ar2_feature_algebra_parity_smoke" / "a7ar2_field_contract_audit.csv"
A7AR2_DECISION = REPO / "runtime" / "a7ar2_feature_algebra_parity_smoke" / "a7ar2_decision_record.json"
A7AR3_MEMORY = REPO / "runtime" / "a7ar3_fresh_memory_dedup_smoke" / "a7ar3_memory_records.csv"
A7AR3_DECISION = REPO / "runtime" / "a7ar3_fresh_memory_dedup_smoke" / "a7ar3_decision_record.json"
A7AL0P = REPO / "runtime" / "a7al0p_pretrain_readiness_gate" / "a7al0p_manifest.json"
A7AL0L = REPO / "runtime" / "a7al0l_fixed_delay_stress_abolition" / "a7al0l_manifest.json"
NEGATIVE_PLAN = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_negative_control_plan.json"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"


MIN_ACTIVITY = 0.05
TARGET_SELECTED = 36
MIN_SELECTED_FAMILIES = 5
MIN_SELECTED_SKELETONS = 20
TOP_SKELETON_SHARE_CAP = 0.15
TOP_FIELD_FAMILY_SHARE_CAP = 0.25
TOP_PRODUCTION_KEY_SHARE_CAP = 0.20
TOP_FORMULA_FAMILY_SHARE_CAP = 0.25
MAX_PER_SKELETON = 3
MAX_PER_FORMULA_FAMILY = 6
MAX_PER_FIELD_FAMILY = 8


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return "`<empty>`"
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def field_family_tokens(value: Any) -> list[str]:
    return sorted({part for part in str(value or "").split("|") if part})


def top_field_family_share(rows: pd.DataFrame) -> tuple[str, int, float]:
    if rows.empty:
        return "", 0, 0.0
    tokens: list[str] = []
    for value in rows["field_families"]:
        tokens.extend(field_family_tokens(value))
    if not tokens:
        return "", 0, 0.0
    counts = Counter(tokens)
    top_value, top_count = counts.most_common(1)[0]
    return top_value, int(top_count), float(top_count / len(tokens))


def wrapper_tags(fields: str, field_families: str) -> str:
    text = f"{fields}|{field_families}".lower()
    tags = []
    if "funding" in text:
        tags.append("funding_wrapper_risk")
    if "basis" in text or "premium" in text or "mark_index" in text:
        tags.append("basis_premium_wrapper_risk")
    if "open_interest" in text or "long_short" in text or "position" in text:
        tags.append("oi_positioning_wrapper_risk")
    if "taker" in text:
        tags.append("taker_flow_wrapper_risk")
    return "|".join(tags) if tags else "none"


def load_inputs() -> pd.DataFrame:
    candidates = pd.read_csv(A7AR1_CANDIDATES)
    metrics = pd.read_csv(A7AR2_METRICS)
    memory = pd.read_csv(A7AR3_MEMORY)
    merged = candidates.merge(metrics.drop(columns=["family", "expression"], errors="ignore"), on="candidate_id", how="left")
    merged = merged.merge(
        memory[
            [
                "candidate_id",
                "expression_key",
                "skeleton_key",
                "production_key",
                "operator_signature",
                "horizon_signature",
            ]
        ],
        on="candidate_id",
        how="left",
    )
    return merged


def base_reject_reason(row: pd.Series, expression_key_counts: Counter[str]) -> str:
    if pd.isna(row.get("eval_status")):
        return "not_in_a7ar2_eval_pool"
    if row.get("eval_status") != "pass":
        return "eval_fail"
    if int(row.get("inf_rows_0bar", 0) or 0) > 0 or int(row.get("inf_rows_field_native_lag1", 0) or 0) > 0:
        return "inf_or_nan_fail"
    if float(row.get("active_ratio_0bar", 0.0) or 0.0) < MIN_ACTIVITY:
        return "low_activity_0bar"
    if float(row.get("active_ratio_field_native_lag1", 0.0) or 0.0) < MIN_ACTIVITY:
        return "low_activity_field_native_lag1"
    if not row.get("expression_key") or pd.isna(row.get("expression_key")):
        return "memory_key_missing"
    if expression_key_counts[str(row.get("expression_key"))] > 1:
        return "memory_expression_collision"
    return "eligible_prediversity"


def score_row(row: pd.Series, family_counts: Counter[str], skeleton_counts: Counter[str]) -> float:
    activity = float(row.get("active_ratio_field_native_lag1", 0.0) or 0.0)
    raw_activity = float(row.get("active_ratio_0bar", 0.0) or 0.0)
    family_rarity = 1.0 / max(family_counts[str(row.get("family"))], 1)
    skeleton_rarity = 1.0 / max(skeleton_counts[str(row.get("skeleton_key"))], 1)
    wrapper_penalty = 0.02 * (wrapper_tags(str(row.get("fields")), str(row.get("field_families"))) != "none")
    return round(activity + 0.25 * raw_activity + 2.0 * family_rarity + 2.0 * skeleton_rarity - wrapper_penalty, 8)


def select_candidates(df: pd.DataFrame) -> pd.DataFrame:
    eligible = df[df["reject_reason"] == "eligible_prediversity"].copy()
    if eligible.empty:
        df["selected_for_pre_replay"] = False
        df["selector_reason"] = df["reject_reason"]
        return df

    family_counts = Counter(eligible["family"].astype(str))
    skeleton_counts = Counter(eligible["skeleton_key"].astype(str))
    eligible["selection_score"] = eligible.apply(lambda row: score_row(row, family_counts, skeleton_counts), axis=1)
    eligible = eligible.sort_values(["selection_score", "candidate_id"], ascending=[False, True])

    selected: set[str] = set()
    selected_skeletons: Counter[str] = Counter()
    selected_families: Counter[str] = Counter()
    selected_field_families: Counter[str] = Counter()

    # First pass: one per available skeleton to maximize structural diversity.
    for _, row in eligible.iterrows():
        candidate_id = str(row["candidate_id"])
        skeleton = str(row["skeleton_key"])
        if selected_skeletons[skeleton] > 0:
            continue
        selected.add(candidate_id)
        selected_skeletons[skeleton] += 1
        selected_families[str(row["family"])] += 1
        for ff in field_family_tokens(row.get("field_families")):
            selected_field_families[ff] += 1

    # Second pass: fill while respecting simple family/skeleton caps.
    for _, row in eligible.iterrows():
        if len(selected) >= TARGET_SELECTED:
            break
        candidate_id = str(row["candidate_id"])
        if candidate_id in selected:
            continue
        skeleton = str(row["skeleton_key"])
        family = str(row["family"])
        ffs = field_family_tokens(row.get("field_families"))
        if selected_skeletons[skeleton] >= MAX_PER_SKELETON:
            continue
        if selected_families[family] >= MAX_PER_FORMULA_FAMILY:
            continue
        if any(selected_field_families[ff] >= MAX_PER_FIELD_FAMILY for ff in ffs):
            continue
        selected.add(candidate_id)
        selected_skeletons[skeleton] += 1
        selected_families[family] += 1
        for ff in ffs:
            selected_field_families[ff] += 1

    # Final prune: keep the selector itself responsible for field-family caps.
    # The first-pass one-per-skeleton fill can otherwise create a near-threshold
    # token concentration even when structural diversity is healthy.
    while True:
        selected_rows = eligible[eligible["candidate_id"].astype(str).isin(selected)].copy()
        top_ff, _, top_share = top_field_family_share(selected_rows)
        if top_share <= TOP_FIELD_FAMILY_SHARE_CAP or len(selected) <= MIN_SELECTED_SKELETONS:
            break
        removable = selected_rows[selected_rows["field_families"].apply(lambda value: top_ff in field_family_tokens(value))].copy()
        if removable.empty:
            break
        removable = removable.sort_values(["selection_score", "candidate_id"], ascending=[True, False])
        removed = False
        for _, candidate in removable.iterrows():
            trial = selected - {str(candidate["candidate_id"])}
            trial_rows = eligible[eligible["candidate_id"].astype(str).isin(trial)]
            if trial_rows["skeleton_key"].nunique() < MIN_SELECTED_SKELETONS:
                continue
            if trial_rows["family"].nunique() < MIN_SELECTED_FAMILIES:
                continue
            selected = trial
            removed = True
            break
        if not removed:
            break

    score_map = dict(zip(eligible["candidate_id"], eligible["selection_score"]))
    df["selection_score"] = df["candidate_id"].map(score_map).fillna(0.0)
    df["selected_for_pre_replay"] = df["candidate_id"].astype(str).isin(selected)
    df["selector_reason"] = df["reject_reason"]
    df.loc[df["selected_for_pre_replay"], "selector_reason"] = "selected_diversity_capped"
    df.loc[(df["reject_reason"] == "eligible_prediversity") & (~df["selected_for_pre_replay"]), "selector_reason"] = "eligible_not_selected_by_caps_or_budget"
    return df


def count_share(values: pd.Series) -> tuple[int, float, str]:
    if values.empty:
        return 0, 0.0, ""
    counts = values.astype(str).value_counts()
    return int(counts.iloc[0]), float(counts.iloc[0] / len(values)), str(counts.index[0])


def build_summary_tables(trace: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    selected = trace[trace["selected_for_pre_replay"]].copy()
    evaled = trace[trace["reject_reason"] != "not_in_a7ar2_eval_pool"].copy()
    tables: dict[str, list[dict[str, Any]]] = {}

    tables["reject_reason_summary"] = [
        {"reason": str(reason), "count": int(count)}
        for reason, count in trace["selector_reason"].value_counts(dropna=False).items()
    ]

    quota_rows = []
    for name, series in [
        ("formula_family", selected["family"] if not selected.empty else pd.Series(dtype=str)),
        ("field_family", selected["field_families"].astype(str).str.split("|").explode() if not selected.empty else pd.Series(dtype=str)),
        ("wrapper_tag", selected["wrapper_tags"].astype(str).str.split("|").explode() if not selected.empty else pd.Series(dtype=str)),
    ]:
        if series.empty:
            quota_rows.append({"quota_type": name, "bucket": "", "selected_count": 0, "selected_share": 0.0})
            continue
        counts = series.value_counts()
        for bucket, count in counts.items():
            quota_rows.append({"quota_type": name, "bucket": str(bucket), "selected_count": int(count), "selected_share": round(float(count / len(selected)), 6)})
    quota_rows.extend(
        [
            {
                "quota_type": "age_listing_latent",
                "bucket": "age_lt30_fixed_quota",
                "selected_count": "",
                "selected_share": "",
                "status": "policy_attached_not_materialized_pre_replay",
            },
            {
                "quota_type": "meme_multiplier",
                "bucket": "meme_multiplier_strata",
                "selected_count": "",
                "selected_share": "",
                "status": "taxonomy_attached; enforced at replay universe stage",
            },
        ]
    )
    tables["quota_summary"] = quota_rows

    family_cap_rows = []
    for cap_name, column, cap in [
        ("top_formula_family_share", "family", TOP_FORMULA_FAMILY_SHARE_CAP),
        ("top_skeleton_share", "skeleton_key", TOP_SKELETON_SHARE_CAP),
        ("top_production_key_share", "production_key", TOP_PRODUCTION_KEY_SHARE_CAP),
    ]:
        top_count, top_share, top_value = count_share(selected[column] if not selected.empty else pd.Series(dtype=str))
        family_cap_rows.append({"cap_name": cap_name, "top_value": top_value, "top_count": top_count, "top_share": round(top_share, 6), "cap": cap, "status": "PASS" if top_share <= cap else "HOLD"})
    if selected.empty:
        ff_series = pd.Series(dtype=str)
    else:
        ff_series = selected["field_families"].astype(str).str.split("|").explode()
    top_count, top_share, top_value = count_share(ff_series)
    family_cap_rows.append({"cap_name": "top_field_family_share", "top_value": top_value, "top_count": top_count, "top_share": round(top_share, 6), "cap": TOP_FIELD_FAMILY_SHARE_CAP, "status": "PASS" if top_share <= TOP_FIELD_FAMILY_SHARE_CAP else "HOLD"})
    tables["family_cap_audit"] = family_cap_rows

    expression_dups = int(trace["expression_key"].dropna().duplicated().sum())
    selected_skeleton_count = int(selected["skeleton_key"].nunique()) if not selected.empty else 0
    tables["memory_dedup_audit"] = [
        {"check": "expression_duplicate_count", "value": expression_dups, "status": "PASS" if expression_dups == 0 else "HOLD"},
        {"check": "evaled_expression_keys", "value": int(evaled["expression_key"].nunique()), "status": "INFO"},
        {"check": "evaled_skeleton_keys", "value": int(evaled["skeleton_key"].nunique()), "status": "INFO"},
        {"check": "selected_skeleton_keys", "value": selected_skeleton_count, "status": "PASS" if selected_skeleton_count >= MIN_SELECTED_SKELETONS else "HOLD"},
    ]
    return tables


def latency_policy_audit() -> list[dict[str, Any]]:
    a7al0l = read_json(A7AL0L)
    fields = pd.read_csv(A7AR2_FIELD_CONTRACT)
    return [
        {
            "check": "fixed_delay_stress_abolished",
            "status": "PASS" if a7al0l.get("decision") == "PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED" else "HOLD",
            "detail": a7al0l.get("decision"),
        },
        {
            "check": "field_contract_all_present",
            "status": "PASS" if bool(fields["in_contract"].all()) else "HOLD",
            "detail": f"fields={len(fields)} missing={int((~fields['in_contract'].astype(bool)).sum())}",
        },
        {
            "check": "same_bar_forbidden",
            "status": "PASS" if not fields["same_bar_execution_allowed"].astype(bool).any() else "HOLD",
            "detail": "same_bar_execution_allowed must be false",
        },
        {
            "check": "fixed_delay_not_required",
            "status": "PASS" if "fixed_delay_stress_required" in fields.columns and not fields["fixed_delay_stress_required"].astype(bool).any() else "HOLD",
            "detail": "field-native latency audit is required instead",
        },
    ]


def negative_control_readiness() -> list[dict[str, Any]]:
    plan = read_json(NEGATIVE_PLAN)
    controls = pd.read_csv(A7AR2_CONTROLS)
    rows = [
        {
            "check": "negative_control_plan_attached",
            "status": "PASS" if bool(plan.get("controls")) else "HOLD",
            "detail": f"plan_controls={len(plan.get('controls', []))}",
        },
        {
            "check": "a7ar2_control_eval_success",
            "status": "PASS" if (controls["eval_status"] == "pass").all() else "HOLD",
            "detail": f"rows={len(controls)} failures={int((controls['eval_status'] != 'pass').sum())}",
        },
    ]
    for control, part in controls.groupby("control"):
        rows.append(
            {
                "check": f"control_available_{control}",
                "status": "PASS",
                "detail": f"rows={len(part)} active_ratio_median={round(float(part['active_ratio'].median()), 6)}",
            }
        )
    return rows


def skeleton_diversity_audit(trace: pd.DataFrame) -> list[dict[str, Any]]:
    selected = trace[trace["selected_for_pre_replay"]]
    evaled = trace[trace["reject_reason"] != "not_in_a7ar2_eval_pool"]
    eligible = trace[trace["reject_reason"] == "eligible_prediversity"]
    top_count, top_share, top_value = count_share(selected["skeleton_key"] if not selected.empty else pd.Series(dtype=str))
    return [
        {"scope": "all_generated", "candidates": int(len(trace)), "skeleton_count": int(trace["skeleton_key"].nunique()), "top_skeleton": str(trace["skeleton_key"].value_counts().index[0]) if trace["skeleton_key"].notna().any() else "", "top_skeleton_share": round(float(trace["skeleton_key"].value_counts(normalize=True).iloc[0]), 6) if trace["skeleton_key"].notna().any() else 0.0},
        {"scope": "a7ar2_evaled", "candidates": int(len(evaled)), "skeleton_count": int(evaled["skeleton_key"].nunique()), "top_skeleton": str(evaled["skeleton_key"].value_counts().index[0]) if not evaled.empty else "", "top_skeleton_share": round(float(evaled["skeleton_key"].value_counts(normalize=True).iloc[0]), 6) if not evaled.empty else 0.0},
        {"scope": "eligible_prediversity", "candidates": int(len(eligible)), "skeleton_count": int(eligible["skeleton_key"].nunique()), "top_skeleton": str(eligible["skeleton_key"].value_counts().index[0]) if not eligible.empty else "", "top_skeleton_share": round(float(eligible["skeleton_key"].value_counts(normalize=True).iloc[0]), 6) if not eligible.empty else 0.0},
        {"scope": "selected", "candidates": int(len(selected)), "skeleton_count": int(selected["skeleton_key"].nunique()), "top_skeleton": top_value, "top_skeleton_share": round(top_share, 6), "required_skeleton_count": MIN_SELECTED_SKELETONS, "status": "PASS" if int(selected["skeleton_key"].nunique()) >= MIN_SELECTED_SKELETONS and top_share <= TOP_SKELETON_SHARE_CAP else "HOLD"},
    ]


def decide(trace: pd.DataFrame, tables: dict[str, list[dict[str, Any]]], latency_rows: list[dict[str, Any]], control_rows: list[dict[str, Any]]) -> tuple[str, list[str]]:
    selected = trace[trace["selected_for_pre_replay"]]
    blockers: list[str] = []
    a7ar2 = read_json(A7AR2_DECISION)
    a7ar3 = read_json(A7AR3_DECISION)
    a7al0p = read_json(A7AL0P)
    a7al0l = read_json(A7AL0L)

    if a7al0p.get("decision") != "PASS_A7AL0P_PRETRAIN_READY_FOR_A7AL1_FIELD_FAMILY_BASELINE":
        blockers.append("a7al0p_not_passed")
    if a7al0l.get("decision") != "PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED":
        blockers.append("a7al0l_fixed_delay_policy_not_passed")
    if a7ar2.get("decision") != "PASS_A7AR2_FEATURE_ALGEBRA_PARITY_SMOKE":
        blockers.append("a7ar2_not_passed")
    if a7ar3.get("decision") != "PASS_A7AR3_FRESH_MEMORY_DEDUP_SMOKE":
        blockers.append("a7ar3_not_passed")
    if selected.empty:
        blockers.append("selected_candidates_zero")
    if selected["family"].nunique() < MIN_SELECTED_FAMILIES:
        blockers.append("selected_family_count_below_min")
    if selected["skeleton_key"].nunique() < MIN_SELECTED_SKELETONS:
        blockers.append("selected_skeleton_count_below_20")
    for row in tables["family_cap_audit"]:
        if row["status"] != "PASS":
            blockers.append(row["cap_name"] + "_fail")
    if any(row["status"] == "HOLD" for row in latency_rows):
        blockers.append("latency_policy_fail")
    if any(row["status"] == "HOLD" for row in control_rows):
        blockers.append("negative_control_unready")
    if any(row["status"] == "HOLD" for row in tables["memory_dedup_audit"] if row["check"] == "expression_duplicate_count"):
        blockers.append("memory_expression_collision")

    if not blockers:
        return "PASS_A7AR4_SELECTOR_ADAPTER_SMOKE", []
    if any(b == "latency_policy_fail" or b == "field_contract_fail" for b in blockers):
        return "HOLD_A7AR4_LATENCY_OR_FIELD_CONTRACT_FAIL", blockers
    if any("memory" in b for b in blockers):
        return "HOLD_A7AR4_MEMORY_COLLISION", blockers
    if any("negative" in b for b in blockers):
        return "HOLD_A7AR4_NEGATIVE_CONTROL_UNREADY", blockers
    if any("skeleton" in b or "share" in b or "family_count" in b for b in blockers):
        return "HOLD_A7AR4_SELECTOR_DIVERSITY_WEAK", blockers
    return "HOLD_A7AR4_SELECTOR_ADAPTER_SMOKE", blockers


def write_authorization_matrix(decision: str, blockers: list[str]) -> dict[str, Any]:
    return {
        "decision": decision,
        "blockers": blockers,
        "authorized": {
            "a7al1_field_family_baseline": True,
            "a7al2_small_formula_search_contract_drafting": decision == "PASS_A7AR4_SELECTOR_ADAPTER_SMOKE",
        },
        "not_authorized": {
            "formula_search_execution": True,
            "alpha_proof": True,
            "shadow": True,
            "paper": True,
            "live": True,
        },
        "note": "A7AR-4 selector smoke does not replace A7AL-1 field-family baseline.",
    }


def make_report(manifest: dict[str, Any], tables: dict[str, list[dict[str, Any]]], latency_rows: list[dict[str, Any]], control_rows: list[dict[str, Any]], skeleton_rows: list[dict[str, Any]]) -> str:
    return f"""# CRYPTO A7AR-4 Selector Adapter Smoke

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

## Summary

```json
{json.dumps(manifest, indent=2)}
```

## Skeleton Diversity

{md_table(skeleton_rows)}

## Family Cap Audit

{md_table(tables["family_cap_audit"])}

## Reject Reasons

{md_table(tables["reject_reason_summary"])}

## Latency Policy

{md_table(latency_rows)}

## Negative Control Readiness

{md_table(control_rows)}

## Boundary

```text
AUTHORIZED:
  A7AL-1 field-family neutralized baseline remains allowed.

CONDITIONAL:
  A7AL-2 small formula search contract drafting only if A7AR-4 PASS.

NOT AUTHORIZED:
  formula search execution
  alpha proof
  shadow / paper / live
```
"""


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    trace = load_inputs()
    expression_counts = Counter(trace["expression_key"].dropna().astype(str))
    trace["wrapper_tags"] = trace.apply(lambda row: wrapper_tags(str(row.get("fields")), str(row.get("field_families"))), axis=1)
    trace["reject_reason"] = trace.apply(lambda row: base_reject_reason(row, expression_counts), axis=1)
    trace = select_candidates(trace)

    tables = build_summary_tables(trace)
    latency_rows = latency_policy_audit()
    control_rows = negative_control_readiness()
    skeleton_rows = skeleton_diversity_audit(trace)
    decision, blockers = decide(trace, tables, latency_rows, control_rows)

    selected = trace[trace["selected_for_pre_replay"]]
    manifest = {
        "generated_at": generated_at,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "generated_candidates": int(len(trace)),
        "a7ar2_evaled_candidates": int((trace["reject_reason"] != "not_in_a7ar2_eval_pool").sum()),
        "eligible_prediversity_candidates": int((trace["reject_reason"] == "eligible_prediversity").sum()),
        "selected_candidates": int(len(selected)),
        "selected_family_count": int(selected["family"].nunique()) if not selected.empty else 0,
        "selected_skeleton_count": int(selected["skeleton_key"].nunique()) if not selected.empty else 0,
        "selected_production_key_count": int(selected["production_key"].nunique()) if not selected.empty else 0,
        "minimum_selected_skeleton_count": MIN_SELECTED_SKELETONS,
        "blockers": blockers,
        "a7al1_field_family_baseline_not_blocked_by_a7ar4": True,
        "authorizes_a7al2_small_formula_search_contract_drafting": decision == "PASS_A7AR4_SELECTOR_ADAPTER_SMOKE",
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "warnings": [
            "A7AR-4 is pre-replay selector plumbing only",
            "A7AR-2 evaluated only 96 generated candidates; non-evaluated candidates are rejected for this smoke",
            "Current generator skeleton diversity is expected to be the binding constraint if selected_skeleton_count < 20",
        ],
    }

    trace_cols = [
        "candidate_id",
        "selected_for_pre_replay",
        "selector_reason",
        "reject_reason",
        "selection_score",
        "family",
        "field_families",
        "fields",
        "operators",
        "windows",
        "wrapper_tags",
        "expression",
        "eval_status",
        "active_ratio_0bar",
        "active_ratio_field_native_lag1",
        "inf_rows_0bar",
        "inf_rows_field_native_lag1",
        "expression_key",
        "skeleton_key",
        "production_key",
        "operator_signature",
        "horizon_signature",
    ]
    write_csv(RUNTIME / "a7ar4_selection_trace.csv", trace[trace_cols].fillna("").to_dict("records"))
    for name, rows in tables.items():
        write_csv(RUNTIME / f"a7ar4_{name}.csv", rows)
    write_csv(RUNTIME / "a7ar4_latency_policy_audit.csv", latency_rows)
    write_csv(RUNTIME / "a7ar4_negative_control_readiness.csv", control_rows)
    write_csv(RUNTIME / "a7ar4_skeleton_diversity_audit.csv", skeleton_rows)
    authorization = write_authorization_matrix(decision, blockers)
    (RUNTIME / "a7ar4_authorization_matrix.json").write_text(json.dumps(authorization, indent=2), encoding="utf-8")
    (RUNTIME / "a7ar4_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    REPORT.write_text(make_report(manifest, tables, latency_rows, control_rows, skeleton_rows), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
