from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls0_checkpoint_large_search_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS0_CHECKPOINT_LARGE_SEARCH_CONTRACT_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
        return "```csv\n" + view.to_csv(index=False) + "```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    arms = pd.DataFrame(
        [
            {
                "arm_id": "A7LS_A",
                "arm_name": "basis_premium_price_vol_evidence_guided",
                "purpose": "Exploit the strongest current evidence from CORE65A: basis/premium with price and volatility transforms.",
                "generated_budget": 60000,
                "materialization_budget": 10000,
                "numeric_budget": 2000,
                "priority": 1,
                "allowed_field_axes": "basis_premium_like;price_like;volatility_like",
                "allowed_transform_depth": "typed_l1_l2_l3",
                "checkpoint_policy": "normal",
                "search_role": "evidence_guided",
            },
            {
                "arm_id": "A7LS_B",
                "arm_name": "raw_multi_axis_discovery",
                "purpose": "Reserve one full route for raw multi-axis search to test system utility beyond hand-shaped objectives.",
                "generated_budget": 60000,
                "materialization_budget": 10000,
                "numeric_budget": 2000,
                "priority": 2,
                "allowed_field_axes": "price_like;basis_premium_like;funding_state_like;open_interest_like;positioning_like;taker_flow_like;liquidity_like;volatility_like;listing_age_like;regime_state",
                "allowed_transform_depth": "raw_or_simple_typed_l1_l2_only",
                "checkpoint_policy": "strict_efficiency",
                "search_role": "raw_discovery",
            },
            {
                "arm_id": "A7LS_C",
                "arm_name": "state_interaction_repair",
                "purpose": "Use repaired state variables, especially funding_state_8h, OI/positioning/taker, as controlled interactions.",
                "generated_budget": 60000,
                "materialization_budget": 10000,
                "numeric_budget": 2000,
                "priority": 3,
                "allowed_field_axes": "funding_state_like;open_interest_like;positioning_like;taker_flow_like;basis_premium_like;regime_state",
                "allowed_transform_depth": "typed_l1_l2_l3",
                "checkpoint_policy": "normal",
                "search_role": "state_interaction",
            },
            {
                "arm_id": "A7LS_D",
                "arm_name": "control_and_selector_stress",
                "purpose": "Keep a budgeted negative/control arm to detect selector self-deception and raw-axis false positives.",
                "generated_budget": 60000,
                "materialization_budget": 10000,
                "numeric_budget": 2000,
                "priority": 4,
                "allowed_field_axes": "placebo;wrong_lag;shuffle;sign_flip;same_family_control;low_prior_axes",
                "allowed_transform_depth": "control_only",
                "checkpoint_policy": "control",
                "search_role": "negative_control",
            },
        ]
    )
    arms["generated_share"] = arms["generated_budget"] / arms["generated_budget"].sum()
    arms["numeric_share"] = arms["numeric_budget"] / arms["numeric_budget"].sum()
    arms.to_csv(RUNTIME / "a7ls0_arm_budget_map.csv", index=False)

    raw_axes = pd.DataFrame(
        [
            {"axis": "price_like", "raw_fields": "trade_close;mark_close;index_close;trade_return_1h", "quota_share_within_raw_arm": 0.12, "notes": "No single price axis may dominate raw arm."},
            {"axis": "basis_premium_like", "raw_fields": "mark_index_basis_bps;premium_close_bps", "quota_share_within_raw_arm": 0.14, "notes": "Allowed because strongest current evidence, but capped inside raw arm."},
            {"axis": "funding_state_like", "raw_fields": "funding_rate_state_last_ffill_8h;funding_event_age_hours", "quota_share_within_raw_arm": 0.10, "notes": "Use repaired PIT state, not sparse raw funding_rate."},
            {"axis": "open_interest_like", "raw_fields": "open_interest_last;open_interest_mean;open_interest_value_last;open_interest_value_mean", "quota_share_within_raw_arm": 0.12, "notes": "Raw OI axis gets real quota despite weak prior."},
            {"axis": "positioning_like", "raw_fields": "global_long_short_account_ratio_last;top_long_short_account_ratio_last;top_long_short_position_ratio_last", "quota_share_within_raw_arm": 0.10, "notes": "Positioning axis included to test independent information."},
            {"axis": "taker_flow_like", "raw_fields": "taker_buy_sell_volume_ratio_last;taker_buy_sell_volume_ratio_mean;kline_taker_buy_quote_share", "quota_share_within_raw_arm": 0.10, "notes": "Flow proxy axis."},
            {"axis": "liquidity_like", "raw_fields": "quote_volume;trade_count;liquidity_rank_active_universe", "quota_share_within_raw_arm": 0.10, "notes": "Must survive neutralization, not standalone liquidity beta."},
            {"axis": "volatility_like", "raw_fields": "realized_vol_24h;realized_vol_72h;realized_vol_168h", "quota_share_within_raw_arm": 0.08, "notes": "Mostly interaction/state axis."},
            {"axis": "listing_age_like", "raw_fields": "listing_age_days;age_x_liquidity;age_x_volatility", "quota_share_within_raw_arm": 0.07, "notes": "Allowed as lifecycle axis; not proof universe substitute."},
            {"axis": "regime_state", "raw_fields": "upper_regime_state;latent_state;liquidity_tier;major_meme_multiplier_tags", "quota_share_within_raw_arm": 0.07, "notes": "Conditioning and neutralization axis; direct signal use capped."},
        ]
    )
    raw_axes.to_csv(RUNTIME / "a7ls0_raw_multi_axis_policy.csv", index=False)

    checkpoint_policy = {
        "stage": "A7LS-0",
        "total_generated_budget": int(arms["generated_budget"].sum()),
        "total_materialization_budget": int(arms["materialization_budget"].sum()),
        "total_numeric_budget": int(arms["numeric_budget"].sum()),
        "checkpoint_interval_numeric_rows": 1000,
        "early_checkpoint_interval_numeric_rows": 500,
        "arm_survival_gates": {
            "activity_ok_rate_min": 0.50,
            "non_l7_clue_rate_min_after_1000": 0.003,
            "control_dominated_rate_max": 0.45,
            "selected_queue_min_after_1000": 4,
            "top_semantic_pair_share_max": 0.40,
            "l7_share_max": 0.60,
        },
        "raw_arm_special_rules": {
            "arm_id": "A7LS_B",
            "must_keep_until_numeric_rows": 2000,
            "min_active_axes_after_checkpoint": 5,
            "top_axis_share_max": 0.25,
            "reason": "Raw multi-axis search is reserved to test system utility and should not be killed by first-checkpoint noise unless controls dominate.",
        },
        "kill_rules": [
            "eval_failure_rate > 0.05",
            "activity_ok_rate < 0.35 after first checkpoint",
            "control_dominated_rate > 0.60 after first checkpoint",
            "non_l7_clue_rate == 0 and selected_queue == 0 after two checkpoints",
            "single semantic pair share > 0.55 after diversity repair",
        ],
        "expand_rules": [
            "non_l7_clue_rate >= 0.008 and selected_queue >= 8",
            "control_dominated_rate <= 0.25",
            "at least three semantic pairs or five raw axes active",
        ],
        "authorization_boundary": {
            "authorizes_blueprint_generation": True,
            "authorizes_materialization_wave": True,
            "authorizes_numeric_wave": True,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        },
    }
    write_json(RUNTIME / "a7ls0_checkpoint_policy.json", checkpoint_policy)

    authorization = {
        "authorized": {
            "A7LS-1 multi-arm blueprint generation": True,
            "A7LS-2 sharded materialization wave with checkpoint": True,
            "A7LS-3 sharded numeric wave with checkpoint": True,
            "raw_multi_axis_discovery_arm": True,
        },
        "not_authorized": {
            "alpha_proof": True,
            "shadow_paper_live": True,
            "unbounded_full_grammar": True,
            "single_arm_budget_capture": True,
            "May_in_selector_score": True,
        },
    }
    write_json(RUNTIME / "a7ls0_authorization_matrix.json", authorization)

    manifest = {
        "stage": "A7LS-0",
        "generated_at": now_utc(),
        "decision": "PASS_A7LS0_CHECKPOINT_LARGE_SEARCH_CONTRACT_READY",
        "arm_count": int(len(arms)),
        "raw_multi_axis_arm_id": "A7LS_B",
        "raw_multi_axis_generated_budget": 60000,
        "total_generated_budget": int(arms["generated_budget"].sum()),
        "total_materialization_budget": int(arms["materialization_budget"].sum()),
        "total_numeric_budget": int(arms["numeric_budget"].sum()),
        "executes_generation": False,
        "executes_materialization": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_a7ls1_blueprint_generation": True,
        "authorizes_a7ls2_materialization_wave": True,
        "authorizes_a7ls3_numeric_wave": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls0_manifest.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-0 CHECKPOINT LARGE SEARCH CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7LS-0 defines a four-arm checkpoint-driven large search. One full route is reserved for raw multi-axis discovery, as a direct test of system usability beyond single-objective convergence.",
        "",
        "## Core Change",
        "",
        "The search is not a one-way basis/premium convergence. `A7LS_B raw_multi_axis_discovery` receives a full 25% budget share and is protected until at least 2,000 numeric rows unless controls dominate.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Arm Budget Map",
        "",
        md_table(arms, 20),
        "",
        "## Raw Multi-Axis Policy",
        "",
        md_table(raw_axes, 40),
        "",
        "## Checkpoint Policy",
        "",
        "```json",
        json.dumps(checkpoint_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "This contract authorizes A7LS-1/2/3 generation and checkpoint waves.",
        "It does not authorize alpha proof, shadow, paper, live, May-informed selector score, or unbounded full grammar.",
        "Raw multi-axis search is budgeted, not merely diagnostic, but remains checkpoint-governed.",
        "```",
    ]), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
