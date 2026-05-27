# CRYPTO A7AC-2C Effective P0 Backfill Coverage Audit

Generated: 2026-05-22T13:13:00Z

## Decision

`PASS_A7AC2C_EFFECTIVE_P0_BACKFILL_SOURCE_COVERAGE_COMPLETE_WITH_LISTING_GAPS`

This is a data-line source coverage audit. It does not build a gold panel, run replay/search, authorize alpha proof, or authorize shadow/paper/live trading.

## Effective Coverage

```text
primary_symbols: 36
monthly_ready_symbols: 36
funding_ready_symbols: 36
metrics_ready_symbols: 36
metrics_density_warning_symbols: 1
monthly_checksum_ok_rows: 4024
monthly_listing_gap_rows: 8
monthly_failure_rows: 0
```

## Listing Gaps

| symbol   | data_type          | interval   | month   | status            | error         |
|:---------|:-------------------|:-----------|:--------|:------------------|:--------------|
| BOMEUSDT | indexPriceKlines   | 1m         | 2024-01 | not_available_404 | 404 Not Found |
| BOMEUSDT | klines             | 1m         | 2024-01 | not_available_404 | 404 Not Found |
| BOMEUSDT | markPriceKlines    | 1m         | 2024-01 | not_available_404 | 404 Not Found |
| BOMEUSDT | premiumIndexKlines | 1m         | 2024-01 | not_available_404 | 404 Not Found |
| BOMEUSDT | indexPriceKlines   | 1m         | 2024-02 | not_available_404 | 404 Not Found |
| BOMEUSDT | klines             | 1m         | 2024-02 | not_available_404 | 404 Not Found |
| BOMEUSDT | markPriceKlines    | 1m         | 2024-02 | not_available_404 | 404 Not Found |
| BOMEUSDT | premiumIndexKlines | 1m         | 2024-02 | not_available_404 | 404 Not Found |

The listing gaps are explicit `not_available_404` rows from Binance Vision monthly source download, not checksum or integrity failures. They must be handled by A7AC-3 listing/survivorship policy before replay.

## Monthly Source Summary

| symbol        |   expected_rows |   manifest_rows |   checksum_ok_rows |   listing_gap_rows |   failure_rows |   missing_manifest_rows | ready   | note             |
|:--------------|----------------:|----------------:|-------------------:|-------------------:|---------------:|------------------------:|:--------|:-----------------|
| 1000BONKUSDT  |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| 1000FLOKIUSDT |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| 1INCHUSDT     |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| AAVEUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ACEUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ACHUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ALGOUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| APEUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| API3USDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| APTUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ARBUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ARUSDT        |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ATOMUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| AXSUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| BANDUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| BATUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| BLURUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| BOMEUSDT      |             112 |             112 |                104 |                  8 |              0 |                       0 | True    | listing_gap_only |
| CELOUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| CHZUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| DASHUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ETCUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| GMXUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| HBARUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| KNCUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| LRCUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| MAGICUSDT     |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| MANAUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| MASKUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| NEARUSDT      |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| PENDLEUSDT    |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| SEIUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| UNIUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| WLDUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| YFIUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |
| ZECUSDT       |             112 |             112 |                112 |                  0 |              0 |                       0 | True    | complete         |

## Funding Source Summary

| symbol        |   ok_runs | initial_ok   | retry_ok   |   rows_max | timestamp_min             | timestamp_max                    | ready   | latest_status   |
|:--------------|----------:|:-------------|:-----------|-----------:|:--------------------------|:---------------------------------|:--------|:----------------|
| 1000BONKUSDT  |         2 | False        | True       |       5232 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| 1000FLOKIUSDT |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| 1INCHUSDT     |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| AAVEUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ACEUSDT       |         1 | True         | False      |       5439 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| ACHUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ALGOUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| APEUSDT       |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| API3USDT      |         1 | True         | False      |       5821 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| APTUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ARBUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ARUSDT        |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ATOMUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| AXSUSDT       |         2 | False        | True       |       3145 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| BANDUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| BATUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| BLURUSDT      |         1 | True         | False      |       2811 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| BOMEUSDT      |         1 | True         | False      |       4780 | 2024-03-16 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| CELOUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| CHZUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| DASHUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ETCUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| GMXUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| HBARUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| KNCUSDT       |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| LRCUSDT       |         1 | True         | False      |       3156 | 2024-01-01 00:00:00+00:00 | 2026-03-24 08:00:00+00:00        | True    | ok              |
| MAGICUSDT     |         2 | False        | True       |       3802 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| MANAUSDT      |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| MASKUSDT      |         1 | True         | False      |       4413 | 2024-01-01 00:00:00+00:00 | 2026-05-21 20:00:00.001000+00:00 | True    | ok              |
| NEARUSDT      |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| PENDLEUSDT    |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| SEIUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| UNIUSDT       |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| WLDUSDT       |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| YFIUSDT       |         1 | True         | False      |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |
| ZECUSDT       |         2 | False        | True       |       2616 | 2024-01-01 00:00:00+00:00 | 2026-05-21 16:00:00+00:00        | True    | ok              |

## Metrics Source Summary

| symbol        |   expected_silver_months |   silver_months |   silver_rows |   silver_density_ratio_vs_30d_5m_proxy | silver_first_month   | silver_last_month   | timestamp_min             | timestamp_max             | missing_silver_months   |   raw_zip_files |   raw_checksum_files |   read_error_count | feature_density_warning   |   sparse_month_count | sparse_months                                     | ready   | note                     |
|:--------------|-------------------------:|----------------:|--------------:|---------------------------------------:|:---------------------|:--------------------|:--------------------------|:--------------------------|:------------------------|----------------:|---------------------:|-------------------:|:--------------------------|---------------------:|:--------------------------------------------------|:--------|:-------------------------|
| 1000BONKUSDT  |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| 1000FLOKIUSDT |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| 1INCHUSDT     |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| AAVEUSDT      |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ACEUSDT       |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ACHUSDT       |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ALGOUSDT      |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| APEUSDT       |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| API3USDT      |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:01+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| APTUSDT       |                       29 |              29 |        250988 |                               1.00171  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ARBUSDT       |                       29 |              29 |        250997 |                               1.00174  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ARUSDT        |                       29 |              29 |        250997 |                               1.00174  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ATOMUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| AXSUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| BANDUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| BATUSDT       |                       29 |              29 |        251005 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| BLURUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| BOMEUSDT      |                       27 |              27 |        229381 |                               0.983286 | 2024-03              | 2026-05             | 2024-03-16 12:35:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             797 |                    0 |                  0 | False                     |                    0 |                                                   | True    | listing_gap_2024_01_02   |
| CELOUSDT      |                       29 |              29 |        250993 |                               1.00173  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| CHZUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| DASHUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ETCUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| GMXUSDT       |                       29 |              29 |        251005 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| HBARUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| KNCUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| LRCUSDT       |                       29 |              29 |        234197 |                               0.934694 | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-21 02:35:08+00:00 |                         |             872 |                    0 |                  0 | True                      |                    3 | 2026-03:6741/8928,2026-04:41/8640,2026-05:25/6048 | True    | vendor_sparse_5m_warning |
| MAGICUSDT     |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| MANAUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| MASKUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| NEARUSDT      |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| PENDLEUSDT    |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| SEIUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| UNIUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| WLDUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| YFIUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |
| ZECUSDT       |                       29 |              29 |        251006 |                               1.00178  | 2024-01              | 2026-05             | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                         |             872 |                    0 |                  0 | False                     |                    0 |                                                   | True    | complete                 |

## Authorization

```text
authorizes_panel_build: True
authorizes_formula_search: false
authorizes_large_search: false
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false
```

## Next

1. Build expanded 1h gold panel from the now-complete source coverage.
2. Run A7AC-3 listing/survivorship policy for explicit listing gaps.
3. Run expanded panel integrity audit before any replay/search.
