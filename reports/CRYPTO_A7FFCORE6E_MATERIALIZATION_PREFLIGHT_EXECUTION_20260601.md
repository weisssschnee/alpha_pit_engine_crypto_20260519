# CRYPTO A7FF-CORE6E MATERIALIZATION PREFLIGHT EXECUTION

Generated: 2026-05-31T18:51:54Z

## Decision

`PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7`

A7FF-CORE6E materializes the CORE5 gate-native queue for finite/activity diagnostics only. It does not compute labels, returns, IC, spread, PnL, replay metrics, selector scores, search, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core7": true,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7",
  "eval_error_count": 0,
  "eval_failure_rate": 0.0,
  "executes_materialization": true,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T18:51:54Z",
  "label_or_may_token_count": 0,
  "latent_panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
  "mean_active_ratio": 0.98326641796875,
  "mean_non_null_ratio": 0.9850193154296876,
  "missing_field_candidate_count": 0,
  "missing_field_rate": 0.0,
  "missing_panel_fields": [],
  "next_allowed": "A7FF-CORE7 gate-native numeric-response contract",
  "ok_count": 2048,
  "panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "panel_rows": 6949596,
  "panel_symbols": 498,
  "queue_rows": 2048,
  "shard_count": 8,
  "source_decision": "PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E",
  "source_stage": "A7FF-CORE6",
  "stage": "A7FF-CORE6E",
  "uses_may": false
}
```

## Status Summary

| status   |   candidates |   mean_non_null_ratio |   mean_active_ratio |
|:---------|-------------:|----------------------:|--------------------:|
| ok       |         2048 |              0.985019 |            0.983266 |

## Shard Summary

|   candidate_count |   eval_error_count |   label_or_may_token_count |   mean_active_ratio |   mean_non_null_ratio |   missing_field_count |   ok_count | output                                                                          | shard_id   |
|------------------:|-------------------:|---------------------------:|--------------------:|----------------------:|----------------------:|-----------:|:--------------------------------------------------------------------------------|:-----------|
|               256 |                  0 |                          0 |            0.973273 |              0.978855 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S00_materialization.csv | S00        |
|               256 |                  0 |                          0 |            0.98849  |              0.990216 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S01_materialization.csv | S01        |
|               256 |                  0 |                          0 |            0.992219 |              0.995356 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S02_materialization.csv | S02        |
|               256 |                  0 |                          0 |            0.997124 |              0.998023 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S03_materialization.csv | S03        |
|               256 |                  0 |                          0 |            0.987669 |              0.987857 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S04_materialization.csv | S04        |
|               256 |                  0 |                          0 |            0.976324 |              0.97774  |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S05_materialization.csv | S05        |
|               256 |                  0 |                          0 |            0.974358 |              0.975118 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S06_materialization.csv | S06        |
|               256 |                  0 |                          0 |            0.976674 |              0.976987 |                     0 |        256 | runtime\a7ffcore6e_materialization_preflight\a7ffcore6e_S07_materialization.csv | S07        |

## Field Presence

| field                                | present   | source   |
|:-------------------------------------|:----------|:---------|
| age_x_liquidity                      | True      | loaded   |
| age_x_volatility                     | True      | loaded   |
| global_long_short_account_ratio_last | True      | loaded   |
| global_long_short_account_ratio_mean | True      | loaded   |
| index_close                          | True      | loaded   |
| liquidity_rank_active_universe       | True      | loaded   |
| log_quote_volume_168h                | True      | loaded   |
| mark_close                           | True      | loaded   |
| mark_high                            | True      | loaded   |
| mark_index_basis_bps                 | True      | loaded   |
| mark_low                             | True      | loaded   |
| median_quote_volume_168h             | True      | loaded   |
| open_interest_change_24h             | True      | loaded   |
| open_interest_last                   | True      | loaded   |
| open_interest_mean                   | True      | loaded   |
| open_interest_value_last             | True      | loaded   |
| open_interest_value_mean             | True      | loaded   |
| realized_vol_168h                    | True      | loaded   |
| realized_vol_24h                     | True      | loaded   |
| taker_buy_quote_volume               | True      | loaded   |
| taker_buy_sell_volume_ratio_last     | True      | loaded   |
| taker_buy_sell_volume_ratio_mean     | True      | loaded   |
| taker_buy_volume                     | True      | loaded   |
| top_long_short_account_ratio_last    | True      | loaded   |
| top_long_short_account_ratio_mean    | True      | loaded   |
| trade_close                          | True      | loaded   |
| trade_count                          | True      | loaded   |
| trade_count_168h                     | True      | loaded   |
| trade_high                           | True      | loaded   |
| trade_low                            | True      | loaded   |
| trade_quote_volume                   | True      | loaded   |
| trade_return_1h                      | True      | loaded   |
| trade_return_24h                     | True      | loaded   |
| trade_volume                         | True      | loaded   |
| volume_volatility_ratio_168h         | True      | loaded   |

## Family Status Summary

| semantic_bucket                      | motif_bucket        | status   |   candidates |   mean_non_null_ratio |   mean_active_ratio |
|:-------------------------------------|:--------------------|:---------|-------------:|----------------------:|--------------------:|
| liquidity_like\|volatility_like      | liquidity_shock     | ok       |          370 |              0.976933 |            0.976439 |
| liquidity_like\|volatility_like      | mean_reversion_gate | ok       |          360 |              0.97837  |            0.976945 |
| liquidity_like\|volatility_like      | safe_div_abs        | ok       |          320 |              0.978148 |            0.977824 |
| open_interest_like\|positioning_like | delta_x_divergence  | ok       |          192 |              0.997658 |            0.994905 |
| taker_flow_like\|basis_premium_like  | gated_sign          | ok       |          192 |              0.998383 |            0.997185 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     | ok       |          192 |              0.996063 |            0.996063 |
| open_interest_like\|price_like       | mean_reversion_gate | ok       |          148 |              0.99398  |            0.990099 |
| liquidity_like                       | single              | ok       |           98 |              0.965833 |            0.952301 |
| open_interest_like\|price_like       | delta_x_divergence  | ok       |           44 |              0.996222 |            0.993757 |
| taker_flow_like                      | single              | ok       |           38 |              0.997988 |            0.997809 |
| open_interest_like                   | delta_x_divergence  | ok       |           20 |              0.998127 |            0.998111 |
| open_interest_like                   | flow_x_leverage     | ok       |           20 |              0.998127 |            0.998111 |
| open_interest_like                   | single              | ok       |           20 |              0.967859 |            0.967857 |
| volatility_like                      | single              | ok       |           14 |              0.954701 |            0.954258 |
| liquidity_like                       | liquidity_shock     | ok       |           10 |              0.999197 |            0.998685 |
| taker_flow_like                      | flow_x_leverage     | ok       |           10 |              0.999197 |            0.998773 |

## Boundary

```text
materialization executed: true
numeric response: false
labels/returns/IC/spread/PnL: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
