# CRYPTO A7FF-12S00 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T03:39:26Z

## Decision

`PASS_A7FF12S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S00 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:39:26Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 38,
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
  "portfolio_queue_count": 17,
  "queue_limit": 90,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 17,
  "selected_portfolio_queue_count": 9,
  "stage": "A7FF-12S00",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S00_NUMERIC_CLUE              L0_raw_forward_return      9
              A7FF12S00_NUMERIC_CLUE L1_cross_sectional_relative_return      9
              A7FF12S00_NUMERIC_CLUE  L3_liquidity_tier_relative_return      9
              A7FF12S00_NUMERIC_CLUE             L5_vol_adjusted_return     11
A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     17
    HOLD_A7FF12S00_CONTROL_DOMINATED              L0_raw_forward_return    116
    HOLD_A7FF12S00_CONTROL_DOMINATED L1_cross_sectional_relative_return    115
    HOLD_A7FF12S00_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    110
    HOLD_A7FF12S00_CONTROL_DOMINATED             L5_vol_adjusted_return    110
    HOLD_A7FF12S00_CONTROL_DOMINATED            L7_ranked_future_return    102
  HOLD_A7FF12S00_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S00_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     22
  HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     23
  HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     24
  HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     30
  HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     43
     HOLD_A7FF12S00_PRE_MAY_UNSTABLE              L0_raw_forward_return    212
     HOLD_A7FF12S00_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    212
     HOLD_A7FF12S00_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    217
     HOLD_A7FF12S00_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    209
     HOLD_A7FF12S00_PRE_MAY_UNSTABLE            L7_ranked_future_return    198
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S00_NUMERIC_CLUE      2
basis_premium_like|basis_premium_like A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE      3
basis_premium_like|basis_premium_like     HOLD_A7FF12S00_CONTROL_DOMINATED    141
basis_premium_like|basis_premium_like   HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE     81
basis_premium_like|basis_premium_like      HOLD_A7FF12S00_PRE_MAY_UNSTABLE    193
  basis_premium_like|positioning_like               A7FF12S00_NUMERIC_CLUE     11
  basis_premium_like|positioning_like A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE      3
  basis_premium_like|positioning_like     HOLD_A7FF12S00_CONTROL_DOMINATED    103
  basis_premium_like|positioning_like   HOLD_A7FF12S00_COST2_PROXY_FRAGILE      2
  basis_premium_like|positioning_like   HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE     27
  basis_premium_like|positioning_like      HOLD_A7FF12S00_PRE_MAY_UNSTABLE    374
        basis_premium_like|price_like               A7FF12S00_NUMERIC_CLUE     19
        basis_premium_like|price_like A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE      4
        basis_premium_like|price_like     HOLD_A7FF12S00_CONTROL_DOMINATED    135
        basis_premium_like|price_like   HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE      9
        basis_premium_like|price_like      HOLD_A7FF12S00_PRE_MAY_UNSTABLE    193
   basis_premium_like|volatility_like               A7FF12S00_NUMERIC_CLUE      6
   basis_premium_like|volatility_like A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE      7
   basis_premium_like|volatility_like     HOLD_A7FF12S00_CONTROL_DOMINATED    174
   basis_premium_like|volatility_like   HOLD_A7FF12S00_ONE_BAR_LAG_FRAGILE     25
   basis_premium_like|volatility_like      HOLD_A7FF12S00_PRE_MAY_UNSTABLE    288
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.714485  324.453353  5400
 same_family_placebo      0.353671  470.346138  5400
           sign_flip      0.998292  185.290221  5400
      symbol_shuffle      0.438291  859.739482  5400
        time_shuffle      0.465859  597.935188  5400
wrong_lag_future_24h      1.381201 5782.641897  5400
wrong_lag_stale_168h      0.520220  407.454589  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                            expression                         semantic_pair              motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_0c55e3731792d3b1                    Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(trade_return_24h)))         basis_premium_like|price_like         gated_sign  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.640765                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333               A7FF12S00_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.607056 skel_069f2015163fa7ef      0.823901       0.998297
a7ff7e_4ffa4d3edf3aac3d                          Mul(Delta(mark_index_basis_bps,12),CSRank(realized_vol_24h))    basis_premium_like|volatility_like                mul  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.972648                     0.189813    True                   0.329820                1.901416       True               0.320306               0.319706                0.318706         94.933333               A7FF12S00_NUMERIC_CLUE           700               -0.020636         -0.670289                           -0.151571                        -1.215873                  0.478571                  712                      -0.029501                -1.049184                                  -0.329820                               -1.901416                         0.470506            712                -0.088928          -2.025198                            -0.736920                         -2.822448                   0.445225                      712                          -0.320706                    -4.396719                                      -1.694249                                   -2.781084                             0.422753           1.0    325.733110 skel_136259b72205469f      0.823901       0.998297
a7ff7e_42cf23f63bb0ad8d                             Mul(CSRank(mark_index_basis_bps),CSRank(trade_return_1h))         basis_premium_like|price_like                mul  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.573783                     0.060421    True                   6.650899                6.650899       True               0.175552               0.174952                0.173952         95.866667               A7FF12S00_NUMERIC_CLUE           719               -0.049667         -3.747982                           -3.747982                        -3.747982                  0.418637                  719                      -0.078454                -6.650899                                  -6.650899                               -6.650899                         0.368567            719                -0.125210          -8.186964                            -8.186964                         -8.186964                   0.333797                      719                          -0.175952                    -7.844688                                      -7.844688                                   -7.844688                             0.371349           1.0    181.378325 skel_293cae94cfd91548      0.999425       1.000000
a7ff7e_6dd372cacc5ae787                         Sub(CSRank(mark_index_basis_bps),Delta(premium_close_bps,12)) basis_premium_like|basis_premium_like                sub  L5_vol_adjusted_return                1                     1.0                            3                 True                  0.559107                     0.044630    True                   2.700944                2.700944       True               0.078540               0.077940                0.076940         95.866667               A7FF12S00_NUMERIC_CLUE           707                0.017746          1.574785                            1.574785                         1.574785                  0.553041                  719                       0.027773                 2.700944                                   2.700944                                2.700944                         0.542420            719                 0.039069           2.898787                             2.898787                          2.898787                   0.575800                      719                           0.078940                     3.883992                                       3.883992                                    3.883992                             0.564673           1.0     84.381180 skel_e47b3d7310e98dd5      0.996265       1.000000
a7ff7e_fc56709eda2d93a6 Sub(CSRank(mark_index_basis_bps),Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))   basis_premium_like|positioning_like                sub  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.358481                     0.023438    True                   3.507634                3.507634       True               0.068369               0.067769                0.066769         95.866667               A7FF12S00_NUMERIC_CLUE           719               -0.003291         -0.393999                           -0.393999                        -0.393999                  0.506259                  719                      -0.031399                -3.507634                                  -3.507634                               -3.507634                         0.420028            719                -0.069438          -5.952841                            -5.952841                         -5.952841                   0.390821                      719                          -0.068769                    -4.174718                                      -4.174718                                   -4.174718                             0.422809           1.0     74.410852 skel_8831e50795566757      0.999713       1.000000
a7ff7e_c6947b37e3edc298                   Mean(Mul(CSRank(mark_index_basis_bps),CSRank(realized_vol_168h)),4)    basis_premium_like|volatility_like smooth_interaction L7_ranked_future_return                4                    -1.0                            3                 True                  0.846824                     0.026264    True                   1.477471                1.685220       True               0.034871               0.034271                0.033271         95.466667 A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE           713               -0.043455         -4.739003                           -2.437335                        -2.836268                  0.420757                  716                      -0.027098                -2.626546                                  -1.477471                               -1.685220                         0.441341            716                -0.028717          -3.656545                            -1.762577                         -2.133272                   0.437151                      716                          -0.035271                    -5.689201                                      -2.827320                                   -3.155672                             0.407821           0.0     39.424359 skel_09509dd135416ab3      0.826487       1.000000
a7ff7e_f0e40ce3e6adb623                   Mul(CSRank(mark_index_basis_bps),Sign(Delta(premium_close_bps,12))) basis_premium_like|basis_premium_like         gated_sign L7_ranked_future_return                1                    -1.0                            3                 True                  0.661973                     0.006586    True                   3.392513                3.392513       True               0.021269               0.020669                0.019669         95.866667 A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE           707               -0.001293         -0.232326                           -0.232326                        -0.232326                  0.493635                  719                      -0.018301                -3.392513                                  -3.392513                               -3.392513                         0.436718            719                -0.021955          -4.118392                            -4.118392                         -4.118392                   0.436718                      719                          -0.021669                    -4.202468                                      -4.202468                                   -4.202468                             0.453408           0.0     26.007083 skel_1a1b3fb29dff7328      0.996265       0.826542
a7ff7e_8ace2f2b545232ef          Mul(CSRank(mark_index_basis_bps),Sign(Clip(ZScore(realized_vol_168h),-3,3)))    basis_premium_like|volatility_like         gated_sign L7_ranked_future_return                4                    -1.0                            3                 True                  0.985179                     0.029889    True                   0.710784                2.271025       True               0.020758               0.020158                0.019158         95.466667 A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.035570         -5.720418                           -2.914524                        -3.276242                  0.409218                  716                      -0.013030                -1.969151                                  -0.710784                               -2.323989                         0.463687            716                -0.017533          -2.942216                            -1.594082                         -2.271025                   0.423184                      716                          -0.021158                    -3.760065                                      -2.102332                                   -2.558778                             0.431564           0.0     25.172385 skel_8ee95cdec48a7c8f      0.827348       1.000000
a7ff7e_c8a2ea47a5e3c7af           Mul(Delta(CSRank(mark_index_basis_bps),4),ZScore(Delta(trade_return_1h,1)))         basis_premium_like|price_like     relative_shock L7_ranked_future_return                4                     1.0                            3                 True                  0.702330                     0.002551    True                   0.765517               -0.773632       True               0.006473               0.005873                0.004873         95.466667 A7FF12S00_RANK_LABEL_DIAGNOSTIC_CLUE           712                0.001511          0.277183                            0.154312                        -1.669314                  0.492978                  716                       0.015129                 2.852813                                   1.077089                                0.241086                         0.516760            716                 0.008939           1.619385                             0.765517                         -0.570679                   0.540503                      716                           0.006873                     1.277014                                       0.953269                                   -0.773632                             0.529330           0.0     11.171070 skel_bef769163788fd41      0.997989       0.976081
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
