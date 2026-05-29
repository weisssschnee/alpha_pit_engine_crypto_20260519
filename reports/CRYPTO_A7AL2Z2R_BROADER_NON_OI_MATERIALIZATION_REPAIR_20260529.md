# CRYPTO A7AL-2Z2R BROADER NON-OI MATERIALIZATION REPAIR

Generated: 2026-05-29T03:41:23Z

## Decision

`PASS_A7AL2Z2R_BROADER_NON_OI_MATERIALIZATION_REPAIR_READY_FOR_Z3_CONTRACT`

Z2R repairs the Z1 materialization queue by replacing sparse or constant expressions from the same static dry pool. It does not compute returns, replay, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7al2z3_numeric_preflight_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay_execution": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AL2Z2R_BROADER_NON_OI_MATERIALIZATION_REPAIR_READY_FOR_Z3_CONTRACT",
  "evaluated_candidates": 216,
  "executes_materialization_repair": true,
  "executes_replay": false,
  "executes_training": false,
  "family_count": 8,
  "generated_at": "2026-05-29T03:41:23Z",
  "group_field_count": 11,
  "ledger_candidates": 1272,
  "numeric_field_count": 18,
  "selected_activity_failure_count": 0,
  "selected_candidates": 128,
  "selected_eval_failure_count": 0,
  "stage": "A7AL-2Z2R",
  "symbols_loaded": 96,
  "target_per_family": 16,
  "timestamps": 21025,
  "uses_may": false
}
```

## Family Summary

| objective_family                         |   selected_count |   z1_seed_retained_count |   unique_skeleton_count |   median_finite_share |   median_nonzero_share |
|:-----------------------------------------|-----------------:|-------------------------:|------------------------:|----------------------:|-----------------------:|
| Z0_funding_basis_premium_dislocation     |               16 |                        9 |                       5 |              0.970526 |               0.999112 |
| Z1_price_range_volatility_structure      |               16 |                       14 |                      11 |              0.997404 |               1        |
| Z2_liquidity_taker_microstructure_lite   |               16 |                       16 |                       8 |              0.997987 |               1        |
| Z3_basis_price_trend_reversal            |               16 |                       16 |                       5 |              0.996239 |               0.999139 |
| Z4_upper_regime_relative_value           |               16 |                       12 |                       3 |              0.968892 |               0.999365 |
| Z5_latent_listing_meme_neutral_structure |               16 |                       12 |                       5 |              0.993468 |               0.999736 |
| Z6_cross_sectional_relative_flow_value   |               16 |                       13 |                       4 |              0.996831 |               0.999999 |
| Z7_market_regime_price_breadth           |               16 |                       16 |                       3 |              0.967915 |               0.999924 |

## Repaired Selected Queue

| candidate_id             | objective_family                       | expression                                                                                     | skeleton_key              |   finite_share |   nonzero_share |
|:-------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------|:--------------------------|---------------:|----------------:|
| a7al2z1_18a6b78a193210db | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,168)),Rank(Mean(funding_rate,168)))                         | skeleton-612ffe194eccb811 |       0.217108 |       0.998795  |
| a7al2z1_0025716230424fb7 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(mark_trade_basis_bps,48))))                                               | skeleton-6ebd7d4c1e06c9bc |       0.998248 |       1         |
| a7al2z1_1fa487e13f578276 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Delta(premium_close_bps,168))))                                                | skeleton-8a6cec079a5f7997 |       0.990848 |       1         |
| a7al2z1_094c52bafda2cb02 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)       | skeleton-93ce4b9755fbcc1f |       0.966536 |       0.999087  |
| a7al2z1_069b0f75654dadde | Z0_funding_basis_premium_dislocation   | Mul(Winsor(ZScore(Mean(premium_close_bps,168))),Winsor(ZScore(Mean(funding_rate,168))))        | skeleton-f59f8b03ae1fd3c4 |       0.216799 |       1         |
| a7al2z1_0313bc007ac9963d | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,12))))                                                  | skeleton-6ebd7d4c1e06c9bc |       0.998393 |       1         |
| a7al2z1_23cc7365fa741d7c | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,72))))                                                  | skeleton-6ebd7d4c1e06c9bc |       0.997887 |       1         |
| a7al2z1_0a1368b901e4b360 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)       | skeleton-93ce4b9755fbcc1f |       0.968866 |       0.999138  |
| a7al2z1_2785f094943ec26b | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_trade_basis_bps,72)),R5_basis_premium_dislocation_state)       | skeleton-93ce4b9755fbcc1f |       0.967333 |       0.998569  |
| a7al2z1_5d8b43fa29769147 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(premium_close_bps,336)),Rank(Mean(funding_rate,336)))                            | skeleton-612ffe194eccb811 |       0.970633 |       0.94177   |
| a7al2z1_902f31baa5005418 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(premium_close_bps,168)),Rank(Mean(funding_rate,168)))                            | skeleton-612ffe194eccb811 |       0.216799 |       0.963621  |
| a7al2z1_b7d8223ba0236850 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_index_basis_bps,168)),Rank(Mean(funding_rate,168)))                         | skeleton-612ffe194eccb811 |       0.217108 |       0.968691  |
| a7al2z1_d0cb162ee47ff62d | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,336)),Rank(Mean(funding_rate,336)))                         | skeleton-612ffe194eccb811 |       0.970858 |       0.989993  |
| a7al2z1_e2abe5031d2b5181 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_index_basis_bps,336)),Rank(Mean(funding_rate,336)))                         | skeleton-612ffe194eccb811 |       0.970419 |       0.968053  |
| a7al2z1_2877ae50ae09b29b | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,24))))                                                  | skeleton-6ebd7d4c1e06c9bc |       0.997816 |       1         |
| a7al2z1_2d8189ddb782e0f0 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(mark_index_basis_bps,336))))                                              | skeleton-6ebd7d4c1e06c9bc |       0.997809 |       1         |
| a7al2z1_086296df472ad4ae | Z1_price_range_volatility_structure    | Neg(Rank(Delta(index_close,168)))                                                              | skeleton-0e746cb1116b151b |       0.990412 |       1         |
| a7al2z1_18a394084ddac9b5 | Z1_price_range_volatility_structure    | Mul(Rank(Mean(Sub(mark_high,mark_low),24)),Neg(Rank(Delta(trade_close,24))))                   | skeleton-237f4484d8782cda |       0.998153 |       1         |
| a7al2z1_066701faa05eebbc | Z1_price_range_volatility_structure    | Mul(Winsor(ZScore(Delta(trade_close,72))),Neg(Winsor(ZScore(Delta(mark_close,72)))))           | skeleton-2f7931a1701c8dd4 |       0.99587  |       1         |
| a7al2z1_1919cb4f0227005e | Z1_price_range_volatility_structure    | Rank(Delta(mark_close,72))                                                                     | skeleton-377d45dadd905908 |       0.99587  |       1         |
| a7al2z1_0137caa89f7a1268 | Z1_price_range_volatility_structure    | SafeDiv(Mean(Sub(trade_high,trade_low),72),Mean(trade_close,72))                               | skeleton-42a2a88aea7a43d9 |       0.998248 |       1         |
| a7al2z1_09ec291c3c80efca | Z1_price_range_volatility_structure    | Sub(Rank(Mean(trade_close,72)),Rank(Mean(index_close,72)))                                     | skeleton-612ffe194eccb811 |       0.997548 |       0.0709871 |
| a7al2z1_0b6494a3a4ef9490 | Z1_price_range_volatility_structure    | GroupNeutralize(Rank(Mean(Sub(trade_high,trade_low),24)),R1_market_volatility_state)           | skeleton-6a0cf455a6085492 |       0.968499 |       0.999889  |
| a7al2z1_48338dedf315f7a2 | Z1_price_range_volatility_structure    | Rank(Mean(Sub(mark_high,mark_low),72))                                                         | skeleton-6f8455dd7afde698 |       0.998248 |       1         |
| a7al2z1_028db6316a60db86 | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(mark_close,72))))                                                        | skeleton-8a6cec079a5f7997 |       0.99587  |       1         |
| a7al2z1_07116c7a8a24208e | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,24)),Rank(Delta(trade_close,24)))                                    | skeleton-8ad46b9059e6381f |       0.998153 |       0.254066  |
| a7al2z1_2d6e3bd57d32e9b1 | Z1_price_range_volatility_structure    | Rank(Delta(Sub(trade_high,trade_low),24))                                                      | skeleton-a00bec3381f16e2c |       0.998153 |       1         |
| a7al2z1_0e268536d1126a2d | Z1_price_range_volatility_structure    | Sub(Rank(Mean(index_close,12)),Rank(Mean(trade_close,12)))                                     | skeleton-612ffe194eccb811 |       0.998035 |       0.0753576 |
| a7al2z1_10d47299f1a5d1ee | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(index_close,24))))                                                       | skeleton-8a6cec079a5f7997 |       0.997404 |       1         |
| a7al2z1_0f752369161ae869 | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,336)),Rank(Delta(index_close,336)))                                  | skeleton-8ad46b9059e6381f |       0.982255 |       0.224583  |
| a7al2z1_15a4669eff9c2869 | Z1_price_range_volatility_structure    | Neg(Rank(Delta(index_close,24)))                                                               | skeleton-0e746cb1116b151b |       0.997404 |       1         |
| a7al2z1_2b6e448dc85041e6 | Z1_price_range_volatility_structure    | Neg(Rank(Delta(index_close,48)))                                                               | skeleton-0e746cb1116b151b |       0.996239 |       1         |
| a7al2z1_9481b2170c90544c | Z2_liquidity_taker_microstructure_lite | Sub(Rank(kline_taker_buy_quote_share),Rank(taker_buy_sell_volume_ratio_last))                  | skeleton-2b903f140c47221a |       0.998771 |       0.984563  |
| a7al2z1_06158e66c283198d | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,12))),Neg(Winsor(ZScore(Delta(trade_close,12)))))   | skeleton-2f7931a1701c8dd4 |       0.998724 |       1         |
| a7al2z1_05bbcd80f3bb1f84 | Z2_liquidity_taker_microstructure_lite | Rank(Mean(taker_buy_sell_volume_ratio_last,6))                                                 | skeleton-361a8342adc82420 |       0.998391 |       1         |
| a7al2z1_031574ff37957433 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,168))                                                   | skeleton-377d45dadd905908 |       0.991209 |       1         |
| a7al2z1_29d77b76d08d3067 | Z2_liquidity_taker_microstructure_lite | SafeDiv(taker_buy_quote_volume,trade_quote_volume)                                             | skeleton-50d91eb323c86baa |       0.999247 |       0.999999  |
| a7al2z1_0ee6ab4ec3285d14 | Z2_liquidity_taker_microstructure_lite | Rank(Abs(ZScore(Delta(kline_taker_buy_quote_share,168))))                                      | skeleton-8a6cec079a5f7997 |       0.991209 |       1         |
| a7al2z1_1af0afda743e28ac | Z2_liquidity_taker_microstructure_lite | Sub(Rank(Delta(trade_volume,48)),Rank(Delta(trade_close,24)))                                  | skeleton-8ad46b9059e6381f |       0.997011 |       0.988872  |
| a7al2z1_0115d3dbe93c2618 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_sell_volume_ratio_last,24)),R3_liquidity_cycle_state)     | skeleton-93ce4b9755fbcc1f |       0.968664 |       0.999924  |
| a7al2z1_0713ad23e3e4f1a1 | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,168))),Neg(Winsor(ZScore(Delta(trade_close,24)))))  | skeleton-2f7931a1701c8dd4 |       0.991304 |       1         |
| a7al2z1_0a1bb022b33cf015 | Z2_liquidity_taker_microstructure_lite | Rank(Mean(trade_count,12))                                                                     | skeleton-361a8342adc82420 |       0.998771 |       1         |
| a7al2z1_0cee318f9177279a | Z2_liquidity_taker_microstructure_lite | Rank(Mean(taker_buy_quote_volume,168))                                                         | skeleton-361a8342adc82420 |       0.998248 |       1         |
| a7al2z1_04308808db9785c7 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,12))                                                    | skeleton-377d45dadd905908 |       0.998629 |       1         |
| a7al2z1_06179c2b2c6fa22c | Z2_liquidity_taker_microstructure_lite | Rank(Delta(taker_buy_sell_volume_ratio_last,12))                                               | skeleton-377d45dadd905908 |       0.99782  |       1         |
| a7al2z1_07b10f27debc2020 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(trade_quote_volume,24))                                                             | skeleton-377d45dadd905908 |       0.998153 |       1         |
| a7al2z1_03845c7516491252 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_quote_volume,24)),R3_liquidity_cycle_state)               | skeleton-93ce4b9755fbcc1f |       0.969616 |       0.999924  |
| a7al2z1_0a75fb1c32beed6e | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_sell_volume_ratio_last,12)),R3_liquidity_cycle_state)     | skeleton-93ce4b9755fbcc1f |       0.968723 |       0.999924  |
| a7al2z1_07407de3ca8314db | Z3_basis_price_trend_reversal          | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,48))),Neg(Winsor(ZScore(Delta(trade_close,48))))) | skeleton-2f7931a1701c8dd4 |       0.996239 |       1         |
| a7al2z1_01ee540865d7b89c | Z3_basis_price_trend_reversal          | Sub(Rank(Mean(mark_index_basis_bps,24)),Rank(Delta(trade_close,24)))                           | skeleton-33e3a49123adc7df |       0.997405 |       0.990317  |
| a7al2z1_058a56eed1333ef3 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(premium_close_bps,168)),Rank(Delta(trade_close,168)))                           | skeleton-8ad46b9059e6381f |       0.990848 |       0.991017  |
| a7al2z1_0646a16788eadb60 | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(mark_index_basis_bps,48)),R0_market_trend_state)                    | skeleton-93ce4b9755fbcc1f |       0.967701 |       0.999118  |
| a7al2z1_10e42708fc0ba025 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_trade_basis_bps,168)),Neg(Rank(Delta(trade_close,168))))                   | skeleton-d8c77be249a1b7db |       0.991304 |       1         |
| a7al2z1_2593267a5a5495c0 | Z3_basis_price_trend_reversal          | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,24))),Neg(Winsor(ZScore(Delta(trade_close,24))))) | skeleton-2f7931a1701c8dd4 |       0.997404 |       1         |
| a7al2z1_1d5101fd76f007d7 | Z3_basis_price_trend_reversal          | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Delta(trade_close,48)))                           | skeleton-33e3a49123adc7df |       0.997011 |       0.989797  |
| a7al2z1_1080aea723374d03 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_index_basis_bps,48)),Rank(Delta(index_close,48)))                          | skeleton-8ad46b9059e6381f |       0.996239 |       0.990496  |
| a7al2z1_1d5813e7f30ddb28 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_index_basis_bps,24)),Rank(Delta(index_close,24)))                          | skeleton-8ad46b9059e6381f |       0.997404 |       0.990457  |
| a7al2z1_2332ae0a674eb61e | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_trade_basis_bps,168)),Rank(Delta(trade_close,168)))                        | skeleton-8ad46b9059e6381f |       0.991304 |       0.990933  |
| a7al2z1_0e3e0240604d5ce6 | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(mark_index_basis_bps,12)),R0_market_trend_state)                    | skeleton-93ce4b9755fbcc1f |       0.96889  |       0.99916   |
| a7al2z1_2193f2355135ba3d | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(premium_close_bps,168)),R0_market_trend_state)                      | skeleton-93ce4b9755fbcc1f |       0.96231  |       0.997937  |
| a7al2z1_118d9e3951e724ca | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,48)),Neg(Rank(Delta(index_close,48))))                     | skeleton-d8c77be249a1b7db |       0.996239 |       1         |
| a7al2z1_1596b15a56aa40e3 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(premium_close_bps,48)),Neg(Rank(Delta(trade_close,48))))                        | skeleton-d8c77be249a1b7db |       0.996615 |       1         |
| a7al2z1_1e1f29f96b2684ea | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,168)),Neg(Rank(Delta(trade_close,168))))                   | skeleton-d8c77be249a1b7db |       0.990412 |       1         |
| a7al2z1_25a51da6deb9bdc6 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,24)),Neg(Rank(Delta(index_close,24))))                     | skeleton-d8c77be249a1b7db |       0.997404 |       1         |
| a7al2z1_000f7a58ee0cecab | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(trade_quote_volume,168)),R10_stress_proxy_state)                     | skeleton-2d05b222193f0313 |       0.969663 |       0.999924  |
| a7al2z1_00031079a29042a5 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(mark_index_basis_bps,24),R10_stress_proxy_state)                       | skeleton-619f11aa0aaa14be |       0.968866 |       1         |
| a7al2z1_01144b6aeae51153 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R1_market_volatility_state)               | skeleton-93ce4b9755fbcc1f |       0.966536 |       0.999087  |
| a7al2z1_02f0aa46165930ef | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,72)),R3_liquidity_cycle_state)                     | skeleton-2d05b222193f0313 |       0.969302 |       0.999552  |
| a7al2z1_03adf58750b956c5 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)        | skeleton-2d05b222193f0313 |       0.968963 |       0.999201  |
| a7al2z1_09d7f79331848fdb | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)        | skeleton-2d05b222193f0313 |       0.968915 |       0.999152  |
| a7al2z1_09e2fd4a441553b4 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,24)),R0_market_trend_state)                     | skeleton-2d05b222193f0313 |       0.968868 |       0.999152  |
| a7al2z1_0b6e676dd75c1780 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,72)),R0_market_trend_state)                        | skeleton-2d05b222193f0313 |       0.969256 |       0.999552  |
| a7al2z1_13af2e476c2f9448 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(funding_rate,168)),R2_market_breadth_state)                          | skeleton-2d05b222193f0313 |       0.216002 |       0.982339  |
| a7al2z1_013bc4e85cf82308 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(trade_quote_volume,24),R2_market_breadth_state)                        | skeleton-619f11aa0aaa14be |       0.969616 |       1         |
| a7al2z1_0417b7031aaf2f21 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(premium_close_bps,72)),R0_market_trend_state)                       | skeleton-93ce4b9755fbcc1f |       0.966924 |       0.997794  |
| a7al2z1_08a69b564ec2fd77 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(premium_close_bps,168)),R3_liquidity_cycle_state)                   | skeleton-93ce4b9755fbcc1f |       0.96231  |       0.997937  |
| a7al2z1_1f7b91b01c23c231 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,24)),R2_market_breadth_state)                      | skeleton-2d05b222193f0313 |       0.969279 |       0.999528  |
| a7al2z1_272ab0e782d365d1 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(trade_quote_volume,168)),R1_market_volatility_state)                 | skeleton-2d05b222193f0313 |       0.968499 |       0.999924  |
| a7al2z1_27b834f852d4445d | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(funding_rate,168)),R0_market_trend_state)                            | skeleton-2d05b222193f0313 |       0.216002 |       0.982339  |
| a7al2z1_28f1910fe86e39c5 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,168)),R3_liquidity_cycle_state)                    | skeleton-2d05b222193f0313 |       0.96935  |       0.999601  |

## Evaluation Trace Preview

| candidate_id             | objective_family                     | expression                                                                                   | skeleton_key              | was_z1_selected   | eval_success   |   finite_share |   nonzero_share | activity_ok   |   min_value |   max_value | error   |
|:-------------------------|:-------------------------------------|:---------------------------------------------------------------------------------------------|:--------------------------|:------------------|:---------------|---------------:|----------------:|:--------------|------------:|------------:|:--------|
| a7al2z1_2a30bd2ef1694609 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336)))) | skeleton-0f95d494e3163e7b | True              | True           |     0.145621   |        1        | False         | -24.2615    |   25        |         |
| a7al2z1_0744891cb8e08bbf | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Mean(funding_rate,48)))                         | skeleton-612ffe194eccb811 | True              | True           |     0.00197929 |        0.976971 | False         |  -0.989583  |    0.46875  |         |
| a7al2z1_0e0300e409dbd037 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_index_basis_bps,48)),Rank(Mean(funding_rate,48)))                         | skeleton-612ffe194eccb811 | True              | True           |     0.00197929 |        0.991239 | False         |  -0.989583  |    0        |         |
| a7al2z1_18a6b78a193210db | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_trade_basis_bps,168)),Rank(Mean(funding_rate,168)))                       | skeleton-612ffe194eccb811 | True              | True           |     0.217108   |        0.998795 | True          |  -0.989583  |    0.962963 |         |
| a7al2z1_0025716230424fb7 | Z0_funding_basis_premium_dislocation | Rank(Abs(ZScore(Mean(mark_trade_basis_bps,48))))                                             | skeleton-6ebd7d4c1e06c9bc | True              | True           |     0.998248   |        1        | True          |   0.0104167 |    1        |         |
| a7al2z1_1fa487e13f578276 | Z0_funding_basis_premium_dislocation | Rank(Abs(ZScore(Delta(premium_close_bps,168))))                                              | skeleton-8a6cec079a5f7997 | True              | True           |     0.990848   |        1        | True          |   0.0104167 |    1        |         |
| a7al2z1_0098920a5ffc5a6b | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,168)),Rank(Delta(funding_rate,168)))                     | skeleton-8ad46b9059e6381f | True              | True           |     0.147711   |        0.986567 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_0ec1de18c96369a2 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,24)),Rank(Delta(funding_rate,24)))                          | skeleton-8ad46b9059e6381f | True              | True           |     0.149381   |        0.986173 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_0fd66b0116db4b6b | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,336)),Rank(Delta(funding_rate,336)))                     | skeleton-8ad46b9059e6381f | True              | True           |     0.146091   |        0.986513 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_094c52bafda2cb02 | Z0_funding_basis_premium_dislocation | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)     | skeleton-93ce4b9755fbcc1f | True              | True           |     0.966536   |        0.999087 | True          |  -0.494792  |    0.494792 |         |
| a7al2z1_069b0f75654dadde | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Mean(premium_close_bps,168))),Winsor(ZScore(Mean(funding_rate,168))))      | skeleton-f59f8b03ae1fd3c4 | True              | True           |     0.216799   |        1        | True          |  -8.32604   |   25        |         |
| a7al2z1_2c511a8b8037ed73 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.0543168  |        1        | False         | -25         |   25        |         |
| a7al2z1_353ec53a77aa2b5e | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.147832   |        1        | False         | -25         |   25        |         |
| a7al2z1_37546f2175cb7dec | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,336))),Winsor(ZScore(Delta(funding_rate,336))))    | skeleton-0f95d494e3163e7b | False             | True           |     0.145619   |        1        | False         | -25         |   25        |         |
| a7al2z1_392d429448f04dd9 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.0544104  |        1        | False         | -25         |   25        |         |
| a7al2z1_3aeaf330cbfe790b | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.148167   |        1        | False         | -25         |   25        |         |
| a7al2z1_4e26c9492ca0dc98 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,168))),Winsor(ZScore(Delta(funding_rate,168)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.147085   |        1        | False         | -25         |   25        |         |
| a7al2z1_53722da81325036e | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.148339   |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_615886de5d54eb10 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.14834    |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_6f2eb7ccca45a9e1 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,168))),Winsor(ZScore(Delta(funding_rate,168))))    | skeleton-0f95d494e3163e7b | False             | True           |     0.146972   |        1        | False         | -25         |   25        |         |
| a7al2z1_959734fcd6c011bc | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,168))),Winsor(ZScore(Delta(funding_rate,168)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.146973   |        1        | False         | -25         |   25        |         |
| a7al2z1_9dc4dfe8c8adf016 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.14807    |        1        | False         | -25         |   25        |         |
| a7al2z1_c490408540eb4787 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.0544104  |        1        | False         | -23.7519    |   23.6173   |         |
| a7al2z1_dc95bab1d560fff1 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.147833   |        1        | False         | -25         |   25        |         |
| a7al2z1_e32e3f4554a753d6 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.148434   |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_f68f3e8dd54fd345 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.147933   |        1        | False         | -25         |   25        |         |
| a7al2z1_feed841ff4307e9f | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.148069   |        1        | False         | -25         |   25        |         |
| a7al2z1_ffa4e9d0da121a6c | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.145753   |        1        | False         | -25         |   25        |         |
| a7al2z1_2b3d7fa1fd0bb43c | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,12)),Rank(Delta(funding_rate,12)))                          | skeleton-8ad46b9059e6381f | False             | True           |     0.0554162  |        0.991373 | False         |  -0.989583  |    0.967742 |         |
| a7al2z1_39511d7433049b30 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,48)),Rank(Delta(funding_rate,48)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.149161   |        0.992822 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_439f2d494207a873 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,12)),Rank(Delta(funding_rate,12)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.0555098  |        0.997197 | False         |  -0.989583  |    0.967742 |         |
| a7al2z1_48e6137a625f4d59 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,168)),Rank(Delta(funding_rate,168)))                        | skeleton-8ad46b9059e6381f | False             | True           |     0.14771    |        0.984578 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_5da8a37d861c48f5 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,72)),Rank(Delta(funding_rate,72)))                          | skeleton-8ad46b9059e6381f | False             | True           |     0.148765   |        0.984011 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_6dfc9a8e5722ae35 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,72)),Rank(Delta(funding_rate,72)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.148866   |        0.992515 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_8b2cfab0feb99325 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,48)),Rank(Delta(funding_rate,48)))                          | skeleton-8ad46b9059e6381f | False             | True           |     0.149063   |        0.984412 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_8b925afb92adf975 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,48)),Rank(Delta(funding_rate,48)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.149065   |        0.986895 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_8e28967850191917 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,24)),Rank(Delta(funding_rate,24)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.149476   |        0.992602 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_a2afb055d0fb1d06 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,168)),Rank(Delta(funding_rate,168)))                     | skeleton-8ad46b9059e6381f | False             | True           |     0.147823   |        0.992707 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_ba65bcf60db21497 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,24)),Rank(Delta(funding_rate,24)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.149382   |        0.987755 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_d9152b6ab7f91fb8 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,12)),Rank(Delta(funding_rate,12)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.0555098  |        0.992708 | False         |  -0.989583  |    0.967742 |         |
| a7al2z1_e6bb9414422e29dc | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,72)),Rank(Delta(funding_rate,72)))                       | skeleton-8ad46b9059e6381f | False             | True           |     0.148767   |        0.986286 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_e9c19ff76009938f | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_trade_basis_bps,336)),Rank(Delta(funding_rate,336)))                     | skeleton-8ad46b9059e6381f | False             | True           |     0.146224   |        0.99283  | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_f3c9e253afa19dd3 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,336)),Rank(Delta(funding_rate,336)))                        | skeleton-8ad46b9059e6381f | False             | True           |     0.14609    |        0.984135 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_2a30bd2ef1694609 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336)))) | skeleton-0f95d494e3163e7b | True              | True           |     0.145621   |        1        | False         | -24.2615    |   25        |         |
| a7al2z1_0744891cb8e08bbf | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Mean(funding_rate,48)))                         | skeleton-612ffe194eccb811 | True              | True           |     0.00197929 |        0.976971 | False         |  -0.989583  |    0.46875  |         |
| a7al2z1_0e0300e409dbd037 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_index_basis_bps,48)),Rank(Mean(funding_rate,48)))                         | skeleton-612ffe194eccb811 | True              | True           |     0.00197929 |        0.991239 | False         |  -0.989583  |    0        |         |
| a7al2z1_19b6336bd472bdd9 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_trade_basis_bps,72)),Rank(Mean(funding_rate,72)))                         | skeleton-612ffe194eccb811 | True              | True           |     0.00228746 |        0.984839 | False         |  -0.989583  |    0.572917 |         |
| a7al2z1_0313bc007ac9963d | Z0_funding_basis_premium_dislocation | Rank(Abs(ZScore(Mean(premium_close_bps,12))))                                                | skeleton-6ebd7d4c1e06c9bc | True              | True           |     0.998393   |        1        | True          |   0.0104167 |    1        |         |
| a7al2z1_23cc7365fa741d7c | Z0_funding_basis_premium_dislocation | Rank(Abs(ZScore(Mean(premium_close_bps,72))))                                                | skeleton-6ebd7d4c1e06c9bc | True              | True           |     0.997887   |        1        | True          |   0.0104167 |    1        |         |
| a7al2z1_0098920a5ffc5a6b | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,168)),Rank(Delta(funding_rate,168)))                     | skeleton-8ad46b9059e6381f | True              | True           |     0.147711   |        0.986567 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_0ec1de18c96369a2 | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(premium_close_bps,24)),Rank(Delta(funding_rate,24)))                          | skeleton-8ad46b9059e6381f | True              | True           |     0.149381   |        0.986173 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_0fd66b0116db4b6b | Z0_funding_basis_premium_dislocation | Sub(Rank(Delta(mark_index_basis_bps,336)),Rank(Delta(funding_rate,336)))                     | skeleton-8ad46b9059e6381f | True              | True           |     0.146091   |        0.986513 | False         |  -0.989583  |    0.989583 |         |
| a7al2z1_0a1368b901e4b360 | Z0_funding_basis_premium_dislocation | GroupNeutralize(Rank(Delta(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)     | skeleton-93ce4b9755fbcc1f | True              | True           |     0.968866   |        0.999138 | True          |  -0.494792  |    0.494792 |         |
| a7al2z1_2785f094943ec26b | Z0_funding_basis_premium_dislocation | GroupNeutralize(Rank(Delta(mark_trade_basis_bps,72)),R5_basis_premium_dislocation_state)     | skeleton-93ce4b9755fbcc1f | True              | True           |     0.967333   |        0.998569 | True          |  -0.494792  |    0.494792 |         |
| a7al2z1_2c511a8b8037ed73 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.0543168  |        1        | False         | -25         |   25        |         |
| a7al2z1_353ec53a77aa2b5e | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.147832   |        1        | False         | -25         |   25        |         |
| a7al2z1_37546f2175cb7dec | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,336))),Winsor(ZScore(Delta(funding_rate,336))))    | skeleton-0f95d494e3163e7b | False             | True           |     0.145619   |        1        | False         | -25         |   25        |         |
| a7al2z1_392d429448f04dd9 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.0544104  |        1        | False         | -25         |   25        |         |
| a7al2z1_3aeaf330cbfe790b | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.148167   |        1        | False         | -25         |   25        |         |
| a7al2z1_4e26c9492ca0dc98 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,168))),Winsor(ZScore(Delta(funding_rate,168)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.147085   |        1        | False         | -25         |   25        |         |
| a7al2z1_53722da81325036e | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.148339   |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_615886de5d54eb10 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.14834    |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_6f2eb7ccca45a9e1 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,168))),Winsor(ZScore(Delta(funding_rate,168))))    | skeleton-0f95d494e3163e7b | False             | True           |     0.146972   |        1        | False         | -25         |   25        |         |
| a7al2z1_959734fcd6c011bc | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,168))),Winsor(ZScore(Delta(funding_rate,168)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.146973   |        1        | False         | -25         |   25        |         |
| a7al2z1_9dc4dfe8c8adf016 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.14807    |        1        | False         | -25         |   25        |         |
| a7al2z1_c490408540eb4787 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,12))),Winsor(ZScore(Delta(funding_rate,12))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.0544104  |        1        | False         | -23.7519    |   23.6173   |         |
| a7al2z1_dc95bab1d560fff1 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.147833   |        1        | False         | -25         |   25        |         |
| a7al2z1_e32e3f4554a753d6 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,24))),Winsor(ZScore(Delta(funding_rate,24))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.148434   |        0.999997 | False         | -25         |   25        |         |
| a7al2z1_f68f3e8dd54fd345 | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,72))),Winsor(ZScore(Delta(funding_rate,72))))   | skeleton-0f95d494e3163e7b | False             | True           |     0.147933   |        1        | False         | -25         |   25        |         |
| a7al2z1_feed841ff4307e9f | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(premium_close_bps,48))),Winsor(ZScore(Delta(funding_rate,48))))      | skeleton-0f95d494e3163e7b | False             | True           |     0.148069   |        1        | False         | -25         |   25        |         |
| a7al2z1_ffa4e9d0da121a6c | Z0_funding_basis_premium_dislocation | Mul(Winsor(ZScore(Delta(mark_trade_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336)))) | skeleton-0f95d494e3163e7b | False             | True           |     0.145753   |        1        | False         | -25         |   25        |         |
| a7al2z1_2b2aa964827604cb | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_trade_basis_bps,24)),Rank(Mean(funding_rate,24)))                         | skeleton-612ffe194eccb811 | False             | True           |     0.00165725 |        0.966816 | False         |  -0.989583  |    0.489583 |         |
| a7al2z1_5d8b43fa29769147 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,336)),Rank(Mean(funding_rate,336)))                          | skeleton-612ffe194eccb811 | False             | True           |     0.970633   |        0.94177  | True          |  -0.822917  |    0.9375   |         |
| a7al2z1_6ba1e2ac12dfd3d3 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_index_basis_bps,24)),Rank(Mean(funding_rate,24)))                         | skeleton-612ffe194eccb811 | False             | True           |     0.00165725 |        0.984454 | False         |  -0.989583  |    0        |         |
| a7al2z1_6f042eef7a6bcf0c | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,72)),Rank(Mean(funding_rate,72)))                            | skeleton-612ffe194eccb811 | False             | True           |     0.00228746 |        0.991986 | False         |  -0.989583  |    0        |         |
| a7al2z1_7db4e9cabcca4c6f | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,12)),Rank(Mean(funding_rate,12)))                            | skeleton-612ffe194eccb811 | False             | True           |     0.00174445 |        0.987504 | False         |  -0.989583  |    0        |         |
| a7al2z1_873710cf89dafc41 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,48)),Rank(Mean(funding_rate,48)))                            | skeleton-612ffe194eccb811 | False             | True           |     0.00197929 |        0.990238 | False         |  -0.989583  |    0        |         |
| a7al2z1_902f31baa5005418 | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,168)),Rank(Mean(funding_rate,168)))                          | skeleton-612ffe194eccb811 | False             | True           |     0.216799   |        0.963621 | True          |  -0.760081  |    0.929167 |         |
| a7al2z1_a02fbb43bcd5f91a | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(premium_close_bps,24)),Rank(Mean(funding_rate,24)))                            | skeleton-612ffe194eccb811 | False             | True           |     0.00165725 |        0.98565  | False         |  -0.989583  |    0        |         |
| a7al2z1_a4663c2a7068240d | Z0_funding_basis_premium_dislocation | Sub(Rank(Mean(mark_index_basis_bps,12)),Rank(Mean(funding_rate,12)))                         | skeleton-612ffe194eccb811 | False             | True           |     0.00174445 |        0.985231 | False         |  -0.989583  |    0        |         |

## Blockers

| candidate_id             | blocker                      | detail                           |
|:-------------------------|:-----------------------------|:---------------------------------|
| a7al2z1_2a30bd2ef1694609 | activity_or_coverage_failure | finite=0.145621;nonzero=1.000000 |
| a7al2z1_0744891cb8e08bbf | activity_or_coverage_failure | finite=0.001979;nonzero=0.976971 |
| a7al2z1_0e0300e409dbd037 | activity_or_coverage_failure | finite=0.001979;nonzero=0.991239 |
| a7al2z1_0098920a5ffc5a6b | activity_or_coverage_failure | finite=0.147711;nonzero=0.986567 |
| a7al2z1_0ec1de18c96369a2 | activity_or_coverage_failure | finite=0.149381;nonzero=0.986173 |
| a7al2z1_0fd66b0116db4b6b | activity_or_coverage_failure | finite=0.146091;nonzero=0.986513 |
| a7al2z1_2c511a8b8037ed73 | activity_or_coverage_failure | finite=0.054317;nonzero=1.000000 |
| a7al2z1_353ec53a77aa2b5e | activity_or_coverage_failure | finite=0.147832;nonzero=1.000000 |
| a7al2z1_37546f2175cb7dec | activity_or_coverage_failure | finite=0.145619;nonzero=1.000000 |
| a7al2z1_392d429448f04dd9 | activity_or_coverage_failure | finite=0.054410;nonzero=1.000000 |
| a7al2z1_3aeaf330cbfe790b | activity_or_coverage_failure | finite=0.148167;nonzero=1.000000 |
| a7al2z1_4e26c9492ca0dc98 | activity_or_coverage_failure | finite=0.147085;nonzero=1.000000 |
| a7al2z1_53722da81325036e | activity_or_coverage_failure | finite=0.148339;nonzero=0.999997 |
| a7al2z1_615886de5d54eb10 | activity_or_coverage_failure | finite=0.148340;nonzero=0.999997 |
| a7al2z1_6f2eb7ccca45a9e1 | activity_or_coverage_failure | finite=0.146972;nonzero=1.000000 |
| a7al2z1_959734fcd6c011bc | activity_or_coverage_failure | finite=0.146973;nonzero=1.000000 |
| a7al2z1_9dc4dfe8c8adf016 | activity_or_coverage_failure | finite=0.148070;nonzero=1.000000 |
| a7al2z1_c490408540eb4787 | activity_or_coverage_failure | finite=0.054410;nonzero=1.000000 |
| a7al2z1_dc95bab1d560fff1 | activity_or_coverage_failure | finite=0.147833;nonzero=1.000000 |
| a7al2z1_e32e3f4554a753d6 | activity_or_coverage_failure | finite=0.148434;nonzero=0.999997 |
| a7al2z1_f68f3e8dd54fd345 | activity_or_coverage_failure | finite=0.147933;nonzero=1.000000 |
| a7al2z1_feed841ff4307e9f | activity_or_coverage_failure | finite=0.148069;nonzero=1.000000 |
| a7al2z1_ffa4e9d0da121a6c | activity_or_coverage_failure | finite=0.145753;nonzero=1.000000 |
| a7al2z1_2b3d7fa1fd0bb43c | activity_or_coverage_failure | finite=0.055416;nonzero=0.991373 |
| a7al2z1_39511d7433049b30 | activity_or_coverage_failure | finite=0.149161;nonzero=0.992822 |
| a7al2z1_439f2d494207a873 | activity_or_coverage_failure | finite=0.055510;nonzero=0.997197 |
| a7al2z1_48e6137a625f4d59 | activity_or_coverage_failure | finite=0.147710;nonzero=0.984578 |
| a7al2z1_5da8a37d861c48f5 | activity_or_coverage_failure | finite=0.148765;nonzero=0.984011 |
| a7al2z1_6dfc9a8e5722ae35 | activity_or_coverage_failure | finite=0.148866;nonzero=0.992515 |
| a7al2z1_8b2cfab0feb99325 | activity_or_coverage_failure | finite=0.149063;nonzero=0.984412 |
| a7al2z1_8b925afb92adf975 | activity_or_coverage_failure | finite=0.149065;nonzero=0.986895 |
| a7al2z1_8e28967850191917 | activity_or_coverage_failure | finite=0.149476;nonzero=0.992602 |
| a7al2z1_a2afb055d0fb1d06 | activity_or_coverage_failure | finite=0.147823;nonzero=0.992707 |
| a7al2z1_ba65bcf60db21497 | activity_or_coverage_failure | finite=0.149382;nonzero=0.987755 |
| a7al2z1_d9152b6ab7f91fb8 | activity_or_coverage_failure | finite=0.055510;nonzero=0.992708 |
| a7al2z1_e6bb9414422e29dc | activity_or_coverage_failure | finite=0.148767;nonzero=0.986286 |
| a7al2z1_e9c19ff76009938f | activity_or_coverage_failure | finite=0.146224;nonzero=0.992830 |
| a7al2z1_f3c9e253afa19dd3 | activity_or_coverage_failure | finite=0.146090;nonzero=0.984135 |
| a7al2z1_2a30bd2ef1694609 | activity_or_coverage_failure | finite=0.145621;nonzero=1.000000 |
| a7al2z1_0744891cb8e08bbf | activity_or_coverage_failure | finite=0.001979;nonzero=0.976971 |
| a7al2z1_0e0300e409dbd037 | activity_or_coverage_failure | finite=0.001979;nonzero=0.991239 |
| a7al2z1_19b6336bd472bdd9 | activity_or_coverage_failure | finite=0.002287;nonzero=0.984839 |
| a7al2z1_0098920a5ffc5a6b | activity_or_coverage_failure | finite=0.147711;nonzero=0.986567 |
| a7al2z1_0ec1de18c96369a2 | activity_or_coverage_failure | finite=0.149381;nonzero=0.986173 |
| a7al2z1_0fd66b0116db4b6b | activity_or_coverage_failure | finite=0.146091;nonzero=0.986513 |
| a7al2z1_2c511a8b8037ed73 | activity_or_coverage_failure | finite=0.054317;nonzero=1.000000 |
| a7al2z1_353ec53a77aa2b5e | activity_or_coverage_failure | finite=0.147832;nonzero=1.000000 |
| a7al2z1_37546f2175cb7dec | activity_or_coverage_failure | finite=0.145619;nonzero=1.000000 |
| a7al2z1_392d429448f04dd9 | activity_or_coverage_failure | finite=0.054410;nonzero=1.000000 |
| a7al2z1_3aeaf330cbfe790b | activity_or_coverage_failure | finite=0.148167;nonzero=1.000000 |
| a7al2z1_4e26c9492ca0dc98 | activity_or_coverage_failure | finite=0.147085;nonzero=1.000000 |
| a7al2z1_53722da81325036e | activity_or_coverage_failure | finite=0.148339;nonzero=0.999997 |
| a7al2z1_615886de5d54eb10 | activity_or_coverage_failure | finite=0.148340;nonzero=0.999997 |
| a7al2z1_6f2eb7ccca45a9e1 | activity_or_coverage_failure | finite=0.146972;nonzero=1.000000 |
| a7al2z1_959734fcd6c011bc | activity_or_coverage_failure | finite=0.146973;nonzero=1.000000 |
| a7al2z1_9dc4dfe8c8adf016 | activity_or_coverage_failure | finite=0.148070;nonzero=1.000000 |
| a7al2z1_c490408540eb4787 | activity_or_coverage_failure | finite=0.054410;nonzero=1.000000 |
| a7al2z1_dc95bab1d560fff1 | activity_or_coverage_failure | finite=0.147833;nonzero=1.000000 |
| a7al2z1_e32e3f4554a753d6 | activity_or_coverage_failure | finite=0.148434;nonzero=0.999997 |
| a7al2z1_f68f3e8dd54fd345 | activity_or_coverage_failure | finite=0.147933;nonzero=1.000000 |
| a7al2z1_feed841ff4307e9f | activity_or_coverage_failure | finite=0.148069;nonzero=1.000000 |
| a7al2z1_ffa4e9d0da121a6c | activity_or_coverage_failure | finite=0.145753;nonzero=1.000000 |
| a7al2z1_2b2aa964827604cb | activity_or_coverage_failure | finite=0.001657;nonzero=0.966816 |
| a7al2z1_6ba1e2ac12dfd3d3 | activity_or_coverage_failure | finite=0.001657;nonzero=0.984454 |
| a7al2z1_6f042eef7a6bcf0c | activity_or_coverage_failure | finite=0.002287;nonzero=0.991986 |
| a7al2z1_7db4e9cabcca4c6f | activity_or_coverage_failure | finite=0.001744;nonzero=0.987504 |
| a7al2z1_873710cf89dafc41 | activity_or_coverage_failure | finite=0.001979;nonzero=0.990238 |
| a7al2z1_a02fbb43bcd5f91a | activity_or_coverage_failure | finite=0.001657;nonzero=0.985650 |
| a7al2z1_a4663c2a7068240d | activity_or_coverage_failure | finite=0.001744;nonzero=0.985231 |
| a7al2z1_e60f406c997cf4d4 | activity_or_coverage_failure | finite=0.001744;nonzero=0.961091 |
| a7al2z1_e9caec36347952ea | activity_or_coverage_failure | finite=0.002287;nonzero=0.991553 |
| a7al2z1_084c5de0fd767b63 | activity_or_coverage_failure | finite=0.998248;nonzero=0.001272 |
| a7al2z1_084c5de0fd767b63 | activity_or_coverage_failure | finite=0.998248;nonzero=0.001272 |
| a7al2z1_1026fb4689800bcc | activity_or_coverage_failure | finite=0.998248;nonzero=0.001272 |
| a7al2z1_14c037279916f855 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z1_17e5d01f0bfb02a9 | activity_or_coverage_failure | finite=0.000027;nonzero=0.666667 |
| a7al2z1_02835f7a0f1e2191 | activity_or_coverage_failure | finite=0.148060;nonzero=1.000000 |
| a7al2z1_0f62f529551c2879 | activity_or_coverage_failure | finite=0.148226;nonzero=1.000000 |
| a7al2z1_04f3782ccb5d5429 | activity_or_coverage_failure | finite=0.144065;nonzero=0.993524 |
| a7al2z1_00a0bd50986c3107 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
