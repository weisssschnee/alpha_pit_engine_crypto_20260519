# CRYPTO A7AP-2 Multiplier Price-Scale Repair

Generated: 2026-05-27T01:14:26Z

## Decision

```text
PASS_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_DIAGNOSTIC_READY
```

This stage repairs OKX/Binance price-scale comparison fields for multiplier contracts by converting OKX mark/index prices to the Binance contract unit before computing cross-exchange basis. It does not alter raw source fields.

## Summary

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_broad_search": false,
  "authorizes_diagnostic_use_repaired_fields": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_DIAGNOSTIC_READY",
  "diagnostic_clue_count": 0,
  "executes_price_scale_repair": true,
  "executes_search": false,
  "executes_small_field_smoke": true,
  "executes_tradable_replay": false,
  "generated_at": "2026-05-27T01:14:26Z",
  "input_gold_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\okx_binance_cross_exchange_1h_30d_v1_20260527",
  "output_gold_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\okx_binance_cross_exchange_1h_30d_v1_price_scale_repaired_20260527",
  "post_repair_extreme_symbol_count": 0,
  "post_repair_extreme_symbols": [],
  "price_scale_repair_symbol_count": 4,
  "price_scale_repair_symbols": [
    "1000BONKUSDT",
    "1000FLOKIUSDT",
    "1000PEPEUSDT",
    "1000SHIBUSDT"
  ],
  "rows": 22345,
  "symbols": 218,
  "taxonomy": "G:\\AlphaFactory_CryptoData\\gold\\metadata\\binance_universe498_contract_meme_taxonomy_v1_20260527.csv",
  "timestamp_max": "2026-04-30 23:00:00+00:00",
  "timestamp_min": "2026-04-26 17:00:00+00:00",
  "unique_hours": 103,
  "warnings": [
    "Raw OKX/Binance fields are preserved; repaired fields use contract-unit OKX prices",
    "Overlap remains only 103 hours",
    "Field smoke is diagnostic only, not executable PnL"
  ]
}
```

## Repair Audit

| symbol        |   rows |   contract_unit_multiplier | price_scale_repair_applied   |   pre_mark_extreme_rows |   post_mark_extreme_rows |   pre_index_extreme_rows |   post_index_extreme_rows |   pre_mark_min |   pre_mark_max |   post_mark_min |   post_mark_max |   pre_index_min |   pre_index_max |   post_index_min |   post_index_max |
|:--------------|-------:|---------------------------:|:-----------------------------|------------------------:|-------------------------:|-------------------------:|--------------------------:|---------------:|---------------:|----------------:|----------------:|----------------:|----------------:|-----------------:|-----------------:|
| 1000BONKUSDT  |    103 |                       1000 | True                         |                     103 |                        0 |                      103 |                         0 |       -9990.01 |       -9989.99 |        -12.7045 |         9.75127 |        -9990.01 |        -9989.99 |         -5.66615 |          5.64897 |
| 1000FLOKIUSDT |    103 |                       1000 | True                         |                     103 |                        0 |                      103 |                         0 |       -9990.01 |       -9990    |        -12.6647 |         3.12891 |        -9990.01 |        -9990    |         -8.36582 |          3.7637  |
| 1000PEPEUSDT  |    103 |                       1000 | True                         |                     103 |                        0 |                      103 |                         0 |       -9990.02 |       -9989.99 |        -15.5399 |        10.1185  |        -9990.01 |        -9989.99 |         -9.54894 |         13.7785  |
| 1000SHIBUSDT  |    103 |                       1000 | True                         |                     103 |                        0 |                      103 |                         0 |       -9990.02 |       -9990    |        -24.4228 |         3.35244 |        -9990.02 |        -9990    |        -16.0556  |          3.1026  |

## Signal Decisions After Repair

| signal_name                                  | field_family   | best_horizon   |   best_mean_ic |   best_ic_tstat |   best_mean_decile_spread |   min_dates_across_horizons | decision                                          |
|:---------------------------------------------|:---------------|:---------------|---------------:|----------------:|--------------------------:|----------------------------:|:--------------------------------------------------|
| binance_internal_basis                       | basis          | 12h            |     0.0262599  |         3.14951 |               0.00183235  |                          91 | NO_DIAGNOSTIC_CLUE                                |
| funding_spread_binance_minus_okx             | funding        | 4h             |    -0.0234775  |        -1.44165 |              -0.00143037  |                          22 | HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC |
| funding_spread_okx_minus_binance             | funding        | 4h             |     0.0234775  |         1.44165 |               0.00143037  |                          22 | HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC |
| index_spread_binance_minus_okx_contract_unit | index_spread   | 12h            |     0.00891506 |         1.20103 |               0.000135056 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| index_spread_okx_contract_unit_minus_binance | index_spread   | 12h            |    -0.00891506 |        -1.20103 |              -0.000135056 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| mark_basis_binance_minus_okx_contract_unit   | basis          | 1h             |    -0.0254347  |        -3.04655 |              -0.000485988 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| mark_basis_okx_contract_unit_minus_binance   | basis          | 1h             |     0.0254347  |         3.04655 |               0.000485988 |                          91 | NO_DIAGNOSTIC_CLUE                                |
| okx_internal_basis                           | basis          | 12h            |     0.0286509  |         3.26333 |               0.00259363  |                          91 | NO_DIAGNOSTIC_CLUE                                |

## Field Smoke Metrics After Repair

| signal_name                                  | field_family   | source_column                                    |   direction | label_horizon   |   valid_rows |   valid_row_share |   n_dates |   avg_n_obs |     mean_ic |   ic_tstat |   positive_ic_rate |   mean_decile_spread |   decile_spread_tstat |   positive_spread_rate |
|:---------------------------------------------|:---------------|:-------------------------------------------------|------------:|:----------------|-------------:|------------------:|----------:|------------:|------------:|-----------:|-------------------:|---------------------:|----------------------:|-----------------------:|
| okx_internal_basis                           | basis          | okx_internal_mark_index_basis_bps                |           1 | 12h             |        22287 |          0.997404 |        91 |     216.165 |  0.0286509  |   3.26333  |           0.692308 |          0.00259363  |              2.47207  |               0.582418 |
| binance_internal_basis                       | basis          | binance_internal_mark_index_basis_bps            |           1 | 12h             |        22345 |          1        |        91 |     216.802 |  0.0262599  |   3.14951  |           0.626374 |          0.00183235  |              1.96165  |               0.538462 |
| mark_basis_okx_contract_unit_minus_binance   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |           1 | 1h              |        22319 |          0.998836 |       102 |     216.676 |  0.0254347  |   3.04655  |           0.588235 |          0.000485988 |              1.09439  |               0.578431 |
| mark_basis_binance_minus_okx_contract_unit   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |          -1 | 1h              |        22319 |          0.998836 |       102 |     216.676 | -0.0254347  |  -3.04655  |           0.411765 |         -0.000485988 |             -1.09439  |               0.421569 |
| funding_spread_binance_minus_okx             | funding        | funding_spread_okx_minus_binance                 |          -1 | 4h              |         4496 |          0.201208 |        24 |     181.292 | -0.0234775  |  -1.44165  |           0.375    |         -0.00143037  |             -0.95933  |               0.458333 |
| funding_spread_okx_minus_binance             | funding        | funding_spread_okx_minus_binance                 |           1 | 4h              |         4496 |          0.201208 |        24 |     181.292 |  0.0234775  |   1.44165  |           0.625    |          0.00143037  |              0.95933  |               0.541667 |
| mark_basis_okx_contract_unit_minus_binance   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |           1 | 4h              |        22319 |          0.998836 |        99 |     216.636 |  0.021426   |   2.42878  |           0.59596  |          0.000679168 |              1.05878  |               0.525253 |
| mark_basis_binance_minus_okx_contract_unit   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |          -1 | 4h              |        22319 |          0.998836 |        99 |     216.636 | -0.021426   |  -2.42878  |           0.40404  |         -0.000679168 |             -1.05878  |               0.474747 |
| binance_internal_basis                       | basis          | binance_internal_mark_index_basis_bps            |           1 | 1h              |        22345 |          1        |       102 |     216.931 | -0.0211832  |  -2.43256  |           0.401961 |          5.03962e-05 |              0.117348 |               0.5      |
| funding_spread_okx_minus_binance             | funding        | funding_spread_okx_minus_binance                 |           1 | 12h             |         4496 |          0.201208 |        22 |     181.273 | -0.0203233  |  -1.31284  |           0.409091 |          0.000875938 |              0.32773  |               0.409091 |
| funding_spread_binance_minus_okx             | funding        | funding_spread_okx_minus_binance                 |          -1 | 12h             |         4496 |          0.201208 |        22 |     181.273 |  0.0203233  |   1.31284  |           0.590909 |         -0.000875938 |             -0.32773  |               0.590909 |
| index_spread_okx_contract_unit_minus_binance | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |           1 | 12h             |        22313 |          0.998568 |        91 |     216.451 | -0.00891506 |  -1.20103  |           0.428571 |         -0.000135056 |             -0.130802 |               0.549451 |
| index_spread_binance_minus_okx_contract_unit | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |          -1 | 12h             |        22313 |          0.998568 |        91 |     216.451 |  0.00891506 |   1.20103  |           0.571429 |          0.000135056 |              0.130802 |               0.450549 |
| okx_internal_basis                           | basis          | okx_internal_mark_index_basis_bps                |           1 | 4h              |        22287 |          0.997404 |        99 |     216.313 |  0.00753521 |   0.882499 |           0.535354 |          0.000786314 |              1.10911  |               0.555556 |
| okx_internal_basis                           | basis          | okx_internal_mark_index_basis_bps                |           1 | 1h              |        22287 |          0.997404 |       102 |     216.363 | -0.00519009 |  -0.565603 |           0.421569 |          0.000109021 |              0.237851 |               0.490196 |
| index_spread_okx_contract_unit_minus_binance | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |           1 | 4h              |        22313 |          0.998568 |        99 |     216.576 |  0.00408259 |   0.56116  |           0.525253 |          0.000452408 |              0.70272  |               0.545455 |
| index_spread_binance_minus_okx_contract_unit | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |          -1 | 4h              |        22313 |          0.998568 |        99 |     216.576 | -0.00408259 |  -0.56116  |           0.474747 |         -0.000452408 |             -0.70272  |               0.454545 |
| funding_spread_okx_minus_binance             | funding        | funding_spread_okx_minus_binance                 |           1 | 1h              |         4496 |          0.201208 |        25 |     179.84  | -0.00403501 |  -0.272404 |           0.48     |          0.000328319 |              0.362009 |               0.52     |
| funding_spread_binance_minus_okx             | funding        | funding_spread_okx_minus_binance                 |          -1 | 1h              |         4496 |          0.201208 |        25 |     179.84  |  0.00403501 |   0.272404 |           0.52     |         -0.000328319 |             -0.362009 |               0.48     |
| binance_internal_basis                       | basis          | binance_internal_mark_index_basis_bps            |           1 | 4h              |        22345 |          1        |        99 |     216.899 | -0.00391924 |  -0.450933 |           0.494949 |          0.000314724 |              0.487204 |               0.535354 |
| index_spread_okx_contract_unit_minus_binance | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |           1 | 1h              |        22313 |          0.998568 |       102 |     216.618 |  0.0033755  |   0.508001 |           0.539216 |          0.000225289 |              0.566267 |               0.558824 |
| index_spread_binance_minus_okx_contract_unit | index_spread   | index_spread_bps_okx_contract_unit_minus_binance |          -1 | 1h              |        22313 |          0.998568 |       102 |     216.618 | -0.0033755  |  -0.508001 |           0.460784 |         -0.000225289 |             -0.566267 |               0.441176 |
| mark_basis_binance_minus_okx_contract_unit   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |          -1 | 12h             |        22319 |          0.998836 |        91 |     216.516 | -0.00298137 |  -0.284172 |           0.505495 |         -0.00119055  |             -1.10531  |               0.494505 |
| mark_basis_okx_contract_unit_minus_binance   | basis          | mark_basis_bps_okx_contract_unit_minus_binance   |           1 | 12h             |        22319 |          0.998836 |        91 |     216.516 |  0.00298137 |   0.284172 |           0.494505 |          0.00119055  |              1.10531  |               0.505495 |

## Boundary

```text
AUTHORIZED NEXT:
  use repaired contract-unit fields for short-window diagnostic only
  continue longer overlap / forward telemetry design

NOT AUTHORIZED:
  historical alpha proof
  broad formula search
  shadow / paper / live

CAVEAT:
  overlap remains only 103 hourly timestamps.
```
