# CRYPTO A7T-0 Forward Telemetry Contract

Generated: 2026-05-22T10:00:51Z

## Decision

`PASS_A7T0_FORWARD_TELEMETRY_CONTRACT_READY`

A7T-0 defines the forward telemetry contract. It does not download data, run replay, search formulas, or authorize historical alpha proof.

## Source Inventory

| source_id                          | path                                                                                                                             | exists   |   rows |   symbols | providers         | feature_groups                                                                                                         | latest_observable_time           |   forward_only_rows |   historical_backfill_rows | decision                       |   runs | latest_manifest                                                                     |   downloaded_manifest_rows |   error_manifest_rows | state_file                                                        |   state_rows |
|:-----------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|:---------|-------:|----------:|:------------------|:-----------------------------------------------------------------------------------------------------------------------|:---------------------------------|--------------------:|---------------------------:|:-------------------------------|-------:|:------------------------------------------------------------------------------------|---------------------------:|----------------------:|:------------------------------------------------------------------|-------------:|
| cross_exchange_forward_snapshot    | G:\AlphaFactory_CryptoData\silver\cross_exchange_forward_snapshot\cross_exchange_forward_snapshot_20260522_core12_probe2.parquet | True     |    153 |        12 | binance,bybit,okx | basis_recent,funding,liquidation_recent,open_interest,orderbook_depth,premium_funding,recent_history,ticker_oi_funding | 2026-05-22 09:46:25+00:00        |                  96 |                          0 | READY_FORWARD_TELEMETRY_SAMPLE |        |                                                                                     |                            |                       |                                                                   |              |
| binance_orderbook_forward_snapshot | G:\AlphaFactory_CryptoData\silver\binance_api\orderbook_forward_snapshot                                                         | True     |     36 |        12 | binance           | orderbook_depth                                                                                                        | 2026-05-22 01:10:27.222000+00:00 |                  36 |                          0 | READY_FORWARD_TELEMETRY_SAMPLE |      3 |                                                                                     |                            |                       |                                                                   |              |
| binance_positioning_forward_5m     | G:\AlphaFactory_CryptoData\manifests                                                                                             | True     |  36520 |        12 | binance           | globalLongShortAccountRatio,openInterestHist,takerlongshortRatio,topLongShortAccountRatio,topLongShortPositionRatio    |                                  |               36520 |                          0 | HOLD_FORWARD_MANIFEST_ERRORS   |      4 | G:\AlphaFactory_CryptoData\manifests\positioning_forward_5m_2026-05-22_manifest.csv |                        239 |                     1 | G:\AlphaFactory_CryptoData\metadata\positioning_forward_state.csv |           60 |

## Telemetry Schema Contract

| schema_section               | required_fields                                                                                                           | purpose                                                   | blocking_if_missing   |
|:-----------------------------|:--------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------|:----------------------|
| identity                     | source_id; provider; dataset; symbol; venue_symbol; feature_group                                                         | Stable routing, venue mapping, and symbol-level coverage. | True                  |
| time_contract                | collection_time; observable_time; event_time; feature_available_time; timezone                                            | PIT alignment and append-only evidence boundary.          | True                  |
| source_trace                 | raw_path; raw_sha256; source_url; request_time; response_status; collector_version                                        | Reproducibility and source audit.                         | True                  |
| forward_flags                | forward_only_flag; no_historical_backfill_flag; is_historical_backfill                                                    | Prevents accidental historical proof use.                 | True                  |
| orderbook_depth              | best_bid; best_ask; spread_bps; depth_bid_notional_5/10/20; depth_ask_notional_5/10/20; depth_imbalance_5/10/20           | Displayed liquidity telemetry.                            | False                 |
| liquidation_recent           | liquidation_buy_notional; liquidation_sell_notional; liquidation_count; large_liquidation_notional; liquidation_imbalance | Forward/recent forced-flow pressure telemetry.            | False                 |
| positioning_forward          | openInterestHist; globalLongShortAccountRatio; topLongShortAccountRatio; topLongShortPositionRatio; takerlongshortRatio   | Append-only positioning telemetry.                        | False                 |
| basis_funding_cross_exchange | funding_rate; basis; basis_rate; premium; mark_price; index_price; next_funding_time; venue                               | Cross-venue basis/funding dispersion telemetry.           | False                 |

## Append-Only Policy

| policy_id      | rule                                                                                                     | enforcement                                                                                           |
|:---------------|:---------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| A7T_APPEND_001 | All forward telemetry writes are append-only; existing raw/silver rows cannot be overwritten.            | partition by run/date; write new manifest per run; quarantine repairs in separate repair path         |
| A7T_APPEND_002 | Forward-only fields cannot be joined to historical proof windows before their collection timestamp.      | feature_available_time >= observable_time; no_historical_backfill_flag must remain true               |
| A7T_APPEND_003 | Any schema change increments collector_version and starts a new compatibility segment.                   | collector_version and schema_hash in manifest                                                         |
| A7T_APPEND_004 | May 2026 remains stress/failure-attribution only and is never used for telemetry ranking/tuning.         | May columns absent from collector, ranking, and scheduler inputs                                      |
| A7T_APPEND_005 | Telemetry may become alpha evidence only after a locked forward window and a separate replay/proof gate. | A7T cannot authorize alpha proof; later stage must freeze candidate definitions before forward window |

## Collector Schedule

| collector                          | cadence                                               | minimum_fields                                                         | primary_use                                          | historical_proof_use                             |
|:-----------------------------------|:------------------------------------------------------|:-----------------------------------------------------------------------|:-----------------------------------------------------|:-------------------------------------------------|
| cross_exchange_forward_snapshot    | hourly or 15min during experiment hours               | provider/dataset/symbol/observable_time/raw_sha256/feature_group       | forward telemetry dashboard and source coverage      | blocked                                          |
| binance_orderbook_forward_snapshot | hourly baseline; 15min optional during stress periods | best bid/ask, spread, depth notional, depth imbalance                  | liquidity state and depth telemetry                  | blocked                                          |
| binance_positioning_forward_5m     | daily append catch-up; source period remains 5m       | event_time, observable_time, collector_time, forward flags, raw sha256 | positioning telemetry and future append-only history | blocked until accumulated after collector freeze |
| daily_forward_health_report        | daily                                                 | row counts, missing symbols, stale feeds, schema hash, error count     | collector operations and proof hygiene               | audit metadata only                              |

## Evidence Boundary

| evidence_type          | allowed_now   | minimum_condition                                                                  | notes                                                                               |
|:-----------------------|:--------------|:-----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|
| source_audit           | True          | raw_path/raw_sha256/source_url/time fields present                                 | A7T can support source audit and telemetry design.                                  |
| forward_telemetry      | True          | append-only collector with manifest and schema version                             | Telemetry only; no trading authorization.                                           |
| historical_alpha_proof | False         | not allowed from forward-only snapshots                                            | Requires independent historical source contract or future append-only proof window. |
| research_candidate     | False         | candidate definitions frozen before forward window; controls/cost/lag/LOO required | A7T does not produce candidates.                                                    |
| shadow_paper_live      | False         | separate alpha proof gate                                                          | Explicitly blocked.                                                                 |

## Authorization

| decision                                   | generated_at         | executes_download   | executes_search   | executes_replay   |   ready_forward_sources |   total_forward_sources | authorizes_forward_telemetry_collection_design   | authorizes_append_only_observation   | authorizes_historical_alpha_proof   | authorizes_research_candidate   | authorizes_shadow_paper_live   | blockers                                                                                                                                                                                                   | warnings                                                         | required_next                                                                                                                                                                                         |
|:-------------------------------------------|:---------------------|:--------------------|:------------------|:------------------|------------------------:|------------------------:|:-------------------------------------------------|:-------------------------------------|:------------------------------------|:--------------------------------|:-------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PASS_A7T0_FORWARD_TELEMETRY_CONTRACT_READY | 2026-05-22T10:00:51Z | False               | False             | False             |                       2 |                       3 | True                                             | True                                 | False                               | False                           | False                          | ['forward-only snapshots cannot be historical proof', 'liquidation retention/pagination contract unresolved', 'orderbook historical source not validated', 'no candidate definitions are frozen in A7T-0'] | ['binance_positioning_forward_5m: HOLD_FORWARD_MANIFEST_ERRORS'] | ['Implement daily forward telemetry health report', 'Add collector_version/schema_hash to forward manifests', 'Keep A7AA-1 contracts for liquidation/cross-exchange historical feasibility separate'] |

## Required Next Action

1. Add `collector_version` and `schema_hash` to forward collector manifests.
2. Produce a daily forward health report covering row counts, stale feeds, missing symbols, schema drift, and error count.
3. Keep liquidation/orderbook/cross-exchange historical use blocked until A7AA-1 contracts close.
4. Do not promote telemetry to alpha evidence without a separately locked forward proof window.
