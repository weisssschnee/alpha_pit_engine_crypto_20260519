# CRYPTO A7AP-1 Cross-Exchange Field Smoke

Generated: 2026-05-27T00:50:13Z

## Decision

```text
PASS_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_DIAGNOSTIC_ONLY
```

This is a small diagnostic IC/spread smoke on the short OKX/Binance overlap. It is not a tradable replay and cannot be alpha proof.

## Summary

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_broad_search": false,
  "authorizes_longer_overlap_or_forward_collection_design": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_DIAGNOSTIC_ONLY",
  "diagnostic_clue_count": 0,
  "executes_search": false,
  "executes_small_field_smoke": true,
  "executes_tradable_replay": false,
  "fields_tested": 8,
  "generated_at": "2026-05-27T00:50:13Z",
  "input_gold_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\okx_binance_cross_exchange_1h_30d_v1_20260527",
  "price_scale_quarantine_applied": true,
  "price_scale_quarantine_symbols": [
    "1000BONKUSDT",
    "1000FLOKIUSDT",
    "1000PEPEUSDT",
    "1000SHIBUSDT"
  ],
  "rows": 21933,
  "symbols": 214,
  "timestamp_max": "2026-04-30 23:00:00+00:00",
  "timestamp_min": "2026-04-26 17:00:00+00:00",
  "unique_hours": 103,
  "warnings": [
    "Only 103 hourly timestamps are available in the overlap",
    "Funding fields are sparse on Binance side",
    "IC/spread diagnostics are not executable PnL"
  ]
}
```

## Signal Decisions

| signal_name                      | field_family   | best_horizon   |   best_mean_ic |   best_ic_tstat |   best_mean_decile_spread |   min_dates_across_horizons | decision                                          |
|:---------------------------------|:---------------|:---------------|---------------:|----------------:|--------------------------:|----------------------------:|:--------------------------------------------------|
| funding_spread_okx_minus_binance | funding        | 4h             |      0.0223294 |         1.4124  |               0.00152472  |                          22 | HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC |
| funding_spread_binance_minus_okx | funding        | 4h             |     -0.0223294 |        -1.4124  |              -0.00152472  |                          22 | HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC |
| okx_internal_basis               | basis          | 12h            |      0.0277168 |         3.17675 |               0.00261812  |                          91 | NO_DIAGNOSTIC_CLUE                                |
| mark_basis_okx_minus_binance     | basis          | 1h             |      0.0258143 |         3.11034 |               0.000472457 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| binance_internal_basis           | basis          | 12h            |      0.0231763 |         2.8008  |               0.00181801  |                          91 | NO_DIAGNOSTIC_CLUE                                |
| index_spread_binance_minus_okx   | index_spread   | 12h            |      0.0089812 |         1.20029 |               0.000239296 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| index_spread_okx_minus_binance   | index_spread   | 12h            |     -0.0089812 |        -1.20029 |              -0.000239296 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| mark_basis_binance_minus_okx     | basis          | 1h             |     -0.0258143 |        -3.11034 |              -0.000472457 |                          91 | NO_DIAGNOSTIC_CLUE                                |

## Metrics

| signal_name                      | field_family   | source_column                         |   direction | label_horizon   |   valid_rows |   valid_row_share |   n_dates |   avg_n_obs |     mean_ic |   ic_tstat |   positive_ic_rate |   mean_decile_spread |   decile_spread_tstat |   positive_spread_rate |
|:---------------------------------|:---------------|:--------------------------------------|------------:|:----------------|-------------:|------------------:|----------:|------------:|------------:|-----------:|-------------------:|---------------------:|----------------------:|-----------------------:|
| okx_internal_basis               | basis          | okx_internal_mark_index_basis_bps     |           1 | 12h             |        21875 |          0.997356 |        91 |     212.165 |  0.0277168  |   3.17675  |           0.692308 |          0.00261812  |              2.50424  |               0.582418 |
| mark_basis_okx_minus_binance     | basis          | mark_basis_bps_okx_minus_binance      |           1 | 1h              |        21907 |          0.998815 |       102 |     212.676 |  0.0258143  |   3.11034  |           0.588235 |          0.000472457 |              1.06415  |               0.588235 |
| mark_basis_binance_minus_okx     | basis          | mark_basis_bps_okx_minus_binance      |          -1 | 1h              |        21907 |          0.998815 |       102 |     212.676 | -0.0258143  |  -3.11034  |           0.411765 |         -0.000472457 |             -1.06415  |               0.411765 |
| mark_basis_okx_minus_binance     | basis          | mark_basis_bps_okx_minus_binance      |           1 | 4h              |        21907 |          0.998815 |        99 |     212.636 |  0.0238945  |   2.73595  |           0.59596  |          0.000763187 |              1.20424  |               0.525253 |
| mark_basis_binance_minus_okx     | basis          | mark_basis_bps_okx_minus_binance      |          -1 | 4h              |        21907 |          0.998815 |        99 |     212.636 | -0.0238945  |  -2.73595  |           0.40404  |         -0.000763187 |             -1.20424  |               0.474747 |
| binance_internal_basis           | basis          | binance_internal_mark_index_basis_bps |           1 | 12h             |        21933 |          1        |        91 |     212.802 |  0.0231763  |   2.8008   |           0.582418 |          0.00181801  |              1.94941  |               0.56044  |
| funding_spread_binance_minus_okx | funding        | funding_spread_okx_minus_binance      |          -1 | 4h              |         4436 |          0.202252 |        24 |     178.833 | -0.0223294  |  -1.4124   |           0.375    |         -0.00152472  |             -1.01103  |               0.458333 |
| funding_spread_okx_minus_binance | funding        | funding_spread_okx_minus_binance      |           1 | 4h              |         4436 |          0.202252 |        24 |     178.833 |  0.0223294  |   1.4124   |           0.625    |          0.00152472  |              1.01103  |               0.541667 |
| binance_internal_basis           | basis          | binance_internal_mark_index_basis_bps |           1 | 1h              |        21933 |          1        |       102 |     212.931 | -0.0213863  |  -2.42611  |           0.411765 |          8.17377e-05 |              0.1889   |               0.5      |
| funding_spread_okx_minus_binance | funding        | funding_spread_okx_minus_binance      |           1 | 12h             |         4436 |          0.202252 |        22 |     178.818 | -0.0199545  |  -1.25204  |           0.409091 |          0.00107641  |              0.402752 |               0.454545 |
| funding_spread_binance_minus_okx | funding        | funding_spread_okx_minus_binance      |          -1 | 12h             |         4436 |          0.202252 |        22 |     178.818 |  0.0199545  |   1.25204  |           0.590909 |         -0.00107641  |             -0.402752 |               0.545455 |
| index_spread_okx_minus_binance   | index_spread   | index_spread_bps_okx_minus_binance    |           1 | 12h             |        21901 |          0.998541 |        91 |     212.451 | -0.0089812  |  -1.20029  |           0.450549 |         -0.000239296 |             -0.23155  |               0.527473 |
| index_spread_binance_minus_okx   | index_spread   | index_spread_bps_okx_minus_binance    |          -1 | 12h             |        21901 |          0.998541 |        91 |     212.451 |  0.0089812  |   1.20029  |           0.549451 |          0.000239296 |              0.23155  |               0.472527 |
| okx_internal_basis               | basis          | okx_internal_mark_index_basis_bps     |           1 | 4h              |        21875 |          0.997356 |        99 |     212.313 |  0.0080258  |   0.935856 |           0.555556 |          0.00075461  |              1.06019  |               0.555556 |
| mark_basis_binance_minus_okx     | basis          | mark_basis_bps_okx_minus_binance      |          -1 | 12h             |        21907 |          0.998815 |        91 |     212.516 | -0.00633781 |  -0.603239 |           0.483516 |         -0.00129251  |             -1.20361  |               0.505495 |
| mark_basis_okx_minus_binance     | basis          | mark_basis_bps_okx_minus_binance      |           1 | 12h             |        21907 |          0.998815 |        91 |     212.516 |  0.00633781 |   0.603239 |           0.516484 |          0.00129251  |              1.20361  |               0.494505 |
| okx_internal_basis               | basis          | okx_internal_mark_index_basis_bps     |           1 | 1h              |        21875 |          0.997356 |       102 |     212.363 | -0.00524896 |  -0.562926 |           0.421569 |          0.000100341 |              0.219384 |               0.490196 |
| index_spread_okx_minus_binance   | index_spread   | index_spread_bps_okx_minus_binance    |           1 | 4h              |        21901 |          0.998541 |        99 |     212.576 |  0.00520994 |   0.716795 |           0.505051 |          0.000414369 |              0.646333 |               0.545455 |
| index_spread_binance_minus_okx   | index_spread   | index_spread_bps_okx_minus_binance    |          -1 | 4h              |        21901 |          0.998541 |        99 |     212.576 | -0.00520994 |  -0.716795 |           0.494949 |         -0.000414369 |             -0.646333 |               0.454545 |
| binance_internal_basis           | basis          | binance_internal_mark_index_basis_bps |           1 | 4h              |        21933 |          1        |        99 |     212.899 | -0.00491136 |  -0.575163 |           0.505051 |          0.000291764 |              0.450141 |               0.525253 |
| funding_spread_binance_minus_okx | funding        | funding_spread_okx_minus_binance      |          -1 | 1h              |         4436 |          0.202252 |        25 |     177.44  |  0.00441331 |   0.293794 |           0.48     |         -0.000261594 |             -0.295604 |               0.48     |
| funding_spread_okx_minus_binance | funding        | funding_spread_okx_minus_binance      |           1 | 1h              |         4436 |          0.202252 |        25 |     177.44  | -0.00441331 |  -0.293794 |           0.52     |          0.000261594 |              0.295604 |               0.52     |
| index_spread_okx_minus_binance   | index_spread   | index_spread_bps_okx_minus_binance    |           1 | 1h              |        21901 |          0.998541 |       102 |     212.618 |  0.00340404 |   0.51021  |           0.529412 |          0.000225383 |              0.565266 |               0.558824 |
| index_spread_binance_minus_okx   | index_spread   | index_spread_bps_okx_minus_binance    |          -1 | 1h              |        21901 |          0.998541 |       102 |     212.618 | -0.00340404 |  -0.51021  |           0.470588 |         -0.000225383 |             -0.565266 |               0.441176 |

## Boundary

```text
AUTHORIZED NEXT:
  Use high-signal fields as diagnostic candidates for longer overlap collection or future forward telemetry.

NOT AUTHORIZED:
  historical alpha proof
  broad formula search
  shadow / paper / live

CAVEAT:
  The overlap window is only 103 hourly timestamps, ending 2026-04-30.
```
