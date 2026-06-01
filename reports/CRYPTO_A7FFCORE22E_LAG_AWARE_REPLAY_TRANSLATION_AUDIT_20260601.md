# CRYPTO A7FF-CORE22E LAG-AWARE REPLAY TRANSLATION AUDIT

Generated: 2026-06-01T15:22:38Z

## Decision

`HOLD_A7FFCORE22E_LAG_TRANSLATION_INSUFFICIENT`

CORE22E audits lag-aware translation from existing replay rows. It does not execute formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core23_contract": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_one_bar_clean_candidate_count": 4,
  "best_one_bar_clean_lane_count": 2,
  "best_same_bar_diagnostic_count": 55,
  "blockers": [
    "one_bar_clean_count_lt_6",
    "one_bar_clean_lane_count_lt_3",
    "same_bar_dominates_one_bar"
  ],
  "decision": "HOLD_A7FFCORE22E_LAG_TRANSLATION_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:22:38Z",
  "next_allowed": "A7FF-CORE22R lag translation forensic",
  "source_decision": "PASS_A7FFCORE22_LAG_AWARE_REPLAY_TRANSLATION_CONTRACT_READY_FOR_CORE22E",
  "source_stage": "A7FF-CORE22",
  "stage": "A7FF-CORE22E"
}
```

## Diagnosis

| finding                    |   value | interpretation                                    |
|:---------------------------|--------:|:--------------------------------------------------|
| one_bar_primary_supply     |       4 | best executable lag clean candidate count         |
| one_bar_primary_lanes      |       2 | best executable lag clean lane breadth            |
| same_bar_diagnostic_supply |      55 | same-bar diagnostic count; not promotion evidence |
| same_bar_minus_one_bar_gap |      51 | timing fragility proxy                            |

## Lag Translation Matrix

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
