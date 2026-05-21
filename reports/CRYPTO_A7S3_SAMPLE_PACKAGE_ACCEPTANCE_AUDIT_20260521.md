# Crypto A7S-3 Sample Package Acceptance Audit

- generated_at: `2026-05-21T07:58:37Z`
- decision: `PASS_A7S3_SAMPLE_PACKAGE_FOR_CONTRACTED_EXPERIMENTS_HOLD_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Acceptance Matrix

| asset                              | decision                                | allowed_use                                       | not_allowed_use                                 |
|:-----------------------------------|:----------------------------------------|:--------------------------------------------------|:------------------------------------------------|
| aggTrades_1h_flow_fast_samples     | PASS_FOR_A7S_EXPERIMENTAL_FEATURE_AUDIT | feature_schema_and_small_research_panel_join_test | full_core12_alpha_proof_until_backfill_contract |
| orderbook_forward_snapshot_samples | PASS_FOR_A7T_FORWARD_CONTEXT_ONLY       | forward_observation_context                       | historical_alpha_proof_or_backfill              |
| positioning_forward_schema         | PASS_FOR_A7T_FORWARD_CONTEXT_ONLY       | append_only_forward_history                       | 2024_2026_historical_proof                      |
| crypto_core12_1h_panel_refresh     | PASS_FOR_A7T_MARKET_DATA_FRESHNESS      | fresh panel base for observation                  | alpha promotion                                 |

## AggTrades 1h Flow Samples

| path                                                                                                            | exists   | symbol   | month   |   rows |   columns_present | missing_required_columns   | min_timestamp        | max_timestamp        |   missing_hour_count | timestamp_all_hour_floor   |   volume_imbalance_min |   volume_imbalance_max |   quantity_additivity_max_abs_diff |   notional_additivity_max_abs_diff |   signed_quantity_max_abs_diff |   signed_notional_max_abs_diff |   volume_imbalance_notional_formula_max_abs_diff |   volume_imbalance_quantity_formula_max_abs_diff |   trade_count_bucket_max_abs_diff |   notional_bucket_max_abs_diff | decision                           |
|:----------------------------------------------------------------------------------------------------------------|:---------|:---------|:--------|-------:|------------------:|:---------------------------|:---------------------|:---------------------|---------------------:|:---------------------------|-----------------------:|-----------------------:|-----------------------------------:|-----------------------------------:|-------------------------------:|-------------------------------:|-------------------------------------------------:|-------------------------------------------------:|----------------------------------:|-------------------------------:|:-----------------------------------|
| G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_fast\symbol=BTCUSDT\month=2025-09\part.parquet | True     | BTCUSDT  | 2025-09 |    720 |                28 |                            | 2025-09-01T00:00:00Z | 2025-09-30T23:00:00Z |                    0 | True                       |              -0.362213 |               0.420891 |                        7.27596e-12 |                        4.76837e-07 |                    2.04636e-12 |                    2.38419e-07 |                                                0 |                                      0.000715655 |                                 0 |                    4.76837e-07 | PASS_A7S3_AGGTRADES_1H_FLOW_SAMPLE |
| G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_fast\symbol=BTCUSDT\month=2025-10\part.parquet | True     | BTCUSDT  | 2025-10 |    744 |                28 |                            | 2025-10-01T00:00:00Z | 2025-10-31T23:00:00Z |                    0 | True                       |              -0.452385 |               0.326764 |                        7.27596e-12 |                        4.76837e-07 |                    7.27596e-12 |                    9.53674e-07 |                                                0 |                                      0.00082754  |                                 0 |                    4.76837e-07 | PASS_A7S3_AGGTRADES_1H_FLOW_SAMPLE |
| G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_fast\symbol=BTCUSDT\month=2025-11\part.parquet | True     | BTCUSDT  | 2025-11 |    720 |                28 |                            | 2025-11-01T00:00:00Z | 2025-11-30T23:00:00Z |                    0 | True                       |              -0.316475 |               0.308635 |                        7.27596e-12 |                        4.76837e-07 |                    1.9611e-12  |                    3.57628e-07 |                                                0 |                                      0.00116339  |                                 0 |                    9.53674e-07 | PASS_A7S3_AGGTRADES_1H_FLOW_SAMPLE |
| G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_fast\symbol=SOLUSDT\month=2026-04\part.parquet | True     | SOLUSDT  | 2026-04 |    720 |                28 |                            | 2026-04-01T00:00:00Z | 2026-04-30T23:00:00Z |                    0 | True                       |              -0.31388  |               0.397667 |                        9.31323e-10 |                        5.96046e-08 |                    3.49246e-10 |                    2.23517e-08 |                                                0 |                                      0.00109891  |                                 0 |                    5.96046e-08 | PASS_A7S3_AGGTRADES_1H_FLOW_SAMPLE |

## Orderbook Forward Snapshots

| path                                                                                                      | exists   |   rows |   symbol_count | missing_required_columns   | forward_only_all_true   | time_fields_not_null   | event_time_equals_collector_time_all   | best_bid_lt_best_ask_all   |   spread_bps_min |   spread_bps_max |   depth_imbalance_min |   depth_imbalance_max | decision                           |
|:----------------------------------------------------------------------------------------------------------|:---------|-------:|---------------:|:---------------------------|:------------------------|:-----------------------|:---------------------------------------|:---------------------------|-----------------:|-----------------:|----------------------:|----------------------:|:-----------------------------------|
| G:\AlphaFactory_CryptoData\silver\binance_api\orderbook_forward_snapshot\run=20260521_071938\part.parquet | True     |     12 |             12 |                            | True                    | True                   | True                                   | True                       |        0.0129012 |          4.0347  |             -0.697041 |              0.211073 | PASS_A7S3_ORDERBOOK_FORWARD_SAMPLE |
| G:\AlphaFactory_CryptoData\silver\binance_api\orderbook_forward_snapshot\run=20260521_074122\part.parquet | True     |     12 |             12 |                            | True                    | True                   | True                                   | True                       |        0.0128774 |          4.01849 |             -0.305528 |              0.233505 | PASS_A7S3_ORDERBOOK_FORWARD_SAMPLE |

## Positioning Forward Schema

| endpoint                    |   manifest_rows |   silver_files_checked |   missing_files |   rows_total | missing_required_columns   |   forward_only_false_count |   no_historical_backfill_false_count | decision                             |
|:----------------------------|----------------:|-----------------------:|----------------:|-------------:|:---------------------------|---------------------------:|-------------------------------------:|:-------------------------------------|
| globalLongShortAccountRatio |              12 |                     12 |               0 |          404 |                            |                          0 |                                    0 | PASS_A7S3_POSITIONING_FORWARD_SCHEMA |
| openInterestHist            |              12 |                     12 |               0 |          300 |                            |                          0 |                                    0 | PASS_A7S3_POSITIONING_FORWARD_SCHEMA |
| takerlongshortRatio         |              12 |                     12 |               0 |          312 |                            |                          0 |                                    0 | PASS_A7S3_POSITIONING_FORWARD_SCHEMA |
| topLongShortAccountRatio    |              12 |                     12 |               0 |          300 |                            |                          0 |                                    0 | PASS_A7S3_POSITIONING_FORWARD_SCHEMA |
| topLongShortPositionRatio   |              12 |                     12 |               0 |          300 |                            |                          0 |                                    0 | PASS_A7S3_POSITIONING_FORWARD_SCHEMA |

## 1h Gold Panel Refresh

| panel_path                                                         | panel_exists   | refresh_manifest_exists   | refresh_report_exists   |   rows |   symbol_count | latest_timestamp     |   latest_timestamp_symbol_count | decision                       |
|:-------------------------------------------------------------------|:---------------|:--------------------------|:------------------------|-------:|---------------:|:---------------------|--------------------------------:|:-------------------------------|
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet | True           | True                      | True                    | 250896 |             12 | 2026-05-21T03:00:00Z |                              12 | PASS_A7S3_PANEL_REFRESH_SAMPLE |

## Notes

- AggTrades samples pass schema, continuity, bucket additivity, signed-flow algebra, and notional-weighted volume imbalance formula checks.
- `is_buyer_maker = true` is treated as seller aggressor; therefore signed aggressor flow equals buy flow minus sell flow under the current definition. `volume_imbalance` is notional-weighted: `signed_aggressor_notional / notional`. This semantic is acceptable for experiments but should remain explicit in the field contract.
- Orderbook snapshots pass forward-only checks, but `event_time` currently equals collector/observable time. Treat it as snapshot observation time, not exchange book-update event time.
- Positioning forward silver files include event/observable/collector time and forward/no-backfill flags.
- None of these sample passes authorize historical alpha proof.

## Authorization

```json
{
  "authorizes_aggtrades_schema_join_experiment": true,
  "authorizes_alpha_proof": false,
  "authorizes_full_core12_aggtrades_backfill": false,
  "authorizes_orderbook_forward_observation_context": true,
  "authorizes_positioning_forward_observation_context": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7S3_SAMPLE_PACKAGE_FOR_CONTRACTED_EXPERIMENTS_HOLD_ALPHA_PROOF",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-21T07:58:37Z",
  "required_before_full_backfill": [
    "costed_storage_runtime_plan",
    "core12_monthly_manifest_plan",
    "checksum_and_repair_policy",
    "gold_join_contract_with_feature_available_time"
  ]
}
```
