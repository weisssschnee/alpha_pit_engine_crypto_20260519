# CRYPTO A7FF-CORE65A EXPANDED NUMERIC PROBE

Generated: 2026-06-05T01:26:22Z

## Decision

`HOLD_A7FFCORE65A_PORTFOLIO_QUEUE_TOO_SMALL`

A7FF-CORE65A materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "portfolio_selected_lt_4"
  ],
  "decision": "HOLD_A7FFCORE65A_PORTFOLIO_QUEUE_TOO_SMALL",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-05T01:26:22Z",
  "input_blueprint_count": 24,
  "label_response_rows": 480,
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
    "L7_ranked_future_return"
  ],
  "materialized_activity_ok_count": 24,
  "non_l7_numeric_clue_rows": 4,
  "plan": {
    "control_probe_cap": 256,
    "controls": [
      "wrong_lag_future",
      "wrong_lag_stale",
      "time_shuffle",
      "symbol_shuffle",
      "sign_flip",
      "same_family_placebo"
    ],
    "deep_audit_cap": 64,
    "fast_numeric_probe_cap": 256,
    "horizons": [
      "1h",
      "4h",
      "8h",
      "24h"
    ],
    "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return",
      "L5_vol_adjusted_return",
      "L7_ranked_future_return_diagnostic_only"
    ],
    "materialize_cap": 384,
    "portfolio_marginal_probe_cap": 128,
    "promotion_blockers": [
      "L7-only cannot promote",
      "control_ratio >= 1.0 blocks",
      "single semantic_pair > 35pct blocks",
      "single skeleton > 15pct blocks",
      "numeric replay required before any search authorization"
    ],
    "required_outputs": [
      "a7ff8_materialization_metrics.csv",
      "a7ff8_label_response_metrics.csv",
      "a7ff8_control_dominance_metrics.csv",
      "a7ff8_nonoverlap_stats.csv",
      "a7ff8_portfolio_marginal_proxy.csv",
      "a7ff8_decision_record.json"
    ],
    "selected_blueprints": 384,
    "stage": "A7FF-8",
    "status": "contract_only_not_executed"
  },
  "portfolio_queue_count": 7,
  "queue_limit": 24,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffcore64_retest_and_funding_state_package\\core64a_numeric_retest_queue.csv",
  "queue_total_rows": 24,
  "rank_label_diagnostic_clue_rows": 7,
  "selected_portfolio_queue_count": 1,
  "stage": "A7FF-CORE65A",
  "uses_may": false,
  "writes_control_detail": true
}
```

## Decision Counts

| decision                               | label_family                       |   count |
|:---------------------------------------|:-----------------------------------|--------:|
| A7FFCORE65A_NUMERIC_CLUE               | L0_raw_forward_return              |       1 |
| A7FFCORE65A_NUMERIC_CLUE               | L1_cross_sectional_relative_return |       1 |
| A7FFCORE65A_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |       1 |
| A7FFCORE65A_NUMERIC_CLUE               | L5_vol_adjusted_return             |       1 |
| A7FFCORE65A_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |       7 |
| HOLD_A7FFCORE65A_CONTROL_DOMINATED     | L0_raw_forward_return              |      28 |
| HOLD_A7FFCORE65A_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |      28 |
| HOLD_A7FFCORE65A_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |      20 |
| HOLD_A7FFCORE65A_CONTROL_DOMINATED     | L5_vol_adjusted_return             |      27 |
| HOLD_A7FFCORE65A_CONTROL_DOMINATED     | L7_ranked_future_return            |       9 |
| HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   | L0_raw_forward_return              |      24 |
| HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   | L1_cross_sectional_relative_return |      24 |
| HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   | L3_liquidity_tier_relative_return  |      27 |
| HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   | L5_vol_adjusted_return             |      29 |
| HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   | L7_ranked_future_return            |      36 |
| HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |      43 |
| HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |      43 |
| HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |      48 |
| HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |      39 |
| HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |      44 |

## Family Summary

| semantic_pair                         | decision                               |   count |
|:--------------------------------------|:---------------------------------------|--------:|
| basis_premium_like                    | A7FFCORE65A_RANK_LABEL_DIAGNOSTIC_CLUE |       1 |
| basis_premium_like                    | HOLD_A7FFCORE65A_CONTROL_DOMINATED     |       8 |
| basis_premium_like                    | HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   |      12 |
| basis_premium_like                    | HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      |      19 |
| basis_premium_like|basis_premium_like | A7FFCORE65A_RANK_LABEL_DIAGNOSTIC_CLUE |       2 |
| basis_premium_like|basis_premium_like | HOLD_A7FFCORE65A_CONTROL_DOMINATED     |      36 |
| basis_premium_like|basis_premium_like | HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   |      46 |
| basis_premium_like|basis_premium_like | HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      |      56 |
| basis_premium_like|price_like         | A7FFCORE65A_NUMERIC_CLUE               |       2 |
| basis_premium_like|price_like         | A7FFCORE65A_RANK_LABEL_DIAGNOSTIC_CLUE |       1 |
| basis_premium_like|price_like         | HOLD_A7FFCORE65A_CONTROL_DOMINATED     |      50 |
| basis_premium_like|price_like         | HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   |      47 |
| basis_premium_like|price_like         | HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      |     100 |
| basis_premium_like|volatility_like    | A7FFCORE65A_NUMERIC_CLUE               |       2 |
| basis_premium_like|volatility_like    | A7FFCORE65A_RANK_LABEL_DIAGNOSTIC_CLUE |       3 |
| basis_premium_like|volatility_like    | HOLD_A7FFCORE65A_CONTROL_DOMINATED     |      18 |
| basis_premium_like|volatility_like    | HOLD_A7FFCORE65A_ONE_BAR_LAG_FRAGILE   |      35 |
| basis_premium_like|volatility_like    | HOLD_A7FFCORE65A_PRE_MAY_UNSTABLE      |      42 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.276236 |    281.563  |   1440 |
| same_family_placebo  |       0.198815 |    337.502  |   1440 |
| sign_flip            |       1.00238  |     34.3885 |   1440 |
| symbol_shuffle       |       0.247595 |    181.578  |   1440 |
| time_shuffle         |       0.251497 |    623.133  |   1440 |
| wrong_lag_future_24h |       0.435782 |    712.571  |   1440 |
| wrong_lag_stale_168h |       0.28421  |    227.815  |   1440 |

## Selected Portfolio Queue

| blueprint_id             | expression                                          | semantic_pair                      | motif   | label_family           |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                 |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key   |   finite_share |   nonzero_share |
|:-------------------------|:----------------------------------------------------|:-----------------------------------|:--------|:-----------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:---------------|---------------:|----------------:|
| a7ff24r_58cd9af618657156 | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h) | basis_premium_like|volatility_like | mul     | L5_vol_adjusted_return |                24 |                       -1 |                             3 | True                  |                   0.904166 |                      0.185804 | True     |                    0.311111 |                  1.70415 | True        |                0.270941 |                0.270341 |                 0.269341 |               92.8 | A7FFCORE65A_NUMERIC_CLUE |            694 |                -0.012675 |          -0.249874 |                           -0.0409538 |                          -1.42577 |                   0.498559 |                   696 |                      -0.0840064 |                  -1.78701 |                                   -0.333308 |                                 -1.87341 |                           0.46408 |             696 |                 -0.192773 |            -2.82794 |                             -0.684388 |                           -1.70415 |                    0.442529 |                       696 |                           -0.271341 |                      -2.34651 |                                       -0.311111 |                                     -2.37114 |                              0.471264 |              1 |        276.437 |                |       0.826774 |        0.998541 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
