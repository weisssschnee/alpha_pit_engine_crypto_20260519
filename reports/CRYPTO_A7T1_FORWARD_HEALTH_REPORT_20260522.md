# CRYPTO A7T-1 Forward Health Report

Generated: 2026-05-22T10:03:23Z

## Decision

`WARN_A7T1_FORWARD_HEALTH_STALE_SAMPLE`

A7T-1 is an operational health report. It does not download data, run replay, search formulas, or authorize alpha proof.

## Source Health

| source_id                          | status                     |   rows |   symbols | providers         | latest_observable_time           |   age_hours |   errors | notes                                                                                    |   runs | manifest                                                                            |   manifest_rows |   downloaded_rows | endpoints                                                                                                           |
|:-----------------------------------|:---------------------------|-------:|----------:|:------------------|:---------------------------------|------------:|---------:|:-----------------------------------------------------------------------------------------|-------:|:------------------------------------------------------------------------------------|----------------:|------------------:|:--------------------------------------------------------------------------------------------------------------------|
| cross_exchange_forward_snapshot    | PASS_SAMPLE_READY          |    153 |        12 | binance,bybit,okx | 2026-05-22 09:46:25+00:00        |    0.282773 |        0 | forward snapshot sample only; not historical proof                                       |        |                                                                                     |                 |                   |                                                                                                                     |
| binance_orderbook_forward_snapshot | WARN_STALE_SAMPLE          |     36 |        12 | binance           | 2026-05-22 01:10:27.222000+00:00 |    8.88216  |        0 | sample is stale for live telemetry; collector should run on schedule                     |      3 |                                                                                     |                 |                   |                                                                                                                     |
| binance_positioning_forward_5m     | PASS_LATEST_MANIFEST_CLEAN |    594 |        12 |                   | 2026-05-22 01:45:33+00:00        |    8.2972   |        0 | latest manifest must be clean before operational forward telemetry is considered healthy |        | G:\AlphaFactory_CryptoData\manifests\positioning_forward_5m_2026-05-22_manifest.csv |              60 |                60 | globalLongShortAccountRatio,openInterestHist,takerlongshortRatio,topLongShortAccountRatio,topLongShortPositionRatio |

## Positioning Error Detail

`<empty>`

## Authorization

| decision                              | generated_at         | executes_download   | executes_search   | executes_replay   |   source_count |   hard_hold_count |   warning_count |   positioning_error_count | authorizes_forward_telemetry_collection   | authorizes_historical_alpha_proof   | authorizes_alpha_proof   | authorizes_shadow_paper_live   | required_next                                                                                                                                                    |
|:--------------------------------------|:---------------------|:--------------------|:------------------|:------------------|---------------:|------------------:|----------------:|--------------------------:|:------------------------------------------|:------------------------------------|:-------------------------|:-------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| WARN_A7T1_FORWARD_HEALTH_STALE_SAMPLE | 2026-05-22T10:03:23Z | False               | False             | False             |              3 |                 0 |               1 |                         0 | True                                      | False                               | False                    | False                          | ['Run orderbook/cross-exchange collectors on fixed schedule if telemetry dashboard is needed', 'Add collector_version and schema_hash to all forward manifests'] |

## Required Next Action

1. Run orderbook/cross-exchange collectors on a fixed cadence if telemetry dashboard freshness is required.
2. Add `collector_version` and `schema_hash` to future forward manifests.
3. Keep this report as telemetry health only; no alpha proof, shadow, paper, or live.
