# CRYPTO A7FF-CORE56 BOUNDED REPLAY PREFLIGHT

Generated: 2026-06-04T12:15:42Z

## Decision

`HOLD_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT`

CORE56 runs bounded replay over the CORE55 replay-ready packet. It uses full panel labels, decile spread, stale/time/symbol/sign controls, and split checks. It is not search or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core57_replay_arbitration": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "clean_candidate_count_lt_12",
    "clean_semantic_pair_count_lt_4",
    "clean_label_family_count_lt_2"
  ],
  "clean_candidate_count": 0,
  "clean_label_family_count": 0,
  "clean_replay_rows": 0,
  "clean_semantic_pair_count": 0,
  "clean_top_semantic_pair_share": 0.0,
  "decision": "HOLD_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT",
  "eval_failure_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "frame_rows": 6949596,
  "frame_symbols": 498,
  "generated_at": "2026-06-04T12:15:42Z",
  "label_matrix_count": 16,
  "packet_count": 114,
  "replay_metric_rows": 1824,
  "source_decision": "PASS_A7FFCORE55_REPLAY_READY_PACKET_BUILT",
  "source_stage": "A7FF-CORE55",
  "stage": "A7FF-CORE56",
  "timestamp_count": 21025,
  "uses_may": false
}
```

## Label Decision Summary

| label_family          |   label_horizon_h | decision                      |   row_count |
|:----------------------|------------------:|:------------------------------|------------:|
| L3_liquidity_relative |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |
| L3_liquidity_relative |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |
| L3_liquidity_relative |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |
| L3_liquidity_relative |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |         114 |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          97 |
| L1_xs                 |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          87 |
| L0_raw                |                 1 | HOLD_CORE56_CONTROL_DOMINATED |          87 |
| L1_xs                 |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          87 |
| L0_raw                |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          87 |
| L5_vol_adjusted       |                24 | HOLD_CORE56_PREMAY_UNSTABLE   |          86 |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |
| L0_raw                |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |
| L1_xs                 |                 8 | HOLD_CORE56_PREMAY_UNSTABLE   |          72 |
| L1_xs                 |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          68 |
| L0_raw                |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          68 |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          58 |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_PREMAY_UNSTABLE   |          55 |
| L0_raw                |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          43 |
| L1_xs                 |                 4 | HOLD_CORE56_CONTROL_DOMINATED |          43 |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          41 |
| L1_xs                 |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          38 |
| L0_raw                |                 8 | HOLD_CORE56_CONTROL_DOMINATED |          38 |
| L5_vol_adjusted       |                24 | HOLD_CORE56_CONTROL_DOMINATED |          28 |
| L0_raw                |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          27 |
| L1_xs                 |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          27 |
| L1_xs                 |                24 | HOLD_CORE56_CONTROL_DOMINATED |          26 |
| L0_raw                |                24 | HOLD_CORE56_CONTROL_DOMINATED |          26 |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_PREMAY_UNSTABLE   |          12 |
| L5_vol_adjusted       |                 1 | HOLD_CORE56_STALE_LAG_FRAGILE |           5 |
| L0_raw                |                 8 | HOLD_CORE56_COST5_FRAGILE     |           3 |
| L0_raw                |                 4 | HOLD_CORE56_COST5_FRAGILE     |           3 |
| L1_xs                 |                 4 | HOLD_CORE56_COST5_FRAGILE     |           3 |
| L1_xs                 |                 8 | HOLD_CORE56_COST5_FRAGILE     |           3 |
| L0_raw                |                24 | HOLD_CORE56_COST5_FRAGILE     |           1 |
| L0_raw                |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |
| L1_xs                 |                24 | HOLD_CORE56_COST5_FRAGILE     |           1 |
| L1_xs                 |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |
| L5_vol_adjusted       |                 4 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |
| L5_vol_adjusted       |                 8 | HOLD_CORE56_STALE_LAG_FRAGILE |           1 |

## Split Observation Summary

| metric             |   train_2024_obs |   validation_2025H1_obs |   test_2025H2_obs |   recent_oos_2026JanApr_obs |
|:-------------------|-----------------:|------------------------:|------------------:|----------------------------:|
| min                |                0 |                       0 |                 0 |                           0 |
| median             |             8736 |                    4344 |              4416 |                        2880 |
| max                |             8784 |                    4344 |              4416 |                        2880 |
| positive_row_count |             1368 |                    1368 |              1368 |                        1368 |

## Clean Semantic Summary

`<empty>`

## Candidate Summary

| blueprint_id             | semantic_pair                         | motif         |   replay_rows |   clean_rows |   label_family_count |   median_control_ratio |   max_recent_spread |
|:-------------------------|:--------------------------------------|:--------------|--------------:|-------------:|---------------------:|-----------------------:|--------------------:|
| a7ff24r_09dc2d7e51641cb0 | basis_premium_like|basis_premium_like | sub           |            16 |            0 |                    4 |                1       |           0.291769  |
| a7ff24r_2fff7c49f91def0b | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                2.04675 |           0.283757  |
| a7ff24r_038ab74762617034 | basis_premium_like|basis_premium_like | mul           |            16 |            0 |                    4 |                2.20481 |           0.19402   |
| a7ff24r_8d906801b8dec4c0 | basis_premium_like|basis_premium_like | mul           |            16 |            0 |                    4 |                3.07287 |           0.188874  |
| a7ff24r_1bf5a62b347b3926 | basis_premium_like|price_like         | spread_rank   |            16 |            0 |                    4 |                1.80684 |           0.12507   |
| a7ff24r_1e19db32c95dfcc4 | basis_premium_like|positioning_like   | smooth_mul    |            16 |            0 |                    4 |                1       |           0.117643  |
| a7ff24r_16601b09f488fcdc | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00504 |           0.0985627 |
| a7ff24r_2353c3ae1292b858 | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00504 |           0.0985627 |
| a7ff24r_146a079f1808397b | basis_premium_like|positioning_like   | safe_div_abs  |            16 |            0 |                    4 |                1.30391 |           0.0979445 |
| a7ff24r_75f3e9364180854b | price_like|volatility_like            | mul           |            16 |            0 |                    4 |                1.28516 |           0.0919536 |
| a7ff24r_029eac5b325dde0b | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00936 |           0.0874567 |
| a7ff24r_0d2e211c74b8ab69 | price_like|volatility_like            | mul           |            16 |            0 |                    4 |                1.2727  |           0.0872278 |
| a7ff24r_6c1047e92aac3e0c | basis_premium_like|price_like         | gated_sign    |            16 |            0 |                    4 |                3.85158 |           0.0862278 |
| a7ff24r_6b86864574e34096 | price_like|volatility_like            | mul           |            16 |            0 |                    4 |                1.21597 |           0.0851657 |
| a7ff24r_5addd614de29d1e7 | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00342 |           0.0806351 |
| a7ff24r_75bc40a3fbfa994d | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00342 |           0.0806351 |
| a7ff24r_8bf0eefef7542ccd | basis_premium_like                    | single        |            16 |            0 |                    4 |                1       |           0.0794718 |
| a7ff24r_2f417cea53e275b6 | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1       |           0.0791922 |
| a7ff24r_7affd59d06f0cdfa | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1       |           0.0791605 |
| a7ff24r_20b072602eeb21eb | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1       |           0.0791341 |
| a7ff24r_b6c425eb5d65f76a | basis_premium_like|price_like         | mul           |            16 |            0 |                    4 |                7.09467 |           0.076772  |
| a7ff24r_18494b19560b1e1c | price_like|volatility_like            | gated_sign    |            16 |            0 |                    4 |                1.37346 |           0.076614  |
| a7ff24r_18d238dbb46f8356 | basis_premium_like|basis_premium_like | gated_sign    |            16 |            0 |                    4 |                1.02654 |           0.0764086 |
| a7ff24r_12f75c2e2796dd6e | basis_premium_like|positioning_like   | mul           |            16 |            0 |                    4 |                2.29351 |           0.0756823 |
| a7ff24r_168885405125bba0 | basis_premium_like|basis_premium_like | gated_sign    |            16 |            0 |                    4 |                1.04385 |           0.0742063 |
| a7ff24r_0e8cf4f2d2d653c7 | basis_premium_like|positioning_like   | spread_rank   |            16 |            0 |                    4 |                1.21024 |           0.0732224 |
| a7ff24r_eab92902c63036e3 | basis_premium_like                    | single        |            16 |            0 |                    4 |                1       |           0.0719592 |
| a7ff24r_503edc81504e964a | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1       |           0.071597  |
| a7ff24r_2896b670ebf3967c | price_like|volatility_like            | mul           |            16 |            0 |                    4 |                2.60839 |           0.0660758 |
| a7ff24r_46dbca9c53956336 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                2.08043 |           0.0582248 |
| a7ff24r_0ba14c1c756fb529 | basis_premium_like|basis_premium_like | safe_div_abs  |            16 |            0 |                    4 |                1       |           0.0571823 |
| a7ff24r_106659470940e2eb | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1       |           0.0563358 |
| a7ff24r_6b9e4107d4ce11d4 | basis_premium_like                    | single        |            16 |            0 |                    4 |                1       |           0.0563145 |
| a7ff24r_842341fb2d786d51 | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1       |           0.0562917 |
| a7ff24r_5fd29d53584be2bf | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00655 |           0.0544091 |
| a7ff24r_596e8f66dbea15c3 | basis_premium_like|basis_premium_like | safe_div_abs  |            16 |            0 |                    4 |                1       |           0.0536849 |
| a7ff24r_542b570f4bf41412 | basis_premium_like|volatility_like    | mul           |            16 |            0 |                    4 |                1       |           0.0525454 |
| a7ff24r_010c17f20813e83d | basis_premium_like|basis_premium_like | sub           |            16 |            0 |                    4 |                1.47033 |           0.0510521 |
| a7ff24r_57e00327a34e91e3 | basis_premium_like                    | single        |            16 |            0 |                    4 |                1.75079 |           0.0504762 |
| a7ff24r_6a8e4e33dbe4b09c | basis_premium_like                    | single        |            16 |            0 |                    4 |                1.21555 |           0.0503387 |
| a7ff24r_84e6b7e0b4d14184 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.11022 |           0.0495188 |
| a7ff24r_95db6511637ff25a | price_like                            | single        |            16 |            0 |                    4 |                6.43754 |           0.049393  |
| a7ff24r_ff9b56ccd0b1474f | price_like                            | single        |            16 |            0 |                    4 |                1.00116 |           0.0489407 |
| a7ff24r_072721eac2a0cfd3 | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1       |           0.0485832 |
| a7ff24r_8e3dd007dfadf9b2 | basis_premium_like|price_like         | mul           |            16 |            0 |                    4 |                4.71374 |           0.0473666 |
| a7ff24r_8176be4b94b1f677 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.31951 |           0.0470553 |
| a7ff24r_650915032f2a5979 | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1.02429 |           0.046531  |
| a7ff24r_858ff2210f276fcf | basis_premium_like                    | single        |            16 |            0 |                    4 |                1.10248 |           0.0465041 |
| a7ff24r_35936163ee9000cf | basis_premium_like|basis_premium_like | spread_rank   |            16 |            0 |                    4 |                1.00741 |           0.0455669 |
| a7ff24r_1c490f81c21f5f03 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.36253 |           0.0421824 |
| a7ff24r_eb94ce69b7faa44c | basis_premium_like                    | single        |            16 |            0 |                    4 |                1       |           0.0409664 |
| a7ff24r_b8f107bc73b71bc4 | liquidity_like|volatility_like        | spread_rank   |            16 |            0 |                    4 |                1.36829 |           0.0398796 |
| a7ff24r_ce8b14f4223a0409 | liquidity_like|volatility_like        | signed_spread |            16 |            0 |                    4 |                1.76625 |           0.0397993 |
| a7ff24r_712cf35327cfd98e | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1.16127 |           0.0397424 |
| a7ff24r_7f35619193e2d6d9 | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1.14165 |           0.0395232 |
| a7ff24r_0f543a2861f3d20f | basis_premium_like|volatility_like    | safe_div_abs  |            16 |            0 |                    4 |                1.20024 |           0.0387169 |
| a7ff24r_acdf1de7772e8224 | basis_premium_like                    | single        |            16 |            0 |                    4 |                1.47119 |           0.0384198 |
| a7ff24r_2c903d264aee7ca3 | basis_premium_like|volatility_like    | safe_div_abs  |            16 |            0 |                    4 |                1.70793 |           0.0382323 |
| a7ff24r_6851231817646ddc | basis_premium_like|price_like         | mul           |            16 |            0 |                    4 |                2.37064 |           0.0381396 |
| a7ff24r_389e925b81a0c645 | basis_premium_like|volatility_like    | smooth_mul    |            16 |            0 |                    4 |                1.96089 |           0.0380673 |
| a7ff24r_610c51dfffdc8f01 | basis_premium_like|volatility_like    | mul           |            16 |            0 |                    4 |                1.60953 |           0.0375073 |
| a7ff24r_7a6f873cfe7bc14d | basis_premium_like|volatility_like    | mul           |            16 |            0 |                    4 |                3.62296 |           0.0364268 |
| a7ff24r_47bcb06b0eb1f42a | basis_premium_like|volatility_like    | mul           |            16 |            0 |                    4 |                1.00625 |           0.0330898 |
| a7ff24r_48f9f812cd8214e5 | basis_premium_like|basis_premium_like | gated_sign    |            16 |            0 |                    4 |                1.77298 |           0.0327432 |
| a7ff24r_36473bbc00718694 | basis_premium_like|basis_premium_like | safe_div_abs  |            16 |            0 |                    4 |                1.33312 |           0.0307878 |
| a7ff24r_145e2d58adad4f4a | basis_premium_like|basis_premium_like | safe_div_abs  |            16 |            0 |                    4 |                1.72225 |           0.0284454 |
| a7ff24r_129519e7eda158fa | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.73022 |           0.0269371 |
| a7ff24r_1e349d20bff26d23 | basis_premium_like|basis_premium_like | safe_div_abs  |            16 |            0 |                    4 |                1.61151 |           0.0255737 |
| a7ff24r_83417b3871e08795 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.92987 |           0.0251294 |
| a7ff24r_5c84c80e5b76b421 | basis_premium_like|price_like         | sub           |            16 |            0 |                    4 |                1.41716 |           0.0249457 |
| a7ff24r_5ee045650ebd8b30 | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.31238 |           0.0246465 |
| a7ff24r_0386a2799693d3f8 | price_like|volatility_like            | gated_sign    |            16 |            0 |                    4 |                2.74205 |           0.0239893 |
| a7ff24r_55434e3c45f77aed | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                2.03064 |           0.0228879 |
| a7ff24r_892545e2049b6eba | basis_premium_like|price_like         | safe_div_abs  |            16 |            0 |                    4 |                1.45259 |           0.0221729 |
| a7ff24r_6550f4a63c432aa1 | price_like|volatility_like            | mul           |            16 |            0 |                    4 |                1.70317 |           0.0218828 |
| a7ff24r_8109a8c7568833d5 | basis_premium_like|price_like         | mul           |            16 |            0 |                    4 |                2.3049  |           0.0218051 |
| a7ff24r_c223ee324263786f | basis_premium_like|volatility_like    | safe_div_abs  |            16 |            0 |                    4 |                1.44356 |           0.0214472 |
| a7ff24r_931e020ea7a720ae | basis_premium_like|volatility_like    | gated_sign    |            16 |            0 |                    4 |                1.04661 |           0.021076  |
| a7ff24r_7eeaa9c128fa6743 | price_like                            | single        |            16 |            0 |                    4 |                3.04492 |           0.0204091 |
| a7ff24r_28c1f862a15e5d51 | basis_premium_like|volatility_like    | safe_div_abs  |            16 |            0 |                    4 |                1.5228  |           0.0193261 |

## Boundary

```text
replay executed: true
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
