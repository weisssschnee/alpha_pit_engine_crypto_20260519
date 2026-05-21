# Crypto A7S-2 Field Semantics / Backfill Feasibility

- generated_at: `2026-05-21T01:09:38Z`
- decision: `HOLD_A7S2_DATA_BACKFILL_CONTRACT_REQUIRED`
- executes_search: `False`
- executes_replay: `False`
- executes_download: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Decision

A7S-2 confirms that the highest-value missing state variables cannot be used immediately for historical alpha search. Open interest and long/short ratios are locally recent/forward-only and the official REST history is short-window. Orderbook and liquidation require collectors or vendor archives. AggTrades is the only locally demonstrated scalable official-file path, but current local coverage is only one symbol/month and needs a storage/backfill contract before research use.

## Source Feasibility Matrix

| source                               | field_family           | official_endpoint_or_source                                | official_doc_url                                                                                                            | documented_history_limit                                                  | local_status                                                                   | pit_semantics                                                                                                                      | 2024_2026_backfill_feasibility                                         | usable_for_next_search                                     | usable_for_forward                                     | risk                                                                                               |
|:-------------------------------------|:-----------------------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------|:-----------------------------------------------------------|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------|
| open_interest_hist                   | open_interest          | GET /futures/data/openInterestHist                         | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics         | latest_1_month_only                                                       | recent29d_plus_forward_collector                                               | timestamp is event time; observable only after API publication/collector time                                                      | not_feasible_from_binance_rest_history                                 | no_historical_alpha_search                                 | yes_append_only                                        | Cannot be used to validate 2024-2026 fixed split unless an independent historical vendor exists.   |
| global_long_short_account_ratio      | positioning_crowding   | GET /futures/data/globalLongShortAccountRatio              | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio                 | latest_30_days_only                                                       | recent29d_plus_forward_collector                                               | timestamp is account ratio observation time; observable only after API publication/collector time                                  | not_feasible_from_binance_rest_history                                 | no_historical_alpha_search                                 | yes_append_only                                        | Crowding signal may be valuable but cannot be retrofitted into historical proof.                   |
| top_trader_long_short_position_ratio | positioning_crowding   | GET /futures/data/topLongShortPositionRatio                | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio      | latest_30_days_only                                                       | recent29d_plus_forward_collector                                               | timestamp is top-trader position ratio observation time; observable only after API publication/collector time                      | not_feasible_from_binance_rest_history                                 | no_historical_alpha_search                                 | yes_append_only                                        | Useful as forward stress/crowding telemetry, not historical alpha proof.                           |
| basis_rest                           | basis_premium          | GET /futures/data/basis                                    | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Basis                            | latest_30_days_only                                                       | not_collected_separately; mark/index/premium klines already exist long-history | REST basis timestamp is event time; local long-history basis should use mark/index/premium klines instead                          | not_needed_for_single_venue_basis; not_feasible_for_rest_basis_history | only_if_new_cross_exchange_or_new_contract                 | yes_if_collected_append_only                           | Single-venue Binance basis is already represented; REST basis does not add new long-history state. |
| aggTrades                            | microstructure_trades  | Binance Vision monthly aggTrades or GET /fapi/v1/aggTrades | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List | REST_not_older_than_24h; Binance_Vision_monthly_history_available_by_file | SOLUSDT_2026_04_pilot_only                                                     | trade timestamp is event time; monthly files can be historical if checksum and timestamp unit pass                                 | feasible_but_storage_heavy_for_core12                                  | not_until_core12_backfill_contract_and_storage_budget_pass | yes_if_collected_or_backfilled_with_versioned_manifest | Large storage/compute; not a quick fix for A7P objective failure.                                  |
| orderbook_depth_snapshot             | orderbook_depth_spread | GET /fapi/v1/depth                                         | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book                       | snapshot_current_only_from_rest                                           | not_found_local                                                                | message output time and transaction time must be retained; historical backfill requires archived snapshots or continuous collector | not_feasible_from_rest_without_archive_vendor                          | no_historical_alpha_search                                 | yes_after_collector_contract                           | High timestamp/storage risk; snapshot sampling can create artificial spread/depth signals.         |
| liquidation_events                   | forced_flow            | websocket liquidation/order stream or vendor archive       | contract_required                                                                                                           | not_verified_in_local_assets                                              | not_found_local                                                                | event time and receive time must be separated; aggregation lag required                                                            | requires_vendor_or_preexisting_archive                                 | no_until_source_contract                                   | yes_after_collector_contract                           | Expected value high for stress regimes but unavailable in current proof pack.                      |
| cross_exchange_basis_funding         | venue_relative_value   | multi-venue vendor/API inventory required                  | contract_required                                                                                                           | venue_dependent                                                           | not_found_local                                                                | venue clocks, symbol mapping, funding schedules, and publication delays must be normalized                                         | unknown_until_vendor_review                                            | no_until_vendor_contract                                   | possible_after_contract                                | Could change hypothesis space materially; also highest semantic mismatch risk.                     |

## PIT Semantics Contract

| source                               | required_field     | required   | status                         |
|:-------------------------------------|:-------------------|:-----------|:-------------------------------|
| open_interest_hist                   | event_time         | True       | required_before_any_future_use |
| open_interest_hist                   | observable_time    | True       | required_before_any_future_use |
| open_interest_hist                   | collector_time     | True       | required_before_any_future_use |
| open_interest_hist                   | publication_delay  | True       | required_before_any_future_use |
| open_interest_hist                   | aggregation_lag    | True       | required_before_any_future_use |
| open_interest_hist                   | symbol_mapping     | True       | required_before_any_future_use |
| open_interest_hist                   | missingness_policy | True       | required_before_any_future_use |
| open_interest_hist                   | restatement_policy | True       | required_before_any_future_use |
| open_interest_hist                   | forward_only_flag  | True       | required_before_any_future_use |
| global_long_short_account_ratio      | event_time         | True       | required_before_any_future_use |
| global_long_short_account_ratio      | observable_time    | True       | required_before_any_future_use |
| global_long_short_account_ratio      | collector_time     | True       | required_before_any_future_use |
| global_long_short_account_ratio      | publication_delay  | True       | required_before_any_future_use |
| global_long_short_account_ratio      | aggregation_lag    | True       | required_before_any_future_use |
| global_long_short_account_ratio      | symbol_mapping     | True       | required_before_any_future_use |
| global_long_short_account_ratio      | missingness_policy | True       | required_before_any_future_use |
| global_long_short_account_ratio      | restatement_policy | True       | required_before_any_future_use |
| global_long_short_account_ratio      | forward_only_flag  | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | event_time         | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | observable_time    | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | collector_time     | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | publication_delay  | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | aggregation_lag    | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | symbol_mapping     | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | missingness_policy | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | restatement_policy | True       | required_before_any_future_use |
| top_trader_long_short_position_ratio | forward_only_flag  | True       | required_before_any_future_use |
| basis_rest                           | event_time         | True       | contract_required              |
| basis_rest                           | observable_time    | True       | contract_required              |
| basis_rest                           | collector_time     | True       | contract_required              |
| basis_rest                           | publication_delay  | True       | contract_required              |
| basis_rest                           | aggregation_lag    | True       | contract_required              |
| basis_rest                           | symbol_mapping     | True       | contract_required              |
| basis_rest                           | missingness_policy | True       | contract_required              |
| basis_rest                           | restatement_policy | True       | contract_required              |
| basis_rest                           | forward_only_flag  | True       | contract_required              |
| aggTrades                            | event_time         | True       | contract_required              |
| aggTrades                            | observable_time    | True       | contract_required              |
| aggTrades                            | collector_time     | True       | contract_required              |
| aggTrades                            | publication_delay  | True       | contract_required              |
| aggTrades                            | aggregation_lag    | True       | contract_required              |
| aggTrades                            | symbol_mapping     | True       | contract_required              |
| aggTrades                            | missingness_policy | True       | contract_required              |
| aggTrades                            | restatement_policy | True       | contract_required              |
| aggTrades                            | forward_only_flag  | True       | contract_required              |
| orderbook_depth_snapshot             | event_time         | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | observable_time    | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | collector_time     | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | publication_delay  | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | aggregation_lag    | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | symbol_mapping     | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | missingness_policy | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | restatement_policy | True       | required_before_any_future_use |
| orderbook_depth_snapshot             | forward_only_flag  | True       | required_before_any_future_use |
| liquidation_events                   | event_time         | True       | contract_required              |
| liquidation_events                   | observable_time    | True       | contract_required              |
| liquidation_events                   | collector_time     | True       | contract_required              |
| liquidation_events                   | publication_delay  | True       | contract_required              |
| liquidation_events                   | aggregation_lag    | True       | contract_required              |
| liquidation_events                   | symbol_mapping     | True       | contract_required              |
| liquidation_events                   | missingness_policy | True       | contract_required              |
| liquidation_events                   | restatement_policy | True       | contract_required              |
| liquidation_events                   | forward_only_flag  | True       | contract_required              |
| cross_exchange_basis_funding         | event_time         | True       | contract_required              |
| cross_exchange_basis_funding         | observable_time    | True       | contract_required              |
| cross_exchange_basis_funding         | collector_time     | True       | contract_required              |
| cross_exchange_basis_funding         | publication_delay  | True       | contract_required              |
| cross_exchange_basis_funding         | aggregation_lag    | True       | contract_required              |
| cross_exchange_basis_funding         | symbol_mapping     | True       | contract_required              |
| cross_exchange_basis_funding         | missingness_policy | True       | contract_required              |
| cross_exchange_basis_funding         | restatement_policy | True       | contract_required              |
| cross_exchange_basis_funding         | forward_only_flag  | True       | contract_required              |

## Backfill Priority

|   priority | source                               | conclusion                               | next_action                                         | authorized_now   |
|-----------:|:-------------------------------------|:-----------------------------------------|:----------------------------------------------------|:-----------------|
|          1 | aggTrades                            | large_but_feasible_with_official_files   | storage_budget_and_core12_monthly_backfill_manifest | False            |
|          2 | open_interest_hist                   | not_historical_from_binance_rest         | external_archive_or_forward_only                    | False            |
|          3 | global_long_short_account_ratio      | not_historical_from_binance_rest         | external_archive_or_forward_only                    | False            |
|          4 | liquidation_events                   | requires_vendor_or_collector             | source_contract_first                               | False            |
|          5 | orderbook_depth_snapshot             | requires_archive_or_collector            | probably_forward_only_initially                     | False            |
|          6 | cross_exchange_basis_funding         | requires_multi_venue_contract            | vendor_inventory_first                              | False            |
|          7 | basis_rest                           | not_incremental_for_single_venue_history | deprioritize_unless_cross_venue                     | False            |
|          8 | top_trader_long_short_position_ratio | not_historical_from_binance_rest         | external_archive_or_forward_only                    | False            |

## Authorization

```json
{
  "authorizes_a7s3_costed_backfill_plan": true,
  "authorizes_a7t0_forward_locked_observation_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_alpha_search": false,
  "authorizes_data_download": false,
  "authorizes_shadow_paper_live": false,
  "blocking_findings": [
    "official_open_interest_and_long_short_rest_history_is_short_window",
    "orderbook_depth_requires_archive_or_forward_collector",
    "liquidation_events_require_source_contract",
    "cross_exchange_sources_absent_and_need_vendor_contract",
    "aggTrades_backfill_feasible_but_storage_heavy_and_not_currently_core12_complete"
  ],
  "decision": "HOLD_A7S2_DATA_BACKFILL_CONTRACT_REQUIRED",
  "executes_download": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-21T01:09:38Z",
  "primary_next": "A7S3_costed_backfill_plan_or_A7T0_forward_locked_observation"
}
```

## External References Checked

- Binance USD-M Open Interest Statistics: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics
- Binance USD-M Long/Short Ratio: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio
- Binance USD-M Top Trader Position Ratio: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio
- Binance USD-M Aggregate Trades: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List
- Binance USD-M Order Book: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book
- Binance USD-M Basis: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Basis
