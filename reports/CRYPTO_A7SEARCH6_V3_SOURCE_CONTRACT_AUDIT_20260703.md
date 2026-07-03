# CRYPTO A7SEARCH6 V3 Source Contract Audit

Generated: `2026-07-03T01:38:22Z`

## Decision

`HOLD_A7SEARCH6V3_SOURCE_CONTRACT_PROOF_REQUIRED`

This is a source-timing and blind-holdout gate for A7SEARCH6 accepted candidates. It does not validate alpha, and it does not authorize shadow, paper, live, or production portfolio construction.

## Counts

- accepted_rows: `18`
- accepted_unique_blueprints: `15`
- formula_rows: `18`
- unique_fields: `14`
- pass_controlled_formula_count: `0`
- hard_hold_formula_count: `18`
- june_holdout_available: `True`
- june_holdout_reward_split_wired: `False`

## Field Family Gate Summary

| field_family        | contract_status          |   fields |   formulas |
|:--------------------|:-------------------------|---------:|-----------:|
| open_interest       | HOLD_SOURCE_PROOF        |        5 |         13 |
| positioning         | HOLD_SOURCE_PROOF        |        3 |         12 |
| basis_premium       | PASS_CONTROLLED_CONTRACT |        2 |          4 |
| regime_state        | HOLD_SOURCE_PROOF        |        1 |          3 |
| event_dense_funding | HOLD_SOURCE_PROOF        |        1 |          2 |
| liquidity           | PASS_CONTROLLED_CONTRACT |        1 |          1 |
| taker_flow          | PASS_CONTROLLED_CONTRACT |        1 |          1 |

## Dataset Contract Inventory

| dataset                                                 | role                                    | report_exists   | field_contract_exists   | manifest_exists   | coverage_exists   | decision                                                                           | timestamp_min       | timestamp_max       |   rows |   symbols |   mean_coverage |   mean_metrics_coverage |   mean_funding_coverage | timestamp_semantics                                                                                                                                               | feature_available_time                                | proof_boundary                                                                           |
|:--------------------------------------------------------|:----------------------------------------|:----------------|:------------------------|:------------------|:------------------|:-----------------------------------------------------------------------------------|:--------------------|:--------------------|-------:|----------:|----------------:|------------------------:|------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|:-----------------------------------------------------------------------------------------|
| binance_universe498_recent_patch_1h_v1_20260612         | June/late-May blind holdout data source | True            | True                    | True              | True              | PASS_BINANCE_UNIVERSE498_RECENT_PATCH_READY_WITH_SYMBOL_GAPS_FAST_CHECKSUM_PENDING | 2026-05-26 00:00:00 | 2026-06-11 23:00:00 | 203184 |       498 |               1 |                0.999724 |                1        | {"timestamp": "1h bucket start UTC naive", "feature_available_time": "timestamp + 1h conservative bucket close availability", "execution_time": "timestamp + 1h"} | timestamp + 1h conservative bucket close availability | controlled_experiment_allowed_fast_checksum_pending; final proof requires CHECKSUM audit |
| binance_universe_pre2024_complete_replay_1h_v1_20260612 | pre-2024 regime enrichment source       | True            | True                    | True              | True              | PASS_PRE2024_COMPLETE_REPLAY_1H_READY_FAST_METRICS_CHECKSUM_PENDING                | 2023-07-01 00:00:00 | 2023-12-31 23:00:00 | 668590 |       176 |             nan |                0.998753 |                0.999337 | "1h UTC bucket timestamp"                                                                                                                                         | timestamp + 1h                                        |                                                                                          |

## June Holdout Wiring Gap

| split_name                       | available   | dataset                                         | start               | end                 |   available_symbols |   dataset_symbols |   mean_coverage |   mean_metrics_coverage |   mean_funding_coverage | reward_split_wired   | blocking_issue                                                                                              | recommended_action                                                                                        |
|:---------------------------------|:------------|:------------------------------------------------|:--------------------|:--------------------|--------------------:|------------------:|----------------:|------------------------:|------------------------:|:---------------------|:------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| blind_june2026_20260601_20260611 | True        | binance_universe498_recent_patch_1h_v1_20260612 | 2026-06-01 00:00:00 | 2026-06-11 23:00:00 |                 498 |               498 |               1 |                0.999724 |                       1 | False                | reward split function does not define June blind split and numeric loader does not merge recent patch panel | add explicit blind_june2026 split after May stress; run accepted formulas only after source-contract gate |

## Formula Source Gate

| source_blueprint_id        |   horizon_h | formula_source_gate                 | field_contract_statuses                    |   min_oos_floor_sortino |   recent_sortino | formula                                                                                                                                                                   |
|:---------------------------|------------:|:------------------------------------|:-------------------------------------------|------------------------:|-----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search6_afa93f504b4c29d0 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                8.6339   |         13.5427  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_afa93f504b4c29d0 |           8 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                8.50321  |         18.3882  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_4c8a38ddff3fb132 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                7.69971  |         12.8057  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_06c5d4a2d2ce5d98 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                7.5507   |         10.702   | SafeDiv(ZScore(Mean(open_interest_value_mean,504)),Abs(global_long_short_account_ratio_last))                                                                             |
| a7search6_5be6987af4a13e67 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                5.72329  |          7.85899 | SafeDiv(Abs(CSRank(open_interest_value_change_24h)),Abs(Decay(account_position_divergence,8)))                                                                            |
| a7search6_4c8a38ddff3fb132 |          24 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                5.71299  |         17.6279  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_e7ee64f0ef980aca |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                5.03834  |         14.7101  | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_5a326bbdc99cd2b9 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                4.89019  |         14.1914  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_5a326bbdc99cd2b9 |           8 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                4.12518  |         17.6046  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_370b9d993902426e |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                2.12792  |         13.6746  | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_229924c832dd5901 |          24 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                1.90384  |          5.9645  | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                                                                                                  |
| a7search6_5a7a41644c28a05a |          24 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                1.73821  |          5.80861 | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                                                                                                 |
| a7search6_0159a7544af64b1d |          24 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                1.68071  |          8.60733 | Sub(CSRank(ZScore(Mean(account_position_divergence,24))),CSRank(Decay(mark_index_basis_bps,336)))                                                                         |
| a7search6_2e796ac0b2a688c4 |          24 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                1.36465  |          2.44163 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                                                                                       |
| a7search6_05d9f75e309aa068 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                0.4619   |         14.873   | Mul(ZScore(global_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                     |
| a7search6_215546fe5dfda21c |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                0.4619   |         14.873   | Mul(CSRank(Abs(CSRank(global_long_short_account_ratio_last))),Sign(Decay(stress_proxy_state,336)))                                                                        |
| a7search6_8d74bccf1d25af11 |           8 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF|PASS_CONTROLLED_CONTRACT |                0.18029  |         17.7061  | SafeDiv(Decay(top_long_short_account_ratio_last,12),Abs(ZScore(Mean(quote_volume_z_168h,504))))                                                                           |
| a7search6_9115fe1cea3feca0 |           4 | HOLD_SOURCE_CONTRACT_PROOF_REQUIRED | HOLD_SOURCE_PROOF                          |                0.082274 |         14.3523  | Mul(ZScore(top_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                        |

## Required Next Actions

1. Attach field-native source timestamps for Binance metrics OI, global/top long-short ratios, and funding-derived state before treating current A7SEARCH6 winners as proof candidates.
2. Wire `blind_june2026_20260601_20260611` into the reward split/loader as an evaluation-only split; do not use it for orientation or search selection.
3. Re-run accepted A7SEARCH6 formulas only after the above gate; broad search remains blocked by this audit.

## Outputs

- `formula_field_map`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_formula_field_map.csv`
- `field_source_contract_gate`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_field_source_contract_gate.csv`
- `formula_source_gate`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_formula_source_gate.csv`
- `dataset_contract_inventory`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_dataset_contract_inventory.csv`
- `june_holdout_wiring_gap`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_june_holdout_wiring_gap.csv`
- `field_family_gate_summary`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_field_family_gate_summary.csv`
- `manifest`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_v3_source_contract_audit_20260703\a7search6_v3_manifest.json`
