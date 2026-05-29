# CRYPTO A7AL-2X4M MATERIALIZATION AND EVALUATOR AUDIT

## Decision

`PASS_A7AL2X4M_READY_FOR_NUMERIC_REPLAY_PREFLIGHT_IMPLEMENTATION`

This audit does not execute numeric replay, search, training, or proof. It checks whether A7AL-2X3 selected candidates can be materialized and interpreted by a replay evaluator.

## Summary

- selected candidates: 176
- resolved selected fields: 13 / 13
- invalid StateMask labels: 0
- blocking operators: 0

## Field Materialization

| field_name                           | status   | source                             | source_path                                                                                            | materialized_field                   | join_key         | caveat                                                                                                |
|:-------------------------------------|:---------|:-----------------------------------|:-------------------------------------------------------------------------------------------------------|:-------------------------------------|:-----------------|:------------------------------------------------------------------------------------------------------|
| R2_market_breadth_state              | resolved | a7al0g_upper_regime_panel_v1       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet    | R2_market_breadth_state              | timestamp        | upper regime was built from v1 panel; requires timestamp alignment audit before numeric replay        |
| R3_liquidity_cycle_state             | resolved | a7al0g_upper_regime_panel_v1       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet    | R3_liquidity_cycle_state             | timestamp        | upper regime was built from v1 panel; requires timestamp alignment audit before numeric replay        |
| R4_leverage_crowding_state           | resolved | a7al0g_upper_regime_panel_v1       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet    | R4_leverage_crowding_state           | timestamp        | upper regime was built from v1 panel; requires timestamp alignment audit before numeric replay        |
| R5_basis_premium_dislocation_state   | resolved | a7al0g_upper_regime_panel_v1       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet    | R5_basis_premium_dislocation_state   | timestamp        | upper regime was built from v1 panel; requires timestamp alignment audit before numeric replay        |
| funding_rate_abs_168h                | resolved | a7ak_lv1_latent_state_panel_v1     | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet | funding_rate_abs_168h                | symbol,timestamp | latent panel was built from v1 panel; requires symbol/timestamp alignment audit before numeric replay |
| global_long_short_account_ratio_last | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | global_long_short_account_ratio_last | symbol,timestamp |                                                                                                       |
| index_close                          | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | index_close                          | symbol,timestamp |                                                                                                       |
| is_major                             | resolved | a7ak_lv1_latent_state_panel_v1     | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet | is_major                             | symbol,timestamp | latent panel was built from v1 panel; requires symbol/timestamp alignment audit before numeric replay |
| kline_taker_buy_quote_share          | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | kline_taker_buy_quote_share          | symbol,timestamp |                                                                                                       |
| liquidity_tier                       | resolved | a7ak_static_contract_meme_taxonomy | G:\AlphaFactory_CryptoData\gold\metadata\binance_universe498_contract_meme_taxonomy_v1_20260527.csv    | liquidity_tier                       | symbol           |                                                                                                       |
| mark_index_basis_bps                 | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | mark_index_basis_bps                 | symbol,timestamp |                                                                                                       |
| open_interest_last                   | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | open_interest_last                   | symbol,timestamp |                                                                                                       |
| top_long_short_account_ratio_last    | resolved | base_replay_panel_v2               | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                     | top_long_short_account_ratio_last    | symbol,timestamp |                                                                                                       |

## StateMask Label Audit

| candidate_id             | objective_family               | expression                                                                | state_field    | materialized_field   | requested_label   | actual_values                      | label_valid   |
|:-------------------------|:-------------------------------|:--------------------------------------------------------------------------|:---------------|:---------------------|:------------------|:-----------------------------------|:--------------|
| a7al2x3_6425856b9df4b997 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,168)),StateMask(is_major,True))         | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_f726e8031e11a5c6 | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,168)),StateMask(is_major,False))        | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_67d3a9b6da05c211 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,168)),StateMask(liquidity_tier,top100)) | liquidity_tier | liquidity_tier       | top100            | tail\|top100\|top20\|top200\|top50 | True          |
| a7al2x3_3cb1db3cafe85fa0 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,24)),StateMask(is_major,True))          | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_0e3c1c804bf9bd55 | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,24)),StateMask(is_major,False))         | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_aaa82dfd8a7c3555 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,336)),StateMask(is_major,True))         | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_1de261dd444f4839 | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,336)),StateMask(is_major,False))        | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_c73e0ebc3866e01e | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,48)),StateMask(is_major,True))          | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_8ad54ecbc6252391 | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,48)),StateMask(is_major,False))         | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_42246afae2fc6cd4 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,72)),StateMask(is_major,True))          | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_8b719d26496ba50d | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,72)),StateMask(is_major,False))         | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_153675f49d4aaa01 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,96)),StateMask(is_major,True))          | is_major       | is_major             | True              | False\|True                        | True          |
| a7al2x3_f6b31033394d4417 | F6_OI_latent_state_interaction | Mul(Sign(Delta(open_interest_last,96)),StateMask(is_major,False))         | is_major       | is_major             | False             | False\|True                        | True          |
| a7al2x3_4b818a882dd9f93a | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,24)),StateMask(liquidity_tier,top100))  | liquidity_tier | liquidity_tier       | top100            | tail\|top100\|top20\|top200\|top50 | True          |
| a7al2x3_58e9d974d2ff93d9 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,336)),StateMask(liquidity_tier,top200)) | liquidity_tier | liquidity_tier       | top200            | tail\|top100\|top20\|top200\|top50 | True          |
| a7al2x3_1d7d8741b269a7ec | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,48)),StateMask(liquidity_tier,tail))    | liquidity_tier | liquidity_tier       | tail              | tail\|top100\|top20\|top200\|top50 | True          |
| a7al2x3_37973669b65c3689 | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,72)),StateMask(liquidity_tier,top100))  | liquidity_tier | liquidity_tier       | top100            | tail\|top100\|top20\|top200\|top50 | True          |
| a7al2x3_23a7d0c66386da1b | F6_OI_latent_state_interaction | Mul(Rank(Delta(open_interest_last,96)),StateMask(liquidity_tier,top20))   | liquidity_tier | liquidity_tier       | top20             | tail\|top100\|top20\|top200\|top50 | True          |

## Operator Semantics

| operator        | status                                   | semantics                                                                                       | is_blocker   |
|:----------------|:-----------------------------------------|:------------------------------------------------------------------------------------------------|:-------------|
| Abs             | already_supported                        | existing fast replay operator                                                                   | False        |
| Add             | already_supported                        | existing fast replay operator                                                                   | False        |
| Clip            | local_extension_contract_ready           | fixed symmetric clipping after scalar transform; proposed default [-5,5], no May fit            | False        |
| Delta           | already_supported                        | existing fast replay operator                                                                   | False        |
| GroupNeutralize | requires_state_aware_evaluator_extension | demean or zscore within timestamp and materialized group field; needs min-group fallback policy | False        |
| Mean            | already_supported                        | existing fast replay operator                                                                   | False        |
| Mul             | already_supported                        | existing fast replay operator                                                                   | False        |
| Neg             | already_supported                        | existing fast replay operator                                                                   | False        |
| Rank            | already_supported                        | existing fast replay operator                                                                   | False        |
| Sign            | already_supported                        | existing fast replay operator                                                                   | False        |
| StateMask       | requires_state_aware_evaluator_extension | indicator for materialized state field equals requested label                                   | False        |
| Sub             | already_supported                        | existing fast replay operator                                                                   | False        |
| Winsor          | local_extension_contract_ready           | fixed symmetric winsorization after scalar transform; proposed default [-5,5], no May fit       | False        |
| ZScore          | already_supported                        | existing fast replay operator                                                                   | False        |

## Blockers

No blockers.

## Authorization

- numeric replay: not authorized
- A7AL-2Y generation: not authorized
- large search: not authorized
- alpha proof / shadow / paper / live: not authorized
