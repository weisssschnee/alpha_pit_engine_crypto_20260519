# CRYPTO A7LS-5 COMPANY RESULT AGGREGATE

Generated: 2026-06-05T11:30:33Z

## Decision

`PASS_A7LS5_COMPANY_NUMERIC_AGGREGATED_READY_FOR_A7LS6_DEEP_FOLLOWUP`

## Summary

- expected_shards: 9
- completed_shards: 9
- pass_shards: 7
- response_rows: 9800
- materialized_activity_ok_total: 490
- non_l7_numeric_clue_rows: 99
- rank_label_diagnostic_rows: 68
- shortlist_rows: 64
- top_non_l7_semantic_pair_share: 0.929

## Shard Summary

| shard   | manifest_path                                                                                        | decision                                                | blockers                | missing_numeric_fields   |   input_blueprint_count |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   portfolio_queue_count |   selected_portfolio_queue_count | generated_at         |
|:--------|:-----------------------------------------------------------------------------------------------------|:--------------------------------------------------------|:------------------------|:-------------------------|------------------------:|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|------------------------:|---------------------------------:|:---------------------|
| s000    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_000\a7ls5_s000_manifest.json | PASS_A7LS5S000_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               55 |                  1100 |                         32 |                                14 |                      13 |                               11 | 2026-06-05T11:20:20Z |
| s001    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_001\a7ls5_s001_manifest.json | PASS_A7LS5S001_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               57 |                  1140 |                         27 |                                11 |                      11 |                               10 | 2026-06-05T11:20:31Z |
| s002    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_002\a7ls5_s002_manifest.json | PASS_A7LS5S002_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               58 |                  1160 |                         16 |                                 9 |                      12 |                               11 | 2026-06-05T11:20:37Z |
| s003    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_003\a7ls5_s003_manifest.json | PASS_A7LS5S003_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               59 |                  1180 |                         17 |                                 3 |                       9 |                                7 | 2026-06-05T11:20:48Z |
| s004    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_004\a7ls5_s004_manifest.json | PASS_A7LS5S004_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               64 |                  1280 |                          2 |                                 5 |                       5 |                                5 | 2026-06-05T11:20:25Z |
| s005    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_005\a7ls5_s005_manifest.json | HOLD_A7LS5S005_PORTFOLIO_QUEUE_TOO_SMALL                | portfolio_selected_lt_4 |                          |                      64 |                               61 |                  1220 |                          1 |                                 3 |                       2 |                                2 | 2026-06-05T11:20:44Z |
| s006    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_006\a7ls5_s006_manifest.json | HOLD_A7LS5S006_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues |                          |                      64 |                               62 |                  1240 |                          0 |                                 0 |                       0 |                                0 | 2026-06-05T11:25:00Z |
| s007    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_007\a7ls5_s007_manifest.json | PASS_A7LS5S007_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      64 |                               55 |                  1100 |                          1 |                                17 |                      13 |                               12 | 2026-06-05T11:24:28Z |
| s008    | G:\AlphaFactory_CryptoData\research_runtime\a7ls5_company_numeric\shard_008\a7ls5_s008_manifest.json | PASS_A7LS5S008_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                          |                      19 |                               19 |                   380 |                          3 |                                 6 |                       4 |                                4 | 2026-06-05T11:22:19Z |

## Non-L7 By Label

| label_family                       |   rows |
|:-----------------------------------|-------:|
| L5_vol_adjusted_return             |     31 |
| L1_cross_sectional_relative_return |     24 |
| L3_liquidity_tier_relative_return  |     24 |
| L0_raw_forward_return              |     20 |

## Non-L7 By Semantic Pair

| semantic_pair      |   rows |
|:-------------------|-------:|
| basis_premium_like |     92 |
| volatility_like    |      4 |
| listing_age_like   |      3 |

## Response Blocker Families

| blocker_family             |   rows |
|:---------------------------|-------:|
| pre_may_unstable           |   7047 |
| control_dominated          |   2125 |
| lag_fragile                |    453 |
| numeric_clue               |     99 |
| rank_label_diagnostic_clue |     68 |
| cost_fragile               |      7 |
| nonoverlap_weak            |      1 |

## Shortlist

| blueprint_id           | expression                                                      | semantic_pair      | motif             | label_family                       |   label_horizon_h |   control_ratio_premay_max |   robust_min_tstat_floor |   cost10_recent_oriented |   one_bar_lag_recent_oriented |   followup_score | shard   |
|:-----------------------|:----------------------------------------------------------------|:-------------------|:------------------|:-----------------------------------|------------------:|---------------------------:|-------------------------:|-------------------------:|------------------------------:|-----------------:|:--------|
| a7ls5_4616845b0b6bf159 | Delta(mark_index_basis_bps,12)                                  | basis_premium_like | single            | L5_vol_adjusted_return             |                 4 |                   0.492406 |                 2.30347  |              0.271911    |                   0.139179    |         464.154  | s001    |
| a7ls5_093c274318822859 | Delta(mark_index_basis_bps,2)                                   | basis_premium_like | single            | L5_vol_adjusted_return             |                24 |                   0.88522  |                 2.11978  |              0.280763    |                   0.165549    |         459.909  | s000    |
| a7ls5_2a2b7e5d4d298995 | Delta(mark_trade_basis_bps,168)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 8 |                   0.701097 |                 0.107186 |              0.232685    |                   0.086658    |         349.34   | s000    |
| a7ls5_093c274318822859 | Delta(mark_index_basis_bps,2)                                   | basis_premium_like | single            | L5_vol_adjusted_return             |                 8 |                   0.861742 |                 2.56037  |              0.209901    |                   0.10672     |         333.008  | s000    |
| a7ls5_35d2fb6b43e8b1d2 | TSRank(mark_index_basis_bps,168)                                | basis_premium_like | single            | L5_vol_adjusted_return             |                 4 |                   0.976537 |                 1.69523  |              0.226898    |                   0.100958    |         331.898  | s000    |
| a7ls5_35a1ae6f13bfd9a5 | TSRank(mark_index_basis_bps,24)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 4 |                   0.723909 |                 2.62265  |              0.191268    |                   0.0838282   |         305.328  | s000    |
| a7ls5_75fcafa367ab667d | Delta(mark_index_basis_bps,1)                                   | basis_premium_like | single            | L5_vol_adjusted_return             |                 8 |                   0.98968  |                 2.25692  |              0.183656    |                   0.103323    |         290.269  | s001    |
| a7ls5_4616845b0b6bf159 | Delta(mark_index_basis_bps,12)                                  | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.178791 |                 6.67706  |              0.142519    |                   0.0564651   |         287.782  | s001    |
| a7ls5_527fcaeaacc0b31d | TSRank(mark_index_basis_bps,72)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.348952 |                 7.15384  |              0.141686    |                   0.0418024   |         255.748  | s001    |
| a7ls5_35d2fb6b43e8b1d2 | TSRank(mark_index_basis_bps,168)                                | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.464198 |                 6.62451  |              0.131901    |                   0.0516029   |         243.708  | s000    |
| a7ls5_f601ad58e52fad89 | Delta(mark_index_basis_bps,168)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.51849  |                 5.50857  |              0.115774    |                   0.0678692   |         237.303  | s003    |
| a7ls5_fb6d0a43f86780d8 | Sub(Mean(mark_index_basis_bps,2),Mean(mark_index_basis_bps,24)) | basis_premium_like | spread_short_long | L5_vol_adjusted_return             |                 1 |                   0.395426 |                 4.78097  |              0.127265    |                   0.0444054   |         236.909  | s003    |
| a7ls5_664d9c7a5d2fd3e4 | Delta(mark_index_basis_bps,24)                                  | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.831063 |                 7.33263  |              0.16044     |                   0.0494657   |         234.132  | s001    |
| a7ls5_35a1ae6f13bfd9a5 | TSRank(mark_index_basis_bps,24)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.306299 |                 5.66829  |              0.10939     |                   0.0409381   |         225.366  | s000    |
| a7ls5_8f2f4ada9562a211 | Sub(Mean(mark_index_basis_bps,4),Mean(mark_index_basis_bps,72)) | basis_premium_like | spread_short_long | L5_vol_adjusted_return             |                 1 |                   0.541996 |                 2.43398  |              0.108111    |                   0.0634855   |         219.831  | s002    |
| a7ls5_2b146a4707fb996d | TSRank(mark_index_basis_bps,12)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 4 |                   0.719972 |                 2.31858  |              0.142345    |                   0.045375    |         218.041  | s000    |
| a7ls5_cea8ba63e1e17180 | Mul(mark_trade_basis_bps,Sign(Mean(mark_trade_basis_bps,24)))   | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 4 |                   0.780621 |                 0.440337 |              0.125416    |                   0.0468914   |         194.685  | s003    |
| a7ls5_2b146a4707fb996d | TSRank(mark_index_basis_bps,12)                                 | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.358195 |                 4.69081  |              0.0856216   |                   0.0272765   |         181.769  | s000    |
| a7ls5_dd6280311359d237 | TSRank(premium_close_bps,72)                                    | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.623862 |                 2.71307  |              0.0963076   |                   0.0349623   |         171.597  | s003    |
| a7ls5_a67277353e6b3d57 | Delta(premium_close_bps,12)                                     | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.531812 |                 2.99752  |              0.0733913   |                   0.0407457   |         163.953  | s002    |
| a7ls5_4baaa0177ac2a671 | Delta(premium_close_bps,24)                                     | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.725125 |                 2.39074  |              0.0848395   |                   0.0471642   |         161.882  | s001    |
| a7ls5_5dd9a3b980a68890 | Mul(mark_index_basis_bps,Sign(Mean(premium_close_bps,8)))       | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 1 |                   0.836802 |                 4.49632  |              0.0938565   |                   0.0248872   |         139.56   | s001    |
| a7ls5_9db83290c767be01 | TSRank(premium_close_bps,24)                                    | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.78333  |                 2.98339  |              0.0867284   |                   0.024851    |         136.23   | s002    |
| a7ls5_8bceb03964f5c25f | TSRank(premium_close_bps,168)                                   | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.925938 |                 2.56479  |              0.0866094   |                   0.0364816   |         133.062  | s002    |
| a7ls5_7bbe46b7fc04a5d3 | Mul(Delta(mark_index_basis_bps,4),Sign(premium_close_bps))      | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 1 |                   0.487072 |                 2.27654  |              0.0444387   |                   0.0207638   |         118.772  | s001    |
| a7ls5_edb930f24fb49e48 | Mul(Delta(mark_index_basis_bps,2),Sign(premium_close_bps))      | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 1 |                   0.480474 |                 2.37229  |              0.0452073   |                   0.0185559   |         118.088  | s003    |
| a7ls5_71510dbfea8d42c9 | TSRank(mark_index_basis_bps,8)                                  | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.740939 |                 3.04515  |              0.0640903   |                   0.0169706   |         110.012  | s001    |
| a7ls5_1bcf1c49f40bab87 | Delta(premium_close_bps,2)                                      | basis_premium_like | single            | L5_vol_adjusted_return             |                 1 |                   0.795982 |                 2.64884  |              0.0555484   |                   0.0281824   |         106.781  | s000    |
| a7ls5_dbf6d3ecf9b901c3 | Mul(mark_index_basis_bps,Sign(Mean(mark_trade_basis_bps,12)))   | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 1 |                   0.859051 |                 2.69004  |              0.0531618   |                   0.0174924   |          87.4392 | s003    |
| a7ls5_cfc06f5f75b3f3cf | Mul(Delta(mark_index_basis_bps,8),Sign(premium_close_bps))      | basis_premium_like | gated_sign        | L5_vol_adjusted_return             |                 1 |                   0.925057 |                 2.15039  |              0.0402214   |                   0.0309899   |          80.8561 | s003    |
| a7ls5_35a1ae6f13bfd9a5 | TSRank(mark_index_basis_bps,24)                                 | basis_premium_like | single            | L3_liquidity_tier_relative_return  |                 1 |                   0.245551 |                 3.23074  |             -0.00124173  |                   0.000564642 |          79.2402 | s000    |
| a7ls5_4616845b0b6bf159 | Delta(mark_index_basis_bps,12)                                  | basis_premium_like | single            | L3_liquidity_tier_relative_return  |                 1 |                   0.271539 |                 3.91291  |             -0.00077486  |                   0.000740557 |          77.4996 | s001    |
| a7ls5_35a1ae6f13bfd9a5 | TSRank(mark_index_basis_bps,24)                                 | basis_premium_like | single            | L0_raw_forward_return              |                 1 |                   0.263065 |                 2.96871  |             -0.00127722  |                   0.000614553 |          77.2768 | s000    |
| a7ls5_35a1ae6f13bfd9a5 | TSRank(mark_index_basis_bps,24)                                 | basis_premium_like | single            | L1_cross_sectional_relative_return |                 1 |                   0.263065 |                 2.96871  |             -0.00127722  |                   0.000614553 |          77.2768 | s000    |
| a7ls5_4616845b0b6bf159 | Delta(mark_index_basis_bps,12)                                  | basis_premium_like | single            | L1_cross_sectional_relative_return |                 1 |                   0.31571  |                 3.70822  |             -0.000810173 |                   0.000764287 |          72.9015 | s001    |
| a7ls5_ac10b376522e0081 | Delta(mark_index_basis_bps,4)                                   | basis_premium_like | single            | L3_liquidity_tier_relative_return  |                 1 |                   0.309509 |                 2.48017  |             -0.00124779  |                   0.000417415 |          71.9467 | s002    |
| a7ls5_527fcaeaacc0b31d | TSRank(mark_index_basis_bps,72)                                 | basis_premium_like | single            | L3_liquidity_tier_relative_return  |                 1 |                   0.347233 |                 4.44619  |             -0.000842008 |                   0.000483615 |          70.2065 | s001    |
| a7ls5_527fcaeaacc0b31d | TSRank(mark_index_basis_bps,72)                                 | basis_premium_like | single            | L0_raw_forward_return              |                 1 |                   0.368379 |                 4.45941  |             -0.00083488  |                   0.00050338  |          68.1248 | s001    |
| a7ls5_527fcaeaacc0b31d | TSRank(mark_index_basis_bps,72)                                 | basis_premium_like | single            | L1_cross_sectional_relative_return |                 1 |                   0.368379 |                 4.45941  |             -0.00083488  |                   0.00050338  |          68.1248 | s001    |
| a7ls5_093c274318822859 | Delta(mark_index_basis_bps,2)                                   | basis_premium_like | single            | L0_raw_forward_return              |                 1 |                   0.344068 |                 2.05867  |             -0.00134944  |                   0.000182689 |          67.8345 | s000    |

## Authorization

- Aggregation only.
- Authorizes A7LS-6 deep follow-up contract drafting only if PASS.
- Does not authorize formula search, alpha proof, shadow, paper, or live.