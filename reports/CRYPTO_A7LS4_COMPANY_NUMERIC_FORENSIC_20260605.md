# CRYPTO A7LS-4 COMPANY NUMERIC FORENSIC

Generated: 2026-06-05T10:05:02Z

## Decision

`PASS_A7LS4_COMPANY_NUMERIC_FORENSIC_READY_FOR_A7LS5_REPAIR_AND_FOLLOWUP`

## Summary

- clue_rows: 45
- non_l7_clue_rows: 22
- l7_rank_label_clue_rows: 23
- response_rows: 33280
- portfolio_rows: 143
- pass_shards: 6
- missing_field_shards: 3
- top_clue_semantic_pair_share: 0.378
- shortlist_rows: 22

## Clue By Label

| label_family                      |   rows |
|:----------------------------------|-------:|
| L7_ranked_future_return           |     23 |
| L5_vol_adjusted_return            |     20 |
| L3_liquidity_tier_relative_return |      2 |

## Clue By Semantic Pair

| semantic_pair                     |   rows |
|:----------------------------------|-------:|
| low_prior_axes|basis_premium_like |     17 |
| basis_premium_like                |     11 |
| liquidity_like                    |      7 |
| open_interest_like                |      7 |
| price_like                        |      3 |

## Response Blockers

| blocker_family             |   rows |       share |
|:---------------------------|-------:|------------:|
| pre_may_unstable           |  24886 | 0.747776    |
| control_dominated          |   6186 | 0.185877    |
| lag_fragile                |   1524 | 0.0457933   |
| numeric_clue               |    462 | 0.0138822   |
| rank_label_diagnostic_clue |    202 | 0.00606971  |
| other                      |     20 | 0.000600962 |

## Missing Field Shards

| shard   | decision                        | blockers               | root_cause                       | missing_field_family   |
|:--------|:--------------------------------|:-----------------------|:---------------------------------|:-----------------------|
| s007    | HOLD_A7LS3HRS007_MISSING_FIELDS | missing_numeric_fields | panel_missing_listing_age_fields | listing_age_like       |
| s013    | HOLD_A7LS3HRS013_MISSING_FIELDS | missing_numeric_fields | panel_missing_listing_age_fields | listing_age_like       |
| s014    | HOLD_A7LS3HRS014_MISSING_FIELDS | missing_numeric_fields | panel_missing_listing_age_fields | listing_age_like       |

## Shortlist

| blueprint_id           | expression                                                                          | semantic_pair                     | motif        | label_family           |   label_horizon_h | decision                 | shard   |   score_no_may |   control_ratio_premay_max |   robust_min_tstat_floor |   cost10_recent_oriented |   one_bar_lag_recent_oriented | skeleton_key          |   finite_share |   nonzero_share |   shortlist_score |
|:-----------------------|:------------------------------------------------------------------------------------|:----------------------------------|:-------------|:-----------------------|------------------:|:-------------------------|:--------|---------------:|---------------------------:|-------------------------:|-------------------------:|------------------------------:|:----------------------|---------------:|----------------:|------------------:|
| a7ls1_12a10b4f6406b9f3 | Delta(mark_index_basis_bps,12)                                                      | basis_premium_like                | single       | L5_vol_adjusted_return |                 8 | A7LS3HRS008_NUMERIC_CLUE | s008    |       395.416  |                   0.831823 |                 2.32574  |                0.388248  |                     0.247474  | skel_1d39996e97d5ace0 |       0.996265 |        0.998429 |          390.408  |
| a7ls1_0d31d5485da3efcc | Neg(Mul(Abs(ZScore(Mean(premium_count,72))),Delta(mark_index_basis_bps,12)))        | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 8 | A7LS3HRS012_NUMERIC_CLUE | s012    |       393.839  |                   0.892562 |                -0.654703 |                0.386732  |                     0.241479  | skel_6973b6ef87ba0b0d |       0.890836 |        0.998441 |          372.715  |
| a7ls1_863cbcd7c72eacad | Delta(mark_index_basis_bps,2)                                                       | basis_premium_like                | single       | L5_vol_adjusted_return |                24 | A7LS3HRS009_NUMERIC_CLUE | s009    |       288.099  |                   0.663244 |                 2.11978  |                0.280763  |                     0.165549  | skel_1d39996e97d5ace0 |       0.999138 |        0.998679 |          285.433  |
| a7ls1_05cf24eeecfd6a55 | Neg(Mul(premium_count,TSRank(mark_index_basis_bps,24)))                             | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 8 | A7LS3HRS010_NUMERIC_CLUE | s010    |       305.119  |                   0.867957 |                -0.870935 |                0.297987  |                     0.192324  | skel_03a79df769f8f145 |       0.993105 |        1        |          283.405  |
| a7ls1_16a5caf2ffe2a929 | Mul(Delta(mark_index_basis_bps,2),Sign(Abs(ZScore(Mean(mark_trade_basis_bps,24))))) | basis_premium_like                | gated_sign   | L5_vol_adjusted_return |                24 | A7LS3HRS000_NUMERIC_CLUE | s000    |       287.86   |                   0.902783 |                 2.11978  |                0.280763  |                     0.165549  | skel_437d739eeb4ca960 |       0.993105 |        0.998671 |          280.403  |
| a7ls1_2329004bd399a4dd | Neg(Mul(premium_count,Delta(mark_trade_basis_bps,168)))                             | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 8 | A7LS3HRS011_NUMERIC_CLUE | s011    |       236.452  |                   0.554175 |                 2.39445  |                0.229006  |                     0.0927706 | skel_03a79df769f8f145 |       0.951451 |        0.88959  |          237.34   |
| a7ls1_06d5726f5d1f3e8b | Neg(Mul(Decay(premium_count,24),Delta(mark_trade_basis_bps,168)))                   | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 8 | A7LS3HRS011_NUMERIC_CLUE | s011    |       235.413  |                   0.5547   |                 2.39445  |                0.227968  |                     0.0919349 | skel_5aa3c6bd7cbc604b |       0.951451 |        0.88959  |          236.291  |
| a7ls1_7f03951e0f6aff50 | Delta(mark_index_basis_bps,24)                                                      | basis_premium_like                | single       | L5_vol_adjusted_return |                 1 | A7LS3HRS011_NUMERIC_CLUE | s011    |       167.608  |                   0.831063 |                 7.33263  |                0.16044   |                     0.0494657 | skel_1d39996e97d5ace0 |       0.992818 |        0.997742 |          187.65   |
| a7ls1_0cc2210239b45ef6 | Neg(Mul(ZScore(Mean(premium_count,168)),TSRank(mark_index_basis_bps,24)))           | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 4 | A7LS3HRS011_NUMERIC_CLUE | s011    |       173.749  |                   0.85256  |                 0.444071 |                0.166602  |                     0.0595271 | skel_9995be0537f8d000 |       0.982189 |        1        |          158.918  |
| a7ls1_1051ff7f77666261 | Neg(Mul(Abs(ZScore(Mean(premium_count,72))),ZScore(Mean(mark_index_basis_bps,2))))  | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 1 | A7LS3HRS012_NUMERIC_CLUE | s012    |       118.348  |                   0.905301 |                 4.24989  |                0.111253  |                     0.0323723 | skel_e0687779aae44bd6 |       0.890836 |        1        |          121.491  |
| a7ls1_3dc585e9cbfa19cb | Neg(Mul(premium_count,ZScore(Mean(mark_index_basis_bps,2))))                        | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 1 | A7LS3HRS009_NUMERIC_CLUE | s009    |       111.3    |                   0.949235 |                 4.35241  |                0.104249  |                     0.0319818 | skel_b3b832e70085d952 |       0.999425 |        1        |          114.078  |
| a7ls1_0bf34355b4a7a5a7 | Neg(Mul(Mean(premium_count,4),ZScore(Mean(mark_index_basis_bps,2))))                | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 1 | A7LS3HRS009_NUMERIC_CLUE | s009    |       111.032  |                   0.956261 |                 4.35241  |                0.103988  |                     0.0320676 | skel_7a46080bacc0bcf0 |       0.998851 |        1        |          113.669  |
| a7ls1_09b48e96ad2d0f9d | Mul(Delta(mark_index_basis_bps,4),Sign(Mean(mark_trade_basis_bps,168)))             | basis_premium_like                | gated_sign   | L5_vol_adjusted_return |                 1 | A7LS3HRS000_NUMERIC_CLUE | s000    |        91.8715 |                   0.283247 |                 4.20254  |                0.0841547 |                     0.0305558 | skel_3afee12eb6a9078f |       0.993105 |        0.998352 |          107.219  |
| a7ls1_0b14870f0c217c0c | Neg(Mul(premium_count,Delta(premium_close_bps,12)))                                 | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 1 | A7LS3HRS012_NUMERIC_CLUE | s012    |        86.7577 |                   0.521876 |                 2.70775  |                0.0792796 |                     0.0447412 | skel_03a79df769f8f145 |       0.996265 |        0.826542 |           89.8589 |
| a7ls1_64f4385708e3b520 | Delta(premium_close_bps,24)                                                         | basis_premium_like                | single       | L5_vol_adjusted_return |                 1 | A7LS3HRS012_NUMERIC_CLUE | s012    |        92.0649 |                   0.774623 |                 2.39074  |                0.0848395 |                     0.0471642 | skel_1d39996e97d5ace0 |       0.992818 |        0.82886  |           88.5261 |
| a7ls1_08b0eb0915a2c45e | Neg(Mul(Mean(premium_count,24),TSRank(premium_close_bps,24)))                       | low_prior_axes|basis_premium_like | control_flip | L5_vol_adjusted_return |                 1 | A7LS3HRS009_NUMERIC_CLUE | s009    |        83.2445 |                   0.844784 |                 2.76111  |                0.0760893 |                     0.0371197 | skel_5aa3c6bd7cbc604b |       0.993105 |        1        |           80.1544 |
| a7ls1_0bb7b0b8b56eb2c3 | Mul(Delta(mark_index_basis_bps,1),Sign(Mean(premium_close_bps,12)))                 | basis_premium_like                | gated_sign   | L5_vol_adjusted_return |                 8 | A7LS3HRS002_NUMERIC_CLUE | s002    |        91.4556 |                   0.571438 |                -0.524667 |                0.0840271 |                     0.0357776 | skel_3afee12eb6a9078f |       0.996553 |        0.980503 |           77.4035 |
| a7ls1_0dcc223f83772ffa | Mul(mark_index_basis_bps,Sign(Mean(mark_trade_basis_bps,12)))                       | basis_premium_like                | gated_sign   | L5_vol_adjusted_return |                 1 | A7LS3HRS002_NUMERIC_CLUE | s002    |        60.3028 |                   0.859051 |                 2.69004  |                0.0531618 |                     0.0174924 | skel_a2f58ee62d9e7ad2 |       0.996553 |        0.987298 |           56.5719 |
| a7ls1_5be46d6af537a5ba | Mul(Delta(trade_close,1),Sign(mark_close))                                          | price_like                        | gated_sign   | L5_vol_adjusted_return |                 1 | A7LS3HRS006_NUMERIC_CLUE | s006    |        54.8986 |                   0.814872 |                 1.33953  |                0.0477135 |                     0.0144941 | skel_136259b72205469f |       0.999425 |        0.964483 |           45.2988 |
| a7ls1_2b8e8f97a11c94b9 | Mul(Delta(trade_close,1),Sign(Mean(mark_close,4)))                                  | price_like                        | gated_sign   | L5_vol_adjusted_return |                 1 | A7LS3HRS006_NUMERIC_CLUE | s006    |        54.8557 |                   0.857746 |                 1.33953  |                0.0477135 |                     0.0144941 | skel_3afee12eb6a9078f |       0.998851 |        0.964463 |           44.3984 |

## Authorization

- Forensic only.
- Does not authorize search, alpha proof, shadow, paper, or live.
- If passed, only authorizes drafting A7LS-5 repair/follow-up contract.