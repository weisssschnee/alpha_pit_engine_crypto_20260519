# CRYPTO A7FF-53E NUMERIC RESPONSE SUMMARY

Generated: 2026-05-31T07:52:57Z

## Decision

`PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH`

A7FF-53E summarizes bounded numeric response shards over the A7FF-52E materialized sample. It is not replay, formula search, alpha proof, shadow, paper, or live authorization.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH",
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "families_with_non_l7_clues": 6,
  "generated_at": "2026-05-31T07:52:57Z",
  "input_blueprint_count": 1200,
  "label_response_rows": 21000,
  "materialized_activity_ok_count": 1050,
  "non_l7_numeric_clue_rows": 186,
  "pass_shard_count": 6,
  "rank_label_diagnostic_clue_rows": 258,
  "selected_portfolio_queue_count": 148,
  "shard_count": 8,
  "stage": "A7FF-53E",
  "uses_may": false
}
```

## Shard Summary

| shard   | decision                                                 | blockers                  |   input_blueprint_count |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count |   queue_offset |
|:--------|:---------------------------------------------------------|:--------------------------|------------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|---------------:|
| S00     | PASS_A7FF53ES00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                         77 |                                39 |                      29 |                               24 |              0 |
| S01     | PASS_A7FF53ES01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                         10 |                                40 |                      23 |                               23 |            150 |
| S02     | PASS_A7FF53ES02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                          3 |                                32 |                      20 |                               20 |            300 |
| S03     | PASS_A7FF53ES03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                         15 |                                60 |                      26 |                               24 |            450 |
| S04     | PASS_A7FF53ES04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                         72 |                                42 |                      31 |                               24 |            600 |
| S05     | PASS_A7FF53ES05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                           |                     150 |                              150 |                  3000 |                          9 |                                31 |                      22 |                               22 |            750 |
| S06     | HOLD_A7FF53ES06_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues   |                     150 |                              150 |                  3000 |                          0 |                                14 |                      11 |                               11 |            900 |
| S07     | HOLD_A7FF53ES07_NO_ACTIVITY_OK_BLUEPRINTS                | no_activity_ok_blueprints |                     150 |                                0 |                     0 |                          0 |                                 0 |                       0 |                                0 |           1050 |

## Decision Summary

| decision                              | label_family                       |   count |
|:--------------------------------------|:-----------------------------------|--------:|
| HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     542 |
| HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     542 |
| HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     534 |
| HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     520 |
| HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     509 |
| HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     508 |
| HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     508 |
| HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     507 |
| HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     497 |
| HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     485 |
| HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     467 |
| HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     466 |
| HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     464 |
| HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     460 |
| HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     460 |
| HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     457 |
| HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     457 |
| HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     453 |
| HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     453 |
| HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     447 |
| HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     427 |
| HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     400 |
| HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     400 |
| HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     400 |
| HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     400 |
| HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     398 |
| HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     398 |
| HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     381 |
| HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     381 |
| HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     370 |
| HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     309 |
| HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     289 |
| HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     289 |
| HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     286 |
| HOLD_A7FF53ES05_CONTROL_DOMINATED     | L7_ranked_future_return            |     286 |
| HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     281 |
| HOLD_A7FF53ES03_CONTROL_DOMINATED     | L7_ranked_future_return            |     254 |
| HOLD_A7FF53ES00_CONTROL_DOMINATED     | L7_ranked_future_return            |     239 |
| HOLD_A7FF53ES01_CONTROL_DOMINATED     | L7_ranked_future_return            |     238 |
| HOLD_A7FF53ES04_CONTROL_DOMINATED     | L7_ranked_future_return            |     234 |
| HOLD_A7FF53ES02_CONTROL_DOMINATED     | L7_ranked_future_return            |     198 |
| HOLD_A7FF53ES04_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     184 |
| HOLD_A7FF53ES00_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     183 |
| HOLD_A7FF53ES04_CONTROL_DOMINATED     | L0_raw_forward_return              |     166 |
| HOLD_A7FF53ES04_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     166 |
| HOLD_A7FF53ES00_CONTROL_DOMINATED     | L0_raw_forward_return              |     166 |
| HOLD_A7FF53ES00_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     159 |
| HOLD_A7FF53ES04_CONTROL_DOMINATED     | L5_vol_adjusted_return             |     156 |
| HOLD_A7FF53ES00_CONTROL_DOMINATED     | L5_vol_adjusted_return             |     155 |
| HOLD_A7FF53ES06_CONTROL_DOMINATED     | L7_ranked_future_return            |     154 |
| HOLD_A7FF53ES03_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     149 |
| HOLD_A7FF53ES03_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     143 |
| HOLD_A7FF53ES03_CONTROL_DOMINATED     | L0_raw_forward_return              |     142 |
| HOLD_A7FF53ES01_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     140 |
| HOLD_A7FF53ES01_CONTROL_DOMINATED     | L0_raw_forward_return              |     138 |
| HOLD_A7FF53ES05_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |     137 |
| HOLD_A7FF53ES05_CONTROL_DOMINATED     | L0_raw_forward_return              |     136 |
| HOLD_A7FF53ES06_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     133 |
| HOLD_A7FF53ES01_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     133 |
| HOLD_A7FF53ES05_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     128 |
| HOLD_A7FF53ES03_CONTROL_DOMINATED     | L5_vol_adjusted_return             |     109 |
| HOLD_A7FF53ES02_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |     102 |
| HOLD_A7FF53ES02_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      92 |
| HOLD_A7FF53ES02_CONTROL_DOMINATED     | L0_raw_forward_return              |      91 |
| HOLD_A7FF53ES02_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |      91 |
| HOLD_A7FF53ES01_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      87 |
| HOLD_A7FF53ES05_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      74 |
| HOLD_A7FF53ES06_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      65 |
| A7FF53ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      60 |
| HOLD_A7FF53ES06_CONTROL_DOMINATED     | L0_raw_forward_return              |      58 |
| HOLD_A7FF53ES06_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |      57 |
| A7FF53ES04_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      42 |
| A7FF53ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      40 |
| A7FF53ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      39 |
| HOLD_A7FF53ES04_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |      35 |
| HOLD_A7FF53ES00_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |      33 |
| A7FF53ES02_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      32 |
| A7FF53ES05_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      31 |
| A7FF53ES00_NUMERIC_CLUE               | L5_vol_adjusted_return             |      24 |
| A7FF53ES04_NUMERIC_CLUE               | L5_vol_adjusted_return             |      23 |

## Family Decision Summary

| semantic_pair                        | decision                              |   count |
|:-------------------------------------|:--------------------------------------|--------:|
| taker_flow_like|basis_premium_like   | HOLD_A7FF53ES06_PRE_MAY_UNSTABLE      |    2511 |
| open_interest_like|price_return_like | HOLD_A7FF53ES02_PRE_MAY_UNSTABLE      |    2390 |
| liquidity_like|price_return_like     | HOLD_A7FF53ES01_PRE_MAY_UNSTABLE      |    2196 |
| volatility_like|basis_premium_like   | HOLD_A7FF53ES05_PRE_MAY_UNSTABLE      |    2188 |
| positioning_like|price_return_like   | HOLD_A7FF53ES03_PRE_MAY_UNSTABLE      |    2124 |
| basis_premium_like|price_return_like | HOLD_A7FF53ES00_PRE_MAY_UNSTABLE      |    1868 |
| regime_state|price_return_like       | HOLD_A7FF53ES04_PRE_MAY_UNSTABLE      |    1868 |
| regime_state|price_return_like       | HOLD_A7FF53ES04_CONTROL_DOMINATED     |     906 |
| basis_premium_like|price_return_like | HOLD_A7FF53ES00_CONTROL_DOMINATED     |     902 |
| positioning_like|price_return_like   | HOLD_A7FF53ES03_CONTROL_DOMINATED     |     797 |
| volatility_like|basis_premium_like   | HOLD_A7FF53ES05_CONTROL_DOMINATED     |     761 |
| liquidity_like|price_return_like     | HOLD_A7FF53ES01_CONTROL_DOMINATED     |     736 |
| open_interest_like|price_return_like | HOLD_A7FF53ES02_CONTROL_DOMINATED     |     574 |
| taker_flow_like|basis_premium_like   | HOLD_A7FF53ES06_CONTROL_DOMINATED     |     467 |
| regime_state|price_return_like       | HOLD_A7FF53ES04_ONE_BAR_LAG_FRAGILE   |     102 |
| basis_premium_like|price_return_like | HOLD_A7FF53ES00_ONE_BAR_LAG_FRAGILE   |     102 |
| basis_premium_like|price_return_like | A7FF53ES00_NUMERIC_CLUE               |      77 |
| regime_state|price_return_like       | A7FF53ES04_NUMERIC_CLUE               |      72 |
| positioning_like|price_return_like   | A7FF53ES03_RANK_LABEL_DIAGNOSTIC_CLUE |      60 |
| regime_state|price_return_like       | A7FF53ES04_RANK_LABEL_DIAGNOSTIC_CLUE |      42 |
| liquidity_like|price_return_like     | A7FF53ES01_RANK_LABEL_DIAGNOSTIC_CLUE |      40 |
| basis_premium_like|price_return_like | A7FF53ES00_RANK_LABEL_DIAGNOSTIC_CLUE |      39 |
| open_interest_like|price_return_like | A7FF53ES02_RANK_LABEL_DIAGNOSTIC_CLUE |      32 |
| volatility_like|basis_premium_like   | A7FF53ES05_RANK_LABEL_DIAGNOSTIC_CLUE |      31 |
| liquidity_like|price_return_like     | HOLD_A7FF53ES01_ONE_BAR_LAG_FRAGILE   |      16 |
| positioning_like|price_return_like   | A7FF53ES03_NUMERIC_CLUE               |      15 |
| taker_flow_like|basis_premium_like   | A7FF53ES06_RANK_LABEL_DIAGNOSTIC_CLUE |      14 |
| basis_premium_like|price_return_like | HOLD_A7FF53ES00_COST2_PROXY_FRAGILE   |      12 |
| liquidity_like|price_return_like     | A7FF53ES01_NUMERIC_CLUE               |      10 |
| regime_state|price_return_like       | HOLD_A7FF53ES04_COST2_PROXY_FRAGILE   |      10 |
| volatility_like|basis_premium_like   | HOLD_A7FF53ES05_ONE_BAR_LAG_FRAGILE   |       9 |
| volatility_like|basis_premium_like   | A7FF53ES05_NUMERIC_CLUE               |       9 |
| taker_flow_like|basis_premium_like   | HOLD_A7FF53ES06_ONE_BAR_LAG_FRAGILE   |       8 |
| positioning_like|price_return_like   | HOLD_A7FF53ES03_ONE_BAR_LAG_FRAGILE   |       4 |
| open_interest_like|price_return_like | A7FF53ES02_NUMERIC_CLUE               |       3 |
| liquidity_like|price_return_like     | HOLD_A7FF53ES01_COST2_PROXY_FRAGILE   |       2 |
| volatility_like|basis_premium_like   | HOLD_A7FF53ES05_COST2_PROXY_FRAGILE   |       2 |
| open_interest_like|price_return_like | HOLD_A7FF53ES02_ONE_BAR_LAG_FRAGILE   |       1 |

## Selected Queue Summary

| semantic_pair                        | label_family            |   selected_count |
|:-------------------------------------|:------------------------|-----------------:|
| basis_premium_like|price_return_like | L5_vol_adjusted_return  |               20 |
| liquidity_like|price_return_like     | L7_ranked_future_return |               20 |
| regime_state|price_return_like       | L5_vol_adjusted_return  |               20 |
| open_interest_like|price_return_like | L7_ranked_future_return |               20 |
| positioning_like|price_return_like   | L7_ranked_future_return |               19 |
| volatility_like|basis_premium_like   | L7_ranked_future_return |               19 |
| taker_flow_like|basis_premium_like   | L7_ranked_future_return |               11 |
| positioning_like|price_return_like   | L5_vol_adjusted_return  |                5 |
| regime_state|price_return_like       | L7_ranked_future_return |                4 |
| basis_premium_like|price_return_like | L7_ranked_future_return |                4 |
| liquidity_like|price_return_like     | L5_vol_adjusted_return  |                3 |
| volatility_like|basis_premium_like   | L5_vol_adjusted_return  |                3 |

## Boundary

```text
numeric response executed: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
