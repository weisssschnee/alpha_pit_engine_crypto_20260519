# CRYPTO A7FF-CORE26D NON-S0 LANE REPAIR CONTRACT

Generated: 2026-06-01T18:03:15Z

## Decision

`PASS_A7FFCORE26D_NON_S0_LANE_REPAIR_CONTRACT_READY_FOR_CORE26DE`

CORE26D authorizes only a bounded non-S0 lane repair numeric probe. S0 clean candidates are calibration-only. No search, large search, alpha proof, shadow, paper, or live is authorized.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26de": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_open_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE26D_NON_S0_LANE_REPAIR_CONTRACT_READY_FOR_CORE26DE",
  "dominant_failure": "single_lane_clean_supply_after_split_repair",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:03:15Z",
  "next_allowed": "A7FF-CORE26DE non-S0 lane repair numeric probe",
  "source_decision": "PASS_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE26D",
  "source_stage": "A7FF-CORE26CER",
  "stage": "A7FF-CORE26D"
}
```

## Lane Policy

| lane                           | status                | allowed                                                                                          | blocked                                                |
|:-------------------------------|:----------------------|:-------------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| S3_cross_family_bridge         | primary_non_s0_repair | basis/OI/liquidity bridge variants around existing S3 near-miss; H8/H24; one-bar executable only | S0 fields, S3-only promotion, same-bar-only candidates |
| S1_liquidity_basis_positioning | secondary_repair      | liquidity x basis/positioning variants with stricter control filtering                           | basis-only/funding-only wrappers and H1 variants       |
| S0_positioning_price_basis     | calibration_only      | retain existing 4 clean candidates as reference                                                  | further S0 expansion in CORE26D                        |

## Gates

| gate                               | threshold                   |
|:-----------------------------------|:----------------------------|
| non_s0_three_split_clean_count     | >= 2                        |
| total_three_split_clean_lane_count | >= 2 including S0 reference |
| control_ratio_policy               | < 1.0 all pre-May splits    |
| search_authorization               | false                       |

## Execution Plan

| stage         | action                           | input                                                    | authorized   |
|:--------------|:---------------------------------|:---------------------------------------------------------|:-------------|
| A7FF-CORE26DE | non-S0 lane repair numeric probe | S3 near-miss + S1 secondary repair policy + S0 reference | True         |
| A7FF-CORE27   | bounded replay contract          | CORE26DE pass only                                       | False        |
