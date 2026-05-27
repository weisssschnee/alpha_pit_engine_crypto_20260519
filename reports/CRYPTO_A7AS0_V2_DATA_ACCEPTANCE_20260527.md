# CRYPTO A7AS-0 V2 Data Acceptance

Generated: 2026-05-27T09:39:51Z

## Decision

```text
PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G
```

## Base Summary

| metric                                      | value                                                                              |
|:--------------------------------------------|:-----------------------------------------------------------------------------------|
| dataset                                     | binance_universe498_replay_1h_v2_20260527                                          |
| path                                        | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527 |
| report_decision                             | BINANCE_UNIVERSE498_REPLAY_BASE_EXTENDED_TO_MAY_PATCH                              |
| symbols_reported                            | 498                                                                                |
| rows_reported                               | 6949596                                                                            |
| min_timestamp                               | 2024-01-01 00:00:00                                                                |
| max_timestamp                               | 2026-05-26 00:00:00                                                                |
| duplicate_timestamp_count                   | 0                                                                                  |
| inf_cell_count                              | 0                                                                                  |
| gap_hours_gt_1                              | 9                                                                                  |
| schema_columns                              | 54                                                                                 |
| missing_required_columns                    | []                                                                                 |
| manifest_rows                               | 498                                                                                |
| manifest_status_columns                     | ['status']                                                                         |
| rows                                        | 498                                                                                |
| metrics_coverage_min                        | 0.8685878962536023                                                                 |
| metrics_coverage_median                     | 1.0                                                                                |
| metrics_coverage_p05                        | 0.9995243757431628                                                                 |
| metrics_coverage_below_095                  | 6                                                                                  |
| market_funding_coverage_min                 | 0.9645659928656362                                                                 |
| market_funding_coverage_median              | 0.9999229729752258                                                                 |
| market_funding_coverage_p05                 | 0.9997814070958411                                                                 |
| market_funding_coverage_below_095           | 0                                                                                  |
| open_interest_last_coverage_min             | 0.8685878962536023                                                                 |
| open_interest_last_coverage_median          | 1.0                                                                                |
| open_interest_last_coverage_p05             | 0.9995243757431628                                                                 |
| open_interest_last_coverage_below_095       | 6                                                                                  |
| open_interest_value_last_coverage_min       | 0.8685878962536023                                                                 |
| open_interest_value_last_coverage_median    | 1.0                                                                                |
| open_interest_value_last_coverage_p05       | 0.9995243757431628                                                                 |
| open_interest_value_last_coverage_below_095 | 6                                                                                  |

## Base Sample Audit

| symbol       |   rows | min_timestamp             | max_timestamp             |   duplicate_symbol_timestamp |   inf_numeric_cells |   trade_close_na |   open_interest_last_na |
|:-------------|-------:|:--------------------------|:--------------------------|-----------------------------:|--------------------:|-----------------:|------------------------:|
| 0GUSDT       |   6010 | 2025-09-17 15:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |                1 |                       0 |
| 1000PEPEUSDT |  21025 | 2024-01-01 00:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |                1 |                      10 |
| BTCUSDT      |  21025 | 2024-01-01 00:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |                1 |                      10 |
| ETHUSDT      |  21025 | 2024-01-01 00:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |                1 |                      10 |
| SOLUSDT      |  21025 | 2024-01-01 00:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |                1 |                      10 |

## Overlay Summary

| metric                            | value                                                                                          |
|:----------------------------------|:-----------------------------------------------------------------------------------------------|
| dataset                           | okx_binance_cross_exchange_unified_1h_30d_v2_20260527                                          |
| path                              | G:\AlphaFactory_CryptoData\gold\features\okx_binance_cross_exchange_unified_1h_30d_v2_20260527 |
| report_decision                   | DIAGNOSTIC_CROSS_EXCHANGE_UNIFIED_V2_READY                                                     |
| symbols_reported                  | 218                                                                                            |
| rows_reported                     | 153363                                                                                         |
| min_timestamp                     | 2026-04-26 17:00:00                                                                            |
| max_timestamp                     | 2026-05-26 00:00:00                                                                            |
| duplicate_timestamp_count         | 0                                                                                              |
| inf_cell_count                    | 0                                                                                              |
| schema_columns                    | 65                                                                                             |
| pattern_hits                      | {'okx': 42, 'binance': 17, 'spread': 4, 'basis': 3, 'funding': 9, 'open_interest': 6}          |
| overlay_symbols_in_base           | 218                                                                                            |
| overlay_symbols_not_in_base       | 0                                                                                              |
| base_symbols_without_overlay      | 280                                                                                            |
| rows                              | 218                                                                                            |
| price_funding_coverage_min        | 0.9971590909090908                                                                             |
| price_funding_coverage_median     | 1.0                                                                                            |
| price_funding_coverage_p05        | 0.9985775248933144                                                                             |
| price_funding_coverage_below_095  | 0                                                                                              |
| oi_coverage_min                   | 0.9857954545454546                                                                             |
| oi_coverage_median                | 1.0                                                                                            |
| oi_coverage_p05                   | 0.9985775248933144                                                                             |
| oi_coverage_below_095             | 0                                                                                              |
| crowding_taker_coverage_min       | 0.9829545454545454                                                                             |
| crowding_taker_coverage_median    | 0.984352773826458                                                                              |
| crowding_taker_coverage_p05       | 0.9829545454545454                                                                             |
| crowding_taker_coverage_below_095 | 0                                                                                              |

## Overlay Sample Audit

| symbol       |   rows | min_timestamp             | max_timestamp             |   duplicate_symbol_timestamp |   inf_numeric_cells |
|:-------------|-------:|:--------------------------|:--------------------------|-----------------------------:|--------------------:|
| 0GUSDT       |    704 | 2026-04-26 17:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |
| 1000PEPEUSDT |    704 | 2026-04-26 17:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |
| BTCUSDT      |    704 | 2026-04-26 17:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |
| ETHUSDT      |    704 | 2026-04-26 17:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |
| SOLUSDT      |    703 | 2026-04-26 18:00:00+00:00 | 2026-05-26 00:00:00+00:00 |                            0 |                   0 |

## Overlay Timing Contract Extract

| field          | source   | pit   | feature_available_time   | usage   |
|:---------------|:---------|:------|:-------------------------|:--------|
| field_families |          |       |                          |         |

## Boundary

```text
Base v2 may replace v1 for replay/field-family smoke after this acceptance.
Overlay v2 is 30d diagnostic only; do not use it as full-history alpha proof input.
One-bar-lag stress remains required. Fixed +2h blanket stress remains prohibited.
No formula search, alpha proof, shadow, paper, or live is authorized by this acceptance.
```
