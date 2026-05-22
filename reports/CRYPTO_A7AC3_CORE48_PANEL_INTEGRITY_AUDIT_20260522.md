# CRYPTO A7AC-3 Core48 Panel Integrity Audit

Generated: 2026-05-22T14:11:53Z

## Decision

`PASS_A7AC3_CORE48_PANEL_READY_FOR_CONTROLLED_REPLAY_PREP`

This is a data-line panel integrity and listing/survivorship audit. It does not authorize replay, formula search, large search, alpha proof, shadow, paper, or live trading.

## Core48 Candidate Panel

```text
output: G:\AlphaFactory_CryptoData\gold\panels\crypto_core48_1h_with_metrics_candidate_v1.parquet
rows: 984600
symbols: 48
columns: 233
timestamp_min: 2024-01-01 00:00:00+00:00
timestamp_max: 2026-05-22 00:00:00+00:00
common_window: 2024-03-16 12:00:00+00:00 .. 2026-04-30 23:00:00+00:00
common_window_rows: 893376
duplicate_key_count: 0
```

## Listing / Survivorship Policy

- `BOMEUSDT` starts at its available Binance Vision source boundary; 2024-01/02 source 404s remain explicit listing/source gaps.
- Core48 historical replay must use the `core48_common_window_eligible` flag unless a test explicitly supports changing universe membership.
- Rows after 2026-04-30 are not part of the current core48 common monthly-source historical window.

## Symbol Coverage

| symbol        | track                         | tier             |   rows | timestamp_min             | timestamp_max             |   common_window_rows |   common_window_missing_hours |   duplicate_keys |   gap_count | listing_policy                 | ready_for_common_window   |
|:--------------|:------------------------------|:-----------------|-------:|:--------------------------|:--------------------------|---------------------:|------------------------------:|-----------------:|------------:|:-------------------------------|:--------------------------|
| BTCUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ETHUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| SOLUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BNBUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| XRPUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| DOGEUSDT      | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ADAUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| LINKUSDT      | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| AVAXUSDT      | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| LTCUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BCHUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| SUIUSDT       | baseline_core12_existing      | core12_existing  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ALGOUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| CELOUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ACHUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| APEUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ARUSDT        | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ATOMUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| CHZUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| DASHUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| GMXUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| LRCUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| MAGICUSDT     | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| MASKUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| NEARUSDT      | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| SEIUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| UNIUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| YFIUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ZECUSDT       | primary_core48_top36_addition | core48_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BLURUSDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BOMEUSDT      | primary_core48_top36_addition | midcap_candidate |  18612 | 2024-03-16 12:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | starts_at_listing_gap_boundary | True                      |
| ETCUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| HBARUSDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| KNCUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| MANAUSDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| PENDLEUSDT    | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| WLDUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| 1000BONKUSDT  | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| 1000FLOKIUSDT | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| 1INCHUSDT     | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| AAVEUSDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ACEUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| API3USDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| APTUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| ARBUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| AXSUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BANDUSDT      | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |
| BATUSDT       | primary_core48_top36_addition | midcap_candidate |  20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                18612 |                             0 |                0 |           0 | continuous_from_2024_01        | True                      |

## Symbols Not Ready For Common Window

`<empty>`

## Schema Mismatches

| field                                 | in_core12   | in_primary_additions   | core12_dtype   | primary_dtype   |
|:--------------------------------------|:------------|:-----------------------|:---------------|:----------------|
| agg_avg_agg_trade_notional            | True        | False                  | float64        |                 |
| agg_avg_trade_notional_24h            | True        | False                  | float64        |                 |
| agg_avg_trade_notional_4h             | True        | False                  | float64        |                 |
| agg_avg_underlying_trade_notional     | True        | False                  | float64        |                 |
| agg_avg_underlying_trades_per_agg     | True        | False                  | float64        |                 |
| agg_btcusdt_flow_imbalance_4h         | True        | False                  | float64        |                 |
| agg_buy_agg_trade_count               | True        | False                  | float64        |                 |
| agg_buy_notional                      | True        | False                  | float64        |                 |
| agg_buy_notional_share                | True        | False                  | float64        |                 |
| agg_buy_quantity                      | True        | False                  | float64        |                 |
| agg_buy_sell_notional_ratio           | True        | False                  | float64        |                 |
| agg_buy_sell_vwap_spread_bps          | True        | False                  | float64        |                 |
| agg_buy_underlying_trade_count        | True        | False                  | float64        |                 |
| agg_buy_vwap                          | True        | False                  | float64        |                 |
| agg_close_price                       | True        | False                  | float64        |                 |
| agg_close_to_open_bps                 | True        | False                  | float64        |                 |
| agg_close_to_open_bps_sum_24h         | True        | False                  | float64        |                 |
| agg_close_to_open_bps_sum_4h          | True        | False                  | float64        |                 |
| agg_cross_symbol_large_notional_share | True        | False                  | float64        |                 |
| agg_cross_symbol_notional_share       | True        | False                  | float64        |                 |
| agg_cross_symbol_signed_flow_share    | True        | False                  | float64        |                 |
| agg_ethusdt_flow_imbalance_4h         | True        | False                  | float64        |                 |
| agg_feature_schema                    | True        | False                  | object         |                 |
| agg_features_available                | True        | False                  | bool           |                 |
| agg_first_agg_trade_id                | True        | False                  | float64        |                 |
| agg_first_transact_time_ms            | True        | False                  | float64        |                 |
| agg_flow_accel_4h_vs_24h              | True        | False                  | float64        |                 |
| agg_flow_imbalance_notional           | True        | False                  | float64        |                 |
| agg_flow_imbalance_notional_24h       | True        | False                  | float64        |                 |
| agg_flow_imbalance_notional_4h        | True        | False                  | float64        |                 |
| agg_flow_imbalance_qty                | True        | False                  | float64        |                 |
| agg_flow_minus_btcusdt_4h             | True        | False                  | float64        |                 |
| agg_flow_minus_ethusdt_4h             | True        | False                  | float64        |                 |
| agg_high_price                        | True        | False                  | float64        |                 |
| agg_large_count_share_100k_plus       | True        | False                  | float64        |                 |
| agg_large_notional_100k_plus          | True        | False                  | float64        |                 |
| agg_large_notional_ratio_100k_plus    | True        | False                  | float64        |                 |
| agg_large_notional_share_100k_plus    | True        | False                  | float64        |                 |
| agg_large_notional_share_24h          | True        | False                  | float64        |                 |
| agg_large_notional_share_4h           | True        | False                  | float64        |                 |
| agg_large_notional_sum_24h            | True        | False                  | float64        |                 |
| agg_large_notional_sum_4h             | True        | False                  | float64        |                 |
| agg_large_trade_count_100k_plus       | True        | False                  | float64        |                 |
| agg_large_trade_count_ratio_100k_plus | True        | False                  | float64        |                 |
| agg_last_agg_trade_id                 | True        | False                  | float64        |                 |
| agg_last_transact_time_ms             | True        | False                  | float64        |                 |
| agg_low_price                         | True        | False                  | float64        |                 |
| agg_max_trade_notional                | True        | False                  | float64        |                 |
| agg_notional                          | True        | False                  | float64        |                 |
| agg_notional_100_1k                   | True        | False                  | float64        |                 |
| agg_notional_100k_1m                  | True        | False                  | float64        |                 |
| agg_notional_10k_100k                 | True        | False                  | float64        |                 |
| agg_notional_1k_10k                   | True        | False                  | float64        |                 |
| agg_notional_accel_4h_vs_24h          | True        | False                  | float64        |                 |
| agg_notional_gt_1m                    | True        | False                  | float64        |                 |
| agg_notional_le_100                   | True        | False                  | float64        |                 |
| agg_notional_shock_24h_mad            | True        | False                  | float64        |                 |
| agg_notional_sum_24h                  | True        | False                  | float64        |                 |
| agg_notional_sum_4h                   | True        | False                  | float64        |                 |
| agg_open_price                        | True        | False                  | float64        |                 |
| agg_price_range_bps                   | True        | False                  | float64        |                 |
| agg_price_range_bps_max_24h           | True        | False                  | float64        |                 |
| agg_price_range_bps_max_4h            | True        | False                  | float64        |                 |
| agg_price_std                         | True        | False                  | float64        |                 |
| agg_quantity                          | True        | False                  | float64        |                 |
| agg_quantity_sum_24h                  | True        | False                  | float64        |                 |
| agg_quantity_sum_4h                   | True        | False                  | float64        |                 |
| agg_sell_agg_trade_count              | True        | False                  | float64        |                 |
| agg_sell_notional                     | True        | False                  | float64        |                 |
| agg_sell_notional_share               | True        | False                  | float64        |                 |
| agg_sell_quantity                     | True        | False                  | float64        |                 |
| agg_sell_underlying_trade_count       | True        | False                  | float64        |                 |
| agg_sell_vwap                         | True        | False                  | float64        |                 |
| agg_signed_aggressor_notional         | True        | False                  | float64        |                 |
| agg_signed_aggressor_quantity         | True        | False                  | float64        |                 |
| agg_signed_flow_z_24h                 | True        | False                  | float64        |                 |
| agg_signed_notional_sum_24h           | True        | False                  | float64        |                 |
| agg_signed_notional_sum_4h            | True        | False                  | float64        |                 |
| agg_signed_quantity_sum_24h           | True        | False                  | float64        |                 |
| agg_signed_quantity_sum_4h            | True        | False                  | float64        |                 |

## Lowest Field Coverage In Common Window

| field                                 | dtype   |   non_null_rate_all |   non_null_rate_common_window |   core12_non_null_rate |   primary_addition_non_null_rate |
|:--------------------------------------|:--------|--------------------:|------------------------------:|-----------------------:|---------------------------------:|
| agg_avg_agg_trade_notional            | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_avg_trade_notional_24h            | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_avg_trade_notional_4h             | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_avg_underlying_trade_notional     | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_avg_underlying_trades_per_agg     | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_btcusdt_flow_imbalance_4h         | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_buy_agg_trade_count               | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_notional                      | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_notional_share                | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_quantity                      | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_sell_notional_ratio           | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_sell_vwap_spread_bps          | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_underlying_trade_count        | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_buy_vwap                          | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_close_price                       | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_close_to_open_bps                 | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_close_to_open_bps_sum_24h         | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_close_to_open_bps_sum_4h          | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_cross_symbol_large_notional_share | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_cross_symbol_notional_share       | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_cross_symbol_signed_flow_share    | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_ethusdt_flow_imbalance_4h         | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_first_agg_trade_id                | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_first_transact_time_ms            | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_flow_accel_4h_vs_24h              | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_flow_imbalance_notional           | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_flow_imbalance_notional_24h       | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_flow_imbalance_notional_4h        | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_flow_imbalance_qty                | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_flow_minus_btcusdt_4h             | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_flow_minus_ethusdt_4h             | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_high_price                        | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_large_count_share_100k_plus       | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_large_notional_100k_plus          | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_large_notional_ratio_100k_plus    | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_large_notional_share_100k_plus    | float64 |           0.0636929 |                        0.0625 |               0.249701 |                                0 |
| agg_large_notional_share_24h          | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_large_notional_share_4h           | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |
| agg_large_notional_sum_24h            | float64 |           0.0636594 |                        0.0625 |               0.24957  |                                0 |
| agg_large_notional_sum_4h             | float64 |           0.0636898 |                        0.0625 |               0.249689 |                                0 |

## Authorization

```text
authorizes_controlled_replay_prep: true
authorizes_formula_search: false
authorizes_large_search: false
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false
```

## Next

1. Define A7AD controlled replay prep using `core48_common_window_eligible` and explicit feature-family availability masks.
2. Do not treat aggTrades fields as available for all 48 symbols; they remain core3/core12 specific depending on source coverage.
3. Do not use tail rows outside the common window for fixed-split historical proof.
