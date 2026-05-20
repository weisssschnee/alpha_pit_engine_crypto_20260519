# Crypto A7O-L1 Pilot Shard Checkpoint

- generated_at: `2026-05-20T16:07:04Z`
- checkpoint_id: `02`
- cell_range: `64-127`
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
| liquidity_volatility_deep_share             | 0.140625                              |
| liquidity_volatility_deep_count             | 27                                    |
| liquidity_volatility_deep_cap               | 28                                    |
| liquidity_volatility_deep_forced_fill_count | 0                                     |
| single_horizon_deep_share                   | 0.15625                               |
| single_return_corr_cluster_share            | 0.041666666666666664                  |
| active_cells_with_valid_deep_audit          | 64                                    |
| post_may_eligible_deep_survivors            | 54                                    |
| placebo_or_null_research_candidates         | 0                                     |
| single_hypothesis_family_share              | 0.140625                              |
| single_feature_operator_horizon_motif_share | 0.015625                              |

## Generation Funnel

| stage                      |   count |
|:---------------------------|--------:|
| generated                  |  131072 |
| unique_expression          |  116078 |
| selected_for_strict_replay |    1536 |
| evaluated_without_failure  |    1536 |
| selected_for_deep_audit    |     192 |
| post_may_eligible_pool     |      54 |

## Cumulative Checkpoint Summary

|   checkpoint_id |   cell_start |   cell_end |   generated |   strict_replay_selected |   deep_audit_selected |   post_may_eligible_deep_survivors |   post_may_eligible_rate |   liquidity_volatility_deep_share |   single_return_corr_cluster_share |   single_horizon_deep_share |   active_cells_with_valid_deep_audit |   placebo_or_null_research_candidates |   may_leakage_violations | decision                                             | blockers   | manifest_hash                                                    | runtime_dir                                                                 | report                                                                                                  |
|----------------:|-------------:|-----------:|------------:|-------------------------:|----------------------:|-----------------------------------:|-------------------------:|----------------------------------:|-----------------------------------:|----------------------------:|-------------------------------------:|--------------------------------------:|-------------------------:|:-----------------------------------------------------|:-----------|:-----------------------------------------------------------------|:----------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
|              01 |            0 |         63 |      131072 |                     1536 |                   192 |                                 49 |                 0.255208 |                          0.145833 |                          0.0520833 |                    0.166667 |                                   62 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS |            | d328533e5f366112e1bf67b81ff14dd94a6bd52ff3310ec112643b16552b8016 | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_pilot         | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_PILOT_SHARD_CHECKPOINT_20260520.md |
|              02 |           64 |        127 |      131072 |                     1536 |                   192 |                                 54 |                 0.28125  |                          0.140625 |                          0.0416667 |                    0.15625  |                                   64 |                                     0 |                        0 | PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS |            | 1d3f8a2a43e213ba4be4c914de0d83004bff30d86401ab809179f3dcc1d1604a | G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7o_l1_checkpoint_02 | G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7O_L1_CHECKPOINT_02_20260521.md          |

## Deep Audit Decision Counts

| candidate_decision             |   count |
|:-------------------------------|--------:|
| A7O_PILOT_MAY_VETOED_NEAR_MISS |      62 |
| A7O_PILOT_RESEARCH_CANDIDATE   |      54 |
| A7O_PILOT_REJECTED             |      38 |
| A7O_PILOT_PRE_MAY_NEAR_MISS    |      29 |
| NEGATIVE_CONTROL               |       9 |

## Boundary

This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.