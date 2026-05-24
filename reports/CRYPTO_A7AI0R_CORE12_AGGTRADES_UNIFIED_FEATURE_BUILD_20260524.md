# CRYPTO A7AI-0R Core12 aggTrades Unified Feature Build

Generated: 2026-05-24T05:36:57Z

## Decision

```text
PASS_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURES_READY
```

This stage materializes a unified core12 aggTrades feature layer from the accepted raw enhanced agg fields. It does not run replay and does not run search.

## Summary

```json
{
  "columns": 87,
  "decision": "PASS_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURES_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-24T05:36:57Z",
  "input_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet",
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ai0r_core12_aggtrades_unified_feature_build",
  "output_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core12_aggtrades_unified_features_v1_20260524.parquet",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURE_BUILD_20260524.md",
  "rows": 251028,
  "symbols": 12,
  "timestamp_max": "2026-05-22 00:00:00+00:00",
  "timestamp_min": "2024-01-01 00:00:00+00:00"
}
```

## Authorization

```json
{
  "authorizes_a7ai1_small_controlled_unified_agg_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AI0R_CORE12_AGGTRADES_UNIFIED_FEATURES_READY",
  "may_policy": "May stress-only and core3-current-month caveated; do not rank/tune on May",
  "warnings": [
    "May 2026 agg coverage remains core3 current-month caveated; not valid as full core12 May history",
    "This build creates experimental features from accepted raw agg fields; it is not alpha evidence"
  ]
}
```

## Split Coverage

| split                    |   rows |   symbols |   agg_available_rows |   agg_available_symbols |   agg_available_rate | may_allowed_for_ranking   |
|:-------------------------|-------:|----------:|---------------------:|------------------------:|---------------------:|:--------------------------|
| train_2024               | 105288 |        12 |               105288 |                      12 |                 1    | True                      |
| validation_2025H1        |  52128 |        12 |                52128 |                      12 |                 1    | True                      |
| recent_2025H2_2026Apr    |  87552 |        12 |                87552 |                      12 |                 1    | True                      |
| may_2026_stress_caveated |   5760 |        12 |                 1440 |                       3 |                 0.25 | False                     |

## Feature Catalog Summary

| source_class         |   count |
|:---------------------|--------:|
| base_context         |       7 |
| cross_symbol_derived |      10 |
| derived              |      12 |
| key                  |       2 |
| past_rolling_derived |      28 |
| raw_aggtrades        |      28 |

## Bounded Feature Audit

| field_name                            |   lower |   upper |   violation_count |
|:--------------------------------------|--------:|--------:|------------------:|
| agg_volume_imbalance                  |      -1 |       1 |                 0 |
| agg_large_notional_ratio_100k_plus    |       0 |       1 |                 0 |
| agg_flow_imbalance_notional           |      -1 |       1 |                 0 |
| agg_buy_notional_share                |       0 |       1 |                 0 |
| agg_sell_notional_share               |       0 |       1 |                 0 |
| agg_flow_imbalance_notional_4h        |      -1 |       1 |                 0 |
| agg_large_notional_share_4h           |       0 |       1 |                 0 |
| agg_flow_imbalance_notional_24h       |      -1 |       1 |                 0 |
| agg_large_notional_share_24h          |       0 |       1 |                 0 |
| agg_cross_symbol_notional_share       |       0 |       1 |                 0 |
| agg_cross_symbol_signed_flow_share    |      -1 |       1 |                 0 |
| agg_cross_symbol_large_notional_share |       0 |       1 |                 0 |

## Numeric Quality Worst Missing

| field_name                             |   non_null_rate |   nan_count |   inf_count |              min |              max |
|:---------------------------------------|----------------:|------------:|------------:|-----------------:|-----------------:|
| agg_notional_shock_24h_mad             |        0.980926 |        4788 |           0 |     -6.00242     |    526.046       |
| premium_index_change_24h               |        0.981165 |        4728 |           0 |     -0.0112549   |      0.0115765   |
| agg_signed_flow_z_24h                  |        0.981261 |        4704 |           0 |     -4.76483     |      4.7756      |
| agg_signed_flow_z_24h_cs_rank          |        0.981261 |        4704 |           0 |      0.0833333   |      1           |
| agg_signed_flow_z_24h_cs_zscore        |        0.981261 |        4704 |           0 |     -3.23875     |      3.26348     |
| agg_notional_accel_4h_vs_24h_cs_zscore |        0.981404 |        4668 |           0 |     -3.06509     |      3.29943     |
| agg_close_to_open_bps_sum_4h           |        0.981452 |        4656 |           0 |  -2497.75        |   5182.83        |
| agg_large_notional_sum_4h              |        0.981452 |        4656 |           0 |      0           |      1.55339e+10 |
| agg_large_notional_share_4h            |        0.981452 |        4656 |           0 |      0           |      0.8477      |
| agg_flow_imbalance_notional_4h         |        0.981452 |        4656 |           0 |     -0.578054    |      0.501687    |
| agg_avg_trade_notional_4h              |        0.981452 |        4656 |           0 |    290.659       |  45121.2         |
| agg_quantity_sum_4h                    |        0.981452 |        4656 |           0 |   1985.13        |      2.16545e+10 |
| agg_trade_count_sum_4h                 |        0.981452 |        4656 |           0 |   3293           |      4.32371e+06 |
| agg_notional_accel_4h_vs_24h           |        0.981452 |        4656 |           0 |     -0.833992    |      5           |
| agg_signed_notional_sum_4h             |        0.981452 |        4656 |           0 |     -2.1946e+09  |      1.40001e+09 |
| agg_notional_sum_4h                    |        0.981452 |        4656 |           0 |      2.72407e+06 |      2.86757e+10 |
| agg_flow_accel_4h_vs_24h               |        0.981452 |        4656 |           0 |     -0.414812    |      0.396641    |
| agg_flow_minus_btcusdt_4h              |        0.981452 |        4656 |           0 |     -0.671611    |      0.485427    |
| agg_notional_accel_4h_vs_24h_cs_rank   |        0.981452 |        4656 |           0 |      0.0833333   |      1           |
| agg_flow_minus_ethusdt_4h              |        0.981452 |        4656 |           0 |     -0.572651    |      0.463306    |
| agg_price_range_bps_max_4h             |        0.981452 |        4656 |           0 |      9.71168     |  11815.5         |
| agg_sell_vwap                          |        0.981596 |        4620 |           0 |      0.075209    | 125641           |
| agg_underlying_trade_count             |        0.981596 |        4620 |           0 |   2077           |      4.36244e+06 |
| agg_trade_count                        |        0.981596 |        4620 |           0 |    648           |      2.46234e+06 |
| agg_signed_aggressor_notional          |        0.981596 |        4620 |           0 |     -1.08849e+09 |      1.17939e+09 |
| agg_avg_agg_trade_notional             |        0.981596 |        4620 |           0 |    149.732       | 119451           |
| agg_avg_underlying_trade_notional      |        0.981596 |        4620 |           0 |     27.5816      |  21077.5         |
| agg_buy_notional                       |        0.981596 |        4620 |           0 | 222927           |      7.23126e+09 |
| agg_notional                           |        0.981596 |        4620 |           0 | 490008           |      1.44809e+10 |
| agg_quantity                           |        0.981596 |        4620 |           0 |    358.475       |      8.99081e+09 |
| agg_sell_notional                      |        0.981596 |        4620 |           0 | 217592           |      7.71394e+09 |
| agg_signed_aggressor_quantity          |        0.981596 |        4620 |           0 |     -7.29463e+08 |      3.91333e+08 |
| agg_sell_notional_share                |        0.981596 |        4620 |           0 |      0.149397    |      0.837843    |
| agg_large_trade_count_ratio_100k_plus  |        0.981596 |        4620 |           0 |      0           |      0.091374    |
| agg_large_notional_ratio_100k_plus     |        0.981596 |        4620 |           0 |      0           |      0.938963    |
| agg_vwap_close_bps                     |        0.981596 |        4620 |           0 |  -1502.29        |   1173.21        |
| agg_buy_sell_vwap_spread_bps           |        0.981596 |        4620 |           0 |   -258.409       |    152.777       |
| agg_avg_underlying_trades_per_agg      |        0.981596 |        4620 |           0 |      1.51064     |     28.0995      |
| agg_buy_notional_share                 |        0.981596 |        4620 |           0 |      0.162157    |      0.850603    |
| agg_large_trade_count_100k_plus        |        0.981596 |        4620 |           0 |      0           |  29689           |

## Boundary

- Use this unified panel for A7AI-1 instead of recomputing rolling/cross-symbol agg fields inside the smoke runner.
- All rolling transforms are past/current-hour only and become available after the 1h bucket closes.
- May 2026 agg coverage is caveated and cannot enter ranking/tuning.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
