# CRYPTO A7FF-10S03 EXPANDED NUMERIC PROBE

Generated: 2026-05-29T19:58:38Z

## Decision

`PASS_A7FF10S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-10S03 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF10S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T19:58:38Z",
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
  "portfolio_queue_count": 18,
  "queue_limit": 96,
  "queue_offset": 288,
  "rank_label_diagnostic_clue_rows": 26,
  "selected_portfolio_queue_count": 13,
  "stage": "A7FF-10S03",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF10S03_NUMERIC_CLUE              L0_raw_forward_return      4
              A7FF10S03_NUMERIC_CLUE L1_cross_sectional_relative_return      4
              A7FF10S03_NUMERIC_CLUE  L3_liquidity_tier_relative_return      4
              A7FF10S03_NUMERIC_CLUE             L5_vol_adjusted_return      7
A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     26
    HOLD_A7FF10S03_CONTROL_DOMINATED              L0_raw_forward_return     74
    HOLD_A7FF10S03_CONTROL_DOMINATED L1_cross_sectional_relative_return     74
    HOLD_A7FF10S03_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     78
    HOLD_A7FF10S03_CONTROL_DOMINATED             L5_vol_adjusted_return     72
    HOLD_A7FF10S03_CONTROL_DOMINATED            L7_ranked_future_return    198
  HOLD_A7FF10S03_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF10S03_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF10S03_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      3
  HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      4
  HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      7
  HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     15
     HOLD_A7FF10S03_PRE_MAY_UNSTABLE              L0_raw_forward_return    302
     HOLD_A7FF10S03_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    302
     HOLD_A7FF10S03_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    297
     HOLD_A7FF10S03_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    298
     HOLD_A7FF10S03_PRE_MAY_UNSTABLE            L7_ranked_future_return    145
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF10S03_NUMERIC_CLUE     13
basis_premium_like|basis_premium_like     HOLD_A7FF10S03_CONTROL_DOMINATED     60
basis_premium_like|basis_premium_like   HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE     17
basis_premium_like|basis_premium_like      HOLD_A7FF10S03_PRE_MAY_UNSTABLE    210
        basis_premium_like|price_like               A7FF10S03_NUMERIC_CLUE      6
        basis_premium_like|price_like A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE     26
        basis_premium_like|price_like     HOLD_A7FF10S03_CONTROL_DOMINATED    436
        basis_premium_like|price_like   HOLD_A7FF10S03_COST2_PROXY_FRAGILE      3
        basis_premium_like|price_like   HOLD_A7FF10S03_ONE_BAR_LAG_FRAGILE     15
        basis_premium_like|price_like      HOLD_A7FF10S03_PRE_MAY_UNSTABLE   1134
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.884330 1149.269231  5760
 same_family_placebo      0.368294 2226.687707  5760
           sign_flip      0.993526  321.561112  5760
      symbol_shuffle      0.487328 1001.332506  5760
        time_shuffle      0.437285 2584.746237  5760
wrong_lag_future_24h      1.878023 5557.223813  5760
wrong_lag_stale_168h      0.589625 2649.146392  5760
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                             expression                         semantic_pair              motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_1eb3f548f136cb3c                   SafeDiv(Abs(ZScore(mark_index_basis_bps)),Abs(mark_trade_basis_bps)) basis_premium_like|basis_premium_like       safe_div_abs  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.941158                     0.095314    True                   0.849016                1.694357       True               0.170778               0.170178                0.169178         63.280556               A7FF10S03_NUMERIC_CLUE           716               -0.008834         -0.405977                           -0.233221                        -0.848370                  0.502793                  716                      -0.052180                -2.197819                                  -0.849016                               -2.880706                         0.449721            716                -0.058279          -2.058484                            -0.969536                         -1.694357                   0.458101                      716                          -0.171178                    -4.111503                                      -1.858293                                   -3.027768                             0.424581           1.0    176.236870 skel_ea6cf56ff46594b4      0.685498       1.000000
a7ff7e_f6c3ddbcb3b20141   Mul(Delta(ZScore(mark_index_basis_bps),4),ZScore(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like     relative_shock  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.822693                     0.058222    True                   0.477678                1.610641       True               0.123603               0.123003                0.122003         94.933333               A7FF10S03_NUMERIC_CLUE           708               -0.008861         -0.331496                           -0.518135                        -1.174074                  0.495763                  712                      -0.050542                -1.864079                                  -0.477678                               -1.839779                         0.471910            712                -0.161618          -4.306078                            -1.613603                         -3.216827                   0.450843                      712                          -0.124003                    -2.161423                                      -0.620852                                   -1.610641                             0.487360           1.0    129.180448 skel_212ff8a4592ba496      0.998564       1.000000
a7ff7e_1f6ec704fe6f7419                     Mean(Mul(Delta(mark_index_basis_bps,1),CSRank(trade_return_1h)),4)         basis_premium_like|price_like smooth_interaction  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.692549                     0.019373    True                   2.935683                2.935683       True               0.074629               0.074029                0.073029         95.866667               A7FF10S03_NUMERIC_CLUE           715               -0.008532         -0.799681                           -0.799681                        -0.799681                  0.469930                  719                      -0.031123                -2.935683                                  -2.935683                               -2.935683                         0.442281            719                -0.072471          -5.070088                            -5.070088                         -5.070088                   0.424200                      719                          -0.075029                    -3.225519                                      -3.225519                                   -3.225519                             0.465925           1.0     80.336411 skel_1128a9bc5ebfee1a      0.997415       0.999886
a7ff7e_18a915f55caf51fd                   SafeDiv(mark_index_basis_bps,Abs(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like       safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.456486                     0.026488    True                   3.995060                3.995060       True               0.071724               0.071124                0.070124         95.866667               A7FF10S03_NUMERIC_CLUE           719               -0.005764         -0.583889                           -0.583889                        -0.583889                  0.465925                  719                      -0.052142                -5.226795                                  -5.226795                               -5.226795                         0.411683            719                -0.065825          -5.460712                            -5.460712                         -5.460712                   0.396384                      719                          -0.072124                    -3.995060                                      -3.995060                                   -3.995060                             0.422809           1.0     77.667382 skel_6a4becaf6b891485      0.999713       0.987410
a7ff7e_17916475944c441b                 Mean(Mul(Delta(mark_index_basis_bps,12),TSRank(trade_return_1h,24)),4)         basis_premium_like|price_like smooth_interaction  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.413343                     0.039693    True                   2.497991                2.497991       True               0.067065               0.066465                0.065465         95.866667               A7FF10S03_NUMERIC_CLUE           693               -0.004383         -0.426157                           -0.426157                        -0.426157                  0.505051                  719                      -0.026368                -2.497991                                  -2.497991                               -2.497991                         0.447844            719                -0.041760          -2.938623                            -2.938623                         -2.938623                   0.433936                      719                          -0.067465                    -2.989782                                      -2.989782                                   -2.989782                             0.463143           1.0     73.051877 skel_8a80c8785bbf365b      0.984487       0.999985
a7ff7e_d1da9288ccc3a5a7                 Mean(Mul(Abs(ZScore(mark_index_basis_bps)),CSRank(trade_return_1h)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                8                    -1.0                            3                 True                  0.609766                     0.043962    True                   1.131320                2.236232       True               0.053497               0.052897                0.051897         94.933333 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.025449         -4.476096                           -1.854478                        -2.503033                  0.414669                  712                      -0.037716                -6.365404                                  -2.331433                               -2.603169                         0.417135            712                -0.019196          -3.123865                            -1.131320                         -2.236232                   0.470506                      712                          -0.053897                    -8.284641                                      -2.939655                                   -4.181913                             0.379213           0.0     58.287218 skel_ec07cc6961c03640      0.997702       1.000000
a7ff7e_e6d66d54754b063c                              Mean(Mul(mark_index_basis_bps,ZScore(trade_return_1h)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                8                     1.0                            3                 True                  0.532874                     0.034819    True                   2.000131                1.058797       True               0.045349               0.044749                0.043749         94.933333 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           709                0.001639          0.240560                            0.040735                        -0.596733                  0.506347                  712                       0.049379                 7.898797                                   2.342480                                1.438732                         0.625000            712                 0.036542           5.888680                             2.000131                          1.058797                   0.564607                      712                           0.045749                     7.286356                                       2.638372                                    1.863119                             0.636236           0.0     50.216580 skel_7fd2912a83f38953      0.997702       0.999751
a7ff7e_a75b6a7329e3d761                Mean(Mul(Abs(ZScore(mark_index_basis_bps)),Decay(trade_return_1h,8)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                4                    -1.0                            3                 True                  0.562605                     0.031186    True                   2.807880                3.990834       True               0.043558               0.042958                0.041958         95.466667 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           706               -0.032269         -4.751417                           -2.300732                        -3.050067                  0.437677                  716                      -0.035530                -5.548284                                  -2.807880                               -4.000853                         0.405028            716                -0.040293          -6.709913                            -3.414439                         -4.121436                   0.399441                      716                          -0.043958                    -6.522787                                      -3.298990                                   -3.990834                             0.392458           0.0     48.395679 skel_5a70d0294f8d4e03      0.993680       0.999973
a7ff7e_10ddf18b688f96a2                      Mean(Mul(CSRank(mark_index_basis_bps),ZScore(trade_return_1h)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                4                    -1.0                            3                 True                  0.428734                     0.024651    True                   2.425581                2.946877       True               0.041499               0.040899                0.039899         95.466667 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           713               -0.047337         -6.661317                           -3.160155                        -4.367822                  0.385694                  716                      -0.041707                -6.289825                                  -3.392409                               -3.581801                         0.409218            716                -0.031119          -4.605469                            -2.425581                         -2.946877                   0.446927                      716                          -0.041899                    -6.602167                                      -3.262129                                   -3.619846                             0.406425           0.0     46.469899 skel_09509dd135416ab3      0.997702       1.000000
a7ff7e_d46843463f63cf9f                             Mean(Mul(mark_index_basis_bps,Decay(trade_return_1h,8)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                8                     1.0                            3                 True                  0.400553                     0.031310    True                   1.613259                1.100309       True               0.032995               0.032395                0.031395         94.933333 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           702                0.012690          1.757954                            0.636569                         0.137517                  0.542735                  712                       0.058021                 9.480818                                   3.403371                                2.478459                         0.641854            712                 0.046155           7.249403                             2.500563                          1.185426                   0.589888                      712                           0.033395                     5.190047                                       1.613259                                    1.100309                             0.581461           0.0     37.994064 skel_644ba0ee0d0e38ee      0.993680       0.999723
a7ff7e_e4c3fbc038c2e96b                     Mean(Mul(CSRank(mark_index_basis_bps),Decay(trade_return_1h,8)),4)         basis_premium_like|price_like smooth_interaction L7_ranked_future_return                1                    -1.0                            3                 True                  0.787880                     0.018114    True                   3.785151                3.785151       True               0.031285               0.030685                0.029685         95.866667 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.029722         -4.314546                           -4.314546                        -4.314546                  0.410437                  719                      -0.025633                -3.785151                                  -3.785151                               -3.785151                         0.453408            719                -0.024818          -3.837022                            -3.837022                         -3.837022                   0.435327                      719                          -0.031685                    -4.600351                                      -4.600351                                   -4.600351                             0.433936           0.0     35.897314 skel_f972d9376d895b33      0.993680       0.999973
a7ff7e_0c377af7f1c1b23b            Sub(CSRank(Delta(mark_index_basis_bps,48)),CSRank(ZScore(trade_return_1h)))         basis_premium_like|price_like        spread_rank L7_ranked_future_return                1                     1.0                            3                 True                  0.964187                     0.018669    True                   0.262369                0.262369       True               0.029159               0.028559                0.027559         95.866667 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           671                0.050777          7.564061                            7.564061                         7.564061                  0.602086                  719                       0.001603                 0.262369                                   0.262369                                0.262369                         0.499305            719                 0.008633           1.493158                             1.493158                          1.493158                   0.522949                      719                           0.029559                     5.008774                                       5.008774                                    5.008774                             0.588317           0.0     33.595188 skel_9505754fb4b5368b      0.985636       0.988123
a7ff7e_5775c61a69fc1eaa Mul(Delta(Clip(ZScore(mark_index_basis_bps),-3,3),4),ZScore(Mean(trade_return_1h,24)))         basis_premium_like|price_like     relative_shock L7_ranked_future_return                8                     1.0                            3                 True                  0.652947                     0.007930    True                   0.445193               -0.829280       True               0.016566               0.015966                0.014966         94.933333 A7FF10S03_RANK_LABEL_DIAGNOSTIC_CLUE           689                0.009005          1.587680                            0.329468                        -0.316067                  0.541364                  712                       0.008047                 1.404469                                   0.445193                               -0.829280                         0.518258            712                 0.016543           3.022653                             1.062079                          0.146751                   0.543539                      712                           0.016966                     2.848009                                       0.760794                                   -0.234377                             0.557584           0.0     21.312825 skel_89c9a5648756465b      0.986211       0.998847
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
