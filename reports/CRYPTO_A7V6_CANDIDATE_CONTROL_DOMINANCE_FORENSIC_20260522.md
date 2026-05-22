# Crypto A7V-6 Candidate/Control Dominance Forensic

- generated_at: `2026-05-22T02:07:32Z`
- decision: `HOLD_A7V6_NO_POST_MAY_DOMINANT_CANDIDATE`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7V-6 reviews the A7V-5 capped smoke outputs. It does not generate candidates and does not rerun replay. The objective is to determine whether A7V-5 smoke-positive candidates dominate their matched row-shuffle, time-shuffle, wrong-lag, and sign-flip controls before any larger replay is considered.

May remains a stress-only label. It is used here only to block robustness claims, not to rank, tune, or select formulas.

## Decision Summary

- A7V-5 smoke positives: `18`
- pre-May control-clean + 20bps dominance clues: `5`
- post-May positive among A7V-5 positives: `0`
- A7V-5 positives with matched control validation+recent positive: `5`
- candidates authorized for promotion: `0`

## A7V-5 Positive Candidate Dominance

| candidate_id                                              | production_family                    | expression                                         | a7v6_label                           |   candidate_net_sum_10bps__validation_2025H1 |   candidate_net_sum_10bps__recent_oos_2025H2_2026Apr |   candidate_net_sum_20bps__recent_oos_2025H2_2026Apr |   candidate_net_sum_10bps__fresh_may_2026 |   margin_vs_max_control_net_sum_10bps__validation_2025H1 |   margin_vs_max_control_net_sum_10bps__recent_oos_2025H2_2026Apr |   control_val_recent_positive_count |   dominates_controls_val_recent_net10 |   dominates_controls_val_recent_ic |   cost20_survives_validation_recent |   may_stress_positive |
|:----------------------------------------------------------|:-------------------------------------|:---------------------------------------------------|:-------------------------------------|---------------------------------------------:|-----------------------------------------------------:|-----------------------------------------------------:|------------------------------------------:|---------------------------------------------------------:|-----------------------------------------------------------------:|------------------------------------:|--------------------------------------:|-----------------------------------:|------------------------------------:|----------------------:|
| a7v3_rolling_self_reproduction_12_69861a81fba7            | rolling_self_reproduction            | Decay(agg_trade_count_100_1k,4)                    | A7V6_HOLD_CONTROL_CONTAMINATED       |                                     1.04578  |                                             3.41082  |                                            3.28482   |                                 -0.169175 |                                                0.738927  |                                                       1.21662    |                                   1 |                                     1 |                                  1 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_214b62a005b2            | rolling_self_reproduction            | Decay(agg_notional_100k_1m,4)                      | A7V6_HOLD_CONTROL_CONTAMINATED       |                                     1.41155  |                                             1.79053  |                                            1.41953   |                                 -0.201037 |                                                0.641285  |                                                       1.00914    |                                   2 |                                     1 |                                  1 |                                   1 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_e5d9f3dbda87 | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_100k_1m)              | A7V6_HOLD_CONTROL_CONTAMINATED       |                                     0.84948  |                                             0.939572 |                                           -0.0514281 |                                 -0.250288 |                                                0.172519  |                                                       0.662629   |                                   1 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_rolling_self_reproduction_12_59b35b375ae9            | rolling_self_reproduction            | Decay(agg_avg_underlying_trade_notional,4)         | A7V6_HOLD_CONTROL_CONTAMINATED       |                                     1.11601  |                                             0.852962 |                                            0.812962  |                                 -0.144166 |                                                0.172084  |                                                       0.00217036 |                                   2 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_61af4a59eadc | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_avg_underlying_trade_notional) | A7V6_HOLD_CONTROL_CONTAMINATED       |                                     0.873261 |                                             0.773015 |                                            0.580015  |                                 -0.158766 |                                               -0.135344  |                                                       0.311587   |                                   1 |                                     0 |                                  0 |                                   1 |                     0 |
| a7v3_interaction_self_reproduction_12_0979984cc839        | interaction_self_reproduction        | Add(ZScore(agg_notional),Rank(mark_index_ratio))   | A7V6_HOLD_COST20_FRAGILE             |                                     0.150698 |                                             0.966409 |                                           -0.291591  |                                 -0.301094 |                                                0.757347  |                                                       1.2681     |                                   0 |                                     1 |                                  1 |                                   0 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_2122721cd54a | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_1k_10k)               | A7V6_HOLD_COST20_FRAGILE             |                                     0.336457 |                                             0.761003 |                                           -0.154997  |                                 -0.303255 |                                                1.26472   |                                                       0.158698   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_interaction_self_reproduction_12_20e05d6d98bf        | interaction_self_reproduction        | Add(ZScore(agg_notional),Rank(ret_12))             | A7V6_HOLD_COST20_FRAGILE             |                                     0.676601 |                                             0.727731 |                                           -0.453269  |                                 -0.236799 |                                                0.700001  |                                                       0.411615   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_4dc42d4c443e | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_10k_100k)             | A7V6_HOLD_COST20_FRAGILE             |                                     0.317181 |                                             0.701146 |                                           -0.486854  |                                 -0.287978 |                                                0.825059  |                                                       0.610913   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_interaction_self_reproduction_12_144cc168716a        | interaction_self_reproduction        | Add(ZScore(agg_notional),Rank(realized_vol_12))    | A7V6_HOLD_COST20_FRAGILE             |                                     0.752851 |                                             0.499194 |                                           -0.772306  |                                 -0.314295 |                                                1.70685   |                                                       0.391585   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_a1e534249441 | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional)                      | A7V6_HOLD_COST20_FRAGILE             |                                     0.616091 |                                             0.45291  |                                           -0.69809   |                                 -0.252629 |                                                0.996073  |                                                       0.506072   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_rolling_self_reproduction_12_b28d7ce95edf            | rolling_self_reproduction            | Decay(agg_max_trade_notional,4)                    | A7V6_HOLD_COST20_FRAGILE             |                                     0.179044 |                                             0.179198 |                                           -0.598802  |                                 -0.280296 |                                                0.0868012 |                                                       0.377595   |                                   0 |                                     1 |                                  0 |                                   0 |                     0 |
| a7v3_interaction_self_reproduction_12_070b69edeb3b        | interaction_self_reproduction        | Add(ZScore(agg_notional),Rank(ret_6))              | A7V6_HOLD_DOES_NOT_DOMINATE_CONTROLS |                                     0.585437 |                                             0.506269 |                                           -0.725731  |                                 -0.242509 |                                                0.637658  |                                                      -0.0275018  |                                   0 |                                     0 |                                  0 |                                   0 |                     0 |
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_100_1k)               | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.40969  |                                             2.49919  |                                            2.13369   |                                 -0.178382 |                                                2.31542   |                                                       0.533417   |                                   0 |                                     1 |                                  1 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | rolling_self_reproduction            | Decay(agg_notional_10k_100k,4)                     | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.1673   |                                             1.41511  |                                            0.971112  |                                 -0.249144 |                                                1.73455   |                                                       1.09814    |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | rolling_self_reproduction            | Decay(agg_notional,4)                              | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     0.829496 |                                             1.38688  |                                            0.932377  |                                 -0.213944 |                                                0.448154  |                                                       0.930896   |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_519354de8b22            | rolling_self_reproduction            | Decay(agg_trade_count_1k_10k,4)                    | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.29952  |                                             1.03867  |                                            0.706166  |                                 -0.270483 |                                                3.04905   |                                                       0.153182   |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | rolling_self_reproduction            | Decay(agg_notional_1k_10k,4)                       | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.16226  |                                             0.932557 |                                            0.580557  |                                 -0.247142 |                                                2.79353   |                                                       0.141883   |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |

## Pre-May Dominance Clues

| candidate_id                                              | production_family                    | expression                           | a7v6_label                           |   candidate_net_sum_10bps__validation_2025H1 |   candidate_net_sum_10bps__recent_oos_2025H2_2026Apr |   candidate_net_sum_20bps__recent_oos_2025H2_2026Apr |   candidate_net_sum_10bps__fresh_may_2026 |   margin_vs_max_control_net_sum_10bps__validation_2025H1 |   margin_vs_max_control_net_sum_10bps__recent_oos_2025H2_2026Apr |   control_val_recent_positive_count |   dominates_controls_val_recent_net10 |   dominates_controls_val_recent_ic |   cost20_survives_validation_recent |   may_stress_positive |
|:----------------------------------------------------------|:-------------------------------------|:-------------------------------------|:-------------------------------------|---------------------------------------------:|-----------------------------------------------------:|-----------------------------------------------------:|------------------------------------------:|---------------------------------------------------------:|-----------------------------------------------------------------:|------------------------------------:|--------------------------------------:|-----------------------------------:|------------------------------------:|----------------------:|
| a7v3_cross_symbol_self_reproduction_core3_12_b48c0093aa71 | cross_symbol_self_reproduction_core3 | CrossSymbolRank(agg_notional_100_1k) | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.40969  |                                             2.49919  |                                             2.13369  |                                 -0.178382 |                                                 2.31542  |                                                         0.533417 |                                   0 |                                     1 |                                  1 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_3eb1e9032578            | rolling_self_reproduction            | Decay(agg_notional_10k_100k,4)       | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.1673   |                                             1.41511  |                                             0.971112 |                                 -0.249144 |                                                 1.73455  |                                                         1.09814  |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_b26d29c81a80            | rolling_self_reproduction            | Decay(agg_notional,4)                | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     0.829496 |                                             1.38688  |                                             0.932377 |                                 -0.213944 |                                                 0.448154 |                                                         0.930896 |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_519354de8b22            | rolling_self_reproduction            | Decay(agg_trade_count_1k_10k,4)      | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.29952  |                                             1.03867  |                                             0.706166 |                                 -0.270483 |                                                 3.04905  |                                                         0.153182 |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |
| a7v3_rolling_self_reproduction_12_9fa317374c73            | rolling_self_reproduction            | Decay(agg_notional_1k_10k,4)         | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |                                     1.16226  |                                             0.932557 |                                             0.580557 |                                 -0.247142 |                                                 2.79353  |                                                         0.141883 |                                   0 |                                     1 |                                  0 |                                   1 |                     0 |

## Control Summary

| control_mode   | production_family                    |   rows |   val_recent_positive |   recent20_positive |   may_positive |   mean_validation_net10 |   mean_recent_net10 |   mean_may_net10 |
|:---------------|:-------------------------------------|-------:|----------------------:|--------------------:|---------------:|------------------------:|--------------------:|-----------------:|
| row_shuffle    | cross_symbol_self_reproduction_core3 |     12 |                     0 |                   0 |              0 |               -2.81476  |           -4.91663  |       -0.320568  |
| row_shuffle    | interaction_self_reproduction        |     12 |                     0 |                   0 |              0 |               -2.61201  |           -4.68441  |       -0.316993  |
| row_shuffle    | rolling_self_reproduction            |     12 |                     0 |                   0 |              0 |               -2.94349  |           -4.94934  |       -0.308189  |
| sign_flip      | cross_symbol_self_reproduction_core3 |     12 |                     0 |                   1 |              9 |               -1.73076  |           -2.40436  |        0.0465424 |
| sign_flip      | interaction_self_reproduction        |     12 |                     0 |                   0 |              4 |               -1.89463  |           -3.25977  |       -0.127937  |
| sign_flip      | rolling_self_reproduction            |     12 |                     0 |                   0 |             12 |               -1.23532  |           -2.0676   |        0.19781   |
| time_shuffle   | cross_symbol_self_reproduction_core3 |     12 |                     0 |                   0 |              1 |               -0.554477 |           -1.84918  |       -0.239558  |
| time_shuffle   | interaction_self_reproduction        |     12 |                     0 |                   0 |              0 |               -1.26884  |           -2.11178  |       -0.27683   |
| time_shuffle   | rolling_self_reproduction            |     12 |                     3 |                   0 |              1 |               -0.62854  |           -0.993738 |       -0.342576  |
| wrong_lag      | cross_symbol_self_reproduction_core3 |     12 |                     2 |                   3 |              1 |               -0.602734 |           -0.796928 |       -0.23821   |
| wrong_lag      | interaction_self_reproduction        |     12 |                     0 |                   0 |              0 |               -0.792234 |           -1.89922  |       -0.291543  |
| wrong_lag      | rolling_self_reproduction            |     12 |                     3 |                   7 |              0 |               -0.391903 |            0.696534 |       -0.26984   |

## Family Summary

| production_family                    | a7v6_label                           |   rows |
|:-------------------------------------|:-------------------------------------|-------:|
| cross_symbol_self_reproduction_core3 | A7V6_HOLD_CONTROL_CONTAMINATED       |      2 |
| cross_symbol_self_reproduction_core3 | A7V6_HOLD_COST20_FRAGILE             |      3 |
| cross_symbol_self_reproduction_core3 | A7V6_NOT_A7V5_POSITIVE               |      6 |
| cross_symbol_self_reproduction_core3 | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |      1 |
| interaction_self_reproduction        | A7V6_HOLD_COST20_FRAGILE             |      3 |
| interaction_self_reproduction        | A7V6_HOLD_DOES_NOT_DOMINATE_CONTROLS |      1 |
| interaction_self_reproduction        | A7V6_NOT_A7V5_POSITIVE               |      8 |
| rolling_self_reproduction            | A7V6_HOLD_CONTROL_CONTAMINATED       |      3 |
| rolling_self_reproduction            | A7V6_HOLD_COST20_FRAGILE             |      1 |
| rolling_self_reproduction            | A7V6_NOT_A7V5_POSITIVE               |      4 |
| rolling_self_reproduction            | A7V6_PRE_MAY_DOMINANCE_CLUE_MAY_FAIL |      4 |

## Candidate Factor Review Notes

- provenance: generated by A7V-3 agg-aware dry run, replay-smoked by A7V-5, reviewed here against matched controls.
- data source: `crypto_core12_1h_with_aggtrades_features_v1.parquet`, restricted to core3 rows with `agg_features_available=true`.
- operator path: aggTrades enhanced fields -> A7V-1 registered rolling/cross-symbol/interaction transforms -> A7V-3 formulas -> A7V-5 core3 top1/bottom1 smoke book.
- keep-list decision: `HOLD_RESEARCH`; no factor is eligible for keep review or promotion from A7V-6.

## Authorization

```json
{
  "a7v5_candidate_count": 36,
  "a7v5_control_count": 144,
  "a7v5_metric_rows_read": 720,
  "a7v5_positives_with_matched_positive_controls": 5,
  "a7v5_smoke_positive_count": 18,
  "authorizes_a7v7_failure_attribution": true,
  "authorizes_alpha_proof": false,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_may_robustness_claim": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_a7v5_positive_survives_may_stress",
    "matched_controls_positive_for_a7v5_positives",
    "pre_may_clues_family_concentrated"
  ],
  "decision": "HOLD_A7V6_NO_POST_MAY_DOMINANT_CANDIDATE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T02:07:32Z",
  "post_may_positive_among_a7v5_positives": 0,
  "pre_may_control_clean_cost20_dominance_count": 5,
  "pre_may_top_family_share": 0.8,
  "required_next": [
    "A7V-7 failure attribution on the 5 pre-May dominance clues",
    "Do not promote A7V candidates; all A7V-5 positives fail May stress",
    "Explain matched-control contamination before any expanded replay",
    "A7U-0R consolidated raw checksum/source trace before final panel claims"
  ]
}
```

## Required Next

- A7V-7 should focus on the 5 pre-May dominance clues as failure-attribution objects, not promotion objects.
- Do not expand replay until May stress failure and matched-control contamination are explained.
- A7U-0R consolidated raw checksum/source trace is still required before final panel claims.
