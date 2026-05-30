# CRYPTO A7FF-28A BOUNDED DEEP REPLAY SUMMARY

Generated: 2026-05-30T09:58:28Z

## Decision

`PASS_A7FF28A_BOUNDED_DEEP_REPLAY_READY_FOR_A7FF29_FORENSIC_NO_SEARCH_AUTH`

A7FF-28A reran the frozen A7FF-28 queue on 181 strict full-history symbols. This summary strips ranked-label diagnostic rows from the next queue and authorizes only A7FF-29 candidate forensic contract work.

## Summary

```json
{
  "a7ff29_max_control_ratio": 0.7212882306454783,
  "a7ff29_queue_count": 6,
  "a7ff29_semantic_pair_count": 3,
  "authorizes_a7ff29_candidate_forensic_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF28A_BOUNDED_DEEP_REPLAY_READY_FOR_A7FF29_FORENSIC_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:58:28Z",
  "input_blueprint_count": 8,
  "label_response_rows": 160,
  "materialized_activity_ok_count": 8,
  "non_l7_numeric_clue_rows": 30,
  "prior_decision": "PASS_A7FF28A_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH",
  "rank_label_diagnostic_clue_rows": 10,
  "selected_rank_label_diagnostic_count": 2,
  "stage": "A7FF-28A-SUMMARY",
  "warnings": [
    "selected_portfolio_queue_contains_rank_label_diagnostic_rows_excluded_from_a7ff29"
  ]
}
```

## A7FF-29 Candidate Forensic Queue

|   a7ff29_queue_rank | blueprint_id             | expression                                                            | semantic_pair                         | motif        | label_family                       |   label_horizon_h |   control_ratio_premay_max |   score_no_may |
|--------------------:|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:-----------------------------------|------------------:|---------------------------:|---------------:|
|                   1 | a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | L5_vol_adjusted_return             |                 1 |                   0.237812 |      271.633   |
|                   2 | a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return             |                 1 |                   0.272877 |      271.61    |
|                   3 | a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | L3_liquidity_tier_relative_return  |                 1 |                   0.150867 |      143.554   |
|                   4 | a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return             |                 8 |                   0.612048 |      131.724   |
|                   5 | a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return             |                 1 |                   0.721288 |       80.8668  |
|                   6 | a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | L1_cross_sectional_relative_return |                 1 |                   0.226391 |        6.77361 |

## Excluded Ranked-Label Diagnostic Selected Rows

| blueprint_id             | expression                                                  | label_family            |   label_horizon_h |   score_no_may |
|:-------------------------|:------------------------------------------------------------|:------------------------|------------------:|---------------:|
| a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)        | L7_ranked_future_return |                 8 |        40.0855 |
| a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps) | L7_ranked_future_return |                 1 |        20.3265 |

## Decision Counts

| decision                           | label_family                       |   count |
|:-----------------------------------|:-----------------------------------|--------:|
| A7FF28A_NUMERIC_CLUE               | L0_raw_forward_return              |       6 |
| A7FF28A_NUMERIC_CLUE               | L1_cross_sectional_relative_return |       7 |
| A7FF28A_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |       8 |
| A7FF28A_NUMERIC_CLUE               | L5_vol_adjusted_return             |       9 |
| A7FF28A_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |      10 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L0_raw_forward_return              |      10 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |       9 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |       8 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L5_vol_adjusted_return             |       5 |
| HOLD_A7FF28A_CONTROL_DOMINATED     | L7_ranked_future_return            |       5 |
| HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |       3 |
| HOLD_A7FF28A_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |       9 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |      16 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |      15 |
| HOLD_A7FF28A_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |       8 |

## Materialization

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          | eval_success   |   finite_share |   nonzero_share | activity_ok   |         min_value |   max_value |     std_value |   error |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|:---------------|---------------:|----------------:|:--------------|------------------:|------------:|--------------:|--------:|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 | True           |       0.996265 |        0.998968 | True          |   -2243.85        |   2074.51   |    17.4842    |     nan |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f | True           |       0.823901 |        0.998919 | True          |   -2243.85        |   2074.51   |    17.5848    |     nan |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 | True           |       0.826199 |        0.99991  | True          |     -12.4461      |     11.3025 |     0.0885254 |     nan |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f | True           |       0.996553 |        0.999317 | True          |   -2054.65        |    401.832  |    12.3716    |     nan |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 | True           |       0.996553 |        0.989336 | True          |      -4.29472e+06 | 696592      |  9160.97      |     nan |
| a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | sub          | skel_0994b3a36a4d53ba | True           |       0.997415 |        0.998463 | True          |    -226.494       |   2215.09   |    15.4454    |     nan |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 | True           |       0.827348 |        0.675194 | True          | -444452           |  32159.1    | 10514.7       |     nan |
| a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps)           | basis_premium_like|basis_premium_like | sub          | skel_97ea9710bb50e137 | True           |       0.997702 |        1        | True          |    -133.259       |   2149.05   |    13.2183    |     nan |

## Family Summary

| semantic_pair                         | motif        | label_family                       |   candidate_count |   median_control_ratio |   median_score_no_may |
|:--------------------------------------|:-------------|:-----------------------------------|------------------:|-----------------------:|----------------------:|
| basis_premium_like                    | single       | L5_vol_adjusted_return             |                 1 |               0.237812 |             271.633   |
| basis_premium_like|basis_premium_like | safe_div_abs | L1_cross_sectional_relative_return |                 1 |               0.226391 |               6.77361 |
| basis_premium_like|basis_premium_like | sub          | L3_liquidity_tier_relative_return  |                 1 |               0.150867 |             143.554   |
| basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return             |                 1 |               0.272877 |             271.61    |
| basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return             |                 1 |               0.721288 |              80.8668  |
| basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return             |                 1 |               0.612048 |             131.724   |

## Boundary

```text
A7FF-28A does not authorize formula generation, large search, alpha proof, shadow, paper, or live execution.
A7FF-29 may only do candidate forensic/deep-audit contract work on the non-L7 queue.
```
