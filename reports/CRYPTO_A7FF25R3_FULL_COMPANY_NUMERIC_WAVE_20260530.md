# CRYPTO A7FF-25R3 FULL COMPANY NUMERIC WAVE

Generated: 2026-05-30T08:45:09Z

## Decision

`PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_WITH_WARNINGS_NO_SEARCH_AUTH`

A7FF-25R3 aggregates the 12 company-machine numeric shards from the A7FF-24R company wave queue. It is numeric response probing only: no generation, replay, search, alpha proof, shadow, paper, or live execution is authorized.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "completed_shards": 12,
  "decision": "PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_WITH_WARNINGS_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:45:09Z",
  "input_blueprint_count": 2400,
  "label_response_rows": 25980,
  "materialized_activity_ok_count": 1299,
  "no_activity_shards": [
    "08",
    "09",
    "10",
    "11"
  ],
  "non_l7_numeric_clue_rows": 387,
  "portfolio_queue_count": 465,
  "rank_label_diagnostic_clue_rows": 770,
  "selected_portfolio_queue_count": 71,
  "selected_top_semantic_pair": "basis_premium_like|price_like",
  "selected_top_semantic_pair_share": 0.09859154929577464,
  "shard_count": 12,
  "stage": "A7FF-25R3",
  "uses_may": false,
  "warnings": [
    "no_activity_shards_present",
    "rank_label_diagnostic_rows_exceed_non_l7"
  ]
}
```

## Shard Summary

|   shard | manifest_exists   |   exit_code | decision                                                  | normalized_decision                                    |   input_blueprint_count |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | uses_may   |
|--------:|:------------------|------------:|:----------------------------------------------------------|:-------------------------------------------------------|------------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:-----------|
|      00 | True              |           0 | PASS_A7FF25R3S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              157 |                  3140 |                         77 |                                56 |                      46 |                                8 | False      |
|      01 | True              |           0 | PASS_A7FF25R3S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              149 |                  2980 |                         31 |                                60 |                      45 |                                9 | False      |
|      02 | True              |           0 | PASS_A7FF25R3S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              167 |                  3340 |                         89 |                               158 |                      91 |                                7 | False      |
|      03 | True              |           0 | PASS_A7FF25R3S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              156 |                  3120 |                          8 |                                94 |                      48 |                                9 | False      |
|      04 | True              |           0 | PASS_A7FF25R3S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              166 |                  3320 |                         98 |                               112 |                      71 |                                8 | False      |
|      05 | True              |           0 | PASS_A7FF25R3S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              169 |                  3380 |                         49 |                                31 |                      43 |                                7 | False      |
|      06 | True              |           0 | PASS_A7FF25R3S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              165 |                  3300 |                         10 |                               155 |                      67 |                               13 | False      |
|      07 | True              |           0 | PASS_A7FF25R3S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH | PASS_A7FF25R3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                     200 |                              170 |                  3400 |                         25 |                               104 |                      54 |                               10 | False      |
|      08 | True              |           0 | HOLD_A7FF25R3S08_NO_ACTIVITY_OK_BLUEPRINTS                | HOLD_A7FF25R3_NO_ACTIVITY_OK_BLUEPRINTS                |                     200 |                                0 |                     0 |                          0 |                                 0 |                       0 |                                0 | False      |
|      09 | True              |           0 | HOLD_A7FF25R3S09_NO_ACTIVITY_OK_BLUEPRINTS                | HOLD_A7FF25R3_NO_ACTIVITY_OK_BLUEPRINTS                |                     200 |                                0 |                     0 |                          0 |                                 0 |                       0 |                                0 | False      |
|      10 | True              |           0 | HOLD_A7FF25R3S10_NO_ACTIVITY_OK_BLUEPRINTS                | HOLD_A7FF25R3_NO_ACTIVITY_OK_BLUEPRINTS                |                     200 |                                0 |                     0 |                          0 |                                 0 |                       0 |                                0 | False      |
|      11 | True              |           0 | HOLD_A7FF25R3S11_NO_ACTIVITY_OK_BLUEPRINTS                | HOLD_A7FF25R3_NO_ACTIVITY_OK_BLUEPRINTS                |                     200 |                                0 |                     0 |                          0 |                                 0 |                       0 |                                0 | False      |

## Decision Counts

| normalized_decision                 | label_family                       |   count |
|:------------------------------------|:-----------------------------------|--------:|
| A7FF25R3_NUMERIC_CLUE               | L0_raw_forward_return              |      89 |
| A7FF25R3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |      90 |
| A7FF25R3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |      99 |
| A7FF25R3_NUMERIC_CLUE               | L5_vol_adjusted_return             |     109 |
| A7FF25R3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |     770 |
| HOLD_A7FF25R3_CONTROL_DOMINATED     | L0_raw_forward_return              |    1258 |
| HOLD_A7FF25R3_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |    1257 |
| HOLD_A7FF25R3_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |    1280 |
| HOLD_A7FF25R3_CONTROL_DOMINATED     | L5_vol_adjusted_return             |    1122 |
| HOLD_A7FF25R3_CONTROL_DOMINATED     | L7_ranked_future_return            |    2091 |
| HOLD_A7FF25R3_COST2_PROXY_FRAGILE   | L0_raw_forward_return              |       8 |
| HOLD_A7FF25R3_COST2_PROXY_FRAGILE   | L1_cross_sectional_relative_return |       9 |
| HOLD_A7FF25R3_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |      14 |
| HOLD_A7FF25R3_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |      85 |
| HOLD_A7FF25R3_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |      84 |
| HOLD_A7FF25R3_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |      96 |
| HOLD_A7FF25R3_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |     146 |
| HOLD_A7FF25R3_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |     279 |
| HOLD_A7FF25R3_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |    3756 |
| HOLD_A7FF25R3_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |    3756 |
| HOLD_A7FF25R3_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |    3707 |
| HOLD_A7FF25R3_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |    3819 |
| HOLD_A7FF25R3_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |    2056 |

## Selected Family Summary

| semantic_pair                         | motif        |   selected_count |
|:--------------------------------------|:-------------|-----------------:|
| basis_premium_like|price_like         | spread_rank  |                7 |
| basis_premium_like|basis_premium_like | spread_rank  |                6 |
| price_like|volatility_like            | smooth_mul   |                6 |
| basis_premium_like|volatility_like    | spread_rank  |                5 |
| basis_premium_like|price_like         | smooth_mul   |                5 |
| basis_premium_like|price_like         | safe_div_abs |                5 |
| basis_premium_like|volatility_like    | smooth_mul   |                4 |
| price_like                            | single       |                4 |
| basis_premium_like|basis_premium_like | sub          |                3 |
| basis_premium_like|basis_premium_like | smooth_mul   |                3 |
| price_like|volatility_like            | gated_sign   |                2 |
| volatility_like|volatility_like       | smooth_mul   |                2 |
| basis_premium_like|volatility_like    | safe_div_abs |                2 |
| basis_premium_like|price_like         | mul          |                2 |
| basis_premium_like|basis_premium_like | safe_div_abs |                2 |
| basis_premium_like|basis_premium_like | mul          |                2 |
| basis_premium_like|volatility_like    | gated_sign   |                2 |
| basis_premium_like                    | single       |                1 |
| basis_premium_like|price_like         | gated_sign   |                1 |
| basis_premium_like|basis_premium_like | gated_sign   |                1 |
| basis_premium_like|volatility_like    | mul          |                1 |
| basis_premium_like|price_like         | sub          |                1 |
| price_like|volatility_like            | mul          |                1 |
| volatility_like                       | single       |                1 |
| volatility_like|volatility_like       | gated_sign   |                1 |
| volatility_like|volatility_like       | mul          |                1 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.90493  |     13223.1 |  77940 |
| same_family_placebo  |       0.328485 |     11574.1 |  77940 |
| sign_flip            |       0.995368 |     16784   |  77940 |
| symbol_shuffle       |       0.468886 |     16176   |  77940 |
| time_shuffle         |       0.439678 |     31682   |  77940 |
| wrong_lag_future_24h |       1.604    |     76657   |  77940 |
| wrong_lag_stale_168h |       0.573463 |    110323   |  77940 |

## Materialization Dropoff

|   shard |   rows |   eval_success |   activity_ok |   finite_share_median |   nonzero_share_median |
|--------:|-------:|---------------:|--------------:|----------------------:|-----------------------:|
|      00 |    200 |            200 |           157 |           0.995978    |               0.9683   |
|      01 |    200 |            200 |           149 |           0.996553    |               0.969214 |
|      02 |    200 |            200 |           167 |           0.995978    |               0.957877 |
|      03 |    200 |            200 |           156 |           0.99368     |               0.999365 |
|      04 |    200 |            200 |           166 |           0.827205    |               0.9881   |
|      05 |    200 |            200 |           169 |           0.825338    |               0.987078 |
|      06 |    200 |            200 |           165 |           0.825338    |               0.989502 |
|      07 |    200 |            200 |           170 |           0.827205    |               0.999309 |
|      08 |    200 |            200 |             0 |           0.000670305 |               1        |
|      09 |    200 |            200 |             0 |           0.000670305 |               1        |
|      10 |    200 |            200 |             0 |           0.000646366 |               0        |
|      11 |    200 |            200 |             0 |           0.00326475  |               0.959071 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
L7 ranked-return rows are diagnostic-only.
This stage does not authorize A7FF formula search, large search, alpha proof, shadow, paper, or live execution.
No-activity shards must be handled before treating the company queue as uniformly healthy.
```
