# CRYPTO A7LS19 CHECKPOINT ARBITRATION

Generated: 2026-06-07T12:21:35Z

## Decision

`PASS_A7LS19_DIVERSIFIED_CHECKPOINT_QUEUE_READY_FOR_A7LS20`

## Manifest

```json
{
  "authorizes_a7ls20_checkpoint_deep_replay": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "checkpoint_basis_premium_count": 70,
  "checkpoint_basis_premium_count_cap": 70,
  "checkpoint_basis_premium_share": 0.5691056910569106,
  "checkpoint_l5_share": 0.8455284552845529,
  "checkpoint_max_semantic_pair_share": 0.0975609756097561,
  "checkpoint_max_skeleton_share": 0.06504065040650407,
  "checkpoint_non_l5_count": 19,
  "checkpoint_queue_count": 123,
  "control_primary_max": 0.9,
  "control_strong_max": 0.8,
  "decision": "PASS_A7LS19_DIVERSIFIED_CHECKPOINT_QUEUE_READY_FOR_A7LS20",
  "excludes_l7_from_checkpoint": true,
  "excludes_low_prior_axes_from_checkpoint": true,
  "excludes_placebo_from_checkpoint": true,
  "executes_search": false,
  "generated_at": "2026-06-07T12:21:35Z",
  "input_selected_count": 2258,
  "input_stage": "A7LS-18",
  "stage": "A7LS-19",
  "strict_non_l7_eligible_count": 329,
  "strong_non_l7_eligible_count": 228,
  "target_queue_size": 128,
  "uses_may": false,
  "warnings": [
    "basis_premium_still_dominant"
  ]
}
```

## Interpretation

A7LS19 does not run search or replay. It arbitrates the completed A7LS18 selected queue into a stricter, non-L7, role-clean checkpoint queue.

Key hard filters:

- excludes L7 ranked-return diagnostic-only rows from checkpoint promotion
- excludes placebo and low-prior semantic axes
- requires pre-May all-positive, lag survival, robust survival, positive cost10
- requires control_ratio_premay_max < 0.9
- applies semantic pair, skeleton, label-family, and basis/premium concentration caps

## Source Family Caps

| source_token       |   selected_count |   selected_share |   strict_eligible_count |   strict_eligible_share |
|:-------------------|-----------------:|-----------------:|------------------------:|------------------------:|
| basis_premium_like |               70 |        0.569106  |                     261 |               0.793313  |
| price_like         |               31 |        0.252033  |                      60 |               0.182371  |
| positioning_like   |               30 |        0.243902  |                      73 |               0.221884  |
| taker_flow_like    |               19 |        0.154472  |                      29 |               0.0881459 |
| liquidity_like     |               18 |        0.146341  |                      40 |               0.121581  |
| listing_age_like   |               15 |        0.121951  |                      54 |               0.164134  |
| regime_state       |               12 |        0.097561  |                      15 |               0.0455927 |
| open_interest_like |               12 |        0.097561  |                      22 |               0.0668693 |
| funding_state_like |                9 |        0.0731707 |                      26 |               0.0790274 |
| volatility_like    |                6 |        0.0487805 |                      28 |               0.0851064 |

## Label Distribution

| label_family                       |   count |     share |
|:-----------------------------------|--------:|----------:|
| L5_vol_adjusted_return             |     104 | 0.845528  |
| L3_liquidity_tier_relative_return  |       7 | 0.0569106 |
| L1_cross_sectional_relative_return |       6 | 0.0487805 |
| L0_raw_forward_return              |       6 | 0.0487805 |

## Semantic Pair Distribution

| semantic_pair                                               |   count |      share |
|:------------------------------------------------------------|--------:|-----------:|
| basis_premium_like                                          |      12 | 0.097561   |
| basis_premium_like|liquidity_like                           |      12 | 0.097561   |
| basis_premium_like|price_like                               |      11 | 0.0894309  |
| basis_premium_like|positioning_like                         |       9 | 0.0731707  |
| basis_premium_like|listing_age_like                         |       7 | 0.0569106  |
| positioning_like|basis_premium_like                         |       6 | 0.0487805  |
| price_like|positioning_like                                 |       5 | 0.0406504  |
| taker_flow_like                                             |       5 | 0.0406504  |
| open_interest_like|positioning_like                         |       4 | 0.0325203  |
| regime_state|price_like                                     |       4 | 0.0325203  |
| open_interest_like|taker_flow_like                          |       4 | 0.0325203  |
| price_like                                                  |       3 | 0.0243902  |
| basis_premium_like|volatility_like                          |       3 | 0.0243902  |
| taker_flow_like|listing_age_like                            |       3 | 0.0243902  |
| positioning_like|taker_flow_like                            |       2 | 0.0162602  |
| basis_premium_like|open_interest_like                       |       2 | 0.0162602  |
| price_like|liquidity_like                                   |       2 | 0.0162602  |
| volatility_like|liquidity_rank_active_universe|regime_state |       2 | 0.0162602  |
| funding_state_like|basis_premium_like                       |       2 | 0.0162602  |
| listing_age_like|basis_premium_like                         |       2 | 0.0162602  |
| basis_premium_like|taker_flow_like                          |       1 | 0.00813008 |
| basis_premium_like|regime_state                             |       1 | 0.00813008 |
| basis_premium_like|funding_state_like                       |       1 | 0.00813008 |
| basis_premium|positioning_flow|regime_state                 |       1 | 0.00813008 |
| liquidity_like                                              |       1 | 0.00813008 |
| funding_state_like|liquidity_like                           |       1 | 0.00813008 |
| funding_state_like                                          |       1 | 0.00813008 |
| positioning_like|regime_state                               |       1 | 0.00813008 |
| positioning_like|listing_age_like                           |       1 | 0.00813008 |
| listing_age_like|liquidity_like                             |       1 | 0.00813008 |
| positioning_like                                            |       1 | 0.00813008 |
| funding_state_like|open_interest_like                       |       1 | 0.00813008 |
| funding_state_like|positioning_like                         |       1 | 0.00813008 |
| funding_state_like|regime_state                             |       1 | 0.00813008 |
| price_like|basis_premium_like                               |       1 | 0.00813008 |
| price_like|regime_state                                     |       1 | 0.00813008 |
| price_like|open_interest_like                               |       1 | 0.00813008 |
| price_like|listing_age_like                                 |       1 | 0.00813008 |
| price_like|funding_state_like                               |       1 | 0.00813008 |
| taker_flow_like|liquidity_like                              |       1 | 0.00813008 |

## Rejection Summary

| a7ls19_reject_reason                                                    |   count |
|:------------------------------------------------------------------------|--------:|
| rank_label_diagnostic_only                                              |     990 |
| rank_label_diagnostic_only;control_ratio_too_high                       |     557 |
| strict_non_l7_eligible                                                  |     329 |
| control_ratio_too_high                                                  |     110 |
| rank_label_diagnostic_only;placebo_semantic_pair                        |      81 |
| cost10_not_positive                                                     |      42 |
| placebo_semantic_pair                                                   |      41 |
| rank_label_diagnostic_only;low_prior_axis                               |      33 |
| rank_label_diagnostic_only;placebo_semantic_pair;control_ratio_too_high |      20 |
| low_prior_axis                                                          |      12 |
| rank_label_diagnostic_only;low_prior_axis;control_ratio_too_high        |      11 |
| placebo_semantic_pair;control_ratio_too_high                            |      10 |
| control_ratio_too_high;cost10_not_positive                              |       9 |
| low_prior_axis;control_ratio_too_high                                   |       6 |
| placebo_semantic_pair;cost10_not_positive                               |       6 |
| low_prior_axis;cost10_not_positive                                      |       1 |

## Top Checkpoint Candidates

|   a7ls19_rank | blueprint_id            | semantic_pair                         | motif          | label_family           |   label_horizon_h |   control_ratio_premay_max |   cost10_recent_oriented |   one_bar_lag_recent_oriented |   score_no_may | expression                                                                                                                                      |
|--------------:|:------------------------|:--------------------------------------|:---------------|:-----------------------|------------------:|---------------------------:|-------------------------:|------------------------------:|---------------:|:------------------------------------------------------------------------------------------------------------------------------------------------|
|             1 | a7ls15_54ad1703758fd224 | basis_premium_like|listing_age_like   | signed_spread  | L5_vol_adjusted_return |                 4 |                   0.553488 |                 1.46333  |                     0.885406  |       1470.77  | Mul(Sub(CSRank(Delta(mark_trade_basis_bps,336)),CSRank(Delta(age_percentile_active_universe,8))),Sign(Delta(age_percentile_active_universe,8))) |
|             2 | a7ls15_204d2b4357f56b5a | taker_flow_like                       | single         | L5_vol_adjusted_return |                24 |                   0.764958 |                 0.994447 |                     1.0034    |       1001.68  | Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,48)))                                                                                          |
|             3 | a7ls15_89afcf1b006412d0 | taker_flow_like|listing_age_like      | state_gate     | L5_vol_adjusted_return |                24 |                   0.596173 |                 0.792431 |                     0.769592  |        799.834 | Mul(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))),Sign(Mean(Abs(ZScore(Mean(sqrt_listing_age_days,72))),24)))                          |
|             4 | a7ls15_63413450465c681d | taker_flow_like|listing_age_like      | gated_sign     | L5_vol_adjusted_return |                24 |                   0.62332  |                 0.792431 |                     0.769592  |        799.807 | Mul(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))),Sign(TSRank(listing_age_days,24)))                                                   |
|             5 | a7ls15_6dde8445b9dc0331 | basis_premium_like|listing_age_like   | state_gate     | L5_vol_adjusted_return |                 8 |                   0.780694 |                 0.689151 |                     0.50534   |        696.37  | Mul(Delta(mark_index_basis_bps,2),Sign(Mean(Delta(age_percentile_active_universe,24),24)))                                                      |
|             6 | a7ls15_6b338a109f660b8c | basis_premium_like|liquidity_like     | signed_spread  | L5_vol_adjusted_return |                24 |                   0.790837 |                 0.623865 |                     0.634236  |        631.074 | Mul(Sub(CSRank(Decay(premium_abs_state,240)),CSRank(ZScore(Mean(trade_volume,12)))),Sign(ZScore(Mean(trade_volume,12))))                        |
|             7 | a7ls15_3df186f6ef65ad1b | taker_flow_like                       | sub            | L5_vol_adjusted_return |                24 |                   0.718839 |                 0.512251 |                     0.511177  |        519.532 | Sub(ZScore(Mean(taker_buy_sell_volume_ratio_mean,24)),ZScore(Mean(taker_buy_sell_volume_ratio_last,4)))                                         |
|             8 | a7ls15_4dcdc7b425d7a981 | taker_flow_like|volatility_like       | sub            | L5_vol_adjusted_return |                24 |                   0.616448 |                 0.425204 |                     0.398806  |        432.588 | Sub(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))),Delta(realized_vol_168h,48))                                                         |
|             9 | a7ls15_defc4a5a369f820f | basis_premium_like                    | gated_sign     | L5_vol_adjusted_return |                 8 |                   0.794953 |                 0.4284   |                     0.347993  |        435.605 | Mul(TSRank(mark_index_basis_bps,240),Sign(Decay(mark_trade_basis_bps,504)))                                                                     |
|            10 | a7ls15_b71e18b57ead6ad9 | taker_flow_like|liquidity_like        | sub            | L5_vol_adjusted_return |                24 |                   0.763716 |                 0.366477 |                     0.388917  |        373.714 | Sub(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,48))),ZScore(Mean(median_quote_volume_168h,72)))                                           |
|            11 | a7ls15_5275f07bf670d712 | basis_premium_like|liquidity_like     | relative_shock | L5_vol_adjusted_return |                24 |                   0.716807 |                 0.402638 |                     0.38808   |        409.921 | Mul(Delta(Abs(ZScore(Mean(basis_abs_168h,16))),4),ZScore(Delta(trade_volume,168)))                                                              |
|            12 | a7ls15_9c1cfb5e02844b76 | basis_premium_like                    | single         | L5_vol_adjusted_return |                 8 |                   0.619643 |                 0.388248 |                     0.247474  |        395.628 | Delta(mark_index_basis_bps,12)                                                                                                                  |
|            13 | a7ls15_8d5c9cb072d21cf6 | basis_premium_like|listing_age_like   | gated_sign     | L5_vol_adjusted_return |                 8 |                   0.619643 |                 0.388248 |                     0.247474  |        395.628 | Mul(Delta(mark_index_basis_bps,12),Sign(Mean(log1p_listing_age_days,168)))                                                                      |
|            14 | a7ls15_ddf2a5a6c7583143 | basis_premium_like|listing_age_like   | mul            | L5_vol_adjusted_return |                 8 |                   0.643259 |                 0.386823 |                     0.247047  |        394.18  | Mul(Delta(mark_index_basis_bps,12),listing_age_days)                                                                                            |
|            15 | a7ls15_d0b0d2d2c2231ec3 | listing_age_like|basis_premium_like   | mul            | L5_vol_adjusted_return |                 8 |                   0.643259 |                 0.386823 |                     0.247047  |        394.18  | Mul(Decay(listing_age_days,8),Delta(mark_index_basis_bps,12))                                                                                   |
|            16 | a7ls15_7355ef8aa37d5217 | basis_premium_like                    | signed_spread  | L5_vol_adjusted_return |                 8 |                   0.658838 |                 0.339446 |                     0.126917  |        346.787 | Mul(Sub(CSRank(Delta(mark_trade_basis_bps,2)),CSRank(TSRank(mark_index_basis_bps,336))),Sign(TSRank(mark_index_basis_bps,336)))                 |
|            17 | a7ls15_f0887dbb68165e6d | basis_premium_like|liquidity_like     | mul            | L5_vol_adjusted_return |                24 |                   0.666064 |                 0.339722 |                     0.242105  |        347.056 | Mul(TSRank(mark_trade_basis_bps,6),Abs(ZScore(Mean(trade_volume,720))))                                                                         |
|            18 | a7ls15_21e2eb5bd528cfa5 | basis_premium_like                    | state_gate     | L5_vol_adjusted_return |                24 |                   0.798349 |                 0.333251 |                     0.300019  |        340.453 | Mul(TSRank(mark_index_basis_bps,3),Sign(Mean(ZScore(Mean(premium_abs_168h,36)),24)))                                                            |
|            19 | a7ls15_02213ddd0b85be23 | basis_premium_like                    | sub            | L5_vol_adjusted_return |                24 |                   0.665854 |                 0.316898 |                     0.203485  |        324.232 | Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(premium_abs_168h,72)))                                                                            |
|            20 | a7ls15_113ef02b00ffc25f | basis_premium_like|price_like         | mul            | L5_vol_adjusted_return |                 8 |                   0.530896 |                 0.304454 |                     0.202112  |        311.923 | Mul(TSRank(mark_index_basis_bps,48),Abs(ZScore(Mean(index_close,240))))                                                                         |
|            21 | a7ls15_b8e42dcf547ae915 | basis_premium_like|price_like         | sub            | L5_vol_adjusted_return |                24 |                   0.556022 |                 0.294657 |                     0.17957   |        302.101 | Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(mark_close,72)))                                                                                  |
|            22 | a7ls15_42dc6539d51aca8b | basis_premium_like|positioning_like   | mul            | L5_vol_adjusted_return |                 8 |                   0.683949 |                 0.299266 |                     0.14609   |        306.582 | Mul(CSRank(mark_trade_basis_bps),Abs(ZScore(Mean(global_long_short_account_ratio_mean,120))))                                                   |
|            23 | a7ls15_36d989bd60108c96 | basis_premium_like|positioning_like   | sub            | L5_vol_adjusted_return |                 8 |                   0.654123 |                 0.291311 |                     0.101871  |        298.657 | Sub(TSRank(mark_trade_basis_bps,72),Delta(top_long_short_position_ratio_last,3))                                                                |
|            24 | a7ls15_3a47210fb17ce6d5 | basis_premium_like|liquidity_like     | safe_div_abs   | L5_vol_adjusted_return |                 8 |                   0.694528 |                 0.29337  |                     0.0797102 |        300.675 | SafeDiv(Delta(mark_trade_basis_bps,6),Abs(Mean(trade_quote_volume,720)))                                                                        |
|            25 | a7ls15_b0801a2fcacafcc5 | basis_premium_like                    | sub            | L5_vol_adjusted_return |                 8 |                   0.739944 |                 0.289913 |                     0.157316  |        297.173 | Sub(Delta(mark_index_basis_bps,6),Delta(mark_trade_basis_bps,16))                                                                               |
|            26 | a7ls15_7d34c860f8f45ca4 | basis_premium_like|liquidity_like     | sub            | L5_vol_adjusted_return |                 8 |                   0.712748 |                 0.286143 |                     0.280392  |        293.43  | Sub(ZScore(Mean(premium_abs_168h,36)),Delta(log_quote_volume_168h,96))                                                                          |
|            27 | a7ls15_82c495acffbea470 | basis_premium_like                    | sub            | L5_vol_adjusted_return |                 8 |                   0.50885  |                 0.263255 |                     0.0975651 |        270.746 | Sub(TSRank(mark_trade_basis_bps,6),TSRank(mark_index_basis_bps,24))                                                                             |
|            28 | a7ls15_83b2ec53c58ee01a | listing_age_like|basis_premium_like   | mul            | L5_vol_adjusted_return |                24 |                   0.78401  |                 0.27953  |                     0.170438  |        286.746 | Mul(ZScore(Mean(listing_age_days,336)),Delta(mark_index_basis_bps,3))                                                                           |
|            29 | a7ls15_f8fbde80779ec39d | basis_premium_like                    | spread_rank    | L5_vol_adjusted_return |                 8 |                   0.673381 |                 0.263985 |                     0.143874  |        271.311 | Sub(CSRank(TSRank(premium_close_bps,6)),CSRank(TSRank(mark_index_basis_bps,24)))                                                                |
|            30 | a7ls15_7acc9ae07db7a40b | positioning_like|basis_premium_like   | spread_rank    | L5_vol_adjusted_return |                 8 |                   0.733494 |                 0.265373 |                     0.171655  |        272.64  | Sub(CSRank(Delta(top_global_account_divergence,6)),CSRank(Delta(mark_trade_basis_bps,16)))                                                      |
|            31 | a7ls15_530252b40793410f | basis_premium_like|liquidity_like     | safe_div_abs   | L5_vol_adjusted_return |                 8 |                   0.51363  |                 0.248237 |                     0.113327  |        255.723 | SafeDiv(Delta(mark_trade_basis_bps,168),Abs(Abs(ZScore(Mean(trade_quote_volume,24)))))                                                          |
|            32 | a7ls15_01ea6cfe8374ef71 | basis_premium_like|liquidity_like     | gated_sign     | L5_vol_adjusted_return |                 8 |                   0.52182  |                 0.247103 |                     0.0638974 |        254.581 | Mul(TSRank(mark_trade_basis_bps,36),Sign(Mean(volume_volatility_ratio_168h,2)))                                                                 |
|            33 | a7ls15_2c7b31909d6612ec | basis_premium_like|price_like         | gated_sign     | L5_vol_adjusted_return |                 8 |                   0.52182  |                 0.247103 |                     0.0638974 |        254.581 | Mul(TSRank(mark_trade_basis_bps,36),Sign(Mean(index_close,2)))                                                                                  |
|            34 | a7ls15_17b0e237103a9ddc | basis_premium_like|volatility_like    | gated_sign     | L5_vol_adjusted_return |                 8 |                   0.52182  |                 0.247103 |                     0.0638974 |        254.581 | Mul(TSRank(mark_trade_basis_bps,36),Sign(Mean(realized_vol_72h,2)))                                                                             |
|            35 | a7ls15_4dc92dc60d615c89 | open_interest_like|taker_flow_like    | smooth_mul     | L5_vol_adjusted_return |                24 |                   0.780788 |                 0.196797 |                     0.215347  |        204.016 | Mean(Mul(ZScore(Mean(open_interest_value_mean,120)),Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)),4)                                     |
|            36 | a7ls15_a03a6be747eccb79 | basis_premium_like|positioning_like   | mul            | L5_vol_adjusted_return |                 4 |                   0.670905 |                 0.243074 |                     0.119595  |        250.404 | Mul(Delta(mark_index_basis_bps,12),Decay(top_long_short_account_ratio_last,48))                                                                 |
|            37 | a7ls15_d90c7d57fdf5069b | positioning_like|basis_premium_like   | sub            | L5_vol_adjusted_return |                 8 |                   0.719638 |                 0.245629 |                     0.145748  |        252.91  | Sub(Delta(top_long_short_position_ratio_mean,3),TSRank(mark_index_basis_bps,24))                                                                |
|            38 | a7ls15_714da0f57e6aaedd | basis_premium_like|volatility_like    | safe_div_abs   | L5_vol_adjusted_return |                 8 |                   0.529825 |                 0.225987 |                     0.0722302 |        233.457 | SafeDiv(Delta(mark_trade_basis_bps,168),Abs(Abs(ZScore(Mean(realized_vol_24h,24)))))                                                            |
|            39 | a7ls15_d07470d7e6c54d70 | basis_premium_like|price_like         | signed_spread  | L5_vol_adjusted_return |                 8 |                   0.741507 |                 0.234531 |                     0.0812235 |        241.789 | Mul(Sub(CSRank(TSRank(mark_trade_basis_bps,120)),CSRank(TSRank(trade_close,3))),Sign(TSRank(trade_close,3)))                                    |
|            40 | a7ls15_c5541bbe8921e72d | funding_state_like|basis_premium_like | safe_div_abs   | L5_vol_adjusted_return |                 8 |                   0.749858 |                 0.229217 |                     0.144711  |        236.468 | SafeDiv(Abs(ZScore(Mean(funding_rate_update_age_hours,8))),Abs(TSRank(mark_index_basis_bps,6)))                                                 |

## Authorization

- A7LS20 checkpoint deep replay / marginal contribution audit: authorized only if decision is PASS.
- New formula search: not authorized.
- Alpha proof / shadow / paper / live: not authorized.
