# CRYPTO A7AF-2 Selected-Field Failure Forensic

Generated: 2026-05-22T15:16:34Z

## Decision

```text
HOLD_A7AF2_CONTROL_CONTAMINATION_AND_NO_SIGNAL
```

This stage uses only A7AF-1 artifacts. It runs no new replay and no search.

## Summary

```json
{
  "candidates": 92,
  "controls": 368,
  "decision": "HOLD_A7AF2_CONTROL_CONTAMINATION_AND_NO_SIGNAL",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T15:16:34Z",
  "negative_control_research_like": 3,
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7af2_selected_field_failure_forensic",
  "post_may_eligible_after_core_candidates": 0,
  "pre_may_core_gate_candidates": 0,
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AF2_SELECTED_FIELD_FAILURE_FORENSIC_20260522.md"
}
```

## Authorization

```json
{
  "authorizes_a7af_expanded_replay": false,
  "authorizes_a7ag0_core3_aggtrades_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_core39_selected_field_expansion": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_pre_may_core_gate_candidate",
    "no_post_may_eligible_after_core_gate",
    "negative_control_research_like_penetration",
    "some_candidates_underperform_matched_best_control_recent"
  ],
  "decision": "HOLD_A7AF2_CONTROL_CONTAMINATION_AND_NO_SIGNAL",
  "may_policy": "May remains post-selection stress only; this forensic does not use May for generation, ranking, threshold tuning, or authorization uplift"
}
```

## Bias Audit

- Factor set: fixed A7AF-1 selected core39 metrics / market-structure candidates.
- Run/experiment_id: A7AF-1 smoke, A7AF-2 forensic.
- Data source and universe: Binance core39 all-features metrics v3 + market structure v1; 39 USD-M futures symbols.
- Frequency and horizon: 1h panel, candidate horizons 24/48, ret_1 forward proxy.
- IS/OOS windows: validation 2025H1, recent 2025H2-2026Apr, May 2026 stress-only.
- OOS sample grade: method smoke only; not promotion evidence.
- Cost model: 10bps primary, 20bps severe in A7AF-1.
- Turnover: implicit hourly position change cost in A7AF-1 proxy replay.
- Discovery status: fixed smoke/replay, not formula discovery.

### Findings

- Look-ahead: no May ranking or generation; May is post-selection stress only.
- Date alignment: A7AF-0 contract uses feature available at timestamp + 1h and execution >= next 1h bar; A7AF-1 remains proxy replay, not execution-grade proof.
- Costs/lag: cost20 and lag1 are explicit gates.
- Replay vs discovery: replay smoke only; no KEEP or promotion.

### Decision

HOLD_RESEARCH. The blocker is signal/control quality, not data availability.

## Gate Summary

| gate                          |   pass_count |   total |   pass_rate |
|:------------------------------|-------------:|--------:|------------:|
| gate_raw_validation_positive  |            0 |      92 |   0         |
| gate_raw_recent_positive      |            2 |      92 |   0.0217391 |
| gate_cost20_recent_positive   |            1 |      92 |   0.0108696 |
| gate_lag1_recent_positive     |            2 |      92 |   0.0217391 |
| gate_residual_recent_positive |            2 |      92 |   0.0217391 |
| gate_controls_clean           |           89 |      92 |   0.967391  |
| pre_may_core_gate             |            0 |      92 |   0         |
| post_may_positive             |           20 |      92 |   0.217391  |
| post_may_eligible_after_core  |            0 |      92 |   0         |

## Family Gate Summary

| family                        |   count |   raw_validation_positive |   raw_recent_positive |   cost20_recent_positive |   lag1_recent_positive |   residual_recent_positive |   controls_clean |   pre_may_core_gate |   post_may_positive |   post_may_eligible_after_core |
|:------------------------------|--------:|--------------------------:|----------------------:|-------------------------:|-----------------------:|---------------------------:|-----------------:|--------------------:|--------------------:|-------------------------------:|
| G3_crowding_x_context         |      24 |                         0 |                     2 |                        1 |                      2 |                          2 |               24 |                   0 |                   7 |                              0 |
| G0_basis_premium_dynamic      |      16 |                         0 |                     0 |                        0 |                      0 |                          0 |               16 |                   0 |                   0 |                              0 |
| G1_crowding_x_basis_dynamic   |      24 |                         0 |                     0 |                        0 |                      0 |                          0 |               24 |                   0 |                  11 |                              0 |
| G2_oi_dynamic_x_basis_dynamic |      18 |                         0 |                     0 |                        0 |                      0 |                          0 |               17 |                   0 |                   2 |                              0 |
| G4_oi_change_x_context        |       6 |                         0 |                     0 |                        0 |                      0 |                          0 |                4 |                   0 |                   0 |                              0 |
| G5_funding_basis_benchmark    |       4 |                         0 |                     0 |                        0 |                      0 |                          0 |                4 |                   0 |                   0 |                              0 |

## Reject Reasons

| reject_reason                       |   count |
|:------------------------------------|--------:|
| raw_validation_nonpositive          |      92 |
| cost20_recent_nonpositive           |      91 |
| lag1_recent_nonpositive             |      90 |
| raw_recent_nonpositive              |      90 |
| residual_funding_recent_nonpositive |      90 |
| negative_control_not_dominated      |       3 |

## Negative Control Penetration

| control_id                                                     | base_candidate_id                                   | family                        | control_mode   |   raw_validation_2025H1_ann_10bps_lag0 |   raw_validation_2025H1_sharpe_10bps_lag0 |   raw_validation_2025H1_sum_10bps_lag0 |   raw_validation_2025H1_active_hours_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_sharpe_10bps_lag0 |   raw_recent_2025H2_2026Apr_sum_10bps_lag0 |   raw_recent_2025H2_2026Apr_active_hours_10bps_lag0 |   raw_may_2026_stress_ann_10bps_lag0 |   raw_may_2026_stress_sharpe_10bps_lag0 |   raw_may_2026_stress_sum_10bps_lag0 |   raw_may_2026_stress_active_hours_10bps_lag0 | control_research_like   | expression                                                           | source_fields                                     |   horizon | decision       | reject_reasons                                                                                                                                                         |   raw_validation_2025H1_ann_10bps_lag0_base |   raw_recent_2025H2_2026Apr_ann_10bps_lag0_base |   raw_recent_2025H2_2026Apr_ann_20bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag1 |   raw_may_2026_stress_ann_10bps_lag0_base |   residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0 |   residual_funding_may_2026_stress_ann_10bps_lag0 |
|:---------------------------------------------------------------|:----------------------------------------------------|:------------------------------|:---------------|---------------------------------------:|------------------------------------------:|---------------------------------------:|------------------------------------------------:|-------------------------------------------:|----------------------------------------------:|-------------------------------------------:|----------------------------------------------------:|-------------------------------------:|----------------------------------------:|-------------------------------------:|----------------------------------------------:|:------------------------|:---------------------------------------------------------------------|:--------------------------------------------------|----------:|:---------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------:|------------------------------------------------:|-------------------------------------------:|-------------------------------------------:|------------------------------------------:|--------------------------------------------------------:|--------------------------------------------------:|
| a7af1_G2_oi_dynamic_x_basis_dynamic_48_044e7404996d__sign_flip | a7af1_G2_oi_dynamic_x_basis_dynamic_48_044e7404996d | G2_oi_dynamic_x_basis_dynamic | sign_flip      |                               0.637657 |                                  0.795982 |                               0.316208 |                                            4344 |                                   0.723385 |                                      0.910372 |                                   0.602325 |                                                7294 |                             -5.15151 |                                -13.3915 |                            -0.296388 |                                           504 | True                    | Mul(ZScore(open_interest_change_24h),Rank(premium_index_change_24h)) | open_interest_change_24h;premium_index_change_24h |        48 | A7AF1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -12.4442 |                                       -12.0319  |                                   -17.6862 |                                  -11.8386  |                                  -6.97182 |                                               -11.9823  |                                          -6.88097 |
| a7af1_G4_oi_change_x_context_48_105456a9a4c3__sign_flip        | a7af1_G4_oi_change_x_context_48_105456a9a4c3        | G4_oi_change_x_context        | sign_flip      |                               8.84004  |                                  5.39397  |                               4.38369  |                                            4344 |                                   4.39575  |                                      3.53772  |                                   3.66011  |                                                7294 |                            -11.1097  |                                -10.138  |                            -0.63919  |                                           504 | True                    | Mul(ZScore(open_interest_change_24h),Rank(ret_24))                   | open_interest_change_24h;ret_24                   |        48 | A7AF1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -14.2975 |                                        -9.54815 |                                   -12.1244 |                                   -9.85673 |                                   6.28025 |                                                -8.34097 |                                          -1.72701 |
| a7af1_G4_oi_change_x_context_48_044e7404996d__sign_flip        | a7af1_G4_oi_change_x_context_48_044e7404996d        | G4_oi_change_x_context        | sign_flip      |                               0.637657 |                                  0.795982 |                               0.316208 |                                            4344 |                                   0.723385 |                                      0.910372 |                                   0.602325 |                                                7294 |                             -5.15151 |                                -13.3915 |                            -0.296388 |                                           504 | True                    | Mul(ZScore(open_interest_change_24h),Rank(premium_index_change_24h)) | open_interest_change_24h;premium_index_change_24h |        48 | A7AF1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -12.4442 |                                       -12.0319  |                                   -17.6862 |                                  -11.8386  |                                  -6.97182 |                                               -11.9823  |                                          -6.88097 |

## Control Mode Summary

| family                        | control_mode        | control_research_like   |   count |
|:------------------------------|:--------------------|:------------------------|--------:|
| G4_oi_change_x_context        | sign_flip           | True                    |       2 |
| G2_oi_dynamic_x_basis_dynamic | sign_flip           | True                    |       1 |
| G1_crowding_x_basis_dynamic   | row_shuffle         | False                   |      24 |
| G1_crowding_x_basis_dynamic   | sign_flip           | False                   |      24 |
| G1_crowding_x_basis_dynamic   | time_shuffle        | False                   |      24 |
| G1_crowding_x_basis_dynamic   | wrong_lag_stale_24h | False                   |      24 |
| G3_crowding_x_context         | row_shuffle         | False                   |      24 |
| G3_crowding_x_context         | sign_flip           | False                   |      24 |
| G3_crowding_x_context         | time_shuffle        | False                   |      24 |
| G3_crowding_x_context         | wrong_lag_stale_24h | False                   |      24 |
| G2_oi_dynamic_x_basis_dynamic | row_shuffle         | False                   |      18 |
| G2_oi_dynamic_x_basis_dynamic | time_shuffle        | False                   |      18 |
| G2_oi_dynamic_x_basis_dynamic | wrong_lag_stale_24h | False                   |      18 |
| G2_oi_dynamic_x_basis_dynamic | sign_flip           | False                   |      17 |
| G0_basis_premium_dynamic      | row_shuffle         | False                   |      16 |
| G0_basis_premium_dynamic      | sign_flip           | False                   |      16 |
| G0_basis_premium_dynamic      | time_shuffle        | False                   |      16 |
| G0_basis_premium_dynamic      | wrong_lag_stale_24h | False                   |      16 |
| G4_oi_change_x_context        | row_shuffle         | False                   |       6 |
| G4_oi_change_x_context        | time_shuffle        | False                   |       6 |
| G4_oi_change_x_context        | wrong_lag_stale_24h | False                   |       6 |
| G4_oi_change_x_context        | sign_flip           | False                   |       4 |
| G5_funding_basis_benchmark    | row_shuffle         | False                   |       4 |
| G5_funding_basis_benchmark    | sign_flip           | False                   |       4 |
| G5_funding_basis_benchmark    | time_shuffle        | False                   |       4 |
| G5_funding_basis_benchmark    | wrong_lag_stale_24h | False                   |       4 |

## Recent-Rank Decile vs May Alignment

|   recent_decile |   count |   raw_recent_mean |   post_may_positive_count |   post_may_positive_rate |   pre_may_core_gate_count |   control_contaminated_count |
|----------------:|--------:|------------------:|--------------------------:|-------------------------:|--------------------------:|-----------------------------:|
|               1 |       9 |          -2.21727 |                         0 |                 0        |                         0 |                            0 |
|               2 |       9 |          -6.00763 |                         0 |                 0        |                         0 |                            0 |
|               3 |       9 |          -7.68095 |                         2 |                 0.222222 |                         0 |                            0 |
|               4 |       9 |          -8.27905 |                         7 |                 0.777778 |                         0 |                            0 |
|               5 |      10 |          -8.45778 |                         9 |                 0.9      |                         0 |                            0 |
|               6 |       9 |          -9.04022 |                         0 |                 0        |                         0 |                            0 |
|               7 |       9 |          -9.67589 |                         0 |                 0        |                         0 |                            1 |
|               8 |       9 |         -10.4869  |                         0 |                 0        |                         0 |                            0 |
|               9 |       9 |         -11.7009  |                         2 |                 0.222222 |                         0 |                            0 |
|              10 |      10 |         -12.4282  |                         0 |                 0        |                         0 |                            2 |

## Weak-Prior Registry

| registry_item                                         | type                  | status                              | reason                                                    |   count |   pre_may_core_gate |   post_may_eligible_after_core |
|:------------------------------------------------------|:----------------------|:------------------------------------|:----------------------------------------------------------|--------:|--------------------:|-------------------------------:|
| G3_crowding_x_context                                 | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |      24 |                   0 |                              0 |
| G0_basis_premium_dynamic                              | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |      16 |                   0 |                              0 |
| G1_crowding_x_basis_dynamic                           | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |      24 |                   0 |                              0 |
| G2_oi_dynamic_x_basis_dynamic                         | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |      18 |                   0 |                              0 |
| G4_oi_change_x_context                                | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |       6 |                   0 |                              0 |
| G5_funding_basis_benchmark                            | family                | blocked_for_expansion               | no_pre_may_core_gate                                      |       4 |                   0 |                              0 |
| G2_oi_dynamic_x_basis_dynamic::sign_flip              | control_contamination | blocked_for_expansion               | negative_control_research_like                            |       1 |                 nan |                            nan |
| G4_oi_change_x_context::sign_flip                     | control_contamination | blocked_for_expansion               | negative_control_research_like                            |       1 |                 nan |                            nan |
| G4_oi_change_x_context::sign_flip                     | control_contamination | blocked_for_expansion               | negative_control_research_like                            |       1 |                 nan |                            nan |
| core39_metrics_market_structure_selected_fields_a7af1 | route                 | do_not_expand_without_new_objective | zero_control_clean_clues_and_negative_control_penetration |      92 |                   0 |                              0 |

## Required Next Action

- Do not expand A7AF core39 selected-field replay.
- Do not run formula search on this selected-field family.
- Keep funding/crowding/basis fields as control/context inputs until a new objective is defined.
- The only authorized next step from this line is A7AG-0 core3 aggTrades interaction contract, not alpha promotion.
