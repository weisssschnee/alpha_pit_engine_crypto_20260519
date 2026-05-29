# CRYPTO A7AA-0 LABEL / FEATURE RESPONSE CONTRACT

Generated: 2026-05-29T05:07:00Z

## Decision

`PASS_A7AA0_LABEL_FEATURE_RESPONSE_CONTRACT_READY_FOR_A7AA1`

A7AA-0 freezes the primitive response-map contract after Z-series formula-first diagnostics failed. It does not search, replay, train, or prove alpha.

## Manifest

```json
{
  "authorizes_a7aa1_primitive_response_map": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AA0_LABEL_FEATURE_RESPONSE_CONTRACT_READY_FOR_A7AA1",
  "executes_contract_only": true,
  "executes_response_map": false,
  "executes_search": false,
  "executes_training": false,
  "feature_count": 32,
  "generated_at": "2026-05-29T05:07:00Z",
  "label_families_allowed_in_a7aa1": 5,
  "source_z9_decision": "HOLD_A7AL2Z9_NO_RESPONSE_GUIDED_PARTIAL_NUMERIC_CLUES",
  "source_z9_stress_clean_count": 0,
  "stage": "A7AA-0",
  "uses_may_for_contract": false
}
```

## Label Families

| label_family                       | definition                                                                | role                                                | allowed_in_a7aa1   |
|:-----------------------------------|:--------------------------------------------------------------------------|:----------------------------------------------------|:-------------------|
| L0_raw_forward_return              | log(close_t+h)-log(close_t)                                               | baseline raw forward return                         | True               |
| L1_cross_sectional_relative_return | raw forward return minus timestamp cross-sectional mean                   | market-mode reduced relative return                 | True               |
| L3_liquidity_tier_relative_return  | raw forward return demeaned within liquidity_tier                         | liquidity-tier relative label                       | True               |
| L5_vol_adjusted_return             | raw forward return divided by realized_vol_168h                           | vol-normalized response                             | True               |
| L7_ranked_future_return            | timestamp cross-sectional rank percentile of raw forward return minus 0.5 | ranked future return                                | True               |
| L2_BTC_ETH_beta_residual_return    | future return residualized versus BTC/ETH beta proxy                      | contract only; not used until beta matrix is frozen | False              |
| L6_downside_avoidance              | asymmetric downside/crash avoidance label                                 | contract only; requires separate downside objective | False              |

## Transforms

| transform      | uses_future   | description                               |
|:---------------|:--------------|:------------------------------------------|
| level          | False         | raw feature value                         |
| delta_4h       | False         | feature_t - feature_t-4                   |
| delta_24h      | False         | feature_t - feature_t-24                  |
| cs_rank        | False         | timestamp cross-sectional rank percentile |
| ts_zscore_168h | False         | past rolling 168h zscore                  |

## Candidate Primitive Fields

| field_name                           | field_family              | source_family                   | feature_class         | allowed_for_search   | allowed_for_label   |
|:-------------------------------------|:--------------------------|:--------------------------------|:----------------------|:---------------------|:--------------------|
| trade_return_1h                      | price_return              | derived_replay_base             | derived_rolling       | True                 | False               |
| trade_return_24h                     | price_return              | trade_ohlcv                     | derived_rolling       | True                 | False               |
| realized_vol_24h                     | volatility                | trade_ohlcv                     | derived_rolling       | True                 | False               |
| realized_vol_168h                    | volatility                | trade_ohlcv                     | derived_rolling       | True                 | False               |
| trade_quote_volume                   | liquidity                 | trade_ohlcv                     | raw_source            | True                 | False               |
| trade_count                          | liquidity                 | trade_ohlcv                     | raw_source            | True                 | False               |
| liquidity_rank_active_universe       | liquidity                 | trade_ohlcv                     | derived_cross_section | True                 | False               |
| kline_taker_buy_quote_share          | taker_flow                | trade_ohlcv                     | raw_source            | True                 | False               |
| taker_buy_sell_volume_ratio_last     | taker_flow                | metrics_positioning             | raw_source            | True                 | False               |
| funding_rate                         | funding                   | funding                         | raw_source            | True                 | False               |
| funding_rate_abs_168h                | funding                   | funding                         | derived_rolling       | True                 | False               |
| funding_rate_mean_168h               | funding                   | funding                         | derived_rolling       | True                 | False               |
| premium_close_bps                    | basis_premium             | derived_replay_base             | derived_rolling       | True                 | False               |
| mark_index_basis_bps                 | basis_premium             | mark_index_premium              | raw_source            | True                 | False               |
| mark_trade_basis_bps                 | basis_premium             | mark_index_premium              | raw_source            | True                 | False               |
| basis_abs_168h                       | basis_premium             | mark_index_premium              | derived_rolling       | True                 | False               |
| premium_abs_168h                     | basis_premium             | mark_index_premium              | derived_rolling       | True                 | False               |
| open_interest_last                   | open_interest             | metrics_positioning             | raw_source            | True                 | False               |
| open_interest_value_last             | open_interest             | metrics_positioning             | raw_source            | True                 | False               |
| open_interest_change_24h             | open_interest             | metrics_positioning             | derived_rolling       | True                 | False               |
| oi_x_price_move_24h                  | open_interest_interaction | metrics_positioning,trade_ohlcv | derived_interaction   | True                 | False               |
| global_long_short_account_ratio_last | positioning               | metrics_positioning             | raw_source            | True                 | False               |
| top_long_short_account_ratio_last    | positioning               | metrics_positioning             | raw_source            | True                 | False               |
| top_long_short_position_ratio_last   | positioning               | metrics_positioning             | raw_source            | True                 | False               |
| age_percentile_active_universe       | listing_age               | metadata_listing                | derived_cross_section | True                 | False               |
| log1p_listing_age_days               | listing_age               | metadata_listing                | derived_latent_state  | True                 | False               |
| age_x_liquidity                      | listing_age_interaction   | metadata_listing,trade_ohlcv    | derived_interaction   | True                 | False               |
| age_x_volatility                     | listing_age_interaction   | metadata_listing,trade_ohlcv    | derived_interaction   | True                 | False               |
| volume_volatility_ratio_168h         | liquidity_volatility      | trade_ohlcv                     | derived_interaction   | True                 | False               |
| rolling_coverage_168h                | coverage                  | metadata_timing                 | derived_rolling       | False                | False               |
| gap_hours_recent_168h                | coverage                  | metadata_timing                 | derived_rolling       | False                | False               |
| median_quote_volume_168h             | liquidity                 | trade_ohlcv                     | derived_rolling       | True                 | False               |

## Controls

| control              | purpose                       |
|:---------------------|:------------------------------|
| one_bar_lag          | entry latency survival        |
| wrong_lag_future_24h | lookahead contamination check |
| wrong_lag_stale_168h | stale signal placebo          |
| same_family_random   | random signal placebo         |
