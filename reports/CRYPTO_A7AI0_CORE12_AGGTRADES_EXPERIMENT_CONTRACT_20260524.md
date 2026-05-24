# CRYPTO A7AI-0 Core12 aggTrades Experiment Contract

Generated: 2026-05-24T04:47:04Z

## Decision

```text
PASS_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_READY
```

This stage defines the controlled experiment contract for the accepted core12 aggTrades handoff. It does not run replay and does not run search.

## Summary

```json
{
  "core12_rows": 251028,
  "decision": "PASS_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_READY",
  "executes_replay": false,
  "executes_search": false,
  "field_count": 20,
  "generated_at": "2026-05-24T04:47:04Z",
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ai0_core12_aggtrades_experiment_contract",
  "panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_20260524.md"
}
```

## Authorization

```json
{
  "authorizes_a7ai1_small_controlled_raw_agg_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_READY",
  "may_policy": "May is post-selection stress only and is core3-current-month caveated; do not rank or tune on it",
  "warnings": [
    "final_panel_contains_raw_enhanced_agg_fields_not_precomputed_rolling_cross_symbol_agg_features",
    "may_2026_agg_coverage_is_core3_current_month_caveat_not_core12_monthly_history",
    "A7AI0 is contract only; no replay and no alpha evidence"
  ]
}
```

## Split Manifest

| split                    | start                     | end                       | usage                                                 |   rows |   symbols |   agg_available_rows |   agg_available_symbol_count | may_allowed_for_ranking   |
|:-------------------------|:--------------------------|:--------------------------|:------------------------------------------------------|-------:|----------:|---------------------:|-----------------------------:|:--------------------------|
| train_2024               | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 | selection_training_only                               | 105288 |        12 |               105288 |                           12 | True                      |
| validation_2025H1        | 2025-01-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 | ranking_allowed_non_may                               |  52128 |        12 |                52128 |                           12 | True                      |
| recent_2025H2_2026Apr    | 2025-07-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | ranking_allowed_non_may                               |  87552 |        12 |                87552 |                           12 | True                      |
| may_2026_stress_caveated | 2026-05-01T00:00:00+00:00 | 2026-05-20T23:00:00+00:00 | post_selection_stress_only_core3_current_month_caveat |   5760 |        12 |                 1440 |                            3 | False                     |

## Experiment Field Contract

| field_name                                | source_family       | status              | usage_note                                              | present   |   core12_non_null_rate |   min_symbol_rate |   median_symbol_rate |   max_symbol_rate |
|:------------------------------------------|:--------------------|:--------------------|:--------------------------------------------------------|:----------|-----------------------:|------------------:|---------------------:|------------------:|
| agg_volume_imbalance                      | agg_flow_balance    | allowed             | bounded [-1,1] hourly buy/sell volume pressure          | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_signed_aggressor_notional             | agg_flow_size       | allowed_with_zscore | raw notional must be normalized before ranking          | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_buy_sell_notional_ratio               | agg_flow_balance    | allowed_with_clip   | ratio can be heavy-tailed; clip/winsor before use       | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_large_notional_ratio_100k_plus        | agg_large_trade     | allowed             | large trade notional share                              | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_large_trade_count_ratio_100k_plus     | agg_large_trade     | allowed             | large trade count share                                 | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_max_trade_notional                    | agg_large_trade     | allowed_with_zscore | raw notional must be normalized                         | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_price_range_bps                       | agg_intrahour_price | allowed             | hour range from aggTrades                               | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_close_to_open_bps                     | agg_intrahour_price | allowed             | intra-hour direction proxy                              | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_vwap                                  | agg_micro_price     | derive_only         | raw VWAP; use with close price to derive vwap-close bps | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_close_price                           | agg_micro_price     | derive_only         | raw close price for derived vwap-close bps              | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_buy_vwap                              | agg_micro_price     | derive_only         | raw buy VWAP for derived buy-sell VWAP spread           | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_sell_vwap                             | agg_micro_price     | derive_only         | raw sell VWAP for derived buy-sell VWAP spread          | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_trade_count                           | agg_trade_structure | derive_only         | used with underlying trade count                        | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| agg_underlying_trade_count                | agg_trade_structure | derive_only         | used to derive avg underlying trades per agg            | True      |               0.981596 |          0.975859 |             0.975859 |          0.998805 |
| open_interest_change_24h                  | positioning_context | context_only        | interaction context, not aggTrades source               | True      |               0.998466 |          0.997419 |             0.998542 |          0.998662 |
| mark_index_basis_change_24h               | basis_context       | context_only        | interaction context                                     | True      |               0.998805 |          0.998805 |             0.998805 |          0.998805 |
| premium_index_change_24h                  | basis_context       | context_only        | interaction context                                     | True      |               0.981165 |          0.787131 |             0.998805 |          0.998805 |
| top_long_short_position_ratio_zscore_168h | crowding_context    | context_only        | interaction context                                     | True      |               0.998901 |          0.998901 |             0.998901 |          0.998901 |
| ret_24                                    | price_context       | context_only        | trend/reversal context                                  | True      |               0.998853 |          0.998853 |             0.998853 |          0.998853 |
| funding_rate_bps                          | funding_baseline    | baseline_only       | residual/control baseline                               | True      |               0.999952 |          0.999952 |             0.999952 |          0.999952 |

## Derived-In-Runner Contract

| derived_transform             | rule                                                                   |
|:------------------------------|:-----------------------------------------------------------------------|
| ts_zscore_24h                 | past-only rolling zscore over 24h                                      |
| ts_zscore_72h                 | past-only rolling zscore over 72h                                      |
| ts_delta_4h                   | past-only 4h change                                                    |
| ts_delta_24h                  | past-only 24h change                                                   |
| rank_cross_symbol_core12      | cross-sectional rank among symbols with agg availability               |
| interaction_mul_context       | agg field x context field; no standalone activity promotion            |
| vwap_close_bps                | (agg_vwap / agg_close_price - 1) * 10000, guarded for zero close       |
| buy_sell_vwap_spread_bps      | (agg_buy_vwap / agg_sell_vwap - 1) * 10000, guarded for zero sell vwap |
| avg_underlying_trades_per_agg | agg_underlying_trade_count / agg_trade_count, guarded for zero count   |

## Blocked Pattern Registry

| pattern                                      | status   | reason                                                                |
|:---------------------------------------------|:---------|:----------------------------------------------------------------------|
| blind_654_column_search                      | blocked  | wide panel includes non-selected, derived, and benchmark fields       |
| standalone_raw_notional_level                | blocked  | size/liquidity level without normalization is capacity/exposure proxy |
| may_tuned_symbol_subset                      | blocked  | May agg coverage is core3 current-month caveated only                 |
| core12_may_stress_claim_without_rem9_may_agg | blocked  | rem9 has agg through 2026-04 only                                     |
| funding_standalone_promotion                 | blocked  | funding remains benchmark/control                                     |

## Boundary

- Use selected aggTrades fields only; no blind 654-column search.
- Raw notional/size fields require zscore/rank/normalization before use.
- May 2026 agg coverage is not full core12 monthly history and cannot be used for ranking/tuning.
- Funding remains baseline/control only.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
