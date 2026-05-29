# CRYPTO A7FF-10S01 EXPANDED NUMERIC PROBE

Generated: 2026-05-29T19:46:31Z

## Decision

`PASS_A7FF10S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-10S01 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF10S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T19:46:31Z",
  "input_blueprint_count": 96,
  "label_response_rows": 1920,
  "materialized_activity_ok_count": 96,
  "non_l7_numeric_clue_rows": 112,
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
  "portfolio_queue_count": 35,
  "queue_limit": 96,
  "queue_offset": 96,
  "rank_label_diagnostic_clue_rows": 23,
  "selected_portfolio_queue_count": 14,
  "stage": "A7FF-10S01",
  "uses_may": false
}
```

## Decision Counts

```text
                            decision                       label_family  count
              A7FF10S01_NUMERIC_CLUE              L0_raw_forward_return     26
              A7FF10S01_NUMERIC_CLUE L1_cross_sectional_relative_return     25
              A7FF10S01_NUMERIC_CLUE  L3_liquidity_tier_relative_return     32
              A7FF10S01_NUMERIC_CLUE             L5_vol_adjusted_return     29
A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return     23
    HOLD_A7FF10S01_CONTROL_DOMINATED              L0_raw_forward_return    128
    HOLD_A7FF10S01_CONTROL_DOMINATED L1_cross_sectional_relative_return    128
    HOLD_A7FF10S01_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    113
    HOLD_A7FF10S01_CONTROL_DOMINATED             L5_vol_adjusted_return    101
    HOLD_A7FF10S01_CONTROL_DOMINATED            L7_ranked_future_return    117
  HOLD_A7FF10S01_COST2_PROXY_FRAGILE              L0_raw_forward_return      3
  HOLD_A7FF10S01_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      4
  HOLD_A7FF10S01_COST2_PROXY_FRAGILE  L3_liquidity_tier_relative_return      3
  HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      7
  HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      7
  HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      6
  HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return     25
  HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return     61
     HOLD_A7FF10S01_PRE_MAY_UNSTABLE              L0_raw_forward_return    220
     HOLD_A7FF10S01_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    220
     HOLD_A7FF10S01_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    230
     HOLD_A7FF10S01_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    229
     HOLD_A7FF10S01_PRE_MAY_UNSTABLE            L7_ranked_future_return    183
```

## Family Summary

```text
                      semantic_pair                             decision  count
basis_premium_like|positioning_like               A7FF10S01_NUMERIC_CLUE      3
basis_premium_like|positioning_like A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE      2
basis_premium_like|positioning_like     HOLD_A7FF10S01_CONTROL_DOMINATED     77
basis_premium_like|positioning_like   HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE     20
basis_premium_like|positioning_like      HOLD_A7FF10S01_PRE_MAY_UNSTABLE    198
 basis_premium_like|volatility_like               A7FF10S01_NUMERIC_CLUE    109
 basis_premium_like|volatility_like A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE     21
 basis_premium_like|volatility_like     HOLD_A7FF10S01_CONTROL_DOMINATED    510
 basis_premium_like|volatility_like   HOLD_A7FF10S01_COST2_PROXY_FRAGILE     10
 basis_premium_like|volatility_like   HOLD_A7FF10S01_ONE_BAR_LAG_FRAGILE     86
 basis_premium_like|volatility_like      HOLD_A7FF10S01_PRE_MAY_UNSTABLE    884
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.695957  285.371858  5760
 same_family_placebo      0.306389  884.667254  5760
           sign_flip      1.012960  285.205118  5760
      symbol_shuffle      0.395863  803.216070  5760
        time_shuffle      0.400824  934.989235  5760
wrong_lag_future_24h      1.322675 2576.604009  5760
wrong_lag_stale_168h      0.479855  287.750883  5760
```

## Selected Portfolio Queue

```text
           blueprint_id                                                                    expression                       semantic_pair motif                      label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                             decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff7e_0eab80fdecd0fd9c               Mul(Delta(mark_index_basis_bps,12),Decay(realized_vol_168h,24))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                8                    -1.0                            3                 True                  0.863198                     0.156942    True                   0.188143                1.806141       True               0.296600               0.296000                0.295000         94.933333               A7FF10S01_NUMERIC_CLUE           689               -0.013621         -0.442820                           -0.021752                        -1.581733                  0.484761                  712                      -0.038822                -1.391113                                  -0.188143                               -2.237688                         0.450843            712                -0.080950          -1.960691                            -0.619841                         -1.806141                   0.452247                      712                          -0.297000                    -4.201826                                      -1.794453                                   -2.879123                             0.435393           1.0    302.136794 skel_8727d93aac220fc6      0.820741       0.998290
a7ff7e_0401884a75b317df                 Mul(Delta(mark_index_basis_bps,12),CSRank(realized_vol_168h))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.666807                     0.133438    True                   0.575366                1.590916       True               0.248253               0.247653                0.246653         95.466667               A7FF10S01_NUMERIC_CLUE           704               -0.018315         -0.867385                           -0.513523                        -1.383969                  0.502841                  716                      -0.039111                -1.973359                                  -0.575366                               -2.437315                         0.479050            716                -0.079861          -2.521436                            -1.244291                         -1.590916                   0.420391                      716                          -0.248653                    -5.288191                                      -2.657643                                   -2.853290                             0.425978           1.0    253.986495 skel_136259b72205469f      0.823901       0.998297
a7ff7e_2ece816e86d97603                         Mul(Delta(mark_index_basis_bps,12),realized_vol_168h)  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.944643                     0.114693    True                   0.774770                1.692633       True               0.237721               0.237121                0.236121         95.466667               A7FF10S01_NUMERIC_CLUE           704               -0.020055         -0.920312                           -0.752704                        -1.477095                  0.484375                  716                      -0.041191                -2.116409                                  -0.774770                               -2.784116                         0.463687            716                -0.068324          -2.190891                            -0.998914                         -1.692633                   0.432961                      716                          -0.238121                    -5.208504                                      -2.681855                                   -3.173869                             0.425978           1.0    243.175894 skel_0994b3a36a4d53ba      0.823901       0.998297
a7ff7e_a88d2c050432e450                Mul(ZScore(mark_index_basis_bps),TSRank(realized_vol_168h,24))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.757258                     0.043353    True                   5.528753                5.528753       True               0.128568               0.127968                0.126968         95.866667               A7FF10S01_NUMERIC_CLUE           696               -0.009452         -0.862275                           -0.862275                        -0.862275                  0.481322                  719                      -0.086964                -7.727085                                  -7.727085                               -7.727085                         0.354659            719                -0.103751          -7.048943                            -7.048943                         -7.048943                   0.365786                      719                          -0.128968                    -5.528753                                      -5.528753                                   -5.528753                             0.400556           1.0    134.211084 skel_e47b3d7310e98dd5      0.820741       1.000000
a7ff7e_dbde891548032719     Mul(Clip(ZScore(mark_index_basis_bps),-3,3),TSRank(realized_vol_168h,24))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.757258                     0.043353    True                   5.528753                5.528753       True               0.128568               0.127968                0.126968         95.866667               A7FF10S01_NUMERIC_CLUE           696               -0.009728         -0.885976                           -0.885976                        -0.885976                  0.481322                  719                      -0.086910                -7.722374                                  -7.722374                               -7.722374                         0.354659            719                -0.103751          -7.048943                            -7.048943                         -7.048943                   0.365786                      719                          -0.128968                    -5.528753                                      -5.528753                                   -5.528753                             0.400556           1.0    134.211084 skel_b04640f9c6171dfc      0.820741       1.000000
a7ff7e_5ebfb876adf8c2c8            Mul(Delta(mark_index_basis_bps,24),Abs(ZScore(realized_vol_168h)))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.860810                     0.035330    True                   4.758636                4.758636       True               0.127043               0.126443                0.125443         95.866667               A7FF10S01_NUMERIC_CLUE           695               -0.033405         -2.915463                           -2.915463                        -2.915463                  0.456115                  719                      -0.050162                -4.758636                                  -4.758636                               -4.758636                         0.406120            719                -0.076846          -5.756261                            -5.756261                         -5.756261                   0.399166                      719                          -0.127443                    -6.489537                                      -6.489537                                   -6.489537                             0.390821           1.0    132.582496 skel_069f2015163fa7ef      0.820454       0.997556
a7ff7e_4802e16816d12d83                           Mul(CSRank(mark_index_basis_bps),realized_vol_168h)  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.401921                     0.032485    True                   5.260383                5.260383       True               0.126224               0.125624                0.124624         95.866667               A7FF10S01_NUMERIC_CLUE           719               -0.017443         -1.470793                           -1.470793                        -1.470793                  0.464534                  719                      -0.068951                -6.253869                                  -6.253869                               -6.253869                         0.376912            719                -0.126470          -8.778964                            -8.778964                         -8.778964                   0.337969                      719                          -0.126624                    -5.260383                                      -5.260383                                   -5.260383                             0.436718           1.0    132.222163 skel_37ba6246678096b3      0.827348       1.000000
a7ff7e_6a41a7577c84bcb4                        Mul(mark_index_basis_bps,TSRank(realized_vol_168h,24))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.896740                     0.033901    True                   5.354624                5.354624       True               0.125176               0.124576                0.123576         95.866667               A7FF10S01_NUMERIC_CLUE           696               -0.003648         -0.316299                           -0.316299                        -0.316299                  0.489943                  719                      -0.086446                -8.142470                                  -8.142470                               -8.142470                         0.342142            719                -0.101132          -6.309745                            -6.309745                         -6.309745                   0.388039                      719                          -0.125576                    -5.354624                                      -5.354624                                   -5.354624                             0.406120           1.0    130.679731 skel_f8484b844efd270f      0.820741       0.987027
a7ff7e_b1c7f75458ff1db4                   Mul(CSRank(mark_index_basis_bps),CSRank(realized_vol_168h))  basis_premium_like|volatility_like   mul            L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.425914                     0.024611    True                   3.658077                3.658077       True               0.091546               0.090946                0.089946         95.866667               A7FF10S01_NUMERIC_CLUE           719               -0.018766         -1.441579                           -1.441579                        -1.441579                  0.470097                  719                      -0.044833                -3.658077                                  -3.658077                               -3.658077                         0.401947            719                -0.089962          -6.675218                            -6.675218                         -6.675218                   0.400556                      719                          -0.091946                    -3.806955                                      -3.806955                                   -3.806955                             0.440890           1.0     97.519977 skel_293cae94cfd91548      0.827348       1.000000
a7ff7e_1398647649b56f7f                      Mul(Abs(ZScore(mark_index_basis_bps)),realized_vol_168h)  basis_premium_like|volatility_like   mul           L7_ranked_future_return                8                    -1.0                            3                 True                  0.684797                     0.048849    True                   0.936124                1.605388       True               0.055712               0.055112                0.054112         94.933333 A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.024362         -4.446238                           -1.640405                        -2.555082                  0.443820                  712                      -0.014806                -2.602599                                  -0.940817                               -1.605388                         0.462079            712                -0.016189          -2.871035                            -0.936124                         -2.289177                   0.448034                      712                          -0.056112                    -8.559124                                      -3.283254                                   -3.852169                             0.384831           0.0     60.426704 skel_7be1b7a1db5c1738      0.827348       1.000000
a7ff7e_6d013e20536da283            Mul(Abs(ZScore(mark_index_basis_bps)),Decay(realized_vol_168h,24))  basis_premium_like|volatility_like   mul           L7_ranked_future_return                8                    -1.0                            3                 True                  0.724737                     0.047369    True                   0.786117                1.641397       True               0.054154               0.053554                0.052554         94.933333 A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE           689               -0.025078         -4.490966                           -1.504358                        -2.629128                  0.447025                  712                      -0.013942                -2.441694                                  -0.882954                               -1.641397                         0.459270            712                -0.013480          -2.397634                            -0.786117                         -2.247599                   0.459270                      712                          -0.054554                    -8.310365                                      -3.143303                                   -3.683636                             0.389045           0.0     58.829710 skel_7c564c472f890218      0.820741       1.000000
a7ff7e_1af09de784d79028 Mul(mark_index_basis_bps,Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)) basis_premium_like|positioning_like   mul            L5_vol_adjusted_return                1                     1.0                            3                 True                  0.987030                     0.019498    True                   2.505105                2.505105       True               0.046164               0.045564                0.044564         95.866667               A7FF10S01_NUMERIC_CLUE           719                0.014054          1.590327                            1.590327                         1.590327                  0.520167                  719                       0.025117                 2.512964                                   2.512964                                2.512964                         0.538248            719                 0.046079           3.561489                             3.561489                          3.561489                   0.573018                      719                           0.046564                     2.505105                                       2.505105                                    2.505105                             0.521558           1.0     51.577468 skel_593666ed3f85046b      0.999713       0.987410
a7ff7e_8311d90eeec7b88e   Mul(Abs(ZScore(mark_index_basis_bps)),Clip(ZScore(realized_vol_168h),-3,3))  basis_premium_like|volatility_like   mul           L7_ranked_future_return                1                    -1.0                            3                 True                  0.629320                     0.022168    True                   1.656603                1.656603       True               0.025786               0.025186                0.024186         95.866667 A7FF10S01_RANK_LABEL_DIAGNOSTIC_CLUE           719               -0.024254         -3.013729                           -3.013729                        -3.013729                  0.453408                  719                      -0.013384                -1.656603                                  -1.656603                               -1.656603                         0.457580            719                -0.025533          -3.984281                            -3.984281                         -3.984281                   0.435327                      719                          -0.026186                    -4.073378                                      -4.073378                                   -4.073378                             0.425591           0.0     30.556902 skel_26519c5fcf83ddd8      0.827348       1.000000
a7ff7e_874d7bfb6c949fc1        Mul(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(realized_vol_168h))  basis_premium_like|volatility_like   mul L3_liquidity_tier_relative_return                1                    -1.0                            3                 True                  0.971789                     0.000391    True                   3.461830                3.461830       True               0.000827               0.000227               -0.000773         95.866667               A7FF10S01_NUMERIC_CLUE           719               -0.000300         -1.588766                           -1.588766                        -1.588766                  0.471488                  719                      -0.000706                -6.482580                                  -6.482580                               -6.482580                         0.375522            719                -0.001229          -7.319507                            -7.319507                         -7.319507                   0.346314                      719                          -0.001227                    -3.461830                                      -3.461830                                   -3.461830                             0.464534           1.0      6.255588 skel_3363cfb4025bd87d      0.827348       1.000000
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
