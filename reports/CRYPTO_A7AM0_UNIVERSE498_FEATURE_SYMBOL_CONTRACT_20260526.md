# CRYPTO A7AM-0 Universe498 Feature And Symbol Contract

Generated: 2026-05-26T14:22:37Z

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

| field_name                           | source_class        | independent_source   | source_detail                        | feature_available_rule                                                 |
|:-------------------------------------|:--------------------|:---------------------|:-------------------------------------|:-----------------------------------------------------------------------|
| symbol                               | key                 | False                | identity                             | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| timestamp                            | key                 | False                | identity                             | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_open                           | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_high                           | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_low                            | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_close                          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_volume                         | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_quote_volume                   | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_count                          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| taker_buy_volume                     | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| taker_buy_quote_volume               | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| metrics_n_5m                         | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| open_interest_last                   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| open_interest_mean                   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| open_interest_value_last             | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| open_interest_value_mean             | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| top_long_short_account_ratio_last    | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| top_long_short_account_ratio_mean    | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| top_long_short_position_ratio_last   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| top_long_short_position_ratio_mean   | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| global_long_short_account_ratio_last | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| global_long_short_account_ratio_mean | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| taker_buy_sell_volume_ratio_last     | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| taker_buy_sell_volume_ratio_mean     | metrics_positioning | True                 | Binance metrics 5m aggregated to 1h  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| funding_interval_hours               | funding             | True                 | Binance funding event observed in 1h | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| funding_rate                         | funding             | True                 | Binance funding event observed in 1h | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_open                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_high                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_low                             | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_close                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_count                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| index_open                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| index_high                           | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| index_low                            | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| index_close                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| index_count                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_open                         | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_high                         | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_low                          | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_close                        | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_count                        | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| source_trade_klines                  | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| source_metrics                       | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| source_market_funding                | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| feature_available_time               | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| execution_time                       | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| is_historical_backfill               | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| is_forward_only                      | metadata_timing     | False                | pipeline metadata                    | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| trade_return_1h                      | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| forward_trade_return_1h              | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_index_basis_bps                 | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| mark_trade_basis_bps                 | mark_index_premium  | True                 | Binance mark/index/premium 1h        | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| premium_close_bps                    | derived_replay_base | False                | derived from accepted source fields  | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
| kline_taker_buy_quote_share          | trade_ohlcv         | True                 | Binance futures trade kline 1h       | timestamp + 1h; use timestamp + 2h for conservative one-bar-lag stress |
