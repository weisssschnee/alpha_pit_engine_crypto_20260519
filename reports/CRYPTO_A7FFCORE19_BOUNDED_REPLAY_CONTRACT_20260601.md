# CRYPTO A7FF-CORE19 BOUNDED REPLAY CONTRACT

Generated: 2026-06-01T14:44:32Z

## Decision

`PASS_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE19E`

CORE19 authorizes bounded replay execution on the locked packet only. It does not authorize formula generation, search expansion, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core19e_bounded_replay_execution": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE19E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:44:32Z",
  "input_packet_size": 96,
  "next_allowed": "A7FF-CORE19E bounded replay execution on locked packet",
  "source_decision": "PASS_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_READY_FOR_CORE19_CONTRACT",
  "source_stage": "A7FF-CORE18E",
  "stage": "A7FF-CORE19"
}
```

## Replay Scope

| item            | value                                                                            | hard_gate   |
|:----------------|:---------------------------------------------------------------------------------|:------------|
| input_packet    | A7FF-CORE17E objective seed packet                                               | True        |
| candidate_count | 96                                                                               | True        |
| selection_mode  | bounded locked packet only; no generation; no mutation; no selector expansion    | True        |
| book            | top/bottom cross-sectional replay proxy with dollar-neutral and lane/family caps | True        |
| controls        | wrong-lag future, stale, row/time/symbol shuffle, same-family placebo            | True        |
| latency         | field-native timing plus one-bar lag stress                                      | True        |
| cost            | 2/5/10/20 bps proxy tiers                                                        | True        |
| neutralization  | global, liquidity tier, latent state, meme/multiplier aware                      | True        |
| statistics      | overlap robust and non-overlap offset stats                                      | True        |

## Pass Gates

| gate               | requirement                                                                          |
|:-------------------|:-------------------------------------------------------------------------------------|
| control_clean      | no selected candidate with control_ratio >= 1.0 in any pre-May split                 |
| lane_breadth       | selected lanes >= 3 and top lane share <= 0.40                                       |
| non_l5_translation | non-L5 evidence must remain nonzero; L5-only pass is diagnostic only                 |
| lag_survival       | one-bar lag replay proxy must not flip or collapse for selected candidates           |
| cost_survival      | 5bps and 10bps tiers must remain directionally positive before deep audit            |
| stress_policy      | May/stress labels post-selection only; no May in ranking, mutation, or weight update |

## Input Lane Counts

| seed_lane                      |   rows |
|:-------------------------------|-------:|
| S1_liquidity_basis_positioning |     33 |
| S0_positioning_price_basis     |     31 |
| S3_cross_family_bridge         |     20 |
| S2_taker_flow_liquidity_oi     |     12 |
