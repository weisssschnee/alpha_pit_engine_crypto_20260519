# CRYPTO A7FF-CORE65B EXPANDED NUMERIC PROBE

Generated: 2026-06-05T01:42:32Z

## Decision

`HOLD_A7FFCORE65B_PORTFOLIO_QUEUE_TOO_SMALL`

A7FF-CORE65B materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "portfolio_selected_lt_4"
  ],
  "decision": "HOLD_A7FFCORE65B_PORTFOLIO_QUEUE_TOO_SMALL",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-05T01:42:32Z",
  "input_blueprint_count": 128,
  "label_response_rows": 1920,
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
    "L7_ranked_future_return"
  ],
  "materialized_activity_ok_count": 96,
  "non_l7_numeric_clue_rows": 2,
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
  "portfolio_queue_count": 1,
  "queue_limit": 128,
  "queue_offset": 0,
  "queue_path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ffcore65b_funding_state_retest_execution\\core65b_patched_funding_state_retest_queue.csv",
  "queue_total_rows": 128,
  "rank_label_diagnostic_clue_rows": 0,
  "selected_portfolio_queue_count": 1,
  "stage": "A7FF-CORE65B",
  "uses_may": false,
  "writes_control_detail": true
}
```

## Decision Counts

| decision                           | label_family                       |   count |
|:-----------------------------------|:-----------------------------------|--------:|
| A7FFCORE65B_NUMERIC_CLUE           | L0_raw_forward_return              |       1 |
| A7FFCORE65B_NUMERIC_CLUE           | L1_cross_sectional_relative_return |       1 |
| HOLD_A7FFCORE65B_CONTROL_DOMINATED | L0_raw_forward_return              |      26 |
| HOLD_A7FFCORE65B_CONTROL_DOMINATED | L1_cross_sectional_relative_return |      26 |
| HOLD_A7FFCORE65B_CONTROL_DOMINATED | L3_liquidity_tier_relative_return  |      29 |
| HOLD_A7FFCORE65B_CONTROL_DOMINATED | L5_vol_adjusted_return             |      57 |
| HOLD_A7FFCORE65B_CONTROL_DOMINATED | L7_ranked_future_return            |      63 |
| HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L0_raw_forward_return              |     357 |
| HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L1_cross_sectional_relative_return |     357 |
| HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L3_liquidity_tier_relative_return  |     355 |
| HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L5_vol_adjusted_return             |     327 |
| HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  | L7_ranked_future_return            |     321 |

## Family Summary

| semantic_pair                         | decision                           |   count |
|:--------------------------------------|:-----------------------------------|--------:|
| basis_premium_like|funding_state_like | A7FFCORE65B_NUMERIC_CLUE           |       2 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_CONTROL_DOMINATED |     175 |
| basis_premium_like|funding_state_like | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  |    1543 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_CONTROL_DOMINATED |      26 |
| funding_state_like|positioning_like   | HOLD_A7FFCORE65B_PRE_MAY_UNSTABLE  |     174 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.952776 |     607.354 |   5760 |
| same_family_placebo  |       0.359834 |    2676.17  |   5760 |
| sign_flip            |       0.983938 |     560.069 |   5760 |
| symbol_shuffle       |       0.639159 |    3024.61  |   5760 |
| time_shuffle         |       0.667918 |    3991.97  |   5760 |
| wrong_lag_future_24h |       1.76783  |    2905.67  |   5760 |
| wrong_lag_stale_168h |       0.824223 |    2889.79  |   5760 |

## Selected Portfolio Queue

| blueprint_id                             | expression                                                                   | semantic_pair                         | motif               | label_family          |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                 |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share |
|:-----------------------------------------|:-----------------------------------------------------------------------------|:--------------------------------------|:--------------------|:----------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:-------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|
| a7ff24r_32041f96444778a3_funding_state8h | Mul(Neg(ZScore(funding_rate_state_last_ffill_8h)),Sign(Delta(mark_close,8))) | basis_premium_like|funding_state_like | mean_reversion_gate | L0_raw_forward_return |                 4 |                        1 |                             3 | True                  |                   0.938888 |                    0.00163492 | True     |                    0.618146 |                -0.498849 | True        |              0.00148661 |             0.000886609 |             -0.000113391 |            95.4667 | A7FFCORE65B_NUMERIC_CLUE |            627 |               0.00219498 |            1.92009 |                             0.932706 |                        -0.0413248 |                   0.503987 |                   632 |                      0.00108381 |                   1.61252 |                                    0.917756 |                                -0.498849 |                          0.476266 |             680 |               0.000839112 |             1.28972 |                              0.618146 |                           0.356404 |                    0.517647 |                       706 |                          0.00188661 |                       1.91199 |                                         1.08189 |                                    0.0771558 |                              0.542493 |              1 |        6.94772 | skel_ac3a45a1120f7842 |       0.825709 |        0.998184 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.
```
