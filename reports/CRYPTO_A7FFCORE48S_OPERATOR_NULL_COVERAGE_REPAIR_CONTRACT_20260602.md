# CRYPTO A7FF-CORE48S OPERATOR-NULL COVERAGE REPAIR CONTRACT

Generated: 2026-06-01T21:19:05Z

## Decision

`PASS_A7FFCORE48S_OPERATOR_NULL_COVERAGE_REPAIR_CONTRACT_READY_FOR_CORE48SE`

CORE48S targets the CORE48E failure mode: operator breadth and motif concentration after successful seed supply. It is contract-only and does not execute replay, search, proof, shadow, paper, live, or promotion.

## Repair Policy

| policy_id                                    | description                                                                                                          | hard_requirement   |
|:---------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|:-------------------|
| P0_repair_operator_breadth_not_field_breadth | CORE48E already has 1200 eligible seeds and 12 semantic families; repair target is operator/motif breadth            | True               |
| P1_no_unprobed_operator_promotion            | new operators may enter repaired queue only if assigned native null-margin proxy and marked repaired_native          | True               |
| P2_keep_null_first_gate                      | operators do not bypass original-vs-null margin, role, family, or motif gates                                        | True               |
| P3_no_replay_search                          | CORE48S/48SE do not authorize numeric replay, formula search, large search, proof, shadow, paper, live, or promotion | True               |

## Operator Repair Set

| operator        | repair_status                        | economic_role                                       | null_margin_proxy                                                                  |
|:----------------|:-------------------------------------|:----------------------------------------------------|:-----------------------------------------------------------------------------------|
| SpreadShortLong | authorized_for_repaired_native_probe | relative-value / slow-fast dislocation              | base semantic-type best native operator margin, capped by field best_control_ratio |
| WinsorZ         | authorized_for_repaired_native_probe | shock clipping / robust delta state                 | base semantic-type best native operator margin, capped by field best_control_ratio |
| AbsDelta        | authorized_for_repaired_native_probe | magnitude dislocation without sign assumption       | Delta margin if available, otherwise field best_control_ratio                      |
| SignedRankDelta | authorized_for_repaired_native_probe | cross-sectional ranked delta with sign preservation | CSRank and Delta margin minimum if available                                       |

## Repaired Gate

| gate                       | threshold   |
|:---------------------------|:------------|
| generated_seed_count       | >= 1200     |
| eligible_seed_count        | >= 360      |
| semantic_family_count      | >= 8        |
| operator_count             | >= 5        |
| motif_cap_violation_count  | 0           |
| family_cap_violation_count | 0           |
| role_violation_count       | 0           |
| repair_operator_share      | <= 0.55     |

## Execution Plan

| stage         | action                                                                    | executes_generation   | executes_replay   | executes_search   |   max_seed_count |
|:--------------|:--------------------------------------------------------------------------|:----------------------|:------------------|:------------------|-----------------:|
| A7FF-CORE48SE | run bounded repaired null-first dry generation with expanded operator set | True                  | False             | False             |             1800 |
| A7FF-CORE49   | if CORE48SE passes, define full-universe null-vector preflight contract   | False                 | False             | False             |              nan |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE48SE repaired null-first dry seed generation": true
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
  "authorizes_core48se_repaired_dry_generation": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE48S_OPERATOR_NULL_COVERAGE_REPAIR_CONTRACT_READY_FOR_CORE48SE",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:19:05Z",
  "next_allowed": "A7FF-CORE48SE repaired null-first dry seed generation",
  "source_decision": "PASS_A7FFCORE48R_DRY_SEED_FORENSIC_READY_FOR_CORE48S_OPERATOR_REPAIR",
  "source_dominant_failure": "operator_breadth_and_motif_concentration_after_successful_seed_supply",
  "source_stage": "A7FF-CORE48R",
  "stage": "A7FF-CORE48S"
}
```
