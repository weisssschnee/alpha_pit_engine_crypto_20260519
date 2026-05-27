# CRYPTO A7AL-0 Universe498 Replay Acceptance

Generated: 2026-05-27T03:47:59Z

## Decision

```text
PASS_A7AL_UNIVERSE498_REPLAY_BASE_ACCEPTED
```

This audit validates the top498 1h replay base. It does not run replay and does not run search.

## Summary

```json
{
  "authorizes_a7ak_min_small_controlled_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "columns": 54,
  "decision": "PASS_A7AL_UNIVERSE498_REPLAY_BASE_ACCEPTED",
  "duplicate_timestamp_count": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-27T03:47:59Z",
  "hold_symbols": 12,
  "inf_cell_count": 0,
  "listing_aware_symbols": 305,
  "negative_non_allowed_count": 0,
  "panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v1_20260525",
  "rows": 6650298,
  "source_report": "G:\\AlphaFactory_CryptoData\\reports\\BINANCE_UNIVERSE498_REPLAY_1H_V1_20260525.json",
  "source_report_rows": 6650298,
  "source_report_symbols": 498,
  "strict_full_history_symbols": 181,
  "symbols": 498,
  "warnings": [
    "May 2026 rows are not present; May cannot be used from this panel",
    "Universe498 membership is current/listing-aware and is not by itself survivorship-safe proof",
    "Panel execution_time equals feature_available_time; experiments should use field-native latency audit and wrong-lag controls",
    "No aggTrades/book/liquidation/cross-exchange fields in this replay base"
  ]
}
```

## Dataset Summary

| dataset                          |   symbols |   rows_manifest |   rows_actual |   duplicate_timestamp_count |   gap_hours |   inf_cell_count |   negative_non_allowed_count |   strict_full_history_symbols |   listing_aware_symbols |
|:---------------------------------|----------:|----------------:|--------------:|----------------------------:|------------:|-----------------:|-----------------------------:|------------------------------:|------------------------:|
| binance_universe498_replay_1h_v1 |       498 |         6650298 |       6650298 |                           0 |         103 |                0 |                            0 |                           181 |                     305 |

## Split Coverage

| split                       |    rows |   symbols_with_rows |   strict_full_history_symbols | may_allowed_for_ranking   |
|:----------------------------|--------:|--------------------:|------------------------------:|:--------------------------|
| train_2024                  | 1880549 |                 276 |                           181 | True                      |
| validation_2025H1           | 1410769 |                 374 |                           181 | True                      |
| recent_2025H2_2026Apr       | 3358980 |                 498 |                           181 | True                      |
| may_2026_stress_unavailable |       0 |                   0 |                             0 | False                     |

## Search Eligibility x Liquidity Tier

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

## Worst Quality Rows

| symbol       | search_eligibility            | history_tier      | liquidity_tier   |   rows |   coverage_metrics |   coverage_market_funding |   gap_hours |   median_hourly_quote_volume |
|:-------------|:------------------------------|:------------------|:-----------------|-------:|-------------------:|--------------------------:|------------:|-----------------------------:|
| PUMPUSDT     | hold_quality_or_short_history | recent_only       | top20            |   7289 |           0.970366 |                  1        |           7 |                  6.67007e+06 |
| LITUSDT      | hold_quality_or_short_history | short_history     | top200           |   3607 |           0.853618 |                  1        |          17 |             861152           |
| CKBUSDT      | hold_quality_or_short_history | full_2024_2026apr | tail             |  20424 |           0.99951  |                  0.964747 |           0 |             302390           |
| ONTUSDT      | hold_quality_or_short_history | full_2024_2026apr | tail             |  20424 |           0.99951  |                  0.963572 |           0 |             250535           |
| USTCUSDT     | hold_quality_or_short_history | full_2024_2026apr | tail             |  20424 |           0.998384 |                  0.963572 |           0 |             228052           |
| AIAUSDT      | hold_quality_or_short_history | short_history     | tail             |   2869 |           0.84106  |                  1        |          11 |             171925           |
| CVXUSDT      | hold_quality_or_short_history | recent_only       | tail             |   7285 |           0.927522 |                  1        |          11 |              81431.8         |
| AERGOUSDT    | hold_quality_or_short_history | recent_only       | tail             |   9469 |           0.961981 |                  1        |          11 |              68132           |
| MAVIAUSDT    | hold_quality_or_short_history | recent_only       | tail             |  10207 |           0.941217 |                  1        |          17 |              59037.8         |
| CVCUSDT      | hold_quality_or_short_history | recent_only       | tail             |   8752 |           0.958867 |                  0.999886 |           8 |              45585.9         |
| SLPUSDT      | hold_quality_or_short_history | recent_only       | tail             |   7285 |           0.927522 |                  1        |          11 |              38716.9         |
| CTKUSDT      | hold_quality_or_short_history | recent_only       | tail             |   9470 |           0.926505 |                  0.999894 |          10 |              34489.3         |
| HYPEUSDT     | listing_aware                 | recent_only       | top20            |   8054 |           1        |                  1        |           0 |                  1.25021e+07 |
| FARTCOINUSDT | listing_aware                 | listed_by_2025H1  | top20            |  11910 |           1        |                  1        |           0 |                  9.79601e+06 |
| ENAUSDT      | listing_aware                 | listed_by_2025H1  | top20            |  18204 |           1        |                  1        |           0 |                  9.48008e+06 |
| TRUMPUSDT    | listing_aware                 | recent_only       | top20            |  11219 |           1        |                  1        |           0 |                  6.82121e+06 |
| ASTERUSDT    | listing_aware                 | short_history     | top20            |   5364 |           1        |                  1        |           0 |                  6.56166e+06 |
| RIVERUSDT    | listing_aware                 | short_history     | top50            |   4690 |           1        |                  1        |           0 |                  6.3781e+06  |
| TAOUSDT      | listing_aware                 | listed_by_2025H1  | top50            |  17986 |           1        |                  1        |           0 |                  4.11818e+06 |
| PENGUUSDT    | listing_aware                 | listed_by_2025H1  | top50            |  11984 |           1        |                  1        |           0 |                  4.0054e+06  |
| XPLUSDT      | listing_aware                 | short_history     | top50            |   6039 |           1        |                  1        |           0 |                  3.18244e+06 |
| VIRTUALUSDT  | listing_aware                 | listed_by_2025H1  | top50            |  12156 |           1        |                  1        |           0 |                  3.05867e+06 |
| WLFIUSDT     | listing_aware                 | short_history     | top50            |   6016 |           1        |                  1        |           0 |                  3.02331e+06 |
| NEIROUSDT    | listing_aware                 | listed_by_2025H1  | top50            |  14197 |           1        |                  1        |           0 |                  2.84305e+06 |
| PNUTUSDT     | listing_aware                 | listed_by_2025H1  | top50            |  12852 |           1        |                  1        |           0 |                  2.65728e+06 |
| ETHFIUSDT    | listing_aware                 | listed_by_2025H1  | top50            |  18561 |           1        |                  1        |           0 |                  2.48139e+06 |
| PAXGUSDT     | listing_aware                 | recent_only       | top50            |   9590 |           1        |                  1        |           0 |                  2.45477e+06 |
| TONUSDT      | listing_aware                 | listed_by_2025H1  | top100           |  18972 |           1        |                  1        |           0 |                  2.33175e+06 |
| POPCATUSDT   | listing_aware                 | listed_by_2025H1  | top100           |  14795 |           1        |                  1        |           0 |                  2.22302e+06 |
| EIGENUSDT    | listing_aware                 | listed_by_2025H1  | top100           |  13842 |           1        |                  1        |           0 |                  2.0069e+06  |
| BOMEUSDT     | listing_aware                 | listed_by_2025H1  | top100           |  18612 |           1        |                  1        |           0 |                  1.83719e+06 |
| BEATUSDT     | listing_aware                 | short_history     | top100           |   4068 |           1        |                  1        |           0 |                  1.57613e+06 |
| GIGGLEUSDT   | listing_aware                 | short_history     | top100           |   4887 |           1        |                  1        |           0 |                  1.39316e+06 |
| RENDERUSDT   | listing_aware                 | listed_by_2025H1  | top100           |  15446 |           1        |                  1        |           0 |                  1.36852e+06 |
| MOODENGUSDT  | listing_aware                 | listed_by_2025H1  | top100           |  13262 |           1        |                  1        |           0 |                  1.3464e+06  |
| TURBOUSDT    | listing_aware                 | listed_by_2025H1  | top100           |  16809 |           0.998632 |                  1        |           0 |                  1.31919e+06 |
| ZROUSDT      | listing_aware                 | listed_by_2025H1  | top100           |  16306 |           1        |                  1        |           0 |                  1.27582e+06 |
| SPXUSDT      | listing_aware                 | listed_by_2025H1  | top100           |  12156 |           1        |                  1        |           0 |                  1.20621e+06 |
| KITEUSDT     | listing_aware                 | short_history     | top100           |   4406 |           1        |                  1        |           0 |                  1.17491e+06 |
| BERAUSDT     | listing_aware                 | recent_only       | top100           |  10761 |           1        |                  1        |           0 |                  1.13039e+06 |

## Timing Boundary

```text
timestamp = 1h bucket start UTC
feature_available_time = timestamp + 1h
panel execution_time = timestamp + 1h
recommended replay execution_time = timestamp + 1h / next 1h bar open; fixed delay stress prohibited
May 2026 rows are not present in this panel and cannot be used for ranking or stress here
```
