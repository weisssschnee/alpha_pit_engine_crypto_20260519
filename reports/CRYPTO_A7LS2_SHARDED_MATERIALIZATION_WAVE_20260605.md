# CRYPTO A7LS-2 SHARDED MATERIALIZATION WAVE

Generated: 2026-06-05T04:08:48Z

## Decision

`PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY`

A7LS-2 executes the materialization wave in memory-safe shards. This run defaults to first checkpoint tranche: one 500-row shard per arm.

## Manifest

```json
{
  "activity_ok_count": 1273,
  "activity_ok_rate": 0.6365,
  "authorizes_a7ls2_continue_materialization": true,
  "authorizes_a7ls3_numeric_wave": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
  "eval_failure_count": 0,
  "executed_arm_count": 4,
  "executed_rows": 2000,
  "executed_shard_count": 4,
  "executes_materialization": true,
  "executes_numeric_probe": false,
  "executes_search": false,
  "generated_at": "2026-06-05T04:08:48Z",
  "source_decision": "PASS_A7LS1_MULTI_ARM_BLUEPRINT_GENERATION_READY_FOR_A7LS2",
  "source_stage": "A7LS-1",
  "stage": "A7LS-2"
}
```

## Checkpoint Status

| shard                       | generated_at         |   queue_rows | a7ls_arm   |   field_count |   missing_field_count | missing_fields   |   symbols_loaded |   timestamps_loaded |   eval_success_count |   eval_failure_count |   activity_ok_count |   activity_ok_rate |
|:----------------------------|:---------------------|-------------:|:-----------|--------------:|----------------------:|:-----------------|-----------------:|--------------------:|---------------------:|---------------------:|--------------------:|-------------------:|
| a7ls_a_materialization_s000 | 2026-06-05T04:03:20Z |          500 | A7LS_A     |             3 |                     0 | []               |               96 |               21025 |                  500 |                    0 |                 433 |              0.866 |
| a7ls_b_materialization_s020 | 2026-06-05T04:05:42Z |          500 | A7LS_B     |            43 |                     0 | []               |               96 |               21025 |                  500 |                    0 |                 367 |              0.734 |
| a7ls_c_materialization_s040 | 2026-06-05T04:06:53Z |          500 | A7LS_C     |             6 |                     0 | []               |               96 |               21025 |                  500 |                    0 |                  66 |              0.132 |
| a7ls_d_materialization_s060 | 2026-06-05T04:08:22Z |          500 | A7LS_D     |            13 |                     0 | []               |               96 |               21025 |                  500 |                    0 |                 407 |              0.814 |

## Semantic Summary

| a7ls_arm   | semantic_pair                     |   rows |   eval_success |   activity_ok |   median_finite_share |   median_nonzero_share |   skeleton_count |   activity_ok_rate |
|:-----------|:----------------------------------|-------:|---------------:|--------------:|----------------------:|-----------------------:|-----------------:|-------------------:|
| A7LS_A     | basis_premium_like                |    500 |            500 |           433 |              0.996833 |               0.988945 |               28 |          0.866     |
| A7LS_B     | basis_premium_like                |     51 |             51 |            34 |              0.997474 |               0.903499 |               10 |          0.666667  |
| A7LS_B     | funding_state_like                |     49 |             49 |            42 |              0.968258 |               0.994634 |                5 |          0.857143  |
| A7LS_B     | funding_state_like|liquidity_like |      2 |              2 |             2 |              0.970312 |               0.78448  |                2 |          1         |
| A7LS_B     | liquidity_like                    |     51 |             51 |            47 |              0.969663 |               1        |                5 |          0.921569  |
| A7LS_B     | listing_age_like                  |     43 |             43 |            43 |              0.969616 |               1        |                3 |          1         |
| A7LS_B     | listing_age_like|regime_state     |      8 |              8 |             0 |              0        |               0        |                5 |          0         |
| A7LS_B     | open_interest_like                |     51 |             51 |            32 |              0.997582 |               0.99996  |                9 |          0.627451  |
| A7LS_B     | positioning_like                  |     50 |             50 |            45 |              0.998415 |               1        |                5 |          0.9       |
| A7LS_B     | positioning_like|liquidity_like   |      1 |              1 |             1 |              0.995394 |               1        |                1 |          1         |
| A7LS_B     | price_like                        |     51 |             51 |            31 |              0.998201 |               0.974875 |               11 |          0.607843  |
| A7LS_B     | regime_state                      |     43 |             43 |             3 |              0        |               0        |                3 |          0.0697674 |
| A7LS_B     | taker_flow_like                   |     46 |             46 |            40 |              0.998415 |               1        |                5 |          0.869565  |
| A7LS_B     | taker_flow_like|liquidity_like    |      4 |              4 |             4 |              0.997796 |               0.999995 |                2 |          1         |
| A7LS_B     | volatility_like                   |     42 |             42 |            38 |              0.969069 |               1        |                5 |          0.904762  |
| A7LS_B     | volatility_like|listing_age_like  |      8 |              8 |             5 |              0.963579 |               1        |                5 |          0.625     |
| A7LS_C     | basis_premium_like                |     70 |             70 |            66 |              0.998248 |               0.999673 |                3 |          0.942857  |
| A7LS_C     | basis_premium_like|regime_state   |    430 |            430 |             0 |              0        |               0        |               18 |          0         |
| A7LS_D     | basis_premium_like                |     70 |             70 |            66 |              0.998248 |               0.999268 |                3 |          0.942857  |
| A7LS_D     | liquidity_like                    |     20 |             20 |            20 |              0.998224 |               1        |                2 |          1         |
| A7LS_D     | low_prior_axes                    |      3 |              3 |             2 |              0.998921 |               1        |                1 |          0.666667  |
| A7LS_D     | low_prior_axes|basis_premium_like |    407 |            407 |           319 |              0.870775 |               0.998033 |               16 |          0.783784  |

## Boundary

```text
materialization executed: true
numeric probe executed: false
search/proof/shadow/live: false
```