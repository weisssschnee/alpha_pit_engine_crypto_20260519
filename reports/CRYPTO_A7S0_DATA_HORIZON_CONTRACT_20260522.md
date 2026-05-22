# Crypto A7S-0 Data / Horizon Contract

- generated_at: `2026-05-22T07:08:33Z`
- decision: `PASS_A7S0_DATA_HORIZON_CONTRACT_READY`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7S-0 defines what data and horizons may enter the next crypto research stage after A7X-4. It does not run alpha search.

The key distinction is historical-proof eligible vs forward-only. Forward-only fields can support observation and future locked tests, not 2024-2026 historical proof.

## Source Inventory

| source_id                                    | local_path                                                                                 | current_status                         | historical_proof_allowed   | forward_only   | pit_requirements                                                                                                       | next_action                                                                                          | path_exists   |   panel_rows |   panel_columns |   agg_feature_columns |   agg_symbol_month_count |
|:---------------------------------------------|:-------------------------------------------------------------------------------------------|:---------------------------------------|:---------------------------|:---------------|:-----------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|:--------------|-------------:|----------------:|----------------------:|-------------------------:|
| unified_core12_1h_with_aggtrades_features_v1 | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet | READY_PANEL_FOR_CONTROLLED_EXPERIMENTS | True                       | False          | inherits base panel plus aggTrades feature availability mask                                                           | primary experiment input for controlled diagnostics only                                             | True          |       251148 |             184 |                    94 |                       87 |
| base_core12_1h_market_funding_mark_index     | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet                         | READY_EXISTING_PANEL                   | True                       | False          | existing A7 linkage/funding contracts remain binding; feature_time < execution_time                                    | usable as baseline panel only; do not treat prior funding-family results as alpha proof              | True          |          nan |             nan |                   nan |                      nan |
| aggtrades_enhanced_v1_core3                  | G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_enhanced_v1               | READY_CORE3_SOURCE_TRACE_PASS          | True                       | False          | timestamp is hour bucket start; feature observable only after hour close; raw checksum/source trace must remain closed | use as state/interaction/horizon feature; do not expand failed activity-liquidity standalone family  | True          |          nan |             nan |                   nan |                      nan |
| aggtrades_enhanced_v1_remaining_core12       | G:\AlphaFactory_CryptoData\gold\microstructure\aggtrades_1h_flow_enhanced_v1               | MISSING_FOR_9_CORE12_SYMBOLS           | False                      | False          | same raw zip checksum/source trace as A7U-0R before experiment use                                                     | data-line can backfill; experiment-line must wait for source trace pass before core12 agg search     | True          |          nan |             nan |                   nan |                      nan |
| orderbook_forward_snapshot                   | G:\AlphaFactory_CryptoData\silver\binance_api\orderbook_forward_snapshot                   | FORWARD_ONLY_AVAILABLE                 | False                      | True           | collector_time/observable_time/event_time retained; no historical backfill into 2024-2026 proof                        | use only for A7T forward observation/live-shadow context until sufficient append-only history exists | True          |          nan |             nan |                   nan |                      nan |
| positioning_forward_oi_longshort_taker_ratio | G:\AlphaFactory_CryptoData\metadata\positioning_forward_state.csv                          | FORWARD_ONLY_AVAILABLE                 | False                      | True           | event_time/observable_time/collector_time and forward_only_flag required; no historical proof use                      | append-only observation only; historical use requires separate PIT contract and raw trace            | True          |          nan |             nan |                   nan |                      nan |
| liquidation_forced_flow                      |                                                                                            | NOT_PRESENT_CONTRACT_REQUIRED          | False                      | False          | event_time and exchange publication semantics; no future aggregate leakage; raw/source trace required                  | high-value candidate source after data contract, sample audit, and checksum trace                    | False         |          nan |             nan |                   nan |                      nan |
| cross_exchange_basis_funding_depth           |                                                                                            | NOT_PRESENT_CONTRACT_REQUIRED          | False                      | False          | venue-specific observable_time, symbol mapping, trading calendar, fee/cost convention, and missingness contract        | do not search before venue/PIT/symbol contract                                                       | False         |          nan |             nan |                   nan |                      nan |

## Panel Coverage

| symbol   |   panel_rows |   agg_rows |   agg_coverage | timestamp_min             | timestamp_max             | agg_status             |
|:---------|-------------:|-----------:|---------------:|:--------------------------|:--------------------------|:-----------------------|
| ADAUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| AVAXUSDT |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| BCHUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| BNBUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| BTCUSDT  |        20929 |      20904 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_ready_core3        |
| DOGEUSDT |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| ETHUSDT  |        20929 |      20904 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_ready_core3        |
| LINKUSDT |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| LTCUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| SOLUSDT  |        20929 |      20904 |       0.998805 | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_ready_core3        |
| SUIUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |
| XRPUSDT  |        20929 |          0 |       0        | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 | agg_missing_for_symbol |

## PIT Timestamp Contract

| field_family                     | timestamp_semantics                                    | observable_time_rule                                    | historical_proof_status                                | forbidden_use                                               |
|:---------------------------------|:-------------------------------------------------------|:--------------------------------------------------------|:-------------------------------------------------------|:------------------------------------------------------------|
| base_1h_ohlcv_mark_index_premium | 1h bar bucket start                                    | bar close plus processing lag; usable next bar or later | allowed_if_existing_A7_alignment_holds                 | same-bar close execution or feature_time >= execution_time  |
| funding_observable               | funding event / known funding field time               | latest-known only; settlement-after-use forbidden       | allowed only under A7D/A7E funding semantics           | next_funding_rate or future settlement rate as signal       |
| aggtrades_enhanced_1h            | floor(event_time, 1h) bucket start                     | 1h aggregate visible only after hour end                | allowed for BTC/ETH/SOL after A7U-0R source trace pass | using current hour aggregate for execution inside same hour |
| orderbook_forward_snapshot       | collector_time / observable_time / event_time snapshot | forward-only snapshot visible after collector_time      | not allowed for 2024-2026 historical proof             | backfill into historical search or May stress proof         |
| positioning_forward              | API event_time plus collector_time                     | append-only forward observation only                    | not allowed until separate historical PIT contract     | retroactive history fill for alpha proof                    |

## Feature Family Contract

| feature_family                          | allowed_role                                   | blocked_role                                                     | must_report                                                                        |
|:----------------------------------------|:-----------------------------------------------|:-----------------------------------------------------------------|:-----------------------------------------------------------------------------------|
| aggtrades_flow_state                    | state/interactor/horizon diagnostic            | standalone activity/liquidity alpha expansion                    | standalone ablation; matched controls; 20bps; lag stress; May stress-only label    |
| aggtrades_large_trade_intensity         | liquidity stress / size regime feature         | raw large-trade bucket rank as candidate without controls        | control dominance and symbol-tier attribution                                      |
| basis_premium_interaction               | interaction with aggTrades or volatility state | funding/basis wrapper without residual vs FundingCore/Core4      | FundingCore/Core4 residual and wrong-lag funding warning                           |
| orderbook_depth_forward                 | forward observation context                    | historical alpha proof                                           | append-only collector_time/observable_time audit                                   |
| liquidation_forced_flow_future_contract | new data candidate after PIT/source contract   | search before field semantics and publication delay are verified | event-time availability, liquidation side convention, venue coverage, source trace |

## Horizon / Execution Contract

| horizon_class   | signal_frequency                                  | execution_lags_required   |   primary_cost_bps | stress_cost_bps   | success_metric_for_diagnostic                                     | authorization                   |
|:----------------|:--------------------------------------------------|:--------------------------|-------------------:|:------------------|:------------------------------------------------------------------|:--------------------------------|
| H4              | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H8              | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H12             | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H24             | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H48             | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H72             | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| H96             | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| mixed_H12_H48   | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |
| mixed_H24_H96   | 1h source panel with slower aggregation/rebalance | 1bar;2bar;3bar            |                 10 | 20;30             | cost/lag survival improves without negative-control contamination | diagnostic_only_not_alpha_proof |

## Cost / Lag Contract

| scenario             |   cost_bps | execution_lag   | required_for                              |
|:---------------------|-----------:|:----------------|:------------------------------------------|
| normal               |         10 | 1bar            | all diagnostics                           |
| stress               |         20 | 1bar            | candidate clue label                      |
| severe               |         30 | 2bar;3bar       | horizon reset comparison                  |
| zero_cost_diagnostic |          0 | 1bar            | failure attribution only, never promotion |

## Authorization

```json
{
  "agg_feature_columns": 94,
  "agg_symbol_month_count": 87,
  "authorizes_a7r_horizon_diagnostic_contract": true,
  "authorizes_a7s1_field_availability_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7S0_DATA_HORIZON_CONTRACT_READY",
  "executes_replay": false,
  "executes_search": false,
  "forward_only_fields_allowed_for_historical_proof": false,
  "generated_at": "2026-05-22T07:08:33Z",
  "may_policy": "stress_only_not_ranking_generation_threshold_or_allocation",
  "panel_columns": 184,
  "panel_exists": true,
  "panel_rows": 251148,
  "required_next": [
    "A7S-1 audit any newly delivered OI/liquidation/orderbook/cross-exchange data before search",
    "A7R horizon diagnostic may run only as diagnostic, not alpha proof",
    "A7T forward-locked observation contract for forward-only fields"
  ],
  "unified_panel": "G:\\AlphaFactory_CryptoData\\gold\\panels\\crypto_core12_1h_with_aggtrades_features_v1.parquet"
}
```

## Required Next

- A7S-1 field availability/source-trace audit when additional data arrives.
- A7R/A7S horizon diagnostic only after the contract is frozen.
- No historical proof use of orderbook or positioning forward fields until append-only history exists.