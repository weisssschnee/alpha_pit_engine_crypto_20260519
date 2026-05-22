# Crypto A7V-7 Failure Attribution

- generated_at: `2026-05-22T02:14:05Z`
- decision: `HOLD_A7V7_ACTIVITY_LIQUIDITY_CLUES_FAIL_MAY_STRESS`
- executes_search: `False`
- executes_replay: `forensic_recompute_on_a7v6_clues_only`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7V-7 recomputes hourly and symbol-level attribution for the five A7V-6 pre-May dominance clues. It is a failure-attribution audit, not a candidate promotion step.

May is still stress-only. The audit uses May only to explain why the pre-May clues fail; it does not tune formulas, thresholds, or rankings.

## Candidate Failure Attribution

| candidate_id                                              | production_family                    | expression                           | source_fields          | source_field_families   |   may_net_sum_10bps |   may_gross_sum |   may_fee_sum |   may_positive_hour_rate |   may_loss_hour_count |   may_active_hour_count | may_worst_hour            |   may_worst_hour_net |   may_top10_loss_share |   may_total_loss_abs |
|:----------------------------------------------------------|:-------------------------------------|:-------------------------------------|:-----------------------|:------------------------|--------------------:|----------------:|--------------:|-------------------------:|----------------------:|------------------------:|:--------------------------|---------------------:|-----------------------:|---------------------:|
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | rolling_self_reproduction            | Decay(agg_notional_10k_100k,4)       | agg_notional_10k_100k  | activity_liquidity      |           -0.249144 |       -0.214644 |        0.0345 |                 0.522772 |                   217 |                     480 | 2026-05-08T13:00:00+00:00 |           -0.0250278 |               0.191367 |              1.08553 |
| a7v3_rolling_self_reproduction_12_519354de8b22            | rolling_self_reproduction            | Decay(agg_trade_count_1k_10k,4)      | agg_trade_count_1k_10k | activity_liquidity      |           -0.270483 |       -0.233983 |        0.0365 |                 0.510891 |                   223 |                     480 | 2026-05-08T13:00:00+00:00 |           -0.0250278 |               0.195104 |              1.06906 |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | rolling_self_reproduction            | Decay(agg_notional_1k_10k,4)         | agg_notional_1k_10k    | activity_liquidity      |           -0.247142 |       -0.212642 |        0.0345 |                 0.522772 |                   217 |                     480 | 2026-05-08T13:00:00+00:00 |           -0.0250278 |               0.195364 |              1.06763 |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | rolling_self_reproduction            | Decay(agg_notional,4)                | agg_notional           | activity_liquidity      |           -0.213944 |       -0.192444 |        0.0215 |                 0.520792 |                   218 |                     480 | 2026-05-08T13:00:00+00:00 |           -0.0250278 |               0.195524 |              1.06676 |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_100_1k) | agg_notional_100_1k    | activity_liquidity      |           -0.178382 |       -0.172882 |        0.0055 |                 0.528713 |                   214 |                     480 | 2026-05-08T13:00:00+00:00 |           -0.0250278 |               0.204354 |              1.03434 |

## May Symbol Contribution Summary

| symbol   |   rows |   gross_pnl_sum_may |   avg_abs_position |   long_hours |   short_hours |
|:---------|-------:|--------------------:|-------------------:|-------------:|--------------:|
| BTCUSDT  |      5 |            0.716156 |          0.381188  |         1925 |             0 |
| ETHUSDT  |      5 |           -0.686788 |          0.0956436 |          474 |             9 |
| SOLUSDT  |      5 |           -1.05596  |          0.473663  |            1 |          2391 |

## Symbol Contribution By Candidate

| candidate_id                                              | symbol   |   gross_pnl_sum_may |   positive_hour_rate_may |   long_hours |   short_hours |   flat_hours |   avg_position |   avg_abs_position |
|:----------------------------------------------------------|:---------|--------------------:|-------------------------:|-------------:|--------------:|-------------:|---------------:|-------------------:|
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | BTCUSDT  |           0.163512  |                0.418699  |          357 |             0 |          148 |      0.353465  |         0.353465   |
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | ETHUSDT  |          -0.196004  |                0.103659  |          122 |             3 |          380 |      0.117822  |         0.123762   |
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | SOLUSDT  |          -0.182152  |                0.45122   |            1 |           477 |           27 |     -0.471287  |         0.473267   |
| a7v3_rolling_self_reproduction_12_519354de8b22            | BTCUSDT  |           0.204509  |                0.380081  |          315 |             0 |          190 |      0.311881  |         0.311881   |
| a7v3_rolling_self_reproduction_12_519354de8b22            | ETHUSDT  |          -0.219975  |                0.148374  |          165 |             0 |          340 |      0.163366  |         0.163366   |
| a7v3_rolling_self_reproduction_12_519354de8b22            | SOLUSDT  |          -0.218517  |                0.449187  |            0 |           480 |           25 |     -0.475248  |         0.475248   |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | BTCUSDT  |           0.150144  |                0.422764  |          363 |             0 |          142 |      0.359406  |         0.359406   |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | ETHUSDT  |          -0.144269  |                0.103659  |          117 |             0 |          388 |      0.115842  |         0.115842   |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | SOLUSDT  |          -0.218517  |                0.449187  |            0 |           480 |           25 |     -0.475248  |         0.475248   |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | BTCUSDT  |           0.115018  |                0.46748   |          413 |             0 |           92 |      0.408911  |         0.408911   |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | ETHUSDT  |          -0.0929236 |                0.0589431 |           67 |             1 |          437 |      0.0653465 |         0.0673267  |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | SOLUSDT  |          -0.214539  |                0.449187  |            0 |           479 |           26 |     -0.474257  |         0.474257   |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | BTCUSDT  |           0.0829722 |                0.530488  |          477 |             0 |           28 |      0.472277  |         0.472277   |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | ETHUSDT  |          -0.0336156 |                0         |            3 |             5 |          497 |     -0.0019802 |         0.00792079 |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | SOLUSDT  |          -0.222239  |                0.441057  |            0 |           475 |           30 |     -0.470297  |         0.470297   |

## Matched Control Detail

| candidate_id                                                                          | base_candidate_id                                         | control_mode   | production_family                    |   net_sum_10bps__validation_2025H1 |   net_sum_10bps__recent_oos_2025H2_2026Apr |   net_sum_20bps__recent_oos_2025H2_2026Apr |   net_sum_10bps__fresh_may_2026 | val_recent_positive   | recent20_positive   |
|:--------------------------------------------------------------------------------------|:----------------------------------------------------------|:---------------|:-------------------------------------|-----------------------------------:|-------------------------------------------:|-------------------------------------------:|--------------------------------:|:----------------------|:--------------------|
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71__ctrl_row_shuffle_e7c7ff27  | a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | row_shuffle    | cross_symbol_self_reproduction_core3 |                          -2.3283   |                                  -4.44772  |                               -9.39522     |                       -0.367414 | False                 | False               |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71__ctrl_sign_flip_402941e8    | a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | sign_flip      | cross_symbol_self_reproduction_core3 |                          -1.91669  |                                  -3.23019  |                               -3.59569     |                        0.167382 | False                 | False               |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71__ctrl_time_shuffle_93b1f488 | a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | time_shuffle   | cross_symbol_self_reproduction_core3 |                          -1.8064   |                                  -2.52654  |                               -5.44354     |                       -0.100469 | False                 | False               |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71__ctrl_wrong_lag_02ccf53f    | a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | wrong_lag      | cross_symbol_self_reproduction_core3 |                          -0.905729 |                                   1.96577  |                                1.59677     |                       -0.123026 | False                 | True                |
| a7v3_rolling_self_reproduction_12_3eb1e9032578__ctrl_row_shuffle_45b7259a             | a7v3_rolling_self_reproduction_12_3eb1e9032578            | row_shuffle    | rolling_self_reproduction            |                          -2.25471  |                                  -4.14396  |                               -9.03346     |                       -0.507219 | False                 | False               |
| a7v3_rolling_self_reproduction_12_3eb1e9032578__ctrl_sign_flip_e72bb551               | a7v3_rolling_self_reproduction_12_3eb1e9032578            | sign_flip      | rolling_self_reproduction            |                          -1.6443   |                                  -2.30311  |                               -2.74711     |                        0.180144 | False                 | False               |
| a7v3_rolling_self_reproduction_12_3eb1e9032578__ctrl_time_shuffle_77ccedcc            | a7v3_rolling_self_reproduction_12_3eb1e9032578            | time_shuffle   | rolling_self_reproduction            |                          -0.567253 |                                  -0.244676 |                               -2.23418     |                       -0.44288  | False                 | False               |
| a7v3_rolling_self_reproduction_12_3eb1e9032578__ctrl_wrong_lag_7de5dd65               | a7v3_rolling_self_reproduction_12_3eb1e9032578            | wrong_lag      | rolling_self_reproduction            |                          -1.59123  |                                   0.316976 |                               -0.127524    |                       -0.284924 | False                 | False               |
| a7v3_rolling_self_reproduction_12_519354de8b22__ctrl_row_shuffle_d48624b4             | a7v3_rolling_self_reproduction_12_519354de8b22            | row_shuffle    | rolling_self_reproduction            |                          -3.06701  |                                  -3.81576  |                               -8.70076     |                       -0.392782 | False                 | False               |
| a7v3_rolling_self_reproduction_12_519354de8b22__ctrl_sign_flip_76f95d3c               | a7v3_rolling_self_reproduction_12_519354de8b22            | sign_flip      | rolling_self_reproduction            |                          -1.74952  |                                  -1.70367  |                               -2.03617     |                        0.197483 | False                 | False               |
| a7v3_rolling_self_reproduction_12_519354de8b22__ctrl_time_shuffle_467eaaef            | a7v3_rolling_self_reproduction_12_519354de8b22            | time_shuffle   | rolling_self_reproduction            |                          -1.91555  |                                  -2.85806  |                               -6.46606     |                       -0.396836 | False                 | False               |
| a7v3_rolling_self_reproduction_12_519354de8b22__ctrl_wrong_lag_180c680e               | a7v3_rolling_self_reproduction_12_519354de8b22            | wrong_lag      | rolling_self_reproduction            |                          -2.1773   |                                   0.885484 |                                0.553484    |                       -0.424187 | False                 | True                |
| a7v3_rolling_self_reproduction_12_9fa317374c73__ctrl_row_shuffle_27cffe8b             | a7v3_rolling_self_reproduction_12_9fa317374c73            | row_shuffle    | rolling_self_reproduction            |                          -3.73729  |                                  -5.97733  |                              -10.8498      |                       -0.255856 | False                 | False               |
| a7v3_rolling_self_reproduction_12_9fa317374c73__ctrl_sign_flip_463a901c               | a7v3_rolling_self_reproduction_12_9fa317374c73            | sign_flip      | rolling_self_reproduction            |                          -1.63126  |                                  -1.63656  |                               -1.98856     |                        0.178142 | False                 | False               |
| a7v3_rolling_self_reproduction_12_9fa317374c73__ctrl_time_shuffle_6fda6857            | a7v3_rolling_self_reproduction_12_9fa317374c73            | time_shuffle   | rolling_self_reproduction            |                          -2.42029  |                                  -2.28395  |                               -5.70945     |                       -0.43296  | False                 | False               |
| a7v3_rolling_self_reproduction_12_9fa317374c73__ctrl_wrong_lag_f33e297c               | a7v3_rolling_self_reproduction_12_9fa317374c73            | wrong_lag      | rolling_self_reproduction            |                          -2.59505  |                                   0.790674 |                                0.438174    |                       -0.374688 | False                 | True                |
| a7v3_rolling_self_reproduction_12_b26d29c81a80__ctrl_row_shuffle_06649ccf             | a7v3_rolling_self_reproduction_12_b26d29c81a80            | row_shuffle    | rolling_self_reproduction            |                          -2.81116  |                                  -6.31798  |                              -11.209       |                       -0.372754 | False                 | False               |
| a7v3_rolling_self_reproduction_12_b26d29c81a80__ctrl_sign_flip_de4bbe7f               | a7v3_rolling_self_reproduction_12_b26d29c81a80            | sign_flip      | rolling_self_reproduction            |                          -1.1705   |                                  -2.29588  |                               -2.75038     |                        0.170944 | False                 | False               |
| a7v3_rolling_self_reproduction_12_b26d29c81a80__ctrl_time_shuffle_92e22d18            | a7v3_rolling_self_reproduction_12_b26d29c81a80            | time_shuffle   | rolling_self_reproduction            |                           0.381341 |                                  -0.193627 |                               -1.58063     |                       -0.340312 | False                 | False               |
| a7v3_rolling_self_reproduction_12_b26d29c81a80__ctrl_wrong_lag_6bb3d2a2               | a7v3_rolling_self_reproduction_12_b26d29c81a80            | wrong_lag      | rolling_self_reproduction            |                          -0.100204 |                                   0.455981 |                               -0.000519017 |                       -0.255477 | False                 | False               |

## Candidate Factor Review Matrix

| factor_id                                                 | formula                              | provenance                                                                          | operator_path                                                                                                            | data_source                                                                                      | feature_family     | nearest_known_factors                                         | overlap_assessment                                                                         | family_diversity_impact                                                               | cluster_coverage                                                                      |   may_net_sum_10bps | keep_list_decision   | required_next_action                                                                               |
|:----------------------------------------------------------|:-------------------------------------|:------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|:-------------------|:--------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|--------------------:|:---------------------|:---------------------------------------------------------------------------------------------------|
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | Decay(agg_notional_10k_100k,4)       | A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue | agg_notional_10k_100k -> Decay -> Decay(agg_notional_10k_100k,4) -> core3 top1/bottom1 next-bar smoke book               | crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true | activity_liquidity | activity/liquidity agg notional and trade-count bucket family | high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants | negative; accepting would concentrate keep list in one microstructure liquidity motif | not promoted; May failure and control contamination prevent cluster-credit assignment |           -0.249144 | HOLD_RESEARCH        | Treat as failure-attribution input; do not promote or expand replay until May failure is explained |
| a7v3_rolling_self_reproduction_12_519354de8b22            | Decay(agg_trade_count_1k_10k,4)      | A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue | agg_trade_count_1k_10k -> Decay -> Decay(agg_trade_count_1k_10k,4) -> core3 top1/bottom1 next-bar smoke book             | crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true | activity_liquidity | activity/liquidity agg notional and trade-count bucket family | high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants | negative; accepting would concentrate keep list in one microstructure liquidity motif | not promoted; May failure and control contamination prevent cluster-credit assignment |           -0.270483 | HOLD_RESEARCH        | Treat as failure-attribution input; do not promote or expand replay until May failure is explained |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | Decay(agg_notional_1k_10k,4)         | A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue | agg_notional_1k_10k -> Decay -> Decay(agg_notional_1k_10k,4) -> core3 top1/bottom1 next-bar smoke book                   | crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true | activity_liquidity | activity/liquidity agg notional and trade-count bucket family | high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants | negative; accepting would concentrate keep list in one microstructure liquidity motif | not promoted; May failure and control contamination prevent cluster-credit assignment |           -0.247142 | HOLD_RESEARCH        | Treat as failure-attribution input; do not promote or expand replay until May failure is explained |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | Decay(agg_notional,4)                | A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue | agg_notional -> Decay -> Decay(agg_notional,4) -> core3 top1/bottom1 next-bar smoke book                                 | crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true | activity_liquidity | activity/liquidity agg notional and trade-count bucket family | high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants | negative; accepting would concentrate keep list in one microstructure liquidity motif | not promoted; May failure and control contamination prevent cluster-credit assignment |           -0.213944 | HOLD_RESEARCH        | Treat as failure-attribution input; do not promote or expand replay until May failure is explained |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | CrossSymbolRank(agg_notional_100_1k) | A7V-3 generated agg-aware dry-run; A7V-5 capped smoke; A7V-6 pre-May dominance clue | agg_notional_100_1k -> CrossSymbolRank -> CrossSymbolRank(agg_notional_100_1k) -> core3 top1/bottom1 next-bar smoke book | crypto_core12_1h_with_aggtrades_features_v1.parquet; core3 rows with agg_features_available=true | activity_liquidity | activity/liquidity agg notional and trade-count bucket family | high overlap; 5 clues are all activity_liquidity and 4/5 are rolling decay bucket variants | negative; accepting would concentrate keep list in one microstructure liquidity motif | not promoted; May failure and control contamination prevent cluster-credit assignment |           -0.178382 | HOLD_RESEARCH        | Treat as failure-attribution input; do not promote or expand replay until May failure is explained |

## Authorization

```json
{
  "authorizes_a7u0r_source_trace": true,
  "authorizes_alpha_proof": false,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_may_robustness_claim": false,
  "authorizes_shadow_paper_live": false,
  "avg_may_positive_hour_rate": 0.5211881188118812,
  "blockers": [
    "all_pre_may_clues_fail_may_stress",
    "activity_liquidity_family_concentration",
    "matched_control_contamination_present_in_a7v6"
  ],
  "candidate_count": 5,
  "decision": "HOLD_A7V7_ACTIVITY_LIQUIDITY_CLUES_FAIL_MAY_STRESS",
  "executes_replay": "forensic_recompute_on_a7v6_clues_only",
  "executes_search": false,
  "generated_at": "2026-05-22T02:14:05Z",
  "max_symbol_loss_share_proxy": 0.6059175626179703,
  "post_may_positive_candidates": 0,
  "required_next": [
    "A7U-0R consolidated raw checksum/source trace",
    "Do not promote A7V clues; all fail May stress",
    "If continuing, redesign objective/data/horizon rather than expanding current A7V clue family"
  ],
  "top_production_family_share": 0.8
}
```

## Required Next

- Do not expand A7V replay from these clues; they are activity-liquidity failure-attribution objects.
- If continuing aggTrades research, redefine the objective around regime/horizon or new data contracts, not the current pre-May clue family.
- Complete A7U-0R consolidated raw checksum/source trace before final panel claims.
