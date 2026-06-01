# CRYPTO A7FF-CORE18 BOUNDED REPLAY PREFLIGHT CONTRACT

Generated: 2026-06-01T14:41:20Z

## Decision

`PASS_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE18E`

CORE18 defines the bounded replay preflight contract only. It does not execute bounded replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_bounded_replay_execution": false,
  "authorizes_core18e": true,
  "authorizes_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE18E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:41:20Z",
  "next_allowed": "A7FF-CORE18E bounded replay preflight execution",
  "packet_size": 96,
  "source_decision": "PASS_A7FFCORE17E_OBJECTIVE_SEED_PACKET_READY_FOR_CORE18_CONTRACT",
  "source_stage": "A7FF-CORE17E",
  "stage": "A7FF-CORE18"
}
```

## Replay Preflight Contract

| contract_item   | requirement                                                                                     | hard_gate   |
|:----------------|:------------------------------------------------------------------------------------------------|:------------|
| input_packet    | use A7FF-CORE17E objective seed packet as the only candidate source                             | True        |
| candidate_count | packet_size == 96; no extra generation, no stale candidate injection                            | True        |
| labels          | evaluate locked label_family/label_horizon plus replay book labels; report non-L5 separately    | True        |
| controls        | wrong-lag future, stale lag, row/time/symbol shuffle, same-family placebo weaker than candidate | True        |
| neutralization  | global, liquidity-tier, latent-state, meme/multiplier aware summaries required                  | True        |
| cost_lag        | 1bar lag and cost proxy stress required before any deep audit authorization                     | True        |
| breadth         | preserve four seed lanes; top selected lane share <= 35%                                        | True        |
| authorization   | CORE18 authorizes only CORE18E replay preflight execution, not bounded replay/search            | True        |

## Execution Plan

| stage        | action                             | input                              | output                                                    | authorized   |
|:-------------|:-----------------------------------|:-----------------------------------|:----------------------------------------------------------|:-------------|
| A7FF-CORE18E | bounded replay preflight execution | A7FF-CORE17E objective seed packet | materialization/eval/control readiness for bounded replay | True         |
| A7FF-CORE19  | bounded replay contract            | A7FF-CORE18E preflight pass        | contract only                                             | False        |

## Blocked

| blocked_task                        | reason                                                            |
|:------------------------------------|:------------------------------------------------------------------|
| A7FF bounded replay execution       | blocked until CORE18E preflight passes and CORE19 contract exists |
| A7FF formula generation/search      | blocked: CORE18 is replay preflight contract only                 |
| A7FF large search                   | blocked until bounded replay produces control-clean candidates    |
| alpha proof / shadow / paper / live | not authorized                                                    |
