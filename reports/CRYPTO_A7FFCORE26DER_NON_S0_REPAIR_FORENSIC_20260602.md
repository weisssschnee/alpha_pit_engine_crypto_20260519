# CRYPTO A7FF-CORE26DER NON-S0 REPAIR FORENSIC

Generated: 2026-06-01T18:19:51Z

## Decision

`PASS_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE27X`

CORE26DER freezes the non-S0 lane repair failure. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core27_replay_contract": false,
  "authorizes_core27x_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE27X",
  "dominant_failure": "non_s0_lane_repair_no_strict_clean",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:19:51Z",
  "next_allowed": "A7FF-CORE27X search-readiness arbitration / objective reset contract",
  "non_s0_three_split_clean_count": 0,
  "non_s0_two_split_near_miss_count": 9,
  "s1_near_miss_count": 7,
  "s3_near_miss_count": 2,
  "source_decision": "HOLD_A7FFCORE26DE_NON_S0_REPAIR_INSUFFICIENT",
  "source_stage": "A7FF-CORE26DE",
  "stage": "A7FF-CORE26DER"
}
```

## Diagnosis

| finding                          | value                              | interpretation                                                          |
|:---------------------------------|:-----------------------------------|:------------------------------------------------------------------------|
| non_s0_three_split_clean_count   | 0                                  | strict non-S0 executable clean supply                                   |
| non_s0_two_split_near_miss_count | 9                                  | partial non-S0 supply                                                   |
| s1_near_miss_count               | 7                                  | S1 has partial but unstable response                                    |
| s3_near_miss_count               | 2                                  | S3 remains weaker than S1 after repair                                  |
| dominant_failure                 | non_s0_lane_repair_no_strict_clean | cannot create independent second executable lane from current field set |

## Lane Summary From CORE26DE

| seed_lane                      |   candidates |   clean_3_split |   near_2_split |   median_control |   median_spread |
|:-------------------------------|-------------:|----------------:|---------------:|-----------------:|----------------:|
| S1_liquidity_basis_positioning |          180 |               0 |              7 |          3.77657 |    -0.000517831 |
| S3_cross_family_bridge         |          180 |               0 |              2 |          5.89386 |    -0.000391979 |

## Recommended Actions

| next_stage                          | action                                         | rationale                                                                                        | authorized   |
|:------------------------------------|:-----------------------------------------------|:-------------------------------------------------------------------------------------------------|:-------------|
| A7FF-CORE27X                        | search readiness arbitration / objective reset | S0 local clue exists, but independent lane cannot be repaired from current S1/S3 targeted probes | True         |
| A7FF-CORE27 bounded replay contract | blocked                                        | non-S0 repair has zero three-split clean candidates                                              | False        |
| large search                        | blocked                                        | search would expand a single-lane S0 clue without independent lane support                       | False        |
