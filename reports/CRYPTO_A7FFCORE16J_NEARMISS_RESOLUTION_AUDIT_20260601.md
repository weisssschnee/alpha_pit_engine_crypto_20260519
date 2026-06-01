# CRYPTO A7FF-CORE16J NEAR-MISS RESOLUTION AUDIT

Generated: 2026-06-01T12:43:59Z

## Decision

`HOLD_A7FFCORE16J_STRICT_QUEUE_H2_FLOOR_INSUFFICIENT`

CORE16J resolves the near-miss rows from CORE16I. Near-miss rows remain excluded from alpha seed eligibility. This stage does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16k": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "strict_queue_size_lt_96",
    "strict_h2_floor_lt_12"
  ],
  "decision": "HOLD_A7FFCORE16J_STRICT_QUEUE_H2_FLOOR_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T12:43:59Z",
  "near_miss_excluded_count": 3,
  "next_allowed": "A7FF-CORE16K H2/I4 strict-floor repair",
  "source_decision": "PASS_A7FFCORE16I_BALANCED_PRESEED_QUEUE_READY_FOR_NEARMISS_RESOLUTION",
  "source_stage": "A7FF-CORE16I",
  "stage": "A7FF-CORE16J",
  "strict_h2_count": 9,
  "strict_queue_size": 93
}
```

## Strict Queue Summary

| metric                  |     value |
|:------------------------|----------:|
| queue_size              | 96        |
| strict_size             | 93        |
| near_miss_size          |  3        |
| strict_family_count     |  4        |
| strict_h2_count         |  9        |
| strict_top_family_share |  0.354839 |
| strict_non_l5_share     |  0.892473 |
| strict_operator_count   |  3        |

## Near-Miss Resolution

| resolution              |   rows | reason                                                                                            |
|:------------------------|-------:|:--------------------------------------------------------------------------------------------------|
| exclude_from_alpha_seed |      3 | near-miss rows have control_ratio >= 1.0 and cannot be promoted without a dedicated strict repair |

## Next Contract

```json
{
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "forbidden": [
    "promoting near-miss as alpha seed",
    "open grammar FormulaGen",
    "bounded replay",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "name": "H2/I4 strict-floor repair",
  "stage": "A7FF-CORE16K",
  "target": {
    "near_miss_promotions_allowed": false,
    "strict_h2_candidate_count": 12,
    "strict_queue_size": 96
  }
}
```
