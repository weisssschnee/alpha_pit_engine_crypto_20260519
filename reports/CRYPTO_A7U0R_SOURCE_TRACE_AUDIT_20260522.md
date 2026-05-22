# Crypto A7U-0R Source Trace Audit

- generated_at: `2026-05-22T02:23:56Z`
- decision: `HOLD_A7U0R_SOURCE_TRACE_INCOMPLETE`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / panel final claim / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7U-0R consolidates the source lineage for the enhanced aggTrades panel used by A7V. It audits raw checksum manifests, hourly enhanced partitions, enhanced feature panel lineage, and unified panel join reports.

This audit does not validate alpha. It only determines whether the panel can be referenced with complete source/checksum traceability.

## Trace Summary

| raw_trace_class               | source_trace_decision       |   rows |
|:------------------------------|:----------------------------|-------:|
| missing_raw_checksum_manifest | HOLD_A7U0R_SOURCE_TRACE_ROW |     12 |
| raw_checksum_not_ok           | HOLD_A7U0R_SOURCE_TRACE_ROW |      2 |
| raw_checksum_ok               | PASS_A7U0R_SOURCE_TRACE_ROW |     73 |

## By Symbol

| symbol   |   rows |   ready |   raw_checksum_ok |   partitions |   row_hours |
|:---------|-------:|--------:|------------------:|-------------:|------------:|
| BTCUSDT  |     29 |      26 |                26 |           29 |       20904 |
| ETHUSDT  |     29 |      23 |                23 |           29 |       20904 |
| SOLUSDT  |     29 |      24 |                24 |           29 |       20904 |

## Panel Lineage

| artifact                                    | report_path                                                                                         | generated_at         | input_root_or_panel                                                          | input_agg_root                                                          | output                                                                                     |   rows |   columns |   agg_rows |   agg_symbol_month_count |
|:--------------------------------------------|:----------------------------------------------------------------------------------------------------|:---------------------|:-----------------------------------------------------------------------------|:------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|-------:|----------:|-----------:|-------------------------:|
| aggtrades_enhanced_features_v1              | G:\AlphaFactory_CryptoData\reports\aggtrades_enhanced_features_v1_20260522_094400.json              | 2026-05-22T01:44:00Z | G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_enhanced_v1 |                                                                         | G:\AlphaFactory_CryptoData\gold\features\aggtrades_enhanced_features_v1                    |  62712 |        99 |            |                       87 |
| crypto_core12_1h_with_aggtrades_features_v1 | G:\AlphaFactory_CryptoData\reports\crypto_core12_1h_with_aggtrades_features_v1_20260522_094411.json | 2026-05-22T01:44:11Z | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet           | G:\AlphaFactory_CryptoData\gold\features\aggtrades_enhanced_features_v1 | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet | 251148 |       184 |      62712 |                       87 |

## Rows Not Ready For Final Raw-Level Claim

| symbol   | month   | raw_trace_class               | checksum_status   | raw_manifest                                                                             |   raw_daily_manifest | conversion_manifest                                      | agg_partition_exists   |   agg_partition_rows |   expected_hours | source_trace_decision       |
|:---------|:--------|:------------------------------|:------------------|:-----------------------------------------------------------------------------------------|---------------------:|:---------------------------------------------------------|:-----------------------|---------------------:|-----------------:|:----------------------------|
| BTCUSDT  | 2024-04 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  720 |              720 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| BTCUSDT  | 2024-05 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| BTCUSDT  | 2026-01 | raw_checksum_not_ok           | mismatch          | aggtrades_raw_latest_roundrobin_2025-11_2026-04_core3_latest6_20260521_company.csv       |                  nan | aggtrades_hourly_enhanced_v1_20260521_221936_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2024-01 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2024-02 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  696 |              696 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2024-03 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2024-04 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  720 |              720 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2024-05 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| ETHUSDT  | 2025-03 | raw_checksum_not_ok           | mismatch          | aggtrades_raw_latest_roundrobin_2024-11_2025-04_core3_202411_202504_20260521_company.csv |                  nan | aggtrades_hourly_enhanced_v1_20260521_221936_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| SOLUSDT  | 2024-01 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| SOLUSDT  | 2024-02 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  696 |              696 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| SOLUSDT  | 2024-03 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| SOLUSDT  | 2024-04 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  720 |              720 | HOLD_A7U0R_SOURCE_TRACE_ROW |
| SOLUSDT  | 2024-05 | missing_raw_checksum_manifest | nan               | nan                                                                                      |                  nan | aggtrades_hourly_enhanced_v1_20260522_005140_company.csv | True                   |                  744 |              744 | HOLD_A7U0R_SOURCE_TRACE_ROW |

## Interpretation

- Enhanced hourly partitions exist for the expected core3 symbol-month rows, including the current partial May daily extension.
- Daily May rows have checksum status from the daily download manifest.
- Several historical monthly rows lack complete raw checksum manifest coverage or have non-ok checksum status in the available local manifest set. These rows can be used for controlled experiments only under the existing panel acceptance boundary, not for final raw-level proof claims.
- The unified panel can remain the A7V experiment input, but final panel claims require resolving the raw checksum trace gaps listed above.

## Authorization

```json
{
  "agg_partition_rows": 87,
  "authorizes_alpha_proof": false,
  "authorizes_controlled_experiments_with_caveat": true,
  "authorizes_final_panel_raw_level_claim": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "source_trace_rows_not_ready",
    "raw_checksum_manifest_coverage_incomplete"
  ],
  "decision": "HOLD_A7U0R_SOURCE_TRACE_INCOMPLETE",
  "executes_replay": false,
  "executes_search": false,
  "expected_trace_rows": 87,
  "generated_at": "2026-05-22T02:23:56Z",
  "raw_checksum_ok_rows": 73,
  "required_next": [
    "Resolve source trace HOLD rows before final raw-level panel claims",
    "Keep A7V experiment claims caveated as controlled experiments, not final panel proof",
    "Request missing or corrected raw checksum manifests from data line"
  ],
  "source_trace_hold_rows": 14,
  "source_trace_ready_rows": 73
}
```

## Required Next

- Ask data line to provide or regenerate raw checksum manifests for the HOLD rows, especially early 2024 ETH/SOL and any monthly checksum mismatch rows.
- Do not use A7V/A7U to claim final raw-level panel proof until all source-trace rows pass.
- Continue controlled experiments only with explicit `source_trace_incomplete` caveat.
