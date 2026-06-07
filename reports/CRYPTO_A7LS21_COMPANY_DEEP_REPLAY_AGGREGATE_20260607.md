# CRYPTO A7LS-21 Company Deep Replay Aggregate (20260607)

## Decision

`PASS_A7LS21_COMPANY_DEEP_REPLAY_AGGREGATE_READY_FOR_A7LS22`

## Summary

- shards completed: 4 / 4
- pass shards: 2
- hold shards: 2
- input blueprints: 48
- materialized activity-ok: 48
- non-L7 numeric clue rows: 20
- L7 ranked-label diagnostic clue rows: 9
- aggregate selected portfolio queue: 13
- selected semantic pairs: 11
- selected skeletons: 12
- top semantic pair share: 0.15384615384615385

## Boundaries

- May was not used.
- This stage executed numeric deep replay only.
- It does not authorize formula search, alpha proof, shadow, paper, or live.

## Shards

| shard_id   | manifest_found   | decision                                                 | blockers                |   input_blueprint_count |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | uses_may   |
|:-----------|:-----------------|:---------------------------------------------------------|:------------------------|------------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:-----------|
| s000       | True             | HOLD_A7LS21s000_PORTFOLIO_QUEUE_TOO_SMALL                | portfolio_selected_lt_4 |                      12 |                               12 |                   240 |                          6 |                                 2 |                       3 |                                3 | False      |
| s001       | True             | PASS_A7LS21s001_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                      12 |                               12 |                   240 |                          3 |                                 1 |                       4 |                                4 | False      |
| s002       | True             | PASS_A7LS21s002_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                      12 |                               12 |                   240 |                         10 |                                 6 |                       6 |                                5 | False      |
| s003       | True             | HOLD_A7LS21s003_PORTFOLIO_QUEUE_TOO_SMALL                | portfolio_selected_lt_4 |                      12 |                               12 |                   240 |                          1 |                                 0 |                       1 |                                1 | False      |

## Next

- A7LS-22 clue attribution / promotion triage is authorized as a diagnostic stage.
- Search execution remains blocked.
