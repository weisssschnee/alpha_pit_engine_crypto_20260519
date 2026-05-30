# CRYPTO A7FF-25R3S06 EXPANDED NUMERIC PROBE

Generated: 2026-05-30T08:34:50Z

## Decision

`PASS_A7FF25R3S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH`

A7FF-25R3S06 materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R3S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T08:34:50Z",
  "input_blueprint_count": 200,
  "label_response_rows": 3300,
  "materialized_activity_ok_count": 165,
  "non_l7_numeric_clue_rows": 10,
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
  "portfolio_queue_count": 67,
  "queue_limit": 200,
  "queue_offset": 0,
  "queue_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_shard_06_queue.csv",
  "queue_total_rows": 200,
  "rank_label_diagnostic_clue_rows": 155,
  "selected_portfolio_queue_count": 13,
  "stage": "A7FF-25R3S06",
  "uses_may": false
}
```

## Decision Counts

```text
                              decision                       label_family  count
              A7FF25R3S06_NUMERIC_CLUE              L0_raw_forward_return      3
              A7FF25R3S06_NUMERIC_CLUE L1_cross_sectional_relative_return      2
              A7FF25R3S06_NUMERIC_CLUE  L3_liquidity_tier_relative_return      2
              A7FF25R3S06_NUMERIC_CLUE             L5_vol_adjusted_return      3
A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE            L7_ranked_future_return    155
    HOLD_A7FF25R3S06_CONTROL_DOMINATED              L0_raw_forward_return    187
    HOLD_A7FF25R3S06_CONTROL_DOMINATED L1_cross_sectional_relative_return    187
    HOLD_A7FF25R3S06_CONTROL_DOMINATED  L3_liquidity_tier_relative_return    225
    HOLD_A7FF25R3S06_CONTROL_DOMINATED             L5_vol_adjusted_return    196
    HOLD_A7FF25R3S06_CONTROL_DOMINATED            L7_ranked_future_return    324
  HOLD_A7FF25R3S06_COST2_PROXY_FRAGILE L1_cross_sectional_relative_return      1
  HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE              L0_raw_forward_return      5
  HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE L1_cross_sectional_relative_return      5
  HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE  L3_liquidity_tier_relative_return      5
  HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE             L5_vol_adjusted_return      3
  HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE            L7_ranked_future_return      6
     HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE              L0_raw_forward_return    465
     HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE L1_cross_sectional_relative_return    465
     HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE  L3_liquidity_tier_relative_return    428
     HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE             L5_vol_adjusted_return    458
     HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE            L7_ranked_future_return    175
```

## Family Summary

```text
                     semantic_pair                               decision  count
basis_premium_like|volatility_like A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE     70
basis_premium_like|volatility_like     HOLD_A7FF25R3S06_CONTROL_DOMINATED    687
basis_premium_like|volatility_like   HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE     11
basis_premium_like|volatility_like      HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE   1452
        price_like|volatility_like               A7FF25R3S06_NUMERIC_CLUE     10
        price_like|volatility_like A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE     85
        price_like|volatility_like     HOLD_A7FF25R3S06_CONTROL_DOMINATED    432
        price_like|volatility_like   HOLD_A7FF25R3S06_COST2_PROXY_FRAGILE      1
        price_like|volatility_like   HOLD_A7FF25R3S06_ONE_BAR_LAG_FRAGILE     13
        price_like|volatility_like      HOLD_A7FF25R3S06_PRE_MAY_UNSTABLE    539
```

## Control Summary

```text
             control  median_ratio   max_ratio  rows
         one_bar_lag      0.867009  976.317079  9900
 same_family_placebo      0.277577 2417.273007  9900
           sign_flip      1.009867  232.538462  9900
      symbol_shuffle      0.431492 2390.751456  9900
        time_shuffle      0.440493 2869.710457  9900
wrong_lag_future_24h      2.826016 5221.471479  9900
wrong_lag_stale_168h      0.449576 1091.619100  9900
```

## Selected Portfolio Queue

```text
            blueprint_id                                                                                   expression                      semantic_pair       motif            label_family  label_horizon_h  orientation_from_train  premay_positive_split_count  premay_all_positive  control_ratio_premay_max  one_bar_lag_recent_oriented  lag_ok  robust_median_tstat_floor  robust_min_tstat_floor  robust_ok  cost2_recent_oriented  cost5_recent_oriented  cost10_recent_oriented  avg_n_obs_recent                               decision  train_2024_n  train_2024_mean_spread  train_2024_tstat  train_2024_nonoverlap_median_tstat  train_2024_nonoverlap_min_tstat  train_2024_positive_rate  validation_2025H1_n  validation_2025H1_mean_spread  validation_2025H1_tstat  validation_2025H1_nonoverlap_median_tstat  validation_2025H1_nonoverlap_min_tstat  validation_2025H1_positive_rate  test_2025H2_n  test_2025H2_mean_spread  test_2025H2_tstat  test_2025H2_nonoverlap_median_tstat  test_2025H2_nonoverlap_min_tstat  test_2025H2_positive_rate  recent_oos_2026JanApr_n  recent_oos_2026JanApr_mean_spread  recent_oos_2026JanApr_tstat  recent_oos_2026JanApr_nonoverlap_median_tstat  recent_oos_2026JanApr_nonoverlap_min_tstat  recent_oos_2026JanApr_positive_rate  non_l7_bonus  score_no_may          skeleton_key  finite_share  nonzero_share
a7ff24r_0d2e211c74b8ab69                                                       Mul(realized_vol_168h,trade_return_1h)         price_like|volatility_like         mul  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.871767                     0.024460    True                   2.183279                2.183279       True               0.076715               0.076115                0.075115         95.866667               A7FF25R3S06_NUMERIC_CLUE           719               -0.071018         -4.375666                           -4.375666                        -4.375666                  0.413074                  719                      -0.033762                -2.183279                                  -2.183279                               -2.183279                         0.435327            719                -0.083292          -4.826727                            -4.826727                         -4.826727                   0.390821                      719                          -0.077115                    -3.045822                                      -3.045822                                   -3.045822                             0.382476           1.0     82.243121 skel_337820bc5afcf6cc      0.827348       0.964160
a7ff24r_56da73ff4908bd30                    Sub(CSRank(ZScore(Mean(premium_close_bps,12))),CSRank(realized_vol_168h)) basis_premium_like|volatility_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.501542                     0.075487    True                   1.157290                0.284818       True               0.074254               0.073654                0.072654         92.800000 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           685                0.083071         11.471194                            2.358683                         1.436955                  0.715328                  696                       0.046199                 5.350870                                   1.157290                                0.284818                         0.560345            696                 0.051899           8.003412                             1.615523                          0.821393                   0.599138                      696                           0.074654                    10.966869                                       2.214788                                    1.518330                             0.660920           0.0     79.152194 skel_206e713fb3d9a164      0.824188       0.989166
a7ff24r_3c67ad4c348bba31 Sub(CSRank(ZScore(Mean(mark_index_basis_bps,12))),CSRank(ZScore(Mean(realized_vol_168h,4)))) basis_premium_like|volatility_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.831940                     0.073692    True                   1.181088                0.434016       True               0.072144               0.071544                0.070544         92.800000 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           685                0.059145          6.794922                            1.442468                         0.548952                  0.646715                  696                       0.049298                 5.359445                                   1.181088                                0.434016                         0.561782            696                 0.071319           9.806027                             1.873074                          0.861504                   0.633621                      696                           0.072544                     9.546334                                       2.014175                                    1.102381                             0.652299           0.0     76.711936 skel_f4061a64df347a31      0.824188       0.988425
a7ff24r_4ba0720360644c7f                                     Sub(CSRank(premium_close_bps),CSRank(realized_vol_168h)) basis_premium_like|volatility_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.764669                     0.062040    True                   0.742966                0.028480       True               0.058685               0.058085                0.057085         92.800000 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           696                0.069959          9.484643                            2.046861                         0.647441                  0.670977                  696                       0.033316                 3.710233                                   0.742966                                0.035098                         0.531609            696                 0.043066           6.771865                             1.347903                          0.028480                   0.597701                      696                           0.059085                     8.749756                                       1.748582                                    1.065626                             0.646552           0.0     63.320412 skel_293cae94cfd91548      0.827348       0.991149
a7ff24r_8f6351646309de9d                             Sub(CSRank(premium_close_bps),CSRank(Mean(realized_vol_168h,2))) basis_premium_like|volatility_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.692546                     0.061085    True                   0.717964               -0.034811       True               0.058073               0.057473                0.056473         92.800000 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           695                0.068969          9.371184                            1.976969                         0.587509                  0.667626                  696                       0.033967                 3.784333                                   0.717964                                0.131815                         0.531609            696                 0.042017           6.611189                             1.294404                         -0.034811                   0.593391                      696                           0.058473                     8.644485                                       1.741574                                    0.898730                             0.645115           0.0     62.780410 skel_1a1b3fb29dff7328      0.827061       0.991139
a7ff24r_90fca106843c7901                     Sub(CSRank(premium_close_bps),CSRank(ZScore(Mean(realized_vol_168h,2)))) basis_premium_like|volatility_like spread_rank L7_ranked_future_return               24                     1.0                            3                 True                  0.820751                     0.061085    True                   0.717964               -0.034811       True               0.058073               0.057473                0.056473         92.800000 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           695                0.068969          9.371184                            1.976969                         0.587509                  0.667626                  696                       0.033967                 3.784333                                   0.717964                                0.131815                         0.531609            696                 0.042017           6.611189                             1.294404                         -0.034811                   0.593391                      696                           0.058473                     8.644485                                       1.741574                                    0.898730                             0.645115           0.0     62.652205 skel_a923757a8885923c      0.827061       0.991139
a7ff24r_18494b19560b1e1c                                                 Mul(realized_vol_168h,Sign(trade_return_1h))         price_like|volatility_like  gated_sign  L5_vol_adjusted_return                4                    -1.0                            3                 True                  0.914522                     0.019153    True                   0.781927                1.110504       True               0.054549               0.053949                0.052949         95.466667               A7FF25R3S06_NUMERIC_CLUE           716               -0.031562         -1.169763                           -0.855690                        -1.467739                  0.483240                  716                      -0.058161                -2.249400                                  -1.168021                               -1.760176                         0.444134            716                -0.101503          -3.654879                            -1.618057                         -2.973802                   0.423184                      716                          -0.054949                    -1.408280                                      -0.781927                                   -1.110504                             0.455307           1.0     60.034304 skel_d9d4f69744bac825      0.827348       0.964160
a7ff24r_1a6cd63fcb1c2549                                      Mean(Mul(Mean(realized_vol_168h,12),trade_return_1h),4)         price_like|volatility_like  smooth_mul L7_ranked_future_return                8                    -1.0                            3                 True                  0.578550                     0.038326    True                   2.707716                4.234195       True               0.051454               0.050854                0.049854         94.933333 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           698               -0.046914         -5.680599                           -2.112378                        -2.881796                  0.424069                  712                      -0.058468                -7.711846                                  -2.731706                               -4.234195                         0.375000            712                -0.054070          -7.812457                            -3.015691                         -4.398074                   0.391854                      712                          -0.051854                    -7.536698                                      -2.707716                                   -4.459288                             0.372191           0.0     56.275740 skel_8184698cb7b24c02      0.823327       0.999309
a7ff24r_99a670aaf2c0cccc                                               Mean(Mul(realized_vol_168h,trade_return_1h),4)         price_like|volatility_like  smooth_mul L7_ranked_future_return                8                    -1.0                            3                 True                  0.603775                     0.037077    True                   2.716131                4.083512       True               0.051084               0.050484                0.049484         94.933333 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.049012         -6.002844                           -2.262398                        -3.083044                  0.420310                  712                      -0.058488                -7.692352                                  -2.770978                               -4.169850                         0.375000            712                -0.052918          -7.651710                            -2.966534                         -4.320987                   0.383427                      712                          -0.051484                    -7.474939                                      -2.716131                                   -4.083512                             0.372191           0.0     55.879966 skel_356a5f3fab58eb27      0.826487       0.999312
a7ff24r_07fd133f7d8485e9                                        Mean(Mul(realized_vol_24h,Mean(trade_return_1h,4)),4)         price_like|volatility_like  smooth_mul L7_ranked_future_return                8                    -1.0                            3                 True                  0.758192                     0.038068    True                   2.369260                4.101074       True               0.049052               0.048452                0.047452         94.933333 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           706               -0.036486         -4.431245                           -1.418387                        -2.299966                  0.439093                  712                      -0.059306                -7.867792                                  -2.558206                               -4.248042                         0.386236            712                -0.050409          -7.643053                            -2.369260                         -4.433731                   0.394663                      712                          -0.049452                    -7.740700                                      -3.155795                                   -4.101074                             0.393258           0.0     53.693909 skel_644ba0ee0d0e38ee      0.825625       0.999880
a7ff24r_83eaca890e3a46b2                                Mean(Mul(realized_vol_24h,ZScore(Mean(trade_return_1h,2))),4)         price_like|volatility_like  smooth_mul L7_ranked_future_return                4                    -1.0                            3                 True                  0.770749                     0.024271    True                   2.768452                3.517657       True               0.042966               0.042366                0.041366         95.466667 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           712               -0.053906         -7.372837                           -3.826184                        -4.003182                  0.386236                  716                      -0.041246                -6.396136                                  -3.193694                               -4.408468                         0.409218            716                -0.042609          -6.600667                            -2.768452                         -5.269094                   0.421788                      716                          -0.043366                    -6.138772                                      -3.135079                                   -3.517657                             0.416201           0.0     47.595011 skel_44a246af570899bb      0.826199       1.000000
a7ff24r_4f5fad181e850eac                                 Mul(realized_vol_168h,Sign(ZScore(Mean(trade_return_1h,2))))         price_like|volatility_like  gated_sign  L5_vol_adjusted_return                1                    -1.0                            3                 True                  0.733619                     0.010591    True                   1.991255                1.991255       True               0.039880               0.039280                0.038280         95.866667               A7FF25R3S06_NUMERIC_CLUE           718               -0.018441         -1.583588                           -1.583588                        -1.583588                  0.469359                  719                      -0.035740                -3.126309                                  -3.126309                               -3.126309                         0.440890            719                -0.048140          -3.297202                            -3.297202                         -3.297202                   0.450626                      719                          -0.040280                    -1.991255                                      -1.991255                                   -1.991255                             0.452017           1.0     45.546620 skel_c80f62c274b367a9      0.827061       1.000000
a7ff24r_58290e1991dd8e5d                                Mean(Mul(ZScore(Mean(realized_vol_24h,8)),trade_return_1h),4)         price_like|volatility_like  smooth_mul L7_ranked_future_return                1                    -1.0                            3                 True                  0.845106                     0.008604    True                   1.191766                1.191766       True               0.007259               0.006659                0.005659         95.866667 A7FF25R3S06_RANK_LABEL_DIAGNOSTIC_CLUE           709               -0.020580         -2.707108                           -2.707108                        -2.707108                  0.462623                  719                      -0.012145                -1.581877                                  -1.581877                               -1.581877                         0.489569            719                -0.024575          -3.752236                            -3.752236                         -3.752236                   0.433936                      719                          -0.007659                    -1.191766                                      -1.191766                                   -1.191766                             0.467316           0.0     11.813824 skel_1717bdff259036b1      0.824476       0.999310
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
