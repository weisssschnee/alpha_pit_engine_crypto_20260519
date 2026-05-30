# CRYPTO A7FF-27 REPLAY PREFLIGHT SUMMARY

Generated: 2026-05-30T09:30:37Z

## Decision

`PASS_A7FF27_REPLAY_PREFLIGHT_READY_FOR_A7FF28_DEEP_REPLAY_CONTRACT_NO_SEARCH_AUTH`

A7FF-27 reruns the A7FF-26 promotion-ready numeric research clues through the numeric replay preflight evaluator. It is a preflight step only; it does not run search, alpha proof, shadow, paper, or live execution.

## Experiment Record

```text
experiment_id: 20260530_a7ff27_replay_preflight
objective: verify whether A7FF-26 promotion-ready numeric clues survive a fresh evaluator run
input: runtime/a7ff26_numeric_clue_forensic/a7ff26_promotion_candidate_queue.csv
parameters: 14 candidates, labels L0/L1/L3/L5/L7, horizons 1/4/8/24h, controls from A7FF numeric probe
command: A7FF8_STAGE=A7FF-27 ... py scripts/crypto_a7ff8_expanded_numeric_probe.py
decision: no search authorization
```

## Manifest

```json
{
  "authorizes_a7ff28_deep_replay_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF27_REPLAY_PREFLIGHT_READY_FOR_A7FF28_DEEP_REPLAY_CONTRACT_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:30:37Z",
  "input_candidate_count": 14,
  "label_response_rows": 280,
  "materialized_activity_ok_count": 14,
  "non_l7_numeric_clue_rows": 49,
  "prior_decision": "PASS_A7FF26_NUMERIC_RESEARCH_CLUES_READY_FOR_REPLAY_PREFLIGHT_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-26",
  "selected_preflight_count": 8,
  "selected_semantic_pair_count": 3,
  "selected_skeleton_count": 8,
  "stage": "A7FF-27",
  "uses_may": false,
  "warnings": []
}
```

## A7FF-28 Preflight Queue

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | label_family           |   label_horizon_h |   score_no_may |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:-----------------------|------------------:|---------------:|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | L5_vol_adjusted_return |                 8 |       395.628  |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                 8 |       395.607  |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return |                 8 |       198.51   |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |       159.014  |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                 4 |       142.369  |
| a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |        91.4977 |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return |                 1 |        91.2013 |
| a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps)           | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                 1 |        85.8802 |

## Candidate Summary

| blueprint_id             | semantic_pair                         | motif        |   response_rows |   non_l7_numeric_clue_rows |   rank_label_diag_rows |   label_family_count |   horizon_count |   control_ratio_min |   control_ratio_median |   robust_min_tstat_max |   cost10_recent_max |   score_no_may | skeleton_key          | selected_for_a7ff28_preflight   |
|:-------------------------|:--------------------------------------|:-------------|----------------:|---------------------------:|-----------------------:|---------------------:|----------------:|--------------------:|-----------------------:|-----------------------:|--------------------:|---------------:|:----------------------|:--------------------------------|
| a7ff24r_650915032f2a5979 | basis_premium_like|volatility_like    | gated_sign   |              20 |                          8 |                      2 |                    5 |               4 |            0.245384 |               0.880772 |                7.04826 |           0.461994  |       395.47   | skel_136259b72205469f | True                            |
| a7ff24r_858ff2210f276fcf | basis_premium_like                    | single       |              20 |                          7 |                      2 |                    5 |               4 |            0.130273 |               0.910286 |                7.04826 |           0.461994  |       395.583  | skel_1d39996e97d5ace0 | True                            |
| a7ff24r_389e925b81a0c645 | basis_premium_like|volatility_like    | smooth_mul   |              20 |                          7 |                      2 |                    5 |               4 |            0.293905 |               0.924537 |                4.40942 |           0.299856  |       198.93   | skel_8184698cb7b24c02 | True                            |
| a7ff24r_bcc3435cf539d883 | basis_premium_like|basis_premium_like | sub          |              20 |                          4 |                      1 |                    5 |               4 |            0.165931 |               2.33224  |                8.97436 |           0.280197  |       159.012  | skel_f8484b844efd270f | True                            |
| a7ff24r_145e2d58adad4f4a | basis_premium_like|basis_premium_like | safe_div_abs |              20 |                          1 |                      1 |                    5 |               4 |            0.204993 |               1.82938  |                7.84942 |           0.135293  |       142.506  | skel_c80f62c274b367a9 | True                            |
| a7ff24r_09dc2d7e51641cb0 | basis_premium_like|basis_premium_like | sub          |              20 |                          1 |                      2 |                    5 |               4 |            0.369217 |               2.42684  |                6.75083 |           0.272975  |        91.4977 | skel_0994b3a36a4d53ba | True                            |
| a7ff24r_c223ee324263786f | basis_premium_like|volatility_like    | safe_div_abs |              20 |                          1 |                      1 |                    5 |               4 |            0.834202 |               4.81214  |                2.53115 |           0.0841199 |        91.4458 | skel_d9d4f69744bac825 | True                            |
| a7ff24r_14bb4d389b4b94f0 | basis_premium_like|basis_premium_like | sub          |              20 |                          1 |                      0 |                    5 |               4 |            0.444371 |              12.5351   |                3.71359 |           0.0925208 |        85.8802 | skel_97ea9710bb50e137 | True                            |
| a7ff24r_8d906801b8dec4c0 | basis_premium_like|basis_premium_like | mul          |              20 |                          4 |                      0 |                    5 |               4 |            0.600993 |               3.94986  |                4.12286 |           0.2265    |       119.327  | skel_f8484b844efd270f | False                           |
| a7ff24r_62921caa01dbd001 | basis_premium_like|volatility_like    | safe_div_abs |              20 |                          4 |                      0 |                    5 |               4 |            0.171806 |               2.12615  |                5.48239 |           0.0922978 |        99.9808 | skel_c80f62c274b367a9 | False                           |
| a7ff24r_4f5fad181e850eac | price_like|volatility_like            | gated_sign   |              20 |                          4 |                      2 |                    5 |               4 |            0.328913 |               1.33163  |                4.85166 |           0.0382802 |        45.5466 | skel_c80f62c274b367a9 | False                           |
| a7ff24r_b74c05b6f58309a0 | basis_premium_like|price_like         | safe_div_abs |              20 |                          3 |                      1 |                    5 |               4 |            0.559623 |               3.73375  |                2.24107 |           0.0799569 |        87.4536 | skel_c80f62c274b367a9 | False                           |
| a7ff24r_809e5867ebe18c47 | basis_premium_like|price_like         | safe_div_abs |              20 |                          3 |                      0 |                    5 |               4 |            0.770569 |               4.67533  |                2.4936  |           0.0681169 |        75.3526 | skel_c80f62c274b367a9 | False                           |
| a7ff24r_f695d065dec8c1ad | basis_premium_like|basis_premium_like | mul          |              20 |                          1 |                      0 |                    5 |               4 |            0.517001 |               3.77127  |                2.28389 |           0.307563  |        48.8533 | skel_0994b3a36a4d53ba | False                           |

## Label Decision Summary

| label_family                       | decision                          |   count |
|:-----------------------------------|:----------------------------------|--------:|
| L0_raw_forward_return              | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      29 |
| L0_raw_forward_return              | HOLD_A7FF27_CONTROL_DOMINATED     |      14 |
| L0_raw_forward_return              | A7FF27_NUMERIC_CLUE               |      10 |
| L0_raw_forward_return              | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       2 |
| L0_raw_forward_return              | HOLD_A7FF27_COST2_PROXY_FRAGILE   |       1 |
| L1_cross_sectional_relative_return | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      29 |
| L1_cross_sectional_relative_return | HOLD_A7FF27_CONTROL_DOMINATED     |      14 |
| L1_cross_sectional_relative_return | A7FF27_NUMERIC_CLUE               |      11 |
| L1_cross_sectional_relative_return | HOLD_A7FF27_COST2_PROXY_FRAGILE   |       1 |
| L1_cross_sectional_relative_return | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       1 |
| L3_liquidity_tier_relative_return  | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      29 |
| L3_liquidity_tier_relative_return  | HOLD_A7FF27_CONTROL_DOMINATED     |      14 |
| L3_liquidity_tier_relative_return  | A7FF27_NUMERIC_CLUE               |       9 |
| L3_liquidity_tier_relative_return  | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       3 |
| L3_liquidity_tier_relative_return  | HOLD_A7FF27_COST2_PROXY_FRAGILE   |       1 |
| L5_vol_adjusted_return             | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      28 |
| L5_vol_adjusted_return             | A7FF27_NUMERIC_CLUE               |      19 |
| L5_vol_adjusted_return             | HOLD_A7FF27_CONTROL_DOMINATED     |       7 |
| L5_vol_adjusted_return             | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |       2 |
| L7_ranked_future_return            | HOLD_A7FF27_PRE_MAY_UNSTABLE      |      21 |
| L7_ranked_future_return            | A7FF27_RANK_LABEL_DIAGNOSTIC_CLUE |      14 |
| L7_ranked_future_return            | HOLD_A7FF27_ONE_BAR_LAG_FRAGILE   |      12 |
| L7_ranked_future_return            | HOLD_A7FF27_CONTROL_DOMINATED     |       9 |

## Selected Family Summary

| semantic_pair                         | motif        |   selected_count |
|:--------------------------------------|:-------------|-----------------:|
| basis_premium_like|basis_premium_like | sub          |                3 |
| basis_premium_like                    | single       |                1 |
| basis_premium_like|basis_premium_like | safe_div_abs |                1 |
| basis_premium_like|volatility_like    | gated_sign   |                1 |
| basis_premium_like|volatility_like    | safe_div_abs |                1 |
| basis_premium_like|volatility_like    | smooth_mul   |                1 |

## Control Summary

| control              |   median_ratio |   max_ratio |   rows |
|:---------------------|---------------:|------------:|-------:|
| one_bar_lag          |       0.554576 |    177.667  |    840 |
| same_family_placebo  |       0.209278 |    297.05   |    840 |
| sign_flip            |       0.996704 |     74.4284 |    840 |
| symbol_shuffle       |       0.264593 |    239.683  |    840 |
| time_shuffle         |       0.311971 |    178.796  |    840 |
| wrong_lag_future_24h |       0.678209 |    434.074  |    840 |
| wrong_lag_stale_168h |       0.350337 |    354.346  |    840 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
L7 ranked-return rows remain diagnostic-only.
A7FF-27 authorizes at most drafting/executing A7FF-28 deep replay contract/preflight for the selected queue.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
