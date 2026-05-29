# CRYPTO A7FF-8 EXPANDED NUMERIC PROBE

Generated: 2026-05-29T17:08:24Z

## Decision

`PASS_A7FF8_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-8 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF8_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T17:08:24Z",
  "input_blueprint_count": 64,
  "label_response_rows": 1280,
  "materialized_activity_ok_count": 64,
  "non_l7_numeric_clue_rows": 65,
  "plan": {
    "control_probe_cap": 256,
    "controls": [
      "wrong_lag_future",
      "wrong_lag_stale",
      "time_shuffle",
      "symbol_shuffle",
      "sign_flip",
      "same_family_placebo"
    ],
    "deep_audit_cap": 64,
    "fast_numeric_probe_cap": 256,
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return_diagnostic_only"
    ],
    "materialize_cap": 384,
    "portfolio_marginal_probe_cap": 128,
    "promotion_blockers": [
      "L7-only cannot promote",
      "control_ratio >= 1.0 blocks",
      "single semantic_pair > 35pct blocks",
      "single skeleton > 15pct blocks",
      "numeric replay required before any search authorization"
    ],
    "required_outputs": [
      "a7ff8_materialization_metrics.csv",
      "a7ff8_label_response_metrics.csv",
      "a7ff8_control_dominance_metrics.csv",
      "a7ff8_nonoverlap_stats.csv",
      "a7ff8_portfolio_marginal_proxy.csv",
      "a7ff8_decision_record.json"
    ],
    "selected_blueprints": 384,
    "stage": "A7FF-8",
    "status": "contract_only_not_executed"
  },
  "portfolio_queue_count": 14,
  "rank_label_diagnostic_clue_rows": 12,
  "selected_portfolio_queue_count": 6,
  "stage": "A7FF-8",
  "uses_may": false
}
```

## Decision Counts

| decision                         | label_family                       |   count |
|:---------------------------------|:-----------------------------------|--------:|
| A7FF8_NUMERIC_CLUE               | L0_raw_forward_return              |      18 |
| A7FF8_NUMERIC_CLUE               | L1_cross_sectional_relative_return |      19 |
| A7FF8_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |      16 |
| A7FF8_NUMERIC_CLUE               | L5_vol_adjusted_return             |      12 |
| A7FF8_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      12 |
| HOLD_A7FF8_CONTROL_DOMINATED     | L0_raw_forward_return              |      58 |
| HOLD_A7FF8_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |      57 |
| HOLD_A7FF8_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |      45 |
| HOLD_A7FF8_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      58 |
| HOLD_A7FF8_CONTROL_DOMINATED     | L7_ranked_future_return            |      39 |
| HOLD_A7FF8_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |       3 |
| HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |       6 |
| HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |       6 |
| HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |       6 |
| HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |      21 |
| HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |      36 |
| HOLD_A7FF8_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |     174 |
| HOLD_A7FF8_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |     174 |
| HOLD_A7FF8_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |     186 |
| HOLD_A7FF8_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |     165 |
| HOLD_A7FF8_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |     169 |

## Family Summary

| semantic_pair                        | decision                         |   count |
|:-------------------------------------|:---------------------------------|--------:|
| basis_premium_like                   | A7FF8_NUMERIC_CLUE               |      27 |
| basis_premium_like                   | A7FF8_RANK_LABEL_DIAGNOSTIC_CLUE |       6 |
| basis_premium_like                   | HOLD_A7FF8_CONTROL_DOMINATED     |     101 |
| basis_premium_like                   | HOLD_A7FF8_COST2_PROXY_FRAGILE   |       1 |
| basis_premium_like                   | HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   |      35 |
| basis_premium_like                   | HOLD_A7FF8_PRE_MAY_UNSTABLE      |     130 |
| basis_premium_like\|positioning_like | A7FF8_NUMERIC_CLUE               |      38 |
| basis_premium_like\|positioning_like | A7FF8_RANK_LABEL_DIAGNOSTIC_CLUE |       6 |
| basis_premium_like\|positioning_like | HOLD_A7FF8_CONTROL_DOMINATED     |     156 |
| basis_premium_like\|positioning_like | HOLD_A7FF8_COST2_PROXY_FRAGILE   |       2 |
| basis_premium_like\|positioning_like | HOLD_A7FF8_ONE_BAR_LAG_FRAGILE   |      40 |
| basis_premium_like\|positioning_like | HOLD_A7FF8_PRE_MAY_UNSTABLE      |     738 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.822272 |    1800.55  |   3840 |
| same_family_placebo  |       0.461281 |    1330.02  |   3840 |
| sign_flip            |       1.00151  |     904.236 |   3840 |
| symbol_shuffle       |       0.512818 |    1441.15  |   3840 |
| time_shuffle         |       0.565478 |    1797.73  |   3840 |
| wrong_lag_future_24h |       1.01987  |    2890.14  |   3840 |
| wrong_lag_stale_168h |       0.692244 |    3228.77  |   3840 |

## Selected Portfolio Queue

| blueprint_id            | expression                                                                                             | semantic_pair                        | motif      | label_family           |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision           |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:------------------------|:-------------------------------------------------------------------------------------------------------|:-------------------------------------|:-----------|:-----------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff7e_454b18e00e63d958 | Delta(mark_index_basis_bps,12)                                                                         | basis_premium_like                   | single     | L5_vol_adjusted_return |                 8 |                       -1 |                             3 | True                  |                   0.790958 |                    0.247474   | True     |                    0.626901 |                  2.32574 | True        |             0.389848    |             0.389248    |               0.388248   |            94.9333 | A7FF8_NUMERIC_CLUE |            700 |             -0.0150161   |          -0.519622 |                            -0.175288 |                          -1.6345  |                   0.48     |                   712 |                    -0.0557262   |                  -2.01878 |                                   -0.626901 |                                 -2.52672 |                          0.441011 |             712 |              -0.137832    |            -3.26193 |                             -1.32965  |                           -2.32574 |                    0.450843 |                       712 |                        -0.390248    |                      -5.50726 |                                        -2.33334 |                                     -3.27856 |                              0.411517 |              1 |      395.457   | skel_1d39996e97d5ace0 |       0.996265 |        0.998429 |
| a7ff7e_303a085bd066346e | Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(taker_buy_sell_volume_ratio_last)))                     | basis_premium_like\|positioning_like | gated_sign | L5_vol_adjusted_return |                 4 |                       -1 |                             3 | True                  |                   0.394847 |                    0.139179   | True     |                    0.852616 |                  2.30347 | True        |             0.273511    |             0.272911    |               0.271911   |            95.4667 | A7FF8_NUMERIC_CLUE |            704 |             -0.015268    |          -0.734626 |                            -0.245353 |                          -1.15187 |                   0.482955 |                   716 |                    -0.0499446   |                  -2.69997 |                                   -0.852616 |                                 -3.05516 |                          0.460894 |             716 |              -0.0966462   |            -3.17183 |                             -1.54387  |                           -2.30347 |                    0.409218 |                       716 |                        -0.273911    |                      -6.03295 |                                        -3.13937 |                                     -3.60932 |                              0.412011 |              1 |      279.517   | skel_069f2015163fa7ef |       0.996265 |        0.998429 |
| a7ff7e_523ba2cd18730994 | Mul(Delta(mark_index_basis_bps,1),Sign(taker_buy_sell_volume_ratio_last))                              | basis_premium_like\|positioning_like | gated_sign | L5_vol_adjusted_return |                 8 |                       -1 |                             3 | True                  |                   0.698578 |                    0.102063   | True     |                    0.661427 |                  2.25692 | True        |             0.184125    |             0.183525    |               0.182525   |            94.9333 | A7FF8_NUMERIC_CLUE |            711 |             -0.0343349   |          -1.29648  |                            -0.288675 |                          -1.70393 |                   0.493671 |                   712 |                    -0.0879959   |                  -2.93251 |                                   -1.11599  |                                 -3.0681  |                          0.441011 |             712 |              -0.0926889   |            -2.41976 |                             -0.661427 |                           -2.73689 |                    0.433989 |                       712 |                        -0.184525    |                      -2.94565 |                                        -1.20638 |                                     -2.25692 |                              0.464888 |              1 |      189.826   | skel_136259b72205469f |       0.999425 |        0.998174 |
| a7ff7e_1c9b88500c7ca5ac | Mul(Delta(mark_index_basis_bps,4),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)))           | basis_premium_like\|positioning_like | gated_sign | L5_vol_adjusted_return |                 1 |                        1 |                             3 | True                  |                   0.571028 |                    0.00963756 | True     |                    1.77077  |                  1.77077 | True        |             0.0345009   |             0.0339009   |               0.0329009  |            95.8667 | A7FF8_NUMERIC_CLUE |            715 |              0.0114671   |           1.22556  |                             1.22556  |                           1.22556 |                   0.532867 |                   719 |                     0.028274    |                   2.84679 |                                    2.84679  |                                  2.84679 |                          0.552156 |             719 |               0.0472673   |             3.47013 |                              3.47013  |                            3.47013 |                    0.568846 |                       719 |                         0.0349009   |                       1.77077 |                                         1.77077 |                                      1.77077 |                              0.529903 |              1 |       40.3298  | skel_6a3533b4d89c4d45 |       0.998564 |        0.998361 |
| a7ff7e_09c74d60d25a4769 | Mul(ZScore(mark_index_basis_bps),Sign(ZScore(taker_buy_sell_volume_ratio_last)))                       | basis_premium_like\|positioning_like | gated_sign | L0_raw_forward_return  |                 1 |                        1 |                             3 | True                  |                   0.968969 |                    0.00020996 | True     |                    2.50178  |                  2.50178 | True        |             0.000439334 |            -0.000160666 |              -0.00116067 |            95.8667 | A7FF8_NUMERIC_CLUE |            719 |              0.000192732 |           1.14862  |                             1.14862  |                           1.14862 |                   0.520167 |                   719 |                     0.000264471 |                   2.50178 |                                    2.50178  |                                  2.50178 |                          0.55911  |             719 |               0.000421004 |             2.70772 |                              2.70772  |                            2.70772 |                    0.571627 |                       719 |                         0.000839334 |                       2.7539  |                                         2.7539  |                                      2.7539  |                              0.506259 |              1 |        6.03103 | skel_897201905b87a210 |       0.999713 |        1        |
| a7ff7e_3de5984ae7a1281a | Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))) | basis_premium_like\|positioning_like | gated_sign | L0_raw_forward_return  |                 1 |                        1 |                             3 | True                  |                   0.968969 |                    0.00020996 | True     |                    2.50178  |                  2.50178 | True        |             0.000439334 |            -0.000160666 |              -0.00116067 |            95.8667 | A7FF8_NUMERIC_CLUE |            719 |              0.000192732 |           1.14862  |                             1.14862  |                           1.14862 |                   0.520167 |                   719 |                     0.000264471 |                   2.50178 |                                    2.50178  |                                  2.50178 |                          0.55911  |             719 |               0.000421004 |             2.70772 |                              2.70772  |                            2.70772 |                    0.571627 |                       719 |                         0.000839334 |                       2.7539  |                                         2.7539  |                                      2.7539  |                              0.506259 |              1 |        6.03103 | skel_f5a350b26e95f33f |       0.999713 |        1        |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
