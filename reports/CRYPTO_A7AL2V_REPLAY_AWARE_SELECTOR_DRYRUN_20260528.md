# CRYPTO A7AL-2V Replay-Aware Selector Dry-Run

Generated: 2026-05-28T14:59:47Z

## Decision

```text
HOLD_A7AL2V_SELECTED_POOL_STRESS_VETO_NO_EXPANSION
```

This stage scores the existing A7AR-7 shared pool using non-May replay-aware selector features. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_direct_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "selected_pool_may_stress_veto"
  ],
  "decision": "HOLD_A7AL2V_SELECTED_POOL_STRESS_VETO_NO_EXPANSION",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "forbidden_selector_feature_overlap_count": 0,
  "generated_at": "2026-05-28T14:59:47Z",
  "input_pool_candidates": 4000,
  "selected_candidates": 4,
  "selected_stress_clean_candidates": 0,
  "selected_with_may_stress_evidence": 4,
  "selector_scored_candidates": 128,
  "uses_may_for_generation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selector_score": false,
  "uses_may_for_veto_or_attribution": true
}
```

## Reject Summary

| selector_hard_reject_reason   |   candidate_count |
|:------------------------------|------------------:|
| premay_control_dominated      |               115 |
| eligible                      |                10 |
| replay_forensic_hold          |                 3 |

## Selected Pool Stress Veto Audit

| candidate_id            |   selector_score_no_may | selector_score_uses_may   | q_decision                                 | r_decision                 | s_a7al2s_tier                               | t_failure_labels                     |   t_may_sign_flip_rows |   t_may_control_dominated_rows |   t_may_min_spread | is_may_stress_failed   | post_selection_stress_status   |
|:------------------------|------------------------:|:--------------------------|:-------------------------------------------|:---------------------------|:--------------------------------------------|:-------------------------------------|-----------------------:|-------------------------------:|-------------------:|:-----------------------|:-------------------------------|
| a7al2q_1378ff7d2322adee |                 3.3642  | False                     | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED |                      2 |                              2 |        -0.00186216 | True                   | MAY_STRESS_VETO                |
| a7al2q_f00f22bbcc48dc2c |                 3.25412 | False                     | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED |                      2 |                              2 |        -0.00155474 | True                   | MAY_STRESS_VETO                |
| a7al2q_0de0d41346741bd1 |                 3.32987 | False                     | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED |                      2 |                              2 |        -0.00185283 | True                   | MAY_STRESS_VETO                |
| a7al2q_69d146749c30da3c |                 3.33571 | False                     | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS | primary_clean_premay__may_control_dominated | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED |                      2 |                              2 |        -0.00180721 | True                   | MAY_STRESS_VETO                |

## Forbidden Feature Audit

| feature                                 | forbidden_pattern_hit   | allowed_for_selector_score   |
|:----------------------------------------|:------------------------|:-----------------------------|
| selector_feature_replay_alignment_score |                         | True                         |
| selector_feature_latency_survival_score |                         | True                         |
| selector_feature_neutral_survival_score |                         | True                         |
| selector_feature_cost_survival_score    |                         | True                         |
| selector_feature_robust_stat_score      |                         | True                         |
| selector_feature_spread_score           |                         | True                         |
| selector_feature_control_penalty        |                         | True                         |
| selector_feature_turnover_penalty       |                         | True                         |
| selector_feature_concentration_penalty  |                         | True                         |
| selector_score_no_may                   |                         | True                         |

## Authorization

| action                           | status         | reason                                               |
|:---------------------------------|:---------------|:-----------------------------------------------------|
| a7ar8_signal_vector_registry     | AUTHORIZED     | needed before larger replay selection                |
| a7al2w_selector_repair_iteration | AUTHORIZED     | dry-run shows remaining blocker state                |
| a7al2q_same_objective_rerun      | NOT_AUTHORIZED | same objective already failed May stress attribution |
| direct_oi_price_expansion        | NOT_AUTHORIZED | stress veto/control dominance unresolved             |
| large_formula_search             | NOT_AUTHORIZED | replay-aware selector dry-run is not a search pass   |
| alpha_proof_shadow_paper_live    | NOT_AUTHORIZED | no stress-clean selected pool                        |

## Boundary

```text
Selector score:
  non-May replay alignment
  non-May control dominance
  non-May cost/latency
  non-May neutralization
  non-May robust statistics

May:
  post-selection veto / attribution only
  not used in score, ranking, generation, mutation, lane allocation, or training target

Not authorized:
  same objective rerun
  direct OI x price expansion
  large search
  alpha proof
  shadow / paper / live
```
