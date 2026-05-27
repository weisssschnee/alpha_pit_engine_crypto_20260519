# Crypto A7Y-0 Unified State Panel

- generated_at: `2026-05-22T09:21:11Z`
- decision: `PASS_A7Y0_UNIFIED_STATE_PANEL_READY`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7Y-0 merges the accepted aggTrades-enhanced panel and Binance metrics 1h feature panel into a single experiment panel. It is a data integration gate, not a signal proof.

Metrics vendor 5m warnings and aggTrades availability flags are preserved. Derived fields are not independent data sources.

## Output Panel

`G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet`

## Panel Summary

| panel_path                                                                                         |   rows |   columns | timestamp_min             | timestamp_max             |   file_size_mb |
|:---------------------------------------------------------------------------------------------------|-------:|----------:|:--------------------------|:--------------------------|---------------:|
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet | 251148 |       222 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |         236.36 |

## Coverage

| symbol   |   rows | timestamp_min             | timestamp_max             |   agg_available_hours |   agg_available_rate |   metrics_available_hours |   metrics_available_rate |
|:---------|-------:|:--------------------------|:--------------------------|----------------------:|---------------------:|--------------------------:|-------------------------:|
| ADAUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| AVAXUSDT |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| BCHUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| BNBUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| BTCUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                 20904 |             0.998805 |                     20917 |                 0.999427 |
| DOGEUSDT |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| ETHUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                 20904 |             0.998805 |                     20917 |                 0.999427 |
| LINKUSDT |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| LTCUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| SOLUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                 20904 |             0.998805 |                     20917 |                 0.999427 |
| SUIUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |
| XRPUSDT  |  20929 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                     0 |             0        |                     20917 |                 0.999427 |

## Registry Summary

| source_layer                 | field_role                 | is_independent_source   |   fields |
|:-----------------------------|:---------------------------|:------------------------|---------:|
| base_aggtrades_panel         | aggtrades_feature          | False                   |       96 |
| base_aggtrades_panel         | base_market_feature        | False                   |       86 |
| base_aggtrades_panel         | key                        | False                   |        2 |
| binance_metrics_derived      | metrics_derived_feature    | False                   |       26 |
| binance_vision_metrics_daily | metrics_independent_source | True                    |        6 |

## Checks

| check                          | value                                      | status   |
|:-------------------------------|:-------------------------------------------|:---------|
| a7s1_metrics_acceptance        | PASS_A7S1_ACCEPTED_WITH_VENDOR_5M_WARNINGS | PASS     |
| a7u0r_source_trace             | PASS_A7U0R_SOURCE_TRACE_COMPLETE           | PASS     |
| rows                           | 251148                                     | PASS     |
| columns                        | 222                                        | PASS     |
| symbols                        | 12                                         | PASS     |
| duplicate_symbol_timestamp     | 0                                          | PASS     |
| inf_numeric_cells              | 0                                          | PASS     |
| metrics_independent_fields     | 6                                          | PASS     |
| metrics_derived_fields         | 26                                         | PASS     |
| derived_fields_not_independent | True                                       | PASS     |
| feature_available_time_rule    | timestamp+1h                               | PASS     |

## Authorization

```json
{
  "authorizes_a7y1_small_interaction_diagnostic": true,
  "authorizes_alpha_proof": false,
  "authorizes_full_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "columns": 222,
  "decision": "PASS_A7Y0_UNIFIED_STATE_PANEL_READY",
  "executes_replay": false,
  "executes_search": false,
  "feature_available_time_rule": "feature_available_time = timestamp + 1h; execution_time >= next 1h bar",
  "generated_at": "2026-05-22T09:21:11Z",
  "output_panel": "G:\\AlphaFactory_CryptoData\\gold\\panels\\crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet",
  "required_next": [
    "A7Y-1 small interaction diagnostic",
    "Do not treat metrics derived fields as independent sources",
    "Preserve agg_features_available and metrics_features_available masks"
  ],
  "rows": 251148,
  "vendor_5m_warning_caveat_required": true
}
```
