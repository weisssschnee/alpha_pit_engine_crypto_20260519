# CRYPTO A7FF-25R3S02 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:23:05Z

## Decision

`PASS_A7FF25R3S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S02 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:23:05Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3340,
  "materialized_activity_ok_count": 167,
  "non_l7_numeric_clue_rows": 89,
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
  "portfolio_queue_count": 91,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_02_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 158,
  "selected_portfolio_queue_count": 7,
  "stage": "A7FF-25R3S02",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S02_NUMERIC_CLUE              L0_raw_forward_return     20
              A7FF25R3S02_NUMERIC_CLUE L1_cross_sectional_relative_return     19
              A7FF25R3S02_NUMERIC_CLUE  L3_liquidity_tier_relative_return     24
              A7FF25R3S02_NUMERIC_CLUE             L5_vol_adjusted_return     26
A7FF25R3S02_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return    158
    HOLD_A7FF25R3S02_CONTROL_DOMINATED              L0_raw_forward_return    175
    HOLD_A7FF25R3S02_CONTROL_DOMINATED L1_cross_sectional_relative_return    176
    HOLD_A7FF25R3S02_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    175
    HOLD_A7FF25R3S02_CONTROL_DOMINATED             L5_vol_adjusted_return    191
    HOLD_A7FF25R3S02_CONTROL_DOMINATED            L7_ranked_future_return    191
  HOLD_A7FF25R3S02_COST2_PROXY_FRAGILE              L0_raw_forward_return      1
  HOLD_A7FF25R3S02_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      2
  HOLD_A7FF25R3S02_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      1
  HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return     17
  HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return     16
  HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return     16
  HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     29
  HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     47
     HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE              L0_raw_forward_return    455
     HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    455
     HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    452
     HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    422
     HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE            L7_ranked_future_return    272
```

## Family Summary

```text
                        semantic_pair                               decision  count
basis_premium_like|basis_premium_like               A7FF25R3S02_NUMERIC_CLUE     11
basis_premium_like|basis_premium_like A7FF25R3S02_RANK_LABEL_DIAGNOSTIC_CLUE      3
basis_premium_like|basis_premium_like     HOLD_A7FF25R3S02_CONTROL_DOMINATED     57
basis_premium_like|basis_premium_like   HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE     35
basis_premium_like|basis_premium_like      HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE     74
        basis_premium_like|price_like               A7FF25R3S02_NUMERIC_CLUE     78
        basis_premium_like|price_like A7FF25R3S02_RANK_LABEL_DIAGNOSTIC_CLUE    155
        basis_premium_like|price_like     HOLD_A7FF25R3S02_CONTROL_DOMINATED    851
        basis_premium_like|price_like   HOLD_A7FF25R3S02_COST2_PROXY_FRAGILE      4
        basis_premium_like|price_like   HOLD_A7FF25R3S02_ONE_BAR_LAG_FRAGILE     90
        basis_premium_like|price_like      HOLD_A7FF25R3S02_PRE_MAY_UNSTABLE   1982
```

## Control Summary

```text
             control  median_ratio    max_ratio  rows
         one_bar_lag      0.769902 13223.086107 10020
 same_family_placebo      0.356348  4035.864999 10020
           sign_flip      0.977600   468.938648 10020
      symbol_shuffle      0.429508  3159.553667 10020
        time_shuffle      0.432742  2677.726142 10020
wrong_lag_future_24h      1.046814 11589.646593 10020
wrong_lag_stale_168h      0.521158  3651.725981 10020
```

## Selected Portfolio Queue

```text
            blueprint_id                                                      expression                         semantic_pair        motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_1c490f81c21f5f03    SafeDiv(Delta(mark_index_basis_bps,12),Abs(trade_return_1h))         basis_premium_like|price_like safe_div_abs  L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.995829                     0.124286    True                   0.711544                2.022910       True               0.199453               0.198853                0.197853         89.912500               A7FF25R3S02_NUMERIC_CLUE           700               -0.017147         -0.647103                           -0.331320                        -1.269498                  0.487143                  712                      -0.053227                -2.160822                                  -0.792624                               -2.022910                         0.467697            712                -0.091015          -2.853203                            -0.711544                         -3.876046                   0.431180                      712                          -0.199853                    -4.088527                                      -1.371370                                   -3.548069                             0.429775           1.0    204.857193 skel_136259b72205469f      0.960449       0.998735
a7ff24r_892545e2049b6eba    SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,12)))         basis_premium_like|price_like safe_div_abs  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.906357                     0.100026    True                   1.258755                1.852687       True               0.181475               0.180875                0.179875         94.568056               A7FF25R3S02_NUMERIC_CLUE           704               -0.007253         -0.352534                           -0.202309                        -0.503944                  0.481534                  716                      -0.057625                -2.552633                                  -1.258755                               -2.639072                         0.424581            716                -0.083025          -2.824995                            -1.442336                         -1.852687                   0.435754                      716                          -0.181875                    -4.977934                                      -2.390787                                   -3.388778                             0.423184           1.0    186.968184 skel_a2f58ee62d9e7ad2      0.990418       0.987664
a7ff24r_bcc3435cf539d883            Sub(mark_index_basis_bps,Mean(premium_close_bps,12)) basis_premium_like|basis_premium_like          sub  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.193843                     0.041617    True                   7.119921                7.119921       True               0.152806               0.152206                0.151206         95.866667               A7FF25R3S02_NUMERIC_CLUE           708               -0.022940         -2.024484                           -2.024484                        -2.024484                  0.475989                  719                      -0.092010                -9.100628                                  -9.100628                               -9.100628                         0.340751            719                -0.142002          -9.744496                            -9.744496                         -9.744496                   0.301808                      719                          -0.153206                    -7.119921                                      -7.119921                                   -7.119921                             0.369958           1.0    159.012128 skel_f8484b844efd270f      0.996553       0.999111
a7ff24r_809e5867ebe18c47 SafeDiv(premium_close_bps,Abs(ZScore(Mean(trade_return_1h,8))))         basis_premium_like|price_like safe_div_abs  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.764264                     0.040941    True                   1.692916                1.692916       True               0.069717               0.069117                0.068117         95.866667               A7FF25R3S02_NUMERIC_CLUE           708               -0.024300         -2.036568                           -2.036568                        -2.036568                  0.449153                  668                      -0.058094                -3.491367                                  -3.491367                               -3.491367                         0.387725            713                -0.030100          -1.692916                            -1.692916                         -1.692916                   0.469846                      719                          -0.070117                    -3.269673                                      -3.269673                                   -3.269673                             0.443672           1.0     75.352645 skel_c80f62c274b367a9      0.995404       0.663952
a7ff24r_ad7b309da8535408                  Mul(Mean(premium_close_bps,2),trade_return_1h)         basis_premium_like|price_like          mul  L5_vol_adjusted_return                8                     1.0                            3                 True                  0.834547                     0.045169    True                   0.140948               -0.948553       True               0.064781               0.064181                0.063181         94.933333               A7FF25R3S02_NUMERIC_CLUE           711                0.056358          1.669327                            0.286537                        -0.533939                  0.555556                  712                       0.126068                 3.250746                                   1.299629                               -0.135829                         0.574438            712                 0.083561           1.936407                             0.950219                         -0.948553                   0.546348                      712                           0.065181                     0.947182                                       0.140948                                   -0.171972                             0.557584           1.0     70.346747 skel_0994b3a36a4d53ba      0.999138       0.794554
a7ff24r_e610c5a1e8d4691c                       Mul(mark_index_basis_bps,trade_return_1h)         basis_premium_like|price_like          mul L7_ranked_future_return                1                     1.0                            3                 True                  0.465917                     0.024001    True                   3.691443                3.691443       True               0.042337               0.041737                0.040737         95.866667 A7FF25R3S02_RANK_LABEL_DIAGNOSTIC_CLUE           719                0.019807          2.981536                            2.981536                         2.981536                  0.541029                  719                       0.022194                 3.691443                                   3.691443                                3.691443                         0.556328            719                 0.030965           5.411709                             5.411709                          5.411709                   0.552156                      719                           0.042737                     7.121444                                       7.121444                                    7.121444                             0.577191           0.0     47.271029 skel_337820bc5afcf6cc      0.999425       0.953264
a7ff24r_95153311226880bf                 Mul(mark_index_basis_bps,Sign(trade_return_1h))         basis_premium_like|price_like   gated_sign L7_ranked_future_return                1                     1.0                            3                 True                  0.936734                     0.013725    True                   2.121475                2.121475       True               0.034825               0.034225                0.033225         95.866667 A7FF25R3S02_RANK_LABEL_DIAGNOSTIC_CLUE           719                0.012402          2.171070                            2.171070                         2.171070                  0.524339                  719                       0.012260                 2.121475                                   2.121475                                2.121475                         0.529903            719                 0.022174           4.072971                             4.072971                          4.072971                   0.553547                      719                           0.035225                     6.193901                                       6.193901                                    6.193901                             0.578581           0.0     39.288172 skel_d9d4f69744bac825      0.999425       0.953264
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
