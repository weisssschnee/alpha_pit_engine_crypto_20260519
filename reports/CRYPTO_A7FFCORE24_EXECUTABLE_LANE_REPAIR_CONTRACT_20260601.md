# CRYPTO A7FF-CORE24 EXECUTABLE LANE REPAIR CONTRACT

Generated: 2026-06-01T15:37:03Z

## Decision

`PASS_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_READY_FOR_CORE24E`

CORE24 defines a bounded repair path for executable lane breadth. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core24e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_READY_FOR_CORE24E",
  "dominant_failure": "executable_lane_supply_too_narrow",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:37:03Z",
  "missing_executable_lanes": [
    "S0_positioning_price_basis",
    "S1_basis_premium_funding"
  ],
  "next_allowed": "A7FF-CORE24E bounded executable lane repair packet construction",
  "source_decision": "PASS_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_COMPLETE_READY_FOR_CORE24",
  "source_stage": "A7FF-CORE23R",
  "stage": "A7FF-CORE24"
}
```

## Lane Policy

| lane                       | repair_target                                                                       | allowed_fields                                         | forbidden                                              |
|:---------------------------|:------------------------------------------------------------------------------------|:-------------------------------------------------------|:-------------------------------------------------------|
| S0_positioning_price_basis | convert same-bar H4/H8 diagnostic supply into one-bar executable H4+/H24 candidates | positioning, price/mark/index, basis/premium           | same-bar-only promotion; direct high-turnover 1h rerun |
| S1_basis_premium_funding   | restore funding/basis lane under executable horizon and one-bar lag                 | basis/premium, funding, low-turnover trend/vol context | funding-only wrapper; basis-only wrapper               |
| S2_taker_flow_liquidity_oi | retain existing H24 executable clue as calibration, not expansion seed              | taker ratio, OI, liquidity state                       | single-lane promotion                                  |
| S3_cross_family_bridge     | retain non-L5 H24 executable bridge as calibration, not proof                       | positioning, OI value, cross-family bridge             | S3-only selector dominance                             |

## Gates

| gate                           | threshold       | scope                                                    |
|:-------------------------------|:----------------|:---------------------------------------------------------|
| min_executable_candidate_count | >= 6            | one-bar H4+ / H24 diagnostic packet                      |
| min_executable_lane_count      | >= 3            | S0/S1/S2/S3 lanes                                        |
| min_non_l5_candidate_count     | >= 3            | non-L7/non-L5 preferred; L5 cannot dominate              |
| same_bar_only_candidate_policy | diagnostic_only | cannot enter replay-clean packet unless one-bar positive |
| search_authorization           | false           | CORE24 authorizes packet construction only               |

## Execution Plan

| stage        | action                                             | input                                             | authorized   |
|:-------------|:---------------------------------------------------|:--------------------------------------------------|:-------------|
| A7FF-CORE24E | bounded executable lane repair packet construction | CORE17E locked packet + CORE23E/23R lane findings | True         |
| A7FF-CORE25  | lower-turnover bounded replay contract             | CORE24E pass only                                 | False        |

## Blocked

| blocked_task                        | reason                                                                  |
|:------------------------------------|:------------------------------------------------------------------------|
| large search                        | blocked: executable lane supply is too narrow                           |
| formula generation/search           | blocked: CORE24 authorizes bounded lane repair packet construction only |
| alpha proof / shadow / paper / live | not authorized                                                          |
