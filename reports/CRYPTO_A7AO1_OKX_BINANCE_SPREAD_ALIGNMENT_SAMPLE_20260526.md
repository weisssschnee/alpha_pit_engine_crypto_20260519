# CRYPTO A7AO-1 OKX-Binance Spread Alignment Sample

Generated: 2026-05-26T15:50:48Z

## Decision

```text
PASS_A7AO_OKX_LIGHT_SAMPLE_ACCEPTED_FOR_TELEMETRY_AND_SPREAD_AUDIT
```

This stage aligns OKX recent mark/index/funding observations with the accepted Binance universe498 replay base where symbols and timestamps overlap.

## Output

```text
G:\AlphaFactory_CryptoData\gold\features\okx_binance_cross_exchange_light_top50_30d_v1_20260526\okx_binance_mark_index_funding_spread_sample.parquet
```

## Alignment Summary

| symbol    |   aligned_rows | timestamp_min             | timestamp_max             |   okx_funding_matched_rows |   basis_spread_bps_mean |   basis_spread_bps_abs_p95 |   mark_close_spread_bps_abs_p95 |   funding_spread_bps_mean |
|:----------|---------------:|:--------------------------|:--------------------------|---------------------------:|------------------------:|---------------------------:|--------------------------------:|--------------------------:|
| 1INCHUSDT |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |                2.035    |                   10.8105  |                        10.4712  |                 0.606624  |
| ADAUSDT   |             85 | 2026-04-27 11:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         10 |               -2.73191  |                    7.53148 |                         8.21564 |                 0.0547174 |
| BTCUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -0.343994 |                    1.98248 |                         1.8526  |                -0.106061  |
| CHZUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                          0 |               -1.28236  |                    7.62331 |                         7.08908 |               nan         |
| CRVUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -3.56979  |                   18.4047  |                        17.744   |                -0.209373  |
| EGLDUSDT  |             85 | 2026-04-27 11:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         10 |               -1.20759  |                   12.2724  |                         9.22895 |                -0.59887   |
| ENJUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         26 |                8.24413  |                   15.925   |                        12.6561  |                 1.32104   |
| GRTUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -5.44541  |                   13.1965  |                        11.9799  |                -0.871162  |
| ICXUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         26 |                1.50149  |                   18.7482  |                        15.8111  |                -0.615418  |
| KSMUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |                4.78402  |                   15.8022  |                         8.35876 |                 0.0409544 |
| LTCUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -1.72898  |                    3.97844 |                         5.00339 |                -0.0488145 |
| RSRUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -7.23164  |                   19.1694  |                        18.2776  |                -0.191195  |
| SNXUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -0.589084 |                   16.4045  |                         8.9923  |                -0.407845  |
| XRPUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         13 |               -6.96851  |                   10.6294  |                        10.8147  |                 0.189987  |
| ZRXUSDT   |            105 | 2026-04-26 15:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                         26 |                6.83041  |                   23.0364  |                        12.6374  |                -0.48714   |

## Authorization

```text
AUTHORIZED:
  cross-exchange spread diagnostic
  forward telemetry design

NOT AUTHORIZED:
  historical alpha proof
  large search
  shadow / paper / live
```
