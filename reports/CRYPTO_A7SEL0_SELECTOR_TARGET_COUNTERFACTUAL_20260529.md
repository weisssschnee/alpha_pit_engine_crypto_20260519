# CRYPTO A7SEL-0 SELECTOR TARGET COUNTERFACTUAL

Generated: 2026-05-29T14:14:36Z

## Decision

`HOLD_A7SEL0_SELECTOR_COUNTERFACTUAL_NOT_PROMOTABLE`

A7SEL-0 dry-reranks existing shared-pool candidates only. It does not generate formulas or run replay.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "selected_stress_clean_candidates_zero"
  ],
  "decision": "HOLD_A7SEL0_SELECTOR_COUNTERFACTUAL_NOT_PROMOTABLE",
  "eligible_queue_count": 13,
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T14:14:36Z",
  "input_candidate_count": 4000,
  "selected_count": 4,
  "selected_stress_clean_candidates": 0,
  "stage": "A7SEL-0",
  "uses_may_for_post_selection_stress_summary": true,
  "uses_may_in_selector_score": false
}
```

## Selected Queue

| candidate_id            | candidate_role       | signal_vector_cluster_id   |   a7sel0_score_no_may |   control_ratio_for_selector |   non_l7_label_alignment_score | stress_clean_observed   |
|:------------------------|:---------------------|:---------------------------|----------------------:|-----------------------------:|-------------------------------:|:------------------------|
| a7al2q_1378ff7d2322adee | risk_defense_only    | svc_015                    |               34.3237 |                     0.59779  |                             12 | False                   |
| a7al2q_69d146749c30da3c | weak_or_unclassified | svc_008                    |               34.2988 |                     0.638674 |                             12 | False                   |
| a7al2q_a4993fe3273bf0c8 | risk_defense_only    | svc_065                    |               34.23   |                     0.66642  |                             12 | False                   |
| a7al2q_5da100b2822dc1a6 | risk_defense_only    | svc_039                    |               34.1359 |                     0.667808 |                             12 | False                   |

## Stress Summary

|   selected_count |   selected_may_observed_count |   selected_stress_clean_candidates |   selected_may_stress_failed_count |
|-----------------:|------------------------------:|-----------------------------------:|-----------------------------------:|
|                4 |                             4 |                                  0 |                                  4 |

## Boundary

```text
No generation, replay, search, alpha proof, shadow, paper, or live execution is authorized.
May is not used in selector score; it is only summarized after selection.
```
