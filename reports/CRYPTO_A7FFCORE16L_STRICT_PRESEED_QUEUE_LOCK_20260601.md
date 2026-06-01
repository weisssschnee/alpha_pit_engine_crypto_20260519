# CRYPTO A7FF-CORE16L STRICT PRESEED QUEUE LOCK

Generated: 2026-06-01T14:34:40Z

## Decision

`PASS_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCKED_READY_FOR_CORE17_CONTRACT`

CORE16L locks the strict pre-seed queue for contract drafting only. It does not execute replay, search, formula generation, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core17_contract": true,
  "authorizes_core17_execution": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCKED_READY_FOR_CORE17_CONTRACT",
  "duplicate_keys": 0,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 4,
  "generated_at": "2026-06-01T14:34:40Z",
  "h2_count": 12,
  "h3_count": 20,
  "locked_queue_size": 96,
  "near_miss_count": 0,
  "next_allowed": "A7FF-CORE17 objective seed policy contract",
  "non_l5_share": 0.8958333333333334,
  "operator_count": 3,
  "source_decision": "PASS_A7FFCORE16ME_H2_FLOOR_REPAIRED_READY_FOR_CORE16L",
  "source_stage": "A7FF-CORE16ME",
  "stage": "A7FF-CORE16L",
  "strict_count": 96,
  "top_family_share": 0.34375
}
```

## Gate Audit

| gate             |     value | threshold    | pass   |
|:-----------------|----------:|:-------------|:-------|
| queue_size       | 96        | >=96         | True   |
| strict_count     | 96        | ==queue_size | True   |
| near_miss_count  |  0        | 0            | True   |
| family_count     |  4        | >=4          | True   |
| top_family_share |  0.34375  | <=0.45       | True   |
| h2_count         | 12        | >=12         | True   |
| h3_count         | 20        | >=12         | True   |
| non_l5_share     |  0.895833 | >=0.40       | True   |
| operator_count   |  3        | >=2          | True   |
| duplicate_keys   |  0        | 0            | True   |

## Family Summary

| second_pass_family     | queue_role       |   rows |   label_family_count |   horizon_count |   operator_count |   lag_ok_count |   median_control_ratio |
|:-----------------------|:-----------------|-------:|---------------------:|----------------:|-----------------:|---------------:|-----------------------:|
| H1_I5_deconcentration  | strict_candidate |     33 |                    3 |               2 |                2 |             33 |               0.71876  |
| H0_I3_deconcentration  | strict_candidate |     31 |                    3 |               1 |                2 |             31 |               0.555319 |
| H3_cross_family_bridge | strict_candidate |     20 |                    4 |               4 |                2 |             15 |               0.830484 |
| H2_I4_near_miss_repair | strict_candidate |     12 |                    4 |               3 |                2 |              5 |               0.741474 |
