# CRYPTO A7SEARCH6 Validation Pack 20260702

Generated: `2026-07-02T18:13:53Z`

## Decision

`PASS_A7SEARCH6_VALIDATION_HAS_INCREMENTAL_CANDIDATES`

This validates whether A7SEARCH6 accepted candidates have incremental evidence over single-leg and nearby-operator baselines. It is not alpha proof and does not authorize shadow, paper, live, or production portfolio construction.

## Counts

- compressed_unique_blueprints: `22`
- validation_queue_rows: `295`
- reward_rows: `1180`
- accepted_rows: `18`
- accepted_unique_blueprints: `15`
- eval_error_rows: `0`
- incremental_source_count: `15`
- non_unique_source_count: `0`
- canonical_failed_source_count: `7`
- blind_june_status: `NOT_EXECUTED_REWARD_SPLIT_NOT_DEFINED_FOR_JUNE_2026`

## Validation Group Summary

| validation_group   |   candidates |   accepted_rows |   accepted_unique |   max_recent_sortino |   max_min_oos_floor_sortino |
|:-------------------|-------------:|----------------:|------------------:|---------------------:|----------------------------:|
| canonical          |           22 |              18 |                15 |              29.0544 |                     8.6339  |
| operator_neighbor  |           97 |               0 |                 0 |              18.6599 |                     3.46468 |
| single_leg         |          176 |               0 |                 0 |              24.2365 |                     3.3914  |

## Source Decisions

| source_blueprint_id        |   source_rank |   canonical_accepted_rows |   single_leg_accepted_rows |   operator_neighbor_accepted_rows |   accepted_rows | decision                              |
|:---------------------------|--------------:|--------------------------:|---------------------------:|----------------------------------:|----------------:|:--------------------------------------|
| a7search6_84f74066182786e3 |             2 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_351a19252c9ff820 |             7 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_8185d7e38fbfef0a |             9 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_54fa70ba1036adfc |            15 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_40090b5c3ec8edfc |            16 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_9102c722a6bc3e6a |            19 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_0bc40820e0608f51 |            22 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS         |
| a7search6_afa93f504b4c29d0 |             1 |                         2 |                          0 |                                 0 |               2 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_06c5d4a2d2ce5d98 |             3 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_5be6987af4a13e67 |             4 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_4c8a38ddff3fb132 |             5 |                         2 |                          0 |                                 0 |               2 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_e7ee64f0ef980aca |             6 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_5a326bbdc99cd2b9 |             8 |                         2 |                          0 |                                 0 |               2 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_370b9d993902426e |            10 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_229924c832dd5901 |            11 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_5a7a41644c28a05a |            12 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_0159a7544af64b1d |            13 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_2e796ac0b2a688c4 |            14 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_05d9f75e309aa068 |            17 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_215546fe5dfda21c |            18 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_8d74bccf1d25af11 |            20 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |
| a7search6_9115fe1cea3feca0 |            21 |                         1 |                          0 |                                 0 |               1 | PASS_INCREMENTAL_INTERACTION_EVIDENCE |

## Top Accepted Validation Rows

| source_blueprint_id        | validation_group   | blueprint_id                                      |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | formula                                                                                                                                                                   |
|:---------------------------|:-------------------|:--------------------------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search6_afa93f504b4c29d0 | canonical          | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           4 |      1 |        2.17796  |            10.1639   |       10.2162  |         13.5427  |                8.6339   |                2.39069 |                      0.768606  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_afa93f504b4c29d0 | canonical          | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           8 |      1 |        2.44731  |            15.8815   |       11.8745  |         18.3882  |                8.50321  |                1.27322 |                      0.398843  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_4c8a38ddff3fb132 | canonical          | a7search6_vp_a7search6_4c8a38ddff3fb132_canonical |           4 |      1 |        3.20525  |             7.88304  |       20.7519  |         12.8057  |                7.69971  |                4.23457 |                      0.354104  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_06c5d4a2d2ce5d98 | canonical          | a7search6_vp_a7search6_06c5d4a2d2ce5d98_canonical |           4 |      1 |        1.23614  |             8.01097  |       10.611   |         10.702   |                7.5507   |                4.14594 |                      0.659038  | SafeDiv(ZScore(Mean(open_interest_value_mean,504)),Abs(global_long_short_account_ratio_last))                                                                             |
| a7search6_5be6987af4a13e67 | canonical          | a7search6_vp_a7search6_5be6987af4a13e67_canonical |           4 |      1 |        1.93837  |             7.46779  |       12.173   |          7.85899 |                5.72329  |                2.85372 |                      0.971161  | SafeDiv(Abs(CSRank(open_interest_value_change_24h)),Abs(Decay(account_position_divergence,8)))                                                                            |
| a7search6_4c8a38ddff3fb132 | canonical          | a7search6_vp_a7search6_4c8a38ddff3fb132_canonical |          24 |      1 |        2.80125  |             9.73968  |       30.3127  |         17.6279  |                5.71299  |                3.21921 |                      0.0809608 | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_e7ee64f0ef980aca | canonical          | a7search6_vp_a7search6_e7ee64f0ef980aca_canonical |           4 |      1 |        2.27386  |             5.27179  |        7.21484 |         14.7101  |                5.03834  |                8.30483 |                      0.321052  | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_5a326bbdc99cd2b9 | canonical          | a7search6_vp_a7search6_5a326bbdc99cd2b9_canonical |           4 |      1 |        1.43957  |             5.53742  |        8.95718 |         14.1914  |                4.89019  |                7.08298 |                      0.508094  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_5a326bbdc99cd2b9 | canonical          | a7search6_vp_a7search6_5a326bbdc99cd2b9_canonical |           8 |      1 |        1.35048  |             6.01743  |        8.43705 |         17.6046  |                4.12518  |                5.87578 |                      0.236695  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_370b9d993902426e | canonical          | a7search6_vp_a7search6_370b9d993902426e_canonical |           4 |      1 |        2.72638  |             2.88422  |        3.80858 |         13.6746  |                2.12792  |                4.07461 |                      0.375933  | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_229924c832dd5901 | canonical          | a7search6_vp_a7search6_229924c832dd5901_canonical |          24 |      1 |        2.70245  |             7.71697  |        2.92514 |          5.9645  |                1.90384  |                3.87699 |                      0.427901  | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                                                                                                  |
| a7search6_5a7a41644c28a05a | canonical          | a7search6_vp_a7search6_5a7a41644c28a05a_canonical |          24 |      1 |        2.68647  |             7.65998  |        3.10159 |          5.80861 |                1.73821  |                3.87436 |                      0.188398  | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                                                                                                 |
| a7search6_0159a7544af64b1d | canonical          | a7search6_vp_a7search6_0159a7544af64b1d_canonical |          24 |      1 |        1.63474  |             2.89055  |        6.62664 |          8.60733 |                1.68071  |                0.97726 |                      0.220905  | Sub(CSRank(ZScore(Mean(account_position_divergence,24))),CSRank(Decay(mark_index_basis_bps,336)))                                                                         |
| a7search6_2e796ac0b2a688c4 | canonical          | a7search6_vp_a7search6_2e796ac0b2a688c4_canonical |          24 |      1 |        0.734413 |             6.94615  |        2.50376 |          2.44163 |                1.36465  |                6.10508 |                      0.845688  | Mul(open_interest_last,Mean(premium_close_bps,504))                                                                                                                       |
| a7search6_05d9f75e309aa068 | canonical          | a7search6_vp_a7search6_05d9f75e309aa068_canonical |           4 |      1 |        0.453798 |             1.00227  |        7.27699 |         14.873   |                0.4619   |                5.12733 |                      0.644717  | Mul(ZScore(global_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                     |
| a7search6_215546fe5dfda21c | canonical          | a7search6_vp_a7search6_215546fe5dfda21c_canonical |           4 |      1 |        0.453798 |             1.00227  |        7.27699 |         14.873   |                0.4619   |                5.12733 |                      0.452678  | Mul(CSRank(Abs(CSRank(global_long_short_account_ratio_last))),Sign(Decay(stress_proxy_state,336)))                                                                        |
| a7search6_8d74bccf1d25af11 | canonical          | a7search6_vp_a7search6_8d74bccf1d25af11_canonical |           8 |      1 |        2.37832  |             0.949114 |        3.43502 |         17.7061  |                0.18029  |                9.85266 |                      0.133306  | SafeDiv(Decay(top_long_short_account_ratio_last,12),Abs(ZScore(Mean(quote_volume_z_168h,504))))                                                                           |
| a7search6_9115fe1cea3feca0 | canonical          | a7search6_vp_a7search6_9115fe1cea3feca0_canonical |           4 |      1 |        0.972032 |             0.508013 |        4.79027 |         14.3523  |                0.082274 |                4.65791 |                      0.264436  | Mul(ZScore(top_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                        |

## Field Timing Risk Summary

| field_family        | timing_risk_note                                          |   fields |   source_blueprints |
|:--------------------|:----------------------------------------------------------|---------:|--------------------:|
| open_interest       | requires OI snapshot timestamp and no same-bar fill proof |        5 |                  16 |
| positioning         | requires account/position ratio publication lag proof     |        3 |                  13 |
| basis_premium       | mark/index/premium bar-close alignment proof required     |        2 |                   6 |
| taker_flow          | bar-close flow field; must execute after bar close        |        2 |                   4 |
| regime_state        | state thresholds must be train-only or rolling-past       |        1 |                   3 |
| event_dense_funding | requires funding publication timestamp / ffill-age proof  |        1 |                   1 |
| liquidity           | bar-close liquidity field; must execute after bar close   |        1 |                   1 |

## Bias Audit Notes

- Discovery status: replay/validation of A7SEARCH6 reward-selected candidates, not new blind discovery.
- Cost model: inherited A7REWARD1 `cost_bps=5.0`.
- Reward windows: train_2024, validation_2025H1, test_2025H2, recent_oos_2026JanApr, known_may2026_stress.
- June 2026 blind check is not executed here because the current reward split function does not define a June holdout split.
- Candidate acceptance remains a research gate only.

## Outputs

- `compressed_mechanisms`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_compressed_mechanisms.csv`
- `validation_queue`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_ablation_queue.csv`
- `accepted_summary`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_accepted_summary.csv`
- `group_summary`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_group_summary.csv`
- `source_decisions`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_source_decisions.csv`
- `field_timing_risk`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_field_timing_risk.csv`
- `field_timing_risk_summary`: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7search6_validation_pack_r2_20260702\a7search6_validation_field_timing_risk_summary.csv`
