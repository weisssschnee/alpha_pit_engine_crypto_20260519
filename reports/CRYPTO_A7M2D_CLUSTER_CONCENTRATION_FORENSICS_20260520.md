# Crypto A7M-2D Cluster Concentration Forensics

- generated_at: `2026-05-20T10:10:20Z`
- decision: `PASS_A7M2D_FORENSICS_KEEP_A7M2_HOLD`
- executes_search: `False`
- executes_replay: `False`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- a7m2_decision: `HOLD_A7M2_ENGINE_BAKEOFF_BLOCKED`
- top_cluster: `rc_000`
- top_cluster_count: `245 / 379`
- top_cluster_share: `0.6464`
- blocker: `True`
- recommendation: `Do not run A7M-3. Add return-corr cluster cap before any next inherited-engine search.`

## Interpretation

A7M-2 produced many survivor/near-miss rows, but the dominant return-corr cluster is too large for a valid inherited-engine promotion signal.
This is a search-space concentration problem, not an alpha proof signal.

## Top Cluster Summary

| return_corr_cluster   |   count |   share_of_positive_deep |   engine_count |   family_count |   field_family_count |   operator_signature_count |   expr_hash_count | top_engine                       |   top_engine_share | top_family                         |   top_family_share | top_field_family     |   top_field_family_share |   median_rank_score |   median_recent_raw_ann |   median_cost20_recent_ann |   median_lag1_recent_ann |   median_may_raw_ann |   median_residual_funding_recent_ann |
|:----------------------|--------:|-------------------------:|---------------:|---------------:|---------------------:|---------------------------:|------------------:|:---------------------------------|-------------------:|:-----------------------------------|-------------------:|:---------------------|-------------------------:|--------------------:|------------------------:|---------------------------:|-------------------------:|---------------------:|-------------------------------------:|
| rc_000                |     245 |               0.646438   |              6 |              6 |                    1 |                          3 |                73 | E5_surrogate_prioritized_sampler |           0.24898  | surrogate_prioritized_equal_budget |           0.24898  | liquidity;volatility |                 1        |            13.4072  |                1.84536  |                   1.1848   |                 1.91568  |             -9.06735 |                              4.43898 |
| rc_003                |      49 |               0.129288   |              6 |              6 |                    3 |                          1 |                26 | E3_AST_failure_aware_repair      |           0.489796 | ast_failure_aware_repair           |           0.489796 | liquidity;volatility |                 0.591837 |            14.0164  |                1.70126  |                   1.19547  |                 1.7438   |             -8.75199 |                              4.48419 |
| rc_002                |      43 |               0.113456   |              5 |              5 |                    1 |                          1 |                34 | E0_current_A7L_manual_generator  |           0.325581 | manual_a7l_control                 |           0.325581 | liquidity;volatility |                 1        |            13.4846  |                1.48356  |                   1.02394  |                 1.5198   |             -9.79398 |                              3.18183 |
| rc_005                |      18 |               0.0474934  |              2 |              2 |                    1 |                          1 |                12 | E4_CEM_adaptive_grammar_crypto   |           0.777778 | cem_adaptive_grammar               |           0.777778 | liquidity            |                 1        |            10.3223  |                0.50133  |                   0.174801 |                 0.487064 |             -7.44409 |                              3.59942 |
| rc_001                |      15 |               0.0395778  |              3 |              3 |                    1 |                          1 |                15 | E0_current_A7L_manual_generator  |           0.533333 | manual_a7l_control                 |           0.533333 | liquidity;volatility |                 1        |            12.3608  |                1.06293  |                   0.538177 |                 1.17359  |             -6.78282 |                              4.28773 |
| rc_004                |       3 |               0.00791557 |              2 |              2 |                    1 |                          2 |                 3 | E1_FormulaGenV2_crypto_adapter   |           0.666667 | formula_gen_v2_crypto              |           0.666667 | liquidity;volatility |                 1        |             9.69858 |                0.944119 |                   0.509412 |                 1.06017  |             -8.29719 |                              2.18664 |
| rc_009                |       2 |               0.00527704 |              1 |              1 |                    1 |                          1 |                 2 | E4_CEM_adaptive_grammar_crypto   |           1        | cem_adaptive_grammar               |           1        | liquidity;volatility |                 1        |            12.977   |                1.92448  |                   0.458891 |                 1.96802  |            -16.4939  |                              6.50049 |
| rc_006                |       1 |               0.00263852 |              1 |              1 |                    1 |                          1 |                 1 | E4_CEM_adaptive_grammar_crypto   |           1        | cem_adaptive_grammar               |           1        | liquidity;volatility |                 1        |            15.4297  |                2.36088  |                   1.74719  |                 2.33697  |            -20.5479  |                              4.03232 |
| rc_007                |       1 |               0.00263852 |              1 |              1 |                    1 |                          1 |                 1 | E4_CEM_adaptive_grammar_crypto   |           1        | cem_adaptive_grammar               |           1        | liquidity;volatility |                 1        |            15.2624  |                2.69628  |                   1.7708   |                 2.49512  |            -15.9635  |                              5.42698 |
| rc_008                |       1 |               0.00263852 |              1 |              1 |                    1 |                          1 |                 1 | E4_CEM_adaptive_grammar_crypto   |           1        | cem_adaptive_grammar               |           1        | liquidity;volatility |                 1        |            13.0868  |                3.4392   |                   3.17836  |                 3.51508  |            -13.7899  |                              7.0696  |
| rc_010                |       1 |               0.00263852 |              1 |              1 |                    1 |                          1 |                 1 | E4_CEM_adaptive_grammar_crypto   |           1        | cem_adaptive_grammar               |           1        | liquidity;volatility |                 1        |             9.45364 |                1.29224  |                   0.971959 |                 1.35472  |             -6.72374 |                              3.41615 |

## Top Cluster Expressions

| return_corr_cluster   | field      | value                                                 |   count |     share |
|:----------------------|:-----------|:------------------------------------------------------|--------:|----------:|
| rc_000                | expression | Mul(Rank(quote_volume_mean_24),Rank(realized_vol_24)) |      13 | 0.0530612 |
| rc_000                | expression | Mul(Rank(number_of_trades),Rank(realized_vol_24))     |      11 | 0.044898  |
| rc_000                | expression | Mul(Rank(realized_vol_24),Rank(quote_volume_mean_24)) |      11 | 0.044898  |
| rc_000                | expression | Mul(Rank(realized_vol_24),Rank(quote_volume_mean_12)) |      10 | 0.0408163 |
| rc_000                | expression | Mul(Rank(realized_vol_24),Rank(number_of_trades))     |      10 | 0.0408163 |
| rc_000                | expression | Mul(Rank(realized_vol_12),Rank(quote_volume_mean_24)) |      10 | 0.0408163 |
| rc_000                | expression | Mul(Rank(quote_asset_volume),Rank(realized_vol_24))   |      10 | 0.0408163 |
| rc_000                | expression | Mul(Rank(quote_volume_mean_12),Rank(realized_vol_12)) |       9 | 0.0367347 |

## Top Cluster Reject Reasons

| return_corr_cluster   | reject_reason                 |   count |   share_in_cluster |
|:----------------------|:------------------------------|--------:|-------------------:|
| rc_000                | may_stress_severe_fail        |     245 |          1         |
| rc_000                | may_residual_funding_negative |     245 |          1         |
| rc_000                | cost20_recent_negative        |      18 |          0.0734694 |
| rc_000                | cost20_validation_negative    |       8 |          0.0326531 |
| rc_000                | core4_beta_too_high           |       6 |          0.0244898 |

## Cluster Cap Counterfactual

|   cap_share |   max_per_cluster |   positive_deep_before |   positive_deep_after_cap_only |   removed_by_cap |   top_cluster_after_cap_share |   engine_count_after_cap |   family_count_after_cap |   field_family_count_after_cap |   median_rank_score_after_cap |
|------------:|------------------:|-----------------------:|-------------------------------:|-----------------:|------------------------------:|-------------------------:|-------------------------:|-------------------------------:|------------------------------:|
|        0.35 |               132 |                    379 |                            266 |              113 |                      0.496241 |                        6 |                        6 |                              3 |                       13.9992 |
|        0.25 |                94 |                    379 |                            228 |              151 |                      0.412281 |                        6 |                        6 |                              3 |                       14.1705 |
|        0.2  |                75 |                    379 |                            209 |              170 |                      0.358852 |                        6 |                        6 |                              3 |                       14.4961 |
|        0.15 |                56 |                    379 |                            190 |              189 |                      0.294737 |                        6 |                        6 |                              3 |                       14.1705 |

## Population Summary

| population        |   count |   engine_count |   family_count |   field_family_count |   expr_hash_count | top_engine                       |   top_engine_share | top_field_family     |   top_field_family_share |
|:------------------|--------:|---------------:|---------------:|---------------------:|------------------:|:---------------------------------|-------------------:|:---------------------|-------------------------:|
| all_strict_replay |    4096 |              8 |              8 |                   11 |              2258 | E0_current_A7L_manual_generator  |           0.125    | liquidity;volatility |                 0.665771 |
| deep_audit        |     512 |              8 |              8 |                    8 |               300 | E0_current_A7L_manual_generator  |           0.125    | liquidity;volatility |                 0.669922 |
| positive_deep     |     379 |              6 |              6 |                    3 |               167 | E0_current_A7L_manual_generator  |           0.168865 | liquidity;volatility |                 0.899736 |
| top_cluster       |     245 |              6 |              6 |                    1 |                73 | E5_surrogate_prioritized_sampler |           0.24898  | liquidity;volatility |                 1        |

## Decision Boundary

- This report does not authorize A7M-3.
- This report does not authorize alpha proof, shadow, paper, live, or production.
- Next valid work is cluster-cap / diversity-first search policy revision, not budget expansion.
