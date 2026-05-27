# Crypto A7O-L1 Pilot Shard Checkpoint

- generated_at: `2026-05-20T18:29:49Z`
- checkpoint_id: `A7P3_W2PILOT`
- cell_range: `0-63`
- decision: `PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS`
- pilot_only: `True`
- executes_search: `True`
- executes_replay: `True`
- authorizes_next_64_cell_checkpoint: `True`
- authorizes_full_l1_without_checkpoint: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `[]`

## Checkpoint Metrics

| metric                                      | value                                 |
|:--------------------------------------------|:--------------------------------------|
| generated                                   | 131072                                |
| strict_replay_selected                      | 1536                                  |
| deep_audit_selected                         | 192                                   |
| eval_failure_count                          | 0                                     |
| fold_metric_missing_rate                    | 0.0                                   |
| deep_selection_policy                       | global_liquidity_volatility_cap_15pct |
| liquidity_volatility_deep_share             | 0.046875                              |
| liquidity_volatility_deep_count             | 9                                     |
| liquidity_volatility_deep_cap               | 28                                    |
| liquidity_volatility_deep_forced_fill_count | 0                                     |
| single_horizon_deep_share                   | 0.296875                              |
| single_return_corr_cluster_share            | 0.09375                               |
| active_cells_with_valid_deep_audit          | 64                                    |
| post_may_eligible_deep_survivors            | 13                                    |
| placebo_or_null_research_candidates         | 0                                     |
| strict_negative_control_research_like       | 0                                     |
| negative_control_dominance_failures         | 0                                     |
| negative_control_dominance_audit_rows       | 0                                     |
| stress_gate_min_gross_exposure              | 0.05                                  |
| stress_gate_min_active_hours                | 10                                    |
| single_hypothesis_family_share              | 0.15625                               |
| single_feature_operator_horizon_motif_share | 0.015625                              |

## Generation Funnel

| stage                      |   count |
|:---------------------------|--------:|
| generated                  |  131072 |
| unique_expression          |  119732 |
| selected_for_strict_replay |    1536 |
| evaluated_without_failure  |    1536 |
| selected_for_deep_audit    |     192 |
| post_may_eligible_pool     |      13 |

## Cumulative Checkpoint Summary

> Note: this section is inherited context from the checkpoint runner's existing cumulative table and is not used for the A7P-3 decision. The authoritative A7P-3 decision is in `CRYPTO_A7P3_PROTECTED_W2_PILOT_DECISION_20260521.md` and the `A7P3_W2PILOT` checkpoint decision JSON.

|   checkpoint_id |   cell_start |   cell_end |   generated |   strict_replay_selected |   deep_audit_selected |   post_may_eligible_deep_survivors |   post_may_eligible_rate |   liquidity_volatility_deep_share |   single_return_corr_cluster_share |   single_horizon_deep_share |   active_cells_with_valid_deep_audit |   placebo_or_null_research_candidates |   may_leakage_violations | decision                                             | blockers                            | manifest_hash                                                    | runtime_dir                                                                 | report                                                                                                  |
|----------------:|-------------:|-----------:|------------:|-------------------------:|----------------------:|-----------------------------------:|-------------------------:|----------------------------------:|-----------------------------------:|----------------------------:|-------------------------------------:|--------------------------------------:|-------------------------:|:-----------------------------------------------------|:------------------------------------|:-----------------------------------------------------------------|:----------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
|               1 |            0 |         63 |      131072 |                     1536 |                   192 |                                 49 |                0.255208  |                          0.145833 |                          0.0520833 |                    0.166667 |                                   62 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | d328533e5f366112e1bf67b81ff14dd94a6bd52ff3310ec112643b16552b8016 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_pilot         | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_PILOT_SHARD_CHECKPOINT_20260520.md |
|               2 |           64 |        127 |      131072 |                     1536 |                   192 |                                 54 |                0.28125   |                          0.140625 |                          0.0416667 |                    0.15625  |                                   64 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | 1d3f8a2a43e213ba4be4c914de0d83004bff30d86401ab809179f3dcc1d1604a | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_02 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_02_20260521.md          |
|               3 |          128 |        191 |      131072 |                     1536 |                   192 |                                  8 |                0.0416667 |                          0.09375  |                          0.046875  |                    0.140625 |                                   64 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | c3ae5fe111d62bb7da059795eabfc8cd72a75b3d144986648f6647f7895ee293 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_03 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_03_20260521.md          |
|               4 |          192 |        255 |      131072 |                     1536 |                   192 |                                  8 |                0.0416667 |                          0.145833 |                          0.0833333 |                    0.177083 |                                   63 |                                     2 |                        0 | HOLD_A7O_L1_PILOT_CHECKPOINT                         | placebo_or_null_research_candidates | 8df00eee6db7dc4d8a41f672a2cfe47087c37c2bbf022a370f4332c76b995c26 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_04 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_04_20260521.md          |
|               5 |          256 |        319 |      131072 |                     1536 |                   192 |                                 11 |                0.0572917 |                          0.145833 |                          0.03125   |                    0.197917 |                                   62 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | e7a9af81b31ea78fbbea3ec0cdfaff98a8859869c55be737de8d0b1cf8758f16 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_05 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_05_20260521.md          |
|               6 |          320 |        383 |      131072 |                     1536 |                   192 |                                 13 |                0.0677083 |                          0.145833 |                          0.0572917 |                    0.140625 |                                   58 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | d9b8114ded5d2a7e8091e0e605335c82048feda2c8075e66b5a00ff23454983c | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_06 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_06_20260521.md          |

## Deep Audit Decision Counts

| candidate_decision             |   count |
|:-------------------------------|--------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS |     166 |
| A7O_PILOT_RESEARCH_CANDIDATE   |      13 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |       7 |
| A7O_PILOT_REJECTED             |       6 |

## Boundary

This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.
