# CRYPTO A7AE-0 New Data Intake Audit

Generated: 2026-05-22T14:57:37Z

## Decision

```text
PASS_A7AE0_NEW_DATA_INTAKE_AUDIT_WITH_USAGE_LIMITS
```

This stage inspects new data only. It does not run replay and does not run search.

## Authorization

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_direct_large_search": false,
  "authorizes_field_selection_contract": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AE0_NEW_DATA_INTAKE_AUDIT_WITH_USAGE_LIMITS",
  "recommended_next": "A7AE1 field-family selection contract for core39/core3 data, then small controlled replay only",
  "warnings": [
    "core12_rem9_aggtrades_raw_download_in_progress_not_ready",
    "market_structure_has_high_missing_funding_related_fields_select_columns_before_replay",
    "core39_all_features_is_wide_derived_table_do_not_feed_all_603_columns_blindly",
    "core3_aggtrades_is_core3_only_not_core39_or_core48_wide"
  ]
}
```

## Dataset Summary

| dataset_id                                      | path                                                                                                              | exists   |   size_mb |   rows |   columns |   symbols | timestamp_min             | timestamp_max             |   duplicate_symbol_timestamp | sample_symbols                                                                                                                                                                                                                                                                                                                    |   agg_columns |   market_structure_columns |   known_independent_metric_source_fields |
|:------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|:---------|----------:|-------:|----------:|----------:|:--------------------------|:--------------------------|-----------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------:|---------------------------:|-----------------------------------------:|
| core39_market_structure_1h                      | G:\AlphaFactory_CryptoData\gold\features\binance_core39_market_structure_1h_features_v1.parquet                   | True     |   185.505 | 816192 |        57 |        39 | 2024-01-01 00:00:00+00:00 | 2026-05-21 23:00:00+00:00 |                            0 | AAVEUSDT;ADAUSDT;ALGOUSDT;APTUSDT;ARBUSDT;ARUSDT;ATOMUSDT;AVAXUSDT;BCHUSDT;BNBUSDT;BTCUSDT;DOGEUSDT;DOTUSDT;ETCUSDT;ETHUSDT;FILUSDT;GALAUSDT;HBARUSDT;ICPUSDT;IMXUSDT;INJUSDT;JTOUSDT;LINKUSDT;LTCUSDT;MANAUSDT;NEARUSDT;OPUSDT;ORDIUSDT;SANDUSDT;SEIUSDT;SOLUSDT;STXUSDT;SUIUSDT;TIAUSDT;TRXUSDT;UNIUSDT;WLDUSDT;XLMUSDT;XRPUSDT |             0 |                         41 |                                        0 |
| core39_all_features_metrics_v3_market_structure | G:\AlphaFactory_CryptoData\gold\features\binance_core39_all_features_metrics_v3_market_structure_v1.parquet       | True     |  2541.36  | 815818 |       603 |        39 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                            0 | AAVEUSDT;ADAUSDT;ALGOUSDT;APTUSDT;ARBUSDT;ARUSDT;ATOMUSDT;AVAXUSDT;BCHUSDT;BNBUSDT;BTCUSDT;DOGEUSDT;DOTUSDT;ETCUSDT;ETHUSDT;FILUSDT;GALAUSDT;HBARUSDT;ICPUSDT;IMXUSDT;INJUSDT;JTOUSDT;LINKUSDT;LTCUSDT;MANAUSDT;NEARUSDT;OPUSDT;ORDIUSDT;SANDUSDT;SEIUSDT;SOLUSDT;STXUSDT;SUIUSDT;TIAUSDT;TRXUSDT;UNIUSDT;WLDUSDT;XLMUSDT;XRPUSDT |             0 |                         41 |                                        6 |
| core3_all_features_with_aggtrades               | G:\AlphaFactory_CryptoData\gold\features\binance_core3_all_features_metrics_market_structure_aggtrades_v1.parquet | True     |   315.766 |  62757 |       699 |         3 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                            0 | BTCUSDT;ETHUSDT;SOLUSDT                                                                                                                                                                                                                                                                                                           |            96 |                         41 |                                        6 |

## Independent Source Contract

| source_family                 | independent_source_fields                                                                                                                                | historical_backfill   | experiment_status                                                       |
|:------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------|:------------------------------------------------------------------------|
| binance_metrics_history       | open_interest;open_interest_value;global_long_short_account_ratio;top_long_short_account_ratio;top_long_short_position_ratio;taker_buy_sell_volume_ratio | True                  | usable_with_vendor_5m_warnings_and_field_selection                      |
| market_structure_rest_history | premiumIndexKlines;markPriceKlines;indexPriceKlines;fundingRate                                                                                          | True                  | usable_for_field_selection; funding fields must preserve asof semantics |
| aggtrades_order_flow_core3    | aggTrades order-flow buckets, signed aggressor flow, large trade buckets                                                                                 | True                  | core3_only; do not project to core39/core48                             |
| aggtrades_raw_core12_rem9     | raw aggTrades zip/checksum                                                                                                                               | False                 | in_progress_raw_only_not_experiment_ready                               |

## Market Structure Quality

| field_name                   |   missing_count |   missing_rate | dtype               |
|:-----------------------------|----------------:|---------------:|:--------------------|
| funding_x_basis              |          249108 |      0.305348  | float64             |
| premium_minus_funding_bps    |          244546 |      0.299756  | float64             |
| funding_rate_zscore_168h     |          236201 |      0.289527  | float64             |
| funding_rate_change_9obs     |          212113 |      0.26      | float64             |
| funding_rate_change_3obs     |          211879 |      0.259714  | float64             |
| funding_rate_change_1obs     |          211801 |      0.259618  | float64             |
| funding_rate                 |          211762 |      0.25957   | float64             |
| funding_source               |          211762 |      0.25957   | object              |
| funding_mark_price           |          211762 |      0.25957   | float64             |
| funding_time                 |          211762 |      0.25957   | datetime64[ns, UTC] |
| hours_since_funding          |          211762 |      0.25957   | float64             |
| funding_rate_bps             |          211762 |      0.25957   | float64             |
| premium_index_return_24h     |          131933 |      0.161719  | float64             |
| premium_index_return_1h      |          131098 |      0.160695  | float64             |
| premium_index_range_bps      |          131061 |      0.16065   | float64             |
| mark_index_basis_zscore_168h |           38943 |      0.0477349 | float64             |
| index_price_return_24h       |           38297 |      0.0469431 | float64             |
| mark_index_basis_change_24h  |           38297 |      0.0469431 | float64             |
| mark_index_basis_change_4h   |           37537 |      0.0460115 | float64             |
| index_price_return_1h        |           37423 |      0.0458718 | float64             |
| mark_index_basis_change_1h   |           37423 |      0.0458718 | float64             |
| index_price_source           |           37385 |      0.0458252 | object              |
| index_price_close            |           37385 |      0.0458252 | float64             |
| index_price_low              |           37385 |      0.0458252 | float64             |
| index_price_high             |           37385 |      0.0458252 | float64             |
| index_price_open             |           37385 |      0.0458252 | float64             |
| index_price_range_bps        |           37385 |      0.0458252 | float64             |
| mark_index_basis_bps         |           37385 |      0.0458252 | float64             |
| mark_index_basis             |           37385 |      0.0458252 | float64             |
| index_price_close_time       |           37385 |      0.0458252 | datetime64[ns, UTC] |
| index_price_sample_count     |           37385 |      0.0458252 | float64             |
| premium_index_change_24h     |           33759 |      0.0413806 | float64             |
| premium_index_change_4h      |           32979 |      0.0404245 | float64             |
| premium_index_change_1h      |           32862 |      0.040281  | float64             |
| premium_index_open           |           32823 |      0.0402332 | float64             |
| premium_index_sample_count   |           32823 |      0.0402332 | float64             |
| premium_index_close_time     |           32823 |      0.0402332 | datetime64[ns, UTC] |
| premium_index_high           |           32823 |      0.0402332 | float64             |
| premium_index_low            |           32823 |      0.0402332 | float64             |
| premium_index_close          |           32823 |      0.0402332 | float64             |

## Core3 aggTrades Coverage

| symbol   |   rows |   agg_rows |   agg_coverage | timestamp_min             | timestamp_max             | agg_timestamp_min         | agg_timestamp_max         |
|:---------|-------:|-----------:|---------------:|:--------------------------|:--------------------------|:--------------------------|:--------------------------|
| BTCUSDT  |  20919 |      20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |
| ETHUSDT  |  20919 |      20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |
| SOLUSDT  |  20919 |      20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |

## Core12 Remaining aggTrades Raw Status

| manifest                                                                                         | status                | symbol   |   rows | checksum_ok_count   | first_download_time   | last_download_time   |
|:-------------------------------------------------------------------------------------------------|:----------------------|:---------|-------:|:--------------------|:----------------------|:---------------------|
| G:\AlphaFactory_CryptoData\manifests\aggtrades_raw_only_2024-01_2026-05_core12_rem9_20260522.csv | partial_manifest_seen | ADAUSDT  |      4 |                     | 2026-05-22T14:48:27Z  | 2026-05-22T14:55:21Z |

## Running Data Processes

|   process_id | name           | command_line                                                                                                                                                                                                                                                                                                   |
|-------------:|:---------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|        20968 | powershell.exe | "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;                                                                                                                                                                                  |
|              |                | G:\PythonProject\.venv\Scripts\python.exe G:\AlphaFactory_CryptoData\scripts\download_aggtrades_raw_only.py --symbols ADAUSDT AVAXUSDT BCHUSDT BNBUSDT DOGEUSDT LINKUSDT LTCUSDT SUIUSDT XRPUSDT --start 2024-01 --end 2026-05 --sleep 0.05 --timeout 300 --tag core12_rem9_20260522"                          |
|        21740 | python.exe     | "G:\PythonProject\.venv\Scripts\python.exe" G:\AlphaFactory_CryptoData\scripts\download_aggtrades_raw_only.py --symbols ADAUSDT AVAXUSDT BCHUSDT BNBUSDT DOGEUSDT LINKUSDT LTCUSDT SUIUSDT XRPUSDT --start 2024-01 --end 2026-05 --sleep 0.05 --timeout 300 --tag core12_rem9_20260522                         |
|        18376 | python.exe     | "C:\Users\12398\AppData\Local\Programs\Python\Python311\python.exe" G:\AlphaFactory_CryptoData\scripts\download_aggtrades_raw_only.py --symbols ADAUSDT AVAXUSDT BCHUSDT BNBUSDT DOGEUSDT LINKUSDT LTCUSDT SUIUSDT XRPUSDT --start 2024-01 --end 2026-05 --sleep 0.05 --timeout 300 --tag core12_rem9_20260522 |
|        23164 | powershell.exe | powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'download_aggtrades_raw_only|core39|market_structure|aggtrades' } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Depth 3"                                                                   |

## Usage Boundary

- `core39_all_features_metrics_v3_market_structure` is a wide research/search table, not a proof panel. It needs field-family selection and correlation pruning first.
- `core39_market_structure` adds PIT-relevant market structure fields from REST historical sources; funding fields must remain as-of/backward only.
- `core3_all_features_with_aggtrades` is strong but core3-only; it cannot be projected to core39/core48.
- `core12_rem9 aggTrades raw` is currently raw/in-progress and is not experiment-ready until checksum/source trace and hourly aggregation close.
- No alpha proof, shadow, paper, live, or large search is authorized by this audit.
