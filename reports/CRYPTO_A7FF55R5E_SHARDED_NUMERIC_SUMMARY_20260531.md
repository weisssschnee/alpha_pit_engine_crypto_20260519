# CRYPTO A7FF-55R5E SHARDED NUMERIC SUMMARY

Generated: 2026-05-31T16:15:44Z

## Decision

`HOLD_A7FF55R5E_SHARDED_NUMERIC_WEAK_RESPONSE`

A7FF-55R5E summarizes the completed repaired-atlas numeric shards. It is numeric-only and does not execute replay or search. The detailed shard runtime directories were compacted into `runtime/a7ff55r5e_sharded_numeric_summary/a7ff55r5e_label_response_compact.csv` and intentionally not retained as standalone versioned artifacts.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "non_l7_clue_rows_below_12",
    "selected_queue_rows_below_8",
    "selected_semantic_pair_count_below_3"
  ],
  "decision": "HOLD_A7FF55R5E_SHARDED_NUMERIC_WEAK_RESPONSE",
  "executes_numeric": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T16:15:44Z",
  "label_response_rows": 4200,
  "next_allowed": "A7FF-55R6 numeric response forensic / atlas repair",
  "non_l7_numeric_clue_rows": 4,
  "sampled_input_blueprints": 350,
  "selected_motif_count": 2,
  "selected_portfolio_queue_count": 2,
  "selected_semantic_pair_count": 2,
  "shard_count": 5,
  "stage": "A7FF-55R5E",
  "uses_may": false
}
```

## Shard Summary

| source_shard   | decision                                 |   input_blueprint_count |   label_response_rows |   materialized_activity_ok_count |   non_l7_numeric_clue_rows |   selected_portfolio_queue_count |   queue_offset |   queue_limit |
|:---------------|:-----------------------------------------|------------------------:|----------------------:|---------------------------------:|---------------------------:|---------------------------------:|---------------:|--------------:|
| S00            | HOLD_A7FF55R5E_NO_NON_L7_NUMERIC_CLUES   |                     100 |                  1200 |                              100 |                          0 |                                0 |             -1 |           100 |
| S01            | HOLD_A7FF55R5E_NO_NON_L7_NUMERIC_CLUES   |                     100 |                  1200 |                              100 |                          0 |                                0 |            100 |           100 |
| S12            | HOLD_A7FF55R5E_NO_NON_L7_NUMERIC_CLUES   |                      50 |                   600 |                               50 |                          0 |                                0 |            600 |            50 |
| S24            | HOLD_A7FF55R5E_PORTFOLIO_QUEUE_TOO_SMALL |                      50 |                   600 |                               50 |                          1 |                                1 |           1200 |            50 |
| S36            | HOLD_A7FF55R5E_PORTFOLIO_QUEUE_TOO_SMALL |                      50 |                   600 |                               50 |                          3 |                                1 |           1800 |            50 |

## Clue Family Summary

| semantic_pair                        | motif          | label_family                       |   clue_rows |
|:-------------------------------------|:---------------|:-----------------------------------|------------:|
| open_interest_like\|positioning_like | safe_div_abs   | L1_cross_sectional_relative_return |           1 |
| taker_flow_like\|open_interest_like  | relative_shock | L0_raw_forward_return              |           1 |
| taker_flow_like\|open_interest_like  | relative_shock | L1_cross_sectional_relative_return |           1 |
| taker_flow_like\|open_interest_like  | relative_shock | L3_liquidity_tier_relative_return  |           1 |

## Selected Family Summary

| semantic_pair                        | motif          | label_family                       |   selected_rows |
|:-------------------------------------|:---------------|:-----------------------------------|----------------:|
| open_interest_like\|positioning_like | safe_div_abs   | L1_cross_sectional_relative_return |               1 |
| taker_flow_like\|open_interest_like  | relative_shock | L0_raw_forward_return              |               1 |

## Boundary

```text
numeric execution: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
