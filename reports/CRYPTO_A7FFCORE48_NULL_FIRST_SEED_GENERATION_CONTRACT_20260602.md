# CRYPTO A7FF-CORE48 NULL-FIRST SEED GENERATION CONTRACT

Generated: 2026-06-01T21:09:47Z

## Decision

`PASS_A7FFCORE48_NULL_FIRST_SEED_GENERATION_CONTRACT_READY_FOR_CORE48E`

CORE48 defines bounded null-first dry seed generation after CORE47E readiness. It authorizes only CORE48E dry generation, not numeric replay, formula search, large search, proof, shadow, paper, live, or promotion.

## Input Sources

| input_id                  | path                                                                                 | role                                                  | required   |
|:--------------------------|:-------------------------------------------------------------------------------------|:------------------------------------------------------|:-----------|
| I0_field_ontology_v3      | runtime/a7ffr1_field_ontology_v3/a7ffr1_field_ontology_v3.csv                        | field semantic and compiler role source               | True       |
| I1_operator_response      | runtime/a7ffr2_operator_probing_v2/a7ffr2_observed_operator_response.csv             | operator response/null pre-score source               | True       |
| I2_pair_policy            | runtime/a7ffr3_feature_pair_policy_v2/a7ffr3_feature_pair_policy_v2.csv              | semantic-compatible pair source                       | True       |
| I3_primitive_response_map | runtime/a7aa1_primitive_response_map/a7aa1_primitive_response_map.csv                | label/control response evidence source                | True       |
| I4_core43e_vector_schema  | runtime/a7ffcore43e_control_vector_rebuild_audit/a7ffcore43e_sample_quality_gate.csv | required full-universe null-vector feasibility source | True       |

## Generation Lanes

| lane_id                       | description                                                                                                     |   max_seed_count | requires_pair   |
|:------------------------------|:----------------------------------------------------------------------------------------------------------------|-----------------:|:----------------|
| N0_single_field_operator_seed | single field x operator seeds with non-L7 response and control/null margin evidence                             |              360 | False           |
| N1_role_compatible_pair_seed  | semantic-compatible field pairs after both sides have response evidence                                         |              360 | True            |
| N2_regime_conditioned_seed    | ordinary-alpha seed conditioned by regime/neutralizer fields without promoting those fields as standalone alpha |              240 | True            |
| N3_control_repair_seed        | near-miss response rows explicitly redesigned to improve original-vs-stale/sign/shuffle separation              |              240 | False           |

## Hard Gates

| gate                          | requirement                                                                        |
|:------------------------------|:-----------------------------------------------------------------------------------|
| field_contract_present        | all fields must exist in ontology/enforcement ledger                               |
| role_allowed                  | diagnostic/risk-defense fields cannot be standalone alpha seeds                    |
| non_l7_response_required      | seed must have non-L7 response evidence or be marked diagnostic-only               |
| control_margin_required       | operator/field evidence must show original signal weaker controls are not dominant |
| full_universe_vector_required | CORE48E must output original/stale/sign/time/symbol score vector fields            |
| family_cap                    | no semantic family may exceed 35 percent of selected seeds                         |
| motif_cap                     | no operator/motif may exceed 25 percent of selected seeds                          |
| no_known_stress_score         | known stress/May-like labels are forbidden in generation score                     |

## Output Schema

| field                 | required   |
|:----------------------|:-----------|
| seed_id               | True       |
| lane_id               | True       |
| field_primary         | True       |
| field_partner         | False      |
| semantic_type_primary | True       |
| semantic_type_partner | False      |
| operator              | True       |
| window_h              | True       |
| expression            | True       |
| compiler_role         | True       |
| non_l7_evidence       | True       |
| operator_null_margin  | True       |
| role_gate_status      | True       |
| family_cap_status     | True       |
| candidate_status      | True       |

## Pass Gate

| gate                       | threshold                        |
|:---------------------------|:---------------------------------|
| generated_seed_count       | >= 400 bounded dry seeds         |
| eligible_seed_count        | >= 120 null-first eligible seeds |
| semantic_family_count      | >= 5 eligible semantic families  |
| operator_count             | >= 4 eligible operators          |
| role_violation_count       | 0                                |
| missing_contract_count     | 0                                |
| family_cap_violation_count | 0                                |

## Execution Plan

| stage        | action                                                                           | executes_generation   | executes_replay   | executes_search   |   max_seed_count |
|:-------------|:---------------------------------------------------------------------------------|:----------------------|:------------------|:------------------|-----------------:|
| A7FF-CORE48E | bounded null-first dry seed generation using CORE48 gates                        | True                  | False             | False             |             1200 |
| A7FF-CORE49  | if CORE48E passes, define full-universe null-vector preflight for eligible seeds | False                 | False             | False             |              nan |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE48E bounded null-first dry seed generation": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "numeric_replay": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core48e_dry_generation": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE48_NULL_FIRST_SEED_GENERATION_CONTRACT_READY_FOR_CORE48E",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:09:47Z",
  "max_core48e_seed_count": 1200,
  "next_allowed": "A7FF-CORE48E bounded null-first dry seed generation",
  "source_decision": "PASS_A7FFCORE47E_COMPILER_READINESS_READY_FOR_CORE48_CONTRACT",
  "source_stage": "A7FF-CORE47E",
  "stage": "A7FF-CORE48"
}
```
