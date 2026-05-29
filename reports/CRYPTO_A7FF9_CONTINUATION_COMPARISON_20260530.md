# CRYPTO A7FF-9 CONTINUATION COMPARISON

Generated: 2026-05-29T18:24:18Z

## Decision

`PASS_A7FF9_CONTINUATION_COMPARISON_BUILT`

A7FF-9 expands the A7FF-8 numeric probe from 64 to 96 auditable blueprints. A 128-blueprint attempt exceeded the local 30 minute execution window and produced no manifest, so it is recorded as a compute-cost fact rather than evidence.

## Summary

| stage     | decision                                            |   input_blueprint_count |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count |   non_l7_clues_per_blueprint |   rank_clues_per_blueprint | uses_may   | authorizes_search   |
|:----------|:----------------------------------------------------|------------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|-----------------------------:|---------------------------:|:-----------|:--------------------|
| A7FF-8_64 | PASS_A7FF8_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      64 |                               64 |                  1280 |                         65 |                                12 |                      14 |                                6 |                       1.0156 |                     0.1875 | False      | False               |
| A7FF-9_96 | PASS_A7FF9_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                      96 |                               96 |                  1920 |                         87 |                                14 |                      21 |                                8 |                       0.9062 |                     0.1458 | False      | False               |

## Family Clue Comparison

| stage     | semantic_pair                        | decision_kind              |   count |
|:----------|:-------------------------------------|:---------------------------|--------:|
| A7FF-8_64 | basis_premium_like                   | NUMERIC_CLUE               |      27 |
| A7FF-8_64 | basis_premium_like                   | RANK_LABEL_DIAGNOSTIC_CLUE |       6 |
| A7FF-8_64 | basis_premium_like\|positioning_like | NUMERIC_CLUE               |      38 |
| A7FF-8_64 | basis_premium_like\|positioning_like | RANK_LABEL_DIAGNOSTIC_CLUE |       6 |
| A7FF-9_96 | basis_premium_like                   | NUMERIC_CLUE               |      27 |
| A7FF-9_96 | basis_premium_like                   | RANK_LABEL_DIAGNOSTIC_CLUE |       6 |
| A7FF-9_96 | basis_premium_like\|positioning_like | NUMERIC_CLUE               |      60 |
| A7FF-9_96 | basis_premium_like\|positioning_like | RANK_LABEL_DIAGNOSTIC_CLUE |       8 |

## Timeout Note

```json
{
  "action": "reran as 96-blueprint continuation to produce complete auditable artifacts",
  "attempted_blueprints": 128,
  "attempted_stage": "A7FF-9_128",
  "result": "timeout_no_manifest",
  "timeout_seconds": 1800
}
```

## Boundary

```text
A7FF-9 is numeric-probe continuation only.
It does not execute generation, replay, search, alpha proof, shadow, paper, or live trading.
May is not used in scoring or authorization.
```
