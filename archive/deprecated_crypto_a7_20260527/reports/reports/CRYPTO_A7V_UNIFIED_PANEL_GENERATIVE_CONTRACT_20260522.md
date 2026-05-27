# Crypto A7V Unified AggTrades Panel Acceptance and Generative Feature Contract

- generated_at: `2026-05-22T01:03:36Z`
- panel: `G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet`
- decision: `PASS_A7V_UNIFIED_PANEL_ACCEPTED_FOR_CONTROLLED_FEATURE_EXPERIMENTS`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Build Report Summary

```json
{
  "agg_feature_columns_reported_numeric": 94,
  "agg_like_columns_detected_in_panel": 96,
  "agg_symbol_month_count": 84,
  "agg_symbols": [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
  ],
  "output_columns": 184,
  "output_rows": 250896,
  "panel_rows": 250896
}
```

## Acceptance Decision

The unified panel is accepted for controlled experiment-line feature joins. It is not a final alpha panel: agg coverage is core3-only, May 2026 agg features are absent by design, and every generator using agg fields must obey the availability/timing mask.

## Coverage by Symbol

| symbol   |   rows | min_timestamp        | max_timestamp        |   agg_rows |   agg_coverage | expected_agg_symbol   | coverage_decision                      |
|:---------|-------:|:---------------------|:---------------------|-----------:|---------------:|:----------------------|:---------------------------------------|
| ADAUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| AVAXUSDT |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| BCHUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| BNBUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| BTCUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |      20424 |       0.976851 | True                  | PASS_EXPECTED_CORE3_PARTIAL_TO_2026_04 |
| DOGEUSDT |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| ETHUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |      20424 |       0.976851 | True                  | PASS_EXPECTED_CORE3_PARTIAL_TO_2026_04 |
| LINKUSDT |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| LTCUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| SOLUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |      20424 |       0.976851 | True                  | PASS_EXPECTED_CORE3_PARTIAL_TO_2026_04 |
| SUIUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |
| XRPUSDT  |  20908 | 2024-01-01T00:00:00Z | 2026-05-21T03:00:00Z |          0 |       0        | False                 | PASS_EXPECTED_NO_AGG_COVERAGE          |

## Field Quality

| field_name                            | field_group          |   non_null_rate_when_available |   finite_rate_when_available |              min |              max |
|:--------------------------------------|:---------------------|-------------------------------:|-----------------------------:|-----------------:|-----------------:|
| agg_trade_count                       | activity_liquidity   |                       1        |                            1 |   2659           |      2.46234e+06 |
| agg_underlying_trade_count            | activity_liquidity   |                       1        |                            1 |   9717           |      4.36244e+06 |
| agg_quantity                          | activity_liquidity   |                       1        |                            1 |    358.475       |      2.30119e+07 |
| agg_notional                          | activity_liquidity   |                       1        |                            1 |      1.11465e+07 |      1.44809e+10 |
| agg_buy_agg_trade_count               | flow                 |                       1        |                            1 |   1401           |      1.22988e+06 |
| agg_sell_agg_trade_count              | flow                 |                       1        |                            1 |   1153           |      1.23246e+06 |
| agg_buy_underlying_trade_count        | flow                 |                       1        |                            1 |   4957           |      2.12829e+06 |
| agg_sell_underlying_trade_count       | flow                 |                       1        |                            1 |   4427           |      2.23415e+06 |
| agg_buy_quantity                      | flow                 |                       1        |                            1 |    186.63        |      1.22164e+07 |
| agg_sell_quantity                     | flow                 |                       1        |                            1 |    144.183       |      1.07956e+07 |
| agg_buy_notional                      | flow                 |                       1        |                            1 |      4.44931e+06 |      7.23126e+09 |
| agg_sell_notional                     | flow                 |                       1        |                            1 |      4.98142e+06 |      7.71394e+09 |
| agg_signed_aggressor_quantity         | flow                 |                       1        |                            1 |     -2.52589e+06 |      1.42081e+06 |
| agg_signed_aggressor_notional         | flow                 |                       1        |                            1 |     -1.08849e+09 |      1.17939e+09 |
| agg_trade_count_le_100                | activity_liquidity   |                       1        |                            1 |      0           |      1.06835e+06 |
| agg_trade_count_100_1k                | activity_liquidity   |                       1        |                            1 |    768           |      1.01562e+06 |
| agg_trade_count_1k_10k                | activity_liquidity   |                       1        |                            1 |    402           | 467169           |
| agg_trade_count_10k_100k              | activity_liquidity   |                       1        |                            1 |    181           | 239032           |
| agg_trade_count_100k_1m               | activity_liquidity   |                       1        |                            1 |      0           |  29062           |
| agg_trade_count_gt_1m                 | activity_liquidity   |                       1        |                            1 |      0           |    962           |
| agg_notional_le_100                   | activity_liquidity   |                       1        |                            1 |      0           |      3.94529e+07 |
| agg_notional_100_1k                   | activity_liquidity   |                       1        |                            1 | 282318           |      2.85155e+08 |
| agg_notional_1k_10k                   | activity_liquidity   |                       1        |                            1 |      1.39577e+06 |      1.66172e+09 |
| agg_notional_10k_100k                 | activity_liquidity   |                       1        |                            1 |      4.25347e+06 |      7.36903e+09 |
| agg_notional_100k_1m                  | activity_liquidity   |                       1        |                            1 |      0           |      6.09158e+09 |
| agg_notional_gt_1m                    | activity_liquidity   |                       1        |                            1 |      0           |      3.11836e+09 |
| agg_first_agg_trade_id                | other                |                       1        |                            1 |      5.13967e+08 |      3.27349e+09 |
| agg_last_agg_trade_id                 | other                |                       1        |                            1 |      5.14012e+08 |      3.27351e+09 |
| agg_first_transact_time_ms            | other                |                       1        |                            1 |      1.70407e+12 |      1.77759e+12 |
| agg_last_transact_time_ms             | other                |                       1        |                            1 |      1.70407e+12 |      1.77759e+12 |
| agg_high_price                        | price_microstructure |                       1        |                            1 |     76.75        | 126208           |
| agg_low_price                         | price_microstructure |                       1        |                            1 |     67.29        | 125185           |
| agg_price_std                         | price_microstructure |                       1        |                            1 |      0.0267663   |   2922.6         |
| agg_max_trade_notional                | activity_liquidity   |                       1        |                            1 |  58660           |      2.37588e+08 |
| agg_open_price                        | price_microstructure |                       1        |                            1 |     75.42        | 125986           |
| agg_close_price                       | price_microstructure |                       1        |                            1 |     75.42        | 125986           |
| agg_vwap                              | price_microstructure |                       1        |                            1 |     72.8606      | 125689           |
| agg_buy_vwap                          | price_microstructure |                       1        |                            1 |     72.935       | 125720           |
| agg_sell_vwap                         | price_microstructure |                       1        |                            1 |     72.7904      | 125641           |
| agg_avg_agg_trade_notional            | activity_liquidity   |                       1        |                            1 |   1216.48        | 119451           |
| agg_avg_underlying_trade_notional     | activity_liquidity   |                       1        |                            1 |    526.7         |  21077.5         |
| agg_volume_imbalance                  | flow                 |                       1        |                            1 |     -0.46205     |      0.538215    |
| agg_buy_sell_notional_ratio           | flow                 |                       1        |                            1 |      0.367942    |      3.33102     |
| agg_price_range_bps                   | price_microstructure |                       1        |                            1 |      5.23739     |   3485.78        |
| agg_close_to_open_bps                 | price_microstructure |                       1        |                            1 |  -1157.68        |   1183.37        |
| agg_large_trade_count_100k_plus       | large_trade          |                       1        |                            1 |      0           |  29689           |
| agg_large_notional_100k_plus          | large_trade          |                       1        |                            1 |      0           |      7.49136e+09 |
| agg_large_trade_count_ratio_100k_plus | large_trade          |                       1        |                            1 |      0           |      0.091374    |
| agg_large_notional_ratio_100k_plus    | large_trade          |                       1        |                            1 |      0           |      0.938963    |
| agg_flow_imbalance_qty                | flow                 |                       1        |                            1 |     -0.462232    |      0.538324    |
| agg_flow_imbalance_notional           | flow                 |                       1        |                            1 |     -0.46205     |      0.538215    |
| agg_buy_notional_share                | flow                 |                       1        |                            1 |      0.268975    |      0.769108    |
| agg_sell_notional_share               | flow                 |                       1        |                            1 |      0.230892    |      0.731025    |
| agg_large_notional_share_100k_plus    | large_trade          |                       1        |                            1 |      0           |      0.938963    |
| agg_large_count_share_100k_plus       | large_trade          |                       1        |                            1 |      0           |      0.091374    |
| agg_vwap_close_bps                    | price_microstructure |                       1        |                            1 |   -574.181       |    634.742       |
| agg_buy_sell_vwap_spread_bps          | price_microstructure |                       1        |                            1 |    -47.8888      |     80.2042      |
| agg_avg_underlying_trades_per_agg     | other                |                       1        |                            1 |      1.54352     |      9.51289     |
| agg_notional_sum_4h                   | rolling              |                       0.999951 |                            1 |      5.57441e+07 |      2.86757e+10 |
| agg_quantity_sum_4h                   | rolling              |                       0.999951 |                            1 |   1985.13        |      3.8634e+07  |
| agg_signed_notional_sum_4h            | rolling              |                       0.999951 |                            1 |     -2.1946e+09  |      1.40001e+09 |
| agg_signed_quantity_sum_4h            | rolling              |                       0.999951 |                            1 |     -2.53617e+06 |      1.71189e+06 |
| agg_flow_imbalance_notional_4h        | rolling              |                       0.999951 |                            1 |     -0.28396     |      0.308458    |
| agg_large_notional_sum_4h             | rolling              |                       0.999951 |                            1 |      1.0987e+06  |      1.55339e+10 |
| agg_large_notional_share_4h           | rolling              |                       0.999951 |                            1 |      0.0124741   |      0.8477      |
| agg_trade_count_sum_4h                | rolling              |                       0.999951 |                            1 |  13136           |      4.32371e+06 |
| agg_avg_trade_notional_4h             | rolling              |                       0.999951 |                            1 |   1267.67        |  45121.2         |
| agg_price_range_bps_max_4h            | rolling              |                       0.999951 |                            1 |      9.71168     |   3485.78        |
| agg_close_to_open_bps_sum_4h          | rolling              |                       0.999951 |                            1 |  -1579.49        |   2014.07        |
| agg_notional_sum_24h                  | rolling              |                       0.999461 |                            1 |      5.75039e+08 |      7.42209e+10 |
| agg_quantity_sum_24h                  | rolling              |                       0.999461 |                            1 |  23482.9         |      1.13028e+08 |
| agg_signed_notional_sum_24h           | rolling              |                       0.999461 |                            1 |     -4.39541e+09 |      2.0786e+09  |
| agg_signed_quantity_sum_24h           | rolling              |                       0.999461 |                            1 |     -4.64082e+06 |      2.15765e+06 |
| agg_flow_imbalance_notional_24h       | rolling              |                       0.999461 |                            1 |     -0.15823     |      0.0912522   |
| agg_large_notional_sum_24h            | rolling              |                       0.999461 |                            1 |      3.1708e+07  |      3.83747e+10 |
| agg_large_notional_share_24h          | rolling              |                       0.999461 |                            1 |      0.0366071   |      0.711007    |
| agg_trade_count_sum_24h               | rolling              |                       0.999461 |                            1 | 123815           |      1.082e+07   |
| agg_avg_trade_notional_24h            | rolling              |                       0.999461 |                            1 |   1485.97        |  19242.8         |
| agg_price_range_bps_max_24h           | rolling              |                       0.999461 |                            1 |     22.5269      |   3485.78        |
| agg_close_to_open_bps_sum_24h         | rolling              |                       0.999461 |                            1 |  -2628.81        |   2326.09        |
| agg_notional_shock_24h_mad            | rolling              |                       0.998923 |                            1 |     -4.17915     |    107.882       |
| agg_signed_flow_z_24h                 | rolling              |                       0.999461 |                            1 |     -4.63425     |      4.62082     |
| agg_notional_accel_4h_vs_24h          | rolling              |                       0.999461 |                            1 |     -0.833992    |      3.63294     |
| agg_flow_accel_4h_vs_24h              | rolling              |                       0.999461 |                            1 |     -0.245054    |      0.290145    |
| agg_universe_notional                 | cross_symbol         |                       1        |                            1 |      9.0158e+07  |      3.09843e+10 |
| agg_universe_signed_notional          | cross_symbol         |                       1        |                            1 |     -1.86415e+09 |      1.80943e+09 |
| agg_universe_large_notional           | cross_symbol         |                       1        |                            1 |      2.51967e+07 |      1.37927e+10 |
| agg_cross_symbol_notional_share       | cross_symbol         |                       1        |                            1 |      0.024643    |      0.842527    |
| agg_cross_symbol_signed_flow_share    | cross_symbol         |                       1        |                            1 |  -5975.39        |   7369.95        |
| agg_cross_symbol_large_notional_share | cross_symbol         |                       1        |                            1 |      0           |      0.928334    |
| agg_btcusdt_flow_imbalance_4h         | cross_symbol         |                       0.999951 |                            1 |     -0.28396     |      0.308458    |
| agg_flow_minus_btcusdt_4h             | cross_symbol         |                       0.999951 |                            1 |     -0.386413    |      0.304192    |
| agg_ethusdt_flow_imbalance_4h         | cross_symbol         |                       0.999951 |                            1 |     -0.21699     |      0.270122    |
| agg_flow_minus_ethusdt_4h             | cross_symbol         |                       0.999951 |                            1 |     -0.322568    |      0.35514     |

## Feature Contract

| field_name                            | field_group            | generator_base_field   | role         | feature_available_time_rule              |
|:--------------------------------------|:-----------------------|:-----------------------|:-------------|:-----------------------------------------|
| agg_trade_count                       | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_underlying_trade_count            | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_quantity                          | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional                          | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_agg_trade_count               | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_agg_trade_count              | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_underlying_trade_count        | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_underlying_trade_count       | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_quantity                      | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_quantity                     | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_notional                      | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_notional                     | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_aggressor_quantity         | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_aggressor_notional         | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_le_100                | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_100_1k                | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_1k_10k                | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_10k_100k              | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_100k_1m               | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_gt_1m                 | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_le_100                   | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_100_1k                   | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_1k_10k                   | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_10k_100k                 | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_100k_1m                  | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_gt_1m                    | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_first_agg_trade_id                | other                  | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_last_agg_trade_id                 | other                  | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_first_transact_time_ms            | other                  | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_last_transact_time_ms             | other                  | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_high_price                        | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_low_price                         | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_price_std                         | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_max_trade_notional                | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_open_price                        | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_close_price                       | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_vwap                              | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_vwap                          | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_vwap                         | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_avg_agg_trade_notional            | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_avg_underlying_trade_notional     | activity_liquidity     | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_volume_imbalance                  | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_sell_notional_ratio           | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_price_range_bps                   | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_close_to_open_bps                 | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_trade_count_100k_plus       | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_100k_plus          | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_trade_count_ratio_100k_plus | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_ratio_100k_plus    | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_imbalance_qty                | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_imbalance_notional           | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_notional_share                | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_sell_notional_share               | flow                   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_share_100k_plus    | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_count_share_100k_plus       | large_trade            | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_vwap_close_bps                    | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_buy_sell_vwap_spread_bps          | price_microstructure   | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_avg_underlying_trades_per_agg     | other                  | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_sum_4h                   | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_quantity_sum_4h                   | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_notional_sum_4h            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_quantity_sum_4h            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_imbalance_notional_4h        | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_sum_4h             | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_share_4h           | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_sum_4h                | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_avg_trade_notional_4h             | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_price_range_bps_max_4h            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_close_to_open_bps_sum_4h          | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_sum_24h                  | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_quantity_sum_24h                  | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_notional_sum_24h           | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_quantity_sum_24h           | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_imbalance_notional_24h       | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_sum_24h            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_large_notional_share_24h          | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_trade_count_sum_24h               | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_avg_trade_notional_24h            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_price_range_bps_max_24h           | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_close_to_open_bps_sum_24h         | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_shock_24h_mad            | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_signed_flow_z_24h                 | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_notional_accel_4h_vs_24h          | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_accel_4h_vs_24h              | rolling                | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_universe_notional                 | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_universe_signed_notional          | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_universe_large_notional           | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_cross_symbol_notional_share       | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_cross_symbol_signed_flow_share    | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_cross_symbol_large_notional_share | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_btcusdt_flow_imbalance_4h         | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_minus_btcusdt_4h             | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_ethusdt_flow_imbalance_4h         | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_flow_minus_ethusdt_4h             | cross_symbol           | True                   | feature      | available_after_hour_close_plus_join_lag |
| agg_features_available                | availability_or_schema | False                  | availability | available_after_hour_close_plus_join_lag |
| agg_feature_schema                    | availability_or_schema | False                  | schema       | available_after_hour_close_plus_join_lag |

## Generator Self-Reproduction Contract

| production_family                       | allowed_inputs                                         | allowed_transforms                                                            | allowed_windows           | may_use_missing_as_signal   | requires_agg_available_mask   | must_residualize_against      | notes                                                                                                                                                                   |
|:----------------------------------------|:-------------------------------------------------------|:------------------------------------------------------------------------------|:--------------------------|:----------------------------|:------------------------------|:------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| base_activity_liquidity                 | activity_liquidity                                     | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_cross_symbol                       | cross_symbol                                           | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_flow                               | flow                                                   | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_large_trade                        | large_trade                                            | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_other                              | other                                                  | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_price_microstructure               | price_microstructure                                   | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| base_rolling                            | rolling                                                | Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg                            | none                      | False                       | True                          | FundingCore,Core4 for scoring | Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.                                                       |
| rolling_self_reproduction               | all_numeric_agg_features                               | TSMean,TSStd,TSRank,Delta,Decay,RollingMin,RollingMax,ZScore                  | 4h,8h,12h,24h,48h,72h,96h | False                       | True                          | FundingCore,Core4             | Formula generator may create rolling descendants, but windows must be past-only and feature_available_time shifts by the full rolling lookback plus one completed hour. |
| cross_symbol_self_reproduction_core3    | BTCUSDT,ETHUSDT,SOLUSDT agg features only              | CrossSymbolRank,CrossSymbolZScore,ShareOfUniverse,RelativeToBTC,RelativeToETH | 1h,4h,24h                 | False                       | True                          | FundingCore,Core4             | Cross-symbol transforms are core3-only until agg coverage expands. Do not rank non-agg core12 symbols as zeros.                                                         |
| interaction_self_reproduction           | agg_features plus existing market/funding/basis fields | Mul,Add,Sub,SafeDiv,HorizonSpread,SmoothInteraction                           | same input windows only   | False                       | True                          | FundingCore,Core4             | Interactions are allowed only after both sides pass PIT availability. Funding remains a baseline/control, not an unrestricted discovery target.                         |
| blocked_missingness_or_core12_zero_fill | none                                                   | none                                                                          | none                      | False                       | True                          | n/a                           | Generator must not treat missing agg rows for non-core3 symbols as negative/zero signal. No zero-fill cross-section ranking.                                            |
| blocked_future_or_same_hour             | none                                                   | none                                                                          | none                      | False                       | True                          | n/a                           | Same-hour close execution and future rolling windows are forbidden.                                                                                                     |

## Join and Timing Contract

| rule_id                | rule                                                                                                                                               | status                   |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------|
| panel_source           | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet                                                         | primary_experiment_panel |
| coverage_scope         | Agg features are valid only for BTCUSDT/ETHUSDT/SOLUSDT through 2026-04-30 23:00 UTC; non-core3 rows remain unavailable.                           | required                 |
| availability_mask      | Every formula using agg fields must require agg_features_available == true for the symbol/timestamp.                                               | required                 |
| feature_available_time | For hour bucket timestamp t, agg features are available after t + 1h; rolling descendants are available after the last required input hour closes. | required                 |
| execution              | Primary replay must execute no earlier than next bar after feature availability. Same-hour close execution is forbidden.                           | required                 |
| negative_controls      | Every agg feature smoke must retain row/time shuffle, wrong-lag, sign-flip, and no-agg controls.                                                   | required                 |

## Authorization

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_controlled_feature_join_experiments": true,
  "authorizes_core12_agg_claim": false,
  "authorizes_generator_self_reproduction_under_contract": true,
  "authorizes_shadow_paper_live": false,
  "authorizes_zero_fill_for_missing_agg": false,
  "decision": "PASS_A7V_UNIFIED_PANEL_ACCEPTED_FOR_CONTROLLED_FEATURE_EXPERIMENTS",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T01:03:36Z",
  "primary_panel": "G:\\AlphaFactory_CryptoData\\gold\\panels\\crypto_core12_1h_with_aggtrades_features_v1.parquet",
  "required_next": [
    "A7V-1 implement feature family registry in formula generator",
    "A7V-2 small no-search feature smoke with negative controls",
    "A7V-3 if smoke passes, define agg-aware search cells; no full search yet"
  ]
}
```
