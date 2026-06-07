# CRYPTO A7LS20 CHECKPOINT DEEP AUDIT

Generated: 2026-06-07T13:19:56Z

## Decision

`PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET`

## Manifest

```json
{
  "authorizes_a7ls21_company_deep_replay_packet": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "checkpoint_basis_premium_count": 70,
  "checkpoint_basis_premium_share": 0.5691056910569106,
  "checkpoint_count": 123,
  "checkpoint_l5_count": 104,
  "checkpoint_l5_share": 0.8455284552845529,
  "checkpoint_max_semantic_pair_share": 0.0975609756097561,
  "checkpoint_max_skeleton_share": 0.06504065040650407,
  "checkpoint_semantic_pair_count": 43,
  "checkpoint_skeleton_count": 50,
  "decision": "PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET",
  "deep_audit_type": "checkpoint_metric_deep_audit_and_marginal_contribution_proxy",
  "executes_new_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-07T13:19:56Z",
  "input_checkpoint_count": 123,
  "input_stage": "A7LS-19",
  "marginal_basis_premium_count": 24,
  "marginal_basis_premium_share": 0.5,
  "marginal_count": 48,
  "marginal_l5_count": 32,
  "marginal_l5_share": 0.6666666666666666,
  "marginal_max_semantic_pair_share": 0.10416666666666667,
  "marginal_max_skeleton_share": 0.08333333333333333,
  "marginal_queue_count": 48,
  "marginal_semantic_pair_count": 23,
  "marginal_skeleton_count": 33,
  "stage": "A7LS-20",
  "target_marginal_queue": 48,
  "uses_may": false,
  "warnings": [
    "marginal_basis_premium_high"
  ]
}
```

## Interpretation

A7LS20 does not run new search or new replay. It deep-audits the A7LS19 checkpoint metrics and builds a marginal-contribution proxy queue for the next replay packet.

The marginal queue is deliberately stricter than A7LS19: it caps basis/premium, L5, semantic pair, skeleton, and metric-vector proxy similarity.

## Checkpoint Source Distribution

| source_token       |   count |     share |
|:-------------------|--------:|----------:|
| basis_premium_like |      70 | 0.569106  |
| price_like         |      31 | 0.252033  |
| positioning_like   |      30 | 0.243902  |
| taker_flow_like    |      19 | 0.154472  |
| liquidity_like     |      18 | 0.146341  |
| listing_age_like   |      15 | 0.121951  |
| regime_state       |      12 | 0.097561  |
| open_interest_like |      12 | 0.097561  |
| funding_state_like |       9 | 0.0731707 |
| volatility_like    |       6 | 0.0487805 |

## Marginal Source Distribution

| source_token       |   count |     share |
|:-------------------|--------:|----------:|
| basis_premium_like |      24 | 0.5       |
| taker_flow_like    |      13 | 0.270833  |
| positioning_like   |       9 | 0.1875    |
| liquidity_like     |       8 | 0.166667  |
| listing_age_like   |       7 | 0.145833  |
| open_interest_like |       7 | 0.145833  |
| price_like         |       5 | 0.104167  |
| regime_state       |       5 | 0.104167  |
| funding_state_like |       4 | 0.0833333 |
| volatility_like    |       3 | 0.0625    |

## Marginal Label Distribution

| label_family                       |   count |    share |
|:-----------------------------------|--------:|---------:|
| L5_vol_adjusted_return             |      32 | 0.666667 |
| L3_liquidity_tier_relative_return  |       6 | 0.125    |
| L1_cross_sectional_relative_return |       5 | 0.104167 |
| L0_raw_forward_return              |       5 | 0.104167 |

## Marginal Semantic Pair Distribution

| semantic_pair                                               |   count |     share |
|:------------------------------------------------------------|--------:|----------:|
| basis_premium_like                                          |       5 | 0.104167  |
| basis_premium_like|liquidity_like                           |       5 | 0.104167  |
| basis_premium_like|listing_age_like                         |       4 | 0.0833333 |
| basis_premium_like|price_like                               |       4 | 0.0833333 |
| open_interest_like|taker_flow_like                          |       4 | 0.0833333 |
| taker_flow_like                                             |       4 | 0.0833333 |
| positioning_like|basis_premium_like                         |       3 | 0.0625    |
| volatility_like|liquidity_rank_active_universe|regime_state |       2 | 0.0416667 |
| open_interest_like|positioning_like                         |       2 | 0.0416667 |
| basis_premium_like|positioning_like                         |       2 | 0.0416667 |
| basis_premium|positioning_flow|regime_state                 |       1 | 0.0208333 |
| funding_state_like|liquidity_like                           |       1 | 0.0208333 |
| funding_state_like|regime_state                             |       1 | 0.0208333 |
| listing_age_like|basis_premium_like                         |       1 | 0.0208333 |
| funding_state_like|open_interest_like                       |       1 | 0.0208333 |
| listing_age_like|liquidity_like                             |       1 | 0.0208333 |
| funding_state_like|positioning_like                         |       1 | 0.0208333 |
| price_like                                                  |       1 | 0.0208333 |
| positioning_like|taker_flow_like                            |       1 | 0.0208333 |
| taker_flow_like|liquidity_like                              |       1 | 0.0208333 |
| taker_flow_like|listing_age_like                            |       1 | 0.0208333 |
| taker_flow_like|regime_state                                |       1 | 0.0208333 |
| taker_flow_like|volatility_like                             |       1 | 0.0208333 |

## Marginal Reject Summary

| reason                                                                      |   count |     share |
|:----------------------------------------------------------------------------|--------:|----------:|
| l5_label_marginal_cap                                                       |      21 | 0.295775  |
| basis_premium_marginal_cap                                                  |      17 | 0.239437  |
| basis_premium_marginal_cap;l5_label_marginal_cap                            |      10 | 0.140845  |
| proxy_corr_cap                                                              |       9 | 0.126761  |
| semantic_pair_marginal_cap                                                  |       6 | 0.084507  |
| basis_premium_marginal_cap;l5_label_marginal_cap;semantic_pair_marginal_cap |       4 | 0.056338  |
| basis_premium_marginal_cap;semantic_pair_marginal_cap                       |       3 | 0.0422535 |
| skeleton_marginal_cap                                                       |       1 | 0.0140845 |

## Top Marginal Candidates

|   a7ls20_rank | blueprint_id            | semantic_pair                                               | motif               | label_family                       |   label_horizon_h |   control_ratio_premay_max |   cost10_recent_oriented |   one_bar_lag_recent_oriented |   robust_min_tstat_floor |   split_tstat_floor |   split_positive_rate_floor |   a7ls20_deep_score | expression                                                                                                                                                                            |
|--------------:|:------------------------|:------------------------------------------------------------|:--------------------|:-----------------------------------|------------------:|---------------------------:|-------------------------:|------------------------------:|-------------------------:|--------------------:|----------------------------:|--------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|             1 | a7ls15_54ad1703758fd224 | basis_premium_like|listing_age_like                         | signed_spread       | L5_vol_adjusted_return             |                 4 |                   0.553488 |              1.46333     |                    0.885406   |               -0.208864  |            1.88713  |                    0.491803 |            2521.64  | Mul(Sub(CSRank(Delta(mark_trade_basis_bps,336)),CSRank(Delta(age_percentile_active_universe,8))),Sign(Delta(age_percentile_active_universe,8)))                                       |
|             2 | a7ls15_204d2b4357f56b5a | taker_flow_like                                             | single              | L5_vol_adjusted_return             |                24 |                   0.764958 |              0.994447    |                    1.0034     |                1.67264   |           -8.98194  |                    0.399425 |            1924.95  | Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,48)))                                                                                                                                |
|             3 | a7ls15_6dde8445b9dc0331 | basis_premium_like|listing_age_like                         | state_gate          | L5_vol_adjusted_return             |                 8 |                   0.780694 |              0.689151    |                    0.50534    |                1.76128   |           -2.71042  |                    0.361702 |            1262.9   | Mul(Delta(mark_index_basis_bps,2),Sign(Mean(Delta(age_percentile_active_universe,24),24)))                                                                                            |
|             4 | a7ls15_6b338a109f660b8c | basis_premium_like|liquidity_like                           | signed_spread       | L5_vol_adjusted_return             |                24 |                   0.790837 |              0.623865    |                    0.634236   |                1.90357   |           -9.69352  |                    0.376437 |            1205.97  | Mul(Sub(CSRank(Decay(premium_abs_state,240)),CSRank(ZScore(Mean(trade_volume,12)))),Sign(ZScore(Mean(trade_volume,12))))                                                              |
|             5 | a7ls15_3df186f6ef65ad1b | taker_flow_like                                             | sub                 | L5_vol_adjusted_return             |                24 |                   0.718839 |              0.512251    |                    0.511177   |                2.56874   |           -7.51745  |                    0.386494 |            1081.97  | Sub(ZScore(Mean(taker_buy_sell_volume_ratio_mean,24)),ZScore(Mean(taker_buy_sell_volume_ratio_last,4)))                                                                               |
|             6 | a7ls15_4dcdc7b425d7a981 | taker_flow_like|volatility_like                             | sub                 | L5_vol_adjusted_return             |                24 |                   0.616448 |              0.425204    |                    0.398806   |                1.53837   |           -5.96292  |                    0.396552 |             904.317 | Sub(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))),Delta(realized_vol_168h,48))                                                                                               |
|             7 | a7ls15_defc4a5a369f820f | basis_premium_like                                          | gated_sign          | L5_vol_adjusted_return             |                 8 |                   0.794953 |              0.4284      |                    0.347993   |                1.60583   |           -6.47505  |                    0.375    |             818.954 | Mul(TSRank(mark_index_basis_bps,240),Sign(Decay(mark_trade_basis_bps,504)))                                                                                                           |
|             8 | a7ls15_5275f07bf670d712 | basis_premium_like|liquidity_like                           | relative_shock      | L5_vol_adjusted_return             |                24 |                   0.716807 |              0.402638    |                    0.38808    |                1.66501   |           -3.82072  |                    0.456439 |             803.272 | Mul(Delta(Abs(ZScore(Mean(basis_abs_168h,16))),4),ZScore(Delta(trade_volume,168)))                                                                                                    |
|             9 | a7ls15_b71e18b57ead6ad9 | taker_flow_like|liquidity_like                              | sub                 | L5_vol_adjusted_return             |                24 |                   0.763716 |              0.366477    |                    0.388917   |                1.71521   |           -9.08058  |                    0.372126 |             799.862 | Sub(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,48))),ZScore(Mean(median_quote_volume_168h,72)))                                                                                 |
|            10 | a7ls15_9c1cfb5e02844b76 | basis_premium_like                                          | single              | L5_vol_adjusted_return             |                 8 |                   0.619643 |              0.388248    |                    0.247474   |                2.32574   |           -5.50726  |                    0.411517 |             767.781 | Delta(mark_index_basis_bps,12)                                                                                                                                                        |
|            11 | a7ls15_ddf2a5a6c7583143 | basis_premium_like|listing_age_like                         | mul                 | L5_vol_adjusted_return             |                 8 |                   0.643259 |              0.386823    |                    0.247047   |                2.32574   |           -5.48783  |                    0.412921 |             762.658 | Mul(Delta(mark_index_basis_bps,12),listing_age_days)                                                                                                                                  |
|            12 | a7ls15_113ef02b00ffc25f | basis_premium_like|price_like                               | mul                 | L5_vol_adjusted_return             |                 8 |                   0.530896 |              0.304454    |                    0.202112   |                2.38898   |           -5.60696  |                    0.428371 |             640.8   | Mul(TSRank(mark_index_basis_bps,48),Abs(ZScore(Mean(index_close,240))))                                                                                                               |
|            13 | a7ls15_02213ddd0b85be23 | basis_premium_like                                          | sub                 | L5_vol_adjusted_return             |                24 |                   0.665854 |              0.316898    |                    0.203485   |                2.25035   |           -3.71237  |                    0.435345 |             640.082 | Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(premium_abs_168h,72)))                                                                                                                  |
|            14 | a7ls15_f0887dbb68165e6d | basis_premium_like|liquidity_like                           | mul                 | L5_vol_adjusted_return             |                24 |                   0.666064 |              0.339722    |                    0.242105   |               -0.819744  |            1.18465  |                    0.508172 |             629.62  | Mul(TSRank(mark_trade_basis_bps,6),Abs(ZScore(Mean(trade_volume,720))))                                                                                                               |
|            15 | a7ls15_21e2eb5bd528cfa5 | basis_premium_like                                          | state_gate          | L5_vol_adjusted_return             |                24 |                   0.798349 |              0.333251    |                    0.300019   |               -1.46552   |            2.12131  |                    0.5      |             621.282 | Mul(TSRank(mark_index_basis_bps,3),Sign(Mean(ZScore(Mean(premium_abs_168h,36)),24)))                                                                                                  |
|            16 | a7ls15_b8e42dcf547ae915 | basis_premium_like|price_like                               | sub                 | L5_vol_adjusted_return             |                24 |                   0.556022 |              0.294657    |                    0.17957    |                2.35139   |           -3.39057  |                    0.435364 |             615.362 | Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(mark_close,72)))                                                                                                                        |
|            17 | a7ls15_7355ef8aa37d5217 | basis_premium_like                                          | signed_spread       | L5_vol_adjusted_return             |                 8 |                   0.658838 |              0.339446    |                    0.126917   |               -0.54471   |            0.601685 |                    0.528302 |             595.524 | Mul(Sub(CSRank(Delta(mark_trade_basis_bps,2)),CSRank(TSRank(mark_index_basis_bps,336))),Sign(TSRank(mark_index_basis_bps,336)))                                                       |
|            18 | a7ls15_7d34c860f8f45ca4 | basis_premium_like|liquidity_like                           | sub                 | L5_vol_adjusted_return             |                 8 |                   0.712748 |              0.286143    |                    0.280392   |                0.650939  |            1.19306  |                    0.530899 |             571.363 | Sub(ZScore(Mean(premium_abs_168h,36)),Delta(log_quote_volume_168h,96))                                                                                                                |
|            19 | a7ls15_6843b56cd44c4d9e | basis_premium_like|price_like                               | signed_spread       | L5_vol_adjusted_return             |                 1 |                   0.240792 |              0.164316    |                    0.0459971  |                8.35796   |            4.35117  |                    0.613506 |             568.086 | Mul(Sub(CSRank(TSRank(mark_trade_basis_bps,96)),CSRank(CSRank(trade_return_1h))),Sign(CSRank(trade_return_1h)))                                                                       |
|            20 | a7ls15_7acc9ae07db7a40b | positioning_like|basis_premium_like                         | spread_rank         | L5_vol_adjusted_return             |                 8 |                   0.733494 |              0.265373    |                    0.171655   |                2.48113   |           -4.4642   |                    0.41573  |             550.832 | Sub(CSRank(Delta(top_global_account_divergence,6)),CSRank(Delta(mark_trade_basis_bps,16)))                                                                                            |
|            21 | a7ls15_83b2ec53c58ee01a | listing_age_like|basis_premium_like                         | mul                 | L5_vol_adjusted_return             |                24 |                   0.78401  |              0.27953     |                    0.170438   |                1.64775   |           -2.45444  |                    0.448276 |             544.755 | Mul(ZScore(Mean(listing_age_days,336)),Delta(mark_index_basis_bps,3))                                                                                                                 |
|            22 | a7ls15_42dc6539d51aca8b | basis_premium_like|positioning_like                         | mul                 | L5_vol_adjusted_return             |                 8 |                   0.683949 |              0.299266    |                    0.14609    |                0.0408884 |            0.807879 |                    0.526851 |             538.991 | Mul(CSRank(mark_trade_basis_bps),Abs(ZScore(Mean(global_long_short_account_ratio_mean,120))))                                                                                         |
|            23 | a7ls15_a03a6be747eccb79 | basis_premium_like|positioning_like                         | mul                 | L5_vol_adjusted_return             |                 4 |                   0.670905 |              0.243074    |                    0.119595   |                2.61465   |           -5.38555  |                    0.414804 |             512.677 | Mul(Delta(mark_index_basis_bps,12),Decay(top_long_short_account_ratio_last,48))                                                                                                       |
|            24 | a7ls15_4dc92dc60d615c89 | open_interest_like|taker_flow_like                          | smooth_mul          | L5_vol_adjusted_return             |                24 |                   0.780788 |              0.196797    |                    0.215347   |                2.20984   |           -3.6266   |                    0.436782 |             503.57  | Mean(Mul(ZScore(Mean(open_interest_value_mean,120)),Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)),4)                                                                           |
|            25 | a7ls15_cb5e75b242622860 | basis_premium_like|listing_age_like                         | gated_sign          | L5_vol_adjusted_return             |                 1 |                   0.327977 |              0.141982    |                    0.042749   |                6.78588   |           -8.38331  |                    0.340751 |             483.759 | Mul(TSRank(mark_index_basis_bps,96),Sign(CSRank(log1p_listing_age_days)))                                                                                                             |
|            26 | a7ls15_530252b40793410f | basis_premium_like|liquidity_like                           | safe_div_abs        | L5_vol_adjusted_return             |                 8 |                   0.51363  |              0.248237    |                    0.113327   |               -0.545293  |            0.443802 |                    0.472426 |             472.204 | SafeDiv(Delta(mark_trade_basis_bps,168),Abs(Abs(ZScore(Mean(trade_quote_volume,24)))))                                                                                                |
|            27 | a7ls15_2c7b31909d6612ec | basis_premium_like|price_like                               | gated_sign          | L5_vol_adjusted_return             |                 8 |                   0.52182  |              0.247103    |                    0.0638974  |               -0.483695  |            0.861233 |                    0.525994 |             454.683 | Mul(TSRank(mark_trade_basis_bps,36),Sign(Mean(index_close,2)))                                                                                                                        |
|            28 | a7ls15_d90c7d57fdf5069b | positioning_like|basis_premium_like                         | sub                 | L5_vol_adjusted_return             |                 8 |                   0.719638 |              0.245629    |                    0.145748   |               -0.115896  |            1.57527  |                    0.529494 |             453.092 | Sub(Delta(top_long_short_position_ratio_mean,3),TSRank(mark_index_basis_bps,24))                                                                                                      |
|            29 | a7ls15_982c459fa90224ed | positioning_like|basis_premium_like                         | spread_rank         | L5_vol_adjusted_return             |                 1 |                   0.203339 |              0.138361    |                    0.0474321  |                5.00693   |            0.85931  |                    0.502086 |             450.34  | Sub(CSRank(top_long_short_account_ratio_last),CSRank(mark_index_basis_bps))                                                                                                           |
|            30 | a7ls15_04d0fe57519a6e45 | open_interest_like|positioning_like                         | smooth_mul          | L5_vol_adjusted_return             |                 4 |                   0.595004 |              0.133348    |                    0.115949   |                2.2816    |           -4.18018  |                    0.414804 |             402.852 | Mean(Mul(Decay(open_interest_mean,16),Delta(top_long_short_position_ratio_mean,4)),4)                                                                                                 |
|            31 | a7ls15_78478a819e0cd255 | open_interest_like|taker_flow_like                          | smooth_mul          | L5_vol_adjusted_return             |                 4 |                   0.767502 |              0.163532    |                    0.143324   |                0.811262  |            1.17403  |                    0.490223 |             398.709 | Mean(Mul(Abs(ZScore(Mean(open_interest_value_mean,120))),Abs(ZScore(Mean(kline_taker_buy_quote_share,96)))),4)                                                                        |
|            32 | a7ls15_4382d4990e40e198 | price_like                                                  | spread_rank         | L5_vol_adjusted_return             |                 8 |                   0.676559 |              0.154072    |                    0.104325   |               -0.427976  |            1.42529  |                    0.520394 |             363.541 | Sub(CSRank(Delta(index_close,1)),CSRank(CSRank(trade_return_1h)))                                                                                                                     |
|            33 | a7ls15_15e77eac9947540d | funding_state_like|liquidity_like                           | mul                 | L3_liquidity_tier_relative_return  |                24 |                   0.810682 |              0.00788927  |                    0.009637   |                2.07093   |          -11.6059   |                    0.301724 |             221.406 | Mul(Decay(funding_state_x_basis_delta,96),Mean(median_quote_volume_168h,96))                                                                                                          |
|            34 | a7ls15_2969ccd90f67db23 | taker_flow_like                                             | sub                 | L0_raw_forward_return              |                24 |                   0.752183 |              0.00186005  |                    0.00370334 |                1.9904    |           -4.95222  |                    0.400862 |             215.647 | Sub(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))),Delta(kline_taker_buy_quote_share,48))                                                                                     |
|            35 | a7ls15_9edb5f77500e18d5 | funding_state_like|regime_state                             | signed_spread       | L1_cross_sectional_relative_return |                24 |                   0.864623 |              0.0102557   |                    0.0116401  |                1.63151   |           -7.6725   |                    0.418841 |             208.044 | Mul(Sub(CSRank(ZScore(Mean(funding_rate_state_last_ffill_8h,48))),CSRank(Mean(market_breadth_state,168))),Sign(Mean(market_breadth_state,168)))                                       |
|            36 | a7ls15_ea8481574724f2ec | taker_flow_like                                             | smooth_mul          | L1_cross_sectional_relative_return |                24 |                   0.78598  |              0.000254948 |                    0.00244621 |                1.63852   |           -8.4915   |                    0.395115 |             199.976 | Mean(Mul(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,36))),Decay(kline_taker_buy_quote_share,4)),4)                                                                              |
|            37 | a7ls15_c61a2e9324cce6db | volatility_like|liquidity_rank_active_universe|regime_state | seed_mul            | L3_liquidity_tier_relative_return  |                24 |                   0.88485  |              0.00403569  |                    0.00595687 |                1.72647   |           -4.98454  |                    0.405896 |             196.936 | Mul(Mul(Delta(realized_vol_72h,168),ZScore(Mean(liquidity_rank_active_universe,168))),Delta(market_breadth_state,24))                                                                 |
|            38 | a7ls15_2d95ff5c78595504 | open_interest_like|taker_flow_like                          | safe_div_abs        | L3_liquidity_tier_relative_return  |                24 |                   0.867041 |              0.00323414  |                    0.00525148 |                1.55003   |          -11.2129   |                    0.331897 |             193.265 | SafeDiv(Clip(ZScore(open_interest_mean),-3,3),Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,336))))                                                                                |
|            39 | a7ls15_81fdc57942461f08 | funding_state_like|open_interest_like                       | relative_shock      | L3_liquidity_tier_relative_return  |                24 |                   0.760707 |              0.000436771 |                    0.00236365 |                1.17747   |           -2.53013  |                    0.41704  |             191.755 | Mul(Delta(TSRank(funding_rate_delta_state_24h,48),4),ZScore(ZScore(Mean(open_interest_mean,6))))                                                                                      |
|            40 | a7ls15_fda4be0acb183aa9 | volatility_like|liquidity_rank_active_universe|regime_state | seed_relative_shock | L3_liquidity_tier_relative_return  |                24 |                   0.61858  |              0.00386629  |                    0.00614228 |               -1.58861   |            0.56472  |                    0.518519 |             185.794 | Mul(Delta(Mul(Delta(realized_vol_168h,336),ZScore(Mean(liquidity_rank_active_universe,336))),4),ZScore(Mean(stress_proxy_state,72)))                                                  |
|            41 | a7ls15_f93f4cd8598c1688 | open_interest_like|positioning_like                         | state_gate          | L1_cross_sectional_relative_return |                24 |                   0.590859 |              0.00161079  |                    0.0036248  |               -0.132486  |            3.7612   |                    0.535714 |             185.01  | Mul(Decay(open_interest_last,336),Sign(Mean(ZScore(Mean(top_long_short_position_ratio_mean,2)),24)))                                                                                  |
|            42 | a7ls15_32b786bf6c2f3ba1 | open_interest_like|taker_flow_like                          | mul                 | L0_raw_forward_return              |                24 |                   0.603012 |              0.00195436  |                    0.00398005 |               -1.11542   |            1.1918   |                    0.508621 |             184.161 | Mul(Abs(ZScore(Mean(open_interest_mean,2))),Mean(taker_buy_sell_volume_ratio_last,4))                                                                                                 |
|            43 | a7ls15_8830a89babfbc15d | taker_flow_like|regime_state                                | state_gate          | L1_cross_sectional_relative_return |                24 |                   0.8387   |              0.0022698   |                    0.00377698 |                1.08418   |           -3.84167  |                    0.433908 |             183.16  | Mul(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_mean,72))),Sign(Mean(Mean(leverage_crowding_state,336),24)))                                                                          |
|            44 | a7ls15_2ea731d575cf1f68 | listing_age_like|liquidity_like                             | relative_shock      | L0_raw_forward_return              |                 8 |                   0.765699 |              0.00320759  |                    0.00464282 |                0.637164  |            0.156208 |                    0.510949 |             182.484 | Mul(Delta(Abs(ZScore(Mean(age_x_volatility,336))),4),ZScore(Decay(trade_volume,16)))                                                                                                  |
|            45 | a7ls15_6d1c3e20633d7d88 | taker_flow_like|listing_age_like                            | smooth_mul          | L0_raw_forward_return              |                24 |                   0.837819 |              0.000194667 |                    0.0022938  |                1.09976   |           -3.91081  |                    0.425287 |             180.098 | Mean(Mul(Abs(ZScore(Mean(taker_buy_sell_volume_ratio_last,48))),Mean(sqrt_listing_age_days,168)),4)                                                                                   |
|            46 | a7ls15_b22141240b8d5ddd | funding_state_like|positioning_like                         | mul                 | L1_cross_sectional_relative_return |                 4 |                   0.887755 |              3.75803e-05 |                    0.00161851 |                1.21749   |           -3.92504  |                    0.477654 |             176.561 | Mul(ZScore(Mean(funding_rate_update_age_hours,96)),Delta(global_long_short_account_ratio_mean,8))                                                                                     |
|            47 | a7ls15_387a3b4fa58108b4 | basis_premium|positioning_flow|regime_state                 | seed_smooth_mul     | L0_raw_forward_return              |                24 |                   0.824871 |              0.005963    |                    0.00727285 |               -2.87008   |            0.686294 |                    0.503497 |             164.317 | Mean(Mul(Mul(Delta(premium_close_bps,12),ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Mean(leverage_crowding_state,168)))),4)                                                |
|            48 | a7ls15_fa0efb084d4e6fde | positioning_like|taker_flow_like                            | delta_x_divergence  | L3_liquidity_tier_relative_return  |                24 |                   0.79612  |              0.00311405  |                    0.00503559 |               -1.08754   |            2.32127  |                    0.498512 |             162.851 | Mul(Delta(Delta(global_long_short_account_ratio_last,720),24),Sub(CSRank(Delta(global_long_short_account_ratio_last,720)),CSRank(ZScore(Mean(taker_buy_sell_volume_ratio_mean,16))))) |

## Authorization

- A7LS21 company deep replay packet: authorized only if decision is PASS.
- New formula search: not authorized.
- Alpha proof / shadow / paper / live: not authorized.
