# CRYPTO A7FF-28A EXPANDED NUMERIC PROBE

Generated: 2026-05-30T09:54:37Z

## Decision

`PASS_A7FF28A_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-28A materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF28A_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:54:37Z",
  "input_blueprint_count": 8,
  "label_response_rows": 160,
  "materialized_activity_ok_count": 8,
  "non_l7_numeric_clue_rows": 30,
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
  "portfolio_queue_count": 8,
  "queue_limit": 8,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff28_deep_replay_contract\\a7ff28_deep_replay_queue.csv",
  "queue_total_rows": 8,
  "rank_label_diagnostic_clue_rows": 10,
  "selected_portfolio_queue_count": 8,
  "stage": "A7FF-28A",
  "uses_may": false
}
```

## Decision Counts

| decision                           | label_family                       |   count |
|:-----------------------------------|:-----------------------------------|--------:|
| A7FF28A_NUMERIC_CLUE               | L0_raw_forward_return              |       6 |
| A7FF28A_NUMERIC_CLUE               | L1_cross_sectional_relative_return |       7 |
| A7FF28A_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |       8 |
| A7FF28A_NUMERIC_CLUE               | L5_vol_adjusted_return             |       9 |
| A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      10 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L0_raw_forward_return              |      10 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |       9 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |       8 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L5_vol_adjusted_return             |       5 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L7_ranked_future_return            |       5 |
| HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |       3 |
| HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |       9 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |      15 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |       8 |

## Family Summary

| semantic_pair                         | decision                           |   count |
|:--------------------------------------|:-----------------------------------|--------:|
| basis_premium_like                    | A7FF28A_NUMERIC_CLUE               |       8 |
| basis_premium_like                    | A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE |       2 |
| basis_premium_like                    | HOLD_A7FF28A_CONTROL_DOMINATED     |       4 |
| basis_premium_like                    | HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   |       1 |
| basis_premium_like                    | HOLD_A7FF28A_PRE_MAY_UNSTABLE      |       5 |
| basis_premium_like|basis_premium_like | A7FF28A_NUMERIC_CLUE               |       7 |
| basis_premium_like|basis_premium_like | A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE |       4 |
| basis_premium_like|basis_premium_like | HOLD_A7FF28A_CONTROL_DOMINATED     |      16 |
| basis_premium_like|basis_premium_like | HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   |       6 |
| basis_premium_like|basis_premium_like | HOLD_A7FF28A_PRE_MAY_UNSTABLE      |      47 |
| basis_premium_like|volatility_like    | A7FF28A_NUMERIC_CLUE               |      15 |
| basis_premium_like|volatility_like    | A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE |       4 |
| basis_premium_like|volatility_like    | HOLD_A7FF28A_CONTROL_DOMINATED     |      17 |
| basis_premium_like|volatility_like    | HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   |       5 |
| basis_premium_like|volatility_like    | HOLD_A7FF28A_PRE_MAY_UNSTABLE      |      19 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.384323 |    79.5493  |    480 |
| same_family_placebo  |       0.150696 |    82.4644  |    480 |
| sign_flip            |       1.0132   |     6.67229 |    480 |
| symbol_shuffle       |       0.201563 |   125.056   |    480 |
| time_shuffle         |       0.232917 |    92.6436  |    480 |
| wrong_lag_future_24h |       0.587077 |   782.646   |    480 |
| wrong_lag_stale_168h |       0.320884 |   111.882   |    480 |

## Selected Portfolio Queue

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                           |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | L5_vol_adjusted_return             |                 8 |                       -1 |                             3 | True                  |                   0.73579  |                   0.139993    | True     |                    0.491109 |                  2.00818 | True        |             0.265969    |             0.265369    |               0.264369   |            178.989 | A7FF28A_NUMERIC_CLUE               |            700 |             -0.0167052   |          -0.708782 |                            -0.055122 |                          -1.80204 |                   0.46     |                   712 |                     -0.0546972  |                  -2.64497 |                                   -0.491109 |                                 -2.26734 |                          0.456461 |             712 |              -0.0957247   |            -3.23359 |                             -1.20701  |                           -2.00818 |                    0.43118  |                       712 |                        -0.266369    |                      -6.09882 |                                        -2.33931 |                                     -3.84961 |                              0.411517 |              1 |      271.633   | skel_1d39996e97d5ace0 |       0.996265 |        0.998968 |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return             |                 8 |                       -1 |                             3 | True                  |                   0.758514 |                   0.139993    | True     |                    0.491109 |                  2.00818 | True        |             0.265969    |             0.265369    |               0.264369   |            178.989 | A7FF28A_NUMERIC_CLUE               |            700 |             -0.0167052   |          -0.708782 |                            -0.055122 |                          -1.80204 |                   0.46     |                   712 |                     -0.0546972  |                  -2.64497 |                                   -0.491109 |                                 -2.26734 |                          0.456461 |             712 |              -0.0957247   |            -3.23359 |                             -1.20701  |                           -2.00818 |                    0.43118  |                       712 |                        -0.266369    |                      -6.09882 |                                        -2.33931 |                                     -3.84961 |                              0.411517 |              1 |      271.61    | skel_136259b72205469f |       0.823901 |        0.998919 |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return             |                 1 |                       -1 |                             3 | True                  |                   0.208748 |                   0.0387771   | True     |                    9.49357  |                  9.49357 | True        |             0.137363    |             0.136763    |               0.135763   |            180.749 | A7FF28A_NUMERIC_CLUE               |            708 |             -0.0255023   |          -2.82035  |                            -2.82035  |                          -2.82035 |                   0.450565 |                   719 |                     -0.0837064  |                  -9.88144 |                                   -9.88144  |                                 -9.88144 |                          0.301808 |             719 |              -0.125302    |           -11.6595  |                            -11.6595   |                          -11.6595  |                    0.294854 |                       719 |                        -0.137763    |                      -9.49357 |                                        -9.49357 |                                     -9.49357 |                              0.332406 |              1 |      143.554   | skel_f8484b844efd270f |       0.996553 |        0.999317 |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return             |                 8 |                       -1 |                             3 | True                  |                   0.612048 |                   0.0565198   | True     |                    0.886194 |                  2.35383 | True        |             0.125936    |             0.125336    |               0.124336   |            178.989 | A7FF28A_NUMERIC_CLUE               |            708 |             -0.0223172   |          -0.977003 |                            -0.297407 |                          -1.5474  |                   0.49435  |                   712 |                     -0.0693447  |                  -3.07061 |                                   -1.27226  |                                 -2.35383 |                          0.446629 |             712 |              -0.0743312   |            -2.62182 |                             -0.886194 |                           -2.82619 |                    0.460674 |                       712 |                        -0.126336    |                      -3.05234 |                                        -1.37162 |                                     -3.90103 |                              0.450843 |              1 |      131.724   | skel_8184698cb7b24c02 |       0.826199 |        0.99991  |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return             |                 1 |                       -1 |                             3 | True                  |                   0.721288 |                   0.0478025   | True     |                    1.81346  |                  1.81346 | True        |             0.0751881   |             0.0745881   |               0.0735881  |            180.749 | A7FF28A_NUMERIC_CLUE               |            718 |             -0.022473    |          -1.58577  |                            -1.58577  |                          -1.58577 |                   0.456825 |                   705 |                     -0.0657306  |                  -4.53456 |                                   -4.53456  |                                 -4.53456 |                          0.397163 |             719 |              -0.0306008   |            -1.81346 |                             -1.81346  |                           -1.81346 |                    0.465925 |                       719 |                        -0.0755881   |                      -3.90811 |                                        -3.90811 |                                     -3.90811 |                              0.426982 |              1 |       80.8668  | skel_d9d4f69744bac825 |       0.827348 |        0.675194 |
| a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | sub          | L7_ranked_future_return            |                 8 |                       -1 |                             3 | True                  |                   0.413729 |                   0.0246591   | True     |                    2.88494  |                  3.44586 | True        |             0.0350992   |             0.0344992   |               0.0334992  |            178.989 | A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE |            704 |             -0.0107427   |          -2.61331  |                            -1.27881  |                          -1.75662 |                   0.455966 |                   712 |                     -0.0274126  |                  -7.50203 |                                   -2.88737  |                                 -3.44586 |                          0.386236 |             712 |              -0.0441219   |           -11.5611  |                             -4.19156  |                           -4.76191 |                    0.348315 |                       712 |                        -0.0354992   |                      -8.91303 |                                        -2.88494 |                                     -4.59065 |                              0.349719 |              0 |       40.0855  | skel_0994b3a36a4d53ba |       0.997415 |        0.998463 |
| a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps)           | basis_premium_like|basis_premium_like | sub          | L7_ranked_future_return            |                 1 |                        1 |                             3 | True                  |                   0.596403 |                   0.00404143  | True     |                    3.96317  |                  3.96317 | True        |             0.0155229   |             0.0149229   |               0.0139229  |            180.749 | A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE |            712 |              0.0150844   |           3.46165  |                             3.46165  |                           3.46165 |                   0.564607 |                   719 |                      0.0289981  |                   6.94993 |                                    6.94993  |                                  6.94993 |                          0.607789 |             719 |               0.0171076   |             4.34815 |                              4.34815  |                            4.34815 |                    0.552156 |                       719 |                         0.0159229   |                       3.96317 |                                         3.96317 |                                      3.96317 |                              0.563282 |              0 |       20.3265  | skel_97ea9710bb50e137 |       0.997702 |        1        |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | L1_cross_sectional_relative_return |                 1 |                       -1 |                             3 | True                  |                   0.226391 |                   0.000234451 | True     |                    5.96095  |                  5.96095 | True        |             0.000236895 |            -0.000363105 |              -0.00136311 |            180.749 | A7FF28A_NUMERIC_CLUE               |            708 |             -0.000232219 |          -1.78965  |                            -1.78965  |                          -1.78965 |                   0.457627 |                   719 |                     -0.00050917 |                  -6.31325 |                                   -6.31325  |                                 -6.31325 |                          0.344924 |             719 |              -0.000696365 |            -8.05832 |                             -8.05832  |                           -8.05832 |                    0.347705 |                       719 |                        -0.000636895 |                      -5.96095 |                                        -5.96095 |                                     -5.96095 |                              0.385257 |              1 |        6.77361 | skel_c80f62c274b367a9 |       0.996553 |        0.989336 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
