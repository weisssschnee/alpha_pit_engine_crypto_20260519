# Crypto A7O-L1W1R Policy Repair And Reclassification

- generated_at: `2026-05-20T17:37:53Z`
- decision: `HOLD_A7O_L1W1R`
- executes_new_search: `False`
- executes_replay: `False`
- authorizes_w2: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `['negative_control_research_like_v2', 'strict_negative_control_research_like_v2', 'control_contaminated_cells', 'wave_post_may_eligible_deep_survivors_v2', 'wave_post_may_eligible_rate_v2', 'reselected_post_may_eligible_deep_survivors_v3', 'reselected_post_may_eligible_rate_v3', 'stress_gate_v3_active_hour_count_unavailable']`

## Checkpoint Summary V2

|   checkpoint_id |   deep_audit_selected |   post_may_eligible_deep_survivors_v2 |   post_may_eligible_rate_v2 |   negative_control_research_like_v2 |   liquidity_volatility_deep_share |   single_return_corr_cluster_share |   active_cells_with_valid_deep_audit | decision_v2                  |
|----------------:|----------------------:|--------------------------------------:|----------------------------:|------------------------------------:|----------------------------------:|-----------------------------------:|-------------------------------------:|:-----------------------------|
|              01 |                   192 |                                    12 |                   0.0625    |                                   0 |                          0.145833 |                          0.0520833 |                                   62 | PASS_RECLASSIFIED_CHECKPOINT |
|              02 |                   192 |                                    24 |                   0.125     |                                   0 |                          0.140625 |                          0.0416667 |                                   64 | PASS_RECLASSIFIED_CHECKPOINT |
|              03 |                   192 |                                     8 |                   0.0416667 |                                   0 |                          0.09375  |                          0.046875  |                                   64 | PASS_RECLASSIFIED_CHECKPOINT |
|              04 |                   192 |                                     8 |                   0.0416667 |                                   2 |                          0.145833 |                          0.0833333 |                                   63 | HOLD_NEGATIVE_CONTROL        |
|              05 |                   192 |                                    11 |                   0.0572917 |                                   0 |                          0.145833 |                          0.03125   |                                   62 | PASS_RECLASSIFIED_CHECKPOINT |
|              06 |                   192 |                                    13 |                   0.0677083 |                                   0 |                          0.145833 |                          0.0572917 |                                   58 | PASS_RECLASSIFIED_CHECKPOINT |

## Artifact Staleness Audit

|   checkpoint_id | artifact                                                                                                                  |   stored_post_may_eligible |   stress_gate_v2_post_may_eligible | stale   |
|----------------:|:--------------------------------------------------------------------------------------------------------------------------|---------------------------:|-----------------------------------:|:--------|
|              01 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_pilot\a7o_l1_pilot_checkpoint_decision.json                 |                         49 |                                 12 | True    |
|              02 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_02\a7o_l1_checkpoint_02_checkpoint_decision.json |                         54 |                                 24 | True    |
|              03 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_03\a7o_l1_checkpoint_03_checkpoint_decision.json |                          8 |                                  8 | False   |
|              04 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_04\a7o_l1_checkpoint_04_checkpoint_decision.json |                          8 |                                  8 | False   |
|              05 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_05\a7o_l1_checkpoint_05_checkpoint_decision.json |                         11 |                                 11 | False   |
|              06 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_06\a7o_l1_checkpoint_06_checkpoint_decision.json |                         13 |                                 13 | False   |

## Negative-Control Forensic

|   checkpoint_id | candidate_id      | stress_gate_v2_reasons   | cell_id   | signal_mode         | expression                                                                                                                                                                          | hypothesis_family            | feature_family_set   | operator_motif           | temporal_horizon_class   | normalization_scope   | residualization_target   | source_field_families   |   pilot_rank_score |   raw_10bp__validation_2025H1 |   raw_10bp__recent_oos_2025H2_2026Apr |   raw_20bp__recent_oos_2025H2_2026Apr |   execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr |   residual_vs_funding_10bp__recent_oos_2025H2_2026Apr |   residual_vs_core4_10bp__recent_oos_2025H2_2026Apr |   raw_10bp__fresh_forward_2026May |   raw_10bp__fresh_forward_2026May__gross_exposure |   residual_vs_funding_10bp__fresh_forward_2026May |   residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure | return_corr_cluster   |
|----------------:|:------------------|:-------------------------|:----------|:--------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------|:---------------------|:-------------------------|:-------------------------|:----------------------|:-------------------------|:------------------------|-------------------:|------------------------------:|--------------------------------------:|--------------------------------------:|---------------------------------------------------------:|------------------------------------------------------:|----------------------------------------------------:|----------------------------------:|--------------------------------------------------:|--------------------------------------------------:|------------------------------------------------------------------:|:----------------------|
|              04 | a7o_l1_C0208_1344 |                          | C0208     | wrong_lag_stale_24h | Neg(Clip(cross_symbol_rank(TSMean(ResidualizeVsCore4(Mul(Rank(TSMean(quote_volume_mean_24,36)),ZScore(TSMean(realized_vol_24,48)))),84)),-4.0,4.0))                                 | H15_placebo_null_adversarial | P8_regime_state      | ResidualizeVsCore4       | H24                      | cross_symbol_rank     | none                     | liquidity;volatility    |          -0.138524 |                      0.942723 |                              2.12268  |                              2.09608  |                                                 2.12982  |                                               4.82656 |                                             4.734   |                          1.25707  |                                          0.497625 |                                            5.1567 |                                                          0.497625 | rc_046                |
|              04 | a7o_l1_C0223_0289 |                          | C0223     | wrong_lag_stale_24h | Neg(TSMean(ResidualizeVsCore4(Add(Abs(ZScore(TSStd(quote_volume_mean_12,72))),ResidualizeVsFundingCore(Mul(Rank(TSMean(quote_volume_mean_12,60)),ZScore(TSMean(ret_12,12)))))),36)) | H15_placebo_null_adversarial | P10_price_liquidity  | ResidualizeVsFundingCore | H48                      | same_symbol_zscore    | Core4                    | liquidity;price         |          -1.26416  |                      0.162903 |                              0.839984 |                              0.744345 |                                                 0.845931 |                                               5.06887 |                                             5.03681 |                          0.616668 |                                          0.463008 |                                            5.3531 |                                                          0.463008 | rc_076                |

## Strict-Pool Negative-Control Forensic

|   checkpoint_id | candidate_id      | stress_gate_v2_reasons   | cell_id   | signal_mode         | expression                                                                                                                                                                          | hypothesis_family            | feature_family_set   | operator_motif           | temporal_horizon_class   | normalization_scope   | residualization_target   | source_field_families   |   pilot_rank_score |   raw_10bp__validation_2025H1 |   raw_10bp__recent_oos_2025H2_2026Apr |   raw_20bp__recent_oos_2025H2_2026Apr |   execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr |   residual_vs_funding_10bp__recent_oos_2025H2_2026Apr |   residual_vs_core4_10bp__recent_oos_2025H2_2026Apr |   raw_10bp__fresh_forward_2026May |   raw_10bp__fresh_forward_2026May__gross_exposure |   residual_vs_funding_10bp__fresh_forward_2026May |   residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure |
|----------------:|:------------------|:-------------------------|:----------|:--------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------|:---------------------|:-------------------------|:-------------------------|:----------------------|:-------------------------|:------------------------|-------------------:|------------------------------:|--------------------------------------:|--------------------------------------:|---------------------------------------------------------:|------------------------------------------------------:|----------------------------------------------------:|----------------------------------:|--------------------------------------------------:|--------------------------------------------------:|------------------------------------------------------------------:|
|              04 | a7o_l1_C0208_1344 |                          | C0208     | wrong_lag_stale_24h | Neg(Clip(cross_symbol_rank(TSMean(ResidualizeVsCore4(Mul(Rank(TSMean(quote_volume_mean_24,36)),ZScore(TSMean(realized_vol_24,48)))),84)),-4.0,4.0))                                 | H15_placebo_null_adversarial | P8_regime_state      | ResidualizeVsCore4       | H24                      | cross_symbol_rank     | none                     | liquidity;volatility    |          -0.138524 |                      0.942723 |                              2.12268  |                              2.09608  |                                                 2.12982  |                                               4.82656 |                                             4.734   |                          1.25707  |                                          0.497625 |                                            5.1567 |                                                          0.497625 |
|              04 | a7o_l1_C0223_0289 |                          | C0223     | wrong_lag_stale_24h | Neg(TSMean(ResidualizeVsCore4(Add(Abs(ZScore(TSStd(quote_volume_mean_12,72))),ResidualizeVsFundingCore(Mul(Rank(TSMean(quote_volume_mean_12,60)),ZScore(TSMean(ret_12,12)))))),36)) | H15_placebo_null_adversarial | P10_price_liquidity  | ResidualizeVsFundingCore | H48                      | same_symbol_zscore    | Core4                    | liquidity;price         |          -1.26416  |                      0.162903 |                              0.839984 |                              0.744345 |                                                 0.845931 |                                               5.06887 |                                             5.03681 |                          0.616668 |                                          0.463008 |                                            5.3531 |                                                          0.463008 |

## Control-Contaminated Cells

|   checkpoint_id | cell_id   |
|----------------:|:----------|
|              04 | C0208     |
|              04 | C0223     |

## W1R Strict-Pool Reselection Counterfactual

| metric                                         |        value |   threshold | operator   | pass   |
|:-----------------------------------------------|-------------:|------------:|:-----------|:-------|
| reselected_deep_count                          | 1152         |     1152    | =          | True   |
| reselected_liquidity_volatility_share          |    0.149306  |        0.15 | <=         | True   |
| reselected_post_may_eligible_deep_survivors_v3 |   78         |      120    | >=         | False  |
| reselected_post_may_eligible_rate_v3           |    0.0677083 |        0.15 | >=         | False  |
| strict_negative_control_research_like_v2       |    2         |        0    | =          | False  |
| control_contaminated_cells                     |    2         |        0    | =          | False  |
| stress_gate_v3_active_hour_count_available     |    0         |        1    | =          | False  |

## Wave V2 Concentration/Productivity

| metric                                   |      value |   threshold | operator   | pass   |
|:-----------------------------------------|-----------:|------------:|:-----------|:-------|
| wave_liquidity_volatility_deep_share     |  0.136285  |        0.15 | <=         | True   |
| wave_single_return_corr_cluster_share    |  0.0269097 |        0.2  | <=         | True   |
| wave_post_may_eligible_deep_survivors_v2 | 76         |      120    | >=         | False  |
| wave_post_may_eligible_rate_v2           |  0.0659722 |        0.15 | >=         | False  |
| negative_control_research_like_v2        |  2         |        0    | =          | False  |

## Stress Gate V3 Limitation

`active_hour_count` is not present in the existing checkpoint artifacts, so W1R does not claim a full active-hour v3 pass. This remains a blocker for W2 authorization.
## Boundary

A7O-L1W1R is a reclassification and forensic stage only. It does not authorize W2, full L1, alpha proof, shadow, paper, or live.