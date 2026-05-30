# CRYPTO A7FF-12S07 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T04:04:38Z

## Decision

`PASS_A7FF12S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-12S07 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF12S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:04:38Z",
  "input_blueprint_count": 90,
  "label_response_rows": 1800,
  "materialized_activity_ok_count": 90,
  "non_l7_numeric_clue_rows": 26,
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
  "portfolio_queue_count": 16,
  "queue_limit": 90,
  "queue_offset": 630,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff12_numeric_wave_queue_contract\\a7ff12_numeric_wave_queue.csv",
  "queue_total_rows": 720,
  "rank_label_diagnostic_clue_rows": 11,
  "selected_portfolio_queue_count": 7,
  "stage": "A7FF-12S07",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF12S07_NUMERIC_CLUE              L0_raw_forward_return      4
              A7FF12S07_NUMERIC_CLUE L1_cross_sectional_relative_return      6
              A7FF12S07_NUMERIC_CLUE  L3_liquidity_tier_relative_return      5
              A7FF12S07_NUMERIC_CLUE             L5_vol_adjusted_return     11
A7FF12S07_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     11
    HOLD_A7FF12S07_CONTROL_DOMINATED              L0_raw_forward_return     92
    HOLD_A7FF12S07_CONTROL_DOMINATED L1_cross_sectional_relative_return     90
    HOLD_A7FF12S07_CONTROL_DOMINATED  L3_liquidity_tier_relative_return     86
    HOLD_A7FF12S07_CONTROL_DOMINATED             L5_vol_adjusted_return     91
    HOLD_A7FF12S07_CONTROL_DOMINATED            L7_ranked_future_return    104
  HOLD_A7FF12S07_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF12S07_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF12S07_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     11
  HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     11
  HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     12
  HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     22
  HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     38
     HOLD_A7FF12S07_PRE_MAY_UNSTABLE              L0_raw_forward_return    252
     HOLD_A7FF12S07_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    252
     HOLD_A7FF12S07_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    256
     HOLD_A7FF12S07_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    236
     HOLD_A7FF12S07_PRE_MAY_UNSTABLE            L7_ranked_future_return    207
```

## Family Summary

```text
                        semantic_pair                             decision  count
basis_premium_like|basis_premium_like               A7FF12S07_NUMERIC_CLUE      1
basis_premium_like|basis_premium_like A7FF12S07_RANK_LABEL_DIAGNOSTIC_CLUE      1
basis_premium_like|basis_premium_like     HOLD_A7FF12S07_CONTROL_DOMINATED    104
basis_premium_like|basis_premium_like   HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE     42
basis_premium_like|basis_premium_like      HOLD_A7FF12S07_PRE_MAY_UNSTABLE    332
  basis_premium_like|positioning_like               A7FF12S07_NUMERIC_CLUE     21
  basis_premium_like|positioning_like A7FF12S07_RANK_LABEL_DIAGNOSTIC_CLUE      6
  basis_premium_like|positioning_like     HOLD_A7FF12S07_CONTROL_DOMINATED    212
  basis_premium_like|positioning_like   HOLD_A7FF12S07_COST2_PROXY_FRAGILE      3
  basis_premium_like|positioning_like   HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE     39
  basis_premium_like|positioning_like      HOLD_A7FF12S07_PRE_MAY_UNSTABLE    519
        basis_premium_like|price_like     HOLD_A7FF12S07_CONTROL_DOMINATED     22
        basis_premium_like|price_like      HOLD_A7FF12S07_PRE_MAY_UNSTABLE     38
   basis_premium_like|volatility_like               A7FF12S07_NUMERIC_CLUE      4
   basis_premium_like|volatility_like A7FF12S07_RANK_LABEL_DIAGNOSTIC_CLUE      4
   basis_premium_like|volatility_like     HOLD_A7FF12S07_CONTROL_DOMINATED    125
   basis_premium_like|volatility_like   HOLD_A7FF12S07_ONE_BAR_LAG_FRAGILE     13
   basis_premium_like|volatility_like      HOLD_A7FF12S07_PRE_MAY_UNSTABLE    314
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.732281 16422.555609  5400
 same_family_placebo      0.360763  3113.855694  5400
           sign_flip      1.004606   574.199174  5400
      symbol_shuffle      0.451099  2392.384615  5400
        time_shuffle      0.446225  3423.427158  5400
wrong_lag_future_24h      1.266167 10077.075144  5400
wrong_lag_stale_168h      0.565311  8579.149928  5400
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                                           expression                         semantic_pair              motif                       label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_b38081e93d4f200f                             Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(mark_trade_basis_bps)) basis_premium_like|basis_premium_like        spread_rank             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.428738                     0.132145    True                   0.475748                2.158152       True               0.340987               0.340387                0.339387         94.933333               A7FF12S07_NUMERIC_CLUE           700               -0.000932         -0.032870                           -0.118851                        -0.891975                  0.495714                  712                      -0.066930                -2.336239                                  -0.475748                               -2.158152                         0.418539            712                -0.215373          -5.396408                            -2.016033                         -3.345147                   0.397472                      712                          -0.341387                    -5.532203                                      -2.181330                                   -3.267341                             0.410112           1.0    346.957947 skel_51c2bb588b20fa9e      0.996265       0.990929
a7ff7e_0f6f9ee438979cdf  Sub(CSRank(Delta(mark_index_basis_bps,1)),CSRank(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like        spread_rank             L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.426712                     0.049014    True                   0.533003                1.981815       True               0.112355               0.111755                0.110755         94.933333               A7FF12S07_NUMERIC_CLUE           688               -0.037923         -1.524823                           -0.565068                        -1.576856                  0.502907                  712                      -0.081704                -2.807095                                  -0.856542                               -2.642850                         0.462079            712                -0.085174          -2.161146                            -0.853805                         -2.851933                   0.435393                      712                          -0.112755                    -1.999716                                      -0.533003                                   -1.981815                             0.448034           1.0    118.328063 skel_af8c1327eb17d836      0.992818       0.994695
a7ff7e_d269bd0257f81477                         Mean(Mul(Delta(mark_index_basis_bps,12),taker_buy_sell_volume_ratio_last),4)   basis_premium_like|positioning_like smooth_interaction             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.425788                     0.043000    True                   2.239003                2.239003       True               0.088053               0.087453                0.086453         95.866667               A7FF12S07_NUMERIC_CLUE           704               -0.008336         -0.812832                           -0.812832                        -0.812832                  0.487216                  719                      -0.022949                -2.239003                                  -2.239003                               -2.239003                         0.447844            719                -0.043667          -3.659463                            -3.659463                         -3.659463                   0.433936                      719                          -0.088453                    -4.219895                                      -4.219895                                   -4.219895                             0.425591           1.0     94.027510 skel_8184698cb7b24c02      0.995404       0.999985
a7ff7e_e6421f87ddaf0f10                           Mean(Mul(Delta(mark_index_basis_bps,12),Abs(ZScore(realized_vol_168h))),4)    basis_premium_like|volatility_like smooth_interaction             L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.758248                     0.043914    True                   2.456687                2.456687       True               0.080621               0.080021                0.079021         95.866667               A7FF12S07_NUMERIC_CLUE           704               -0.000268         -0.022844                           -0.022844                        -0.022844                  0.482955                  719                      -0.026708                -2.456687                                  -2.456687                               -2.456687                         0.465925            719                -0.041807          -3.118932                            -3.118932                         -3.118932                   0.433936                      719                          -0.081021                    -3.786066                                      -3.786066                                   -3.786066                             0.447844           1.0     86.262319 skel_60e4266f7f901971      0.823039       0.999982
a7ff7e_6f14a06b714ad55d                   Mul(Delta(Delta(mark_index_basis_bps,12),4),ZScore(Abs(ZScore(realized_vol_24h))))    basis_premium_like|volatility_like     relative_shock             L5_vol_adjusted_return                1                     1.0                            3                 True                  0.695102                     0.025066    True                   2.525727                2.525727       True               0.063476               0.062876                0.061876         95.866667               A7FF12S07_NUMERIC_CLUE           703                0.002867          0.263278                            0.263278                         0.263278                  0.482219                  719                       0.039889                 3.893638                                   3.893638                                3.893638                         0.553547            719                 0.039182           2.525727                             2.525727                          2.525727                   0.545202                      719                           0.063876                     3.131638                                       3.131638                                    3.131638                             0.577191           1.0     69.181191 skel_dd660997d608c4f9      0.822752       0.999720
a7ff7e_392aac6696d1d60e                                           Mean(Mul(CSRank(mark_index_basis_bps),realized_vol_24h),4)    basis_premium_like|volatility_like smooth_interaction            L7_ranked_future_return                1                    -1.0                            3                 True                  0.738553                     0.025129    True                   2.848916                2.848916       True               0.032230               0.031630                0.030630         95.866667 A7FF12S07_RANK_LABEL_DIAGNOSTIC_CLUE           716               -0.018129         -2.717274                           -2.717274                        -2.717274                  0.448324                  719                      -0.019997                -2.848916                                  -2.848916                               -2.848916                         0.456189            719                -0.033029          -5.160026                            -5.160026                         -5.160026                   0.425591                      719                          -0.032630                    -5.204764                                      -5.204764                                   -5.204764                             0.425591           0.0     36.891241 skel_0cd514a276105a14      0.826487       1.000000
a7ff7e_e5cba00c24d3e3f5 Mul(Delta(Delta(mark_index_basis_bps,1),4),ZScore(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))   basis_premium_like|positioning_like     relative_shock L1_cross_sectional_relative_return                4                     1.0                            3                 True                  0.854306                     0.000824    True                   0.536484               -0.146520       True               0.000467              -0.000133               -0.001133         95.466667               A7FF12S07_NUMERIC_CLUE           692                0.000128          0.428045                            0.324986                        -0.471436                  0.502890                  716                       0.000255                 1.239471                                   0.536484                                0.406468                         0.525140            716                 0.000433           1.565119                             0.609801                         -0.126931                   0.509777                      716                           0.000867                     1.677929                                       1.039312                                   -0.146520                             0.520950           1.0      6.145694 skel_f89a6e67ef647a58      0.992818       0.999732
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
