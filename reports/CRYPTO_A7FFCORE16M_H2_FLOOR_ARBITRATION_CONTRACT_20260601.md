# CRYPTO A7FF-CORE16M H2 FLOOR ARBITRATION CONTRACT

Generated: 2026-06-01T14:00:34Z

## Decision

`PASS_A7FFCORE16M_H2_FLOOR_RETAINED_READY_FOR_CORE16ME`

CORE16M is a contract and arbitration record. It does not execute replay, search, formula generation, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16l": false,
  "authorizes_core16me": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16M_H2_FLOOR_RETAINED_READY_FOR_CORE16ME",
  "executes_replay": false,
  "executes_search": false,
  "floor_policy": "retain_h2_floor_no_nearmiss_promotion",
  "generated_at": "2026-06-01T14:00:34Z",
  "h2_rows_needed": 1,
  "next_allowed": "A7FF-CORE16ME broader checkpointed H2/I4 strict-floor repair execution",
  "queue_rows_needed": 1,
  "source_decision": "PASS_A7FFCORE16KR_H2_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE16M",
  "source_stage": "A7FF-CORE16KR",
  "stage": "A7FF-CORE16M"
}
```

## Floor Policy

| policy_id                    | decision           | reason                                                                                                                |
|:-----------------------------|:-------------------|:----------------------------------------------------------------------------------------------------------------------|
| P0_retain_h2_floor           | retain             | H2/I4 under-supply was the explicit blocker; waiving the floor would make the balanced queue governance meaningless   |
| P1_no_nearmiss_promotion     | retain             | near-miss rows remain forensic evidence only; they cannot be used as strict alpha seeds                               |
| P2_authorize_broader_h2_wave | authorize_core16me | CORE16KE found 2 of 3 required strict rows; the remaining gap is localized and worth one broader checkpointed H2 wave |

## CORE16ME Operator Policy

| family                 | left_families   | right_families          | operators       | left_transforms                                                                           | right_transforms                                                                                |   required_added_strict_h2 |
|:-----------------------|:----------------|:------------------------|:----------------|:------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|---------------------------:|
| H2_I4_near_miss_repair | taker_flow      | liquidity|open_interest | Mul|SafeDiv|Sub | delta_1h|delta_2h|delta_4h|delta_8h|delta_24h|zscore_72h|zscore_168h|shock_24h|tsrank_72h | level|delta_1h|delta_2h|delta_4h|delta_8h|delta_24h|zscore_72h|zscore_168h|shock_24h|tsrank_72h |                          1 |

## Blocked

| blocked_task                        | reason                                                       |
|:------------------------------------|:-------------------------------------------------------------|
| A7FF-CORE16L                        | strict pre-seed queue still below size/H2 floor              |
| A7FF-CORE17                         | objective seed policy blocked until strict queue lock passes |
| formula generation/search           | CORE16M authorizes H2 repair execution only                  |
| alpha proof / shadow / paper / live | not authorized                                               |
