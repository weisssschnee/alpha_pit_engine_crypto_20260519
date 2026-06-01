# CRYPTO A7FF-CORE26C SPLIT-CONSISTENCY REPAIR CONTRACT

Generated: 2026-06-01T17:45:52Z

## Decision

`PASS_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_READY_FOR_CORE26CE`

CORE26C authorizes a bounded repair of split consistency and control dominance after targeted numeric probe failure. It does not authorize open formula generation, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26ce": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_open_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_READY_FOR_CORE26CE",
  "dominant_failure": "split_consistency_failure_after_targeted_generation",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T17:45:52Z",
  "near_miss_count": 7,
  "near_miss_lane_count": 2,
  "next_allowed": "A7FF-CORE26CE split-consistency repair numeric probe",
  "source_decision": "PASS_A7FFCORE26R_TARGETED_NUMERIC_FORENSIC_COMPLETE_READY_FOR_CORE26C",
  "source_stage": "A7FF-CORE26R",
  "stage": "A7FF-CORE26C"
}
```

## Lane Policy

| lane                           | status            | evidence                                                                    | allowed_repair                                                                        |
|:-------------------------------|:------------------|:----------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|
| S0_positioning_price_basis     | near_miss_primary | 3 two-split near misses, 14 spread-positive candidates, high control median | control-resistant variants and split-stability filters around existing S0 field pairs |
| S3_cross_family_bridge         | near_miss_primary | 4 two-split near misses, positive median spread, high control median        | control-resistant bridge variants; cap S3 dominance                                   |
| S1_liquidity_basis_positioning | secondary_weak    | spread-positive candidates exist but zero two-split near miss               | diagnostic only unless control/spread improves                                        |
| S2_taker_flow_liquidity_oi     | blocked_weak      | zero spread-positive three-split and high control                           | no expansion in CORE26C                                                               |

## Repair Budget

| item                     | value                                                                 |
|:-------------------------|:----------------------------------------------------------------------|
| generated_blueprints_max | 2400                                                                  |
| numeric_probe_max        | 360                                                                   |
| focus_lanes              | S0,S3 primary; S1 diagnostic cap; S2 blocked                          |
| required_output          | >=6 three-split clean candidates and >=3 lanes before replay contract |

## Existing Lane Forensic

| seed_lane                      |   candidates |   pass_3_split |   pass_2_split |   pass_spread_3_split |   median_control |   median_spread |
|:-------------------------------|-------------:|---------------:|---------------:|----------------------:|-----------------:|----------------:|
| S0_positioning_price_basis     |          160 |              0 |              3 |                    14 |          4.69565 |    -0.000443243 |
| S1_liquidity_basis_positioning |          160 |              0 |              0 |                     5 |          4.19148 |    -0.00142368  |
| S2_taker_flow_liquidity_oi     |           80 |              0 |              0 |                     0 |         10.3456  |    -0.000557736 |
| S3_cross_family_bridge         |           80 |              0 |              4 |                     6 |          7.77357 |     0.000206658 |

## Blocked

| blocked_task                           | reason                                              |
|:---------------------------------------|:----------------------------------------------------|
| CORE27 bounded replay contract         | no three-split executable candidates                |
| open formula generation / large search | near misses are lane-specific and control-dominated |
| alpha proof / shadow / paper / live    | not authorized                                      |

## Execution Plan

| stage         | action                                                | input                                      | authorized   |
|:--------------|:------------------------------------------------------|:-------------------------------------------|:-------------|
| A7FF-CORE26CE | split-consistency repair generation and numeric probe | CORE26R near-miss candidates + lane policy | True         |
| A7FF-CORE27   | bounded replay contract                               | CORE26CE pass only                         | False        |
