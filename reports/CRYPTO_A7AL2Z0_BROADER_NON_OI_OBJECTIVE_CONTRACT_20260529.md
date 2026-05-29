# CRYPTO A7AL-2Z0 BROADER NON-OI OBJECTIVE CONTRACT

Generated: 2026-05-29T03:29:57Z

## Decision

`PASS_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_READY_FOR_A7AL2Z1`

Z0 is a contract stage. It does not run search, replay, training, or proof.

## Manifest

```json
{
  "allowed_family_count": 8,
  "authorizes_a7al2z1_static_dry_generation": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_READY_FOR_A7AL2Z1",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "forbidden_item_count": 11,
  "generated_at": "2026-05-29T03:29:57Z",
  "input_x7hf_candidate_count": 56,
  "input_x7hf_decision": "HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK",
  "input_x7hf_stress_clean_count": 0,
  "may_policy": "stress_only_veto_and_failure_attribution",
  "stage": "A7AL-2Z0",
  "trigger": "A7AL-2X7H/X7HF heavy OI-positioning pool produced zero stress-clean clues"
}
```

## Allowed Families

| family_id                                | status                             | core_fields                                                                                                                          | state_fields                                                                                                                         | economic_role                                                                      |   minimum_generated |   minimum_selected_for_preflight |
|:-----------------------------------------|:-----------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|--------------------:|---------------------------------:|
| Z0_funding_basis_premium_dislocation     | allowed_static_generation_contract | funding_rate\|premium_close_bps\|mark_index_basis_bps\|mark_trade_basis_bps                                                          | R5_basis_premium_dislocation_state\|R10_stress_proxy_state                                                                           | funding/basis/premium dislocation without OI wrapper                               |                  96 |                               12 |
| Z1_price_range_volatility_structure      | allowed_static_generation_contract | trade_close\|index_close\|mark_close\|trade_high\|trade_low\|mark_high\|mark_low                                                     | R0_market_trend_state\|R1_market_volatility_state\|R10_stress_proxy_state                                                            | price/range/volatility structure and reversal without direct liquidity-vol cluster |                 128 |                               16 |
| Z2_liquidity_taker_microstructure_lite   | allowed_static_generation_contract | trade_quote_volume\|trade_volume\|trade_count\|taker_buy_quote_volume\|kline_taker_buy_quote_share\|taker_buy_sell_volume_ratio_last | R3_liquidity_cycle_state\|R2_market_breadth_state\|R10_stress_proxy_state                                                            | liquidity/taker flow changes as state, not A7V self-reproduction                   |                 128 |                               16 |
| Z3_basis_price_trend_reversal            | allowed_static_generation_contract | mark_index_basis_bps\|mark_trade_basis_bps\|premium_close_bps\|trade_close\|index_close\|mark_close                                  | R0_market_trend_state\|R5_basis_premium_dislocation_state                                                                            | basis/premium interacting with price trend/reversal                                |                  96 |                               12 |
| Z4_upper_regime_relative_value           | allowed_static_generation_contract | funding_rate\|premium_close_bps\|mark_index_basis_bps\|trade_return_1h\|trade_quote_volume                                           | R0_market_trend_state\|R2_market_breadth_state\|R3_liquidity_cycle_state\|R10_stress_proxy_state                                     | relative value under train-frozen upper-regime states                              |                 128 |                               16 |
| Z5_latent_listing_meme_neutral_structure | allowed_static_generation_contract | trade_return_1h\|premium_close_bps\|funding_rate\|trade_quote_volume\|kline_taker_buy_quote_share                                    | liquidity_tier\|meme_contract_group\|is_multiplier_contract\|is_major                                                                | listing/meme/multiplier/major neutral structure without post-hoc May mask          |                 128 |                               16 |
| Z6_cross_sectional_relative_flow_value   | allowed_static_generation_contract | premium_close_bps\|funding_rate\|kline_taker_buy_quote_share\|trade_quote_volume\|trade_count                                        | liquidity_tier\|R3_liquidity_cycle_state                                                                                             | cross-sectional relative flow/value contrast, no OI/positioning                    |                  96 |                               12 |
| Z7_market_regime_price_breadth           | allowed_static_generation_contract | trade_close\|index_close\|trade_return_1h\|trade_quote_volume\|premium_close_bps                                                     | R0_market_trend_state\|R1_market_volatility_state\|R2_market_breadth_state\|R9_alt_vs_major_dispersion_state\|R10_stress_proxy_state | market-regime-aware price/breadth effects, not OI/positioning                      |                 128 |                               16 |

## Forbidden Fields And Families

| item                                     | status            | reason                                    |
|:-----------------------------------------|:------------------|:------------------------------------------|
| open_interest_last                       | forbidden_as_core | A7AL-2X7H/X7HF rejected current OI pool   |
| open_interest_mean                       | forbidden_as_core | A7AL-2X7H/X7HF rejected current OI pool   |
| open_interest_value_last                 | forbidden_as_core | A7AL-2X7H/X7HF rejected current OI pool   |
| open_interest_value_mean                 | forbidden_as_core | A7AL-2X7H/X7HF rejected current OI pool   |
| global_long_short_account_ratio_*        | forbidden_as_core | positioning pool was control dominated    |
| top_long_short_account_ratio_*           | forbidden_as_core | positioning pool was control dominated    |
| top_long_short_position_ratio_*          | forbidden_as_core | positioning pool was control dominated    |
| A7V_activity_liquidity_self_reproduction | forbidden         | previous activity/liquidity family failed |
| liquidity_x_volatility_rc000_style       | forbidden         | previous cluster/stress failure           |
| May_in_selector_or_generation            | forbidden         | May stress-only                           |
| full_open_grammar                        | forbidden         | Z0/Z1 are bounded broader-family stages   |

## Authorization

```json
{
  "A7AL-2Z0": "PASS_A7AL2Z0_BROADER_NON_OI_OBJECTIVE_CONTRACT_READY_FOR_A7AL2Z1",
  "A7AL-2Z1_static_dry_generation": "AUTHORIZED",
  "A7AL-2Z2_materialization_audit": "NOT_AUTHORIZED_UNTIL_Z1_PASS",
  "alpha_proof": "NOT_AUTHORIZED",
  "formula_search_execution": "NOT_AUTHORIZED",
  "large_search": "NOT_AUTHORIZED",
  "numeric_replay": "NOT_AUTHORIZED",
  "shadow_paper_live": "NOT_AUTHORIZED"
}
```
