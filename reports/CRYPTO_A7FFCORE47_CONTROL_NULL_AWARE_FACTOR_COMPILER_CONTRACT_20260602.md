# CRYPTO A7FF-CORE47 CONTROL-NULL-AWARE FACTOR COMPILER CONTRACT

Generated: 2026-06-01T21:03:33Z

## Decision

`PASS_A7FFCORE47_CONTROL_NULL_AWARE_COMPILER_CONTRACT_READY_FOR_CORE47E`

CORE47 defines the next feature-to-factor compiler after CORE45R/CORE46 found zero orthogonal book survivors. It is contract-only and does not execute generation, replay, search, proof, shadow, paper, or live.

## Compiler Principles

| principle_id                   | description                                                                                                  | hard_requirement   |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------------|:-------------------|
| C0_null_first                  | feature-to-factor candidates must expose original-vs-null separability before replay or book selection       | True               |
| C1_full_universe_vectors       | candidate scoring must be evaluated on full timestamp-symbol score vectors, not selected top/bottom rows     | True               |
| C2_role_typed_generation       | signal, regime, neutralizer, and risk-defense fields must remain role-tagged through compilation             | True               |
| C3_response_before_interaction | single-field/operator response and null-separation evidence must exist before pairwise interaction expansion | True               |
| C4_portfolio_marginal_later    | book/replay reward can only be used after null-separation and role checks pass                               | True               |

## Score Contract

| score_component           | source                                                     | allowed_stage                | may_use   |
|:--------------------------|:-----------------------------------------------------------|:-----------------------------|:----------|
| original_response_score   | feature x transform x label/horizon response               | probe                        | True      |
| stale_null_margin         | original score vector versus stale score vector            | probe_and_gate               | True      |
| sign_flip_asymmetry       | original score behavior versus sign-flipped score behavior | probe_and_gate               | True      |
| shuffle_time_margin       | original score vector versus time-shuffle null             | probe_and_gate               | True      |
| shuffle_symbol_margin     | original score vector versus symbol-shuffle null           | probe_and_gate               | True      |
| role_violation_penalty    | field ontology / role enforcement ledger                   | hard_gate                    | True      |
| family_breadth_bonus      | semantic family and motif diversity                        | selection_after_gate         | True      |
| may_or_known_stress_score | known stress label or May-like post-selection veto result  | forbidden_for_compiler_score | False     |

## Generation Funnel

| level                       | action                                                                                | max_output_role                    |
|:----------------------------|:--------------------------------------------------------------------------------------|:-----------------------------------|
| L0_field_operator_probe     | probe field_type x operator with null-vector margins before derived feature promotion | probe_result                       |
| L1_single_field_factor_seed | promote only fields/transforms with non-null separation and non-L7 response evidence  | ordinary_alpha_seed_or_regime_only |
| L2_compatible_pair_probe    | test semantic-compatible field pairs only after both sides have L1 evidence           | interaction_probe                  |
| L3_state_conditioned_factor | allow regime/neutralizer fields only as conditioners unless response-backed as signal | factor_candidate                   |
| L4_replay_candidate_packet  | build full-universe vectors and control-null residual score packet before book replay | replay_candidate                   |

## Blocked Patterns

| pattern                                                     | status    |
|:------------------------------------------------------------|:----------|
| selected_top_bottom_only_orthogonalization                  | FORBIDDEN |
| control_dominated_candidate_expansion                       | FORBIDDEN |
| same_family_rerun_after_zero_survivors                      | FORBIDDEN |
| diagnostic_or_risk_defense_field_as_alpha_without_promotion | FORBIDDEN |
| formula_shape_expansion_without_null_margin                 | FORBIDDEN |
| May_or_known_stress_in_compiler_score                       | FORBIDDEN |

## Next Audit Plan

| stage        | action                                                                                           | executes_generation   | executes_replay   | executes_search   |
|:-------------|:-------------------------------------------------------------------------------------------------|:----------------------|:------------------|:------------------|
| A7FF-CORE47E | audit existing feature/operator/field-family artifacts for control-null-aware compiler readiness | False                 | False             | False             |
| A7FF-CORE48  | if CORE47E passes, define bounded null-first factor seed generation contract                     | False                 | False             | False             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE47E control-null-aware compiler readiness audit": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "current_candidate_expansion": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "same_family_rerun": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core47e_audit": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_new_generation": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE47_CONTROL_NULL_AWARE_COMPILER_CONTRACT_READY_FOR_CORE47E",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:03:33Z",
  "next_allowed": "A7FF-CORE47E control-null-aware compiler readiness audit",
  "source_decision": "PASS_A7FFCORE46_ROUTE_ARBITRATION_READY_FOR_CORE47_CONTRACT",
  "source_selected_route": "R3_control_null_aware_factor_compiler_contract",
  "source_stage": "A7FF-CORE46",
  "stage": "A7FF-CORE47"
}
```
