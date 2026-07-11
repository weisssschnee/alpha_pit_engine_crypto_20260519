# CRYPTO A7AJ-0 Universe500 Silver Acceptance

Generated: 2026-07-11T05:32:46Z

## Decision

```text
PASS_A7AJ_UNIVERSE500_SILVER_ACCEPTED_AND_SEARCH_PANEL_PREPARED
```

This audit validates the incoming company-machine silver aggregates on the local machine. It does not run replay and does not run search.

## Summary

```json
{
  "authorizes_a7ak_small_field_family_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AJ_UNIVERSE500_SILVER_ACCEPTED_AND_SEARCH_PANEL_PREPARED",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-07-11T05:32:46Z",
  "incoming_root": "G:\\AlphaFactory_CryptoData\\incoming_company\\crypto_universe500_silver_20260525",
  "market_metrics_intersection_symbols": 300,
  "market_rows_manifest": 5362049,
  "market_symbols": 300,
  "metrics_rows_manifest": 6918822,
  "metrics_symbols": 498,
  "output_panel_columns_sample": 124,
  "output_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe300_market_metrics_agg_overlay_1h_v1_20260525",
  "output_panel_rows": 5362049,
  "output_panel_symbols": 300,
  "warnings": [
    "Incoming company package contains silver aggregates only; raw checksum trace remains on company machine",
    "Universe300 is current/top selection and is not by itself a survivorship-safe proof universe",
    "Output market/funding panel ends at 2026-04-30; May stress requires separate current/forward source and remains excluded from ranking",
    "May remains stress-only and must not be used for ranking, tuning, universe selection, or promotion"
  ]
}
```

## Dataset Summary

| dataset                             |   manifest_symbols |   ok_status |   audit_read_ok |   rows_manifest |   rows_actual |   duplicate_timestamp_count |   gap_hours |   inf_cell_count |
|:------------------------------------|-------------------:|------------:|----------------:|----------------:|--------------:|----------------------------:|------------:|-----------------:|
| metrics_1h_universe500_v1           |                498 |         498 |             498 |         6918822 |       6918822 |                           0 |        1988 |                0 |
| monthly_market_funding_1h_top300_v1 |                300 |         300 |             300 |         5362049 |       5362049 |                           0 |          65 |                0 |

## Manifest Reports

```text
metrics_report: G:\AlphaFactory_CryptoData\incoming_company\crypto_universe500_silver_20260525\extracted\reports\metrics_1h_universe500_v1_20260525_aggregate_v1.json
market_report: G:\AlphaFactory_CryptoData\incoming_company\crypto_universe500_silver_20260525\extracted\reports\monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.json
metrics_manifest: G:\AlphaFactory_CryptoData\incoming_company\crypto_universe500_silver_20260525\extracted\manifests\metrics_1h_universe500_v1_20260525_aggregate_v1.csv
market_manifest: G:\AlphaFactory_CryptoData\incoming_company\crypto_universe500_silver_20260525\extracted\manifests\monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.csv
```

## Worst Metrics Gaps

| symbol        |   actual_rows | actual_min_timestamp      | actual_max_timestamp      |   gap_hours |   duplicate_timestamp_count |   inf_cell_count |
|:--------------|--------------:|:--------------------------|:--------------------------|------------:|----------------------------:|-----------------:|
| NFPUSDT       |         20943 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          34 |                           0 |                0 |
| USTCUSDT      |         20944 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          33 |                           0 |                0 |
| VETUSDT       |         20944 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          33 |                           0 |                0 |
| XLMUSDT       |         20944 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          33 |                           0 |                0 |
| TURBOUSDT     |         17339 | 2024-05-30 15:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          23 |                           0 |                0 |
| 1000BONKUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000FLOKIUSDT |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000LUNCUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000PEPEUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000RATSUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000SATSUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000SHIBUSDT  |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1000XECUSDT   |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| 1INCHUSDT     |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ACEUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ACHUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| AGLDUSDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ALICEUSDT     |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ANKRUSDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| APEUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| API3USDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| APTUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ARBUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ARKMUSDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ARKUSDT       |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ARPAUSDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ARUSDT        |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| ASTRUSDT      |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| AUCTIONUSDT   |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |
| BEAMXUSDT     |         20967 | 2024-01-01 00:00:00+00:00 | 2026-05-24 00:00:00+00:00 |          10 |                           0 |                0 |

## Worst Market Gaps

| symbol        |   actual_rows | actual_min_timestamp      | actual_max_timestamp      |   gap_hours |   duplicate_timestamp_count |   inf_cell_count |
|:--------------|--------------:|:--------------------------|:--------------------------|------------:|----------------------------:|-----------------:|
| CATIUSDT      |         14107 | 2024-09-18 16:00:00+00:00 | 2026-04-30 23:00:00+00:00 |          37 |                           0 |                0 |
| RONINUSDT     |         19561 | 2024-02-05 16:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           7 |                           0 |                0 |
| METISUSDT     |         18721 | 2024-03-11 16:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           7 |                           0 |                0 |
| SAGAUSDT      |         18041 | 2024-04-09 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           7 |                           0 |                0 |
| BANANAUSDT    |         14977 | 2024-08-14 16:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           7 |                           0 |                0 |
| 1000BONKUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000FLOKIUSDT |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000LUNCUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000PEPEUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000RATSUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000SATSUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000SHIBUSDT  |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1000XECUSDT   |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| 1INCHUSDT     |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| AAVEUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ACEUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ACHUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ADAUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| AGLDUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ALGOUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ALICEUSDT     |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ANKRUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| APEUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| API3USDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| APTUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ARBUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ARKMUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ARKUSDT       |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ARPAUSDT      |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |
| ARUSDT        |         20424 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |           0 |                           0 |                0 |

## Boundary

```text
raw data remains on company machine
local acceptance covers silver aggregates and company manifests only
May remains stress-only
no alpha proof, large search, shadow, paper, or live authorization
```
