# CRYPTO A7FF-25R3S05 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:35:00Z

## Decision

`PASS_A7FF25R3S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S05 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:35:00Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3380,
  "materialized_activity_ok_count": 169,
  "non_l7_numeric_clue_rows": 49,
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
  "portfolio_queue_count": 43,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_05_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 31,
  "selected_portfolio_queue_count": 7,
  "stage": "A7FF-25R3S05",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S05_NUMERIC_CLUE              L0_raw_forward_return     12
              A7FF25R3S05_NUMERIC_CLUE L1_cross_sectional_relative_return     10
              A7FF25R3S05_NUMERIC_CLUE  L3_liquidity_tier_relative_return     13
              A7FF25R3S05_NUMERIC_CLUE             L5_vol_adjusted_return     14
A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     31
    HOLD_A7FF25R3S05_CONTROL_DOMINATED              L0_raw_forward_return    117
    HOLD_A7FF25R3S05_CONTROL_DOMINATED L1_cross_sectional_relative_return    119
    HOLD_A7FF25R3S05_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    122
    HOLD_A7FF25R3S05_CONTROL_DOMINATED             L5_vol_adjusted_return    117
    HOLD_A7FF25R3S05_CONTROL_DOMINATED            L7_ranked_future_return    337
  HOLD_A7FF25R3S05_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF25R3S05_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF25R3S05_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      2
  HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      6
  HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      6
  HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      6
  HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     13
  HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     27
     HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE              L0_raw_forward_return    540
     HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    540
     HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    533
     HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    532
     HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE            L7_ranked_future_return    281
```

## Family Summary

```text
                     semantic_pair                               decision  count
basis_premium_like|volatility_like               A7FF25R3S05_NUMERIC_CLUE     49
basis_premium_like|volatility_like A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE     31
basis_premium_like|volatility_like     HOLD_A7FF25R3S05_CONTROL_DOMINATED    812
basis_premium_like|volatility_like   HOLD_A7FF25R3S05_COST2_PROXY_FRAGILE      4
basis_premium_like|volatility_like   HOLD_A7FF25R3S05_ONE_BAR_LAG_FRAGILE     58
basis_premium_like|volatility_like      HOLD_A7FF25R3S05_PRE_MAY_UNSTABLE   2426
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.982667 1605.593020 10140
 same_family_placebo      0.328170 1378.125090 10140
           sign_flip      0.983637  346.576862 10140
      symbol_shuffle      0.525387 1576.518874 10140
        time_shuffle      0.524163 1992.959951 10140
wrong_lag_future_24h      2.896297 5466.535234 10140
wrong_lag_stale_168h      0.673590  982.502443 10140
```

## Selected Portfolio Queue

```text
            blueprint_id                                                            expression                      semantic_pair        motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_389e925b81a0c645          Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4) basis_premium_like|volatility_like   smooth_mul  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.552241                     0.112020    True                   0.083963                2.514335       True               0.193082               0.192482                0.191482         94.933333               A7FF25R3S05_NUMERIC_CLUE           708               -0.008843         -0.316081                            0.032939                        -1.214860                  0.491525                  712                      -0.054447                -1.808740                                  -0.669007                               -2.514335                         0.463483            712                -0.078245          -1.951041                            -0.083963                         -3.608013                   0.457865                      712                          -0.193482                    -3.062553                                      -1.423251                                   -4.553313                             0.457865           1.0    198.929896 skel_8184698cb7b24c02      0.826199       0.999830
a7ff24r_62921caa01dbd001 SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,12)))) basis_premium_like|volatility_like safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.316995                     0.024922    True                   4.596211                4.596211       True               0.093898               0.093298                0.092298         95.866667               A7FF25R3S05_NUMERIC_CLUE           708               -0.008091         -0.775244                           -0.775244                        -0.775244                  0.478814                  719                      -0.068852                -7.056194                                  -7.056194                               -7.056194                         0.354659            719                -0.092352          -7.158756                            -7.158756                         -7.158756                   0.354659                      719                          -0.094298                    -4.596211                                      -4.596211                                   -4.596211                             0.392211           1.0     99.980798 skel_c80f62c274b367a9      0.824188       0.987078
a7ff24r_c223ee324263786f                     SafeDiv(premium_close_bps,Abs(realized_vol_168h)) basis_premium_like|volatility_like safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.674115                     0.039465    True                   2.531147                2.531147       True               0.085720               0.085120                0.084120         95.866667               A7FF25R3S05_NUMERIC_CLUE           715               -0.023435         -1.867839                           -1.867839                        -1.867839                  0.454545                  668                      -0.056895                -3.178943                                  -3.178943                               -3.178943                         0.411677            713                -0.050226          -2.531147                            -2.531147                         -2.531147                   0.441795                      719                          -0.086120                    -3.368669                                      -3.368669                                   -3.368669                             0.438108           1.0     91.445831 skel_d9d4f69744bac825      0.827348       0.672833
a7ff24r_cff5d7f207bd19d3   Mean(Mul(mark_index_basis_bps,ZScore(Mean(realized_vol_168h,2))),4) basis_premium_like|volatility_like   smooth_mul L7_ranked_future_return                8                     1.0                            3                 True                  0.946377                     0.068876    True                   1.246024                1.023864       True               0.069958               0.069358                0.068358         94.933333 A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE           708                0.016904          2.220036                            0.770066                         0.224374                  0.553672                  712                       0.031307                 3.839124                                   1.246024                                1.023864                         0.563202            712                 0.031704           5.055679                             1.773802                          1.220319                   0.578652                      712                           0.070358                    10.368692                                       3.665861                                    2.929655                             0.646067           0.0     74.411558 skel_44a246af570899bb      0.826199       0.999710
a7ff24r_f0f23082ea64c621              Mean(Mul(premium_close_bps,Mean(realized_vol_168h,8)),4) basis_premium_like|volatility_like   smooth_mul L7_ranked_future_return               24                     1.0                            3                 True                  0.828535                     0.056305    True                   1.182046               -0.300390       True               0.053180               0.052580                0.051580         92.800000 A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE           686                0.025424          4.286763                            0.785326                        -0.151771                  0.574344                  696                       0.038437                 7.194432                                   1.610034                               -0.091177                         0.597701            696                 0.037522           5.912858                             1.182046                         -0.300390                   0.589080                      696                           0.053580                     8.640699                                       1.852985                                    0.054483                             0.625000           0.0     57.751189 skel_644ba0ee0d0e38ee      0.824476       0.922884
a7ff24r_130f31863e20ac2b                      Mean(Mul(premium_close_bps,realized_vol_168h),4) basis_premium_like|volatility_like   smooth_mul L7_ranked_future_return               24                     1.0                            3                 True                  0.835808                     0.054933    True                   1.104565               -0.253686       True               0.051898               0.051298                0.050298         92.800000 A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE           693                0.024289          4.160563                            0.887839                        -0.208827                  0.574315                  696                       0.040723                 7.543393                                   1.631645                               -0.120031                         0.604885            696                 0.035974           5.672320                             1.104565                         -0.253686                   0.583333                      696                           0.052298                     8.409071                                       1.823997                                   -0.001846                             0.619253           0.0     56.462004 skel_356a5f3fab58eb27      0.826487       0.923057
a7ff24r_e1b520e8bb5bd0ba               Mul(ZScore(Mean(premium_close_bps,2)),realized_vol_24h) basis_premium_like|volatility_like          mul L7_ranked_future_return                1                    -1.0                            3                 True                  0.830530                     0.007081    True                   1.048024                1.048024       True               0.006157               0.005557                0.004557         95.866667 A7FF25R3S05_RANK_LABEL_DIAGNOSTIC_CLUE           718               -0.005635         -0.940583                           -0.940583                        -0.940583                  0.470752                  719                      -0.016312                -2.921038                                  -2.921038                               -2.921038                         0.460362            719                -0.018634          -3.185785                            -3.185785                         -3.185785                   0.440890                      719                          -0.006557                    -1.048024                                      -1.048024                                   -1.048024                             0.486787           0.0     10.726690 skel_97ea9710bb50e137      0.827061       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
