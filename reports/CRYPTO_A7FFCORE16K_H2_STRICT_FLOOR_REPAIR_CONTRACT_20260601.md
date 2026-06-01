# CRYPTO A7FF-CORE16K H2 STRICT-FLOOR REPAIR CONTRACT

Generated: 2026-06-01T12:44:59Z

## Decision

`PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE`

CORE16K defines a narrow repair for the H2/I4 strict floor. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "additional_h2_needed": 3,
  "authorizes_alpha_proof": false,
  "authorizes_core16ke": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE",
  "excluded_h2_near_miss_count": 3,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T12:44:59Z",
  "next_allowed": "A7FF-CORE16KE H2/I4 strict-floor repair execution",
  "source_decision": "HOLD_A7FFCORE16J_STRICT_QUEUE_H2_FLOOR_INSUFFICIENT",
  "source_stage": "A7FF-CORE16J",
  "stage": "A7FF-CORE16K",
  "strict_h2_count": 9
}
```

## Repair Policy

| policy_id             | scope                  | action                                                                               | target                                                              |
|:----------------------|:-----------------------|:-------------------------------------------------------------------------------------|:--------------------------------------------------------------------|
| h2_delta_repair       | H2_I4_near_miss_repair | run H2-only asymmetric transform variants around excluded near-miss rows             | at least 3 additional strict H2 candidates with control_ratio < 1.0 |
| no_nearmiss_promotion | H2 near-miss           | near-miss rows remain excluded unless rerun as strict rows under repaired transforms | no forensic row enters CORE17 queue directly                        |
| queue_fill            | balanced strict queue  | replace excluded near-miss rows with strict H2 rows only                             | strict queue size 96 and H2 strict count >= 12                      |

## Execution Contract

```json
{
  "allowed_scope": [
    "H2_I4_near_miss_repair only",
    "taker_flow x OI/liquidity typed probes",
    "control_ratio < 1.0 strict promotion only"
  ],
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "forbidden": [
    "near-miss direct promotion",
    "open grammar FormulaGen",
    "bounded replay",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "name": "H2/I4 strict-floor repair execution",
  "stage": "A7FF-CORE16KE",
  "target": {
    "additional_h2_strict_candidates": 3,
    "strict_h2_count": 12,
    "strict_queue_size": 96
  }
}
```
