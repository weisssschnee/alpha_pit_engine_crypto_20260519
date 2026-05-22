# Crypto A7U-0R Source Trace Audit

- generated_at: `2026-05-22T06:27:04Z`
- decision: `PASS_A7U0R_SOURCE_TRACE_COMPLETE`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / panel final claim / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7U-0R consolidates the source lineage for the enhanced aggTrades panel used by A7V. It audits raw checksum manifests, hourly enhanced partitions, enhanced feature panel lineage, and unified panel join reports.

This audit does not validate alpha. It only determines whether the panel can be referenced with complete source/checksum traceability.

## Trace Summary

| raw_trace_class   | source_trace_decision       |   rows |
|:------------------|:----------------------------|-------:|
| raw_checksum_ok   | PASS_A7U0R_SOURCE_TRACE_ROW |     87 |

## By Symbol

| symbol   |   rows |   ready |   raw_checksum_ok |   partitions |   row_hours |
|:---------|-------:|--------:|------------------:|-------------:|------------:|
| BTCUSDT  |     29 |      29 |                29 |           29 |       20904 |
| ETHUSDT  |     29 |      29 |                29 |           29 |       20904 |
| SOLUSDT  |     29 |      29 |                29 |           29 |       20904 |

## Panel Lineage

| artifact                                    | report_path                                                                                         | generated_at         | input_root_or_panel                                                          | input_agg_root                                                          | output                                                                                     |   rows |   columns |   agg_rows |   agg_symbol_month_count |
|:--------------------------------------------|:----------------------------------------------------------------------------------------------------|:---------------------|:-----------------------------------------------------------------------------|:------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|-------:|----------:|-----------:|-------------------------:|
| aggtrades_enhanced_features_v1              | G:\AlphaFactory_CryptoData\reports\aggtrades_enhanced_features_v1_20260522_094400.json              | 2026-05-22T01:44:00Z | G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_enhanced_v1 |                                                                         | G:\AlphaFactory_CryptoData\gold\features\aggtrades_enhanced_features_v1                    |  62712 |        99 |            |                       87 |
| crypto_core12_1h_with_aggtrades_features_v1 | G:\AlphaFactory_CryptoData\reports\crypto_core12_1h_with_aggtrades_features_v1_20260522_094411.json | 2026-05-22T01:44:11Z | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet           | G:\AlphaFactory_CryptoData\gold\features\aggtrades_enhanced_features_v1 | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet | 251148 |       184 |      62712 |                       87 |

## Rows Not Ready For Final Raw-Level Claim

`<empty>`

## Interpretation

- All 87 core3 symbol-month source trace rows have raw checksum status `ok` and matching enhanced hourly partitions.
- Enhanced hourly partitions exist for the expected core3 symbol-month rows, including the current partial May daily extension.
- The `source_trace_incomplete` caveat is removed for A7V controlled experiments.
- This closes raw-level source trace for the enhanced aggTrades panel; it does not validate alpha, strategy robustness, or production readiness.

## Authorization

```json
{
  "agg_partition_rows": 87,
  "authorizes_alpha_proof": false,
  "authorizes_controlled_experiments_with_caveat": false,
  "authorizes_controlled_experiments_without_source_trace_caveat": true,
  "authorizes_final_panel_raw_level_claim": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7U0R_SOURCE_TRACE_COMPLETE",
  "executes_replay": false,
  "executes_search": false,
  "expected_trace_rows": 87,
  "generated_at": "2026-05-22T06:27:04Z",
  "raw_checksum_ok_rows": 87,
  "required_next": [
    "A7V/A7U may reference the enhanced aggTrades panel without source_trace_incomplete caveat",
    "Alpha proof, expanded replay, shadow, paper, and live remain blocked by A7V-6/A7V-7 signal failures",
    "Rerun A7U-0R after any future aggTrades panel refresh"
  ],
  "source_trace_hold_rows": 0,
  "source_trace_ready_rows": 87
}
```

## Required Next

- A7V/A7U may reference the enhanced aggTrades panel without the previous `source_trace_incomplete` caveat.
- Continue to keep alpha proof / shadow / paper / live blocked by A7V-6/A7V-7 signal failures.
- Any future aggTrades panel refresh must rerun A7U-0R before final panel claims.
