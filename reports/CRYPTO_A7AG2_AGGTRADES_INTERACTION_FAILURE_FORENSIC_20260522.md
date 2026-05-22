# CRYPTO A7AG-2 aggTrades Interaction Failure Forensic

Generated: 2026-05-22T15:24:16Z

## Decision

```text
HOLD_A7AG2_PRE_MAY_ONLY_AND_CONTROL_CONTAMINATION
```

This stage uses only A7AG-1 artifacts. It runs no new replay and no search.

## Summary

```json
{
  "candidates": 90,
  "controls": 360,
  "decision": "HOLD_A7AG2_PRE_MAY_ONLY_AND_CONTROL_CONTAMINATION",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T15:24:16Z",
  "negative_control_research_like": 3,
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ag2_aggtrades_interaction_failure_forensic",
  "post_may_eligible_after_core_candidates": 0,
  "pre_may_core_gate_candidates": 1,
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AG2_AGGTRADES_INTERACTION_FAILURE_FORENSIC_20260522.md"
}
```

## Authorization

```json
{
  "authorizes_a7ag_expanded_replay": false,
  "authorizes_aggtrades_interaction_expansion": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_post_may_eligible_after_core_gate",
    "negative_control_research_like_penetration",
    "pre_may_clue_fails_may_stress"
  ],
  "decision": "HOLD_A7AG2_PRE_MAY_ONLY_AND_CONTROL_CONTAMINATION",
  "may_policy": "May remains post-selection stress only; no May ranking or symbol tuning",
  "suggested_next": "wait_for_core12_rem9_aggtrades_or_define_new_non_1h_objective_contract"
}
```

## Gate Summary

| gate                          |   pass_count |   total |   pass_rate |
|:------------------------------|-------------:|--------:|------------:|
| gate_raw_validation_positive  |            8 |      90 |   0.0888889 |
| gate_raw_recent_positive      |            7 |      90 |   0.0777778 |
| gate_cost20_recent_positive   |            2 |      90 |   0.0222222 |
| gate_lag1_recent_positive     |            7 |      90 |   0.0777778 |
| gate_lag2_recent_positive     |            7 |      90 |   0.0777778 |
| gate_residual_recent_positive |            1 |      90 |   0.0111111 |
| gate_controls_clean           |           87 |      90 |   0.966667  |
| pre_may_core_gate             |            1 |      90 |   0.0111111 |
| post_may_positive             |           16 |      90 |   0.177778  |
| post_may_eligible_after_core  |            0 |      90 |   0         |

## Family Gate Summary

| family                     |   count |   pre_may_core_gate |   post_may_positive |   post_may_eligible_after_core |   raw_recent_positive |   cost20_recent_positive |   lag2_recent_positive |   residual_recent_positive |   control_contaminated |
|:---------------------------|--------:|--------------------:|--------------------:|-------------------------------:|----------------------:|-------------------------:|-----------------------:|---------------------------:|-----------------------:|
| H0_agg_flow_x_context      |      64 |                   1 |                  12 |                              0 |                     1 |                        1 |                      1 |                          1 |                      0 |
| H1_large_trade_x_context   |      18 |                   0 |                   4 |                              0 |                     6 |                        1 |                      6 |                          0 |                      0 |
| H2_flow_x_crowding         |       6 |                   0 |                   0 |                              0 |                     0 |                        0 |                      0 |                          0 |                      3 |
| H3_flow_pressure_benchmark |       2 |                   0 |                   0 |                              0 |                     0 |                        0 |                      0 |                          0 |                      0 |

## Reject Reasons

| reject_reason                       |   count |
|:------------------------------------|--------:|
| residual_funding_recent_nonpositive |      89 |
| cost20_recent_nonpositive           |      88 |
| lag1_recent_nonpositive             |      83 |
| lag2_recent_nonpositive             |      83 |
| raw_recent_nonpositive              |      83 |
| raw_validation_nonpositive          |      82 |
| negative_control_not_dominated      |       3 |
| may_stress_not_positive             |       1 |

## Shortlist Forensic

| candidate_id                                | family                | expression                                                   |   horizon |   raw_validation_2025H1_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_20bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag1 |   raw_recent_2025H2_2026Apr_ann_10bps_lag2 |   raw_may_2026_stress_ann_10bps_lag0 |   residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0 |   residual_funding_may_2026_stress_ann_10bps_lag0 |   control_research_like_count | decision                | reject_reasons          |
|:--------------------------------------------|:----------------------|:-------------------------------------------------------------|----------:|---------------------------------------:|-------------------------------------------:|-------------------------------------------:|-------------------------------------------:|-------------------------------------------:|-------------------------------------:|--------------------------------------------------------:|--------------------------------------------------:|------------------------------:|:------------------------|:------------------------|
| a7ag1_H0_agg_flow_x_context_48_176b5ddf86de | H0_agg_flow_x_context | Mul(Neg(Rank(agg_flow_imbalance_notional_24h)),Rank(ret_24)) |        48 |                                8.64429 |                                    2.87991 |                                   0.401819 |                                    3.08605 |                                    3.46212 |                             -17.4719 |                                                 1.72304 |                                          -7.33138 |                             0 | A7AG1_PRE_MAY_ONLY_CLUE | may_stress_not_positive |

## Negative Control Penetration

| control_id                                          | base_candidate_id                        | family             | control_mode   |   raw_validation_2025H1_ann_10bps_lag0 |   raw_validation_2025H1_sharpe_10bps_lag0 |   raw_validation_2025H1_sum_10bps_lag0 |   raw_validation_2025H1_active_hours_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_sharpe_10bps_lag0 |   raw_recent_2025H2_2026Apr_sum_10bps_lag0 |   raw_recent_2025H2_2026Apr_active_hours_10bps_lag0 |   raw_may_2026_stress_ann_10bps_lag0 |   raw_may_2026_stress_sharpe_10bps_lag0 |   raw_may_2026_stress_sum_10bps_lag0 |   raw_may_2026_stress_active_hours_10bps_lag0 | control_research_like   | expression                                                                                        | source_fields                                                             |   horizon | decision       | reject_reasons                                                                                                                                                                                 |   raw_validation_2025H1_ann_10bps_lag0_base |   raw_recent_2025H2_2026Apr_ann_10bps_lag0_base |   raw_may_2026_stress_ann_10bps_lag0_base |   residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0 |   residual_funding_may_2026_stress_ann_10bps_lag0 |
|:----------------------------------------------------|:-----------------------------------------|:-------------------|:---------------|---------------------------------------:|------------------------------------------:|---------------------------------------:|------------------------------------------------:|-------------------------------------------:|----------------------------------------------:|-------------------------------------------:|----------------------------------------------------:|-------------------------------------:|----------------------------------------:|-------------------------------------:|----------------------------------------------:|:------------------------|:--------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------|----------:|:---------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------:|------------------------------------------------:|------------------------------------------:|--------------------------------------------------------:|--------------------------------------------------:|
| a7ag1_H2_flow_x_crowding_48_d7e6bbc6972e__sign_flip | a7ag1_H2_flow_x_crowding_48_d7e6bbc6972e | H2_flow_x_crowding | sign_flip      |                                5.45703 |                                   3.12447 |                                2.70609 |                                            4344 |                                   0.218791 |                                      0.168643 |                                   0.182226 |                                                7296 |                              41.2616 |                                 33.6634 |                              2.26091 |                                           480 | True                    | Mul(Rank(agg_signed_flow_z_24h),Neg(ZScore(top_long_short_position_ratio_zscore_168h)))           | agg_signed_flow_z_24h;top_long_short_position_ratio_zscore_168h           |        48 | A7AG1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;lag2_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -11.3785 |                                        -5.58434 |                                  -45.4531 |                                                -5.01273 |                                          -20.8071 |
| a7ag1_H2_flow_x_crowding_48_96e374aa3750__sign_flip | a7ag1_H2_flow_x_crowding_48_96e374aa3750 | H2_flow_x_crowding | sign_flip      |                                7.17941 |                                   4.1938  |                                3.5602  |                                            4344 |                                   2.0633   |                                      1.6021   |                                   1.71847  |                                                7296 |                              43.7918 |                                 35.4329 |                              2.39955 |                                           480 | True                    | Mul(Rank(agg_flow_imbalance_notional_24h),Neg(ZScore(top_long_short_position_ratio_zscore_168h))) | agg_flow_imbalance_notional_24h;top_long_short_position_ratio_zscore_168h |        48 | A7AG1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;lag2_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -11.1802 |                                        -5.57401 |                                  -45.9551 |                                                -7.5006  |                                          -20.74   |
| a7ag1_H2_flow_x_crowding_48_cea05bc1ebb3__sign_flip | a7ag1_H2_flow_x_crowding_48_cea05bc1ebb3 | H2_flow_x_crowding | sign_flip      |                                6.55875 |                                   3.77597 |                                3.25242 |                                            4344 |                                   0.77421  |                                      0.598407 |                                   0.644822 |                                                7296 |                              42.8331 |                                 34.8922 |                              2.34702 |                                           480 | True                    | Mul(Rank(agg_flow_accel_4h_vs_24h),Neg(ZScore(top_long_short_position_ratio_zscore_168h)))        | agg_flow_accel_4h_vs_24h;top_long_short_position_ratio_zscore_168h        |        48 | A7AG1_REJECTED | cost20_recent_nonpositive;lag1_recent_nonpositive;lag2_recent_nonpositive;negative_control_not_dominated;raw_recent_nonpositive;raw_validation_nonpositive;residual_funding_recent_nonpositive |                                    -11.244  |                                        -5.01953 |                                  -46.1686 |                                                -4.16388 |                                          -19.8328 |

## Recent-Rank Decile vs May Alignment

|   recent_decile |   count |   raw_recent_mean |   post_may_positive_count |   pre_may_core_gate_count |   control_contaminated_count |
|----------------:|--------:|------------------:|--------------------------:|--------------------------:|-----------------------------:|
|               1 |       9 |           1.03562 |                         6 |                         1 |                            0 |
|               2 |       9 |          -1.68837 |                         2 |                         0 |                            0 |
|               3 |       9 |          -2.7011  |                         2 |                         0 |                            0 |
|               4 |       9 |          -3.62851 |                         1 |                         0 |                            0 |
|               5 |       9 |          -4.88127 |                         2 |                         0 |                            2 |
|               6 |       9 |          -6.14351 |                         1 |                         0 |                            1 |
|               7 |       9 |          -7.58953 |                         2 |                         0 |                            0 |
|               8 |       9 |          -8.41297 |                         0 |                         0 |                            0 |
|               9 |       9 |          -9.63411 |                         0 |                         0 |                            0 |
|              10 |       9 |         -11.7673  |                         0 |                         0 |                            0 |

## Required Next Action

- Do not expand A7AG core3 aggTrades interaction replay.
- Do not promote the pre-May clue; it fails May stress.
- Do not use H2 flow x crowding until sign-flip control contamination is resolved.
- Next valid work is either core12 rem9 aggTrades source completion audit or a new non-1h objective/horizon contract.
