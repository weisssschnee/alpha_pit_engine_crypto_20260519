# CRYPTO A7FF-37A EXPANDED NUMERIC PROBE

Generated: 2026-05-30T11:55:04Z

## Decision

`PASS_A7FF37A_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-37A materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF37A_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:55:04Z",
  "input_blueprint_count": 4,
  "label_response_rows": 80,
  "materialized_activity_ok_count": 4,
  "non_l7_numeric_clue_rows": 19,
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
  "portfolio_queue_count": 4,
  "queue_limit": 4,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff37_deep_replay_contract\\a7ff37_deep_replay_queue.csv",
  "queue_total_rows": 4,
  "rank_label_diagnostic_clue_rows": 5,
  "selected_portfolio_queue_count": 4,
  "stage": "A7FF-37A",
  "uses_may": false
}
```

## Decision Counts

| decision                           | label_family                       |   count |
|:-----------------------------------|:-----------------------------------|--------:|
| A7FF37A_NUMERIC_CLUE               | L0_raw_forward_return              |       5 |
| A7FF37A_NUMERIC_CLUE               | L1_cross_sectional_relative_return |       6 |
| A7FF37A_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |       4 |
| A7FF37A_NUMERIC_CLUE               | L5_vol_adjusted_return             |       4 |
| A7FF37A_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |       5 |
| HOLD_A7FF37A_CONTROL_DOMINATED     | L0_raw_forward_return              |       5 |
| HOLD_A7FF37A_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |       4 |
| HOLD_A7FF37A_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |       6 |
| HOLD_A7FF37A_CONTROL_DOMINATED     | L5_vol_adjusted_return             |       6 |
| HOLD_A7FF37A_CONTROL_DOMINATED     | L7_ranked_future_return            |       2 |
| HOLD_A7FF37A_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |       1 |
| HOLD_A7FF37A_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |       2 |
| HOLD_A7FF37A_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |       4 |
| HOLD_A7FF37A_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |       6 |
| HOLD_A7FF37A_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |       6 |
| HOLD_A7FF37A_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |       5 |
| HOLD_A7FF37A_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |       4 |
| HOLD_A7FF37A_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |       5 |

## Family Summary

| semantic_pair                         | decision                           |   count |
|:--------------------------------------|:-----------------------------------|--------:|
| basis_premium_like|basis_premium_like | A7FF37A_NUMERIC_CLUE               |       3 |
| basis_premium_like|basis_premium_like | A7FF37A_RANK_LABEL_DIAGNOSTIC_CLUE |       1 |
| basis_premium_like|basis_premium_like | HOLD_A7FF37A_CONTROL_DOMINATED     |       3 |
| basis_premium_like|basis_premium_like | HOLD_A7FF37A_ONE_BAR_LAG_FRAGILE   |       2 |
| basis_premium_like|basis_premium_like | HOLD_A7FF37A_PRE_MAY_UNSTABLE      |      11 |
| funding_like|basis_premium_like       | A7FF37A_NUMERIC_CLUE               |      14 |
| funding_like|basis_premium_like       | A7FF37A_RANK_LABEL_DIAGNOSTIC_CLUE |       1 |
| funding_like|basis_premium_like       | HOLD_A7FF37A_CONTROL_DOMINATED     |       6 |
| funding_like|basis_premium_like       | HOLD_A7FF37A_ONE_BAR_LAG_FRAGILE   |       4 |
| funding_like|basis_premium_like       | HOLD_A7FF37A_PRE_MAY_UNSTABLE      |      15 |
| regime_state|price_return_like        | A7FF37A_NUMERIC_CLUE               |       2 |
| regime_state|price_return_like        | A7FF37A_RANK_LABEL_DIAGNOSTIC_CLUE |       3 |
| regime_state|price_return_like        | HOLD_A7FF37A_CONTROL_DOMINATED     |      14 |
| regime_state|price_return_like        | HOLD_A7FF37A_COST2_PROXY_FRAGILE   |       1 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.457887 |    10.0505  |    240 |
| same_family_placebo  |       0.167718 |     5.01952 |    240 |
| sign_flip            |       0.980721 |     1.36598 |    240 |
| symbol_shuffle       |       0.175711 |    14.3043  |    240 |
| time_shuffle         |       0.227309 |    10.5295  |    240 |
| wrong_lag_future_24h |       0.420595 |    54.6682  |    240 |
| wrong_lag_stale_168h |       0.266062 |    18.2471  |    240 |

## Selected Portfolio Queue

| blueprint_id            | expression                                                                  | semantic_pair                         | motif         | label_family            |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                           |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:------------------------|:----------------------------------------------------------------------------|:--------------------------------------|:--------------|:------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff33_c8b780256ff30837 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,1))         | funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return  |                 8 |                        1 |                             3 | True                  |                   0.623967 |                    0.0605104  | True     |                    0.954081 |                -0.59559  | True        |               0.138825  |               0.138225  |                0.137225  |            178.989 | A7FF37A_NUMERIC_CLUE               |            711 |               0.0176095  |           0.753341 |                             0.538959 |                          -1.56002 |                   0.518987 |                   712 |                       0.0611987 |                  2.61871  |                                    0.954081 |                                -0.165524 |                          0.563202 |             712 |                 0.0774342 |             2.80333 |                               1.01277 |                           -0.59559 |                    0.563202 |                       712 |                           0.139225  |                       3.33142 |                                         1.02992 |                                     0.305286 |                              0.546348 |              1 |       144.601  | skel_f8484b844efd270f |       0.82778  |        0.999996 |
| a7ff33_0c0da14842542e13 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(mark_index_basis_bps))  | funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.316668 |                    0.0324719  | True     |                    6.48799  |                 6.48799  | True        |               0.114627  |               0.114027  |                0.113027  |            180.749 | A7FF37A_NUMERIC_CLUE               |            719 |               0.0186135  |           2.08386  |                             2.08386  |                           2.08386 |                   0.522949 |                   719 |                       0.0597057 |                  6.48799  |                                    6.48799  |                                 6.48799  |                          0.611961 |             719 |                 0.0823185 |             7.66861 |                               7.66861 |                            7.66861 |                    0.652295 |                       719 |                           0.115027  |                       7.97118 |                                         7.97118 |                                     7.97118  |                              0.613352 |              1 |       120.711  | skel_293cae94cfd91548 |       0.828067 |        1        |
| a7ff33_fe3e0c6a7b32a1d7 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1)))         | regime_state|price_return_like        | spread_rank   | L5_vol_adjusted_return  |                 1 |                        1 |                             3 | True                  |                   0.864797 |                    0.0316268  | True     |                    0.860207 |                 0.860207 | True        |               0.0469772 |               0.0463772 |                0.0453772 |            180.749 | A7FF37A_NUMERIC_CLUE               |            718 |               0.0291984  |           2.14455  |                             2.14455  |                           2.14455 |                   0.56546  |                   719 |                       0.0110419 |                  0.860207 |                                    0.860207 |                                 0.860207 |                          0.54242  |             719 |                 0.030168  |             2.09118 |                               2.09118 |                            2.09118 |                    0.600834 |                       719 |                           0.0473772 |                       2.4655  |                                         2.4655  |                                     2.4655   |                              0.561892 |              1 |        52.5124 | skel_1a1b3fb29dff7328 |       0.827061 |        0.994477 |
| a7ff33_dcdd07a710d41c9f | Clip(SafeDiv(mark_index_basis_bps,Abs(Delta(mark_index_basis_bps,1))),-5,5) | basis_premium_like|basis_premium_like | safe_div_clip | L7_ranked_future_return |                 1 |                       -1 |                             3 | True                  |                   0.423449 |                    0.00744372 | True     |                    5.43259  |                 5.43259  | True        |               0.0251401 |               0.0245401 |                0.0235401 |            180.514 | A7FF37A_RANK_LABEL_DIAGNOSTIC_CLUE |            499 |              -0.00703994 |          -1.42524  |                            -1.42524  |                          -1.42524 |                   0.48497  |                   401 |                      -0.0317321 |                 -5.52885  |                                   -5.52885  |                                -5.52885  |                          0.376559 |             345 |                -0.0406063 |            -7.72082 |                              -7.72082 |                           -7.72082 |                    0.336232 |                       396 |                          -0.0255401 |                      -5.43259 |                                        -5.43259 |                                    -5.43259  |                              0.383838 |              0 |        30.1166 | skel_6badd2926fa2941d |       0.998606 |        0.990087 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
