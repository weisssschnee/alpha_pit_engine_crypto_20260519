from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x2_objective_family_coverage_gap"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X2_OBJECTIVE_FAMILY_COVERAGE_GAP_AUDIT_20260529.md"

GENERATED = ROOT / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_generated_candidates.csv"
REPLAYED = ROOT / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_replayed_candidates.csv"
DECISIONS = ROOT / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_decisions.csv"
SHARED = ROOT / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
X1_TRACE = ROOT / "runtime" / "a7al2x1_dry_rerank" / "a7al2x1_selector_trace.csv"
X_CONTRACT = ROOT / "runtime" / "a7al2x_objective_family_reset" / "a7al2x_allowed_objective_families.csv"


FAMILIES = [
    "F0_OI_delta_price_interaction",
    "F1_OI_basis_premium_interaction",
    "F2_OI_funding_crowding_interaction",
    "F3_positioning_divergence",
    "F4_OI_taker_flow_interaction",
    "F5_OI_upper_regime_interaction",
    "F6_OI_latent_state_interaction",
    "DIRECT_OI_PRICE_WEAK_PRIOR",
    "UNMAPPED_OR_FORBIDDEN",
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def as_bool(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def tokens(row: pd.Series) -> str:
    parts: Iterable[str] = [
        str(row.get("fields", "")),
        str(row.get("field_families", "")),
        str(row.get("family", "")),
        str(row.get("expression", "")),
        str(row.get("operators", "")),
        str(row.get("feature_role", "")),
        str(row.get("pattern_id", "")),
    ]
    return "|".join(parts).lower()


def classify_family(row: pd.Series) -> str:
    text = tokens(row)
    has_oi = "open_interest" in text or "oi_" in text
    has_price = any(x in text for x in ["trade_close", "mark_close", "index_close", "price_move", "price"])
    has_delta = any(x in text for x in ["delta", "change", "move"])
    has_basis = "basis" in text or "premium" in text
    has_funding = "funding" in text
    has_positioning = any(
        x in text
        for x in [
            "positioning",
            "long_short",
            "account_ratio",
            "position_ratio",
            "taker_buy_sell_ratio",
        ]
    )
    has_taker = any(x in text for x in ["taker", "aggressive_flow"])
    has_latent = any(x in text for x in ["latent", "listing_age", "meme", "multiplier", "liquidity_tier"])
    has_regime = any(
        x in text
        for x in [
            "regime",
            "stress_proxy",
            "breadth",
            "liquidity_cycle",
            "leverage_crowding",
            "trade_count",
            "trade_volume",
            "trade_quote_volume",
        ]
    )

    if has_oi and has_price and has_delta:
        return "F0_OI_delta_price_interaction"
    if has_oi and has_basis:
        return "F1_OI_basis_premium_interaction"
    if has_oi and has_funding:
        return "F2_OI_funding_crowding_interaction"
    if has_positioning and not has_oi:
        return "F3_positioning_divergence"
    if has_oi and has_taker:
        return "F4_OI_taker_flow_interaction"
    if has_oi and has_regime:
        return "F5_OI_upper_regime_interaction"
    if has_oi and has_latent:
        return "F6_OI_latent_state_interaction"
    if has_oi and has_price:
        return "DIRECT_OI_PRICE_WEAK_PRIOR"
    return "UNMAPPED_OR_FORBIDDEN"


def overlay_flag(row: pd.Series) -> bool:
    text = tokens(row)
    return "cross_exchange_overlay" in text or "cross_exchange_30d_overlay" in text


def count_unique(df: pd.DataFrame, column: str) -> int:
    if df.empty or column not in df:
        return 0
    return int(df[column].dropna().nunique())


def group_count(df: pd.DataFrame, group_col: str, mask: pd.Series | None = None) -> dict[str, int]:
    if df.empty or group_col not in df:
        return {}
    view = df if mask is None else df[mask]
    return view[group_col].value_counts(dropna=False).astype(int).to_dict()


def family_count(counts: dict[str, int], family: str) -> int:
    return int(counts.get(family, 0))


def gap_stage(row: pd.Series) -> str:
    if row.generated_count == 0:
        return "not_generated"
    if row.historical_generated_count == 0:
        return "generated_only_as_overlay_or_nonhistorical"
    if row.selected_for_a7al2l_count == 0:
        return "not_selected_by_a7al2k_caps"
    if row.a7al2l_replayed_count == 0:
        return "a7al2l_target_replay_mode_excluded"
    if row.shared_pool_count == 0:
        return "not_promoted_to_shared_pool_source_of_truth"
    if row.x1_non_rejected_count == 0:
        return "x1_control_or_contract_rejected"
    return "available_for_x1_selection"


def repair_action(row: pd.Series) -> str:
    stage = row.gap_stage
    if stage == "not_generated":
        return "add_family_to_generator_templates"
    if stage == "generated_only_as_overlay_or_nonhistorical":
        return "replace_overlay_only_fields_with_historical_binance_fields_or_contract_source"
    if stage == "not_selected_by_a7al2k_caps":
        return "add_family_min_quota_before_replay_preflight"
    if stage == "a7al2l_target_replay_mode_excluded":
        return "run_family_balanced_preflight_instead_of_two_target_replay"
    if stage == "not_promoted_to_shared_pool_source_of_truth":
        return "link_family_candidates_into_shared_pool_ledger"
    if stage == "x1_control_or_contract_rejected":
        return "repair_control_dominance_or_keep_as_rejected_family"
    return "none"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    return df.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    generated = read_csv(GENERATED)
    replayed = read_csv(REPLAYED)
    decisions = read_csv(DECISIONS)
    shared = read_csv(SHARED)
    x1 = read_csv(X1_TRACE)
    contract = read_csv(X_CONTRACT)

    for df in [generated, replayed, shared]:
        if not df.empty:
            df["a7al2x2_objective_family"] = df.apply(classify_family, axis=1)
            df["is_overlay_diagnostic"] = df.apply(overlay_flag, axis=1)

    if not x1.empty:
        if "a7al2x_objective_family" in x1.columns:
            x1["a7al2x2_objective_family"] = x1["a7al2x_objective_family"]
        else:
            x1["a7al2x2_objective_family"] = x1.apply(classify_family, axis=1)

    if not replayed.empty and not decisions.empty and "candidate_id" in decisions.columns:
        replayed_decisions = replayed.merge(
            decisions[["candidate_id", "decision"]],
            on="candidate_id",
            how="left",
        )
    else:
        replayed_decisions = replayed.copy()
        if not replayed_decisions.empty:
            replayed_decisions["decision"] = ""

    selected_mask = (
        as_bool(generated.get("selected_for_a7al2l_replay_preflight", pd.Series(dtype=str)))
        if not generated.empty
        else pd.Series(dtype=bool)
    )
    historical_mask = ~generated.get("is_overlay_diagnostic", pd.Series(False, index=generated.index))

    generated_counts = group_count(generated, "a7al2x2_objective_family")
    historical_counts = group_count(generated, "a7al2x2_objective_family", historical_mask)
    selected_counts = group_count(generated, "a7al2x2_objective_family", selected_mask)
    selected_historical_counts = group_count(generated, "a7al2x2_objective_family", selected_mask & historical_mask)
    replayed_counts = group_count(replayed_decisions, "a7al2x2_objective_family")
    clue_counts = group_count(
        replayed_decisions,
        "a7al2x2_objective_family",
        replayed_decisions.get("decision", pd.Series(dtype=str)).astype(str).str.contains("CLUE", na=False)
        if not replayed_decisions.empty
        else pd.Series(dtype=bool),
    )

    shared_counts = group_count(shared, "a7al2x2_objective_family")
    shared_fast_counts = group_count(
        shared,
        "a7al2x2_objective_family",
        as_bool(shared.get("selected_for_fast_replay", pd.Series(dtype=str))) if not shared.empty else pd.Series(dtype=bool),
    )
    x1_non_rejected_counts = group_count(
        x1,
        "a7al2x2_objective_family",
        x1.get("x1_reject_reason", pd.Series(dtype=str)).fillna("").eq("")
        if not x1.empty
        else pd.Series(dtype=bool),
    )
    x1_selected_counts = group_count(
        x1,
        "a7al2x2_objective_family",
        as_bool(x1.get("selected_by_a7al2x1", pd.Series(dtype=str))) if not x1.empty else pd.Series(dtype=bool),
    )

    rows = []
    for family in FAMILIES:
        rows.append(
            {
                "family_id": family,
                "generated_count": family_count(generated_counts, family),
                "historical_generated_count": family_count(historical_counts, family),
                "selected_for_a7al2l_count": family_count(selected_counts, family),
                "selected_historical_for_a7al2l_count": family_count(selected_historical_counts, family),
                "a7al2l_replayed_count": family_count(replayed_counts, family),
                "a7al2l_clue_count": family_count(clue_counts, family),
                "shared_pool_count": family_count(shared_counts, family),
                "shared_fast_replay_count": family_count(shared_fast_counts, family),
                "x1_non_rejected_count": family_count(x1_non_rejected_counts, family),
                "x1_selected_count": family_count(x1_selected_counts, family),
            }
        )

    funnel = pd.DataFrame(rows)
    total_generated = max(1, int(funnel.generated_count.sum()))
    funnel["generated_share"] = funnel["generated_count"] / total_generated
    funnel["gap_stage"] = funnel.apply(gap_stage, axis=1)
    funnel["recommended_repair"] = funnel.apply(repair_action, axis=1)

    contract_family_ids = set(contract.get("family_id", pd.Series(dtype=str)).astype(str).tolist())
    allowed_rows = []
    for family in FAMILIES[:7]:
        r = funnel[funnel.family_id == family].iloc[0].to_dict()
        allowed_rows.append(
            {
                "family_id": family,
                "in_a7al2x_contract": family in contract_family_ids,
                "has_generated_candidates": r["generated_count"] > 0,
                "has_historical_generated_candidates": r["historical_generated_count"] > 0,
                "has_a7al2l_replay": r["a7al2l_replayed_count"] > 0,
                "has_shared_pool_candidates": r["shared_pool_count"] > 0,
                "has_x1_eligible_candidates": r["x1_non_rejected_count"] > 0,
                "primary_gap": r["gap_stage"],
                "required_action": r["recommended_repair"],
            }
        )
    missing = pd.DataFrame(allowed_rows)

    generated_family_coverage = (
        generated.groupby(["a7al2x2_objective_family", "cell", "family", "feature_role"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            selected_for_a7al2l_count=("selected_for_a7al2l_replay_preflight", lambda s: int(as_bool(s).sum())),
            unique_skeleton_count=("skeleton_key", "nunique"),
            unique_production_count=("production_key", "nunique"),
        )
        .reset_index()
        .sort_values(["a7al2x2_objective_family", "candidate_count"], ascending=[True, False])
        if not generated.empty
        else pd.DataFrame()
    )

    shared_source_rows = []
    for label, df in [
        ("a7al2k_generated_pool", generated),
        ("a7al2l_replayed_target_pool", replayed_decisions),
        ("a7ar7_shared_candidate_pool", shared),
        ("a7al2x1_dry_rerank_trace", x1),
    ]:
        if df.empty:
            shared_source_rows.append(
                {
                    "artifact": label,
                    "candidate_count": 0,
                    "family_count": 0,
                    "top_family": "",
                    "top_family_share": 0.0,
                    "source_of_truth_role": "",
                }
            )
            continue
        vc = df["a7al2x2_objective_family"].value_counts()
        shared_source_rows.append(
            {
                "artifact": label,
                "candidate_count": int(len(df)),
                "family_count": int(vc.shape[0]),
                "top_family": str(vc.index[0]),
                "top_family_share": float(vc.iloc[0] / len(df)),
                "source_of_truth_role": (
                    "generator_broad_pool"
                    if label == "a7al2k_generated_pool"
                    else "current_selector_source_of_truth"
                    if label == "a7ar7_shared_candidate_pool"
                    else "downstream_stage"
                ),
            }
        )
    source_gap = pd.DataFrame(shared_source_rows)

    repair_plan = pd.DataFrame(
        [
            {
                "step": "A7AL-2X2R0",
                "name": "family-balanced generator coverage repair contract",
                "description": "Add explicit quotas for F1-F6 historical fields before any selector or replay.",
                "executes_generation": False,
                "executes_replay": False,
                "authorizes_search": False,
            },
            {
                "step": "A7AL-2X2R1",
                "name": "shared-pool ledger rebuild contract",
                "description": "Define a new shared pool source-of-truth that includes all A7AL-2X families, not only local OI-price candidates.",
                "executes_generation": False,
                "executes_replay": False,
                "authorizes_search": False,
            },
            {
                "step": "A7AL-2X3",
                "name": "family-balanced dry generation smoke",
                "description": "Only after R0/R1, generate a small balanced candidate pool and stop before replay.",
                "executes_generation": True,
                "executes_replay": False,
                "authorizes_search": False,
            },
        ]
    )

    blockers = []
    if int(funnel.loc[funnel.family_id.isin(FAMILIES[:7]), "x1_non_rejected_count"].sum()) == 0:
        blockers.append("no_a7al2x_allowed_family_candidate_survives_x1_dry_rerank")
    if int(funnel.loc[funnel.family_id.isin(FAMILIES[1:7]), "shared_pool_count"].sum()) == 0:
        blockers.append("f1_f6_absent_from_a7ar7_shared_pool_source_of_truth")
    if int(funnel.loc[funnel.family_id.isin(FAMILIES[1:7]), "a7al2l_replayed_count"].sum()) == 0:
        blockers.append("f1_f6_absent_from_a7al2l_target_replay")
    if int(funnel.loc[funnel.family_id == "F3_positioning_divergence", "historical_generated_count"].iloc[0]) == 0:
        blockers.append("positioning_family_generated_only_as_j5_overlay_diagnostic")
    if int(funnel.loc[funnel.family_id == "F6_OI_latent_state_interaction", "generated_count"].iloc[0]) == 0:
        blockers.append("latent_state_interaction_family_not_generated")

    decision = "HOLD_A7AL2X2_OBJECTIVE_FAMILY_COVERAGE_GAP_REQUIRES_GENERATOR_AND_SHARED_POOL_REPAIR"
    manifest = {
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7al2x3_generation": False,
        "authorizes_a7al2y_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "input_generated_candidates": int(len(generated)),
        "input_shared_pool_candidates": int(len(shared)),
        "allowed_family_generated_total": int(funnel.loc[funnel.family_id.isin(FAMILIES[:7]), "generated_count"].sum()),
        "allowed_family_shared_pool_total": int(funnel.loc[funnel.family_id.isin(FAMILIES[:7]), "shared_pool_count"].sum()),
        "allowed_family_x1_non_rejected_total": int(funnel.loc[funnel.family_id.isin(FAMILIES[:7]), "x1_non_rejected_count"].sum()),
        "blockers": blockers,
    }

    decision_record = {
        "decision": decision,
        "a7al2x3_family_balanced_generation": "NOT_AUTHORIZED",
        "a7al2y_generation": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
        "reason": "Existing shared pool is local OI-price oriented; A7AL-2X allowed F1-F6 families lack replay/shared-pool coverage and X1 eligible candidates.",
    }

    generated_family_coverage.to_csv(RUNTIME / "a7al2x2_generated_family_coverage.csv", index=False)
    funnel.to_csv(RUNTIME / "a7al2x2_stage_funnel_by_family.csv", index=False)
    missing.to_csv(RUNTIME / "a7al2x2_missing_family_gap_audit.csv", index=False)
    source_gap.to_csv(RUNTIME / "a7al2x2_source_of_truth_gap.csv", index=False)
    repair_plan.to_csv(RUNTIME / "a7al2x2_repair_plan.csv", index=False)
    write_json(RUNTIME / "a7al2x2_manifest.json", manifest)
    write_json(RUNTIME / "a7al2x2_decision_record.json", decision_record)

    report = f"""# CRYPTO A7AL-2X2 Objective-Family Coverage Gap Audit

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This audit executes no generation, no replay, no training, and no search. It reconciles A7AL-2K generated candidates, A7AL-2L fast replay preflight, A7AR-7 shared pool, and A7AL-2X1 dry rerank against the A7AL-2X objective-family reset contract.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Stage Funnel By Family

{md_table(funnel)}

## Missing Family Gap Audit

{md_table(missing)}

## Source-Of-Truth Gap

{md_table(source_gap)}

## Repair Plan

{md_table(repair_plan)}

## Interpretation

```text
The current shared pool is not an A7AL-2X broad OI/positioning interaction pool.
It is a local OI-price lineage pool inherited from A7AL-2P2/A7AL-2Q.

A7AL-2K did generate some F1/F2/F4/F5-like structures, but A7AL-2L ran in two-target replay mode and did not replay those families.
F3 positioning is present only through J5 cross-exchange overlay diagnostics, not as a historical proof-grade Binance metrics family.
F6 latent-state interaction is not generated.

Therefore A7AL-2Y remains not authorized.
The next valid work is a family-balanced generator/shared-pool repair contract, not replay or search execution.
```

## Boundary

```text
No generation.
No replay.
No search.
No May in selector/ranking/mutation/generation.
No alpha proof / shadow / paper / live.
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
