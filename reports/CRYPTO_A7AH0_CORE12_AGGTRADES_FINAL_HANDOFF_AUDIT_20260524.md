# CRYPTO A7AH-0 Core12 aggTrades Final Handoff Audit

Generated: 2026-05-24T04:44:32Z

## Decision

```text
PASS_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_ACCEPTED
```

This stage validates the final core12 aggTrades handoff data. It does not run replay and does not run search.

## Summary

```json
{
  "core12_max_agg_coverage": 0.998804914192839,
  "core12_min_agg_coverage": 0.9758592666953487,
  "decision": "PASS_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_ACCEPTED",
  "duplicate_keys": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-24T04:44:32Z",
  "handoff_report": "G:\\AlphaFactory_CryptoData\\reports\\CRYPTO_CORE12_AGGTRADES_FINAL_HANDOFF_20260524.md",
  "non_core12_agg_rows": 0,
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ah0_core12_aggtrades_final_handoff_audit",
  "panel_columns": 654,
  "panel_file_size_bytes": 2736669923,
  "panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet",
  "panel_rows": 815818,
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_AUDIT_20260524.md",
  "symbols": 39,
  "timestamp_max": "2026-05-22 00:00:00+00:00",
  "timestamp_min": "2024-01-01 00:00:00+00:00"
}
```

## Authorization

```json
{
  "authorizes_a7ai0_core12_aggtrades_experiment_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AH0_CORE12_AGGTRADES_FINAL_HANDOFF_ACCEPTED",
  "may_policy": "2026-05 aggTrades monthly history is not claimed; any May agg coverage is caveated and cannot be ranking/tuning proof",
  "warnings": [
    "derived_agg_feature_fields_not_merged_into_final_panel_use_feature_root_or_rebuild_if_needed",
    "some_core12_symbols_have_2026_05_agg_rows; handoff says monthly May unavailable so treat May agg as forward/current-month caveat",
    "handoff_report_and_build_json_have_non_blocking_metric_discrepancies",
    "panel_has_symbol_timestamp_gaps_relative_to_global_panel_range"
  ]
}
```

## Report Consistency Audit

| metric                                    |   observed |   expected_or_reported | source                         | matches   |
|:------------------------------------------|-----------:|-----------------------:|:-------------------------------|:----------|
| final_panel_rows                          |     815818 |                 815818 | handoff_expected               | True      |
| final_panel_columns                       |        654 |                    654 | handoff_expected               | True      |
| merge_report_output_rows                  |     815818 |                 815818 | merge_json                     | True      |
| merge_report_output_columns               |        654 |                    654 | merge_json                     | True      |
| agg_feature_report_rows                   |     245088 |                 245088 | agg_feature_json_vs_handoff    | True      |
| agg_feature_report_symbol_month_count     |        336 |                    336 | agg_feature_json_vs_handoff    | True      |
| merge_report_input_agg_rows               |     246528 |                 245088 | merge_json_vs_agg_feature_json | False     |
| merge_report_input_agg_symbol_month_count |        339 |                    336 | merge_json_vs_agg_feature_json | False     |

## Key Coverage By Symbol

| symbol   |   rows | timestamp_min             | timestamp_max             |   duplicate_keys |   missing_hours_vs_panel_range |
|:---------|-------:|:--------------------------|:--------------------------|-----------------:|-------------------------------:|
| AAVEUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ADAUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ALGOUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| APTUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ARBUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ARUSDT   |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ATOMUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| AVAXUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| BCHUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| BNBUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| BTCUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| DOGEUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| DOTUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ETCUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ETHUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| FILUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| GALAUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| HBARUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ICPUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| IMXUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| INJUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| JTOUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| LINKUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| LTCUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| MANAUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| NEARUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| OPUSDT   |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| ORDIUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| SANDUSDT |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| SEIUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| SOLUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| STXUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| SUIUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| TIAUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| TRXUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| UNIUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| WLDUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |
| XLMUSDT  |  20896 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             33 |
| XRPUSDT  |  20919 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |                0 |                             10 |

## aggTrades Coverage By Symbol

| symbol   | is_core12   |   rows |   agg_available_rows |   agg_coverage | agg_first_timestamp       | agg_last_timestamp        |   may_2026_agg_rows |
|:---------|:------------|-------:|---------------------:|---------------:|:--------------------------|:--------------------------|--------------------:|
| ADAUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| AVAXUSDT | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| BCHUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| BNBUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| BTCUSDT  | True        |  20919 |                20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |                 480 |
| DOGEUSDT | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| ETHUSDT  | True        |  20919 |                20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |                 480 |
| LINKUSDT | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| LTCUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| SOLUSDT  | True        |  20919 |                20894 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-20 23:00:00+00:00 |                 480 |
| SUIUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| XRPUSDT  | True        |  20919 |                20414 |       0.975859 | 2024-01-01 00:00:00+00:00 | 2026-04-30 23:00:00+00:00 |                   0 |
| AAVEUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ALGOUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| APTUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ARBUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ARUSDT   | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ATOMUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| DOTUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ETCUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| FILUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| GALAUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| HBARUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ICPUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| IMXUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| INJUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| JTOUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| MANAUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| NEARUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| OPUSDT   | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| ORDIUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| SANDUSDT | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| SEIUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| STXUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| TIAUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| TRXUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| UNIUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| WLDUSDT  | False       |  20919 |                    0 |       0        |                           |                           |                   0 |
| XLMUSDT  | False       |  20896 |                    0 |       0        |                           |                           |                   0 |

## agg Feature Partition Audit

| symbol   |   partition_months | has_all_2024_01_to_2026_04   | extra_months   | missing_months   |
|:---------|-------------------:|:-----------------------------|:---------------|:-----------------|
| ADAUSDT  |                 28 | True                         |                |                  |
| AVAXUSDT |                 28 | True                         |                |                  |
| BCHUSDT  |                 28 | True                         |                |                  |
| BNBUSDT  |                 28 | True                         |                |                  |
| BTCUSDT  |                 29 | True                         | 2026-05        |                  |
| DOGEUSDT |                 28 | True                         |                |                  |
| ETHUSDT  |                 29 | True                         | 2026-05        |                  |
| LINKUSDT |                 28 | True                         |                |                  |
| LTCUSDT  |                 28 | True                         |                |                  |
| SOLUSDT  |                 29 | True                         | 2026-05        |                  |
| SUIUSDT  |                 28 | True                         |                |                  |
| XRPUSDT  |                 28 | True                         |                |                  |

## Hourly Enhanced Partition Audit

| symbol   |   hourly_months | has_all_2024_01_to_2026_04   | extra_months   | missing_months   |
|:---------|----------------:|:-----------------------------|:---------------|:-----------------|
| ADAUSDT  |              28 | True                         |                |                  |
| AVAXUSDT |              28 | True                         |                |                  |
| BCHUSDT  |              28 | True                         |                |                  |
| BNBUSDT  |              28 | True                         |                |                  |
| BTCUSDT  |              29 | True                         | 2026-05        |                  |
| DOGEUSDT |              28 | True                         |                |                  |
| ETHUSDT  |              29 | True                         | 2026-05        |                  |
| LINKUSDT |              28 | True                         |                |                  |
| LTCUSDT  |              28 | True                         |                |                  |
| SOLUSDT  |              29 | True                         | 2026-05        |                  |
| SUIUSDT  |              28 | True                         |                |                  |
| XRPUSDT  |              28 | True                         |                |                  |

## Checksum Count Audit

| symbol   |   checksum_files_2024_01_2026_04 | has_all_2024_01_to_2026_04   | extra_months   | missing_months                                                                                                                                                                          |
|:---------|---------------------------------:|:-----------------------------|:---------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ADAUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |
| AVAXUSDT |                               28 | True                         |                |                                                                                                                                                                                         |
| BCHUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |
| BNBUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |
| BTCUSDT  |                                5 | False                        |                | 2024-03;2024-06;2024-07;2024-08;2024-09;2024-10;2024-11;2024-12;2025-01;2025-02;2025-03;2025-04;2025-05;2025-06;2025-07;2025-08;2025-09;2025-10;2025-11;2025-12;2026-02;2026-03;2026-04 |
| DOGEUSDT |                               28 | True                         |                |                                                                                                                                                                                         |
| ETHUSDT  |                                6 | False                        |                | 2024-06;2024-07;2024-08;2024-09;2024-10;2024-11;2024-12;2025-01;2025-02;2025-04;2025-05;2025-06;2025-07;2025-08;2025-09;2025-10;2025-11;2025-12;2026-01;2026-02;2026-03;2026-04         |
| LINKUSDT |                               28 | True                         |                |                                                                                                                                                                                         |
| LTCUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |
| SOLUSDT  |                                5 | False                        |                | 2024-06;2024-07;2024-08;2024-09;2024-10;2024-11;2024-12;2025-01;2025-02;2025-03;2025-04;2025-05;2025-06;2025-07;2025-08;2025-09;2025-10;2025-11;2025-12;2026-01;2026-02;2026-03;2026-04 |
| SUIUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |
| XRPUSDT  |                               28 | True                         |                |                                                                                                                                                                                         |

## Source Trace Closure Audit

| symbol   | source_trace_method      |   trace_rows |   ready_rows |   expected_rows | source_trace_complete   | note                                                                                |
|:---------|:-------------------------|-------------:|-------------:|----------------:|:------------------------|:------------------------------------------------------------------------------------|
| ADAUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| AVAXUSDT | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| BCHUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| BNBUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| BTCUSDT  | A7U0R_source_trace_audit |           29 |           29 |              29 | True                    | core3 source trace closed by A7U-0R; checksum files may live outside package_a path |
| DOGEUSDT | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| ETHUSDT  | A7U0R_source_trace_audit |           29 |           29 |              29 | True                    | core3 source trace closed by A7U-0R; checksum files may live outside package_a path |
| LINKUSDT | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| LTCUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| SOLUSDT  | A7U0R_source_trace_audit |           29 |           29 |              29 | True                    | core3 source trace closed by A7U-0R; checksum files may live outside package_a path |
| SUIUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |
| XRPUSDT  | package_a_checksum_files |           28 |           28 |              28 | True                    | rem9 monthly 2024-01..2026-04 checksum files present                                |

## Bounded Field Audit

| field_name                         |   lower |   upper |   violation_count |
|:-----------------------------------|--------:|--------:|------------------:|
| agg_large_notional_ratio_100k_plus |       0 |       1 |                 0 |
| agg_volume_imbalance               |      -1 |       1 |                 0 |

## Numeric Quality Sample

| field_name                         |   non_null_rate |   nan_count |   inf_count |   negative_count |              min |         max |
|:-----------------------------------|----------------:|------------:|------------:|-----------------:|-----------------:|------------:|
| agg_buy_notional                   |        0.302038 |      569410 |           0 |                0 | 222927           | 7.23126e+09 |
| agg_large_notional_100k_plus       |        0.302038 |      569410 |           0 |                0 |      0           | 7.49136e+09 |
| agg_large_notional_ratio_100k_plus |        0.302038 |      569410 |           0 |                0 |      0           | 0.938963    |
| agg_notional                       |        0.302038 |      569410 |           0 |                0 | 490008           | 1.44809e+10 |
| agg_quantity                       |        0.302038 |      569410 |           0 |                0 |    358.475       | 8.99081e+09 |
| agg_sell_notional                  |        0.302038 |      569410 |           0 |                0 | 217592           | 7.71394e+09 |
| agg_trade_count                    |        0.302038 |      569410 |           0 |                0 |    648           | 2.46234e+06 |
| agg_underlying_trade_count         |        0.302038 |      569410 |           0 |                0 |   2077           | 4.36244e+06 |
| agg_buy_sell_notional_ratio        |        0.302038 |      569410 |           0 |              nan |      0.193542    | 5.69357     |
| agg_signed_aggressor_notional      |        0.302038 |      569410 |           0 |              nan |     -1.08849e+09 | 1.17939e+09 |
| agg_volume_imbalance               |        0.302038 |      569410 |           0 |              nan |     -0.675685    | 0.701206    |
| agg_features_available             |        1        |           0 |           0 |              nan |      0           | 1           |

## Boundary

- This is a data-line acceptance audit, not alpha evidence.
- The final parquet is a core39-sized panel with aggTrades fields populated for core12 only.
- 2026-05 monthly aggTrades history is not claimed by this handoff.
- Any experiment must use selected fields and an explicit time-availability contract.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
