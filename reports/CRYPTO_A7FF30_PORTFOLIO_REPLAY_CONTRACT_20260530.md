# CRYPTO A7FF-30 PORTFOLIO REPLAY CONTRACT

Generated: 2026-05-30T10:20:04Z

## Decision

`PASS_A7FF30_PORTFOLIO_REPLAY_CONTRACT_READY_NO_SEARCH_AUTH`

A7FF-30 defines portfolio replay rules for the frozen A7FF-29 six-candidate queue. It does not execute replay, generate formulas, run search, or prove alpha.

## Experiment Record

```text
experiment_id: 20260530_a7ff30_portfolio_replay_contract
objective: define a bounded portfolio replay for the six non-L7 candidates without search or learned weights
input: runtime/a7ff29_candidate_forensic/a7ff29_a7ff30_portfolio_replay_contract_queue.csv
parameters: equal candidate weights only; 2/5/10 bps cost stress; concentration and leave-one-out required
```

## Manifest

```json
{
  "authorizes_a7ff30a_portfolio_replay_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 6,
  "decision": "PASS_A7FF30_PORTFOLIO_REPLAY_CONTRACT_READY_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T10:20:04Z",
  "prior_decision": "PASS_A7FF29_FORENSIC_READY_FOR_A7FF30_PORTFOLIO_REPLAY_CONTRACT_WITH_CONCENTRATION_WARNINGS_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-29",
  "semantic_pair_count": 3,
  "stage": "A7FF-30",
  "warnings": [
    "all_candidates_have_basis_premium_root",
    "safe_div_outlier_risk_present"
  ]
}
```

## Frozen Queue

|   a7ff30_queue_rank | blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          | best_label_family                  |   best_label_horizon_h |   min_control_ratio |   max_control_ratio |   finite_share |   nonzero_share | warning_flags                                                              | portfolio_replay_allowed   | weight_policy               | search_allowed   |
|--------------------:|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|:-----------------------------------|-----------------------:|--------------------:|--------------------:|---------------:|----------------:|:---------------------------------------------------------------------------|:---------------------------|:----------------------------|:-----------------|
|                   1 | a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 | L5_vol_adjusted_return             |                      1 |            0.237812 |            0.781908 |       0.996265 |        0.998968 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | True                       | equal_candidate_weight_only | False            |
|                   2 | a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f | L5_vol_adjusted_return             |                      1 |            0.272877 |            0.781908 |       0.823901 |        0.998919 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | True                       | equal_candidate_weight_only | False            |
|                   3 | a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f | L3_liquidity_tier_relative_return  |                      1 |            0.150867 |            0.208748 |       0.996553 |        0.999317 | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | True                       | equal_candidate_weight_only | False            |
|                   4 | a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 | L5_vol_adjusted_return             |                      8 |            0.612048 |            0.762822 |       0.826199 |        0.99991  | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | True                       | equal_candidate_weight_only | False            |
|                   5 | a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 | L5_vol_adjusted_return             |                      1 |            0.721288 |            0.721288 |       0.827348 |        0.675194 | basis_premium_root|safe_div_outlier_risk                                   | True                       | equal_candidate_weight_only | False            |
|                   6 | a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 | L1_cross_sectional_relative_return |                      1 |            0.226391 |            0.312858 |       0.996553 |        0.989336 | basis_premium_root|safe_div_outlier_risk|extreme_value_to_std_ratio_gt_100 | True                       | equal_candidate_weight_only | False            |

## Replay Modes

| mode                        | description                                                                                         | required_outputs                                                                  |
|:----------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
| equal_weight_top_bottom     | rank signal cross-sectionally each hour; long top bucket, short bottom bucket; equal symbol weights | gross/net spread; turnover; cost2/5/10; symbol/month/state concentration          |
| liquidity_capped_top_bottom | same as equal-weight but cap symbol weights by liquidity tier and active universe size              | gross/net spread; liquidity-cap hit rate; top weight concentration                |
| candidate_ensemble_equal    | average normalized ranks across the 6 frozen candidates; no learned weights                         | ensemble gross/net spread; candidate marginal contribution; candidate correlation |
| candidate_leave_one_out     | remove one candidate at a time from ensemble to estimate marginal contribution                      | delta net spread; delta tstat; concentration change                               |

## Gates

| gate                  | rule                                                                                              | hard   |
|:----------------------|:--------------------------------------------------------------------------------------------------|:-------|
| frozen_queue_only     | input must be runtime/a7ff29_candidate_forensic/a7ff29_a7ff30_portfolio_replay_contract_queue.csv | True   |
| no_weight_learning    | no trained weights; equal candidate ensemble only                                                 | True   |
| non_l7_only           | ranked-return diagnostic rows are excluded                                                        | True   |
| control_clean         | reject any candidate with max_control_ratio >= 1.0; warn >= 0.8                                   | True   |
| cost_stress           | report 2/5/10 bps net proxies; no promotion if cost2 collapses                                    | True   |
| concentration         | report symbol, month, semantic pair, skeleton, liquidity tier, and latent-state concentration     | True   |
| basis_premium_warning | basis/premium-root concentration is a warning; do not generalize to broad crypto alpha            | True   |
| no_may_selector       | May/stress remains post-selection attribution only                                                | True   |

## Risk Register

| risk                             | observed   | mitigation                                                            |
|:---------------------------------|:-----------|:----------------------------------------------------------------------|
| basis_premium_root_concentration | True       | portfolio replay must report this as a family concentration warning   |
| safe_div_outlier                 | True       | replay must report winsorized and raw variants side by side           |
| single_label_family              | False      | report per-label and ensemble results; no promotion on one label only |

## Prior Forensic

| blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          |   non_l7_clue_rows | non_l7_label_families                                                                                             | non_l7_horizons   | best_label_family                  |   best_label_horizon_h |   min_control_ratio |   max_control_ratio |   min_robust_min_tstat_floor |   finite_share |   nonzero_share | activity_ok   | warning_flags                                                              | forensic_decision          |
|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|-------------------:|:------------------------------------------------------------------------------------------------------------------|:------------------|:-----------------------------------|-----------------------:|--------------------:|--------------------:|-----------------------------:|---------------:|----------------:|:--------------|:---------------------------------------------------------------------------|:---------------------------|
| a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 |                  8 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      1 |            0.237812 |            0.781908 |                      1.57266 |       0.996265 |        0.998968 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f |                  9 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      1 |            0.272877 |            0.781908 |                      1.57266 |       0.823901 |        0.998919 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f |                  4 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1                 | L3_liquidity_tier_relative_return  |                      1 |            0.150867 |            0.208748 |                      6.38034 |       0.996553 |        0.999317 | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 |                  5 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return | 1|4|8             | L5_vol_adjusted_return             |                      8 |            0.612048 |            0.762822 |                      2.09524 |       0.826199 |        0.99991  | True          | basis_premium_root|extreme_value_to_std_ratio_gt_100                       | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 |                  1 | L5_vol_adjusted_return                                                                                            | 1                 | L5_vol_adjusted_return             |                      1 |            0.721288 |            0.721288 |                      1.81346 |       0.827348 |        0.675194 | True          | basis_premium_root|safe_div_outlier_risk                                   | A7FF29_FORENSIC_QUEUE_KEEP |
| a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 |                  3 | L0_raw_forward_return|L1_cross_sectional_relative_return|L3_liquidity_tier_relative_return                        | 1                 | L1_cross_sectional_relative_return |                      1 |            0.226391 |            0.312858 |                      5.80349 |       0.996553 |        0.989336 | True          | basis_premium_root|safe_div_outlier_risk|extreme_value_to_std_ratio_gt_100 | A7FF29_FORENSIC_QUEUE_KEEP |

## Boundary

```text
A7FF-30 authorizes only A7FF-30A portfolio replay smoke on the frozen queue.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
