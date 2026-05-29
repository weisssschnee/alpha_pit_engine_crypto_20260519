# CRYPTO A7FF-10S02 EXPANDED NUMERIC PROBE

Generated: 2026-05-29T19:52:30Z

## Decision

`PASS_A7FF10S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-10S02 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF10S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T19:52:30Z",
  "input_blueprint_count": 96,
  "label_response_rows": 1920,
  "materialized_activity_ok_count": 96,
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
  "portfolio_queue_count": 6,
  "queue_limit": 96,
  "queue_offset": 192,
  "rank_label_diagnostic_clue_rows": 3,
  "selected_portfolio_queue_count": 5,
  "stage": "A7FF-10S02",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF10S02_NUMERIC_CLUE              L0_raw_forward_return      3
              A7FF10S02_NUMERIC_CLUE L1_cross_sectional_relative_return      6
              A7FF10S02_NUMERIC_CLUE  L3_liquidity_tier_relative_return      5
              A7FF10S02_NUMERIC_CLUE             L5_vol_adjusted_return      5
A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return      3
    HOLD_A7FF10S02_CONTROL_DOMINATED              L0_raw_forward_return     48
    HOLD_A7FF10S02_CONTROL_DOMINATED L1_cross_sectional_relative_return     44
    HOLD_A7FF10S02_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     42
    HOLD_A7FF10S02_CONTROL_DOMINATED             L5_vol_adjusted_return     50
    HOLD_A7FF10S02_CONTROL_DOMINATED            L7_ranked_future_return     42
      HOLD_A7FF10S02_NONOVERLAP_WEAK             L5_vol_adjusted_return      1
  HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      2
  HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      3
  HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      3
  HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      5
  HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     17
     HOLD_A7FF10S02_PRE_MAY_UNSTABLE              L0_raw_forward_return    331
     HOLD_A7FF10S02_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    331
     HOLD_A7FF10S02_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    334
     HOLD_A7FF10S02_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    323
     HOLD_A7FF10S02_PRE_MAY_UNSTABLE            L7_ranked_future_return    322
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF10S02_NUMERIC_CLUE     18
basis_premium_like|basis_premium_like A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE      2
basis_premium_like|basis_premium_like     HOLD_A7FF10S02_CONTROL_DOMINATED    189
basis_premium_like|basis_premium_like       HOLD_A7FF10S02_NONOVERLAP_WEAK      1
basis_premium_like|basis_premium_like   HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE     27
basis_premium_like|basis_premium_like      HOLD_A7FF10S02_PRE_MAY_UNSTABLE   1383
   basis_premium_like|volatility_like               A7FF10S02_NUMERIC_CLUE      1
   basis_premium_like|volatility_like A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE      1
   basis_premium_like|volatility_like     HOLD_A7FF10S02_CONTROL_DOMINATED     37
   basis_premium_like|volatility_like   HOLD_A7FF10S02_ONE_BAR_LAG_FRAGILE      3
   basis_premium_like|volatility_like      HOLD_A7FF10S02_PRE_MAY_UNSTABLE    258
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.886797  342.437978  5760
 same_family_placebo      0.573436 1350.844828  5760
           sign_flip      0.985622  243.724138  5760
      symbol_shuffle      0.580215  650.922130  5760
        time_shuffle      0.666628  713.901707  5760
wrong_lag_future_24h      0.858685 1276.000000  5760
wrong_lag_stale_168h      0.798375  924.431034  5760
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                      expression                         semantic_pair          motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_cc00b6733f9dc5b8            Mul(Delta(CSRank(mark_index_basis_bps),4),ZScore(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like relative_shock  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.795925                     0.061689    True                   0.626640                1.901517       True               0.097136               0.096536                0.095536         94.933333               A7FF10S02_NUMERIC_CLUE           708               -0.011065         -0.452347                           -0.431815                        -0.901502                  0.483051                  712                      -0.054159                -2.056950                                  -0.626640                               -3.165661                         0.463483            712                -0.120172          -3.412401                            -1.142578                         -2.320913                   0.469101                      712                          -0.097536                    -2.104618                                      -1.085596                                   -1.901517                             0.495787           1.0    102.740158 skel_212ff8a4592ba496      0.998564       0.976086
a7ff7e_5b0ccb3d598b54e2 Mul(Delta(Clip(ZScore(mark_index_basis_bps),-3,3),4),ZScore(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like relative_shock  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.880862                     0.064418    True                   0.787886                1.863713       True               0.094628               0.094028                0.093028         95.466667               A7FF10S02_NUMERIC_CLUE           712               -0.001048         -0.055131                            0.109683                        -1.134263                  0.504213                  716                      -0.051216                -2.853321                                  -1.541107                               -1.863713                         0.445531            716                -0.130999          -4.848567                            -2.120196                         -4.068165                   0.413408                      716                          -0.095028                    -2.408718                                      -0.787886                                   -2.439449                             0.455307           1.0    100.147514 skel_f4bab95847f60af5      0.998564       0.998861
a7ff7e_18c6e12ed1ffd3a5                                  Mul(CSRank(mark_index_basis_bps),CSRank(mark_trade_basis_bps)) basis_premium_like|basis_premium_like            mul L7_ranked_future_return                8                     1.0                            3                 True                  0.474764                     0.014343    True                   0.798778               -1.069353       True               0.032972               0.032372                0.031372         94.933333 A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE           712                0.010564          1.921796                            0.613277                        -0.879998                  0.535112                  712                       0.012530                 2.387380                                   0.798778                               -1.069353                         0.536517            712                 0.038077           6.800019                             2.763492                          1.149793                   0.585674                      712                           0.033372                     5.808242                                       1.928471                                    0.584216                             0.591292           0.0     37.897709 skel_293cae94cfd91548      0.999713       1.000000
a7ff7e_f502dcb33ed6820d                        Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Delta(realized_vol_168h,24))    basis_premium_like|volatility_like            mul L7_ranked_future_return                1                     1.0                            3                 True                  0.976223                     0.009997    True                   1.377595                1.377595       True               0.013254               0.012654                0.011654         95.866667 A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE           695                0.003607          0.633261                            0.633261                         0.633261                  0.502158                  719                       0.008013                 1.377595                                   1.377595                                1.377595                         0.514604            719                 0.009578           1.648720                             1.648720                          1.648720                   0.532684                      719                           0.013654                     2.416605                                       2.416605                                    2.416605                             0.539638           0.0     17.678126 skel_b04640f9c6171dfc      0.820454       1.000000
a7ff7e_e1d6ddf54c650093           Mul(Delta(Delta(mark_index_basis_bps,4),4),ZScore(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like relative_shock L7_ranked_future_return                4                    -1.0                            3                 True                  0.787316                     0.006730    True                   0.948296                1.224218       True               0.005879               0.005279                0.004279         95.466667 A7FF10S02_RANK_LABEL_DIAGNOSTIC_CLUE           708               -0.001796         -0.364017                           -0.025126                        -1.297913                  0.514124                  716                      -0.013009                -2.590740                                  -1.078846                               -2.188610                         0.441341            716                -0.020288          -3.844837                            -1.902476                         -2.862487                   0.451117                      716                          -0.006279                    -1.085649                                      -0.948296                                   -1.224218                             0.500000           0.0     10.491781 skel_dd660997d608c4f9      0.997415       0.999433
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
