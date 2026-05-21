# Crypto A7S-1 Data Source Availability / PIT Audit

- generated_at: `2026-05-21T01:05:38Z`
- decision: `HOLD_A7S1_NEW_DATA_NOT_READY_FOR_ALPHA_SEARCH`
- executes_search: `False`
- executes_replay: `False`
- executes_download: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Decision

A7S-1 confirms the current local data can support continued engineering and append-only forward observation, but it does not authorize a new crypto alpha search. The only long-history research-ready families are the same Binance futures/mark/index/premium/funding/spot-core6 data already used by A7P/A7R. The genuinely new state variables are either recent/forward-only or absent locally.

## Existing Manifest Inventory

| source_id                    | path                                                                                | exists   |   file_size_bytes |   manifest_rows | status_counts                  |   data_type_count |   symbol_count |   row_count_sum | date_range_min                                                    | date_range_max                                                    |
|:-----------------------------|:------------------------------------------------------------------------------------|:---------|------------------:|----------------:|:-------------------------------|------------------:|---------------:|----------------:|:------------------------------------------------------------------|:------------------------------------------------------------------|
| silver                       | G:\AlphaFactory_CryptoData\manifests\crypto_silver_manifest_20260519.csv            | True     |           1914342 |            4104 | {"written": 4104}              |                11 |             12 |        72235710 | 2024-01                                                           | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 |
| funding_rate                 | G:\AlphaFactory_CryptoData\manifests\fundingRate_core12_202401_current_manifest.csv | True     |              3822 |              12 | {"downloaded": 12}             |                 1 |             12 |           31296 | 2024-01-01_current                                                | 2024-01-01_current                                                |
| positioning_recent29d        | G:\AlphaFactory_CryptoData\manifests\positioning_core12_recent29d_5m_manifest.csv   | True     |             25770 |              60 | {"downloaded": 60}             |                 5 |             12 |          500928 | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 |
| positioning_recent30d        | G:\AlphaFactory_CryptoData\manifests\positioning_core12_recent30d_5m_manifest.csv   | True     |             23310 |              60 | {"error": 60}                  |                 5 |             12 |               0 | 2026-04-19_2026-05-19                                             | 2026-04-19_2026-05-19                                             |
| positioning_forward_20260519 | G:\AlphaFactory_CryptoData\manifests\positioning_forward_5m_2026-05-19_manifest.csv | True     |             27462 |              60 | {"downloaded": 60}             |                 5 |             12 |            9192 | 2026-05-19T03:50:00Z                                              | 2026-05-19T16:35:08Z                                              |
| positioning_forward_20260520 | G:\AlphaFactory_CryptoData\manifests\positioning_forward_5m_2026-05-20_manifest.csv | True     |             27479 |              60 | {"downloaded": 59, "error": 1} |                 5 |             12 |           17062 | 2026-05-19T16:30:00Z                                              | 2026-05-20T16:35:08Z                                              |
| microstructure_pilot         | G:\AlphaFactory_CryptoData\manifests\microstructure_pilot_20260519_manifest.csv     | True     |               745 |               1 | {"downloaded": 1}              |                 1 |              1 |         8601508 | 2026-04                                                           | 2026-04                                                           |
| spot_core6                   | G:\AlphaFactory_CryptoData\manifests\spot_core6_202401_202604_manifest.csv          | True     |            242612 |             672 | {"downloaded": 672}            |                 1 |              6 |         8950818 | 2024-01                                                           | 2026-04                                                           |

## Gold Panel Coverage

| panel_id                  | path                                                                               | exists   |    rows |   columns |   symbol_count | min_timestamp             | max_timestamp             | has_positioning_columns   | has_open_interest   | has_long_short   | has_liquidation   | has_orderbook   | has_cross_exchange   |   duplicate_key_count | positioning_recent_excluded   |   checksum_ok_rows |   spot_close_missing_rate |   spot_perp_basis_missing_rate |
|:--------------------------|:-----------------------------------------------------------------------------------|:---------|--------:|----------:|---------------:|:--------------------------|:--------------------------|:--------------------------|:--------------------|:-----------------|:------------------|:----------------|:---------------------|----------------------:|:------------------------------|-------------------:|--------------------------:|-------------------------------:|
| core12_1h                 | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet                 | True     |  250656 |        88 |             12 | 2024-01-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | True                      | False               | False            | False             | False           | False                |                     0 | True                          |             245088 |                       0.5 |                            0.5 |
| core12_1h_forward_updated | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1_forward_updated.parquet | True     |  250860 |        88 |             12 | 2024-01-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | True                      | False               | False            | False             | False           | False                |                     0 | True                          |             245088 |                       0.5 |                            0.5 |
| core12_5m                 | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_5m_v1.parquet                 | True     | 2941056 |        88 |             12 | 2024-01-01T00:00:00+00:00 | 2026-04-30T23:55:00+00:00 | True                      | False               | False            | False             | False           | False                |                     0 | True                          |            2941056 |                       0.5 |                            0.5 |

## Candidate Source Contract

| source                           | local_status                   | local_evidence                                                      | history_window                         | core12_coverage   | pit_status                                               | alpha_search_status                                 | next_action                                                                          | notes                                                               |
|:---------------------------------|:-------------------------------|:--------------------------------------------------------------------|:---------------------------------------|:------------------|:---------------------------------------------------------|:----------------------------------------------------|:-------------------------------------------------------------------------------------|:--------------------------------------------------------------------|
| futures_ohlcv_mark_index_premium | available_long_history         | crypto_silver_manifest_20260519.csv                                 | 2024-01_to_2026-04                     | core12            | research_usable_existing_panel                           | already_exhausted_by_A7P_A7R_current_line           | do_not_continue_current_1h_objective_without_new_contract                            | silver rows=72235710                                                |
| funding_rate                     | available_long_history         | fundingRate_core12_202401_current_manifest.csv                      | 2024-01_to_current                     | core12            | usable_as_observable_latest_known_after_A7D_A7E_controls | mandatory_baseline_not_new_edge_source              | keep_residual_baseline_and_wrong_lag_controls                                        | rows=31296                                                          |
| spot_perp_basis                  | available_partial              | spot_core6_202401_202604_manifest.csv and panel spot_available mask | 2024-01_to_2026-04                     | core6_only        | usable_only_with_availability_mask_or_core6_universe     | not_core12_full_universe_without_contract           | if used, run core6-only or masked proof line                                         | spot rows=8950818; panel spot_perp_missing_rate=0.5                 |
| open_interest                    | recent_and_forward_only        | positioning_recent29d + positioning_forward manifests               | recent29d_plus_forward_from_2026-05-19 | core12_recent     | not_eligible_for_2024_2026_historical_alpha_search       | forward_observation_or_requires_historical_backfill | A7S2_field_semantics_and_backfill_feasibility                                        | recent rows=500928; latest forward rows=17062                       |
| long_short_positioning           | recent_and_forward_only        | positioning_recent29d + positioning_forward manifests               | recent29d_plus_forward_from_2026-05-19 | core12_recent     | not_eligible_for_2024_2026_historical_alpha_search       | forward_observation_or_requires_historical_backfill | A7S2_field_semantics_and_backfill_feasibility                                        | includes global/top account/position ratios where downloaded        |
| aggTrades_microstructure         | single_symbol_month_pilot_only | microstructure_pilot_20260519_manifest.csv                          | SOLUSDT_2026-04_only                   | not_core12        | data_feasibility_sample_only                             | not_eligible_for_core12_historical_proof            | only use for parser/storage/cost feasibility unless broader backfill contract passes | rows=8601508                                                        |
| liquidation_events_or_volume     | not_found_local                | no local manifest detected                                          | none                                   | none              | contract_required                                        | not_authorized                                      | source/vendor inventory and PIT timestamp contract                                   | high expected value for forced-flow state, but no local proof asset |
| orderbook_depth_spread_imbalance | not_found_local                | no depth/orderbook manifest detected                                | none                                   | none              | contract_required                                        | not_authorized                                      | source/vendor inventory and storage/timestamp feasibility                            | high timestamp and storage risk                                     |
| cross_exchange_basis_or_funding  | not_found_local                | single-venue Binance data only                                      | none                                   | none              | contract_required                                        | not_authorized                                      | venue inventory and symbol mapping contract                                          | would change hypothesis space; currently absent                     |

## PIT Readiness Matrix

| source                           | local_status                   | pit_readiness         | alpha_search_authorization   | data_download_authorization   | forward_observation_authorization   | blocking_reason                                                                    |
|:---------------------------------|:-------------------------------|:----------------------|:-----------------------------|:------------------------------|:------------------------------------|:-----------------------------------------------------------------------------------|
| futures_ohlcv_mark_index_premium | available_long_history         | usable_existing       | not_authorized               | not_authorized                | authorized_if_append_only           | No new alpha authorization; already evaluated under A7P/A7R current-space failure. |
| funding_rate                     | available_long_history         | usable_existing       | not_authorized               | not_authorized                | authorized_if_append_only           | No new alpha authorization; already evaluated under A7P/A7R current-space failure. |
| spot_perp_basis                  | available_partial              | usable_with_mask_only | not_authorized               | not_authorized                | not_authorized                      | Core6/availability mask required; not full core12.                                 |
| open_interest                    | recent_and_forward_only        | not_historical_proof  | not_authorized               | not_authorized                | authorized_if_append_only           | Can support forward observation; cannot backfill 2024-2026 proof.                  |
| long_short_positioning           | recent_and_forward_only        | not_historical_proof  | not_authorized               | not_authorized                | authorized_if_append_only           | Can support forward observation; cannot backfill 2024-2026 proof.                  |
| aggTrades_microstructure         | single_symbol_month_pilot_only | feasibility_only      | not_authorized               | not_authorized                | not_authorized                      | Parser/storage feasibility; not research proof.                                    |
| liquidation_events_or_volume     | not_found_local                | contract_required     | not_authorized               | not_authorized                | not_authorized                      | Need source, PIT, coverage, and cost contract before collection/search.            |
| orderbook_depth_spread_imbalance | not_found_local                | contract_required     | not_authorized               | not_authorized                | not_authorized                      | Need source, PIT, coverage, and cost contract before collection/search.            |
| cross_exchange_basis_or_funding  | not_found_local                | contract_required     | not_authorized               | not_authorized                | not_authorized                      | Need source, PIT, coverage, and cost contract before collection/search.            |

## Positioning Audit

| source_id                    | endpoint                    | exists   |   manifest_rows |   symbols | status_counts                  |   row_count_sum | min_start            | max_end              | date_range_sample                                                 | pit_use_status                           |   future_timestamp_warning |
|:-----------------------------|:----------------------------|:---------|----------------:|----------:|:-------------------------------|----------------:|:---------------------|:---------------------|:------------------------------------------------------------------|:-----------------------------------------|---------------------------:|
| positioning_recent29d        | globalLongShortAccountRatio | True     |              12 |        12 | {"downloaded": 12}             |          100224 |                      |                      | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent29d        | openInterestHist            | True     |              12 |        12 | {"downloaded": 12}             |          100224 |                      |                      | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent29d        | takerlongshortRatio         | True     |              12 |        12 | {"downloaded": 12}             |          100032 |                      |                      | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent29d        | topLongShortAccountRatio    | True     |              12 |        12 | {"downloaded": 12}             |          100224 |                      |                      | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent29d        | topLongShortPositionRatio   | True     |              12 |        12 | {"downloaded": 12}             |          100224 |                      |                      | 2026-04-20T02:26:01.046237+00:00_2026-05-19T02:26:01.046237+00:00 | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent30d        | globalLongShortAccountRatio | True     |              12 |        12 | {"error": 12}                  |               0 |                      |                      | 2026-04-19_2026-05-19                                             | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent30d        | openInterestHist            | True     |              12 |        12 | {"error": 12}                  |               0 |                      |                      | 2026-04-19_2026-05-19                                             | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent30d        | takerlongshortRatio         | True     |              12 |        12 | {"error": 12}                  |               0 |                      |                      | 2026-04-19_2026-05-19                                             | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent30d        | topLongShortAccountRatio    | True     |              12 |        12 | {"error": 12}                  |               0 |                      |                      | 2026-04-19_2026-05-19                                             | recent_forward_only_not_historical_proof |                        nan |
| positioning_recent30d        | topLongShortPositionRatio   | True     |              12 |        12 | {"error": 12}                  |               0 |                      |                      | 2026-04-19_2026-05-19                                             | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260519 | globalLongShortAccountRatio | True     |              12 |        12 | {"downloaded": 12}             |            1836 | 2026-05-19T03:55:00Z | 2026-05-19T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260519 | openInterestHist            | True     |              12 |        12 | {"downloaded": 12}             |            1836 | 2026-05-19T03:55:00Z | 2026-05-19T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260519 | takerlongshortRatio         | True     |              12 |        12 | {"downloaded": 12}             |            1848 | 2026-05-19T03:50:00Z | 2026-05-19T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260519 | topLongShortAccountRatio    | True     |              12 |        12 | {"downloaded": 12}             |            1836 | 2026-05-19T03:55:00Z | 2026-05-19T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260519 | topLongShortPositionRatio   | True     |              12 |        12 | {"downloaded": 12}             |            1836 | 2026-05-19T03:55:00Z | 2026-05-19T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260520 | globalLongShortAccountRatio | True     |              12 |        12 | {"downloaded": 12}             |            3468 | 2026-05-19T16:35:00Z | 2026-05-20T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260520 | openInterestHist            | True     |              12 |        12 | {"downloaded": 12}             |            3468 | 2026-05-19T16:35:00Z | 2026-05-20T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260520 | takerlongshortRatio         | True     |              12 |        12 | {"downloaded": 11, "error": 1} |            3190 | 2026-05-19T16:30:00Z | 2026-05-20T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260520 | topLongShortAccountRatio    | True     |              12 |        12 | {"downloaded": 12}             |            3468 | 2026-05-19T16:35:00Z | 2026-05-20T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_20260520 | topLongShortPositionRatio   | True     |              12 |        12 | {"downloaded": 12}             |            3468 | 2026-05-19T16:35:00Z | 2026-05-20T16:35:08Z |                                                                   | recent_forward_only_not_historical_proof |                        nan |
| positioning_forward_state    | globalLongShortAccountRatio | True     |              12 |        12 | {}                             |                 |                      | 2026-05-20T16:35:00Z |                                                                   | state_file_forward_only                  |                          0 |
| positioning_forward_state    | openInterestHist            | True     |              12 |        12 | {}                             |                 |                      | 2026-05-20T16:35:00Z |                                                                   | state_file_forward_only                  |                          0 |
| positioning_forward_state    | takerlongshortRatio         | True     |              12 |        12 | {}                             |                 |                      | 2026-05-20T16:30:00Z |                                                                   | state_file_forward_only                  |                          0 |
| positioning_forward_state    | topLongShortAccountRatio    | True     |              12 |        12 | {}                             |                 |                      | 2026-05-20T16:35:00Z |                                                                   | state_file_forward_only                  |                          0 |
| positioning_forward_state    | topLongShortPositionRatio   | True     |              12 |        12 | {}                             |                 |                      | 2026-05-20T16:35:00Z |                                                                   | state_file_forward_only                  |                          0 |

## Microstructure Pilot Audit

| source               | exists   |   symbol_count | symbols   | date_ranges   | data_types   |   row_count_sum | checksum_status_counts   | research_status                                        |
|:---------------------|:---------|---------------:|:----------|:--------------|:-------------|----------------:|:-------------------------|:-------------------------------------------------------|
| microstructure_pilot | True     |              1 | SOLUSDT   | 2026-04       | aggTrades    |         8601508 | {"ok": 1}                | parser_storage_feasibility_only_not_core12_alpha_proof |

## Authorization Matrix

```json
{
  "authorizes_a7s2_field_semantics_review": true,
  "authorizes_alpha_proof": false,
  "authorizes_alpha_search": false,
  "authorizes_data_download": false,
  "authorizes_forward_observation_contract": true,
  "authorizes_shadow_paper_live": false,
  "blocking_findings": [
    "open_interest_and_long_short_are_recent_forward_only_not_2024_2026_historical_proof",
    "liquidation_orderbook_cross_exchange_sources_not_found_locally",
    "spot_perp_basis_is_core6_partial_not_core12_full_universe",
    "aggTrades_microstructure_is_SOLUSDT_2026_04_pilot_only",
    "current_long_history_panel_is_same_feature_space_that_A7P_A7R_already_rejected_for_alpha_search"
  ],
  "decision": "HOLD_A7S1_NEW_DATA_NOT_READY_FOR_ALPHA_SEARCH",
  "executes_download": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-21T01:05:38Z",
  "required_before_download": [
    "source_cost_and_access_contract",
    "PIT_timestamp_contract",
    "symbol_coverage_contract",
    "storage_cost_contract",
    "small_sample_timestamp_audit"
  ]
}
```

## Required Next Action

1. `A7S-2`: field semantics and backfill feasibility review for open interest / long-short / liquidation / orderbook / cross-exchange sources.
2. `A7T-0`: forward-locked observation contract using append-only data only.
3. Do not restart current 1h formula search from A7P/A7R/A7O without a new data or horizon contract.
