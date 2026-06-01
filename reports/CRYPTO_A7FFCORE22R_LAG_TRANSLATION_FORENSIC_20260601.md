# CRYPTO A7FF-CORE22R LAG TRANSLATION FORENSIC

Generated: 2026-06-01T15:24:03Z

## Decision

`PASS_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_COMPLETE_READY_FOR_CORE23`

CORE22R freezes the lag translation failure. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core23_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_one_bar_clean_candidate_count": 4,
  "best_one_bar_clean_lane_count": 2,
  "best_same_bar_diagnostic_count": 55,
  "decision": "PASS_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_COMPLETE_READY_FOR_CORE23",
  "dominant_failure": "same_bar_diagnostic_dominates_one_bar_executable",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:24:03Z",
  "next_allowed": "A7FF-CORE23 executable-horizon redesign contract",
  "source_decision": "HOLD_A7FFCORE22E_LAG_TRANSLATION_INSUFFICIENT",
  "source_stage": "A7FF-CORE22E",
  "stage": "A7FF-CORE22R"
}
```

## Diagnosis

| finding                           | evidence                                                                    | interpretation                                                       |
|:----------------------------------|:----------------------------------------------------------------------------|:---------------------------------------------------------------------|
| same_bar_diagnostic_excess        | same-bar diagnostic count 55 vs one-bar count 4                             | current packet has strong timing fragility                           |
| one_bar_lane_breadth_insufficient | one-bar lane count 2 < 3                                                    | executable evidence is not broad enough for search readiness         |
| large_search_not_justified        | failure occurs after governance/materialization/preflight and before search | expanding formula generation would amplify timing-fragile structures |

## Recommended Actions

| action_id             | action                                                     | reason                                                                            |
|:----------------------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------|
| R0_freeze_core22_path | freeze current locked-packet replay path as timing-fragile | same-bar diagnostic overwhelms one-bar executable supply                          |
| R1_core23_contract    | write CORE23 executable-horizon redesign contract          | next work must target lower-turnover/horizon/execution framing, not bigger search |
| R2_no_search          | continue blocking large search and formula expansion       | one-bar clean evidence is 4 candidates across 2 lanes                             |

## Lag Matrix

| lag_bucket             |   cost_bps |   clean_candidate_count |   clean_lane_count |   non_l5_share |
|:-----------------------|-----------:|------------------------:|-------------------:|---------------:|
| same_bar_diagnostic    |          2 |                      55 |                  4 |       0.854545 |
| one_bar_primary_costed |          2 |                       4 |                  2 |       0.75     |
| stale_proxy_uncosted   |          2 |                      80 |                  4 |       0.9      |
| same_bar_diagnostic    |          5 |                       9 |                  2 |       0.111111 |
| one_bar_primary_costed |          5 |                       4 |                  2 |       0.75     |
| stale_proxy_uncosted   |          5 |                      80 |                  4 |       0.9      |
| same_bar_diagnostic    |         10 |                       8 |                  2 |       0        |
| one_bar_primary_costed |         10 |                       1 |                  1 |       0        |
| stale_proxy_uncosted   |         10 |                      80 |                  4 |       0.9      |
| same_bar_diagnostic    |         20 |                       8 |                  2 |       0        |
| one_bar_primary_costed |         20 |                       1 |                  1 |       0        |
| stale_proxy_uncosted   |         20 |                      80 |                  4 |       0.9      |
