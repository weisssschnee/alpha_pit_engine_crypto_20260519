# CRYPTO A7FF-CORE15Y REPLAY-STABILITY OBJECTIVE SURFACE

Generated: 2026-06-01T07:58:42Z

## Decision

`HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT`

A7FF-CORE15Y builds a replay-stability objective surface from existing numeric/replay/forensic rows. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15z": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "surface_candidate_count_lt_32",
    "semantic_bucket_count_lt_5",
    "motif_bucket_count_lt_4",
    "top_family_share_gt_35pct"
  ],
  "decision": "HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T07:58:42Z",
  "next_allowed": "A7FF-CORE15YR objective-surface failure repair",
  "source_decision": "PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y",
  "source_stage": "A7FF-CORE15X",
  "stage": "A7FF-CORE15Y",
  "surface_candidate_count": 4,
  "surface_motif_bucket_count": 2,
  "surface_row_count": 256,
  "surface_semantic_bucket_count": 2,
  "top_family_share": 0.75
}
```

## Family Scorecard

| source                    | semantic_bucket                      | motif_bucket       |   candidate_count |   surface_candidate_count |   median_surface_score |   median_control_ratio |   median_cost_adjusted_spread |
|:--------------------------|:-------------------------------------|:-------------------|------------------:|--------------------------:|-----------------------:|-----------------------:|------------------------------:|
| core14e_original_packet   | liquidity_like\|volatility_like      | liquidity_shock    |                28 |                         2 |               1.01676  |                1.47976 |                  -0.000962569 |
| core14see_repaired_packet | liquidity_like\|volatility_like      | liquidity_shock    |                25 |                         1 |               1.27617  |                1.86411 |                  -0.000869653 |
| core14see_repaired_packet | taker_flow_like\|basis_premium_like  | gated_sign         |                25 |                         1 |              -0.713828 |                2.81693 |                  -0.000619951 |
| core14e_original_packet   | open_interest_like\|positioning_like | delta_x_divergence |                28 |                         0 |              -2.41649  |                3.02504 |                  -0.000899898 |
| core14see_repaired_packet | open_interest_like\|positioning_like | delta_x_divergence |                25 |                         0 |              -0.683089 |                3.58639 |                  -0.000825792 |
| core14see_repaired_packet | taker_flow_like\|open_interest_like  | flow_x_leverage    |                25 |                         0 |               0.260238 |                2.64465 |                  -0.00108206  |
| core14e_original_packet   | taker_flow_like\|basis_premium_like  | gated_sign         |                24 |                         0 |              -0.882379 |                3.44304 |                  -0.000648944 |
| core14e_original_packet   | taker_flow_like\|open_interest_like  | flow_x_leverage    |                24 |                         0 |              -1.6758   |                2.74259 |                  -0.001062    |
| core14see_repaired_packet | liquidity_like                       | single             |                23 |                         0 |              -3.83779  |                4.54086 |                  -0.00119274  |
| core14e_original_packet   | liquidity_like                       | single             |                20 |                         0 |              -1.91251  |                3.3943  |                  -0.00111708  |
| core14see_repaired_packet | open_interest_like                   | single             |                 5 |                         0 |              -1.41552  |                3.0913  |                  -0.000992103 |
| core14e_original_packet   | open_interest_like                   | single             |                 4 |                         0 |              -4.20717  |                5.39583 |                  -0.00106419  |

## Surface Candidates

| candidate_id                   | semantic_bucket                     | motif_bucket    |   split_count |   strict_split_count |   positive_split_count |   control_clean_split_count |   median_cost_adjusted_spread |   median_control_ratio |   max_tstat | control_clean_recent   | control_clean_train   | control_clean_validation   | positive_recent   | positive_train   | positive_validation   | strict_recent   | strict_train   | strict_validation   | source                    | split_stable_proxy   |   surface_score |   numeric_clue_rows |   numeric_label_count |   numeric_horizon_count |   numeric_min_control_ratio |   numeric_best_original_score | objective_surface_candidate   |
|:-------------------------------|:------------------------------------|:----------------|--------------:|---------------------:|-----------------------:|----------------------------:|------------------------------:|-----------------------:|------------:|:-----------------------|:----------------------|:---------------------------|:------------------|:-----------------|:----------------------|:----------------|:---------------|:--------------------|:--------------------------|:---------------------|----------------:|--------------------:|----------------------:|------------------------:|----------------------------:|------------------------------:|:------------------------------|
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like | gated_sign      |             3 |                    2 |                      2 |                           2 |                   2.97212e-05 |               0.832834 |     2.85705 | True                   | False                 | True                       | True              | False            | True                  | True            | False          | True                | core14see_repaired_packet | True                 |         16.0242 |                   4 |                     3 |                       3 |                    0.549227 |                     0.0868757 | True                          |
| a7ffcore11e_2a2d48956a572ac1ab | liquidity_like\|volatility_like     | liquidity_shock |             3 |                    2 |                      3 |                           2 |                   0.0362133   |               0.93515  |     1.18513 | True                   | True                  | False                      | True              | True             | True                  | True            | True           | False               | core14see_repaired_packet | True                 |         15.75   |                   4 |                     3 |                       3 |                    0.217611 |                     0.454002  | True                          |
| a7ffcore11e_34c80c6d72709214b6 | liquidity_like\|volatility_like     | liquidity_shock |             3 |                    2 |                      2 |                           2 |                   0.000480064 |               0.818117 |     2.48624 | True                   | False                 | True                       | True              | False            | True                  | True            | False          | True                | core14e_original_packet   | True                 |         15.6681 |                   6 |                     3 |                       4 |                    0.494815 |                     0.354532  | True                          |
| a7ffcore11e_47e7feb2ae3fd724af | liquidity_like\|volatility_like     | liquidity_shock |             3 |                    2 |                      2 |                           2 |                   0.000704919 |               0.948511 |     2.30997 | True                   | False                 | True                       | True              | False            | True                  | True            | False          | True                | core14e_original_packet   | True                 |         15.3615 |                   4 |                     3 |                       3 |                    0.568381 |                     0.373251  | True                          |
