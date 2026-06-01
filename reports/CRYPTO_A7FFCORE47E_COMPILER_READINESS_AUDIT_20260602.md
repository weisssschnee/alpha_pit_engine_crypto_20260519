# CRYPTO A7FF-CORE47E COMPILER READINESS AUDIT

Generated: 2026-06-01T21:07:34Z

## Decision

`PASS_A7FFCORE47E_COMPILER_READINESS_READY_FOR_CORE48_CONTRACT`

CORE47E audits whether the existing evidence base can support a control-null-aware compiler contract. It does not execute generation, replay, search, proof, shadow, paper, or live.

## Input Inventory

| artifact                     | path                                                                                 | exists   |   rows |
|:-----------------------------|:-------------------------------------------------------------------------------------|:---------|-------:|
| field_ontology_v3            | runtime/a7ffr1_field_ontology_v3/a7ffr1_field_ontology_v3.csv                        | True     |     81 |
| operator_response            | runtime/a7ffr2_operator_probing_v2/a7ffr2_observed_operator_response.csv             | True     |     21 |
| feature_pair_policy          | runtime/a7ffr3_feature_pair_policy_v2/a7ffr3_feature_pair_policy_v2.csv              | True     |   3003 |
| primitive_response_map       | runtime/a7aa1_primitive_response_map/a7aa1_primitive_response_map.csv                | True     |    648 |
| field_enforcement_manifest   | runtime/a7aif2_field_enforcement_regression/a7aif2_manifest.json                     | True     |    nan |
| materialization_manifest     | runtime/a7aif3_materialization_evaluator_parity/a7aif3_manifest.json                 | True     |    nan |
| control_vector_quality       | runtime/a7ffcore43e_control_vector_rebuild_audit/a7ffcore43e_sample_quality_gate.csv | True     |      6 |
| orthogonal_replay_manifest   | runtime/a7ffcore45e_orthogonal_book_replay_execution/a7ffcore45e_manifest.json       | True     |    nan |
| orthogonal_forensic_manifest | runtime/a7ffcore45r_orthogonal_book_replay_forensic/a7ffcore45r_manifest.json        | True     |    nan |

## Readiness Matrix

| requirement                              | evidence                          | status   | notes                                                                                                                         |
|:-----------------------------------------|:----------------------------------|:---------|:------------------------------------------------------------------------------------------------------------------------------|
| field ontology with compiler roles       | a7ffr1_field_ontology_v3          | PASS     | rows=81                                                                                                                       |
| operator probing evidence                | a7ffr2_observed_operator_response | PASS     | rows=21                                                                                                                       |
| feature pair policy                      | a7ffr3_feature_pair_policy_v2     | PASS     | rows=3003                                                                                                                     |
| primitive response map                   | a7aa1_primitive_response_map      | PASS     | rows=648                                                                                                                      |
| role enforcement connected               | A7AI-F2                           | PASS     | role_violation_count=0                                                                                                        |
| materialization/evaluator parity         | A7AI-F3                           | PASS     | fields=32; operators=15                                                                                                       |
| full-universe control vector feasibility | A7FF-CORE43E                      | PASS     | quality_rows=6                                                                                                                |
| negative replay evidence available       | A7FF-CORE45E/45R                  | PASS     | core45e=HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT; failure=orthogonal_book_replay_control_dominated_zero_survivors |

## Generation Readiness

| capability                            | status         | reason                                                                                                    |
|:--------------------------------------|:---------------|:----------------------------------------------------------------------------------------------------------|
| define_null_first_generation_contract | READY          | source artifacts are sufficient to define a bounded null-first generation contract                        |
| execute_null_first_generation_now     | NOT_READY      | compiler implementation and gate-native output schema are not built yet; CORE47E is audit-only            |
| execute_formula_search_now            | NOT_AUTHORIZED | CORE46/CORE47 explicitly block generation/search until null-first compiler contract and later gates exist |

## Gap Matrix

| gap_id                             | severity                   | description                                                                                            | blocks_core48_contract   | blocks_generation_execution   |
|:-----------------------------------|:---------------------------|:-------------------------------------------------------------------------------------------------------|:-------------------------|:------------------------------|
| G0_compiler_implementation_missing | expected_next_contract_gap | no null-first compiler execution entrypoint exists yet                                                 | False                    | True                          |
| G1_operator_null_margin_not_native | implementation_gap         | operator probing has response/control summaries but not native full-universe null vectors per operator | False                    | True                          |
| G2_pair_policy_not_null_ranked     | implementation_gap         | feature-pair policy exists but must be re-ranked by null-margin evidence before generation             | False                    | True                          |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE48 bounded null-first factor seed generation contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "current_candidate_expansion": true,
    "formula_search": true,
    "large_search": true,
    "null_first_generation_execution": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core48_contract": true,
  "authorizes_formula_search": false,
  "authorizes_generation_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE47E_COMPILER_READINESS_READY_FOR_CORE48_CONTRACT",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:07:34Z",
  "next_allowed": "A7FF-CORE48 bounded null-first factor seed generation contract",
  "readiness_pass_count": 8,
  "readiness_total_count": 8,
  "source_decision": "PASS_A7FFCORE47_CONTROL_NULL_AWARE_COMPILER_CONTRACT_READY_FOR_CORE47E",
  "source_stage": "A7FF-CORE47",
  "stage": "A7FF-CORE47E"
}
```
