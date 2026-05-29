# CRYPTO A7FF-10S00 EXPANDED NUMERIC PROBE

Generated: 2026-05-29T20:07:44Z

## Decision

`PASS_A7FF10S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-10S00 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF10S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T20:07:44Z",
  "input_blueprint_count": 96,
  "label_response_rows": 1920,
  "materialized_activity_ok_count": 96,
  "non_l7_numeric_clue_rows": 87,
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
  "queue_limit": 96,
  "queue_offset": 0,
  "rank_label_diagnostic_clue_rows": 14,
  "selected_portfolio_queue_count": 8,
  "stage": "A7FF-10S00",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF10S00_NUMERIC_CLUE              L0_raw_forward_return     24
              A7FF10S00_NUMERIC_CLUE L1_cross_sectional_relative_return     25
              A7FF10S00_NUMERIC_CLUE  L3_liquidity_tier_relative_return     20
              A7FF10S00_NUMERIC_CLUE             L5_vol_adjusted_return     18
A7FF10S00_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     14
    HOLD_A7FF10S00_CONTROL_DOMINATED              L0_raw_forward_return     86
    HOLD_A7FF10S00_CONTROL_DOMINATED L1_cross_sectional_relative_return     85
    HOLD_A7FF10S00_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     71
    HOLD_A7FF10S00_CONTROL_DOMINATED             L5_vol_adjusted_return     87
    HOLD_A7FF10S00_CONTROL_DOMINATED            L7_ranked_future_return     56
  HOLD_A7FF10S00_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      3
  HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     10
  HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     10
  HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     10
  HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     28
  HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     50
     HOLD_A7FF10S00_PRE_MAY_UNSTABLE              L0_raw_forward_return    264
     HOLD_A7FF10S00_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    264
     HOLD_A7FF10S00_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    280
     HOLD_A7FF10S00_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    251
     HOLD_A7FF10S00_PRE_MAY_UNSTABLE            L7_ranked_future_return    264
```

## Family Summary

```text
                      semantic_pair                             decision  count
                 basis_premium_like               A7FF10S00_NUMERIC_CLUE     27
                 basis_premium_like A7FF10S00_RANK_LABEL_DIAGNOSTIC_CLUE      6
                 basis_premium_like     HOLD_A7FF10S00_CONTROL_DOMINATED    101
                 basis_premium_like   HOLD_A7FF10S00_COST2_PROXY_FRAGILE      1
                 basis_premium_like   HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE     35
                 basis_premium_like      HOLD_A7FF10S00_PRE_MAY_UNSTABLE    130
basis_premium_like|positioning_like               A7FF10S00_NUMERIC_CLUE     60
basis_premium_like|positioning_like A7FF10S00_RANK_LABEL_DIAGNOSTIC_CLUE      8
basis_premium_like|positioning_like     HOLD_A7FF10S00_CONTROL_DOMINATED    284
basis_premium_like|positioning_like   HOLD_A7FF10S00_COST2_PROXY_FRAGILE      2
basis_premium_like|positioning_like   HOLD_A7FF10S00_ONE_BAR_LAG_FRAGILE     73
basis_premium_like|positioning_like      HOLD_A7FF10S00_PRE_MAY_UNSTABLE   1193
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.830562 1800.545455  5760
 same_family_placebo      0.505600 1330.020539  5760
           sign_flip      1.003086  904.236364  5760
      symbol_shuffle      0.547632 1441.145455  5760
        time_shuffle      0.610213 2453.182347  5760
wrong_lag_future_24h      1.088202 2890.140133  5760
wrong_lag_stale_168h      0.746480 3228.768155  5760
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                             expression                       semantic_pair      motif           label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_454b18e00e63d958                                                                         Delta(mark_index_basis_bps,12)                  basis_premium_like     single L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.790958                     0.247474    True                   0.626901                2.325739       True               0.389848               0.389248                0.388248         94.933333 A7FF10S00_NUMERIC_CLUE           700               -0.015016         -0.519622                           -0.175288                        -1.634500                  0.480000                  712                      -0.055726                -2.018783                                  -0.626901                               -2.526720                         0.441011            712                -0.137832          -3.261929                            -1.329647                         -2.325739                   0.450843                      712                          -0.390248                    -5.507264                                      -2.333339                                   -3.278556                             0.411517           1.0    395.456864 skel_1d39996e97d5ace0      0.996265       0.998429
a7ff7e_debf48d0ab3ed5aa                             Mul(Delta(mark_index_basis_bps,12),Sign(taker_buy_sell_volume_ratio_last)) basis_premium_like|positioning_like gated_sign L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.492260                     0.139538    True                   0.929143                2.272430       True               0.273793               0.273193                0.272193         95.466667 A7FF10S00_NUMERIC_CLUE           704               -0.015268         -0.734626                           -0.245353                        -1.151874                  0.482955                  716                      -0.051182                -2.764916                                  -0.929143                               -3.048001                         0.458101            716                -0.096440          -3.167772                            -1.539107                         -2.272430                   0.409218                      716                          -0.274193                    -6.038820                                      -3.132985                                   -3.609319                             0.410615           1.0    279.701165 skel_136259b72205469f      0.996265       0.998060
a7ff7e_303a085bd066346e                     Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(taker_buy_sell_volume_ratio_last))) basis_premium_like|positioning_like gated_sign L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.394847                     0.139179    True                   0.852616                2.303467       True               0.273511               0.272911                0.271911         95.466667 A7FF10S00_NUMERIC_CLUE           704               -0.015268         -0.734626                           -0.245353                        -1.151874                  0.482955                  716                      -0.049945                -2.699969                                  -0.852616                               -3.055159                         0.460894            716                -0.096646          -3.171834                            -1.543866                         -2.303467                   0.409218                      716                          -0.273911                    -6.032953                                      -3.139373                                   -3.609319                             0.412011           1.0    279.516561 skel_069f2015163fa7ef      0.996265       0.998429
a7ff7e_b542fd793bf96942          Mul(Delta(mark_index_basis_bps,12),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))) basis_premium_like|positioning_like gated_sign L5_vol_adjusted_return                1                     1.0                            3                 True                  0.648499                     0.028011    True                   1.952994                1.952994       True               0.081507               0.080907                0.079907         95.866667 A7FF10S00_NUMERIC_CLUE           707                0.019076          2.024512                            2.024512                         2.024512                  0.545969                  719                       0.018514                 1.952994                                   1.952994                                1.952994                         0.535466            719                 0.046674           3.478591                             3.478591                          3.478591                   0.543811                      719                           0.081907                     3.850828                                       3.850828                                    3.850828                             0.529903           1.0     87.258636 skel_6a3533b4d89c4d45      0.996265       0.998429
a7ff7e_09c74d60d25a4769                       Mul(ZScore(mark_index_basis_bps),Sign(ZScore(taker_buy_sell_volume_ratio_last))) basis_premium_like|positioning_like gated_sign  L0_raw_forward_return                1                     1.0                            3                 True                  0.968969                     0.000210    True                   2.501784                2.501784       True               0.000439              -0.000161               -0.001161         95.866667 A7FF10S00_NUMERIC_CLUE           719                0.000193          1.148621                            1.148621                         1.148621                  0.520167                  719                       0.000264                 2.501784                                   2.501784                                2.501784                         0.559110            719                 0.000421           2.707721                             2.707721                          2.707721                   0.571627                      719                           0.000839                     2.753905                                       2.753905                                    2.753905                             0.506259           1.0      6.031031 skel_897201905b87a210      0.999713       1.000000
a7ff7e_3de5984ae7a1281a Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))) basis_premium_like|positioning_like gated_sign  L0_raw_forward_return                1                     1.0                            3                 True                  0.968969                     0.000210    True                   2.501784                2.501784       True               0.000439              -0.000161               -0.001161         95.866667 A7FF10S00_NUMERIC_CLUE           719                0.000193          1.148621                            1.148621                         1.148621                  0.520167                  719                       0.000264                 2.501784                                   2.501784                                2.501784                         0.559110            719                 0.000421           2.707721                             2.707721                          2.707721                   0.571627                      719                           0.000839                     2.753905                                       2.753905                                    2.753905                             0.506259           1.0      6.031031 skel_f5a350b26e95f33f      0.999713       1.000000
a7ff7e_e26061c262476c8a            Mul(Clip(ZScore(mark_index_basis_bps),-3,3),Sign(ZScore(taker_buy_sell_volume_ratio_last))) basis_premium_like|positioning_like gated_sign  L0_raw_forward_return                1                     1.0                            3                 True                  0.968969                     0.000210    True                   2.501784                2.501784       True               0.000439              -0.000161               -0.001161         95.866667 A7FF10S00_NUMERIC_CLUE           719                0.000193          1.148621                            1.148621                         1.148621                  0.520167                  719                       0.000264                 2.501784                                   2.501784                                2.501784                         0.559110            719                 0.000421           2.707721                             2.707721                          2.707721                   0.571627                      719                           0.000839                     2.753905                                       2.753905                                    2.753905                             0.506259           1.0      6.031031 skel_99250fb0b3bee329      0.999713       1.000000
a7ff7e_e6b9862b22744590            Mul(ZScore(mark_index_basis_bps),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))) basis_premium_like|positioning_like gated_sign  L0_raw_forward_return                1                     1.0                            3                 True                  0.968969                     0.000210    True                   2.501784                2.501784       True               0.000439              -0.000161               -0.001161         95.866667 A7FF10S00_NUMERIC_CLUE           719                0.000193          1.148621                            1.148621                         1.148621                  0.520167                  719                       0.000264                 2.501784                                   2.501784                                2.501784                         0.559110            719                 0.000421           2.707721                             2.707721                          2.707721                   0.571627                      719                           0.000839                     2.753905                                       2.753905                                    2.753905                             0.506259           1.0      6.031031 skel_8ee95cdec48a7c8f      0.999713       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
