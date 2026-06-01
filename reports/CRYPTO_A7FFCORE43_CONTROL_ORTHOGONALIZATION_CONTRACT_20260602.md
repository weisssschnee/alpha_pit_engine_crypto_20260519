# CRYPTO A7FF-CORE43 CONTROL ORTHOGONALIZATION CONTRACT

Generated: 2026-06-01T20:32:28Z

## Decision

`PASS_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_READY_FOR_CORE43E`

CORE43 defines the control-orthogonalization layer after CORE42 rejected expansion of a weak single-family partial survivor. It does not run generation, search, large search, alpha proof, shadow, paper, or live.

## Orthogonalization Policy

| policy_id                       | description                                                                                                           | hard_requirement   |
|:--------------------------------|:----------------------------------------------------------------------------------------------------------------------|:-------------------|
| O0_full_universe_score_required | orthogonalization must occur before top/bottom book selection, so full timestamp-symbol candidate scores are required | True               |
| O1_stale_score_residual         | residualize candidate_score against stale_score by candidate/timestamp cross-section                                  | True               |
| O2_sign_arbitrariness_filter    | reject candidate/objective if original and sign-flip produce symmetric book results after residualization             | True               |
| O3_shuffle_null_margin          | book objective must beat row/time/symbol shuffle null variants with margin                                            | True               |
| O4_no_search                    | no new formula generation or large search before control-orthogonal packet passes                                     | True               |

## Required Control Vector Packet

| field                           | level         | required   |
|:--------------------------------|:--------------|:-----------|
| candidate_score_original        | full_universe | True       |
| candidate_score_stale           | full_universe | True       |
| candidate_score_sign_flip       | full_universe | True       |
| candidate_score_shuffle_time    | full_universe | True       |
| candidate_score_shuffle_symbol  | full_universe | True       |
| residual_score_stale_orthogonal | full_universe | True       |
| residual_score_null_orthogonal  | full_universe | True       |
| book_weight_from_residual_score | selected_book | True       |

## Current Input Audit

| artifact                            | status                             | reason                                                                          |
|:------------------------------------|:-----------------------------------|:--------------------------------------------------------------------------------|
| CORE39E selected book packet sample | INSUFFICIENT_FOR_ORTHOGONALIZATION | contains selected top/bottom rows, not full-universe score vectors              |
| CORE33 candidate queue              | SUFFICIENT_AS_CANDIDATE_SOURCE     | expressions and fields are available for rebuilding full-universe score vectors |

## Execution Plan

| stage        | action                                                                                               | executes_new_generation   | executes_search   |
|:-------------|:-----------------------------------------------------------------------------------------------------|:--------------------------|:------------------|
| A7FF-CORE43E | audit whether full-universe score/control vectors can be rebuilt from existing candidates and panels | False                     | False             |
| A7FF-CORE44  | if CORE43E passes, define full-universe orthogonal score packet construction                         | False                     | False             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE43E full-universe control-vector rebuild audit": true
  },
  "not_authorized": {
    "F1b_partial_survivor_expansion": true,
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core43e_audit": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_READY_FOR_CORE43E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:32:28Z",
  "next_allowed": "A7FF-CORE43E full-universe control-vector rebuild audit",
  "source_decision": "PASS_A7FFCORE42_ROUTE_ARBITRATION_READY_FOR_CORE43_CONTROL_ORTHOGONALIZATION_CONTRACT",
  "source_stage": "A7FF-CORE42",
  "stage": "A7FF-CORE43"
}
```
