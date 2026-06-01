# CRYPTO A7FF-CORE46 ORTHOGONAL FAILURE ROUTE ARBITRATION

Generated: 2026-06-01T20:58:54Z

## Decision

`PASS_A7FFCORE46_ROUTE_ARBITRATION_READY_FOR_CORE47_CONTRACT`

CORE46 freezes the zero-survivor, control-dominated orthogonal replay result and selects the next non-search route. It does not authorize formula generation, large search, alpha proof, shadow, paper, or live.

## Route Options

| route_id                                       | decision   | reason                                                                                                                 | authorizes_next   |
|:-----------------------------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------|:------------------|
| R0_expand_current_core33_candidates            | REJECT     | CORE45E/45R found zero survivors after full-universe control orthogonalization                                         | False             |
| R1_large_formula_search                        | REJECT     | current objective surface remains control dominated; large search would scale the wrong target                         | False             |
| R2_same_family_rerun                           | REJECT     | F1a/F1b/F2a all failed under residual-null book replay                                                                 | False             |
| R3_control_null_aware_factor_compiler_contract | SELECT     | next work must redesign feature-to-factor generation around control-null separation before new candidates enter replay | True              |

## Freeze Matrix

| item                                                    | status                   |
|:--------------------------------------------------------|:-------------------------|
| CORE33 candidate expansion                              | NOT_AUTHORIZED           |
| F1a/F1b/F2a same-family rerun                           | NOT_AUTHORIZED           |
| large formula search                                    | NOT_AUTHORIZED           |
| alpha proof                                             | NOT_AUTHORIZED           |
| shadow/paper/live                                       | NOT_AUTHORIZED           |
| A7FF-CORE47 control-null-aware factor compiler contract | AUTHORIZED_CONTRACT_ONLY |

## Selected Route

```json
{
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "goal": "define how future feature/factor generation must optimize original-vs-null separability before replay",
  "next_stage": "A7FF-CORE47",
  "next_stage_name": "control-null-aware feature-to-factor compiler contract",
  "selected_route": "R3_control_null_aware_factor_compiler_contract"
}
```

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE47 control-null-aware feature-to-factor compiler contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "current_candidate_expansion": true,
    "formula_search": true,
    "large_search": true,
    "same_family_rerun": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core47_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE46_ROUTE_ARBITRATION_READY_FOR_CORE47_CONTRACT",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:58:54Z",
  "next_allowed": "A7FF-CORE47 control-null-aware feature-to-factor compiler contract",
  "selected_route": "R3_control_null_aware_factor_compiler_contract",
  "source_decision": "PASS_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_READY_FOR_CORE46_ROUTE_ARBITRATION",
  "source_dominant_failure": "orthogonal_book_replay_control_dominated_zero_survivors",
  "source_stage": "A7FF-CORE45R",
  "stage": "A7FF-CORE46"
}
```
