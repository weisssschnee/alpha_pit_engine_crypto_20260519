# CRYPTO A7AR-8 Signal-Vector Cluster Registry

Generated: 2026-05-28T15:10:04Z

## Decision

```text
HOLD_A7AR8_SELECTED_QUEUE_STRESS_VETO_NO_EXPANSION
```

This stage builds a pre-May replay-behavior cluster registry. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_direct_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "selected_queue_pairwise_corr_high",
    "selected_queue_may_stress_veto"
  ],
  "candidate_vectors": 128,
  "cluster_corr_threshold": 0.95,
  "decision": "HOLD_A7AR8_SELECTED_QUEUE_STRESS_VETO_NO_EXPANSION",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T15:10:04Z",
  "selected_count": 4,
  "selected_max_pairwise_corr": 0.9582527973890684,
  "selected_same_cluster_pairs": 3,
  "selected_signal_vector_clusters": 2,
  "selected_stress_clean_candidates": 0,
  "selected_top_cluster_share": 0.75,
  "signal_vector_clusters": 119,
  "uses_may_for_cluster": false,
  "uses_may_for_selection": false,
  "uses_may_for_veto_or_attribution": true,
  "vector_feature_count": 135
}
```

## Selected Queue Diversity Audit

|   selected_count |   selected_signal_vector_clusters |   selected_top_cluster_share |   selected_max_pairwise_corr |   selected_same_cluster_pairs |   selected_stress_clean_candidates | uses_may_for_cluster   |
|-----------------:|----------------------------------:|-----------------------------:|-----------------------------:|------------------------------:|-----------------------------------:|:-----------------------|
|                4 |                                 2 |                         0.75 |                     0.958253 |                             3 |                                  0 | False                  |

## Selected Queue Registry

| candidate_id            | signal_vector_cluster_id   |   max_corr_to_other_signal_vector |   selector_score_no_may | r_decision                 | s_a7al2s_tier                               | is_may_stress_failed   |
|:------------------------|:---------------------------|----------------------------------:|------------------------:|:---------------------------|:--------------------------------------------|:-----------------------|
| a7al2q_0de0d41346741bd1 | svc_008                    |                          0.963753 |                 3.32987 | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | True                   |
| a7al2q_1378ff7d2322adee | svc_015                    |                          0.979022 |                 3.3642  | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | True                   |
| a7al2q_69d146749c30da3c | svc_008                    |                          0.966456 |                 3.33571 | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | True                   |
| a7al2q_f00f22bbcc48dc2c | svc_008                    |                          0.963799 |                 3.25412 | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | True                   |

## Cluster Summary

| signal_vector_cluster_id   |   candidate_count |   selected_count |   forensic_pass_count |   may_stress_failed_count | top_field_family     | top_skeleton_key          | top_production_key                                                                                    |
|:---------------------------|------------------:|-----------------:|----------------------:|--------------------------:|:---------------------|:--------------------------|:------------------------------------------------------------------------------------------------------|
| svc_008                    |                 5 |                3 |                     5 |                         5 | open_interest\|price | skeleton-834f1fb23958e23f | a7al2q_local_oi_price::abs_level_gap::open_interest_value_last\|trade_close::24\|24                   |
| svc_015                    |                 2 |                1 |                     2 |                         2 | open_interest\|price | skeleton-834f1fb23958e23f | a7al2q_local_oi_price::abs_level_gap::open_interest_value_last\|trade_close::24\|8                    |
| svc_012                    |                 3 |                0 |                     0 |                         0 | open_interest\|price | skeleton-834f1fb23958e23f | a7al2q_local_oi_price::abs_level_gap::open_interest_mean\|index_close::4\|24                          |
| svc_022                    |                 2 |                0 |                     0 |                         0 | open_interest\|price | skeleton-cdd50cc367bea61c | a7al2q_local_oi_price::oi_level_plus_neg_price_delta::open_interest_last\|index_close::8\|96          |
| svc_062                    |                 2 |                0 |                     0 |                         0 | open_interest\|price | skeleton-a31a62d6cd42777e | a7al2q_local_oi_price::oi_delta_plus_neg_price_level::open_interest_mean\|index_close::720\|72        |
| svc_000                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-34595505730d2c62 | a7al2q_local_oi_price::oi_level_x_price_delta::open_interest_last\|mark_close::4\|504                 |
| svc_001                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-65ce4cb2af0cf72a | a7al2q_local_oi_price::abs_delta_gap::open_interest_value_mean\|mark_close::720\|12                   |
| svc_002                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-cdd50cc367bea61c | a7al2q_local_oi_price::oi_level_plus_neg_price_delta::open_interest_last\|index_close::168\|4         |
| svc_003                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_last\|mark_close::72\|720              |
| svc_004                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-c843c26fad347fd9 | a7al2q_local_oi_price::oi_delta_x_price_delta::open_interest_last\|index_close::504\|12               |
| svc_005                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-bb9ca3f57ba3a72b | a7al2q_local_oi_price::oi_abs_delta_x_price_abs::open_interest_value_mean\|trade_close::168\|72       |
| svc_006                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_mean\|index_close::96\|24              |
| svc_007                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-a31a62d6cd42777e | a7al2q_local_oi_price::oi_delta_plus_neg_price_level::open_interest_value_last\|trade_close::168\|720 |
| svc_009                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-6a73164c2e3655ed | a7al2q_local_oi_price::oi_delta_x_price_level::open_interest_value_mean\|mark_close::72\|504          |
| svc_010                    |                 1 |                0 |                     0 |                         1 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_value_last\|index_close::4\|72         |
| svc_011                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-6a73164c2e3655ed | a7al2q_local_oi_price::oi_delta_x_price_level::open_interest_value_last\|index_close::48\|24          |
| svc_013                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-65ce4cb2af0cf72a | a7al2q_local_oi_price::abs_delta_gap::open_interest_value_mean\|trade_close::4\|336                   |
| svc_014                    |                 1 |                0 |                     1 |                         1 | open_interest\|price | skeleton-834f1fb23958e23f | a7al2q_local_oi_price::abs_level_gap::open_interest_value_mean\|trade_close::168\|504                 |
| svc_016                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-6a73164c2e3655ed | a7al2q_local_oi_price::oi_delta_x_price_level::open_interest_mean\|mark_close::4\|72                  |
| svc_017                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-b86d839c2c31ff74 | a7al2q_local_oi_price::delta_spread::open_interest_value_last\|index_close::8\|24                     |
| svc_018                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-34595505730d2c62 | a7al2q_local_oi_price::oi_level_x_price_delta::open_interest_mean\|trade_close::504\|96               |
| svc_019                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_mean\|trade_close::24\|72              |
| svc_020                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-b86d839c2c31ff74 | a7al2q_local_oi_price::delta_spread::open_interest_mean\|mark_close::48\|96                           |
| svc_021                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-c843c26fad347fd9 | a7al2q_local_oi_price::oi_delta_x_price_delta::open_interest_last\|index_close::48\|336               |
| svc_023                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-bb9ca3f57ba3a72b | a7al2q_local_oi_price::oi_abs_delta_x_price_abs::open_interest_last\|trade_close::4\|8                |
| svc_024                    |                 1 |                0 |                     0 |                         1 | open_interest\|price | skeleton-834f1fb23958e23f | a7al2q_local_oi_price::abs_level_gap::open_interest_value_mean\|mark_close::168\|336                  |
| svc_025                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-a31a62d6cd42777e | a7al2q_local_oi_price::oi_delta_plus_neg_price_level::open_interest_last\|index_close::4\|24          |
| svc_026                    |                 1 |                0 |                     0 |                         1 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_value_mean\|mark_close::12\|336        |
| svc_027                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-65ce4cb2af0cf72a | a7al2q_local_oi_price::abs_delta_gap::open_interest_mean\|mark_close::8\|12                           |
| svc_028                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-a31a62d6cd42777e | a7al2q_local_oi_price::oi_delta_plus_neg_price_level::open_interest_value_last\|mark_close::96\|168   |
| svc_029                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-65ce4cb2af0cf72a | a7al2q_local_oi_price::abs_delta_gap::open_interest_value_last\|index_close::336\|8                   |
| svc_030                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-34595505730d2c62 | a7al2q_local_oi_price::oi_level_x_price_delta::open_interest_value_last\|mark_close::12\|24           |
| svc_031                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-34595505730d2c62 | a7al2q_local_oi_price::oi_level_x_price_delta::open_interest_last\|index_close::168\|168              |
| svc_032                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_value_last\|index_close::4\|720        |
| svc_033                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-5ca10905a35c5fca | a7al2q_local_oi_price::oi_abs_x_price_abs_delta::open_interest_mean\|index_close::504\|336            |
| svc_034                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-6a73164c2e3655ed | a7al2q_local_oi_price::oi_delta_x_price_level::open_interest_value_last\|mark_close::336\|504         |
| svc_035                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-3c104d6d475f05ac | a7al2q_local_oi_price::level_spread::open_interest_value_last\|trade_close::12\|8                     |
| svc_036                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-bb9ca3f57ba3a72b | a7al2q_local_oi_price::oi_abs_delta_x_price_abs::open_interest_last\|trade_close::12\|504             |
| svc_037                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-34595505730d2c62 | a7al2q_local_oi_price::oi_level_x_price_delta::open_interest_value_last\|mark_close::96\|504          |
| svc_038                    |                 1 |                0 |                     0 |                         0 | open_interest\|price | skeleton-a31a62d6cd42777e | a7al2q_local_oi_price::oi_delta_plus_neg_price_level::open_interest_value_last\|trade_close::168\|4   |

## Authorization

| action                        | status         | reason                                                                 |
|:------------------------------|:---------------|:-----------------------------------------------------------------------|
| a7al2w_objective_repair       | AUTHORIZED     | selected queue is stress-vetoed; repair objective before any expansion |
| same_objective_rerun          | NOT_AUTHORIZED | A7AL-2V selected queue has zero stress-clean candidates                |
| direct_oi_price_expansion     | NOT_AUTHORIZED | signal-vector registry does not repair May stress veto                 |
| large_formula_search          | NOT_AUTHORIZED | registry is diagnostic; no stress-clean selected pool                  |
| alpha_proof_shadow_paper_live | NOT_AUTHORIZED | no candidate-level proof                                               |

## Boundary

```text
Cluster features:
  pre-May replay metrics only
  validation/test/recent splits only
  original and one-bar-lag variants
  label_t_to_t24 / label_t1_to_t25 / label_t2_to_t26 entries

May:
  not used for cluster construction
  not used for selector score
  retained only as post-selection veto / attribution

Not authorized:
  same objective rerun
  direct OI x price expansion
  large search
  alpha proof
  shadow / paper / live
```
