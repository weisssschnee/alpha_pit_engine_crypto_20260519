# CRYPTO A7FF-CORE27X SEARCH READINESS ARBITRATION

Generated: 2026-06-01T18:20:37Z

## Decision

`HOLD_A7FFCORE27X_SEARCH_NOT_READY_SINGLE_LANE_SUPPLY`

CORE27X arbitrates whether the current A7FF chain is ready for bounded replay or larger search. It is not ready: clean evidence is single-lane S0 only, and non-S0 repair produced no strict clean candidates.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core27_replay_contract": false,
  "authorizes_core28_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE27X_SEARCH_NOT_READY_SINGLE_LANE_SUPPLY",
  "dominant_failure": "single_lane_s0_clue_without_independent_executable_lane",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:20:37Z",
  "next_allowed": "A7FF-CORE28 objective/data-family reset contract",
  "non_s0_clean_count": 0,
  "non_s0_near_miss_count": 9,
  "s0_clean_count": 4,
  "s0_clean_lane_count": 1,
  "source_decision": "PASS_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE27X",
  "source_stage": "A7FF-CORE26DER",
  "stage": "A7FF-CORE27X"
}
```

## Readiness Verdict

| axis                     | evidence                                      | verdict                                                  |
|:-------------------------|:----------------------------------------------|:---------------------------------------------------------|
| S0 local clue            | 4 clean candidates / 1 lane                   | diagnostic clue only; cannot support replay/search alone |
| non-S0 independent lane  | 0 clean, 9 near-miss                          | no strict independent lane                               |
| bounded replay readiness | requires multi-lane strict clean supply       | not ready                                                |
| large search readiness   | single-lane S0 clue and non-S0 repair failure | not authorized                                           |

## Authorization Matrix

| task                                             | reason                                                                        | authorized   |
|:-------------------------------------------------|:------------------------------------------------------------------------------|:-------------|
| A7FF-CORE28 objective/data-family reset contract | current S0/S1/S3 field set cannot produce independent executable lane breadth | True         |
| A7FF-CORE27 bounded replay contract              | blocked until multi-lane strict clean supply exists                           | False        |
| large search / formula search                    | blocked; would amplify a single-lane clue                                     | False        |
