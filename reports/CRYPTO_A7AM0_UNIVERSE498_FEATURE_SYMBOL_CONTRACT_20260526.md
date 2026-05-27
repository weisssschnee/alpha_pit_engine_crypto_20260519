# CRYPTO A7AM-0 Universe498 Feature And Symbol Contract

Generated: 2026-05-27T03:47:59Z

## Decision

```text
PASS_A7AL_UNIVERSE498_REPLAY_BASE_ACCEPTED
```

This contract separates feature families and symbol classes for the next controlled smoke. It does not authorize large search.

## Feature Families

| source_class        |   fields |
|:--------------------|---------:|
| derived_replay_base |        3 |
| funding             |        2 |
| key                 |        2 |
| mark_index_premium  |       17 |
| metadata_timing     |        7 |
| metrics_positioning |       13 |
| trade_ohlcv         |       10 |

## Symbol Classes

| search_eligibility            | liquidity_tier   |   symbols |
|:------------------------------|:-----------------|----------:|
| hold_quality_or_short_history | tail             |        10 |
| hold_quality_or_short_history | top20            |         1 |
| hold_quality_or_short_history | top200           |         1 |
| listing_aware                 | tail             |       209 |
| listing_aware                 | top100           |        25 |
| listing_aware                 | top20            |         5 |
| listing_aware                 | top200           |        56 |
| listing_aware                 | top50            |        10 |
| strict_full_history           | tail             |        79 |
| strict_full_history           | top100           |        25 |
| strict_full_history           | top20            |        14 |
| strict_full_history           | top200           |        43 |
| strict_full_history           | top50            |        20 |

## Authorized Next Step

```text
AUTHORIZED:
  A7AK-min small controlled field-family smoke

NOT AUTHORIZED:
  large formula search
  alpha proof
  shadow / paper / live

UNIVERSE:
  primary = strict_full_history subset
  secondary = listing_aware diagnostic only
  May unavailable in this panel

FEATURE FAMILY BLOCKS:
  trade_ohlcv
  mark_index_premium
  funding
  metrics_positioning
  derived_replay_base
```

## Feature Contract Sample

| field_name                           | source_class        | independent_source   | source_detail                        | feature_available_rule                                                                                |
|:-------------------------------------|:--------------------|:---------------------|:-------------------------------------|:------------------------------------------------------------------------------------------------------|
| symbol                               | key                 | False                | identity                             | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| timestamp                            | key                 | False                | identity                             | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_open                           | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_high                           | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_low                            | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_close                          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_volume                         | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_quote_volume                   | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_count                          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| taker_buy_volume                     | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| taker_buy_quote_volume               | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| metrics_n_5m                         | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| open_interest_last                   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| open_interest_mean                   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| open_interest_value_last             | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| open_interest_value_mean             | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| top_long_short_account_ratio_last    | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| top_long_short_account_ratio_mean    | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| top_long_short_position_ratio_last   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| top_long_short_position_ratio_mean   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| global_long_short_account_ratio_last | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| global_long_short_account_ratio_mean | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| taker_buy_sell_volume_ratio_last     | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| taker_buy_sell_volume_ratio_mean     | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| funding_interval_hours               | funding             | True                 | Binance funding event observed in 1h | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| funding_rate                         | funding             | True                 | Binance funding event observed in 1h | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_open                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_high                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_low                             | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_close                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_count                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| index_open                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| index_high                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| index_low                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| index_close                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| index_count                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_open                         | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_high                         | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_low                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_close                        | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_count                        | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| source_trade_klines                  | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| source_metrics                       | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| source_market_funding                | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| feature_available_time               | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| execution_time                       | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| is_historical_backfill               | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| is_forward_only                      | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| trade_return_1h                      | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| forward_trade_return_1h              | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_index_basis_bps                 | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| mark_trade_basis_bps                 | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| premium_close_bps                    | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| kline_taker_buy_quote_share          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
