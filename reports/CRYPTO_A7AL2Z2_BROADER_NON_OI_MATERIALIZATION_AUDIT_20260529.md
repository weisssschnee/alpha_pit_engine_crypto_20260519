# CRYPTO A7AL-2Z2 BROADER NON-OI MATERIALIZATION AUDIT

Generated: 2026-05-29T03:36:19Z

## Decision

`HOLD_A7AL2Z2_EVAL_OR_ACTIVITY_FAILURE`

Z2 evaluates Z1-selected static expressions on a bounded strict-universe sample. It does not compute returns, run replay, train, or authorize proof.

## Manifest

```json
{
  "activity_failure_count": 20,
  "authorizes_a7al2z3_numeric_preflight_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay_execution": false,
  "authorizes_shadow_paper_live": false,
  "base_numeric_field_count": 18,
  "decision": "HOLD_A7AL2Z2_EVAL_OR_ACTIVITY_FAILURE",
  "eval_failure_count": 0,
  "evaluated_candidates": 128,
  "executes_materialization_audit": true,
  "executes_replay": false,
  "executes_training": false,
  "generated_at": "2026-05-29T03:36:19Z",
  "group_field_count": 11,
  "latent_numeric_field_count": 0,
  "numeric_field_count": 18,
  "stage": "A7AL-2Z2",
  "symbols_loaded": 96,
  "timestamps": 21025,
  "uses_may": false
}
```

## Family Summary

| objective_family                         |   evaluated_count |   eval_success_count |   activity_ok_count |   median_finite_share |   median_nonzero_share |
|:-----------------------------------------|------------------:|---------------------:|--------------------:|----------------------:|-----------------------:|
| Z0_funding_basis_premium_dislocation     |                16 |                   16 |                   9 |              0.216953 |               0.998941 |
| Z1_price_range_volatility_structure      |                16 |                   16 |                  14 |              0.997791 |               1        |
| Z2_liquidity_taker_microstructure_lite   |                16 |                   16 |                  16 |              0.997987 |               1        |
| Z3_basis_price_trend_reversal            |                16 |                   16 |                  16 |              0.996239 |               0.999139 |
| Z4_upper_regime_relative_value           |                16 |                   16 |                  12 |              0.967895 |               0.999177 |
| Z5_latent_listing_meme_neutral_structure |                16 |                   16 |                  12 |              0.978701 |               0.997458 |
| Z6_cross_sectional_relative_flow_value   |                16 |                   16 |                  13 |              0.995775 |               0.999999 |
| Z7_market_regime_price_breadth           |                16 |                   16 |                  16 |              0.967915 |               0.999924 |

## Candidate Evaluation Summary

| candidate_id             | objective_family                       | expression                                                                                     | operator_signature               | eval_success   |   finite_share |   nonzero_share | activity_ok   |    min_value |     max_value | error   |
|:-------------------------|:---------------------------------------|:-----------------------------------------------------------------------------------------------|:---------------------------------|:---------------|---------------:|----------------:|:--------------|-------------:|--------------:|:--------|
| a7al2z1_0025716230424fb7 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(mark_trade_basis_bps,48))))                                               | Abs\|Mean\|Rank\|ZScore          | True           |    0.998248    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0098920a5ffc5a6b | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(mark_index_basis_bps,168)),Rank(Delta(funding_rate,168)))                       | Delta\|Rank\|Sub                 | True           |    0.147711    |      0.986567   | False         |  -0.989583   |   0.989583    |         |
| a7al2z1_0313bc007ac9963d | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,12))))                                                  | Abs\|Mean\|Rank\|ZScore          | True           |    0.998393    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_069b0f75654dadde | Z0_funding_basis_premium_dislocation   | Mul(Winsor(ZScore(Mean(premium_close_bps,168))),Winsor(ZScore(Mean(funding_rate,168))))        | Mean\|Mul\|Winsor\|ZScore        | True           |    0.216799    |      1          | True          |  -8.32604    |  25           |         |
| a7al2z1_0744891cb8e08bbf | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Mean(funding_rate,48)))                           | Mean\|Rank\|Sub                  | True           |    0.00197929  |      0.976971   | False         |  -0.989583   |   0.46875     |         |
| a7al2z1_094c52bafda2cb02 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)       | Delta\|GroupNeutralize\|Rank     | True           |    0.966536    |      0.999087   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0a1368b901e4b360 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)       | Delta\|GroupNeutralize\|Rank     | True           |    0.968866    |      0.999138   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0e0300e409dbd037 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_index_basis_bps,48)),Rank(Mean(funding_rate,48)))                           | Mean\|Rank\|Sub                  | True           |    0.00197929  |      0.991239   | False         |  -0.989583   |   0           |         |
| a7al2z1_0ec1de18c96369a2 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(premium_close_bps,24)),Rank(Delta(funding_rate,24)))                            | Delta\|Rank\|Sub                 | True           |    0.149381    |      0.986173   | False         |  -0.989583   |   0.989583    |         |
| a7al2z1_0fd66b0116db4b6b | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(mark_index_basis_bps,336)),Rank(Delta(funding_rate,336)))                       | Delta\|Rank\|Sub                 | True           |    0.146091    |      0.986513   | False         |  -0.989583   |   0.989583    |         |
| a7al2z1_18a6b78a193210db | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,168)),Rank(Mean(funding_rate,168)))                         | Mean\|Rank\|Sub                  | True           |    0.217108    |      0.998795   | True          |  -0.989583   |   0.962963    |         |
| a7al2z1_19b6336bd472bdd9 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,72)),Rank(Mean(funding_rate,72)))                           | Mean\|Rank\|Sub                  | True           |    0.00228746  |      0.984839   | False         |  -0.989583   |   0.572917    |         |
| a7al2z1_1fa487e13f578276 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Delta(premium_close_bps,168))))                                                | Abs\|Delta\|Rank\|ZScore         | True           |    0.990848    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_23cc7365fa741d7c | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,72))))                                                  | Abs\|Mean\|Rank\|ZScore          | True           |    0.997887    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_2785f094943ec26b | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_trade_basis_bps,72)),R5_basis_premium_dislocation_state)       | Delta\|GroupNeutralize\|Rank     | True           |    0.967333    |      0.998569   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_2a30bd2ef1694609 | Z0_funding_basis_premium_dislocation   | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336))))   | Delta\|Mul\|Winsor\|ZScore       | True           |    0.145621    |      1          | False         | -24.2615     |  25           |         |
| a7al2z1_0137caa89f7a1268 | Z1_price_range_volatility_structure    | SafeDiv(Mean(Sub(trade_high,trade_low),72),Mean(trade_close,72))                               | Mean\|SafeDiv\|Sub               | True           |    0.998248    |      1          | True          |   0.00211734 |   0.164487    |         |
| a7al2z1_028db6316a60db86 | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(mark_close,72))))                                                        | Abs\|Delta\|Rank\|ZScore         | True           |    0.99587     |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_066701faa05eebbc | Z1_price_range_volatility_structure    | Mul(Winsor(ZScore(Delta(trade_close,72))),Neg(Winsor(ZScore(Delta(mark_close,72)))))           | Delta\|Mul\|Neg\|Winsor\|ZScore  | True           |    0.99587     |      1          | True          | -25          |   9.00898     |         |
| a7al2z1_07116c7a8a24208e | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,24)),Rank(Delta(trade_close,24)))                                    | Delta\|Rank\|Sub                 | True           |    0.998153    |      0.254066   | True          |  -0.979167   |   0.979167    |         |
| a7al2z1_084c5de0fd767b63 | Z1_price_range_volatility_structure    | Sub(Rank(Mean(mark_close,72)),Rank(Mean(trade_close,72)))                                      | Mean\|Rank\|Sub                  | True           |    0.998248    |      0.00127205 | False         |  -0.0208333  |   0.0208333   |         |
| a7al2z1_086296df472ad4ae | Z1_price_range_volatility_structure    | Neg(Rank(Delta(index_close,168)))                                                              | Delta\|Neg\|Rank                 | True           |    0.990412    |      1          | True          |  -1          |  -0.0104167   |         |
| a7al2z1_09ec291c3c80efca | Z1_price_range_volatility_structure    | Sub(Rank(Mean(trade_close,72)),Rank(Mean(index_close,72)))                                     | Mean\|Rank\|Sub                  | True           |    0.997548    |      0.0709871  | True          |  -0.0234649  |   0.0208333   |         |
| a7al2z1_0b6494a3a4ef9490 | Z1_price_range_volatility_structure    | GroupNeutralize(Rank(Mean(Sub(trade_high,trade_low),24)),R1_market_volatility_state)           | GroupNeutralize\|Mean\|Rank\|Sub | True           |    0.968499    |      0.999889   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0e268536d1126a2d | Z1_price_range_volatility_structure    | Sub(Rank(Mean(index_close,12)),Rank(Mean(trade_close,12)))                                     | Mean\|Rank\|Sub                  | True           |    0.998035    |      0.0753576  | True          |  -0.03125    |   0.0319149   |         |
| a7al2z1_0f752369161ae869 | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,336)),Rank(Delta(index_close,336)))                                  | Delta\|Rank\|Sub                 | True           |    0.982255    |      0.224583   | True          |  -0.96875    |   0.947917    |         |
| a7al2z1_1026fb4689800bcc | Z1_price_range_volatility_structure    | Sub(Rank(Mean(trade_close,72)),Rank(Mean(mark_close,72)))                                      | Mean\|Rank\|Sub                  | True           |    0.998248    |      0.00127205 | False         |  -0.0208333  |   0.0208333   |         |
| a7al2z1_10d47299f1a5d1ee | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(index_close,24))))                                                       | Abs\|Delta\|Rank\|ZScore         | True           |    0.997404    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_18a394084ddac9b5 | Z1_price_range_volatility_structure    | Mul(Rank(Mean(Sub(mark_high,mark_low),24)),Neg(Rank(Delta(trade_close,24))))                   | Delta\|Mean\|Mul\|Neg\|Rank\|Sub | True           |    0.998153    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_1919cb4f0227005e | Z1_price_range_volatility_structure    | Rank(Delta(mark_close,72))                                                                     | Delta\|Rank                      | True           |    0.99587     |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_2d6e3bd57d32e9b1 | Z1_price_range_volatility_structure    | Rank(Delta(Sub(trade_high,trade_low),24))                                                      | Delta\|Rank\|Sub                 | True           |    0.998153    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_48338dedf315f7a2 | Z1_price_range_volatility_structure    | Rank(Mean(Sub(mark_high,mark_low),72))                                                         | Mean\|Rank\|Sub                  | True           |    0.998248    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0115d3dbe93c2618 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_sell_volume_ratio_last,24)),R3_liquidity_cycle_state)     | Delta\|GroupNeutralize\|Rank     | True           |    0.968664    |      0.999924   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_031574ff37957433 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,168))                                                   | Delta\|Rank                      | True           |    0.991209    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_03845c7516491252 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_quote_volume,24)),R3_liquidity_cycle_state)               | Delta\|GroupNeutralize\|Rank     | True           |    0.969616    |      0.999924   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_04308808db9785c7 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,12))                                                    | Delta\|Rank                      | True           |    0.998629    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_05bbcd80f3bb1f84 | Z2_liquidity_taker_microstructure_lite | Rank(Mean(taker_buy_sell_volume_ratio_last,6))                                                 | Mean\|Rank                       | True           |    0.998391    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_06158e66c283198d | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,12))),Neg(Winsor(ZScore(Delta(trade_close,12)))))   | Delta\|Mul\|Neg\|Winsor\|ZScore  | True           |    0.998724    |      1          | True          | -25          |  25           |         |
| a7al2z1_06179c2b2c6fa22c | Z2_liquidity_taker_microstructure_lite | Rank(Delta(taker_buy_sell_volume_ratio_last,12))                                               | Delta\|Rank                      | True           |    0.99782     |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0713ad23e3e4f1a1 | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,168))),Neg(Winsor(ZScore(Delta(trade_close,24)))))  | Delta\|Mul\|Neg\|Winsor\|ZScore  | True           |    0.991304    |      1          | True          | -25          |  25           |         |
| a7al2z1_07b10f27debc2020 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(trade_quote_volume,24))                                                             | Delta\|Rank                      | True           |    0.998153    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0a1bb022b33cf015 | Z2_liquidity_taker_microstructure_lite | Rank(Mean(trade_count,12))                                                                     | Mean\|Rank                       | True           |    0.998771    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0a75fb1c32beed6e | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_sell_volume_ratio_last,12)),R3_liquidity_cycle_state)     | Delta\|GroupNeutralize\|Rank     | True           |    0.968723    |      0.999924   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0cee318f9177279a | Z2_liquidity_taker_microstructure_lite | Rank(Mean(taker_buy_quote_volume,168))                                                         | Mean\|Rank                       | True           |    0.998248    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_0ee6ab4ec3285d14 | Z2_liquidity_taker_microstructure_lite | Rank(Abs(ZScore(Delta(kline_taker_buy_quote_share,168))))                                      | Abs\|Delta\|Rank\|ZScore         | True           |    0.991209    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_1af0afda743e28ac | Z2_liquidity_taker_microstructure_lite | Sub(Rank(Delta(trade_volume,48)),Rank(Delta(trade_close,24)))                                  | Delta\|Rank\|Sub                 | True           |    0.997011    |      0.988872   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_29d77b76d08d3067 | Z2_liquidity_taker_microstructure_lite | SafeDiv(taker_buy_quote_volume,trade_quote_volume)                                             | SafeDiv                          | True           |    0.999247    |      0.999999   | True          |   0          |   0.973467    |         |
| a7al2z1_9481b2170c90544c | Z2_liquidity_taker_microstructure_lite | Sub(Rank(kline_taker_buy_quote_share),Rank(taker_buy_sell_volume_ratio_last))                  | Rank\|Sub                        | True           |    0.998771    |      0.984563   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_01ee540865d7b89c | Z3_basis_price_trend_reversal          | Sub(Rank(Mean(mark_index_basis_bps,24)),Rank(Delta(trade_close,24)))                           | Delta\|Mean\|Rank\|Sub           | True           |    0.997405    |      0.990317   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_058a56eed1333ef3 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(premium_close_bps,168)),Rank(Delta(trade_close,168)))                           | Delta\|Rank\|Sub                 | True           |    0.990848    |      0.991017   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_0646a16788eadb60 | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(mark_index_basis_bps,48)),R0_market_trend_state)                    | Delta\|GroupNeutralize\|Rank     | True           |    0.967701    |      0.999118   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_07407de3ca8314db | Z3_basis_price_trend_reversal          | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,48))),Neg(Winsor(ZScore(Delta(trade_close,48))))) | Delta\|Mul\|Neg\|Winsor\|ZScore  | True           |    0.996239    |      1          | True          | -19.1712     |  17.4044      |         |
| a7al2z1_0e3e0240604d5ce6 | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(mark_index_basis_bps,12)),R0_market_trend_state)                    | Delta\|GroupNeutralize\|Rank     | True           |    0.96889     |      0.99916    | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_1080aea723374d03 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_index_basis_bps,48)),Rank(Delta(index_close,48)))                          | Delta\|Rank\|Sub                 | True           |    0.996239    |      0.990496   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_10e42708fc0ba025 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_trade_basis_bps,168)),Neg(Rank(Delta(trade_close,168))))                   | Delta\|Mul\|Neg\|Rank            | True           |    0.991304    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_118d9e3951e724ca | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,48)),Neg(Rank(Delta(index_close,48))))                     | Delta\|Mul\|Neg\|Rank            | True           |    0.996239    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_1596b15a56aa40e3 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(premium_close_bps,48)),Neg(Rank(Delta(trade_close,48))))                        | Delta\|Mul\|Neg\|Rank            | True           |    0.996615    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_1d5101fd76f007d7 | Z3_basis_price_trend_reversal          | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Delta(trade_close,48)))                           | Delta\|Mean\|Rank\|Sub           | True           |    0.997011    |      0.989797   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_1d5813e7f30ddb28 | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_index_basis_bps,24)),Rank(Delta(index_close,24)))                          | Delta\|Rank\|Sub                 | True           |    0.997404    |      0.990457   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_1e1f29f96b2684ea | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,168)),Neg(Rank(Delta(trade_close,168))))                   | Delta\|Mul\|Neg\|Rank            | True           |    0.990412    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_2193f2355135ba3d | Z3_basis_price_trend_reversal          | GroupNeutralize(Rank(Delta(premium_close_bps,168)),R0_market_trend_state)                      | Delta\|GroupNeutralize\|Rank     | True           |    0.96231     |      0.997937   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_2332ae0a674eb61e | Z3_basis_price_trend_reversal          | Sub(Rank(Delta(mark_trade_basis_bps,168)),Rank(Delta(trade_close,168)))                        | Delta\|Rank\|Sub                 | True           |    0.991304    |      0.990933   | True          |  -0.989583   |   0.989583    |         |
| a7al2z1_2593267a5a5495c0 | Z3_basis_price_trend_reversal          | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,24))),Neg(Winsor(ZScore(Delta(trade_close,24))))) | Delta\|Mul\|Neg\|Winsor\|ZScore  | True           |    0.997404    |      1          | True          | -25          |  25           |         |
| a7al2z1_25a51da6deb9bdc6 | Z3_basis_price_trend_reversal          | Mul(Rank(Delta(mark_index_basis_bps,24)),Neg(Rank(Delta(index_close,24))))                     | Delta\|Mul\|Neg\|Rank            | True           |    0.997404    |      1          | True          |  -1          |  -0.000108507 |         |
| a7al2z1_00031079a29042a5 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(mark_index_basis_bps,24),R10_stress_proxy_state)                       | Delta\|LatentNeutralRank         | True           |    0.968866    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_000f7a58ee0cecab | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(trade_quote_volume,168)),R10_stress_proxy_state)                     | GroupNeutralize\|Mean\|Rank      | True           |    0.969663    |      0.999924   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_01144b6aeae51153 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R1_market_volatility_state)               | Delta\|GroupNeutralize\|Rank     | True           |    0.966536    |      0.999087   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_013bc4e85cf82308 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(trade_quote_volume,24),R2_market_breadth_state)                        | Delta\|LatentNeutralRank         | True           |    0.969616    |      1          | True          |   0.0104167  |   1           |         |
| a7al2z1_02835f7a0f1e2191 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(funding_rate,24),R1_market_volatility_state)                           | Delta\|LatentNeutralRank         | True           |    0.14806     |      1          | False         |   0.0104167  |   1           |         |
| a7al2z1_02f0aa46165930ef | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,72)),R3_liquidity_cycle_state)                     | GroupNeutralize\|Mean\|Rank      | True           |    0.969302    |      0.999552   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_03adf58750b956c5 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)        | GroupNeutralize\|Mean\|Rank      | True           |    0.968963    |      0.999201   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0417b7031aaf2f21 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(premium_close_bps,72)),R0_market_trend_state)                       | Delta\|GroupNeutralize\|Rank     | True           |    0.966924    |      0.997794   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_08a69b564ec2fd77 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Delta(premium_close_bps,168)),R3_liquidity_cycle_state)                   | Delta\|GroupNeutralize\|Rank     | True           |    0.96231     |      0.997937   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_09d7f79331848fdb | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)        | GroupNeutralize\|Mean\|Rank      | True           |    0.968915    |      0.999152   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_09e2fd4a441553b4 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(mark_index_basis_bps,24)),R0_market_trend_state)                     | GroupNeutralize\|Mean\|Rank      | True           |    0.968868    |      0.999152   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0b6e676dd75c1780 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(premium_close_bps,72)),R0_market_trend_state)                        | GroupNeutralize\|Mean\|Rank      | True           |    0.969256    |      0.999552   | True          |  -0.494792   |   0.494792    |         |
| a7al2z1_0f62f529551c2879 | Z4_upper_regime_relative_value         | LatentNeutralRank(Delta(funding_rate,24),R3_liquidity_cycle_state)                             | Delta\|LatentNeutralRank         | True           |    0.148226    |      1          | False         |   0.0104167  |   1           |         |
| a7al2z1_13af2e476c2f9448 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(funding_rate,168)),R2_market_breadth_state)                          | GroupNeutralize\|Mean\|Rank      | True           |    0.216002    |      0.982339   | True          |  -0.483871   |   0.483871    |         |
| a7al2z1_14c037279916f855 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(funding_rate,24)),R3_liquidity_cycle_state)                          | GroupNeutralize\|Mean\|Rank      | True           |    0           |      0          | False         | nan          | nan           |         |
| a7al2z1_17e5d01f0bfb02a9 | Z4_upper_regime_relative_value         | GroupNeutralize(Rank(Mean(funding_rate,72)),R0_market_trend_state)                             | GroupNeutralize\|Mean\|Rank      | True           |    2.67539e-05 |      0.666667   | False         |  -0.333333   |   0.333333    |         |

## Operator Coverage

| operator          |   selected_candidate_count |
|:------------------|---------------------------:|
| Abs               |                          7 |
| Delta             |                         81 |
| GroupNeutralize   |                         42 |
| LatentNeutralRank |                         14 |
| Mean              |                         48 |
| Mul               |                         25 |
| Neg               |                         12 |
| Rank              |                         95 |
| SafeDiv           |                          2 |
| StateMask         |                          2 |
| Sub               |                         32 |
| Winsor            |                         17 |
| ZScore            |                         24 |

## Group Field Coverage

| group_field                        |   unique_values | values                                                                                               |
|:-----------------------------------|----------------:|:-----------------------------------------------------------------------------------------------------|
| R0_market_trend_state              |               3 | trend_down\|trend_mid\|trend_up                                                                      |
| R10_stress_proxy_state             |               3 | stress_high\|stress_low\|stress_mid                                                                  |
| R1_market_volatility_state         |               3 | vol_high\|vol_low\|vol_mid                                                                           |
| R2_market_breadth_state            |               3 | breadth_mid\|breadth_strong\|breadth_weak                                                            |
| R3_liquidity_cycle_state           |               3 | liq_contracting\|liq_expanding\|liq_mid                                                              |
| R5_basis_premium_dislocation_state |               3 | basis_high\|basis_low\|basis_mid                                                                     |
| R9_alt_vs_major_dispersion_state   |               3 | alt_lag\|alt_lead\|alt_mid                                                                           |
| is_major                           |               2 | False\|True                                                                                          |
| is_multiplier_contract             |               2 | False\|True                                                                                          |
| liquidity_tier                     |               5 | tail\|top100\|top20\|top200\|top50                                                                   |
| meme_contract_group                |               4 | meme_multiplier_contract\|meme_plain_contract\|non_meme_multiplier_contract\|non_meme_plain_contract |

## Blockers

| candidate_id             | blocker                      | detail                           |
|:-------------------------|:-----------------------------|:---------------------------------|
| a7al2z1_0098920a5ffc5a6b | activity_or_coverage_failure | finite=0.147711;nonzero=0.986567 |
| a7al2z1_0744891cb8e08bbf | activity_or_coverage_failure | finite=0.001979;nonzero=0.976971 |
| a7al2z1_0e0300e409dbd037 | activity_or_coverage_failure | finite=0.001979;nonzero=0.991239 |
| a7al2z1_0ec1de18c96369a2 | activity_or_coverage_failure | finite=0.149381;nonzero=0.986173 |
| a7al2z1_0fd66b0116db4b6b | activity_or_coverage_failure | finite=0.146091;nonzero=0.986513 |
| a7al2z1_19b6336bd472bdd9 | activity_or_coverage_failure | finite=0.002287;nonzero=0.984839 |
| a7al2z1_2a30bd2ef1694609 | activity_or_coverage_failure | finite=0.145621;nonzero=1.000000 |
| a7al2z1_084c5de0fd767b63 | activity_or_coverage_failure | finite=0.998248;nonzero=0.001272 |
| a7al2z1_1026fb4689800bcc | activity_or_coverage_failure | finite=0.998248;nonzero=0.001272 |
| a7al2z1_02835f7a0f1e2191 | activity_or_coverage_failure | finite=0.148060;nonzero=1.000000 |
| a7al2z1_0f62f529551c2879 | activity_or_coverage_failure | finite=0.148226;nonzero=1.000000 |
| a7al2z1_14c037279916f855 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z1_17e5d01f0bfb02a9 | activity_or_coverage_failure | finite=0.000027;nonzero=0.666667 |
| a7al2z1_00a0bd50986c3107 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z1_04f3782ccb5d5429 | activity_or_coverage_failure | finite=0.144065;nonzero=0.993524 |
| a7al2z1_0b6cd7ac04e4982f | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z1_0cb60f1c1f07ee16 | activity_or_coverage_failure | finite=0.000000;nonzero=0.000000 |
| a7al2z1_196835a9a86d3cb1 | activity_or_coverage_failure | finite=0.147085;nonzero=1.000000 |
| a7al2z1_1e659e82fd0208b3 | activity_or_coverage_failure | finite=0.054410;nonzero=1.000000 |
| a7al2z1_1f0da4becb02bb62 | activity_or_coverage_failure | finite=0.148434;nonzero=0.999997 |
