# Crypto A7S-1 Metrics Acceptance Audit

- generated_at: `2026-05-22T08:24:18Z`
- decision: `PASS_A7S1_ACCEPTED_WITH_VENDOR_5M_WARNINGS`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

This is the experiment-side acceptance audit for Binance Vision daily/metrics. It verifies source trace closure, field contract boundaries, feature availability, and gold parquet sanity. It does not run alpha search.

Vendor 5m jitter/gap warnings are retained as caveats. They do not block controlled experiments, but must be carried into reports.

## Source Trace Summary

| check                             |   value | status   |
|:----------------------------------|--------:|:---------|
| expected_symbol_days              |   10464 | INFO     |
| ready_symbol_days                 |   10464 | PASS     |
| checksum_not_ok                   |       0 | PASS     |
| raw_duplicate_timestamp_count     |       0 | PASS     |
| rounded_5m_bucket_duplicate_count |      72 | WARNING  |
| rounded_5m_timestamp_gap_count    |     132 | WARNING  |
| gap_symbol_days                   |      48 | WARNING  |
| raw_nan_count                     |    1501 | WARNING  |
| negative_raw_values               |       0 | PASS     |
| symbols                           |      12 | PASS     |

## Gold Panel Summary

| check                           | value                     | status   |
|:--------------------------------|:--------------------------|:---------|
| gold_path_exists                | True                      | PASS     |
| gold_rows                       | 251028                    | PASS     |
| gold_columns                    | 40                        | PASS     |
| gold_symbols                    | 12                        | PASS     |
| gold_timestamp_min              | 2024-01-01 00:00:00+00:00 | INFO     |
| gold_timestamp_max              | 2026-05-22 00:00:00+00:00 | INFO     |
| gold_duplicate_symbol_timestamp | 0                         | PASS     |
| gold_inf_cells                  | 0                         | PASS     |
| gold_nan_numeric_cells          | 5048                      | WARNING  |

## Field Contract Summary

| check                                  |   value | status   |
|:---------------------------------------|--------:|:---------|
| independent_source_field_count         |       6 | PASS     |
| derived_field_count                    |      29 | PASS     |
| forward_only_independent_fields        |       0 | PASS     |
| historical_backfill_independent_fields |       6 | PASS     |

## Independent Source Fields

```text
global_long_short_account_ratio
open_interest
open_interest_value
taker_buy_sell_volume_ratio
top_long_short_account_ratio
top_long_short_position_ratio
```

## Derived Feature Fields

```text
global_long_short_account_ratio_change_1h
global_long_short_account_ratio_change_24h
global_long_short_account_ratio_change_4h
global_long_short_account_ratio_zscore_168h
open_interest_change_1h
open_interest_change_24h
open_interest_change_4h
open_interest_value_change_1h
open_interest_value_change_24h
open_interest_value_change_4h
open_interest_value_zscore_168h
open_interest_x_agg_signed_quote_notional
open_interest_x_price_move_1h
open_interest_x_signed_aggressor_volume
open_interest_x_taker_imbalance
open_interest_x_volume_imbalance
open_interest_zscore_168h
taker_buy_sell_volume_ratio_change_1h
taker_buy_sell_volume_ratio_change_24h
taker_buy_sell_volume_ratio_change_4h
taker_buy_sell_volume_ratio_zscore_168h
top_long_short_account_ratio_change_1h
top_long_short_account_ratio_change_24h
top_long_short_account_ratio_change_4h
top_long_short_account_ratio_zscore_168h
top_long_short_position_ratio_change_1h
top_long_short_position_ratio_change_24h
top_long_short_position_ratio_change_4h
top_long_short_position_ratio_zscore_168h
```

## Availability Summary

| check                                  |   value | status   |
|:---------------------------------------|--------:|:---------|
| availability_symbols                   |      12 | PASS     |
| available_before_execution_all         |    True | PASS     |
| availability_duplicate_timestamp_count |       0 | PASS     |
| availability_inf_cells                 |       0 | PASS     |
| availability_nan_cells                 |    4736 | WARNING  |

## Coverage By Symbol

| symbol   |   expected_days |   ready_days |   missing_or_hold_days |   checksum_ok_days |   coverage_by_date |   row_coverage |   timestamp_gap_count_5m |   nan_count_raw_values |   negative_count_raw_values |
|:---------|----------------:|-------------:|-----------------------:|-------------------:|-------------------:|---------------:|-------------------------:|-----------------------:|----------------------------:|
| ADAUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999411 |                       11 |                    125 |                           0 |
| AVAXUSDT |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    125 |                           0 |
| BCHUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    124 |                           0 |
| BNBUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    126 |                           0 |
| BTCUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    122 |                           0 |
| DOGEUSDT |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    126 |                           0 |
| ETHUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    128 |                           0 |
| LINKUSDT |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    123 |                           0 |
| LTCUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    120 |                           0 |
| SOLUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    128 |                           0 |
| SUIUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    126 |                           0 |
| XRPUSDT  |             872 |          872 |                      0 |                872 |                  1 |       0.999482 |                       11 |                    128 |                           0 |

## Authorization

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_controlled_metrics_diagnostics": true,
  "authorizes_metrics_feature_registry_integration": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7S1_ACCEPTED_WITH_VENDOR_5M_WARNINGS",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T08:24:18Z",
  "gold_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_metrics_1h_features_v1.parquet",
  "independent_source_fields": [
    "global_long_short_account_ratio",
    "open_interest",
    "open_interest_value",
    "taker_buy_sell_volume_ratio",
    "top_long_short_account_ratio",
    "top_long_short_position_ratio"
  ],
  "required_next": [
    "A7S-2 metrics feature registry integration and controlled diagnostics",
    "Do not classify change/zscore/interaction fields as independent sources",
    "Carry vendor 5m bucket duplicate/gap/NaN caveats downstream"
  ],
  "source_report": "G:\\AlphaFactory_CryptoData\\alphafactory_crypto\\reports\\CRYPTO_A7S1_BINANCE_METRICS_SOURCE_TRACE_20260522.md",
  "vendor_5m_warning_caveat_required": true,
  "warnings": [
    "rounded_5m_bucket_duplicate_count",
    "rounded_5m_timestamp_gap_count",
    "gap_symbol_days",
    "raw_nan_count",
    "gold_nan_numeric_cells",
    "availability_nan_cells"
  ]
}
```

## Required Next

- Merge metrics into the experiment feature registry as `independent metrics source + derived feature layer`.
- Run only controlled A7S-2/A7R-style diagnostics first; no alpha proof or full search.
- Preserve vendor 5m warning caveat in all downstream reports.