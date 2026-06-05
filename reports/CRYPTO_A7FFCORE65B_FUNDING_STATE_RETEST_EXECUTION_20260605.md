# CRYPTO A7FF-CORE65B FUNDING STATE RETEST EXECUTION

Generated: 2026-06-05T01:42:32Z

## Decision

`HOLD_CORE65B_FUNDING_STATE_REPAIR_STILL_WEAK`

CORE65B rewrites raw `funding_rate` formulas to PIT dense `funding_rate_state_last_ffill_8h` formulas and executes a bounded numeric retest. It does not run formula search, replay promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "funding_state_non_l7_clues_lt_4",
    "funding_state_selected_queue_lt_4"
  ],
  "decision": "HOLD_CORE65B_FUNDING_STATE_REPAIR_STILL_WEAK",
  "executed_queue_rows": 128,
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "full_patched_queue_rows": 373,
  "generated_at": "2026-06-05T01:42:32Z",
  "label_response_rows": 1920,
  "materialized_activity_ok_count": 96,
  "non_l7_numeric_clue_rows": 2,
  "numeric_decision": "HOLD_A7FFCORE65B_PORTFOLIO_QUEUE_TOO_SMALL",
  "numeric_returncode": 0,
  "rank_label_diagnostic_clue_rows": 0,
  "selected_portfolio_queue_count": 1,
  "stage": "A7FF-CORE65B"
}
```

## Materialization Summary

| semantic_pair                         |   rows |   eval_success |   activity_ok |   median_finite_share |   median_nonzero_share |
|:--------------------------------------|-------:|---------------:|--------------:|----------------------:|-----------------------:|
| basis_premium_like|funding_state_like |    115 |            115 |            86 |              0.824847 |               0.999479 |
| funding_state_like|positioning_like   |     13 |             13 |            10 |              0.824847 |               0.653197 |

## Response Summary

| semantic_pair                         | decision                           | label_family                       |   rows |
|:--------------------------------------|:-----------------------------------|:-----------------------------------|-------:|
| basis_premium_like|funding_state_like | A7FFCORE65B_NUMERIC_CLUE           | L0_raw_forward_return              |      1 |
| basis_premium_like|funding_state_like | A7FFCORE65B_NUMERIC_CLUE           | L1_cross_sectional_relative_return |      1 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L0_raw_forward_return              |     23 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L1_cross_sectional_relative_return |     23 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L3_liquidity_tier_relative_return  |     26 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L5_vol_adjusted_return             |     51 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L7_ranked_future_return            |     52 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L0_raw_forward_return              |    320 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L1_cross_sectional_relative_return |    320 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L3_liquidity_tier_relative_return  |    318 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L5_vol_adjusted_return             |    293 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L7_ranked_future_return            |    292 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L0_raw_forward_return              |      3 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L1_cross_sectional_relative_return |      3 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L3_liquidity_tier_relative_return  |      3 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L5_vol_adjusted_return             |      6 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED | L7_ranked_future_return            |     11 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L0_raw_forward_return              |     37 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L1_cross_sectional_relative_return |     37 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L3_liquidity_tier_relative_return  |     37 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L5_vol_adjusted_return             |     34 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L7_ranked_future_return            |     29 |

## Selected Summary

| semantic_pair                         | label_family          |   rows |
|:--------------------------------------|:----------------------|-------:|
| basis_premium_like|funding_state_like | L0_raw_forward_return |      1 |
