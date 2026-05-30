# CRYPTO A7FF-29 CANDIDATE FORENSIC

Generated: 2026-05-30T10:17:28Z

## Decision

`PASS_A7FF29_FORENSIC_READY_FOR_A7FF30_PORTFOLIO_REPLAY_CONTRACT_WITH_CONCENTRATION_WARNINGS_NO_SEARCH_AUTH`

A7FF-29 audits the 6 non-L7 candidates from A7FF-28A. It does not generate formulas, execute search, or claim alpha.

## Experiment Record

```text
experiment_id: 20260530_a7ff29_candidate_forensic
objective: decide whether the 181-symbol non-L7 clue queue is clean enough for a portfolio replay contract
inputs: runtime/a7ff28a_bounded_deep_replay/*
parameters: no generation; no search; non-L7 only; control_ratio < 1 hard gate
```

## Manifest

```json
{
  "authorizes_a7ff30_portfolio_replay_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 6,
  "decision": "PASS_A7FF29_FORENSIC_READY_FOR_A7FF30_PORTFOLIO_REPLAY_CONTRACT_WITH_CONCENTRATION_WARNINGS_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T10:17:28Z",
  "kept_candidate_count": 6,
  "max_control_ratio": 0.7819075601681075,
  "prior_decision": "PASS_A7FF28A_BOUNDED_DEEP_REPLAY_READY_FOR_A7FF29_FORENSIC_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-28A-SUMMARY",
  "semantic_pair_count": 3,
  "stage": "A7FF-29",
  "warnings": [
    "all_candidates_have_basis_premium_root",
    "safe_div_outlier_risk_present"
  ]
}
```

## Candidate Forensic Summary

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          |   non_l7_clue_rows | non_l7_label_families                                                                                             | non_l7_horizons   | best_label_family                  |   best_label_horizon_h |   min_control_ratio |   max_control_ratio |   min_robust_min_tstat_floor |   finite_share |   nonzero_share | activity_ok   | warning_flags                                                              | forensic_decision          |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|-------------------:|:------------------------------------------------------------------------------------------------------------------|:------------------|:-----------------------------------|-----------------------:|--------------------:|--------------------:|-----------------------------:|---------------:|----------------:|:--------------|:---------------------------------------------------------------------------|:---------------------------|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 |                  8 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      1 |            0.237812 |            0.781908 |                      1.57266 |       0.996265 |        0.998968 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f |                  9 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      1 |            0.272877 |            0.781908 |                      1.57266 |       0.823901 |        0.998919 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f |                  4 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1                 | L3_liquidity_tier_relative_return  |                      1 |            0.150867 |            0.208748 |                      6.38034 |       0.996553 |        0.999317 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 |                  5 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      8 |            0.612048 |            0.762822 |                      2.09524 |       0.826199 |        0.99991  | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 |                  1 | L5_vol_adjusted_return                                                                                            | 1                 | L5_vol_adjusted_return             |                      1 |            0.721288 |            0.721288 |                      1.81346 |       0.827348 |        0.675194 | True          | basis_premium_root|safe_div_outlier_risk                                   | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 |                  3 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return                        | 1                 | L1_cross_sectional_relative_return |                      1 |            0.226391 |            0.312858 |                      5.80349 |       0.996553 |        0.989336 | True          | basis_premium_root|safe_div_outlier_risk|extreme_value_to_std_ratio_gt_100 | A7FF29_FORENSIC_QUEUE_KEEP |

## A7FF-30 Contract Queue

|   a7ff30_queue_rank | blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          | best_label_family                  |   best_label_horizon_h |   min_control_ratio |   max_control_ratio |   finite_share |   nonzero_share | warning_flags                                                              |
|--------------------:|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|:-----------------------------------|-----------------------:|--------------------:|--------------------:|---------------:|----------------:|:---------------------------------------------------------------------------|
|                   1 | a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 | L5_vol_adjusted_return             |                      1 |            0.237812 |            0.781908 |       0.996265 |        0.998968 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       |
|                   2 | a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f | L5_vol_adjusted_return             |                      1 |            0.272877 |            0.781908 |       0.823901 |        0.998919 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       |
|                   3 | a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f | L3_liquidity_tier_relative_return  |                      1 |            0.150867 |            0.208748 |       0.996553 |        0.999317 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       |
|                   4 | a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 | L5_vol_adjusted_return             |                      8 |            0.612048 |            0.762822 |       0.826199 |        0.99991  | basis_premium_root|extreme_value_to_std_ratio_gt_100                       |
|                   5 | a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 | L5_vol_adjusted_return             |                      1 |            0.721288 |            0.721288 |       0.827348 |        0.675194 | basis_premium_root|safe_div_outlier_risk                                   |
|                   6 | a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 | L1_cross_sectional_relative_return |                      1 |            0.226391 |            0.312858 |       0.996553 |        0.989336 | basis_premium_root|safe_div_outlier_risk|extreme_value_to_std_ratio_gt_100 |

## Concentration Audit

| axis          | value                                 |   count |
|:--------------|:--------------------------------------|--------:|
| semantic_pair | basis_premium_like|volatility_like    |       3 |
| semantic_pair | basis_premium_like|basis_premium_like |       2 |
| semantic_pair | basis_premium_like                    |       1 |
| motif         | safe_div_abs                          |       2 |
| motif         | single                                |       1 |
| motif         | gated_sign                            |       1 |
| motif         | sub                                   |       1 |
| motif         | smooth_mul                            |       1 |

## Control Summary

| blueprint_id             | label_family                       |   label_horizon_h |   max_control_ratio |   median_control_ratio | worst_control                                                                             |
|:-------------------------|:-----------------------------------|------------------:|--------------------:|-----------------------:|:------------------------------------------------------------------------------------------|
| a7ff24r_145e2d58adad4f4a | L0_raw_forward_return              |                 1 |            0.304637 |              0.116399  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L0_raw_forward_return              |                 4 |            1.18948  |              0.286143  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L0_raw_forward_return              |                 8 |            1.5959   |              0.285857  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L0_raw_forward_return              |                24 |          345.375    |              1.14333   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L1_cross_sectional_relative_return |                 1 |            0.226391 |              0.0973658 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L1_cross_sectional_relative_return |                 4 |            1.18948  |              0.254161  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L1_cross_sectional_relative_return |                 8 |            1.5959   |              0.425114  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L1_cross_sectional_relative_return |                24 |          345.375    |              1.91569   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L3_liquidity_tier_relative_return  |                 1 |            0.312858 |              0.0890743 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L3_liquidity_tier_relative_return  |                 4 |            1.54337  |              0.273227  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L3_liquidity_tier_relative_return  |                 8 |            2.26158  |              0.475793  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L3_liquidity_tier_relative_return  |                24 |           16.8458   |              1.09211   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L5_vol_adjusted_return             |                 1 |            0.259274 |              0.103135  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L5_vol_adjusted_return             |                 4 |            1.10112  |              0.171205  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L5_vol_adjusted_return             |                 8 |            1.53828  |              0.376295  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L5_vol_adjusted_return             |                24 |           21.8003   |              0.835344  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L7_ranked_future_return            |                 1 |            0.181083 |              0.0633955 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L7_ranked_future_return            |                 4 |            0.838138 |              0.085237  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L7_ranked_future_return            |                 8 |            2.00631  |              0.332452  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_145e2d58adad4f4a | L7_ranked_future_return            |                24 |           20.2351   |              1.07494   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L0_raw_forward_return              |                 1 |            0.706245 |              0.10193   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L0_raw_forward_return              |                 4 |            1.46432  |              0.383997  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L0_raw_forward_return              |                 8 |            1.12327  |              0.389171  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L0_raw_forward_return              |                24 |            1.2933   |              0.314431  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L1_cross_sectional_relative_return |                 1 |            0.706245 |              0.0993543 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L1_cross_sectional_relative_return |                 4 |            1.05616  |              0.224484  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L1_cross_sectional_relative_return |                 8 |            1.12327  |              0.203303  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L1_cross_sectional_relative_return |                24 |            1.2933   |              0.307962  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L3_liquidity_tier_relative_return  |                 1 |            0.660742 |              0.0873515 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L3_liquidity_tier_relative_return  |                 4 |            0.762822 |              0.18279   | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L3_liquidity_tier_relative_return  |                 8 |            1.03148  |              0.345412  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L3_liquidity_tier_relative_return  |                24 |            1.29744  |              0.328051  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L5_vol_adjusted_return             |                 1 |            0.242105 |              0.0745555 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L5_vol_adjusted_return             |                 4 |            0.665352 |              0.296203  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L5_vol_adjusted_return             |                 8 |            0.612048 |              0.247888  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L5_vol_adjusted_return             |                24 |            1.38624  |              0.264745  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L7_ranked_future_return            |                 1 |            0.290473 |              0.0493816 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L7_ranked_future_return            |                 4 |            0.389661 |              0.131958  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L7_ranked_future_return            |                 8 |            0.386517 |              0.0859189 | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |
| a7ff24r_389e925b81a0c645 | L7_ranked_future_return            |                24 |            0.761888 |              0.217231  | same_family_placebo|symbol_shuffle|time_shuffle|wrong_lag_future_24h|wrong_lag_stale_168h |

## Boundary

```text
The queue is not an alpha proof. It remains concentrated in basis/premium-root candidates.
A7FF-30 may only be a portfolio replay contract on this frozen queue.
No formula search, large search, shadow, paper, or live execution is authorized.
```
