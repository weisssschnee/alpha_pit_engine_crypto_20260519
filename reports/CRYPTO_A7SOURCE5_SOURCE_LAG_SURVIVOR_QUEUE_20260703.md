# CRYPTO A7SOURCE-5 Source-Lag Survivor Reward Queue

Generated: `2026-07-03T06:51:45Z`

## Decision

`PASS_A7SOURCE5_SURVIVOR_REWARD_QUEUE_BUILT`

This packages A7SOURCE-4 source-lag survivors into a strict reward queue. It is not alpha proof.

## Counts

- queue_rows: `5`
- unique_source_blueprints: `4`

## Survivor Queue

| source_blueprint_id        | blueprint_id                                      |   horizon_h | expression                                                                                          | formula                                                                                             | candidate_role                         | semantic_pair               | motif                         | skeleton_key                                                                                    | source_lag_gate                  |   sortino_source_lag_1h |   sortino_source_lag_2h |   sortino_source_lag_4h |   nonoverlap_floor_sortino_source_lag_1h |   nonoverlap_floor_sortino_source_lag_2h |   nonoverlap_floor_sortino_source_lag_4h |   rankic_mean_source_lag_2h |   floor_retention_source_lag_2h |   source_lag_survivor_rank |
|:---------------------------|:--------------------------------------------------|------------:|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|:---------------------------------------|:----------------------------|:------------------------------|:------------------------------------------------------------------------------------------------|:---------------------------------|------------------------:|------------------------:|------------------------:|-----------------------------------------:|-----------------------------------------:|-----------------------------------------:|----------------------------:|--------------------------------:|---------------------------:|
| a7search6_afa93f504b4c29d0 | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | source_lag_survivor_research_candidate | open_interest|funding_state | a7source5_source_lag_survivor | SafeDiv(TSRank(open_interest_value_last,N),CSRank(ZScore(Mean(funding_rate_delta_state_Nh,N)))) | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |                11.0258  |                 8.82097 |                 4.5242  |                                 8.18257  |                                 6.22251  |                                 2.70251  |                  0.0277093  |                        0.448925 |                          1 |
| a7search6_afa93f504b4c29d0 | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | source_lag_survivor_research_candidate | open_interest|funding_state | a7source5_source_lag_survivor | SafeDiv(TSRank(open_interest_value_last,N),CSRank(ZScore(Mean(funding_rate_delta_state_Nh,N)))) | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |                 7.46497 |                 6.57066 |                 4.48947 |                                 4.56265  |                                 4.07075  |                                 1.76318  |                  0.0321666  |                        0.598154 |                          2 |
| a7search6_5a7a41644c28a05a | a7search6_vp_a7search6_5a7a41644c28a05a_canonical |          24 | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                           | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                           | source_lag_survivor_research_candidate | open_interest|basis_premium | a7source5_source_lag_survivor | Mul(CSRank(Mean(open_interest_mean,N)),Sign(Mean(premium_close_bps,N)))                         | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |                 3.25226 |                 3.31902 |                 3.18935 |                                 0.548434 |                                 0.68027  |                                -0.421123 |                  0.0113615  |                        1.77952  |                          3 |
| a7search6_229924c832dd5901 | a7search6_vp_a7search6_229924c832dd5901_canonical |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            | source_lag_survivor_research_candidate | open_interest|basis_premium | a7source5_source_lag_survivor | Mul(CSRank(Mean(open_interest_mean,N)),Sign(Mean(premium_close_bps,N)))                         | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |                 3.20428 |                 3.27969 |                 3.16279 |                                 0.467021 |                                 0.587335 |                                -0.305337 |                  0.0113563  |                        2.31014  |                          4 |
| a7search6_2e796ac0b2a688c4 | a7search6_vp_a7search6_2e796ac0b2a688c4_canonical |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 | source_lag_survivor_research_candidate | open_interest|basis_premium | a7source5_source_lag_survivor | Mul(open_interest_last,Mean(premium_close_bps,N))                                               | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC |                 2.47332 |                 2.47238 |                 2.45804 |                                 0.409991 |                                 0.425837 |                                 0.440479 |                  0.00245661 |                        0.903321 |                          5 |

## Family Summary

| semantic_pair               |   count |
|:----------------------------|--------:|
| open_interest|basis_premium |       3 |
| open_interest|funding_state |       2 |

## Next Required

- Run A7REWARD-2 strict reward on this queue.
- Keep source-lag and source-publication proof gates active.

