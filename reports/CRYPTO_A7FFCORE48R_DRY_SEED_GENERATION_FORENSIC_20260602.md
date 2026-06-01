# CRYPTO A7FF-CORE48R DRY SEED GENERATION FORENSIC

Generated: 2026-06-01T21:15:05Z

## Decision

`PASS_A7FFCORE48R_DRY_SEED_FORENSIC_READY_FOR_CORE48S_OPERATOR_REPAIR`

CORE48R classifies CORE48E as a supply-width improvement with an operator/motif coverage failure, not a field-family failure. It does not authorize replay, formula search, large search, proof, shadow, paper, live, or promotion.

## Gate Forensic

| metric                     |   value | pass   | forensic_class           |
|:---------------------------|--------:|:-------|:-------------------------|
| generated_seed_count       |    1200 | True   | pass                     |
| eligible_seed_count        |    1200 | True   | pass                     |
| semantic_family_count      |      12 | True   | pass                     |
| operator_count             |       3 | False  | operator_breadth_fail    |
| role_violation_count       |       0 | True   | pass                     |
| missing_contract_count     |       0 | True   | pass                     |
| family_cap_violation_count |       0 | True   | pass                     |
| motif_cap_violation_count  |       3 | False  | motif_concentration_fail |

## Operator Forensic

| operator   |   seed_count |   semantic_family_count |   seed_share |
|:-----------|-------------:|------------------------:|-------------:|
| Delta      |          409 |                      12 |     0.340833 |
| CSRank     |          408 |                      12 |     0.34     |
| Identity   |          383 |                      12 |     0.319167 |

## Family Forensic

| semantic_pair                         |   seed_count |   operator_count |   seed_share |
|:--------------------------------------|-------------:|-----------------:|-------------:|
| basis_premium_like|positioning_like   |          285 |                3 |   0.2375     |
| basis_premium_like|liquidity_like     |          225 |                3 |   0.1875     |
| basis_premium_like|basis_premium_like |          210 |                3 |   0.175      |
| basis_premium_like|volatility_like    |          114 |                3 |   0.095      |
| basis_premium_like|state_or_taxonomy  |           90 |                3 |   0.075      |
| basis_premium_like|price_like         |           90 |                3 |   0.075      |
| basis_premium_like|generic_numeric    |           90 |                3 |   0.075      |
| basis_premium_like|funding_like       |           30 |                3 |   0.025      |
| liquidity_like|price_like             |           30 |                3 |   0.025      |
| price_like|price_like                 |           15 |                3 |   0.0125     |
| basis_premium_like                    |           14 |                3 |   0.0116667  |
| price_like                            |            7 |                3 |   0.00583333 |

## Route Options

| route_id                                  | decision   | reason                                                                                                       |
|:------------------------------------------|:-----------|:-------------------------------------------------------------------------------------------------------------|
| R0_relax_operator_gate                    | REJECT     | would admit unprobed operators into eligible null-first queue                                                |
| R1_proceed_to_core49                      | REJECT     | eligible seed queue has only three native operators and motif caps fail                                      |
| R2_operator_null_coverage_repair_contract | SELECT     | field/family breadth is adequate; repair missing native null-aware operator coverage before vector preflight |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core48s_operator_repair_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE48R_DRY_SEED_FORENSIC_READY_FOR_CORE48S_OPERATOR_REPAIR",
  "dominant_failure": "operator_breadth_and_motif_concentration_after_successful_seed_supply",
  "eligible_operator_count": 3,
  "eligible_seed_count": 1200,
  "eligible_semantic_family_count": 12,
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:15:05Z",
  "next_allowed": "A7FF-CORE48S operator-null coverage repair contract",
  "source_decision": "HOLD_A7FFCORE48E_NULL_FIRST_DRY_SEEDS_INSUFFICIENT",
  "source_stage": "A7FF-CORE48E",
  "stage": "A7FF-CORE48R"
}
```
