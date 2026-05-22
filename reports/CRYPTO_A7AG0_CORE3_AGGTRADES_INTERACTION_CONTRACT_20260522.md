# CRYPTO A7AG-0 Core3 aggTrades Interaction Contract

Generated: 2026-05-22T15:18:39Z

## Decision

```text
PASS_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_READY
```

This stage validates the core3 aggTrades-enhanced panel for a small interaction smoke. It does not run replay and does not run search.

## Summary

```json
{
  "agg_features_available_rate": 0.998804914192839,
  "columns_read": 18,
  "decision": "PASS_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_READY",
  "duplicate_keys": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T15:18:39Z",
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ag0_core3_aggtrades_interaction_contract",
  "panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core3_all_features_metrics_market_structure_aggtrades_v1.parquet",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_20260522.md",
  "rows": 62757,
  "symbols": [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT"
  ],
  "timestamp_max": "2026-05-22 00:00:00+00:00",
  "timestamp_min": "2024-01-01 00:00:00+00:00"
}
```

## Authorization

```json
{
  "authorizes_a7ag1_small_controlled_interaction_smoke": true,
  "authorizes_aggtrades_standalone_activity_expansion": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_READY",
  "may_policy": "May 2026 stress-only; not ranking, field selection, symbol weighting, or threshold tuning",
  "warnings": [
    "A7AG0 is a contract only; no replay and no alpha evidence",
    "A7V activity/liquidity standalone family remains rejected"
  ]
}
```

## Split Manifest

| split                 | start                     | end                       | usage                      |   rows |   symbols |   expected_rows_if_full |   row_coverage | may_allowed_for_ranking   | feature_time_rule                                           | execution_rule                                     |
|:----------------------|:--------------------------|:--------------------------|:---------------------------|-------:|----------:|------------------------:|---------------:|:--------------------------|:------------------------------------------------------------|:---------------------------------------------------|
| train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 | selection_training_only    |  26322 |         3 |                   26352 |       0.998862 | True                      | aggTrades 1h bucket feature available only after hour close | execution_time >= next 1h bar; lag stress required |
| validation_2025H1     | 2025-01-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 | ranking_allowed_non_may    |  13032 |         3 |                   13032 |       1        | True                      | aggTrades 1h bucket feature available only after hour close | execution_time >= next 1h bar; lag stress required |
| recent_2025H2_2026Apr | 2025-07-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | ranking_allowed_non_may    |  21888 |         3 |                   21888 |       1        | True                      | aggTrades 1h bucket feature available only after hour close | execution_time >= next 1h bar; lag stress required |
| may_2026_stress       | 2026-05-01T00:00:00+00:00 | 2026-05-20T23:00:00+00:00 | post_selection_stress_only |   1440 |         3 |                    1440 |       1        | False                     | aggTrades 1h bucket feature available only after hour close | execution_time >= next 1h bar; lag stress required |

## Interaction Field Contract

| field_name                                | source_family          | status                      | usage_note                                              | present   |   non_null_rate |   min_symbol_rate |   median_symbol_rate |   max_symbol_rate |
|:------------------------------------------|:-----------------------|:----------------------------|:--------------------------------------------------------|:----------|----------------:|------------------:|---------------------:|------------------:|
| agg_signed_flow_z_24h                     | aggtrades_flow         | state_interaction_allowed   | signed aggressor flow shock; not standalone alpha       | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_flow_imbalance_notional_24h           | aggtrades_flow         | state_interaction_allowed   | 24h buy/sell pressure balance                           | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_large_notional_share_24h              | aggtrades_large_trade  | state_interaction_allowed   | large trade share, capped as context                    | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_cross_symbol_signed_flow_share        | aggtrades_cross_symbol | state_interaction_allowed   | core3 relative signed flow share                        | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| agg_notional_accel_4h_vs_24h              | aggtrades_activity     | state_interaction_allowed   | activity acceleration; standalone blocked               | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_flow_accel_4h_vs_24h                  | aggtrades_flow         | state_interaction_allowed   | signed flow acceleration                                | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_large_notional_share_4h               | aggtrades_large_trade  | state_interaction_allowed   | shorter large-trade pressure                            | True      |        0.998757 |          0.998757 |             0.998757 |          0.998757 |
| agg_cross_symbol_large_notional_share     | aggtrades_cross_symbol | state_interaction_allowed   | large trade cross-symbol share                          | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| mark_index_basis_change_24h               | basis_market_structure | interaction_context_allowed | basis dynamic context                                   | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| premium_index_change_24h                  | basis_market_structure | interaction_context_allowed | premium dynamic context                                 | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| open_interest_change_24h                  | positioning            | interaction_context_allowed | positioning pressure context                            | True      |        0.998152 |          0.997419 |             0.99847  |          0.998566 |
| top_long_short_position_ratio_zscore_168h | positioning_crowding   | interaction_context_allowed | crowding context                                        | True      |        0.998901 |          0.998901 |             0.998901 |          0.998901 |
| flow_pressure_score_v1                    | derived_existing_flow  | benchmark_context_only      | existing derived flow benchmark, not independent source | True      |        0.997992 |          0.997992 |             0.997992 |          0.997992 |

## Field Availability

| field_name                                | present   |   non_null_rate |   min_symbol_rate |   median_symbol_rate |   max_symbol_rate |
|:------------------------------------------|:----------|----------------:|------------------:|---------------------:|------------------:|
| agg_cross_symbol_large_notional_share     | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| agg_cross_symbol_signed_flow_share        | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| agg_features_available                    | True      |        1        |          1        |             1        |          1        |
| agg_flow_accel_4h_vs_24h                  | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_flow_imbalance_notional_24h           | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_large_notional_share_24h              | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_large_notional_share_4h               | True      |        0.998757 |          0.998757 |             0.998757 |          0.998757 |
| agg_notional_accel_4h_vs_24h              | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| agg_signed_flow_z_24h                     | True      |        0.998279 |          0.998279 |             0.998279 |          0.998279 |
| flow_pressure_score_v1                    | True      |        0.997992 |          0.997992 |             0.997992 |          0.997992 |
| mark_index_basis_change_24h               | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| open_interest_change_24h                  | True      |        0.998152 |          0.997419 |             0.99847  |          0.998566 |
| premium_index_change_24h                  | True      |        0.998805 |          0.998805 |             0.998805 |          0.998805 |
| ret_1                                     | True      |        0.999952 |          0.999952 |             0.999952 |          0.999952 |
| ret_24                                    | True      |        0.998853 |          0.998853 |             0.998853 |          0.998853 |
| symbol                                    | True      |        1        |          1        |             1        |          1        |
| timestamp                                 | True      |        1        |          1        |             1        |          1        |
| top_long_short_position_ratio_zscore_168h | True      |        0.998901 |          0.998901 |             0.998901 |          0.998901 |

## Blocked Pattern Registry

| pattern                                    | status   | reason                                                                |
|:-------------------------------------------|:---------|:----------------------------------------------------------------------|
| agg_activity_liquidity_self_reproduction   | blocked  | A7V rejected activity/liquidity clue family after source trace pass   |
| raw_agg_notional_or_trade_count_standalone | blocked  | standalone activity level can be control-contaminated and May-fragile |
| core3_agg_projected_to_core39              | blocked  | aggTrades panel covers BTC/ETH/SOL only                               |
| may_tuned_symbol_specific_btc_eth_sol_rule | blocked  | May is stress-only and cannot tune symbol weights                     |
| blind_699_column_search                    | blocked  | wide table includes derived fields; selected contract required        |

## Boundary

- Core3 aggTrades fields cover BTCUSDT, ETHUSDT, and SOLUSDT only.
- aggTrades activity/liquidity standalone family remains blocked by A7V.
- A7AG-1, if run, must use aggTrades only as interaction/state inputs.
- May is stress-only and cannot tune symbols, weights, thresholds, generation, or ranking.
- No formula search, large search, alpha proof, shadow, paper, or live is authorized.
