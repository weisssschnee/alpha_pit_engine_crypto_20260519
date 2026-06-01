# CRYPTO A7FF-CORE17 OBJECTIVE SEED POLICY CONTRACT

Generated: 2026-06-01T14:37:41Z

## Decision

`PASS_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_READY_FOR_CORE17E`

CORE17 converts the locked CORE16L strict queue into objective seed policy for packet construction only. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core17e": true,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_READY_FOR_CORE17E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:37:41Z",
  "next_allowed": "A7FF-CORE17E objective seed packet construction audit",
  "seed_lane_count": 4,
  "seed_queue_size": 96,
  "source_decision": "PASS_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCKED_READY_FOR_CORE17_CONTRACT",
  "source_stage": "A7FF-CORE16L",
  "stage": "A7FF-CORE17",
  "top_seed_lane_share": 0.34375
}
```

## Seed Lane Summary

| seed_lane                      | second_pass_family     |   rows |   label_family_count |   horizon_count |   operator_count |   median_control_ratio |   lag_ok_count |
|:-------------------------------|:-----------------------|-------:|---------------------:|----------------:|-----------------:|-----------------------:|---------------:|
| S1_liquidity_basis_positioning | H1_I5_deconcentration  |     33 |                    3 |               2 |                2 |               0.71876  |             33 |
| S0_positioning_price_basis     | H0_I3_deconcentration  |     31 |                    3 |               1 |                2 |               0.555319 |             31 |
| S3_cross_family_bridge         | H3_cross_family_bridge |     20 |                    4 |               4 |                2 |               0.830484 |             15 |
| S2_taker_flow_liquidity_oi     | H2_I4_near_miss_repair |     12 |                    4 |               3 |                2 |               0.741474 |              5 |

## Objective Policy

| policy_id              | rule                                                                          | reason                                                                                                                  |
|:-----------------------|:------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| P0_seed_packet_only    | CORE17 authorizes only CORE17E seed packet construction                       | locked preseed rows still require packet-level dedup, label/horizon balance, and replay preflight before numeric replay |
| P1_no_search           | no open grammar formula generation or large search                            | CORE16 produced a governed seed queue, not an alpha pool                                                                |
| P2_no_direct_promotion | no seed row can become research_candidate without bounded replay and controls | current evidence is pre-replay response/control surface only                                                            |
| P3_preserve_breadth    | CORE17E must preserve all four seed lanes and cap top lane share              | prior failure mode was family concentration                                                                             |

## Blocked

| blocked_task                        | reason                                                                      |
|:------------------------------------|:----------------------------------------------------------------------------|
| A7FF bounded replay                 | blocked until CORE17E seed packet and CORE18 replay preflight contract pass |
| A7FF formula generation/search      | blocked: CORE17 is seed policy contract only                                |
| A7FF large search                   | blocked until bounded replay produces control-clean evidence                |
| alpha proof / shadow / paper / live | not authorized                                                              |
