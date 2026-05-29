# CRYPTO A7AE-0 LABEL ADEQUACY EXTENSION CONTRACT

Generated: 2026-05-29T07:56:54Z

## Decision

`PASS_A7AE0_LABEL_ADEQUACY_EXTENSION_CONTRACT_READY_FOR_A7AE1`

A7AE-0 extends A7AA/A7AD from rank-label diagnostics into a broader label adequacy audit. It does not generate formulas, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7ae1_label_adequacy_response_map": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AE0_LABEL_ADEQUACY_EXTENSION_CONTRACT_READY_FOR_A7AE1",
  "executes_contract_only": true,
  "executes_response_map": false,
  "executes_search": false,
  "executes_training": false,
  "feature_count": 24,
  "generated_at": "2026-05-29T07:56:54Z",
  "label_family_count": 7,
  "source_a7ad1_decision": "HOLD_A7AD1_RANKED_LABEL_TRANSLATION_TOO_NARROW",
  "source_a7ad1_translated_candidates": 1,
  "stage": "A7AE-0",
  "transform_count": 3,
  "uses_may": false
}
```

## Label Families

| label_family                       | definition                                                                               | role                                | enabled_in_a7ae1   |
|:-----------------------------------|:-----------------------------------------------------------------------------------------|:------------------------------------|:-------------------|
| L0_raw_forward_return              | log(close_t+h)-log(close_t)                                                              | baseline tradable raw return proxy  | True               |
| L1_cross_sectional_relative_return | raw forward return minus timestamp cross-sectional mean                                  | market-mode reduced relative return | True               |
| L2_BTC_ETH_beta_residual_return    | train-fit per-symbol residual versus BTC and ETH forward-return factors                  | major-beta residual return          | True               |
| L3_liquidity_tier_relative_return  | raw forward return demeaned within liquidity_tier at timestamp                           | liquidity-tier relative return      | True               |
| L5_vol_adjusted_return             | raw forward return divided by contemporaneous realized_vol_168h                          | volatility-normalized return        | True               |
| L6_downside_avoidance              | min(raw forward return, 0); higher spread means top bucket loses less in downside states | downside-avoidance diagnostic       | True               |
| L7_ranked_future_return            | timestamp cross-sectional rank percentile of raw forward return minus 0.5                | rank-label diagnostic only          | True               |

## Primitive Field Universe

| field_name                           | field_family              | source_family                   | feature_class         | allowed_for_search   | allowed_for_label   | a7aa2_seed_field   |
|:-------------------------------------|:--------------------------|:--------------------------------|:----------------------|:---------------------|:--------------------|:-------------------|
| trade_return_1h                      | price_return              | derived_replay_base             | derived_rolling       | True                 | False               | True               |
| trade_return_24h                     | price_return              | trade_ohlcv                     | derived_rolling       | True                 | False               | False              |
| realized_vol_24h                     | volatility                | trade_ohlcv                     | derived_rolling       | True                 | False               | True               |
| realized_vol_168h                    | volatility                | trade_ohlcv                     | derived_rolling       | True                 | False               | True               |
| trade_quote_volume                   | liquidity                 | trade_ohlcv                     | raw_source            | True                 | False               | False              |
| trade_count                          | liquidity                 | trade_ohlcv                     | raw_source            | True                 | False               | False              |
| liquidity_rank_active_universe       | liquidity                 | trade_ohlcv                     | derived_cross_section | True                 | False               | False              |
| kline_taker_buy_quote_share          | taker_flow                | trade_ohlcv                     | raw_source            | True                 | False               | False              |
| taker_buy_sell_volume_ratio_last     | taker_flow                | metrics_positioning             | raw_source            | True                 | False               | False              |
| funding_rate                         | funding                   | funding                         | raw_source            | True                 | False               | False              |
| funding_rate_abs_168h                | funding                   | funding                         | derived_rolling       | True                 | False               | False              |
| funding_rate_mean_168h               | funding                   | funding                         | derived_rolling       | True                 | False               | False              |
| premium_close_bps                    | basis_premium             | derived_replay_base             | derived_rolling       | True                 | False               | True               |
| mark_index_basis_bps                 | basis_premium             | mark_index_premium              | raw_source            | True                 | False               | True               |
| mark_trade_basis_bps                 | basis_premium             | mark_index_premium              | raw_source            | True                 | False               | False              |
| basis_abs_168h                       | basis_premium             | mark_index_premium              | derived_rolling       | True                 | False               | False              |
| premium_abs_168h                     | basis_premium             | mark_index_premium              | derived_rolling       | True                 | False               | False              |
| open_interest_last                   | open_interest             | metrics_positioning             | raw_source            | True                 | False               | False              |
| open_interest_value_last             | open_interest             | metrics_positioning             | raw_source            | True                 | False               | False              |
| open_interest_change_24h             | open_interest             | metrics_positioning             | derived_rolling       | True                 | False               | False              |
| oi_x_price_move_24h                  | open_interest_interaction | metrics_positioning,trade_ohlcv | derived_interaction   | True                 | False               | False              |
| global_long_short_account_ratio_last | positioning               | metrics_positioning             | raw_source            | True                 | False               | False              |
| top_long_short_account_ratio_last    | positioning               | metrics_positioning             | raw_source            | True                 | False               | False              |
| top_long_short_position_ratio_last   | positioning               | metrics_positioning             | raw_source            | True                 | False               | False              |

## Transforms

| transform   | description                               | enabled_in_a7ae1   |
|:------------|:------------------------------------------|:-------------------|
| level       | raw feature value                         | True               |
| delta_24h   | feature_t - feature_t-24                  | True               |
| cs_rank     | timestamp cross-sectional rank percentile | True               |

## Negative Controls

| control              | purpose                       |
|:---------------------|:------------------------------|
| one_bar_lag          | entry latency survival        |
| wrong_lag_future_24h | lookahead contamination check |
| wrong_lag_stale_168h | stale signal placebo          |
| same_family_random   | random signal placebo         |

## Boundary

```text
A7AE-1 is diagnostic only.
No formula search, large search, alpha proof, shadow, paper, or live authorization.
May is not used.
```
