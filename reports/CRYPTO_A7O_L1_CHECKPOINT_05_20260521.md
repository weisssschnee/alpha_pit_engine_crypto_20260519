# Crypto A7O-L1 Pilot Shard Checkpoint

- generated_at: `2026-05-20T16:52:14Z`
- checkpoint_id: `05`
- cell_range: `256-319`
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
| liquidity_volatility_deep_share             | 0.14583333333333334                   |
| liquidity_volatility_deep_count             | 28                                    |
| liquidity_volatility_deep_cap               | 28                                    |
| liquidity_volatility_deep_forced_fill_count | 0                                     |
| single_horizon_deep_share                   | 0.19791666666666666                   |
| single_return_corr_cluster_share            | 0.03125                               |
| active_cells_with_valid_deep_audit          | 62                                    |
| post_may_eligible_deep_survivors            | 11                                    |
| placebo_or_null_research_candidates         | 0                                     |
| single_hypothesis_family_share              | 0.10416666666666667                   |
| single_feature_operator_horizon_motif_share | 0.026041666666666668                  |

## Generation Funnel

| stage                      |   count |
|:---------------------------|--------:|
| generated                  |  131072 |
| unique_expression          |  116134 |
| selected_for_strict_replay |    1536 |
| evaluated_without_failure  |    1536 |
| selected_for_deep_audit    |     192 |
| post_may_eligible_pool     |      11 |

## Cumulative Checkpoint Summary

|   checkpoint_id |   cell_start |   cell_end |   generated |   strict_replay_selected |   deep_audit_selected |   post_may_eligible_deep_survivors |   post_may_eligible_rate |   liquidity_volatility_deep_share |   single_return_corr_cluster_share |   single_horizon_deep_share |   active_cells_with_valid_deep_audit |   placebo_or_null_research_candidates |   may_leakage_violations | decision                                             | blockers                            | manifest_hash                                                    | runtime_dir                                                                 | report                                                                                                  |
|----------------:|-------------:|-----------:|------------:|-------------------------:|----------------------:|-----------------------------------:|-------------------------:|----------------------------------:|-----------------------------------:|----------------------------:|-------------------------------------:|--------------------------------------:|-------------------------:|:-----------------------------------------------------|:------------------------------------|:-----------------------------------------------------------------|:----------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
|               1 |            0 |         63 |      131072 |                     1536 |                   192 |                                 49 |                 0.255208 |                          0.145833 |                          0.0520833 |                    0.166667 |                                   62 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | d328533e5f366112e1bf67b81ff14dd94a6bd52ff3310ec112643b16552b8016 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_pilot         | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_PILOT_SHARD_CHECKPOINT_20260520.md |
|               2 |           64 |        127 |      131072 |                     1536 |                   192 |                                 54 |                 0.28125  |                          0.140625 |                          0.0416667 |                    0.15625  |                                   64 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | 1d3f8a2a43e213ba4be4c914de0d83004bff30d86401ab809179f3dcc1d1604a | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_02 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_02_20260521.md          |
|               3 |          128 |        191 |      131072 |                     1536 |                   192 |                                 43 |                 0.223958 |                          0.09375  |                          0.046875  |                    0.140625 |                                   64 |                                     1 |                        0 | HOLD_A7O_L1_PILOT_CHECKPOINT                         | placebo_or_null_research_candidates | 783e15be2f8365919a7bb252944d68c73c54ca27e75abb6c770bf686156330f9 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_03 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_03_20260521.md          |
|               4 |          192 |        255 |      131072 |                     1536 |                   192 |                                 35 |                 0.182292 |                          0.145833 |                          0.0833333 |                    0.177083 |                                   63 |                                     2 |                        0 | HOLD_A7O_L1_PILOT_CHECKPOINT                         | placebo_or_null_research_candidates | e941b25ef4602962baf09858ad43089bd965db187bafe11fb1e08553def904fa | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_04 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_04_20260521.md          |
|               5 |          256 |        319 |      131072 |                     1536 |                   192 |                                 47 |                 0.244792 |                          0.145833 |                          0.03125   |                    0.197917 |                                   62 |                                     1 |                        0 | HOLD_A7O_L1_PILOT_CHECKPOINT                         | placebo_or_null_research_candidates | dd9ad66d1c47597f6c503173d95568d26bd024cc0ae5485811708bd8228f1e70 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_05 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_05_20260521.md          |
|               6 |          320 |        383 |      131072 |                     1536 |                   192 |                                 46 |                 0.239583 |                          0.145833 |                          0.0572917 |                    0.140625 |                                   58 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS | nan                                 | 62f0a7151cbd5ba4082331337a4a8bc8f18c077a263961873ff90e3bc06e3d8d | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_06 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_06_20260521.md          |

## Deep Audit Decision Counts

| candidate_decision             |   count |
|:-------------------------------|--------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS |      94 |
| A7O_PILOT_REJECTED             |      52 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |      23 |
| NEGATIVE_CONTROL               |      12 |
| A7O_PILOT_RESEARCH_CANDIDATE   |      11 |

## Boundary

This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.