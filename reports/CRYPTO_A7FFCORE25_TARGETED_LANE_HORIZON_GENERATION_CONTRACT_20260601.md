# CRYPTO A7FF-CORE25 TARGETED LANE/HORIZON GENERATION CONTRACT

Generated: 2026-06-01T15:44:06Z

## Decision

`PASS_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_READY_FOR_CORE25E`

CORE25 authorizes a bounded targeted generation preflight to repair missing executable lane/horizon coverage. It is not open formula search and does not authorize replay execution, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core25e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_open_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "authorizes_targeted_generation": true,
  "decision": "PASS_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_READY_FOR_CORE25E",
  "dominant_failure": "source_packet_missing_executable_lane_horizon_coverage",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:44:06Z",
  "next_allowed": "A7FF-CORE25E targeted lane/horizon generation preflight packet",
  "source_decision": "PASS_A7FFCORE24R_LANE_PACKET_FORENSIC_COMPLETE_READY_FOR_CORE25",
  "source_stage": "A7FF-CORE24R",
  "stage": "A7FF-CORE25"
}
```

## Target Policy

| target                         | reason                                                  | horizons   | allowed_templates                                                                    | blocked_templates                                                 |   min_packet_quota |
|:-------------------------------|:--------------------------------------------------------|:-----------|:-------------------------------------------------------------------------------------|:------------------------------------------------------------------|-------------------:|
| S0_positioning_price_basis     | missing from H4+ repair packet                          | 4h,8h,24h  | positioning x basis/price lower-turnover transforms; rank/tsrank/zscore/delta/spread | H1-only rerun; same-bar promotion; open grammar                   |                160 |
| S1_liquidity_basis_positioning | same-bar diagnostic exists but one-bar executable fails | 4h,8h,24h  | liquidity x basis/positioning lag-resilient smoothing and low-turnover transforms    | basis-only wrapper; funding-only wrapper; same-bar-only promotion |                160 |
| S2_taker_flow_liquidity_oi     | existing H24 executable clue is calibration lane        | 24h        | calibration variants only                                                            | single-lane expansion                                             |                 40 |
| S3_cross_family_bridge         | existing non-L5 executable bridge is calibration lane   | 8h,24h     | calibration variants only                                                            | S3-only dominance                                                 |                 40 |

## Generation Budget

| item                          |   value |
|:------------------------------|--------:|
| generated_blueprints_max      |    4800 |
| materialization_preflight_max |     960 |
| numeric_probe_max             |     480 |
| target_lane_min_count         |       2 |
| target_horizon_min_count      |       3 |

## Gates

| gate                      | requirement                                                                            |
|:--------------------------|:---------------------------------------------------------------------------------------|
| targeted_generation_only  | all candidates must belong to CORE25 target lanes and H4+/H24 horizons                 |
| s0_s1_presence            | S0 and S1 must both be present in generated packet                                     |
| one_bar_executable_policy | same-bar-only candidates remain diagnostic; one-bar positive required for replay-clean |
| lane_cap                  | no lane may exceed 45% of materialization preflight packet                             |
| search_auth               | no search, large search, alpha proof, shadow, paper, or live                           |

## Execution Plan

| stage        | action                                                                       | input                                              | authorized   |
|:-------------|:-----------------------------------------------------------------------------|:---------------------------------------------------|:-------------|
| A7FF-CORE25E | targeted lane/horizon blueprint generation and preflight packet construction | CORE25 contract + existing field/operator registry | True         |
| A7FF-CORE26  | targeted numeric probe contract                                              | CORE25E pass only                                  | False        |
