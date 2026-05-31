# CRYPTO A7FF-CORE7E NUMERIC RESPONSE EXECUTION

Generated: 2026-05-31T22:59:18Z

## Decision

`HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK`

A7FF-CORE7E computes bounded label/control numeric response for the CORE6E materialized gate-native queue. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core8": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_primary_non_l7_numeric_clues"
  ],
  "candidate_count": 2048,
  "decision": "HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK",
  "eval_error_count": 0,
  "executes_numeric": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T22:59:18Z",
  "next_allowed": "A7FF-CORE7R response repair or label/control forensic",
  "numeric_clue_rows": 0,
  "panel_rows": 6949596,
  "primary_non_l7_clue_rows": 0,
  "response_rows": 40960,
  "sample_rows": 169239,
  "sample_timestamp_count": 512,
  "shard_count": 8,
  "source_decision": "PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E",
  "source_stage": "A7FF-CORE7",
  "stage": "A7FF-CORE7E",
  "uses_may": false,
  "wrong_lag_or_control_dominated_rows": 40960
}
```

## Label Summary

| label_id                           |   horizon |   rows |   numeric_clues |   median_abs_corr |   median_control_ratio |
|:-----------------------------------|----------:|-------:|----------------:|------------------:|-----------------------:|
| L7_ranked_future_return            |        24 |   2048 |               0 |        0.00496372 |                1.00251 |
| L7_ranked_future_return            |         4 |   2048 |               0 |        0.00380063 |                1.02774 |
| L7_ranked_future_return            |         8 |   2048 |               0 |        0.00371876 |                1.03334 |
| L7_ranked_future_return            |         1 |   2048 |               0 |        0.00331615 |                1.69764 |
| L0_raw_forward_return              |         1 |   2048 |               0 |        0.00295127 |                2.83077 |
| L0_raw_forward_return              |         4 |   2048 |               0 |        0.00282683 |                1.99069 |
| L1_cross_sectional_relative_return |         1 |   2048 |               0 |        0.00279358 |                2.96904 |
| L5_vol_adjusted_return             |         4 |   2048 |               0 |        0.00262764 |                2.0205  |
| L1_cross_sectional_relative_return |         4 |   2048 |               0 |        0.00240584 |                2.75671 |
| L3_liquidity_tier_relative_return  |         8 |   2048 |               0 |        0.00236324 |                2.62558 |
| L0_raw_forward_return              |         8 |   2048 |               0 |        0.00232868 |                1.93618 |
| L1_cross_sectional_relative_return |        24 |   2048 |               0 |        0.00225949 |                1.84512 |
| L5_vol_adjusted_return             |         1 |   2048 |               0 |        0.00224189 |                3.19629 |
| L3_liquidity_tier_relative_return  |        24 |   2048 |               0 |        0.00222545 |                2.11695 |
| L0_raw_forward_return              |        24 |   2048 |               0 |        0.00220993 |                1.84164 |
| L5_vol_adjusted_return             |         8 |   2048 |               0 |        0.00219428 |                1.69884 |
| L3_liquidity_tier_relative_return  |         1 |   2048 |               0 |        0.00218463 |                3.7056  |
| L1_cross_sectional_relative_return |         8 |   2048 |               0 |        0.00212835 |                2.86087 |
| L3_liquidity_tier_relative_return  |         4 |   2048 |               0 |        0.00209748 |                2.70505 |
| L5_vol_adjusted_return             |        24 |   2048 |               0 |        0.00165209 |                2.09001 |

## Family Summary

| semantic_bucket                      | motif_bucket        |   rows |   candidate_count |   numeric_clues |   median_control_ratio |
|:-------------------------------------|:--------------------|-------:|------------------:|----------------:|-----------------------:|
| liquidity_like                       | liquidity_shock     |    200 |                10 |               0 |                1.38178 |
| liquidity_like                       | single              |   1960 |                98 |               0 |                1.26515 |
| liquidity_like\|volatility_like      | liquidity_shock     |   7400 |               370 |               0 |                1.87675 |
| liquidity_like\|volatility_like      | mean_reversion_gate |   7200 |               360 |               0 |                2.05209 |
| liquidity_like\|volatility_like      | safe_div_abs        |   6400 |               320 |               0 |                1.6993  |
| open_interest_like                   | delta_x_divergence  |    400 |                20 |               0 |                1.40592 |
| open_interest_like                   | flow_x_leverage     |    400 |                20 |               0 |                2.64814 |
| open_interest_like                   | single              |    400 |                20 |               0 |                2.15033 |
| open_interest_like\|positioning_like | delta_x_divergence  |   3840 |               192 |               0 |                4.93406 |
| open_interest_like\|price_like       | delta_x_divergence  |    880 |                44 |               0 |                7.18699 |
| open_interest_like\|price_like       | mean_reversion_gate |   2960 |               148 |               0 |                1.95026 |
| taker_flow_like                      | flow_x_leverage     |    200 |                10 |               0 |                2.15173 |
| taker_flow_like                      | single              |    760 |                38 |               0 |                2.53507 |
| taker_flow_like\|basis_premium_like  | gated_sign          |   3840 |               192 |               0 |                3.05538 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |   3840 |               192 |               0 |                1.91941 |
| volatility_like                      | single              |    280 |                14 |               0 |                1.59267 |

## Shard Summary

| shard_id   |   candidate_count |   response_rows |   eval_errors |   numeric_clues |   primary_non_l7_clues | output                                                          |
|:-----------|------------------:|----------------:|--------------:|----------------:|-----------------------:|:----------------------------------------------------------------|
| S00        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S00_response.csv |
| S01        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S01_response.csv |
| S02        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S02_response.csv |
| S03        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S03_response.csv |
| S04        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S04_response.csv |
| S05        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S05_response.csv |
| S06        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S06_response.csv |
| S07        |               256 |            5120 |             0 |               0 |                      0 | runtime\a7ffcore7e_numeric_response\a7ffcore7e_S07_response.csv |

## Top Numeric Clues

`<empty>`

## Boundary

```text
numeric response executed: true
portfolio replay: false
search: false
promotion: false
May used for orientation/scoring: false
alpha proof / shadow / paper / live: false
```
