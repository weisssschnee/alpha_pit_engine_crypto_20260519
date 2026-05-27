# CRYPTO A7AR-4 Selector Adapter Smoke

Generated: 2026-05-27T04:16:41Z

## Decision

```text
HOLD_A7AR4_SELECTOR_DIVERSITY_WEAK
```

## Summary

```json
{
  "generated_at": "2026-05-27T04:16:41Z",
  "decision": "HOLD_A7AR4_SELECTOR_DIVERSITY_WEAK",
  "executes_search": false,
  "executes_replay": false,
  "generated_candidates": 1000,
  "a7ar2_evaled_candidates": 96,
  "eligible_prediversity_candidates": 90,
  "selected_candidates": 20,
  "selected_family_count": 6,
  "selected_skeleton_count": 9,
  "selected_production_key_count": 20,
  "minimum_selected_skeleton_count": 20,
  "blockers": [
    "selected_skeleton_count_below_20"
  ],
  "a7al1_field_family_baseline_not_blocked_by_a7ar4": true,
  "authorizes_a7al2_small_formula_search_contract_drafting": false,
  "authorizes_formula_search_execution": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "warnings": [
    "A7AR-4 is pre-replay selector plumbing only",
    "A7AR-2 evaluated only 96 generated candidates; non-evaluated candidates are rejected for this smoke",
    "Current generator skeleton diversity is expected to be the binding constraint if selected_skeleton_count < 20"
  ]
}
```

## Skeleton Diversity

| scope | candidates | skeleton_count | top_skeleton | top_skeleton_share |
| --- | --- | --- | --- | --- |
| all_generated | 1000 | 9 | skeleton-7762e3f46e546cc2 | 0.247 |
| a7ar2_evaled | 96 | 9 | skeleton-7762e3f46e546cc2 | 0.25 |
| eligible_prediversity | 90 | 9 | skeleton-7762e3f46e546cc2 | 0.233333 |
| selected | 20 | 9 | skeleton-7762e3f46e546cc2 | 0.15 |

## Family Cap Audit

| cap_name | top_value | top_count | top_share | cap | status |
| --- | --- | --- | --- | --- | --- |
| top_formula_family_share | basis_funding_crowding | 5 | 0.25 | 0.25 | PASS |
| top_skeleton_share | skeleton-7762e3f46e546cc2 | 3 | 0.15 | 0.15 | PASS |
| top_production_key_share | crypto_formula_gen_v2_adapter::basis_funding_crowding::basis|funding::8|336 | 1 | 0.05 | 0.2 | PASS |
| top_field_family_share | price | 8 | 0.2 | 0.25 | PASS |

## Reject Reasons

| reason | count |
| --- | --- |
| not_in_a7ar2_eval_pool | 904 |
| eligible_not_selected_by_caps_or_budget | 70 |
| selected_diversity_capped | 20 |
| low_activity_0bar | 6 |

## Latency Policy

| check | status | detail |
| --- | --- | --- |
| fixed_delay_stress_abolished | PASS | PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED |
| field_contract_all_present | PASS | fields=28 missing=0 |
| same_bar_forbidden | PASS | same_bar_execution_allowed must be false |
| fixed_delay_not_required | PASS | field-native latency audit is required instead |

## Negative Control Readiness

| check | status | detail |
| --- | --- | --- |
| negative_control_plan_attached | PASS | plan_controls=8 |
| a7ar2_control_eval_success | PASS | rows=288 failures=0 |
| control_available_random_field | PASS | rows=96 active_ratio_median=1.0 |
| control_available_wrong_lag_future_1h | PASS | rows=96 active_ratio_median=0.987176 |
| control_available_wrong_lag_stale_24h | PASS | rows=96 active_ratio_median=0.985344 |

## Boundary

```text
AUTHORIZED:
  A7AL-1 field-family neutralized baseline remains allowed.

CONDITIONAL:
  A7AL-2 small formula search contract drafting only if A7AR-4 PASS.

NOT AUTHORIZED:
  formula search execution
  alpha proof
  shadow / paper / live
```
