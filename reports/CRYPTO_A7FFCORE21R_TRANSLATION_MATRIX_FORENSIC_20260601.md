# CRYPTO A7FF-CORE21R TRANSLATION MATRIX FORENSIC

Generated: 2026-06-01T15:18:33Z

## Decision

`PASS_A7FFCORE21R_TRANSLATION_MATRIX_FORENSIC_COMPLETE_READY_FOR_CORE22`

CORE21R freezes the translation matrix result. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core22_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_label_cost_clean_candidate_count": 1,
  "best_lane_cost_clean_candidate_count": 3,
  "decision": "PASS_A7FFCORE21R_TRANSLATION_MATRIX_FORENSIC_COMPLETE_READY_FOR_CORE22",
  "dominant_failure": "lag_and_lane_translation_bottleneck",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:18:33Z",
  "next_allowed": "A7FF-CORE22 lag-aware replay translation contract",
  "non_l5_clean_2bps": 3,
  "source_decision": "HOLD_A7FFCORE21E_TRANSLATION_MATRIX_INSUFFICIENT",
  "source_stage": "A7FF-CORE21E",
  "stage": "A7FF-CORE21R"
}
```

## Diagnosis

| finding                             | evidence                                                                             | severity   |
|:------------------------------------|:-------------------------------------------------------------------------------------|:-----------|
| cost_relief_exists_but_insufficient | 2bps non-L5 clean count is 3, but best label/cost bucket clean count is 1            | high       |
| lag_gate_is_major_suppressor        | L0/L1 2bps each have 17 clean-without-lag candidates but only 1 with lag gate        | high       |
| lane_breadth_still_insufficient     | current replay-clean lane count is 2; S0/S1 do not translate to clean bounded replay | high       |
| not_l5_only                         | non-L5 2bps clean count exceeds L5 2bps clean count, but breadth is still too low    | medium     |

## Recommended Actions

| action_id                   | action                                                      | reason                                                                   |
|:----------------------------|:------------------------------------------------------------|:-------------------------------------------------------------------------|
| R0_no_large_search          | do not authorize large search                               | translation matrix remains too narrow after cost and label decomposition |
| R1_lag_translation_contract | write CORE22 lag-aware replay translation contract          | lag gate suppresses many otherwise cost/control-clean L0/L1/L3 rows      |
| R2_lane_specific_repair     | require S0/S1 lane repair before any search-readiness claim | clean replay evidence remains concentrated in S2/S3                      |

## Top Lag Gate Loss

| label_family                       |   cost_bps |   clean_candidate_count |   clean_without_lag_gate |   lag_gate_loss |
|:-----------------------------------|-----------:|------------------------:|-------------------------:|----------------:|
| L0_raw_forward_return              |          2 |                       1 |                       17 |              16 |
| L1_cross_sectional_relative_return |          2 |                       1 |                       17 |              16 |
| L3_liquidity_tier_relative_return  |          2 |                       1 |                       13 |              12 |
| L5_vol_adjusted_return             |         10 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |          2 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |          5 |                       1 |                        8 |               7 |
| L5_vol_adjusted_return             |         20 |                       1 |                        8 |               7 |
| L0_raw_forward_return              |         10 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |         20 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |         10 |                       0 |                      nan |               0 |
| L1_cross_sectional_relative_return |          5 |                       0 |                      nan |               0 |
| L0_raw_forward_return              |         20 |                       0 |                      nan |               0 |
| L0_raw_forward_return              |          5 |                       0 |                      nan |               0 |
| L3_liquidity_tier_relative_return  |         20 |                       0 |                      nan |               0 |
| L3_liquidity_tier_relative_return  |          5 |                       1 |                        1 |               0 |
| L3_liquidity_tier_relative_return  |         10 |                       0 |                      nan |               0 |
