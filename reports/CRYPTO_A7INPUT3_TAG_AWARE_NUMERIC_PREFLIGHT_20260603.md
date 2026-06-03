# CRYPTO A7INPUT-3 TAG-AWARE NUMERIC PREFLIGHT

Generated: 2026-06-03T06:12:11Z

## Decision

`PASS_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT_READY_FOR_CORE54E`

A7INPUT-3 runs the existing numeric probe over a substantial tag-aware queue sample. This is execution progress, not another approval-only contract. It still does not run full replay, formula search, alpha proof, shadow, paper, or live.

Large detailed response/control/non-overlap CSVs are stored outside git:

```text
G:/AlphaFactory_CryptoData/research_runtime/a7input3_tag_aware_numeric_preflight_20260603
```

The repo keeps compact summaries, manifests, the sampled queue, selected queue, materialization metrics, and the executable script.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core54e_tag_aware_numeric_execution": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_rows": 351120,
  "decision": "PASS_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT_READY_FOR_CORE54E",
  "eval_failure_count": 0,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-03T06:12:11Z",
  "input_queue_rows": 1216,
  "interaction_rows": 512,
  "label_response_rows": 16720,
  "materialized_activity_ok_count": 836,
  "non_l7_numeric_clue_rows": 272,
  "numeric_probe_decision": "PASS_A7INPUT3_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "ordinary_rows": 512,
  "portfolio_queue_count": 298,
  "process_exit_code": 0,
  "rank_label_diagnostic_clue_rows": 489,
  "rescue_rows": 192,
  "selected_portfolio_queue_count": 23,
  "source_decision": "PASS_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_READY_FOR_CORE54",
  "source_stage": "A7INPUT-2",
  "stage": "A7INPUT-3",
  "started_at": "2026-06-03T04:42:06Z",
  "timed_out": false,
  "timeout_seconds": 7200,
  "uses_may": false
}
```

## Materialization By Queue

| a7input_queue     |   rows |   eval_success |   activity_ok |   median_finite_share |   median_nonzero_share |
|:------------------|-------:|---------------:|--------------:|----------------------:|-----------------------:|
| interaction_alpha |    512 |            512 |           412 |             0.827061  |               0.982423 |
| ordinary_alpha    |    512 |            512 |           424 |             0.971319  |               0.98817  |
| rescue_lane       |    192 |            192 |             0 |             0.0030852 |               0.994655 |

## Decision By Queue

| a7input_queue     | decision                            | label_family                       |   row_count |
|:------------------|:------------------------------------|:-----------------------------------|------------:|
| ordinary_alpha    | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |        1256 |
| ordinary_alpha    | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |        1234 |
| ordinary_alpha    | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |        1234 |
| ordinary_alpha    | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |        1224 |
| interaction_alpha | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |        1222 |
| interaction_alpha | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |        1222 |
| interaction_alpha | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |        1197 |
| interaction_alpha | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |        1184 |
| ordinary_alpha    | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         717 |
| interaction_alpha | HOLD_A7INPUT3_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         653 |
| ordinary_alpha    | HOLD_A7INPUT3_CONTROL_DOMINATED     | L7_ranked_future_return            |         653 |
| interaction_alpha | HOLD_A7INPUT3_CONTROL_DOMINATED     | L7_ranked_future_return            |         638 |
| ordinary_alpha    | HOLD_A7INPUT3_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         393 |
| ordinary_alpha    | HOLD_A7INPUT3_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         393 |
| ordinary_alpha    | HOLD_A7INPUT3_CONTROL_DOMINATED     | L0_raw_forward_return              |         391 |
| interaction_alpha | HOLD_A7INPUT3_CONTROL_DOMINATED     | L5_vol_adjusted_return             |         389 |
| interaction_alpha | HOLD_A7INPUT3_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         386 |
| interaction_alpha | HOLD_A7INPUT3_CONTROL_DOMINATED     | L0_raw_forward_return              |         374 |
| interaction_alpha | HOLD_A7INPUT3_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         372 |
| ordinary_alpha    | HOLD_A7INPUT3_CONTROL_DOMINATED     | L5_vol_adjusted_return             |         340 |
| interaction_alpha | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |         273 |
| ordinary_alpha    | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |         216 |
| ordinary_alpha    | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |         109 |
| interaction_alpha | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |          83 |
| ordinary_alpha    | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |          60 |
| ordinary_alpha    | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |          45 |
| interaction_alpha | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |          40 |
| ordinary_alpha    | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          40 |
| interaction_alpha | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          38 |
| ordinary_alpha    | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |          36 |
| ordinary_alpha    | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |          36 |
| interaction_alpha | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          35 |
| ordinary_alpha    | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |          33 |
| interaction_alpha | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          33 |
| ordinary_alpha    | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          32 |
| interaction_alpha | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |          31 |
| ordinary_alpha    | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          30 |
| interaction_alpha | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |          21 |
| interaction_alpha | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |          18 |
| interaction_alpha | HOLD_A7INPUT3_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |          18 |
| interaction_alpha | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |           6 |
| ordinary_alpha    | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L3_liquidity_tier_relative_return  |           4 |
| interaction_alpha | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L0_raw_forward_return              |           3 |
| interaction_alpha | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L1_cross_sectional_relative_return |           3 |
| ordinary_alpha    | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L0_raw_forward_return              |           2 |
| interaction_alpha | HOLD_A7INPUT3_NONOVERLAP_WEAK       | L7_ranked_future_return            |           1 |
| ordinary_alpha    | HOLD_A7INPUT3_NONOVERLAP_WEAK       | L7_ranked_future_return            |           1 |
| ordinary_alpha    | HOLD_A7INPUT3_COST2_PROXY_FRAGILE   | L1_cross_sectional_relative_return |           1 |

## Semantic Response Summary

| a7input_queue     | semantic_pair                         | decision                            | label_family                       |   row_count |
|:------------------|:--------------------------------------|:------------------------------------|:-----------------------------------|------------:|
| interaction_alpha | basis_premium_like|price_like         | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |         140 |
| ordinary_alpha    | basis_premium_like|price_like         | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |         104 |
| interaction_alpha | basis_premium_like|volatility_like    | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          65 |
| interaction_alpha | price_like|volatility_like            | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          40 |
| ordinary_alpha    | price_like|volatility_like            | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          39 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          34 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          27 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          23 |
| interaction_alpha | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          18 |
| interaction_alpha | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          17 |
| interaction_alpha | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          17 |
| interaction_alpha | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          14 |
| interaction_alpha | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |          14 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          13 |
| interaction_alpha | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          13 |
| ordinary_alpha    | basis_premium_like                    | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          12 |
| ordinary_alpha    | basis_premium_like                    | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |          11 |
| ordinary_alpha    | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |          11 |
| ordinary_alpha    | basis_premium_like                    | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          11 |
| interaction_alpha | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          11 |
| interaction_alpha | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |          11 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           9 |
| ordinary_alpha    | volatility_like|volatility_like       | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           9 |
| ordinary_alpha    | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           8 |
| ordinary_alpha    | basis_premium_like                    | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |           8 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           7 |
| ordinary_alpha    | basis_premium_like                    | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           7 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           7 |
| ordinary_alpha    | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           7 |
| ordinary_alpha    | basis_premium_like|price_like         | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           6 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           6 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |           6 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           5 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           5 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           4 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           4 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           4 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |           3 |
| ordinary_alpha    | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |           2 |
| ordinary_alpha    | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           2 |
| interaction_alpha | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L5_vol_adjusted_return             |           1 |
| interaction_alpha | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           1 |
| interaction_alpha | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           1 |
| interaction_alpha | volatility_like|volatility_like       | A7INPUT3_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           1 |
| interaction_alpha | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           1 |
| ordinary_alpha    | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L0_raw_forward_return              |           1 |
| ordinary_alpha    | price_like|volatility_like            | A7INPUT3_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           1 |

## Selected Summary

| a7input_queue     | semantic_pair                         | label_family            |   row_count |
|:------------------|:--------------------------------------|:------------------------|------------:|
| interaction_alpha | basis_premium_like|volatility_like    | L7_ranked_future_return |           4 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | L5_vol_adjusted_return  |           4 |
| interaction_alpha | basis_premium_like|price_like         | L7_ranked_future_return |           2 |
| ordinary_alpha    | basis_premium_like|volatility_like    | L7_ranked_future_return |           2 |
| interaction_alpha | basis_premium_like|volatility_like    | L5_vol_adjusted_return  |           2 |
| ordinary_alpha    | basis_premium_like|volatility_like    | L5_vol_adjusted_return  |           2 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | L7_ranked_future_return |           2 |
| ordinary_alpha    | volatility_like|volatility_like       | L7_ranked_future_return |           2 |
| interaction_alpha | basis_premium_like|price_like         | L5_vol_adjusted_return  |           1 |
| ordinary_alpha    | basis_premium_like                    | L5_vol_adjusted_return  |           1 |
| interaction_alpha | price_like|volatility_like            | L7_ranked_future_return |           1 |

## Boundary

```text
numeric probe executed: true
replay executed: false
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
