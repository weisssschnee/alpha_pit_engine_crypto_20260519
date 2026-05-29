# CRYPTO A7AL-2Z1 BROADER NON-OI DRY GENERATION

Generated: 2026-05-29T03:33:29Z

## Decision

`PASS_A7AL2Z1_BROADER_NON_OI_DRY_GENERATION_READY_FOR_MATERIALIZATION_AUDIT`

Z1 is static dry generation only. It does not run replay, train a model, or authorize alpha proof.

## Manifest

```json
{
  "authorizes_a7al2z2_materialization_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "blocker_count": 0,
  "decision": "PASS_A7AL2Z1_BROADER_NON_OI_DRY_GENERATION_READY_FOR_MATERIALIZATION_AUDIT",
  "executes_numeric_replay": false,
  "executes_static_generation": true,
  "executes_training": false,
  "family_count": 8,
  "generated_at": "2026-05-29T03:33:29Z",
  "generated_total": 1272,
  "selected_for_z2_count": 128,
  "selected_top_family_share": 0.125,
  "stage": "A7AL-2Z1",
  "static_valid_count": 1272,
  "unique_expr_ratio": 0.9622641509433962,
  "uses_may": false,
  "uses_oi_or_positioning_core": false
}
```

## Family Quota Audit

| objective_family                         |   generated_count |   static_valid_count |   selected_for_z2_count |   unique_skeleton_count |   unique_production_count | family_id                                |   minimum_generated |   minimum_selected_for_preflight | quota_pass   |
|:-----------------------------------------|------------------:|---------------------:|------------------------:|------------------------:|--------------------------:|:-----------------------------------------|--------------------:|---------------------------------:|:-------------|
| Z0_funding_basis_premium_dislocation     |               126 |                  126 |                      16 |                       7 |                       126 | Z0_funding_basis_premium_dislocation     |                  96 |                               12 | True         |
| Z1_price_range_volatility_structure      |               182 |                  182 |                      16 |                      11 |                       128 | Z1_price_range_volatility_structure      |                 128 |                               16 | True         |
| Z2_liquidity_taker_microstructure_lite   |               182 |                  182 |                      16 |                       8 |                       182 | Z2_liquidity_taker_microstructure_lite   |                 128 |                               16 | True         |
| Z3_basis_price_trend_reversal            |               108 |                  108 |                      16 |                       5 |                       108 | Z3_basis_price_trend_reversal            |                  96 |                               12 | True         |
| Z4_upper_regime_relative_value           |               216 |                  216 |                      16 |                       3 |                       216 | Z4_upper_regime_relative_value           |                 128 |                               16 | True         |
| Z5_latent_listing_meme_neutral_structure |               182 |                  182 |                      16 |                       5 |                       181 | Z5_latent_listing_meme_neutral_structure |                 128 |                               16 | True         |
| Z6_cross_sectional_relative_flow_value   |                96 |                   96 |                      16 |                       4 |                        96 | Z6_cross_sectional_relative_flow_value   |                  96 |                               12 | True         |
| Z7_market_regime_price_breadth           |               180 |                  180 |                      16 |                       3 |                       180 | Z7_market_regime_price_breadth           |                 128 |                               16 | True         |

## Selected Preview

| candidate_id             | objective_family                       | expression                                                                                    | field_families         | operator_signature               | skeleton_key              |
|:-------------------------|:---------------------------------------|:----------------------------------------------------------------------------------------------|:-----------------------|:---------------------------------|:--------------------------|
| a7al2z1_0025716230424fb7 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(mark_trade_basis_bps,48))))                                              | basis_premium          | Abs\|Mean\|Rank\|ZScore          | skeleton-6ebd7d4c1e06c9bc |
| a7al2z1_0098920a5ffc5a6b | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(mark_index_basis_bps,168)),Rank(Delta(funding_rate,168)))                      | basis_premium\|funding | Delta\|Rank\|Sub                 | skeleton-8ad46b9059e6381f |
| a7al2z1_0313bc007ac9963d | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,12))))                                                 | basis_premium          | Abs\|Mean\|Rank\|ZScore          | skeleton-6ebd7d4c1e06c9bc |
| a7al2z1_069b0f75654dadde | Z0_funding_basis_premium_dislocation   | Mul(Winsor(ZScore(Mean(premium_close_bps,168))),Winsor(ZScore(Mean(funding_rate,168))))       | basis_premium\|funding | Mean\|Mul\|Winsor\|ZScore        | skeleton-f59f8b03ae1fd3c4 |
| a7al2z1_0744891cb8e08bbf | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,48)),Rank(Mean(funding_rate,48)))                          | basis_premium\|funding | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_094c52bafda2cb02 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,72)),R5_basis_premium_dislocation_state)      | basis_premium\|state   | Delta\|GroupNeutralize\|Rank     | skeleton-93ce4b9755fbcc1f |
| a7al2z1_0a1368b901e4b360 | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_index_basis_bps,24)),R5_basis_premium_dislocation_state)      | basis_premium\|state   | Delta\|GroupNeutralize\|Rank     | skeleton-93ce4b9755fbcc1f |
| a7al2z1_0e0300e409dbd037 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_index_basis_bps,48)),Rank(Mean(funding_rate,48)))                          | basis_premium\|funding | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_0ec1de18c96369a2 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(premium_close_bps,24)),Rank(Delta(funding_rate,24)))                           | basis_premium\|funding | Delta\|Rank\|Sub                 | skeleton-8ad46b9059e6381f |
| a7al2z1_0fd66b0116db4b6b | Z0_funding_basis_premium_dislocation   | Sub(Rank(Delta(mark_index_basis_bps,336)),Rank(Delta(funding_rate,336)))                      | basis_premium\|funding | Delta\|Rank\|Sub                 | skeleton-8ad46b9059e6381f |
| a7al2z1_18a6b78a193210db | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,168)),Rank(Mean(funding_rate,168)))                        | basis_premium\|funding | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_19b6336bd472bdd9 | Z0_funding_basis_premium_dislocation   | Sub(Rank(Mean(mark_trade_basis_bps,72)),Rank(Mean(funding_rate,72)))                          | basis_premium\|funding | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_1fa487e13f578276 | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Delta(premium_close_bps,168))))                                               | basis_premium          | Abs\|Delta\|Rank\|ZScore         | skeleton-8a6cec079a5f7997 |
| a7al2z1_23cc7365fa741d7c | Z0_funding_basis_premium_dislocation   | Rank(Abs(ZScore(Mean(premium_close_bps,72))))                                                 | basis_premium          | Abs\|Mean\|Rank\|ZScore          | skeleton-6ebd7d4c1e06c9bc |
| a7al2z1_2785f094943ec26b | Z0_funding_basis_premium_dislocation   | GroupNeutralize(Rank(Delta(mark_trade_basis_bps,72)),R5_basis_premium_dislocation_state)      | basis_premium\|state   | Delta\|GroupNeutralize\|Rank     | skeleton-93ce4b9755fbcc1f |
| a7al2z1_2a30bd2ef1694609 | Z0_funding_basis_premium_dislocation   | Mul(Winsor(ZScore(Delta(mark_index_basis_bps,336))),Winsor(ZScore(Delta(funding_rate,336))))  | basis_premium\|funding | Delta\|Mul\|Winsor\|ZScore       | skeleton-0f95d494e3163e7b |
| a7al2z1_0137caa89f7a1268 | Z1_price_range_volatility_structure    | SafeDiv(Mean(Sub(trade_high,trade_low),72),Mean(trade_close,72))                              | price\|range           | Mean\|SafeDiv\|Sub               | skeleton-42a2a88aea7a43d9 |
| a7al2z1_028db6316a60db86 | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(mark_close,72))))                                                       | price                  | Abs\|Delta\|Rank\|ZScore         | skeleton-8a6cec079a5f7997 |
| a7al2z1_066701faa05eebbc | Z1_price_range_volatility_structure    | Mul(Winsor(ZScore(Delta(trade_close,72))),Neg(Winsor(ZScore(Delta(mark_close,72)))))          | price                  | Delta\|Mul\|Neg\|Winsor\|ZScore  | skeleton-2f7931a1701c8dd4 |
| a7al2z1_07116c7a8a24208e | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,24)),Rank(Delta(trade_close,24)))                                   | price                  | Delta\|Rank\|Sub                 | skeleton-8ad46b9059e6381f |
| a7al2z1_084c5de0fd767b63 | Z1_price_range_volatility_structure    | Sub(Rank(Mean(mark_close,72)),Rank(Mean(trade_close,72)))                                     | price                  | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_086296df472ad4ae | Z1_price_range_volatility_structure    | Neg(Rank(Delta(index_close,168)))                                                             | price                  | Delta\|Neg\|Rank                 | skeleton-0e746cb1116b151b |
| a7al2z1_09ec291c3c80efca | Z1_price_range_volatility_structure    | Sub(Rank(Mean(trade_close,72)),Rank(Mean(index_close,72)))                                    | price                  | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_0b6494a3a4ef9490 | Z1_price_range_volatility_structure    | GroupNeutralize(Rank(Mean(Sub(trade_high,trade_low),24)),R1_market_volatility_state)          | range\|state           | GroupNeutralize\|Mean\|Rank\|Sub | skeleton-6a0cf455a6085492 |
| a7al2z1_0e268536d1126a2d | Z1_price_range_volatility_structure    | Sub(Rank(Mean(index_close,12)),Rank(Mean(trade_close,12)))                                    | price                  | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_0f752369161ae869 | Z1_price_range_volatility_structure    | Sub(Rank(Delta(mark_close,336)),Rank(Delta(index_close,336)))                                 | price                  | Delta\|Rank\|Sub                 | skeleton-8ad46b9059e6381f |
| a7al2z1_1026fb4689800bcc | Z1_price_range_volatility_structure    | Sub(Rank(Mean(trade_close,72)),Rank(Mean(mark_close,72)))                                     | price                  | Mean\|Rank\|Sub                  | skeleton-612ffe194eccb811 |
| a7al2z1_10d47299f1a5d1ee | Z1_price_range_volatility_structure    | Rank(Abs(ZScore(Delta(index_close,24))))                                                      | price                  | Abs\|Delta\|Rank\|ZScore         | skeleton-8a6cec079a5f7997 |
| a7al2z1_18a394084ddac9b5 | Z1_price_range_volatility_structure    | Mul(Rank(Mean(Sub(mark_high,mark_low),24)),Neg(Rank(Delta(trade_close,24))))                  | price\|range           | Delta\|Mean\|Mul\|Neg\|Rank\|Sub | skeleton-237f4484d8782cda |
| a7al2z1_1919cb4f0227005e | Z1_price_range_volatility_structure    | Rank(Delta(mark_close,72))                                                                    | price                  | Delta\|Rank                      | skeleton-377d45dadd905908 |
| a7al2z1_2d6e3bd57d32e9b1 | Z1_price_range_volatility_structure    | Rank(Delta(Sub(trade_high,trade_low),24))                                                     | range                  | Delta\|Rank\|Sub                 | skeleton-a00bec3381f16e2c |
| a7al2z1_48338dedf315f7a2 | Z1_price_range_volatility_structure    | Rank(Mean(Sub(mark_high,mark_low),72))                                                        | range                  | Mean\|Rank\|Sub                  | skeleton-6f8455dd7afde698 |
| a7al2z1_0115d3dbe93c2618 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_sell_volume_ratio_last,24)),R3_liquidity_cycle_state)    | state\|taker_flow      | Delta\|GroupNeutralize\|Rank     | skeleton-93ce4b9755fbcc1f |
| a7al2z1_031574ff37957433 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,168))                                                  | taker_flow             | Delta\|Rank                      | skeleton-377d45dadd905908 |
| a7al2z1_03845c7516491252 | Z2_liquidity_taker_microstructure_lite | GroupNeutralize(Rank(Delta(taker_buy_quote_volume,24)),R3_liquidity_cycle_state)              | state\|taker_flow      | Delta\|GroupNeutralize\|Rank     | skeleton-93ce4b9755fbcc1f |
| a7al2z1_04308808db9785c7 | Z2_liquidity_taker_microstructure_lite | Rank(Delta(kline_taker_buy_quote_share,12))                                                   | taker_flow             | Delta\|Rank                      | skeleton-377d45dadd905908 |
| a7al2z1_05bbcd80f3bb1f84 | Z2_liquidity_taker_microstructure_lite | Rank(Mean(taker_buy_sell_volume_ratio_last,6))                                                | taker_flow             | Mean\|Rank                       | skeleton-361a8342adc82420 |
| a7al2z1_06158e66c283198d | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,12))),Neg(Winsor(ZScore(Delta(trade_close,12)))))  | liquidity\|price       | Delta\|Mul\|Neg\|Winsor\|ZScore  | skeleton-2f7931a1701c8dd4 |
| a7al2z1_06179c2b2c6fa22c | Z2_liquidity_taker_microstructure_lite | Rank(Delta(taker_buy_sell_volume_ratio_last,12))                                              | taker_flow             | Delta\|Rank                      | skeleton-377d45dadd905908 |
| a7al2z1_0713ad23e3e4f1a1 | Z2_liquidity_taker_microstructure_lite | Mul(Winsor(ZScore(Delta(trade_quote_volume,168))),Neg(Winsor(ZScore(Delta(trade_close,24))))) | liquidity\|price       | Delta\|Mul\|Neg\|Winsor\|ZScore  | skeleton-2f7931a1701c8dd4 |

## Blockers

No blockers.
