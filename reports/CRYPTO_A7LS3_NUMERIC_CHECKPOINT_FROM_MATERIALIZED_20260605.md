# CRYPTO A7LS-3 NUMERIC CHECKPOINT FROM MATERIALIZED

Generated: 2026-06-05T05:10:49Z

## Decision

`HOLD_A7LS3_NUMERIC_CHECKPOINT_WEAK`

A7LS-3 builds a memory-safe numeric checkpoint queue from A7LS-2 activity-ok materialized candidates and runs the existing numeric probe.

## Manifest

```json
{
  "authorizes_a7ls4_checkpoint_triage": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "numeric_probe_returncode_nonzero",
    "numeric_probe_timeout",
    "numeric_materialization_activity_below_70pct",
    "non_l7_numeric_clues_lt_4",
    "selected_portfolio_queue_lt_4"
  ],
  "decision": "HOLD_A7LS3_NUMERIC_CHECKPOINT_WEAK",
  "executes_numeric_probe": true,
  "executes_search": false,
  "generated_at": "2026-06-05T05:10:49Z",
  "input_materialized_rows": 2000,
  "label_response_rows": 0,
  "materialized_activity_ok_count": 0,
  "non_l7_numeric_clue_rows": 0,
  "numeric_checkpoint_queue_rows": 128,
  "numeric_decision": "HOLD_A7LS3_NUMERIC_PROBE_TIMEOUT_OR_NO_MANIFEST",
  "numeric_returncode": -9,
  "rank_label_diagnostic_clue_rows": 0,
  "selected_portfolio_queue_count": 0,
  "source_decision": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
  "source_stage": "A7LS-2",
  "stage": "A7LS-3"
}
```

## Queue Summary

| a7ls_arm   | semantic_pair                     |   rows |
|:-----------|:----------------------------------|-------:|
| A7LS_A     | basis_premium_like                |     32 |
| A7LS_B     | liquidity_like                    |     12 |
| A7LS_B     | price_like                        |     10 |
| A7LS_B     | taker_flow_like                   |     10 |
| A7LS_C     | basis_premium_like                |     48 |
| A7LS_D     | basis_premium_like                |      3 |
| A7LS_D     | liquidity_like                    |      4 |
| A7LS_D     | low_prior_axes                    |      1 |
| A7LS_D     | low_prior_axes|basis_premium_like |      8 |

## Response Summary

`<empty>`

## Selected Summary

`<empty>`

## Numeric Materialization Summary

`<empty>`
