# CRYPTO A7FF-CORE24E EXECUTABLE LANE REPAIR PACKET

Generated: 2026-06-01T15:39:46Z

## Decision

`HOLD_A7FFCORE24E_SOURCE_PACKET_LANE_COVERAGE_INSUFFICIENT`

CORE24E builds a bounded repair packet from existing rows. Same-bar repair seeds remain diagnostic-only. This stage does not authorize formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core25_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "executable_clean_count_lt_6",
    "executable_clean_lane_count_lt_3",
    "repair_packet_missing_lanes"
  ],
  "decision": "HOLD_A7FFCORE24E_SOURCE_PACKET_LANE_COVERAGE_INSUFFICIENT",
  "executable_clean_candidate_count": 4,
  "executable_clean_lane_count": 2,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:39:46Z",
  "missing_executable_lanes": [
    "S0_positioning_price_basis",
    "S1_liquidity_basis_positioning"
  ],
  "missing_packet_lanes": [
    "S0_positioning_price_basis"
  ],
  "next_allowed": "A7FF-CORE24R lane packet coverage forensic",
  "repair_packet_candidate_count": 12,
  "repair_packet_lane_count": 3,
  "source_decision": "PASS_A7FFCORE24_EXECUTABLE_LANE_REPAIR_CONTRACT_READY_FOR_CORE24E",
  "source_stage": "A7FF-CORE24",
  "stage": "A7FF-CORE24E"
}
```

## Diagnosis

| finding                  | value                                                     | interpretation                                        |
|:-------------------------|:----------------------------------------------------------|:------------------------------------------------------|
| repair_packet_count      | 12                                                        | includes executable clean and diagnostic repair seeds |
| executable_clean_count   | 4                                                         | true one-bar executable clean supply                  |
| executable_clean_lanes   | 2                                                         | true executable lane breadth                          |
| missing_executable_lanes | S0_positioning_price_basis,S1_liquidity_basis_positioning | lanes not yet executable                              |
| missing_packet_lanes     | S0_positioning_price_basis                                | lanes absent even as repair packet seeds              |

## Role Summary

| packet_role            |   candidate_count |   lane_count |   label_family_count |
|:-----------------------|------------------:|-------------:|---------------------:|
| executable_clean       |                 4 |            2 |                    4 |
| one_bar_near_miss_seed |                 5 |            1 |                    3 |
| same_bar_repair_seed   |                 3 |            2 |                    3 |

## Lane Summary

| packet_role            | seed_lane                      |   candidate_count |   label_family_count |
|:-----------------------|:-------------------------------|------------------:|---------------------:|
| executable_clean       | S2_taker_flow_liquidity_oi     |                 1 |                    1 |
| executable_clean       | S3_cross_family_bridge         |                 3 |                    3 |
| one_bar_near_miss_seed | S3_cross_family_bridge         |                 5 |                    3 |
| same_bar_repair_seed   | S1_liquidity_basis_positioning |                 2 |                    2 |
| same_bar_repair_seed   | S3_cross_family_bridge         |                 1 |                    1 |

## Source Lane Horizon Coverage

| seed_lane                      |   candidate_count | horizons   |
|:-------------------------------|------------------:|:-----------|
| S0_positioning_price_basis     |                31 | 1          |
| S1_liquidity_basis_positioning |                33 | 1,4        |
| S2_taker_flow_liquidity_oi     |                12 | 1,4,24     |
| S3_cross_family_bridge         |                20 | 1,4,8,24   |
