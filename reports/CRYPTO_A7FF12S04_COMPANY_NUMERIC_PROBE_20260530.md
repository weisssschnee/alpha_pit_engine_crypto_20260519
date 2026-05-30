# CRYPTO A7FF-12S04 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:59:05Z

## Decision

`PASS_A7FF12S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S04 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:59:05Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 78,
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
  "portfolio_queue_count": 24,
  "queue_limit": 90,
  "queue_offset": 360,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 24,
  "selected_portfolio_queue_count": 10,
  "stage": "A7FF-12S04",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S04_NUMERIC_CLUE              L0_raw_forward_return     17
              A7FF12S04_NUMERIC_CLUE L1_cross_sectional_relative_return     19
              A7FF12S04_NUMERIC_CLUE  L3_liquidity_tier_relative_return     19
              A7FF12S04_NUMERIC_CLUE             L5_vol_adjusted_return     23
A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     24
    HOLD_A7FF12S04_CONTROL_DOMINATED              L0_raw_forward_return     98
    HOLD_A7FF12S04_CONTROL_DOMINATED L1_cross_sectional_relative_return     96
    HOLD_A7FF12S04_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     79
    HOLD_A7FF12S04_CONTROL_DOMINATED             L5_vol_adjusted_return     97
    HOLD_A7FF12S04_CONTROL_DOMINATED            L7_ranked_future_return    100
  HOLD_A7FF12S04_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S04_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF12S04_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      4
  HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     21
  HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     21
  HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     23
  HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     38
  HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     63
     HOLD_A7FF12S04_PRE_MAY_UNSTABLE              L0_raw_forward_return    223
     HOLD_A7FF12S04_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    223
     HOLD_A7FF12S04_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    235
     HOLD_A7FF12S04_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    202
     HOLD_A7FF12S04_PRE_MAY_UNSTABLE            L7_ranked_future_return    173
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S04_NUMERIC_CLUE     18
basis_premium_like|basis_premium_like A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE     11
basis_premium_like|basis_premium_like     HOLD_A7FF12S04_CONTROL_DOMINATED    120
basis_premium_like|basis_premium_like   HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE     84
basis_premium_like|basis_premium_like      HOLD_A7FF12S04_PRE_MAY_UNSTABLE    287
  basis_premium_like|positioning_like               A7FF12S04_NUMERIC_CLUE     26
  basis_premium_like|positioning_like A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE      5
  basis_premium_like|positioning_like     HOLD_A7FF12S04_CONTROL_DOMINATED    128
  basis_premium_like|positioning_like   HOLD_A7FF12S04_COST2_PROXY_FRAGILE      2
  basis_premium_like|positioning_like   HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE     35
  basis_premium_like|positioning_like      HOLD_A7FF12S04_PRE_MAY_UNSTABLE    244
        basis_premium_like|price_like               A7FF12S04_NUMERIC_CLUE      4
        basis_premium_like|price_like A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE      5
        basis_premium_like|price_like     HOLD_A7FF12S04_CONTROL_DOMINATED    112
        basis_premium_like|price_like   HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE     15
        basis_premium_like|price_like      HOLD_A7FF12S04_PRE_MAY_UNSTABLE    264
   basis_premium_like|volatility_like               A7FF12S04_NUMERIC_CLUE     30
   basis_premium_like|volatility_like A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE      3
   basis_premium_like|volatility_like     HOLD_A7FF12S04_CONTROL_DOMINATED    110
   basis_premium_like|volatility_like   HOLD_A7FF12S04_COST2_PROXY_FRAGILE      4
   basis_premium_like|volatility_like   HOLD_A7FF12S04_ONE_BAR_LAG_FRAGILE     32
   basis_premium_like|volatility_like      HOLD_A7FF12S04_PRE_MAY_UNSTABLE    261
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.635381 12156.307692  5400
 same_family_placebo      0.294396  1561.846154  5400
           sign_flip      0.994014  1761.769231  5400
      symbol_shuffle      0.366774  8253.230769  5400
        time_shuffle      0.371181   726.441998  5400
wrong_lag_future_24h      1.175000 14305.153846  5400
wrong_lag_stale_168h      0.469046  5670.384615  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                    expression                         semantic_pair          motif                       label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_af0cebc89db56866                   Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(mark_trade_basis_bps)))) basis_premium_like|basis_premium_like     gated_sign             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.619643                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF12S04_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.628179 skel_3d008dc9486239b2      0.996265       0.998429
a7ff7e_175e58eb9e5404d5                          Sub(Delta(mark_index_basis_bps,12),taker_buy_sell_volume_ratio_last)   basis_premium_like|positioning_like            sub             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.895971                     0.221632    True                   0.392998                1.937686       True               0.358454               0.357854                0.356854         94.933333               A7FF12S04_NUMERIC_CLUE           700               -0.010450         -0.361474                           -0.158077                        -1.470155                  0.477143                  712                      -0.042515                -1.495904                                  -0.392998                               -1.937686                         0.452247            712                -0.127146          -3.151206                            -1.109472                         -2.184041                   0.432584                      712                          -0.358854                    -5.133974                                      -2.133213                                   -3.208312                             0.408708           1.0    363.957668 skel_0994b3a36a4d53ba      0.996265       0.999991
a7ff7e_ffdab637dbab0125                   SafeDiv(mark_index_basis_bps,Abs(CSRank(taker_buy_sell_volume_ratio_last)))   basis_premium_like|positioning_like   safe_div_abs             L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.850748                     0.051286    True                   1.330573                2.527708       True               0.180422               0.179822                0.178822         95.466667               A7FF12S04_NUMERIC_CLUE           716               -0.004460         -0.243583                           -0.358945                        -1.113859                  0.474860                  716                      -0.064687                -3.116657                                  -1.330573                               -3.509182                         0.416201            716                -0.090435          -3.097455                            -1.868217                         -2.527708                   0.459497                      716                          -0.180822                    -4.886136                                      -2.141755                                   -3.705698                             0.417598           1.0    185.970933 skel_06aed53e0aa5366a      0.999713       0.987410
a7ff7e_4e141259215570d3 SafeDiv(Delta(mark_index_basis_bps,24),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like   safe_div_abs             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.831063                     0.049466    True                   7.332632                7.332632       True               0.162040               0.161440                0.160440         95.866667               A7FF12S04_NUMERIC_CLUE           695               -0.026785         -2.514293                           -2.514293                        -2.514293                  0.428777                  719                      -0.076397                -7.950472                                  -7.950472                               -7.950472                         0.358832            719                -0.127540          -9.024634                            -9.024634                         -9.024634                   0.328234                      719                          -0.162440                    -7.332632                                      -7.332632                                   -7.332632                             0.381085           1.0    167.608449 skel_156d0fafafecde17      0.992818       0.997742
a7ff7e_42b9aa89029367d2                                SafeDiv(mark_index_basis_bps,Abs(Delta(realized_vol_168h,24)))    basis_premium_like|volatility_like   safe_div_abs             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.184541                     0.030430    True                   7.280667                7.280667       True               0.106999               0.106399                0.105399         95.866667               A7FF12S04_NUMERIC_CLUE           695               -0.003147         -0.289641                           -0.289641                        -0.289641                  0.480576                  719                      -0.077038                -8.237201                                  -8.237201                               -8.237201                         0.369958            719                -0.105477          -8.113440                            -8.113440                         -8.113440                   0.357441                      719                          -0.107399                    -7.280667                                      -7.280667                                   -7.280667                             0.368567           1.0    113.213989 skel_a2f58ee62d9e7ad2      0.820454       0.987023
a7ff7e_5c0e7b1ec4ee0ab8                       SafeDiv(mark_index_basis_bps,Abs(Clip(ZScore(premium_close_bps),-3,3))) basis_premium_like|basis_premium_like   safe_div_abs            L7_ranked_future_return                4                    -1.0                            3                 True                  0.524115                     0.010556    True                   2.266474                2.608804       True               0.034557               0.033957                0.032957         95.466667 A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.000818         -0.154706                            0.324886                        -2.388718                  0.491620                  716                      -0.026157                -5.147631                                  -2.266474                               -4.243258                         0.413408            716                -0.024999          -4.795168                            -2.372666                         -2.608804                   0.428771                      716                          -0.034957                    -6.476873                                      -3.426043                                   -4.574541                             0.406425           0.0     39.432956 skel_1c4b9d5957f9af9c      0.999713       0.987410
a7ff7e_03c6987b58c53d7f                                           Mul(mark_index_basis_bps,Delta(trade_return_24h,1))         basis_premium_like|price_like            mul            L7_ranked_future_return                4                     1.0                            3                 True                  0.946364                     0.012044    True                   1.752224                1.444180       True               0.030990               0.030390                0.029390         95.466667 A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE           715                0.012914          2.087724                            1.197702                         0.303814                  0.537063                  716                       0.021697                 3.855325                                   1.752224                                1.444180                         0.553073            716                 0.026859           4.624012                             2.275616                          1.987183                   0.579609                      716                           0.031390                     5.429361                                       2.714345                                    2.197418                             0.590782           0.0     35.443382 skel_f8484b844efd270f      0.827061       0.981772
a7ff7e_26f35a9e559c2e1e                                Mul(mark_index_basis_bps,Clip(ZScore(premium_close_bps),-3,3)) basis_premium_like|basis_premium_like            mul            L7_ranked_future_return                8                    -1.0                            3                 True                  0.685382                     0.022157    True                   0.865544                2.076685       True               0.029061               0.028461                0.027461         94.933333 A7FF12S04_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.004300         -0.867671                           -0.216061                        -1.547287                  0.501404                  712                      -0.020998                -4.077563                                  -1.564660                               -2.676363                         0.452247            712                -0.014306          -2.666210                            -0.865544                         -2.076685                   0.469101                      712                          -0.029461                    -5.298826                                      -2.019697                                   -2.653792                             0.405899           0.0     33.776001 skel_593666ed3f85046b      0.999713       0.987410
a7ff7e_0c7cd03187d0a1be                            Sub(mark_index_basis_bps,CSRank(taker_buy_sell_volume_ratio_last))   basis_premium_like|positioning_like            sub  L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.698038                     0.000294    True                   3.611575                3.611575       True               0.000735               0.000135               -0.000865         95.866667               A7FF12S04_NUMERIC_CLUE           719               -0.000201         -1.203953                           -1.203953                        -1.203953                  0.481224                  719                      -0.000725                -6.983896                                  -6.983896                               -6.983896                         0.374131            719                -0.001133          -7.555773                            -7.555773                         -7.555773                   0.349096                      719                          -0.001135                    -3.611575                                      -3.611575                                   -3.611575                             0.450626           1.0      6.436617 skel_d9d4f69744bac825      0.999713       0.999997
a7ff7e_68c2e2321ad3882e      Mul(Delta(Clip(ZScore(mark_index_basis_bps),-3,3),4),ZScore(Delta(trade_return_24h,24)))         basis_premium_like|price_like relative_shock L1_cross_sectional_relative_return                4                    -1.0                            3                 True                  0.996588                     0.001163    True                   0.558247                1.337091       True               0.000272              -0.000328               -0.001328         95.466667               A7FF12S04_NUMERIC_CLUE           692               -0.000220         -0.627935                           -0.286131                        -1.303888                  0.504335                  716                      -0.000292                -1.169292                                  -0.582631                               -1.337091                         0.467877            716                -0.000492          -1.434976                            -0.765290                         -1.368876                   0.491620                      716                          -0.000672                    -1.156706                                      -0.558247                                   -1.869806                             0.490223           1.0      6.003412 skel_89c9a5648756465b      0.820454       0.998738
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
