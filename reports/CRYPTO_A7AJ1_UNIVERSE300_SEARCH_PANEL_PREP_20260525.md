# CRYPTO A7AJ-1 Universe300 Search Panel Prep

Generated: 2026-07-11T05:32:46Z

## Decision

```text
PASS_A7AJ_UNIVERSE500_SILVER_ACCEPTED_AND_SEARCH_PANEL_PREPARED
```

This stage materializes a partitioned top300 market+metrics panel and overlays the accepted core12 aggTrades unified features where available. It prepares the next controlled smoke path; it does not authorize direct formula search.

## Output Panel

```text
G:\AlphaFactory_CryptoData\gold\features\binance_universe300_market_metrics_agg_overlay_1h_v1_20260525
```

## Panel Summary

```json
{
  "authorizes_a7ak_small_field_family_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "output_panel_columns_sample": 124,
  "output_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe300_market_metrics_agg_overlay_1h_v1_20260525",
  "output_panel_rows": 5362049,
  "output_panel_symbols": 300
}
```

## Universe Tiers

| search_tier                          |   symbols |
|:-------------------------------------|----------:|
| top300_full_history_market_metrics   |       164 |
| listing_aware_market_metrics         |       124 |
| core12_full_history_with_agg_overlay |        12 |

## Split Coverage

| split                 |    rows |   symbols |   metrics_complete_5m_rate |   agg_overlay_available_rate | may_allowed_for_ranking   |
|:----------------------|--------:|----------:|---------------------------:|-----------------------------:|:--------------------------|
| may_2026_stress_only  |       0 |       300 |                 nan        |                  nan         | False                     |
| recent_2025H2_2026Apr | 2188800 |       300 |                   0.999792 |                    0.04      | True                      |
| train_2024            | 1880986 |       300 |                   0.99611  |                    0.0434288 | True                      |
| validation_2025H1     | 1292263 |       300 |                   0.999452 |                    0.04      | True                      |

## Feature Contract Summary

| source_class             |   fields |
|:-------------------------|---------:|
| core12_aggtrades_overlay |       79 |
| market_funding           |       23 |
| binance_metrics          |       14 |
| metadata                 |        5 |
| key                      |        2 |
| derived                  |        1 |

## Search Chain Boundary

```text
AUTHORIZED:
  A7AK1 small controlled field-family smoke on strict full-history subset

NOT AUTHORIZED:
  direct large formula search
  alpha proof
  shadow / paper / live

TIMING:
  timestamp = 1h bucket start UTC
  feature_available_time = timestamp + 1h
  minimum execution_time = timestamp + 1h / next 1h bar open
  fixed delay stress = prohibited

MAY:
  this panel has no May 2026 market/funding rows
  May stress requires a separate current/forward source
  stress-only; not ranking, tuning, selection, universe selection, or promotion
```
