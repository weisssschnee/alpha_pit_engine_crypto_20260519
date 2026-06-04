# CRYPTO A7FF-CORE59G QUEUE TARGET ATTRITION MAP

Generated: 2026-06-04T15:50:50Z

## Decision

`HOLD_CORE59G_QUEUE_COVERAGE_TOO_NARROW`

CORE59G maps attrition from queue to materialization, rank-label diagnostics, selected queue, and non-L7 clues. It does not search, replay, or promote candidates.

## Decision Record

```json
{
  "activity_ok_rate": 0.5391666666666667,
  "activity_ok_rows": 647,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "queue_non_l7_semantic_width_lt_4",
    "non_l7_top_semantic_pair_share_gt_0_8",
    "activity_ok_rate_lt_0_6"
  ],
  "decision": "HOLD_CORE59G_QUEUE_COVERAGE_TOO_NARROW",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T15:50:50Z",
  "label_response_rows": 12940,
  "non_l7_numeric_clue_rows": 6,
  "non_l7_semantic_pair_count": 2,
  "queue_rows": 1200,
  "rank_label_diagnostic_clue_rows": 341,
  "selected_portfolio_queue_rows": 44,
  "stage": "A7FF-CORE59G",
  "top_non_l7_semantic_share": 0.8333333333333334,
  "top_queue_semantic_share": 0.3,
  "top_selected_semantic_share": 0.29545454545454547
}
```

## Funnel By Semantic Pair

| semantic_pair                         |   queue_rows |   materialized_rows |   activity_ok_rows |   label_response_rows |   rank_label_clue_rows |   selected_rows |   non_l7_rows |   activity_ok_rate_vs_queue |   selected_rate_vs_rank_clue |   non_l7_rate_vs_selected |
|:--------------------------------------|-------------:|--------------------:|-------------------:|----------------------:|-----------------------:|----------------:|--------------:|----------------------------:|-----------------------------:|--------------------------:|
| basis_premium_like|funding_like       |          360 |                 360 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |
| basis_premium_like|price_like         |          282 |                 282 |                230 |                  4600 |                    172 |              13 |             5 |                    0.815603 |                    0.0755814 |                  0.384615 |
| basis_premium_like|volatility_like    |          213 |                 213 |                167 |                  3340 |                     65 |              10 |             1 |                    0.784038 |                    0.153846  |                  0.1      |
| basis_premium_like|basis_premium_like |          200 |                 200 |                132 |                  2640 |                     49 |               8 |             0 |                    0.66     |                    0.163265  |                  0        |
| price_like|volatility_like            |           51 |                  51 |                 43 |                   860 |                     28 |               3 |             0 |                    0.843137 |                    0.107143  |                  0        |
| basis_premium_like                    |           38 |                  38 |                 36 |                   720 |                      1 |               1 |             0 |                    0.947368 |                    1         |                  0        |
| volatility_like|volatility_like       |           26 |                  26 |                 22 |                   440 |                     11 |               4 |             0 |                    0.846154 |                    0.363636  |                  0        |
| volatility_like                       |           14 |                  14 |                 14 |                   280 |                      6 |               2 |             0 |                    1        |                    0.333333  |                  0        |
| funding_like|positioning_like         |           13 |                  13 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |
| price_like                            |            3 |                   3 |                  3 |                    60 |                      9 |               3 |             0 |                    1        |                    0.333333  |                  0        |

## Funnel By Motif

| motif               |   queue_rows |   materialized_rows |   activity_ok_rows |   label_response_rows |   rank_label_clue_rows |   selected_rows |   non_l7_rows |   activity_ok_rate_vs_queue |   selected_rate_vs_rank_clue |   non_l7_rate_vs_selected |
|:--------------------|-------------:|--------------------:|-------------------:|----------------------:|-----------------------:|----------------:|--------------:|----------------------------:|-----------------------------:|--------------------------:|
| smooth_mul          |          216 |                 216 |                167 |                  3340 |                     76 |              11 |             0 |                    0.773148 |                    0.144737  |                  0        |
| spread_rank         |          216 |                 216 |                166 |                  3320 |                    129 |              12 |             0 |                    0.768519 |                    0.0930233 |                  0        |
| relative_shock      |          216 |                 216 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |
| mean_reversion_gate |          144 |                 144 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |
| gated_sign          |          122 |                 122 |                 89 |                  1780 |                     50 |               4 |             0 |                    0.729508 |                    0.08      |                  0        |
| mul                 |          117 |                 117 |                 87 |                  1740 |                     59 |               9 |             2 |                    0.74359  |                    0.152542  |                  0.222222 |
| sub                 |           67 |                  67 |                 50 |                  1000 |                      5 |               1 |             1 |                    0.746269 |                    0.2       |                  1        |
| single              |           55 |                  55 |                 53 |                  1060 |                     16 |               6 |             0 |                    0.963636 |                    0.375     |                  0        |
| safe_div_abs        |           47 |                  47 |                 35 |                   700 |                      6 |               1 |             3 |                    0.744681 |                    0.166667  |                  3        |

## Funnel By Target

| label_family                       |   label_horizon_h | decision                            |   label_response_rows |
|:-----------------------------------|------------------:|:------------------------------------|----------------------:|
| L5_vol_adjusted_return             |                24 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   147 |
| L5_vol_adjusted_return             |                24 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   146 |
| L5_vol_adjusted_return             |                24 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   144 |
| L1_cross_sectional_relative_return |                 8 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   139 |
| L0_raw_forward_return              |                 8 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   139 |
| L5_vol_adjusted_return             |                 4 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   138 |
| L3_liquidity_tier_relative_return  |                 8 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   138 |
| L5_vol_adjusted_return             |                 8 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   137 |
| L0_raw_forward_return              |                 4 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   136 |
| L1_cross_sectional_relative_return |                 4 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   136 |
| L3_liquidity_tier_relative_return  |                 4 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   133 |
| L0_raw_forward_return              |                 8 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   132 |
| L1_cross_sectional_relative_return |                 8 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   132 |
| L1_cross_sectional_relative_return |                24 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   129 |
| L0_raw_forward_return              |                24 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   129 |
| L3_liquidity_tier_relative_return  |                 8 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   128 |
| L5_vol_adjusted_return             |                24 | HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE |                   128 |
| L3_liquidity_tier_relative_return  |                 8 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   128 |
| L0_raw_forward_return              |                24 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   126 |
| L3_liquidity_tier_relative_return  |                 4 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   126 |
| L1_cross_sectional_relative_return |                24 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   126 |
| L3_liquidity_tier_relative_return  |                24 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   126 |
| L0_raw_forward_return              |                24 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   125 |
| L1_cross_sectional_relative_return |                24 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   125 |
| L3_liquidity_tier_relative_return  |                 8 | HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE |                   125 |
| L5_vol_adjusted_return             |                 8 | HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE |                   124 |
| L1_cross_sectional_relative_return |                 4 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   123 |
| L0_raw_forward_return              |                 8 | HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE |                   123 |
| L5_vol_adjusted_return             |                 8 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   123 |
| L1_cross_sectional_relative_return |                 8 | HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE |                   123 |
| L0_raw_forward_return              |                 4 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   123 |
| L0_raw_forward_return              |                 4 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   123 |
| L1_cross_sectional_relative_return |                 4 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   123 |
| L3_liquidity_tier_relative_return  |                 1 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   122 |
| L5_vol_adjusted_return             |                 8 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   121 |
| L1_cross_sectional_relative_return |                 8 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   120 |
| L0_raw_forward_return              |                 8 | HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE |                   120 |
| L3_liquidity_tier_relative_return  |                24 | HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE |                   119 |
| L0_raw_forward_return              |                 1 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   119 |
| L1_cross_sectional_relative_return |                 1 | HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE |                   119 |

## Materialization Failure Map

| semantic_pair                         | motif               | materialization_status   |   rows |
|:--------------------------------------|:--------------------|:-------------------------|-------:|
| basis_premium_like|funding_like       | relative_shock      | inactive_or_sparse       |    216 |
| basis_premium_like|funding_like       | mean_reversion_gate | inactive_or_sparse       |    144 |
| basis_premium_like|price_like         | smooth_mul          | activity_ok              |     71 |
| basis_premium_like|volatility_like    | spread_rank         | activity_ok              |     58 |
| basis_premium_like|price_like         | spread_rank         | activity_ok              |     51 |
| basis_premium_like|basis_premium_like | smooth_mul          | activity_ok              |     51 |
| basis_premium_like                    | single              | activity_ok              |     36 |
| basis_premium_like|volatility_like    | gated_sign          | activity_ok              |     36 |
| basis_premium_like|volatility_like    | mul                 | activity_ok              |     35 |
| basis_premium_like|price_like         | gated_sign          | activity_ok              |     33 |
| basis_premium_like|price_like         | mul                 | activity_ok              |     29 |
| basis_premium_like|basis_premium_like | spread_rank         | activity_ok              |     29 |
| basis_premium_like|price_like         | sub                 | activity_ok              |     25 |
| basis_premium_like|price_like         | smooth_mul          | inactive_or_sparse       |     24 |
| basis_premium_like|volatility_like    | smooth_mul          | activity_ok              |     22 |
| basis_premium_like|price_like         | safe_div_abs        | activity_ok              |     21 |
| price_like|volatility_like            | spread_rank         | activity_ok              |     19 |
| basis_premium_like|basis_premium_like | mul                 | activity_ok              |     17 |
| basis_premium_like|basis_premium_like | spread_rank         | inactive_or_sparse       |     16 |
| basis_premium_like|volatility_like    | spread_rank         | inactive_or_sparse       |     16 |
| basis_premium_like|basis_premium_like | gated_sign          | activity_ok              |     15 |
| basis_premium_like|basis_premium_like | smooth_mul          | inactive_or_sparse       |     15 |
| price_like|volatility_like            | smooth_mul          | activity_ok              |     14 |
| volatility_like                       | single              | activity_ok              |     14 |
| basis_premium_like|basis_premium_like | sub                 | inactive_or_sparse       |     13 |
| basis_premium_like|volatility_like    | sub                 | activity_ok              |     13 |
| funding_like|positioning_like         | gated_sign          | inactive_or_sparse       |     13 |
| basis_premium_like|basis_premium_like | mul                 | inactive_or_sparse       |     12 |
| basis_premium_like|price_like         | spread_rank         | inactive_or_sparse       |     11 |
| basis_premium_like|volatility_like    | mul                 | inactive_or_sparse       |     11 |
| basis_premium_like|basis_premium_like | sub                 | activity_ok              |     10 |
| basis_premium_like|basis_premium_like | safe_div_abs        | activity_ok              |     10 |
| volatility_like|volatility_like       | smooth_mul          | activity_ok              |      9 |
| volatility_like|volatility_like       | spread_rank         | activity_ok              |      9 |
| basis_premium_like|volatility_like    | gated_sign          | inactive_or_sparse       |      8 |
| basis_premium_like|volatility_like    | smooth_mul          | inactive_or_sparse       |      7 |
| basis_premium_like|basis_premium_like | gated_sign          | inactive_or_sparse       |      7 |
| price_like|volatility_like            | spread_rank         | inactive_or_sparse       |      5 |
| basis_premium_like|price_like         | safe_div_abs        | inactive_or_sparse       |      5 |
| basis_premium_like|basis_premium_like | safe_div_abs        | inactive_or_sparse       |      5 |

## Selector Rejection / Survival Map

| selector_stage             | semantic_pair                         | motif        | label_family                       |   rows |
|:---------------------------|:--------------------------------------|:-------------|:-----------------------------------|-------:|
| rank_label_diagnostic_clue | basis_premium_like|price_like         | spread_rank  | L7_ranked_future_return            |     65 |
| rank_label_diagnostic_clue | basis_premium_like|volatility_like    | spread_rank  | L7_ranked_future_return            |     50 |
| rank_label_diagnostic_clue | basis_premium_like|price_like         | mul          | L7_ranked_future_return            |     43 |
| rank_label_diagnostic_clue | basis_premium_like|price_like         | gated_sign   | L7_ranked_future_return            |     33 |
| rank_label_diagnostic_clue | basis_premium_like|price_like         | smooth_mul   | L7_ranked_future_return            |     27 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | smooth_mul   | L7_ranked_future_return            |     20 |
| rank_label_diagnostic_clue | price_like|volatility_like            | smooth_mul   | L7_ranked_future_return            |     17 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | spread_rank  | L7_ranked_future_return            |     14 |
| rank_label_diagnostic_clue | price_like                            | single       | L7_ranked_future_return            |      9 |
| rank_label_diagnostic_clue | price_like|volatility_like            | gated_sign   | L7_ranked_future_return            |      8 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | mul          | L7_ranked_future_return            |      6 |
| selected_portfolio_queue   | basis_premium_like|volatility_like    | spread_rank  | L7_ranked_future_return            |      6 |
| rank_label_diagnostic_clue | volatility_like|volatility_like       | smooth_mul   | L7_ranked_future_return            |      6 |
| rank_label_diagnostic_clue | volatility_like                       | single       | L7_ranked_future_return            |      6 |
| rank_label_diagnostic_clue | basis_premium_like|volatility_like    | smooth_mul   | L7_ranked_future_return            |      6 |
| rank_label_diagnostic_clue | basis_premium_like|volatility_like    | gated_sign   | L7_ranked_future_return            |      6 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | sub          | L7_ranked_future_return            |      5 |
| rank_label_diagnostic_clue | basis_premium_like|price_like         | safe_div_abs | L7_ranked_future_return            |      4 |
| selected_portfolio_queue   | basis_premium_like|price_like         | mul          | L7_ranked_future_return            |      4 |
| rank_label_diagnostic_clue | volatility_like|volatility_like       | mul          | L7_ranked_future_return            |      4 |
| selected_portfolio_queue   | basis_premium_like|price_like         | spread_rank  | L7_ranked_future_return            |      4 |
| rank_label_diagnostic_clue | basis_premium_like|volatility_like    | mul          | L7_ranked_future_return            |      3 |
| selected_portfolio_queue   | basis_premium_like|basis_premium_like | smooth_mul   | L7_ranked_future_return            |      3 |
| selected_portfolio_queue   | basis_premium_like|price_like         | smooth_mul   | L7_ranked_future_return            |      3 |
| rank_label_diagnostic_clue | price_like|volatility_like            | mul          | L7_ranked_future_return            |      3 |
| selected_portfolio_queue   | price_like                            | single       | L7_ranked_future_return            |      3 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | safe_div_abs | L7_ranked_future_return            |      2 |
| selected_portfolio_queue   | basis_premium_like|basis_premium_like | mul          | L7_ranked_future_return            |      2 |
| selected_portfolio_queue   | basis_premium_like|volatility_like    | smooth_mul   | L7_ranked_future_return            |      2 |
| selected_portfolio_queue   | volatility_like                       | single       | L7_ranked_future_return            |      2 |
| selected_portfolio_queue   | volatility_like|volatility_like       | smooth_mul   | L7_ranked_future_return            |      2 |
| rank_label_diagnostic_clue | basis_premium_like|basis_premium_like | gated_sign   | L7_ranked_future_return            |      2 |
| non_l7_numeric_clue        | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return             |      2 |
| selected_portfolio_queue   | basis_premium_like|basis_premium_like | spread_rank  | L7_ranked_future_return            |      2 |
| non_l7_numeric_clue        | basis_premium_like|price_like         | mul          | L1_cross_sectional_relative_return |      1 |
| non_l7_numeric_clue        | basis_premium_like|price_like         | sub          | L3_liquidity_tier_relative_return  |      1 |
| rank_label_diagnostic_clue | basis_premium_like                    | single       | L7_ranked_future_return            |      1 |
| non_l7_numeric_clue        | basis_premium_like|volatility_like    | mul          | L0_raw_forward_return              |      1 |
| non_l7_numeric_clue        | basis_premium_like|price_like         | safe_div_abs | L0_raw_forward_return              |      1 |
| selected_portfolio_queue   | basis_premium_like|price_like         | gated_sign   | L7_ranked_future_return            |      1 |

## Non-L7 Loss Map

| semantic_pair                         |   queue_rows |   materialized_rows |   activity_ok_rows |   label_response_rows |   rank_label_clue_rows |   selected_rows |   non_l7_rows |   activity_ok_rate_vs_queue |   selected_rate_vs_rank_clue |   non_l7_rate_vs_selected |   rank_to_non_l7_loss_rows |   selected_to_non_l7_loss_rows |
|:--------------------------------------|-------------:|--------------------:|-------------------:|----------------------:|-----------------------:|----------------:|--------------:|----------------------------:|-----------------------------:|--------------------------:|---------------------------:|-------------------------------:|
| basis_premium_like|price_like         |          282 |                 282 |                230 |                  4600 |                    172 |              13 |             5 |                    0.815603 |                    0.0755814 |                  0.384615 |                        167 |                              8 |
| basis_premium_like|volatility_like    |          213 |                 213 |                167 |                  3340 |                     65 |              10 |             1 |                    0.784038 |                    0.153846  |                  0.1      |                         64 |                              9 |
| basis_premium_like|basis_premium_like |          200 |                 200 |                132 |                  2640 |                     49 |               8 |             0 |                    0.66     |                    0.163265  |                  0        |                         49 |                              8 |
| price_like|volatility_like            |           51 |                  51 |                 43 |                   860 |                     28 |               3 |             0 |                    0.843137 |                    0.107143  |                  0        |                         28 |                              3 |
| volatility_like|volatility_like       |           26 |                  26 |                 22 |                   440 |                     11 |               4 |             0 |                    0.846154 |                    0.363636  |                  0        |                         11 |                              4 |
| price_like                            |            3 |                   3 |                  3 |                    60 |                      9 |               3 |             0 |                    1        |                    0.333333  |                  0        |                          9 |                              3 |
| volatility_like                       |           14 |                  14 |                 14 |                   280 |                      6 |               2 |             0 |                    1        |                    0.333333  |                  0        |                          6 |                              2 |
| basis_premium_like                    |           38 |                  38 |                 36 |                   720 |                      1 |               1 |             0 |                    0.947368 |                    1         |                  0        |                          1 |                              1 |
| basis_premium_like|funding_like       |          360 |                 360 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |                          0 |                              0 |
| funding_like|positioning_like         |           13 |                  13 |                  0 |                     0 |                      0 |               0 |             0 |                    0        |                  nan         |                nan        |                          0 |                              0 |
