# CRYPTO A7MECH-1 OI x Funding Mechanism Queue

Generated: `2026-07-03T07:12:43Z`

## Decision

`PASS_A7MECH1_MECHANISM_QUEUE_BUILT`

This builds a controlled mechanism queue around the only strict A7REWARD-2 survivor. It is not alpha proof and does not authorize broad search.

## Counts

- queue_rows: `180`

## Mechanism Groups

| mechanism_group       |   count |
|:----------------------|--------:|
| single_leg_ablation   |     102 |
| interaction_expansion |      75 |
| base_reproduction     |       3 |

## Motifs

| motif                           |   count |
|:--------------------------------|--------:|
| oi_only_tsrank                  |      36 |
| oi_only_cs_tsrank               |      36 |
| safe_div_cs_oi_over_abs_funding |      19 |
| oi_rank_times_funding_sign      |      19 |
| oi_rank_minus_funding_rank      |      19 |
| safe_div_rank_over_funding_rank |      18 |
| funding_only_csrank_zmean       |      15 |
| funding_only_sign               |      15 |
| base_safe_div_oi_funding        |       3 |

## Queue Preview

| blueprint_id                           |   horizon_h | mechanism_group     | motif                     | formula                                                                                             |
|:---------------------------------------|------------:|:--------------------|:--------------------------|:----------------------------------------------------------------------------------------------------|
| a7mech1_0001_base_safe_div_oi_funding  |           4 | base_reproduction   | base_safe_div_oi_funding  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7mech1_0002_base_safe_div_oi_funding  |           8 | base_reproduction   | base_safe_div_oi_funding  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7mech1_0003_base_safe_div_oi_funding  |          24 | base_reproduction   | base_safe_div_oi_funding  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7mech1_0004_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_last,168)                                                                |
| a7mech1_0005_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_last,168))                                                        |
| a7mech1_0006_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_last,336)                                                                |
| a7mech1_0007_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_last,336))                                                        |
| a7mech1_0008_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_last,504)                                                                |
| a7mech1_0009_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_last,504))                                                        |
| a7mech1_0010_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_mean,168)                                                                |
| a7mech1_0011_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_mean,168))                                                        |
| a7mech1_0012_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_mean,336)                                                                |
| a7mech1_0013_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_mean,336))                                                        |
| a7mech1_0014_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_mean,504)                                                                |
| a7mech1_0015_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_mean,504))                                                        |
| a7mech1_0016_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_last,168)                                                                      |
| a7mech1_0017_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_last,168))                                                              |
| a7mech1_0018_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_last,336)                                                                      |
| a7mech1_0019_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_last,336))                                                              |
| a7mech1_0020_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_last,504)                                                                      |
| a7mech1_0021_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_last,504))                                                              |
| a7mech1_0022_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_mean,168)                                                                      |
| a7mech1_0023_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_mean,168))                                                              |
| a7mech1_0024_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_mean,336)                                                                      |
| a7mech1_0025_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_mean,336))                                                              |
| a7mech1_0026_oi_only_tsrank            |           4 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_mean,504)                                                                      |
| a7mech1_0027_oi_only_cs_tsrank         |           4 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_mean,504))                                                              |
| a7mech1_0028_funding_only_csrank_zmean |           4 | single_leg_ablation | funding_only_csrank_zmean | CSRank(ZScore(Mean(funding_rate_delta_state_24h,24)))                                               |
| a7mech1_0029_funding_only_sign         |           4 | single_leg_ablation | funding_only_sign         | Sign(Mean(funding_rate_delta_state_24h,24))                                                         |
| a7mech1_0030_funding_only_csrank_zmean |           4 | single_leg_ablation | funding_only_csrank_zmean | CSRank(ZScore(Mean(funding_rate_delta_state_24h,48)))                                               |
| a7mech1_0031_funding_only_sign         |           4 | single_leg_ablation | funding_only_sign         | Sign(Mean(funding_rate_delta_state_24h,48))                                                         |
| a7mech1_0032_funding_only_csrank_zmean |           4 | single_leg_ablation | funding_only_csrank_zmean | CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))                                               |
| a7mech1_0033_funding_only_sign         |           4 | single_leg_ablation | funding_only_sign         | Sign(Mean(funding_rate_delta_state_24h,72))                                                         |
| a7mech1_0034_funding_only_csrank_zmean |           4 | single_leg_ablation | funding_only_csrank_zmean | CSRank(ZScore(Mean(funding_rate_delta_state_24h,96)))                                               |
| a7mech1_0035_funding_only_sign         |           4 | single_leg_ablation | funding_only_sign         | Sign(Mean(funding_rate_delta_state_24h,96))                                                         |
| a7mech1_0036_funding_only_csrank_zmean |           4 | single_leg_ablation | funding_only_csrank_zmean | CSRank(ZScore(Mean(funding_rate_delta_state_24h,168)))                                              |
| a7mech1_0037_funding_only_sign         |           4 | single_leg_ablation | funding_only_sign         | Sign(Mean(funding_rate_delta_state_24h,168))                                                        |
| a7mech1_0038_oi_only_tsrank            |           8 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_last,168)                                                                |
| a7mech1_0039_oi_only_cs_tsrank         |           8 | single_leg_ablation | oi_only_cs_tsrank         | CSRank(TSRank(open_interest_value_last,168))                                                        |
| a7mech1_0040_oi_only_tsrank            |           8 | single_leg_ablation | oi_only_tsrank            | TSRank(open_interest_value_last,336)                                                                |

## Next Required

- Run source-lag retest before any strict reward evaluation.
- Keep source publication proof gates active.

