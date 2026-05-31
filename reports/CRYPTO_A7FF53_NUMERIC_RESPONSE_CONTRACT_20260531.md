# CRYPTO A7FF-53 NUMERIC RESPONSE CONTRACT

Generated: 2026-05-31T05:20:05Z

## Decision

`PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH`

A7FF-53 converts the A7FF-52E materialization pass into a numeric-response execution contract. It does not run labels, controls, replay, search, or alpha proof.

## Source Summary

```json
{
  "activity_ok_rate": 0.875,
  "decision": "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT",
  "eval_failure_count": 0,
  "families_retained": 7,
  "low_activity_families": [
    "funding_like|basis_premium_like"
  ],
  "sample_rows": 1200
}
```

## Family Numeric Policy

| semantic_pair                        |   rows_in_materialization_sample |   eval_success_rows |   activity_ok_rows |   median_finite_share |   median_nonzero_share |   median_std | numeric_policy               | caveat                                                                |
|:-------------------------------------|---------------------------------:|--------------------:|-------------------:|----------------------:|-----------------------:|-------------:|:-----------------------------|:----------------------------------------------------------------------|
| basis_premium_like|price_return_like |                              150 |                 150 |                150 |            0.820741   |               0.999993 |  2.09564     | primary_numeric_candidate    |                                                                       |
| funding_like|basis_premium_like      |                              150 |                 150 |                  0 |            0.00335452 |               0.995041 |  0.707107    | diagnostic_only_low_activity | activity_ok_rows=0 in A7FF-52E; exclude from primary response gates   |
| liquidity_like|price_return_like     |                              150 |                 150 |                150 |            0.820741   |               0.996074 |  0.953852    | primary_numeric_candidate    |                                                                       |
| open_interest_like|price_return_like |                              150 |                 150 |                150 |            0.820681   |               1        |  0.99051     | primary_numeric_candidate    |                                                                       |
| positioning_like|price_return_like   |                              150 |                 150 |                150 |            0.992531   |               1        |  0.994682    | primary_numeric_candidate    |                                                                       |
| regime_state|price_return_like       |                              150 |                 150 |                150 |            0.820741   |               0.999993 |  2.09564     | primary_numeric_candidate    |                                                                       |
| taker_flow_like|basis_premium_like   |                              150 |                 150 |                150 |            0.82505    |               1        |  1.32395e+07 | primary_with_scale_guard     | large numeric scale; require winsor/scale audit before clue promotion |
| volatility_like|basis_premium_like   |                              150 |                 150 |                150 |            0.820741   |               1        |  0.99472     | primary_numeric_candidate    |                                                                       |

## Label Plan

| label_family                       | role            | horizons     | pass_use                                                      |
|:-----------------------------------|:----------------|:-------------|:--------------------------------------------------------------|
| L0_raw_forward_return              | primary         | 1h,4h,8h,24h | can support clue only if control-clean and split-stable       |
| L1_cross_sectional_relative_return | primary         | 1h,4h,8h,24h | required to prevent pure ranked-label artifacts               |
| L3_liquidity_tier_relative_return  | primary         | 1h,4h,8h,24h | tests liquidity-tier robustness                               |
| L5_vol_adjusted_return             | secondary       | 4h,8h,24h    | supports risk-normalized clue evidence but cannot stand alone |
| L7_ranked_future_return            | diagnostic_only | 1h,4h,8h,24h | never sufficient for promotion without non-L7 evidence        |

## Control Plan

| control             | hard_gate                               |
|:--------------------|:----------------------------------------|
| wrong_lag_future    | control_ratio < 0.80 for clue promotion |
| wrong_lag_stale     | control_ratio < 0.80 for clue promotion |
| row_shuffle         | must be weaker than original signal     |
| time_shuffle        | must be weaker than original signal     |
| symbol_shuffle      | must be weaker than original signal     |
| sign_flip           | cannot produce symmetric pass           |
| same_family_placebo | must not dominate original family       |

## Contract

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric_response_execution": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH",
  "execution_budget_if_later_approved": {
    "diagnostic_only_low_activity_families": [
      "funding_like|basis_premium_like"
    ],
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_materialized_rows": 1200,
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return"
    ],
    "max_reports": 1,
    "max_runtime_tables": 6,
    "max_scripts": 1,
    "primary_semantic_families": [
      "basis_premium_like|price_return_like",
      "liquidity_like|price_return_like",
      "open_interest_like|price_return_like",
      "positioning_like|price_return_like",
      "regime_state|price_return_like",
      "taker_flow_like|basis_premium_like",
      "volatility_like|basis_premium_like"
    ]
  },
  "hard_gates_for_future_execution": {
    "control_ratio_for_clue": "< 0.80",
    "l7_only_evidence": "diagnostic_only_not_promotable",
    "low_activity_family_primary_rows": 0,
    "materialization_eval_failure_count": 0,
    "missing_field_count": 0,
    "non_l7_primary_label_clue_rows": "> 0",
    "primary_family_count": ">= 6",
    "uses_may_in_score": false,
    "wrong_lag_dominance": 0
  },
  "hard_stop_before": [
    "formula search",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "input_metrics": "runtime/a7ff52e_materialization_preflight/a7ff52e_materialization_metrics.csv",
  "input_summary": "runtime/a7ff52e_materialization_preflight/a7ff52e_summary.csv",
  "name": "numeric response contract after A7FF-52E materialization preflight",
  "source_stage": "A7FF-52E",
  "stage": "A7FF-53"
}
```

## Boundary

```text
numeric response executed: false
replay executed: false
search executed: false
May used in scoring: false
alpha proof / shadow / paper / live: false
```
