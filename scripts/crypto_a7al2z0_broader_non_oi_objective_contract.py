from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z0_broader_non_oi_objective_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_20260529.md"

X7HF_MANIFEST = REPO / "runtime" / "a7al2x7hf_heavy_replay_preflight_forensic" / "a7al2x7hf_manifest.json"
X7HF_FAMILY = REPO / "runtime" / "a7al2x7hf_heavy_replay_preflight_forensic" / "a7al2x7hf_objective_family_failure_summary.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if df[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    x7hf = read_json(X7HF_MANIFEST)
    if x7hf.get("stage") != "A7AL-2X7HF":
        raise SystemExit("A7AL-2X7HF manifest missing; run heavy forensic first")
    if int(x7hf.get("stress_clean_preflight_clue_count", -1)) != 0:
        raise SystemExit("A7AL-2Z0 expects X7HF zero stress-clean clue as reset trigger")

    families = pd.DataFrame(
        [
            {
                "family_id": "Z0_funding_basis_premium_dislocation",
                "status": "allowed_static_generation_contract",
                "core_fields": "funding_rate|premium_close_bps|mark_index_basis_bps|mark_trade_basis_bps",
                "state_fields": "R5_basis_premium_dislocation_state|R10_stress_proxy_state",
                "economic_role": "funding/basis/premium dislocation without OI wrapper",
                "minimum_generated": 96,
                "minimum_selected_for_preflight": 12,
            },
            {
                "family_id": "Z1_price_range_volatility_structure",
                "status": "allowed_static_generation_contract",
                "core_fields": "trade_close|index_close|mark_close|trade_high|trade_low|mark_high|mark_low",
                "state_fields": "R0_market_trend_state|R1_market_volatility_state|R10_stress_proxy_state",
                "economic_role": "price/range/volatility structure and reversal without direct liquidity-vol cluster",
                "minimum_generated": 128,
                "minimum_selected_for_preflight": 16,
            },
            {
                "family_id": "Z2_liquidity_taker_microstructure_lite",
                "status": "allowed_static_generation_contract",
                "core_fields": "trade_quote_volume|trade_volume|trade_count|taker_buy_quote_volume|kline_taker_buy_quote_share|taker_buy_sell_volume_ratio_last",
                "state_fields": "R3_liquidity_cycle_state|R2_market_breadth_state|R10_stress_proxy_state",
                "economic_role": "liquidity/taker flow changes as state, not A7V self-reproduction",
                "minimum_generated": 128,
                "minimum_selected_for_preflight": 16,
            },
            {
                "family_id": "Z3_basis_price_trend_reversal",
                "status": "allowed_static_generation_contract",
                "core_fields": "mark_index_basis_bps|mark_trade_basis_bps|premium_close_bps|trade_close|index_close|mark_close",
                "state_fields": "R0_market_trend_state|R5_basis_premium_dislocation_state",
                "economic_role": "basis/premium interacting with price trend/reversal",
                "minimum_generated": 96,
                "minimum_selected_for_preflight": 12,
            },
            {
                "family_id": "Z4_upper_regime_relative_value",
                "status": "allowed_static_generation_contract",
                "core_fields": "funding_rate|premium_close_bps|mark_index_basis_bps|trade_return_1h|trade_quote_volume",
                "state_fields": "R0_market_trend_state|R2_market_breadth_state|R3_liquidity_cycle_state|R10_stress_proxy_state",
                "economic_role": "relative value under train-frozen upper-regime states",
                "minimum_generated": 128,
                "minimum_selected_for_preflight": 16,
            },
            {
                "family_id": "Z5_latent_listing_meme_neutral_structure",
                "status": "allowed_static_generation_contract",
                "core_fields": "trade_return_1h|premium_close_bps|funding_rate|trade_quote_volume|kline_taker_buy_quote_share",
                "state_fields": "liquidity_tier|meme_contract_group|is_multiplier_contract|is_major",
                "economic_role": "listing/meme/multiplier/major neutral structure without post-hoc May mask",
                "minimum_generated": 128,
                "minimum_selected_for_preflight": 16,
            },
            {
                "family_id": "Z6_cross_sectional_relative_flow_value",
                "status": "allowed_static_generation_contract",
                "core_fields": "premium_close_bps|funding_rate|kline_taker_buy_quote_share|trade_quote_volume|trade_count",
                "state_fields": "liquidity_tier|R3_liquidity_cycle_state",
                "economic_role": "cross-sectional relative flow/value contrast, no OI/positioning",
                "minimum_generated": 96,
                "minimum_selected_for_preflight": 12,
            },
            {
                "family_id": "Z7_market_regime_price_breadth",
                "status": "allowed_static_generation_contract",
                "core_fields": "trade_close|index_close|trade_return_1h|trade_quote_volume|premium_close_bps",
                "state_fields": "R0_market_trend_state|R1_market_volatility_state|R2_market_breadth_state|R9_alt_vs_major_dispersion_state|R10_stress_proxy_state",
                "economic_role": "market-regime-aware price/breadth effects, not OI/positioning",
                "minimum_generated": 128,
                "minimum_selected_for_preflight": 16,
            },
        ]
    )

    forbidden = pd.DataFrame(
        [
            {"item": "open_interest_last", "status": "forbidden_as_core", "reason": "A7AL-2X7H/X7HF rejected current OI pool"},
            {"item": "open_interest_mean", "status": "forbidden_as_core", "reason": "A7AL-2X7H/X7HF rejected current OI pool"},
            {"item": "open_interest_value_last", "status": "forbidden_as_core", "reason": "A7AL-2X7H/X7HF rejected current OI pool"},
            {"item": "open_interest_value_mean", "status": "forbidden_as_core", "reason": "A7AL-2X7H/X7HF rejected current OI pool"},
            {"item": "global_long_short_account_ratio_*", "status": "forbidden_as_core", "reason": "positioning pool was control dominated"},
            {"item": "top_long_short_account_ratio_*", "status": "forbidden_as_core", "reason": "positioning pool was control dominated"},
            {"item": "top_long_short_position_ratio_*", "status": "forbidden_as_core", "reason": "positioning pool was control dominated"},
            {"item": "A7V_activity_liquidity_self_reproduction", "status": "forbidden", "reason": "previous activity/liquidity family failed"},
            {"item": "liquidity_x_volatility_rc000_style", "status": "forbidden", "reason": "previous cluster/stress failure"},
            {"item": "May_in_selector_or_generation", "status": "forbidden", "reason": "May stress-only"},
            {"item": "full_open_grammar", "status": "forbidden", "reason": "Z0/Z1 are bounded broader-family stages"},
        ]
    )

    selector_contract = {
        "allowed": [
            "field_lineage_ok",
            "pit_policy_ok",
            "activity_coverage",
            "family_balanced_quota",
            "skeleton_diversity",
            "signal_vector_diversity_later",
            "matched_control_attachment",
            "one_bar_lag_later",
            "cost_proxy_later",
            "timevarying_latent_neutral_later",
        ],
        "forbidden": [
            "May_return",
            "May_pass_fail",
            "May_margin",
            "promotion_label",
            "stale_A7AL2X_oi_pool_score",
        ],
        "required_controls": [
            "one_bar_lag",
            "wrong_lag_future_24h",
            "wrong_lag_stale_168h",
            "time_shuffle",
            "symbol_shuffle",
            "same_family_random",
        ],
    }

    authorization = {
        "A7AL-2Z0": "PASS_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_READY_FOR_A7AL2Z1",
        "A7AL-2Z1_static_dry_generation": "AUTHORIZED",
        "A7AL-2Z2_materialization_audit": "NOT_AUTHORIZED_UNTIL_Z1_PASS",
        "numeric_replay": "NOT_AUTHORIZED",
        "formula_search_execution": "NOT_AUTHORIZED",
        "large_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
    }

    manifest = {
        "stage": "A7AL-2Z0",
        "generated_at": now_utc(),
        "decision": "PASS_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_READY_FOR_A7AL2Z1",
        "trigger": "A7AL-2X7H/X7HF heavy OI-positioning pool produced zero stress-clean clues",
        "input_x7hf_decision": x7hf.get("decision"),
        "input_x7hf_candidate_count": x7hf.get("candidate_count"),
        "input_x7hf_stress_clean_count": x7hf.get("stress_clean_preflight_clue_count"),
        "allowed_family_count": int(len(families)),
        "forbidden_item_count": int(len(forbidden)),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7al2z1_static_dry_generation": True,
        "authorizes_numeric_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "stress_only_veto_and_failure_attribution",
    }

    families.to_csv(RUNTIME / "a7al2z0_allowed_objective_families.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7al2z0_forbidden_fields_and_families.csv", index=False)
    write_json(RUNTIME / "a7al2z0_selector_contract.json", selector_contract)
    write_json(RUNTIME / "a7al2z0_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7al2z0_manifest.json", manifest)

    x7_family = pd.read_csv(X7HF_FAMILY) if X7HF_FAMILY.exists() else pd.DataFrame()
    if not x7_family.empty:
        x7_family.to_csv(RUNTIME / "a7al2z0_prior_oi_positioning_failure_summary.csv", index=False)

    lines = [
        "# CRYPTO A7AL-2Z0 BROADER NON-OI OBJECTIVE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z0 is a contract stage. It does not run search, replay, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Allowed Families",
        "",
        md_table(families),
        "",
        "## Forbidden Fields And Families",
        "",
        md_table(forbidden),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
