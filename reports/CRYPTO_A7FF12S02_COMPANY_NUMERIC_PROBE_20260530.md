# CRYPTO A7FF-12S02 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:45:09Z

## Decision

`PASS_A7FF12S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S02 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:45:09Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 40,
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
  "portfolio_queue_count": 21,
  "queue_limit": 90,
  "queue_offset": 180,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 15,
  "selected_portfolio_queue_count": 11,
  "stage": "A7FF-12S02",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S02_NUMERIC_CLUE              L0_raw_forward_return     10
              A7FF12S02_NUMERIC_CLUE L1_cross_sectional_relative_return      9
              A7FF12S02_NUMERIC_CLUE  L3_liquidity_tier_relative_return      8
              A7FF12S02_NUMERIC_CLUE             L5_vol_adjusted_return     13
A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     15
    HOLD_A7FF12S02_CONTROL_DOMINATED              L0_raw_forward_return     74
    HOLD_A7FF12S02_CONTROL_DOMINATED L1_cross_sectional_relative_return     76
    HOLD_A7FF12S02_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     64
    HOLD_A7FF12S02_CONTROL_DOMINATED             L5_vol_adjusted_return     83
    HOLD_A7FF12S02_CONTROL_DOMINATED            L7_ranked_future_return    108
  HOLD_A7FF12S02_COST2_PROXY_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF12S02_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF12S02_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      3
  HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     13
  HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     14
  HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     15
  HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     20
  HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     35
     HOLD_A7FF12S02_PRE_MAY_UNSTABLE              L0_raw_forward_return    260
     HOLD_A7FF12S02_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    260
     HOLD_A7FF12S02_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    270
     HOLD_A7FF12S02_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    244
     HOLD_A7FF12S02_PRE_MAY_UNSTABLE            L7_ranked_future_return    202
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S02_NUMERIC_CLUE      4
basis_premium_like|basis_premium_like A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE      4
basis_premium_like|basis_premium_like     HOLD_A7FF12S02_CONTROL_DOMINATED     95
basis_premium_like|basis_premium_like   HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE     47
basis_premium_like|basis_premium_like      HOLD_A7FF12S02_PRE_MAY_UNSTABLE    310
  basis_premium_like|positioning_like               A7FF12S02_NUMERIC_CLUE     22
  basis_premium_like|positioning_like A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE      4
  basis_premium_like|positioning_like     HOLD_A7FF12S02_CONTROL_DOMINATED    113
  basis_premium_like|positioning_like   HOLD_A7FF12S02_COST2_PROXY_FRAGILE      2
  basis_premium_like|positioning_like   HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE     20
  basis_premium_like|positioning_like      HOLD_A7FF12S02_PRE_MAY_UNSTABLE    299
        basis_premium_like|price_like               A7FF12S02_NUMERIC_CLUE      1
        basis_premium_like|price_like A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE      4
        basis_premium_like|price_like     HOLD_A7FF12S02_CONTROL_DOMINATED     94
        basis_premium_like|price_like   HOLD_A7FF12S02_COST2_PROXY_FRAGILE      5
        basis_premium_like|price_like   HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE     13
        basis_premium_like|price_like      HOLD_A7FF12S02_PRE_MAY_UNSTABLE    303
   basis_premium_like|volatility_like               A7FF12S02_NUMERIC_CLUE     13
   basis_premium_like|volatility_like A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE      3
   basis_premium_like|volatility_like     HOLD_A7FF12S02_CONTROL_DOMINATED    103
   basis_premium_like|volatility_like   HOLD_A7FF12S02_ONE_BAR_LAG_FRAGILE     17
   basis_premium_like|volatility_like      HOLD_A7FF12S02_PRE_MAY_UNSTABLE    324
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.794808 4181.203394  5400
 same_family_placebo      0.354681 2523.448287  5400
           sign_flip      0.999151  363.997826  5400
      symbol_shuffle      0.452983 1124.428940  5400
        time_shuffle      0.469316 2549.270603  5400
wrong_lag_future_24h      1.520395 4935.573098  5400
wrong_lag_stale_168h      0.554252 1063.896688  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                              expression                         semantic_pair          motif                      label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_3f3c420268049cb3                        Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(CSRank(mark_trade_basis_bps))) basis_premium_like|basis_premium_like    spread_rank            L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.597855                     0.132145    True                   0.475748                2.158152       True               0.340987           3.403867e-01                0.339387         94.933333               A7FF12S02_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.788830 skel_9505754fb4b5368b      0.996265       0.990929
a7ff7e_01654e884fbd77b8           Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Delta(taker_buy_sell_volume_ratio_last,1)))   basis_premium_like|positioning_like    spread_rank            L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.645262                     0.155476    True                   0.543865                1.245732       True               0.209926           2.093264e-01                0.208326         94.933333               A7FF12S02_NUMERIC_CLUE           700               -0.021066         -0.805084                           -0.345086                        -1.441461                  0.472857                  712                      -0.041860                -1.493677                                  -0.543865                               -1.245732                         0.485955            712                -0.088683          -2.239636                            -0.827556                         -2.019118                   0.452247                      712                          -0.210326                    -4.013948                                      -1.603986                                   -2.691655                             0.433989           1.0    215.681140 skel_bcb165b7818f5d85      0.996265       0.988733
a7ff7e_baf8979f98b80ea5                          SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(CSRank(realized_vol_24h)))    basis_premium_like|volatility_like   safe_div_abs            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.416378                     0.030263    True                   4.944009                4.944009       True               0.111877           1.112772e-01                0.110277         95.866667               A7FF12S02_NUMERIC_CLUE           719               -0.018351         -1.671998                           -1.671998                        -1.671998                  0.479833                  719                      -0.049712                -4.944009                                  -4.944009                               -4.944009                         0.386648            719                -0.106842          -7.832724                            -7.832724                         -7.832724                   0.381085                      719                          -0.112277                    -5.712993                                      -5.712993                                   -5.712993                             0.396384           1.0    117.860807 skel_99250fb0b3bee329      0.827348       1.000000
a7ff7e_08deeb012a9bb0df                        SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Delta(realized_vol_24h,24)))    basis_premium_like|volatility_like   safe_div_abs            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.196134                     0.033905    True                   7.059976                7.059976       True               0.110607           1.100075e-01                0.109007         95.866667               A7FF12S02_NUMERIC_CLUE           695               -0.023297         -2.325111                           -2.325111                        -2.325111                  0.463309                  719                      -0.073297                -7.272419                                  -7.272419                               -7.272419                         0.346314            719                -0.127631         -10.209463                           -10.209463                        -10.209463                   0.331015                      719                          -0.111007                    -7.059976                                      -7.059976                                   -7.059976                             0.376912           1.0    116.811333 skel_084c9fa0938eb532      0.820454       1.000000
a7ff7e_0926ea37046eb212        Sub(Clip(ZScore(mark_index_basis_bps),-3,3),Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))   basis_premium_like|positioning_like            sub            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.786281                     0.035494    True                   4.003979                4.003979       True               0.084169           8.356907e-02                0.082569         95.866667               A7FF12S02_NUMERIC_CLUE           719               -0.006249         -0.648207                           -0.648207                        -0.648207                  0.475661                  719                      -0.067491                -6.551661                                  -6.551661                               -6.551661                         0.375522            719                -0.103387          -7.198074                            -7.198074                         -7.198074                   0.356050                      719                          -0.084569                    -4.003979                                      -4.003979                                   -4.003979                             0.425591           1.0     89.782785 skel_912c5df9db94937c      0.999713       0.999988
a7ff7e_600569f7d9453450                                Sub(Clip(ZScore(mark_index_basis_bps),-3,3),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like            sub            L5_vol_adjusted_return                1                     1.0                            3                 True                  0.632298                     0.042518    True                   2.381781                2.381781       True               0.074772           7.417168e-02                0.073172         95.866667               A7FF12S02_NUMERIC_CLUE           707                0.007699          0.706371                            0.706371                         0.706371                  0.550212                  719                       0.024502                 2.381781                                   2.381781                                2.381781                         0.534075            719                 0.033989           2.564809                             2.564809                          2.564809                   0.568846                      719                           0.075172                     3.706909                                       3.706909                                    3.706909                             0.561892           1.0     80.539383 skel_b04640f9c6171dfc      0.996265       1.000000
a7ff7e_92c2a8df4ad61915 Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)))   basis_premium_like|positioning_like    spread_rank            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.587240                     0.032961    True                   3.916567                3.916567       True               0.063040           6.244028e-02                0.061440         95.866667               A7FF12S02_NUMERIC_CLUE           707               -0.014191         -1.507964                           -1.507964                        -1.507964                  0.459689                  719                      -0.046288                -5.226794                                  -5.226794                               -5.226794                         0.390821            719                -0.076679          -6.646303                            -6.646303                         -6.646303                   0.378303                      719                          -0.063440                    -3.916567                                      -3.916567                                   -3.916567                             0.443672           1.0     68.853044 skel_00fa107e5b1b71eb      0.996265       0.988706
a7ff7e_ae30b011d39a3253                                         Mul(Abs(ZScore(mark_index_basis_bps)),CSRank(realized_vol_24h))    basis_premium_like|volatility_like            mul           L7_ranked_future_return                8                    -1.0                            3                 True                  0.970515                     0.051310    True                   1.139446                1.507176       True               0.057100           5.650023e-02                0.055500         94.933333 A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.056948         -7.806489                           -3.028735                        -3.745985                  0.390449                  712                      -0.024654                -2.951221                                  -1.139446                               -1.507176                         0.463483            712                -0.025984          -4.112717                            -1.402291                         -2.699041                   0.436798                      712                          -0.057500                    -8.285607                                      -3.035462                                   -3.900370                             0.377809           0.0     61.529713 skel_ea6cf56ff46594b4      0.827348       1.000000
a7ff7e_da49aa1841a88a0f                 Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Sign(Clip(ZScore(premium_close_bps),-3,3))) basis_premium_like|basis_premium_like     gated_sign           L7_ranked_future_return                8                    -1.0                            3                 True                  0.953783                     0.025148    True                   0.438857                1.873492       True               0.037704           3.710381e-02                0.036104         94.933333 A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.005003         -1.015176                           -0.186748                        -1.718570                  0.488764                  712                      -0.006194                -1.259070                                  -0.438857                               -1.873492                         0.490169            712                -0.028563          -5.538585                            -2.143467                         -3.814534                   0.436798                      712                          -0.038104                    -7.058735                                      -2.396767                                   -3.583689                             0.396067           0.0     42.150028 skel_f5a350b26e95f33f      0.999713       1.000000
a7ff7e_bb7ca4f16ff9c7e0                        Mul(Delta(Delta(mark_index_basis_bps,12),4),ZScore(Delta(realized_vol_168h,24)))    basis_premium_like|volatility_like relative_shock           L7_ranked_future_return                8                     1.0                            3                 True                  0.797678                     0.003871    True                   0.350597               -0.830560       True               0.005840           5.240490e-03                0.004240         94.933333 A7FF12S02_RANK_LABEL_DIAGNOSTIC_CLUE           688                0.001850          0.317728                            0.155812                        -1.807509                  0.488372                  712                       0.008560                 1.551938                                   0.350597                               -0.481698                         0.509831            712                 0.013197           2.378304                             0.769507                         -0.360014                   0.540730                      712                           0.006240                     1.065452                                       0.481763                                   -0.830560                             0.495787           0.0     10.442813 skel_effc632350c0cac6      0.820454       0.999719
a7ff7e_262acefd9ad42f98                   Sub(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like            sub L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.855423                     0.000282    True                   3.057590                3.057590       True               0.000599          -9.044205e-07               -0.001001         95.866667               A7FF12S02_NUMERIC_CLUE           719               -0.000122         -0.723375                           -0.723375                        -0.723375                  0.485396                  719                      -0.000674                -6.703118                                  -6.703118                               -6.703118                         0.372740            719                -0.001063          -7.090864                            -7.090864                         -7.090864                   0.332406                      719                          -0.000999                    -3.057590                                      -3.057590                                   -3.057590                             0.456189           1.0      6.144577 skel_3363cfb4025bd87d      0.999713       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
