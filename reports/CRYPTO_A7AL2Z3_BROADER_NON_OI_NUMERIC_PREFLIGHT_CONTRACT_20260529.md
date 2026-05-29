# CRYPTO A7AL-2Z3 BROADER NON-OI NUMERIC PREFLIGHT CONTRACT

Generated: 2026-05-29T03:44:34Z

## Decision

`PASS_A7AL2Z3_BROADER_NON_OI_NUMERIC_PREFLIGHT_CONTRACT_READY_FOR_Z4`

Z3 authorizes one bounded numeric preflight on the Z2R materialized queue. It does not authorize search, full replay, or proof.

## Manifest

```json
{
  "authorizes_a7al2z4_broader_non_oi_numeric_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_full_replay": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 128,
  "cost_proxy_bps": [
    10
  ],
  "decision": "PASS_A7AL2Z3_BROADER_NON_OI_NUMERIC_PREFLIGHT_CONTRACT_READY_FOR_Z4",
  "executes_contract_only": true,
  "executes_numeric_replay": false,
  "executes_training": false,
  "family_count": 8,
  "generated_at": "2026-05-29T03:44:34Z",
  "hours_per_split": 720,
  "label": "log_trade_close_t_plus_24h_minus_log_trade_close_t",
  "may_policy": "post_selection_stress_only",
  "orientation": "train_2024_original_spread_sign_only",
  "stage": "A7AL-2Z3",
  "symbol_cap": 96,
  "uses_may_in_selector_or_generation": false
}
```

## Family Inputs

| objective_family                         |   candidate_count |   skeleton_count |
|:-----------------------------------------|------------------:|-----------------:|
| Z0_funding_basis_premium_dislocation     |                16 |                5 |
| Z1_price_range_volatility_structure      |                16 |               11 |
| Z2_liquidity_taker_microstructure_lite   |                16 |                8 |
| Z3_basis_price_trend_reversal            |                16 |                5 |
| Z4_upper_regime_relative_value           |                16 |                3 |
| Z5_latent_listing_meme_neutral_structure |                16 |                5 |
| Z6_cross_sectional_relative_flow_value   |                16 |                4 |
| Z7_market_regime_price_breadth           |                16 |                3 |

## Negative Controls

| control              | purpose                        |
|:---------------------|:-------------------------------|
| one_bar_lag          | entry latency survival         |
| wrong_lag_future_24h | future-lag contamination check |
| wrong_lag_stale_168h | stale-lag contamination check  |
| time_shuffle         | time structure placebo         |
| symbol_shuffle       | cross-symbol identity placebo  |
| same_family_random   | same-shape random placebo      |
