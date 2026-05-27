# CRYPTO A7AP-0 OKX/Binance Cross-Exchange Overlay Acceptance

Generated: 2026-05-27T00:49:59Z

## Decision

```text
PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_WITH_PRICE_SCALE_QUARANTINE
```

This audit validates the OKX/Binance recent 30d cross-exchange overlay as a short overlap diagnostic dataset. It does not authorize historical alpha proof.

## Summary

```json
{
  "authorizes_a7ap1_small_diagnostic_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_broad_search": false,
  "authorizes_shadow_paper_live": false,
  "binance_funding_non_null_rate": 0.20143208771537258,
  "blockers": [],
  "clean_symbols_after_price_scale_quarantine": 214,
  "coverage": "G:\\AlphaFactory_CryptoData\\manifests\\okx_binance_cross_exchange_1h_30d_v1_20260527_coverage.csv",
  "decision": "PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_WITH_PRICE_SCALE_QUARANTINE",
  "duplicate_symbol_timestamp_rows": 0,
  "executes_acceptance_audit": true,
  "executes_replay": false,
  "executes_search": false,
  "field_contract": "G:\\AlphaFactory_CryptoData\\gold\\metadata\\okx_binance_cross_exchange_1h_30d_v1_field_contract_20260527.json",
  "generated_at": "2026-05-27T00:49:59Z",
  "gold_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\okx_binance_cross_exchange_1h_30d_v1_20260527",
  "manifest": "G:\\AlphaFactory_CryptoData\\manifests\\okx_binance_cross_exchange_1h_30d_v1_20260527_manifest.csv",
  "numeric_inf_cells": 0,
  "okx_funding_non_null_rate": 0.9629447303647348,
  "okx_index_non_null_rate": 0.9985679122846274,
  "okx_mark_non_null_rate": 0.9988364287312598,
  "price_scale_quarantine_symbol_count": 4,
  "price_scale_quarantine_symbols": [
    "1000BONKUSDT",
    "1000FLOKIUSDT",
    "1000PEPEUSDT",
    "1000SHIBUSDT"
  ],
  "rows": 22345,
  "source_report": "G:\\AlphaFactory_CryptoData\\reports\\OKX_BINANCE_CROSS_EXCHANGE_1H_30D_V1_20260527.md",
  "symbols": 218,
  "timestamp_max": "2026-04-30 23:00:00+00:00",
  "timestamp_min": "2026-04-26 17:00:00+00:00",
  "unique_hours": 103,
  "warnings": [
    "short_overlap_window_diagnostic_only",
    "binance_funding_sparse_in_overlap",
    "price_scale_mismatch_symbols_quarantined"
  ]
}
```

## Field Quality

| field_name                            | exists   |   non_null_rate |   nan_count |   inf_count |            min |            max |           mean |
|:--------------------------------------|:---------|----------------:|------------:|------------:|---------------:|---------------:|---------------:|
| okx_mark_close                        | True     |        0.998836 |          26 |           0 |     3.775e-06  | 79242.8        |  387.459       |
| okx_index_close                       | True     |        0.998568 |          32 |           0 |     3.777e-06  | 79283.5        |  387.688       |
| okx_funding_rate                      | True     |        0.962945 |         828 |           0 |    -0.00820405 |     0.0010148  |   -8.74039e-06 |
| okx_realized_rate                     | True     |        0.962945 |         828 |           0 |    -0.00820405 |     0.0010148  |   -8.74039e-06 |
| binance_trade_close                   | True     |        1        |           0 |           0 |     8.472e-05  | 79263.7        |  387.065       |
| binance_mark_close                    | True     |        1        |           0 |           0 |     8.473e-05  | 79245.2        |  387.075       |
| binance_index_close                   | True     |        1        |           0 |           0 |     8.484e-05  | 79283.4        |  387.278       |
| binance_funding_rate                  | True     |        0.201432 |       17844 |           0 |    -0.00738443 |     0.00095703 |   -1.25898e-05 |
| mark_basis_bps_okx_minus_binance      | True     |        0.998836 |          26 |           0 | -9990.02       |   113.552      | -185.512       |
| index_spread_bps_okx_minus_binance    | True     |        0.998568 |          32 |           0 | -9990.02       |   112.684      | -185.856       |
| funding_spread_okx_minus_binance      | True     |        0.201208 |       17849 |           0 |    -0.00180663 |     0.00143961 |    3.72771e-06 |
| okx_internal_mark_index_basis_bps     | True     |        0.997404 |          58 |           0 |  -364.795      |    61.8673     |   -8.71494     |
| binance_internal_mark_index_basis_bps | True     |        1        |           0 |           0 |  -417.259      |    60.3257     |   -8.94457     |

## Timing Audit

| check                                       |   pass_rate |   fail_count |
|:--------------------------------------------|------------:|-------------:|
| feature_available_time_eq_timestamp_plus_1h |           1 |            0 |
| execution_time_eq_feature_available_time    |           1 |            0 |
| stress_execution_time_eq_timestamp_plus_2h  |           1 |            0 |
| historical_backfill_true                    |           1 |            0 |
| forward_only_false                          |           1 |            0 |

## Price Scale / Contract Unit Audit

| symbol        |   rows |   mark_extreme_rows |   index_extreme_rows |   mark_extreme_share |   index_extreme_share |   mark_basis_min |   mark_basis_max |   index_spread_min |   index_spread_max | price_scale_status              |
|:--------------|-------:|--------------------:|---------------------:|---------------------:|----------------------:|-----------------:|-----------------:|-------------------:|-------------------:|:--------------------------------|
| 1000BONKUSDT  |    103 |                 103 |                  103 |                    1 |                     1 |         -9990.01 |         -9989.99 |           -9990.01 |           -9989.99 | quarantine_price_scale_mismatch |
| 1000FLOKIUSDT |    103 |                 103 |                  103 |                    1 |                     1 |         -9990.01 |         -9990    |           -9990.01 |           -9990    | quarantine_price_scale_mismatch |
| 1000PEPEUSDT  |    103 |                 103 |                  103 |                    1 |                     1 |         -9990.02 |         -9989.99 |           -9990.01 |           -9989.99 | quarantine_price_scale_mismatch |
| 1000SHIBUSDT  |    103 |                 103 |                  103 |                    1 |                     1 |         -9990.02 |         -9990    |           -9990.02 |           -9990    | quarantine_price_scale_mismatch |

## Symbol Quality Sample

| symbol        |   rows | timestamp_min             | timestamp_max             |   expected_hours_between_min_max |   missing_hour_count_between_min_max |   duplicate_timestamp_count |   okx_mark_non_null_rate |   okx_index_non_null_rate |   okx_funding_non_null_rate |   binance_funding_non_null_rate |
|:--------------|-------:|:--------------------------|:--------------------------|---------------------------------:|-------------------------------------:|----------------------------:|-------------------------:|--------------------------:|----------------------------:|--------------------------------:|
| 0GUSDT        |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.970874 |                        0.242718 |
| 1000BONKUSDT  |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.242718 |
| 1000FLOKIUSDT |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| 1000PEPEUSDT  |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| 1000SHIBUSDT  |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| 1INCHUSDT     |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| 2ZUSDT        |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| AAVEUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.932039 |                        0.116505 |
| ACHUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.970874 |                        0.116505 |
| ACTUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| ACUUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| ADAUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| AEVOUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| AGLDUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| ALGOUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| ANIMEUSDT     |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  0.980583 |                    0.970874 |                        0.242718 |
| APEUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| API3USDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| APRUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| APTUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  0.980583 |                    0.932039 |                        0.116505 |
| ARBUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.932039 |                        0.116505 |
| ARKMUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| ASTERUSDT     |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.970874 |                        0.242718 |
| ATHUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.970874 |                        0.242718 |
| ATOMUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  0.980583 |                    0.932039 |                        0.116505 |
| AVAXUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  0.980583 |                    0.932039 |                        0.116505 |
| AVNTUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| AXSUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BABYUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BANDUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| BARDUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BATUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| BCHUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 0.980583 |                  1        |                    0.932039 |                        0.116505 |
| BEATUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BICOUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| BIGTIMEUSDT   |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BIOUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BLURUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |
| BNBUSDT       |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.932039 |                        0.116505 |
| BOMEUSDT      |    103 | 2026-04-26 17:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                              103 |                                    0 |                           0 |                 1        |                  1        |                    0.970874 |                        0.242718 |

## Manifest Summary

| status   |   symbols |
|:---------|----------:|
| ok       |       218 |

## Coverage Summary

| decision               |   symbols |
|:-----------------------|----------:|
| usable_overlap_overlay |       218 |

## Contract Audit

| item                              | value                                                                                                            |
|:----------------------------------|:-----------------------------------------------------------------------------------------------------------------|
| dataset                           | okx_binance_cross_exchange_1h_30d_v1_20260527                                                                    |
| decision                          | CANDIDATE_DIAGNOSTIC_OVERLAY_CLEAN_SUBSET_ONLY                                                                   |
| okx_source                        | OKX public REST funding-rate-history, mark-price-candles, index-candles; 30d recent pull; clean subset only      |
| binance_source                    | binance_universe498_replay_1h_v1_20260525 accepted replay base                                                   |
| join_rule                         | inner join on symbol + hourly timestamp; OKX funding backward-asof to hourly rows using fundingTime <= timestamp |
| feature_available_time            | timestamp + 1h                                                                                                   |
| recommended_stress_execution_time | timestamp + 2h                                                                                                   |
| not_authorized                    | alpha proof;shadow;paper;live                                                                                    |

## Boundary

```text
AUTHORIZED:
  A7AP-1 small diagnostic field-family smoke on overlap rows only

NOT AUTHORIZED:
  historical alpha proof
  broad search
  shadow / paper / live

PRIMARY CAVEAT:
  OKX 30d recent data only overlaps the accepted Binance panel from 2026-04-26 17:00 UTC to 2026-04-30 23:00 UTC.
```
