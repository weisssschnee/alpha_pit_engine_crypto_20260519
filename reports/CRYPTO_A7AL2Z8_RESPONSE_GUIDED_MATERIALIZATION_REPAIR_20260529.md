# CRYPTO A7AL-2Z8 RESPONSE-GUIDED MATERIALIZATION REPAIR

Generated: 2026-05-29T04:42:18Z

## Decision

`HOLD_A7AL2Z8_REPAIR_QUOTA_OR_ACTIVITY_FAILURE`

Z8 materializes and repairs the Z7 response-guided queue. It does not compute returns, run replay, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7al2z9_numeric_diagnostic": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay_execution": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7AL2Z8_REPAIR_QUOTA_OR_ACTIVITY_FAILURE",
  "evaluated_candidates": 379,
  "executes_materialization_repair": true,
  "executes_replay": false,
  "executes_training": false,
  "family_count": 6,
  "full_timestamps_before_materialization_subset": 21025,
  "generated_at": "2026-05-29T04:42:18Z",
  "group_field_count": 11,
  "ledger_candidates": 6789,
  "max_eval_per_family": 96,
  "numeric_field_count": 17,
  "selected_activity_failure_count": 0,
  "selected_candidates": 82,
  "selected_eval_failure_count": 0,
  "stage": "A7AL-2Z8",
  "symbols_loaded": 96,
  "target_per_family": 16,
  "timestamps": 3481,
  "uses_may": false
}
```

## Family Summary

| objective_family                     |   selected_count |   z7_seed_retained_count |   unique_skeleton_count |   median_finite_share |   median_nonzero_share |
|:-------------------------------------|-----------------:|-------------------------:|------------------------:|----------------------:|-----------------------:|
| M1_price_range_smoothed_reversal     |               16 |                       16 |                       4 |              0.820741 |               1        |
| M2_taker_liquidity_control_resistant |               16 |                       16 |                       6 |              0.953165 |               0.999989 |
| M3_latent_meme_major_neutral         |               16 |                       13 |                       2 |              0.977018 |               1        |
| M4_regime_relative_value             |               16 |                       11 |                       2 |              0.814996 |               1        |
| M5_trend_breadth_interaction         |               16 |                       16 |                       2 |              0.817294 |               1        |
| M6_low_turnover_funding_premium      |                2 |                        2 |                       2 |              0.516876 |               0.999773 |

## Selected Queue

| candidate_id             | objective_family                     | expression                                                                                                                                                                             | skeleton_key              |   finite_share |   nonzero_share |
|:-------------------------|:-------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------|---------------:|----------------:|
| a7al2z7_01cba4970c25369f | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),12),Mean(trade_close,12))),Rank(Delta(trade_close,12))),liquidity_tier)                                                | skeleton-0fd76254a649d3de |       0.996265 |        1        |
| a7al2z7_00db615b9305fec8 | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),48),Mean(trade_close,48))),Neg(Rank(Delta(trade_close,24)))),liquidity_tier)                                             | skeleton-7522e672725c8071 |       0.992818 |        0.999994 |
| a7al2z7_009122ab58cd2a9c | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),12),Mean(index_close,12))),Rank(Delta(index_close,24))),R0_market_trend_state)                                       | skeleton-a7537d92797064d4 |       0.820454 |        1        |
| a7al2z7_00465f6a4d7171aa | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),48),Mean(index_close,48))),Neg(Rank(Delta(index_close,24)))),R1_market_volatility_state)                               | skeleton-a8da5fed8b17facd |       0.820454 |        0.999996 |
| a7al2z7_05688909c97d394a | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),48),Mean(index_close,48))),Rank(Delta(index_close,4))),liquidity_tier)                                                 | skeleton-0fd76254a649d3de |       0.993105 |        1        |
| a7al2z7_06ea7f699ed8f206 | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),24),Mean(trade_close,24))),Neg(Rank(Delta(trade_close,8)))),liquidity_tier)                                            | skeleton-7522e672725c8071 |       0.993105 |        0.999994 |
| a7al2z7_0788b9564003a690 | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),48),Mean(index_close,48))),Neg(Rank(Delta(index_close,12)))),liquidity_tier)                                             | skeleton-7522e672725c8071 |       0.993105 |        0.999988 |
| a7al2z7_0138e50d0e7b387a | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),72),Mean(mark_close,72))),Rank(Delta(mark_close,12))),R0_market_trend_state)                                         | skeleton-a7537d92797064d4 |       0.820741 |        1        |
| a7al2z7_01cc321810e635c7 | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),24),Mean(trade_close,24))),Rank(Delta(trade_close,4))),R1_market_volatility_state)                                     | skeleton-a7537d92797064d4 |       0.820741 |        1        |
| a7al2z7_037571959d044fcd | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),12),Mean(index_close,12))),Rank(Delta(index_close,24))),R0_market_trend_state)                                         | skeleton-a7537d92797064d4 |       0.820454 |        1        |
| a7al2z7_0383d053fd041a38 | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),48),Mean(mark_close,48))),Rank(Delta(mark_close,8))),R1_market_volatility_state)                                     | skeleton-a7537d92797064d4 |       0.820741 |        1        |
| a7al2z7_049337112af7153b | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(trade_high,trade_low),48),Mean(trade_close,48))),Rank(Delta(trade_close,8))),R1_market_volatility_state)                                   | skeleton-a7537d92797064d4 |       0.820741 |        1        |
| a7al2z7_04f82708eab5c29d | M1_price_range_smoothed_reversal     | LatentNeutralRank(Sub(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),72),Mean(index_close,72))),Rank(Delta(index_close,12))),R1_market_volatility_state)                                    | skeleton-a7537d92797064d4 |       0.820741 |        1        |
| a7al2z7_02add0ebbc1d07bd | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),24),Mean(index_close,24))),Neg(Rank(Delta(index_close,12)))),R0_market_trend_state)                                      | skeleton-a8da5fed8b17facd |       0.820741 |        1        |
| a7al2z7_04fa8b02a635cb47 | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),12),Mean(mark_close,12))),Neg(Rank(Delta(mark_close,4)))),R1_market_volatility_state)                                    | skeleton-a8da5fed8b17facd |       0.824188 |        1        |
| a7al2z7_05b057e58bb433ba | M1_price_range_smoothed_reversal     | GroupNeutralize(Mul(Rank(SafeDiv(Mean(Sub(mark_high,mark_low),24),Mean(trade_close,24))),Neg(Rank(Delta(trade_close,4)))),R0_market_trend_state)                                       | skeleton-a8da5fed8b17facd |       0.820741 |        1        |
| a7al2z7_0041d5fb3124fa47 | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,8),8)),Rank(Mean(Delta(trade_count,8),8))),Neg(Rank(Delta(trade_close,8)))),meme_contract_group)                   | skeleton-083e6f1b3a15137b |       0.964297 |        0.999994 |
| a7al2z7_015149b9c8223e6a | M2_taker_liquidity_control_resistant | LatentNeutralRank(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,4),8)),Rank(Mean(Delta(trade_quote_volume,4),8))),R3_liquidity_cycle_state)                                     | skeleton-1d048fd25fceb186 |       0.824188 |        1        |
| a7al2z7_00db8d680b5b65af | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,4),12)),Rank(Mean(Delta(taker_buy_quote_volume,4),12))),Neg(Rank(Delta(trade_close,4)))),R3_liquidity_cycle_state) | skeleton-35ccb86a77df3dd0 |       0.823039 |        0.999993 |
| a7al2z7_00e7c95da6ccaad7 | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,8),8)),Rank(Mean(Delta(trade_count,8),8))),R3_liquidity_cycle_state)                                              | skeleton-4964bb24550c433f |       0.823039 |        0.992288 |
| a7al2z7_01a5639ce271a902 | M2_taker_liquidity_control_resistant | LatentNeutralRank(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,48),8)),Rank(Mean(Delta(trade_count,48),8))),meme_contract_group)                                               | skeleton-aea444a5ed8a6400 |       0.953165 |        1        |
| a7al2z7_01f3fd4785a42217 | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,24),4)),Rank(Mean(Delta(trade_count,24),4))),liquidity_tier)                                                           | skeleton-c0f866db89ee2ec1 |       0.991956 |        0.999397 |
| a7al2z7_00bf2939f831a24a | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,48),8)),Rank(Mean(Delta(trade_volume,48),8))),Neg(Rank(Delta(trade_close,24)))),meme_contract_group)          | skeleton-083e6f1b3a15137b |       0.953165 |        0.999994 |
| a7al2z7_00e90fb95f68ca2c | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,4),4)),Rank(Mean(Delta(trade_volume,4),4))),Neg(Rank(Delta(trade_close,4)))),meme_contract_group)             | skeleton-083e6f1b3a15137b |       0.966524 |        0.999994 |
| a7al2z7_014cec2ab624f1d7 | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,24),12)),Rank(Mean(Delta(trade_volume,24),12))),Neg(Rank(Delta(trade_close,24)))),meme_contract_group)             | skeleton-083e6f1b3a15137b |       0.958731 |        0.999994 |
| a7al2z7_03279a4239d43baf | M2_taker_liquidity_control_resistant | GroupNeutralize(Mul(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,12),12)),Rank(Mean(Delta(trade_count,12),12))),Neg(Rank(Delta(trade_close,12)))),liquidity_tier)              | skeleton-083e6f1b3a15137b |       0.993105 |        0.999985 |
| a7al2z7_045b20a618f8654f | M2_taker_liquidity_control_resistant | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,12),12)),Rank(Mean(Delta(trade_count,12),12))),R3_liquidity_cycle_state)                                             | skeleton-1d048fd25fceb186 |       0.820741 |        1        |
| a7al2z7_039973337b1794bb | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,4),8)),Rank(Mean(Delta(taker_buy_quote_volume,4),8))),R3_liquidity_cycle_state)                                   | skeleton-4964bb24550c433f |       0.824188 |        0.991384 |
| a7al2z7_03a9d37ce500e682 | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,24),8)),Rank(Mean(Delta(taker_buy_quote_volume,24),8))),R3_liquidity_cycle_state)                                      | skeleton-4964bb24550c433f |       0.818443 |        0.99011  |
| a7al2z7_026eaaa6d8a55b18 | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,12),12)),Rank(Mean(Delta(trade_count,12),12))),liquidity_tier)                                                    | skeleton-c0f866db89ee2ec1 |       0.993105 |        0.999443 |
| a7al2z7_02f1df4268618e5a | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,48),8)),Rank(Mean(Delta(trade_quote_volume,48),8))),liquidity_tier)                                               | skeleton-c0f866db89ee2ec1 |       0.983913 |        0.999392 |
| a7al2z7_038e24f509c5dbfe | M2_taker_liquidity_control_resistant | GroupNeutralize(Sub(Rank(Mean(Delta(taker_buy_sell_volume_ratio_last,48),8)),Rank(Mean(Delta(taker_buy_quote_volume,48),8))),meme_contract_group)                                      | skeleton-c0f866db89ee2ec1 |       0.953165 |        0.999821 |
| a7al2z7_00f9889f17c7e8ee | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,72),8)),Rank(Mean(Delta(trade_close,24),8))),is_major)                                                                      | skeleton-aea444a5ed8a6400 |       0.977018 |        1        |
| a7al2z7_02441c645efc7315 | M3_latent_meme_major_neutral         | GroupNeutralize(Sub(Rank(Mean(Delta(mark_index_basis_bps,168),4)),Rank(Mean(Delta(trade_close,24),4))),meme_contract_group)                                                            | skeleton-c0f866db89ee2ec1 |       0.920883 |        0.999779 |
| a7al2z7_0146b4c57a203cc6 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(trade_quote_volume,24),12)),Rank(Mean(Delta(trade_close,24),12))),meme_contract_group)                                                           | skeleton-aea444a5ed8a6400 |       0.958731 |        1        |
| a7al2z7_01c36d9b66585435 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,168),8)),Rank(Mean(Delta(trade_close,24),8))),meme_contract_group)                                                   | skeleton-aea444a5ed8a6400 |       0.91977  |        1        |
| a7al2z7_02d8caa20d9955be | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,24),12)),Rank(Mean(Delta(trade_close,24),12))),meme_contract_group)                                                         | skeleton-aea444a5ed8a6400 |       0.958731 |        1        |
| a7al2z7_03ab14ae270475ef | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,48),12)),Rank(Mean(Delta(trade_close,24),12))),is_multiplier_contract)                                                      | skeleton-aea444a5ed8a6400 |       0.982764 |        1        |
| a7al2z7_03f765455c711865 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(trade_quote_volume,168),12)),Rank(Mean(Delta(trade_close,24),12))),is_multiplier_contract)                                                       | skeleton-aea444a5ed8a6400 |       0.948291 |        1        |
| a7al2z7_052c264c4cbf7a33 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,24),8)),Rank(Mean(Delta(trade_close,24),8))),is_major)                                                                         | skeleton-aea444a5ed8a6400 |       0.990807 |        1        |
| a7al2z7_071abead654ddcb8 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,168),8)),Rank(Mean(Delta(trade_close,24),8))),liquidity_tier)                                                               | skeleton-aea444a5ed8a6400 |       0.94944  |        1        |
| a7al2z7_071e10145db8f822 | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,12),8)),Rank(Mean(Delta(trade_close,12),8))),is_major)                                                                         | skeleton-aea444a5ed8a6400 |       0.994255 |        1        |
| a7al2z7_0286d91c7d250bce | M3_latent_meme_major_neutral         | GroupNeutralize(Sub(Rank(Mean(Delta(premium_close_bps,24),8)),Rank(Mean(Delta(trade_close,24),8))),is_multiplier_contract)                                                             | skeleton-c0f866db89ee2ec1 |       0.990807 |        0.999831 |
| a7al2z7_02cb2d8e30b5d27c | M3_latent_meme_major_neutral         | GroupNeutralize(Sub(Rank(Mean(Delta(trade_quote_volume,48),8)),Rank(Mean(Delta(trade_close,24),8))),liquidity_tier)                                                                    | skeleton-c0f866db89ee2ec1 |       0.983913 |        0.99948  |
| a7al2z7_08874e5851c16618 | M3_latent_meme_major_neutral         | GroupNeutralize(Sub(Rank(Mean(Delta(premium_close_bps,24),8)),Rank(Mean(Delta(trade_close,24),8))),is_major)                                                                           | skeleton-c0f866db89ee2ec1 |       0.990807 |        0.999698 |
| a7al2z7_09e3208bbf5abbda | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,12),8)),Rank(Mean(Delta(trade_close,12),8))),meme_contract_group)                                                           | skeleton-aea444a5ed8a6400 |       0.963184 |        1        |
| a7al2z7_0d4619b60c7fec6c | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,72),8)),Rank(Mean(Delta(trade_close,24),8))),is_multiplier_contract)                                                        | skeleton-aea444a5ed8a6400 |       0.977018 |        1        |
| a7al2z7_0e59a2be75b3d68b | M3_latent_meme_major_neutral         | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,12),8)),Rank(Mean(Delta(trade_close,12),8))),liquidity_tier)                                                                   | skeleton-aea444a5ed8a6400 |       0.994255 |        1        |
| a7al2z7_006fe6dc67750595 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,48),4)),Rank(Mean(Delta(trade_quote_volume,24),4))),R9_alt_vs_major_dispersion_state)                                          | skeleton-1d048fd25fceb186 |       0.812698 |        1        |
| a7al2z7_0042814db7da9e9b | M4_regime_relative_value             | GroupNeutralize(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,72),4)),Rank(Mean(Delta(trade_quote_volume,24),4))),R10_stress_proxy_state)                                            | skeleton-4964bb24550c433f |       0.805803 |        0.990712 |
| a7al2z7_0155bffd65f36281 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,24),4)),Rank(Mean(Delta(trade_quote_volume,24),4))),R1_market_volatility_state)                                                | skeleton-1d048fd25fceb186 |       0.819592 |        1        |
| a7al2z7_016c6c324420b043 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,72),8)),Rank(Mean(Delta(trade_close,24),8))),R2_market_breadth_state)                                                       | skeleton-1d048fd25fceb186 |       0.804654 |        1        |
| a7al2z7_01a2421b4dcf6854 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,24),4)),Rank(Mean(Delta(trade_quote_volume,24),4))),R9_alt_vs_major_dispersion_state)                                | skeleton-1d048fd25fceb186 |       0.819592 |        1        |
| a7al2z7_023ed82a2153a6b4 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,48),12)),Rank(Mean(Delta(trade_close,24),12))),R1_market_volatility_state)                                                     | skeleton-1d048fd25fceb186 |       0.810399 |        1        |
| a7al2z7_023f8096d7214b6f | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,12),8)),Rank(Mean(Delta(trade_close,12),8))),R9_alt_vs_major_dispersion_state)                                              | skeleton-1d048fd25fceb186 |       0.82189  |        1        |
| a7al2z7_0130c606e292a49d | M4_regime_relative_value             | GroupNeutralize(Sub(Rank(Mean(Delta(premium_close_bps,24),4)),Rank(Mean(Delta(trade_close,24),4))),R5_basis_premium_dislocation_state)                                                 | skeleton-4964bb24550c433f |       0.819592 |        0.989748 |
| a7al2z7_015fea2961ef8672 | M4_regime_relative_value             | GroupNeutralize(Sub(Rank(Mean(Delta(mark_index_basis_bps,72),12)),Rank(Mean(Delta(trade_quote_volume,24),12))),R2_market_breadth_state)                                                | skeleton-4964bb24550c433f |       0.803505 |        0.990183 |
| a7al2z7_01cca295a4e7c271 | M4_regime_relative_value             | GroupNeutralize(Sub(Rank(Mean(Delta(premium_close_bps,12),8)),Rank(Mean(Delta(trade_close,12),8))),R2_market_breadth_state)                                                            | skeleton-4964bb24550c433f |       0.82189  |        0.989511 |
| a7al2z7_025ee4acd7fb84d2 | M4_regime_relative_value             | GroupNeutralize(Sub(Rank(Mean(Delta(mark_index_basis_bps,48),4)),Rank(Mean(Delta(index_close,24),4))),R1_market_volatility_state)                                                      | skeleton-4964bb24550c433f |       0.812698 |        0.990519 |
| a7al2z7_028fb982648a2d17 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,48),4)),Rank(Mean(Delta(index_close,24),4))),R2_market_breadth_state)                                                          | skeleton-1d048fd25fceb186 |       0.812698 |        1        |
| a7al2z7_02e96cbfc3c4f949 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,72),12)),Rank(Mean(Delta(trade_quote_volume,24),12))),R3_liquidity_cycle_state)                                      | skeleton-1d048fd25fceb186 |       0.803505 |        1        |
| a7al2z7_02f5ce8ba7764802 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,12),8)),Rank(Mean(Delta(index_close,12),8))),R0_market_trend_state)                                                            | skeleton-1d048fd25fceb186 |       0.82189  |        1        |
| a7al2z7_02fd6dd4c18725a7 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,24),12)),Rank(Mean(Delta(trade_close,24),12))),R2_market_breadth_state)                                              | skeleton-1d048fd25fceb186 |       0.817294 |        1        |
| a7al2z7_035cf1da8f8be677 | M4_regime_relative_value             | LatentNeutralRank(Sub(Rank(Mean(Delta(kline_taker_buy_quote_share,12),4)),Rank(Mean(Delta(trade_close,12),4))),R9_alt_vs_major_dispersion_state)                                       | skeleton-1d048fd25fceb186 |       0.823039 |        1        |
| a7al2z7_00476fd02850de3f | M5_trend_breadth_interaction         | LatentNeutralRank(Sub(Rank(Mean(Delta(premium_close_bps,48),12)),Rank(Mean(Delta(trade_close,48),12))),R2_market_breadth_state)                                                        | skeleton-1d048fd25fceb186 |       0.810399 |        1        |
| a7al2z7_0007e507cc56d3e3 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(trade_close,24),8))),Rank(Mean(Delta(mark_index_basis_bps,24),8))),R9_alt_vs_major_dispersion_state)                                           | skeleton-aa6f825a7a0a2bae |       0.818443 |        1        |
| a7al2z7_013f25dbecab09d6 | M5_trend_breadth_interaction         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_trade_basis_bps,12),4)),Rank(Mean(Delta(trade_close,12),4))),R0_market_trend_state)                                                         | skeleton-1d048fd25fceb186 |       0.823039 |        1        |
| a7al2z7_01643fc51752e53d | M5_trend_breadth_interaction         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,72),12)),Rank(Mean(Delta(mark_close,72),12))),R2_market_breadth_state)                                                      | skeleton-1d048fd25fceb186 |       0.803505 |        1        |
| a7al2z7_01eb7edbcd5a252e | M5_trend_breadth_interaction         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_trade_basis_bps,72),12)),Rank(Mean(Delta(index_close,72),12))),R9_alt_vs_major_dispersion_state)                                            | skeleton-1d048fd25fceb186 |       0.803505 |        1        |
| a7al2z7_0391abb03c3c66ba | M5_trend_breadth_interaction         | LatentNeutralRank(Sub(Rank(Mean(Delta(mark_index_basis_bps,12),4)),Rank(Mean(Delta(trade_close,12),4))),R0_market_trend_state)                                                         | skeleton-1d048fd25fceb186 |       0.823039 |        1        |
| a7al2z7_0051d4ba2c48f760 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(trade_close,24),12))),Rank(Mean(Delta(mark_trade_basis_bps,24),12))),R2_market_breadth_state)                                                  | skeleton-aa6f825a7a0a2bae |       0.817294 |        1        |
| a7al2z7_0072e9c2ed1bf9a3 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(mark_close,72),12))),Rank(Mean(Delta(mark_index_basis_bps,72),12))),R9_alt_vs_major_dispersion_state)                                          | skeleton-aa6f825a7a0a2bae |       0.803505 |        0.999996 |
| a7al2z7_0152a2deacacf882 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(index_close,72),4))),Rank(Mean(Delta(mark_index_basis_bps,72),4))),R9_alt_vs_major_dispersion_state)                                           | skeleton-aa6f825a7a0a2bae |       0.805803 |        1        |
| a7al2z7_024bc6d6a8b62220 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(mark_close,72),4))),Rank(Mean(Delta(premium_close_bps,72),4))),R9_alt_vs_major_dispersion_state)                                               | skeleton-aa6f825a7a0a2bae |       0.805803 |        1        |
| a7al2z7_02696ab005b800b7 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(trade_close,24),4))),Rank(Mean(Delta(premium_close_bps,24),4))),R10_stress_proxy_state)                                                        | skeleton-aa6f825a7a0a2bae |       0.819592 |        1        |
| a7al2z7_02a8f3146e4d3ead | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(mark_close,12),8))),Rank(Mean(Delta(mark_trade_basis_bps,12),8))),R9_alt_vs_major_dispersion_state)                                            | skeleton-aa6f825a7a0a2bae |       0.82189  |        1        |
| a7al2z7_035821f24a832355 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(trade_close,48),12))),Rank(Mean(Delta(mark_index_basis_bps,48),12))),R0_market_trend_state)                                                    | skeleton-aa6f825a7a0a2bae |       0.810399 |        1        |
| a7al2z7_0394c4e9970a6603 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(index_close,24),8))),Rank(Mean(Delta(mark_index_basis_bps,24),8))),R0_market_trend_state)                                                      | skeleton-aa6f825a7a0a2bae |       0.818443 |        0.999996 |
| a7al2z7_04babe16e29845a3 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(index_close,12),4))),Rank(Mean(Delta(premium_close_bps,12),4))),R10_stress_proxy_state)                                                        | skeleton-aa6f825a7a0a2bae |       0.823039 |        1        |
| a7al2z7_0500f942c89acb80 | M5_trend_breadth_interaction         | GroupNeutralize(Mul(Neg(Rank(Mean(Delta(trade_close,24),12))),Rank(Mean(Delta(mark_index_basis_bps,24),12))),R0_market_trend_state)                                                    | skeleton-aa6f825a7a0a2bae |       0.817294 |        1        |

## Blockers

| candidate_id             | blocker                      | detail                           |
|:-------------------------|:-----------------------------|:---------------------------------|
| a7al2z7_00b9f7f2e817cf7d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_029bd0dc4ea7deaa | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_02c858f34d65b612 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_0360ff84330cad0a | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_082fbbd3dfdcd912 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_02a37ddf932978e0 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_02bf2e7e1a213cbd | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_065abbf8a0fe1fb7 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_066be0cdc6266ec1 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_087b0dafeafd155d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_002f1b9a11a16083 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_068bb1a1076a5844 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_077a7ed6ad2b4e7c | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_09b3119c49b19810 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_0f2955824976ef30 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_07b817c9b7cafc4e | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_0a6474b051adf02b | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_0d801bcb056219af | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_14b4823fc7a5771d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_15539000829e3e0e | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_159ee20a81036531 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_1ae5e63ee31c77db | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_211ca5e23af65f30 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_228383801fa1f336 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_248d802f5505ba57 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_248dce15fc08b7e4 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_24b06615c0fadabc | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_2883dbcf3c943718 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_2a37b40a979ea4ba | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_36456ac38e09ef97 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_36df885682410bf7 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_3b7e8f5cb3c3afc6 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_3d0c180c0f8e0e49 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_46ccba63ac8c621f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_47a42fcb279cc36f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_4b3e69d501588410 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_54932c6fcbdcb2fa | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_596e2402edff7c41 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_5d6d790fbca2d608 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_5f3be5c17fb03f7d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_615c6c918b3fb2c7 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_64e2c8e0bd1ff5ec | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_66913793d096fef5 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_67255322717fd1e3 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_71b1c9f4b999afd0 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_7262c3e8a9ce8add | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_72aaadb03b1c65fb | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_7425060ea0a5072f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_7495751ccb8246e6 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_7e11ee217180ef75 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_8487ea3719a44c8d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_848e0ee2d2b6911f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_8bcb5d26bf877942 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_8e66bb27a2e23faf | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_8eba9b15985be531 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_90138a557457ec2d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_9953ebc8642613d7 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_9b1f6f1f4256f9c4 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_a0d1030e3c672c49 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_a24f3f2c5bb12d94 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_a4c8d2f3e9f93d62 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_a75a45faa0d7b56d | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_a7c11182947f493a | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_ab598f2c69653579 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_aec88d687a2a2d48 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_b1270a3bc85305e5 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_b62591b0dfc002bf | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_bbb22032d23a8633 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_bd509f5394f761c0 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_c5af9dd1afdcbdea | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_c9d94c03ec434f23 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_ca17665955af0284 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cb7c215402fc56d6 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cb88065644cce541 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cbc020fcc2d1535f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cc4c1d8ed71743bd | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cd1f4765adf984e0 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_ce7d8f9477332935 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_cf2fde05cc4e8d28 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z7_d1044e95576dd437 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
