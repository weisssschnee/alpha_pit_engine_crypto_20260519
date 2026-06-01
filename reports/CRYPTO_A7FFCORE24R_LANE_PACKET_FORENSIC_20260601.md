# CRYPTO A7FF-CORE24R LANE PACKET FORENSIC

Generated: 2026-06-01T15:41:08Z

## Decision

`PASS_A7FFCORE24R_LANE_PACKET_FORENSIC_COMPLETE_READY_FOR_CORE25`

CORE24R shows the old locked packet cannot internally repair executable lane breadth. It authorizes only a targeted lane/horizon generation contract, not search execution or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core25_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE24R_LANE_PACKET_FORENSIC_COMPLETE_READY_FOR_CORE25",
  "dominant_failure": "source_packet_missing_executable_lane_horizon_coverage",
  "executable_clean_candidate_count": 4,
  "executable_clean_lane_count": 2,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:41:08Z",
  "missing_executable_lanes": [
    "S0_positioning_price_basis",
    "S1_liquidity_basis_positioning"
  ],
  "missing_packet_lanes": [
    "S0_positioning_price_basis"
  ],
  "next_allowed": "A7FF-CORE25 targeted executable-lane horizon generation contract",
  "repair_packet_candidate_count": 12,
  "repair_packet_lane_count": 3,
  "source_decision": "HOLD_A7FFCORE24E_SOURCE_PACKET_LANE_COVERAGE_INSUFFICIENT",
  "source_stage": "A7FF-CORE24E",
  "stage": "A7FF-CORE24R"
}
```

## Diagnosis

| finding                       | value                                                  | interpretation                                                                                      |
|:------------------------------|:-------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| repair_packet_exists          | 12                                                     | packet can preserve diagnostic seeds, but cannot become executable evidence                         |
| s0_absent_from_h4_plus_packet | True                                                   | S0 source candidates are H1-only and cannot be repaired without new bounded lane/horizon generation |
| s1_same_bar_only              | True                                                   | S1 enters packet as diagnostic but fails one-bar executable gate                                    |
| dominant_failure              | source_packet_missing_executable_lane_horizon_coverage | old locked packet cannot supply enough executable lane breadth                                      |

## Target Lanes

| target_lane                    | needed_horizons   | reason                                                          | generation_scope                                       |
|:-------------------------------|:------------------|:----------------------------------------------------------------|:-------------------------------------------------------|
| S0_positioning_price_basis     | 4h/8h/24h         | current source packet has S0 only at H1                         | bounded lane-native transformations only               |
| S1_liquidity_basis_positioning | 4h/8h/24h         | same-bar diagnostic exists, one-bar executable conversion fails | lower-turnover smoothing / lag-resilient variants only |

## Role Summary From CORE24E

| packet_role            |   candidate_count |   lane_count |   label_family_count |
|:-----------------------|------------------:|-------------:|---------------------:|
| executable_clean       |                 4 |            2 |                    4 |
| one_bar_near_miss_seed |                 5 |            1 |                    3 |
| same_bar_repair_seed   |                 3 |            2 |                    3 |

## Lane Summary From CORE24E

| packet_role            | seed_lane                      |   candidate_count |   label_family_count |
|:-----------------------|:-------------------------------|------------------:|---------------------:|
| executable_clean       | S2_taker_flow_liquidity_oi     |                 1 |                    1 |
| executable_clean       | S3_cross_family_bridge         |                 3 |                    3 |
| one_bar_near_miss_seed | S3_cross_family_bridge         |                 5 |                    3 |
| same_bar_repair_seed   | S1_liquidity_basis_positioning |                 2 |                    2 |
| same_bar_repair_seed   | S3_cross_family_bridge         |                 1 |                    1 |

## Source Horizon Coverage

| seed_lane                      |   candidate_count | horizons   |
|:-------------------------------|------------------:|:-----------|
| S0_positioning_price_basis     |                31 | 1          |
| S1_liquidity_basis_positioning |                33 | 1,4        |
| S2_taker_flow_liquidity_oi     |                12 | 1,4,24     |
| S3_cross_family_bridge         |                20 | 1,4,8,24   |

## Recommended Actions

| next_stage        | action                                               | rationale                                                                                                         | authorized   |
|:------------------|:-----------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|:-------------|
| A7FF-CORE25       | targeted executable-lane horizon generation contract | bounded generation is required for S0 H4+/H24 and S1 one-bar conversion; old packet cannot repair this internally | True         |
| A7FF large search | blocked                                              | needed generation is lane/horizon-targeted, not open grammar or large search                                      | False        |
