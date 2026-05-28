# CRYPTO A7AL-2W Signal-Vector Selector Repair

Generated: 2026-05-28T15:23:36Z

## Decision

```text
HOLD_A7AL2W_SELECTOR_DIVERSITY_REPAIRED_BUT_STRESS_VETO
```

This stage repairs selected-queue diversity using pre-May signal-vector clusters. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{
  "authorizes_a7al2x_objective_family_reset_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "selected_queue_may_stress_veto"
  ],
  "decision": "HOLD_A7AL2W_SELECTOR_DIVERSITY_REPAIRED_BUT_STRESS_VETO",
  "eligible_before_repair": 10,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T15:23:36Z",
  "input_selector_candidates": 128,
  "selected_count": 2,
  "selected_max_pairwise_corr": 0.8945560120210092,
  "selected_signal_vector_clusters": 2,
  "selected_stress_clean_candidates": 0,
  "selected_top_cluster_share": 0.5,
  "uses_may_for_generation": false,
  "uses_may_for_selector": false,
  "uses_may_for_veto_or_attribution": true,
  "uses_may_for_weight_update": false
}
```

## Queue Diversity Audit

|   eligible_before_repair |   selected_count |   selected_signal_vector_clusters |   selected_top_cluster_share |   selected_max_pairwise_corr |   selected_stress_clean_candidates | uses_may_for_selector   |
|-------------------------:|-----------------:|----------------------------------:|-----------------------------:|-----------------------------:|-----------------------------------:|:------------------------|
|                       10 |                2 |                                 2 |                          0.5 |                     0.894556 |                                  0 | False                   |

## Repaired Selected Pool

| candidate_id            |   selector_score_no_may | signal_vector_cluster_id   | a7al2w_queue_reason       | is_may_stress_failed   | t_failure_labels                                           |
|:------------------------|------------------------:|:---------------------------|:--------------------------|:-----------------------|:-----------------------------------------------------------|
| a7al2q_1378ff7d2322adee |                 3.3642  | svc_015                    | selected_strict_diversity | True                   | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       |
| a7al2q_a4993fe3273bf0c8 |                 3.11372 | svc_065                    | selected_strict_diversity | True                   | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE |

## Pairwise Correlation

| left_candidate_id       | right_candidate_id      |   signal_vector_corr | above_0p90   | above_0p95   |
|:------------------------|:------------------------|---------------------:|:-------------|:-------------|
| a7al2q_1378ff7d2322adee | a7al2q_a4993fe3273bf0c8 |             0.894556 | False        | False        |

## Repair Reason Summary

| a7al2w_queue_reason             |   candidate_count |
|:--------------------------------|------------------:|
| skip_selected_queue_corr_ge_0.9 |                 7 |
| selected_strict_diversity       |                 2 |
| skip_same_signal_vector_cluster |                 1 |

## Post-Selection Stress Quarantine

| candidate_id            | signal_vector_cluster_id   | t_failure_labels                                           |   t_may_min_spread |   t_may_sign_flip_rows |   t_may_control_dominated_rows | quarantine_type                 | allowed_for_selector_score   | allowed_for_generation_weight_update   |
|:------------------------|:---------------------------|:-----------------------------------------------------------|-------------------:|-----------------------:|-------------------------------:|:--------------------------------|:-----------------------------|:---------------------------------------|
| a7al2q_1378ff7d2322adee | svc_015                    | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       |        -0.00186216 |                      2 |                              2 | post_selection_stress_veto_only | False                        | False                                  |
| a7al2q_a4993fe3273bf0c8 | svc_065                    | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE |        -0.00185592 |                      2 |                              2 | post_selection_stress_veto_only | False                        | False                                  |

## Authorization

| action                                 | status         | reason                                                           |
|:---------------------------------------|:---------------|:-----------------------------------------------------------------|
| same_objective_rerun                   | NOT_AUTHORIZED | selector diversity repair still has zero stress-clean candidates |
| direct_oi_price_expansion              | NOT_AUTHORIZED | post-selection stress veto remains                               |
| large_formula_search                   | NOT_AUTHORIZED | objective stress mismatch unresolved                             |
| a7al2x_objective_family_reset_contract | AUTHORIZED     | selector mechanics repaired enough to move to objective reset    |
| alpha_proof_shadow_paper_live          | NOT_AUTHORIZED | no stress-clean candidate                                        |

## Boundary

```text
Selector repair:
  uses pre-May replay-aware selector score
  uses pre-May signal-vector clusters
  enforces selected-queue diversity

May:
  not used for selector score
  not used for generation or weight update
  retained only as post-selection veto / attribution

Not authorized:
  same objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
