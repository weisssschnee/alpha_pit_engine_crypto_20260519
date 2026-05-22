# CRYPTO A7AB-0 Forward Data Handoff Audit

Generated: 2026-05-22T09:55:44Z

## Decision

`PASS_A7AB0_DATA_HANDOFF_ACCEPTED_FOR_SOURCE_AUDIT_AND_FORWARD_TELEMETRY`

A7AB-0 accepts the data handoff for source audit and forward telemetry design. It does not run search or replay and does not authorize historical alpha proof.

## External Handoff Summary

- Cross-exchange report rows: 153.
- Cross-exchange providers: binance, bybit, okx.
- Cross-exchange role: forward snapshot sample, not historical proof.

## Binance Metrics History

| dataset                        | path                                                                            | exists   |   rows |   columns |   symbols | timestamp_min             | timestamp_max             | decision                                |
|:-------------------------------|:--------------------------------------------------------------------------------|:---------|-------:|----------:|----------:|:--------------------------|:--------------------------|:----------------------------------------|
| binance_metrics_1h_features_v1 | G:\AlphaFactory_CryptoData\gold\features\binance_metrics_1h_features_v1.parquet | True     | 251028 |        40 |        12 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | PASS_METRICS_HISTORY_SOURCE_AUDIT_INPUT |

### Metrics Field Audit

| field                                       | present   |   non_null | independent_source   | allowed_role                    | caveat                                                   |
|:--------------------------------------------|:----------|-----------:|:---------------------|:--------------------------------|:---------------------------------------------------------|
| open_interest                               | True      |     251028 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| open_interest_value                         | True      |     251028 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| global_long_short_account_ratio             | True      |     251028 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| top_long_short_account_ratio                | True      |     251004 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| top_long_short_position_ratio               | True      |     251028 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| taker_buy_sell_volume_ratio                 | True      |     251028 | True                 | historical source-audit feature | vendor 5m jitter/gap warnings from A7S-1 remain attached |
| open_interest_change_1h                     | True      |     250919 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_change_4h                     | True      |     250883 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_change_24h                    | True      |     250643 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_zscore_168h                   | True      |     250752 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_value_change_1h               | True      |     250919 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_value_change_4h               | True      |     250883 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_value_change_24h              | True      |     250643 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_value_zscore_168h             | True      |     250752 | False                | derived transform only          | inherits parent source contract; not independent source  |
| global_long_short_account_ratio_change_1h   | True      |     251016 | False                | derived transform only          | inherits parent source contract; not independent source  |
| global_long_short_account_ratio_change_4h   | True      |     250980 | False                | derived transform only          | inherits parent source contract; not independent source  |
| global_long_short_account_ratio_change_24h  | True      |     250740 | False                | derived transform only          | inherits parent source contract; not independent source  |
| global_long_short_account_ratio_zscore_168h | True      |     250752 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_account_ratio_change_1h      | True      |     250980 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_account_ratio_change_4h      | True      |     250932 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_account_ratio_change_24h     | True      |     250692 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_account_ratio_zscore_168h    | True      |     250728 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_position_ratio_change_1h     | True      |     251016 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_position_ratio_change_4h     | True      |     250980 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_position_ratio_change_24h    | True      |     250740 | False                | derived transform only          | inherits parent source contract; not independent source  |
| top_long_short_position_ratio_zscore_168h   | True      |     250752 | False                | derived transform only          | inherits parent source contract; not independent source  |
| taker_buy_sell_volume_ratio_change_1h       | True      |     251016 | False                | derived transform only          | inherits parent source contract; not independent source  |
| taker_buy_sell_volume_ratio_change_4h       | True      |     250980 | False                | derived transform only          | inherits parent source contract; not independent source  |
| taker_buy_sell_volume_ratio_change_24h      | True      |     250740 | False                | derived transform only          | inherits parent source contract; not independent source  |
| taker_buy_sell_volume_ratio_zscore_168h     | True      |     250752 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_x_price_move_1h               | True      |     250919 | False                | derived transform only          | inherits parent source contract; not independent source  |
| open_interest_x_taker_imbalance             | True      |     250907 | False                | derived transform only          | inherits parent source contract; not independent source  |

## Cross-Exchange Forward Snapshot

| dataset                                                | path                                                                                                                             | exists   |   rows |   columns |   symbols | providers         | feature_groups                                                                                                         |   forward_only_rows |   historical_backfill_rows |   observable_time_non_null |   event_time_blank_count |   raw_sha256_non_null | decision                                                   |
|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|:---------|-------:|----------:|----------:|:------------------|:-----------------------------------------------------------------------------------------------------------------------|--------------------:|---------------------------:|---------------------------:|-------------------------:|----------------------:|:-----------------------------------------------------------|
| cross_exchange_forward_snapshot_20260522_core12_probe2 | G:\AlphaFactory_CryptoData\silver\cross_exchange_forward_snapshot\cross_exchange_forward_snapshot_20260522_core12_probe2.parquet | True     |    153 |        44 |        12 | binance,bybit,okx | basis_recent,funding,liquidation_recent,open_interest,orderbook_depth,premium_funding,recent_history,ticker_oi_funding |                  96 |                          0 |                        153 |                       24 |                   153 | PASS_FORWARD_SNAPSHOT_TELEMETRY_INPUT_NOT_HISTORICAL_PROOF |

### Cross-Exchange Feature Groups

| provider   | dataset                   | feature_group      |   rows |   symbols |   forward_only_rows |   historical_backfill_rows |
|:-----------|:--------------------------|:-------------------|-------:|----------:|--------------------:|---------------------------:|
| binance    | basis_1h_recent           | basis_recent       |      9 |         9 |                   0 |                          0 |
| binance    | current_open_interest     | open_interest      |     12 |        12 |                  12 |                          0 |
| binance    | orderbook_depth_20        | orderbook_depth    |     12 |        12 |                  12 |                          0 |
| binance    | premium_index             | premium_funding    |     12 |        12 |                  12 |                          0 |
| bybit      | current_ticker_oi_funding | ticker_oi_funding  |     12 |        12 |                  12 |                          0 |
| bybit      | funding_rate_history      | recent_history     |     12 |        12 |                   0 |                          0 |
| bybit      | open_interest_1h_recent   | recent_history     |     12 |        12 |                   0 |                          0 |
| bybit      | orderbook_depth_50        | orderbook_depth    |     12 |        12 |                  12 |                          0 |
| okx        | current_open_interest     | open_interest      |     12 |        12 |                  12 |                          0 |
| okx        | funding_rate_current      | funding            |     12 |        12 |                  12 |                          0 |
| okx        | funding_rate_history      | funding            |     12 |        12 |                   0 |                          0 |
| okx        | liquidation_orders_probe  | liquidation_recent |     12 |        12 |                   0 |                          0 |
| okx        | orderbook_depth_20        | orderbook_depth    |     12 |        12 |                  12 |                          0 |

### Cross-Exchange Schema

| column                     | dtype   |   non_null | example                                                                                                                  | field_family          |
|:---------------------------|:--------|-----------:|:-------------------------------------------------------------------------------------------------------------------------|:----------------------|
| collection_time            | str     |        153 | 2026-05-22T09:44:32Z                                                                                                     | time_contract         |
| provider                   | str     |        153 | binance                                                                                                                  | source_contract       |
| dataset                    | str     |        153 | current_open_interest                                                                                                    | source_contract       |
| symbol                     | str     |        153 | BTCUSDT                                                                                                                  | source_contract       |
| feature_group              | str     |        153 | open_interest                                                                                                            | source_contract       |
| raw_path                   | str     |        153 | G:\AlphaFactory_CryptoData\raw\source_probes\cross_exchange_20260522_core12_probe2\binance__current_open_interest__BTCUS | source_trace          |
| raw_sha256                 | str     |        153 | 5cf9bac310c222f4637fb6e9ac3ae93bb9caa01b1bd487954236e8b856e3ec7f                                                         | source_trace          |
| source_url                 | str     |        153 | https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT                                                             | source_contract       |
| history_depth              | str     |        153 | snapshot_only                                                                                                            | source_contract       |
| proof_role                 | str     |        153 | forward_observation                                                                                                      | source_contract       |
| is_forward_only            | bool    |        153 | True                                                                                                                     | source_contract       |
| is_historical_backfill     | bool    |        153 | False                                                                                                                    | source_contract       |
| timezone                   | str     |        153 | UTC                                                                                                                      | time_contract         |
| event_time                 | str     |        153 | 2026-05-22T09:44:26.020000Z                                                                                              | time_contract         |
| observable_time            | str     |        153 | 2026-05-22T09:44:32Z                                                                                                     | time_contract         |
| open_interest              | float64 |         48 | 100686.683                                                                                                               | open_interest         |
| best_bid                   | float64 |         36 | 77293.5                                                                                                                  | orderbook_depth       |
| best_ask                   | float64 |         36 | 77293.6                                                                                                                  | orderbook_depth       |
| mid                        | float64 |         36 | 77293.55                                                                                                                 | orderbook_depth       |
| spread_bps                 | float64 |         36 | 0.012937690144367901                                                                                                     | orderbook_depth       |
| depth_bid_notional_5       | float64 |         36 | 1380539.14                                                                                                               | orderbook_depth       |
| depth_ask_notional_5       | float64 |         36 | 871639.9522                                                                                                              | orderbook_depth       |
| depth_imbalance_5          | float64 |         36 | 0.225958579210009                                                                                                        | orderbook_depth       |
| depth_bid_notional_10      | float64 |         36 | 1396615.9357                                                                                                             | orderbook_depth       |
| depth_ask_notional_10      | float64 |         36 | 902557.8818                                                                                                              | orderbook_depth       |
| depth_imbalance_10         | float64 |         36 | 0.21488503832964342                                                                                                      | orderbook_depth       |
| depth_bid_notional_20      | float64 |         36 | 1438817.0182000005                                                                                                       | orderbook_depth       |
| depth_ask_notional_20      | float64 |         36 | 932162.1451999999                                                                                                        | orderbook_depth       |
| depth_imbalance_20         | float64 |         36 | 0.21369014153353166                                                                                                      | orderbook_depth       |
| depth_thinness_20          | float64 |         36 | 4.2176667574167677e-07                                                                                                   | orderbook_depth       |
| mark_price                 | float64 |         24 | 77290.06939167                                                                                                           | funding_basis_premium |
| index_price                | float64 |         24 | 77325.54475                                                                                                              | funding_basis_premium |
| last_funding_rate          | float64 |         12 | 1.111e-05                                                                                                                | funding_basis_premium |
| next_funding_time          | str     |         36 | 2026-05-22T16:00:00Z                                                                                                     | funding_basis_premium |
| basis                      | float64 |          9 | -38.475                                                                                                                  | funding_basis_premium |
| basis_rate                 | float64 |          9 | -0.0005                                                                                                                  | funding_basis_premium |
| open_interest_ccy          | float64 |         12 | 32570.658600000228                                                                                                       | open_interest         |
| funding_rate               | float64 |         48 | 5.69304999139e-05                                                                                                        | funding_basis_premium |
| liquidation_buy_notional   | float64 |         12 | 253984480.34099984                                                                                                       | liquidation_recent    |
| liquidation_sell_notional  | float64 |         12 | 476691907.28799975                                                                                                       | liquidation_recent    |
| liquidation_count          | float64 |         12 | 1140.0                                                                                                                   | liquidation_recent    |
| large_liquidation_notional | float64 |         12 | 59946412.28                                                                                                              | liquidation_recent    |
| liquidation_imbalance      | float64 |         12 | -0.30479625552109596                                                                                                     | liquidation_recent    |
| open_interest_value        | float64 |         12 | 4044967698.44                                                                                                            | open_interest         |

## Probe Manifest Summary

| provider   | dataset                   |   rows |   ready |   http_hold | symbols                                                                                            | decision              |
|:-----------|:--------------------------|-------:|--------:|------------:|:---------------------------------------------------------------------------------------------------|:----------------------|
| binance    | basis_1h_recent           |     12 |       9 |           3 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | WARN_INCOMPLETE_PROBE |
| binance    | current_open_interest     |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| binance    | orderbook_depth_20        |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| binance    | premium_index             |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| bybit      | current_ticker_oi_funding |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| bybit      | funding_rate_history      |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| bybit      | open_interest_1h_recent   |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| bybit      | orderbook_depth_50        |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| okx        | current_open_interest     |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| okx        | funding_rate_current      |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| okx        | funding_rate_history      |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| okx        | liquidation_orders_probe  |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |
| okx        | orderbook_depth_20        |     12 |      12 |           0 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | PASS_READY            |

## Use Policy

| data_line                       | historical_experiment_allowed   | forward_telemetry_allowed   | alpha_proof_allowed   | use_boundary                                                                                       |
|:--------------------------------|:--------------------------------|:----------------------------|:----------------------|:---------------------------------------------------------------------------------------------------|
| binance_metrics_history         | True                            | True                        | False                 | Can enter A7S-1 source audit and controlled historical experiments with vendor 5m warning caveat.  |
| cross_exchange_forward_snapshot | False                           | True                        | False                 | Use for forward-only telemetry design and source audit sample; do not backfill historical proof.   |
| okx_liquidation_recent          | False                           | True                        | False                 | Recent/forward liquidation pressure source only until retention/pagination/PIT contract is closed. |
| orderbook_depth_snapshot        | False                           | True                        | False                 | Forward collector only unless a validated historical depth source is contracted.                   |

## Authorization

| decision                                                                | generated_at         | executes_search   | executes_replay   | metrics_gold_ready   | cross_exchange_forward_snapshot_ready   |   probe_ready_endpoints |   probe_total_endpoints | authorizes_metrics_historical_source_audit   | authorizes_cross_exchange_forward_telemetry_design   | authorizes_historical_alpha_proof_from_cross_exchange_snapshot   | authorizes_alpha_proof   | authorizes_shadow_paper_live   | blockers                                                                                                                                                                                                                                 | required_next                                                                                                                                                                                                                                 |
|:------------------------------------------------------------------------|:---------------------|:------------------|:------------------|:---------------------|:----------------------------------------|------------------------:|------------------------:|:---------------------------------------------|:-----------------------------------------------------|:-----------------------------------------------------------------|:-------------------------|:-------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PASS_A7AB0_DATA_HANDOFF_ACCEPTED_FOR_SOURCE_AUDIT_AND_FORWARD_TELEMETRY | 2026-05-22T09:55:44Z | False             | False             | True                 | True                                    |                     153 |                     156 | True                                         | True                                                 | False                                                            | False                    | False                          | ['cross-exchange snapshot is forward-only', 'OKX liquidation retention/pagination contract unresolved', 'orderbook snapshots cannot be backfilled into historical proof', 'Binance basis probe has 3 rate-limit holds in core12_probe2'] | ['Use Binance metrics history in A7S-1 controlled source audit with vendor warning caveat', 'Design A7T forward telemetry from cross-exchange snapshot fields', 'Do not run historical alpha proof on liquidation/orderbook snapshot fields'] |

## Required Next Action

1. Give experiment side `binance_metrics_1h_features_v1.parquet` as historical source-audit input with vendor 5m warning caveat.
2. Use `cross_exchange_forward_snapshot_20260522_core12_probe2.parquet` only for forward telemetry design.
3. Keep liquidation/orderbook as forward/recent context until PIT retention and historical source contracts close.
4. Keep derived transforms out of independent-source counts.
