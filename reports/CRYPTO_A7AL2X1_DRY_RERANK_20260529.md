# CRYPTO A7AL-2X1 Dry Rerank

Generated: 2026-05-28T16:31:38Z

## Decision

```text
HOLD_A7AL2X1_NO_ELIGIBLE_ALLOWED_OBJECTIVE_FAMILY_IN_SHARED_POOL
```

This stage dry-reranks the existing A7AR-7 shared pool under the A7AL-2X objective-family reset contract. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{
  "authorizes_a7al2y_generation": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "selected_count_below_4",
    "selected_stress_clean_candidates_zero"
  ],
  "decision": "HOLD_A7AL2X1_NO_ELIGIBLE_ALLOWED_OBJECTIVE_FAMILY_IN_SHARED_POOL",
  "eligible_allowed_family_candidates": 0,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "fast_replay_candidates": 128,
  "generated_at": "2026-05-28T16:31:38Z",
  "input_pool_candidates": 4000,
  "selected_control_dominated": 0,
  "selected_count": 0,
  "selected_latent_fragile": 0,
  "selected_max_pairwise_corr": 0.0,
  "selected_signal_vector_clusters": 0,
  "selected_stress_clean_candidates": 0,
  "selected_with_stress_evidence": 0,
  "uses_may_for_generation": false,
  "uses_may_for_selector": false,
  "uses_may_for_veto_or_attribution": true
}
```

## Objective Family Funnel

| a7al2x_objective_family       | x1_reject_reason                          |   candidate_count |
|:------------------------------|:------------------------------------------|------------------:|
| F0_OI_delta_price_interaction | matched_control_dominated                 |                64 |
| UNMAPPED_OR_FORBIDDEN         | matched_control_dominated                 |                36 |
| DIRECT_OI_PRICE_WEAK_PRIOR    | matched_control_dominated                 |                14 |
| DIRECT_OI_PRICE_WEAK_PRIOR    | direct_oi_price_weak_prior_not_standalone |                10 |
| UNMAPPED_OR_FORBIDDEN         | timevarying_latent_fragile                |                 3 |
| DIRECT_OI_PRICE_WEAK_PRIOR    | forensic_control_dominated                |                 1 |

## Selected Queue

`<empty>`

## Signal-Vector Diversity Audit

|   selected_count |   selected_signal_vector_clusters |   selected_max_pairwise_corr |   selected_control_dominated |   selected_latent_fragile |   selected_with_stress_evidence |   selected_stress_clean_candidates | uses_may_for_selector   |
|-----------------:|----------------------------------:|-----------------------------:|-----------------------------:|--------------------------:|--------------------------------:|-----------------------------------:|:------------------------|
|                0 |                                 0 |                            0 |                            0 |                         0 |                               0 |                                  0 | False                   |

## Control Dominance Audit

`<empty>`

## Stress Veto Summary

`<empty>`

## Authorization

```json
{
  "a7al2y_generation": "NOT_AUTHORIZED",
  "alpha_proof": "NOT_AUTHORIZED",
  "decision": "HOLD_A7AL2X1_NO_ELIGIBLE_ALLOWED_OBJECTIVE_FAMILY_IN_SHARED_POOL",
  "large_formula_search": "NOT_AUTHORIZED",
  "reason": "A7AL-2X1 is dry rerank only; generation requires stress-clean selected evidence, which is absent.",
  "shadow_paper_live": "NOT_AUTHORIZED"
}
```

## Boundary

```text
No generation.
No replay.
No search.
No May in selector score.
May is post-selection veto / attribution only.
```
