# CRYPTO A7FF-CORE1 AST SCHEMA ADAPTER

Generated: 2026-05-31T17:22:27Z

## Decision

`PASS_A7FFCORE1_AST_SCHEMA_ADAPTER_READY_FOR_CORE2`

A7FF-CORE1 validates a typed AST adapter over the repaired A7FF-55R3 formula atlas. It parses expression strings, renders them back, and audits node inventories. It does not execute generation, numeric evaluation, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core2": true,
  "authorizes_generation": false,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE1_AST_SCHEMA_ADAPTER_READY_FOR_CORE2",
  "executes_generation": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "field_types": 35,
  "generated_at": "2026-05-31T17:22:27Z",
  "input_formula_rows": 9240,
  "max_ast_depth": 6,
  "next_allowed": "A7FF-CORE2 FeatureFactory subgraph registry",
  "operator_types": 10,
  "parse_failure_rows": 0,
  "parse_ok_rows": 9240,
  "roundtrip_failure_rows": 0,
  "roundtrip_ok_rows": 9240,
  "schema_version": "a7ff_core_ast_v0",
  "source_decision": "PASS_A7FFCORE0_TYPED_AST_GOVERNANCE_READY_FOR_CORE1",
  "source_stage": "A7FF-CORE0",
  "stage": "A7FF-CORE1",
  "uses_may": false
}
```

## Family Roundtrip Summary

| semantic_pair                        | motif               |   rows |   parse_ok |   roundtrip_ok |   median_nodes |   max_depth |   field_count |
|:-------------------------------------|:--------------------|-------:|-----------:|---------------:|---------------:|------------:|--------------:|
| open_interest_like\|price_like       | smooth_mul          |    450 |        450 |            450 |              9 |           5 |             2 |
| open_interest_like\|price_like       | mean_reversion_gate |    450 |        450 |            450 |             10 |           6 |             2 |
| open_interest_like\|price_like       | delta_x_divergence  |    450 |        450 |            450 |             15 |           6 |             2 |
| taker_flow_like\|basis_premium_like  | safe_div_abs        |    450 |        450 |            450 |              8 |           5 |             2 |
| taker_flow_like\|basis_premium_like  | smooth_mul          |    450 |        450 |            450 |              9 |           5 |             2 |
| taker_flow_like\|basis_premium_like  | gated_sign          |    450 |        450 |            450 |              8 |           5 |             2 |
| taker_flow_like\|basis_premium_like  | relative_shock      |    450 |        450 |            450 |             10 |           5 |             2 |
| open_interest_like\|price_like       | spread_rank         |    450 |        450 |            450 |              9 |           5 |             2 |
| liquidity_like\|volatility_like      | liquidity_shock     |    360 |        360 |            360 |             11 |           6 |             2 |
| liquidity_like\|volatility_like      | mean_reversion_gate |    360 |        360 |            360 |             10 |           6 |             2 |
| liquidity_like\|volatility_like      | safe_div_abs        |    360 |        360 |            360 |              8 |           5 |             2 |
| taker_flow_like\|open_interest_like  | relative_shock      |    360 |        360 |            360 |             10 |           5 |             2 |
| open_interest_like\|positioning_like | spread_rank         |    360 |        360 |            360 |              9 |           5 |             2 |
| open_interest_like\|positioning_like | safe_div_abs        |    360 |        360 |            360 |              8 |           5 |             2 |
| open_interest_like\|positioning_like | smooth_mul          |    360 |        360 |            360 |              9 |           5 |             2 |
| open_interest_like\|positioning_like | delta_x_divergence  |    360 |        360 |            360 |             15 |           6 |             2 |
| liquidity_like\|volatility_like      | spread_rank         |    360 |        360 |            360 |              9 |           5 |             2 |
| liquidity_like\|volatility_like      | smooth_mul          |    360 |        360 |            360 |              9 |           5 |             2 |
| open_interest_like\|positioning_like | signed_spread       |    360 |        360 |            360 |             14 |           6 |             2 |
| taker_flow_like\|open_interest_like  | smooth_mul          |    360 |        360 |            360 |              9 |           5 |             2 |
| taker_flow_like\|open_interest_like  | safe_div_abs        |    360 |        360 |            360 |              8 |           5 |             2 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |    360 |        360 |            360 |             10 |           5 |             2 |
| taker_flow_like\|open_interest_like  | gated_sign          |    360 |        360 |            360 |              8 |           5 |             2 |
| liquidity_like                       | single              |    108 |        108 |            108 |              3 |           3 |             1 |
| open_interest_like                   | single              |     60 |         60 |             60 |              3 |           3 |             1 |
| taker_flow_like                      | single              |     48 |         48 |             48 |              3 |           3 |             1 |
| volatility_like                      | single              |     24 |         24 |             24 |              3 |           3 |             1 |

## Operator Inventory

| node_value   |   operator_node_count |
|:-------------|----------------------:|
| Mean         |                 13436 |
| Delta        |                  8248 |
| ZScore       |                  7978 |
| Mul          |                  6300 |
| CSRank       |                  4680 |
| Sub          |                  2340 |
| Sign         |                  1980 |
| Abs          |                  1890 |
| SafeDiv      |                  1530 |
| Neg          |                   810 |

## Field Inventory

| node_value                           |   field_node_count |
|:-------------------------------------|-------------------:|
| taker_buy_quote_volume               |               3612 |
| open_interest_last                   |               3512 |
| trade_count                          |               1812 |
| open_interest_mean                   |               1112 |
| trade_close                          |                800 |
| trade_return_1h                      |                600 |
| open_interest_value_last             |                512 |
| trade_low                            |                500 |
| global_long_short_account_ratio_last |                500 |
| age_x_volatility                     |                500 |
| global_long_short_account_ratio_mean |                500 |
| trade_high                           |                500 |
| top_long_short_account_ratio_last    |                500 |
| mark_index_basis_bps                 |                400 |
| trade_return_24h                     |                400 |
| mark_high                            |                400 |
| index_close                          |                400 |
| mark_close                           |                400 |
| open_interest_value_mean             |                312 |
| realized_vol_168h                    |                312 |
| top_long_short_account_ratio_mean    |                300 |
| mark_low                             |                200 |
| age_x_liquidity                      |                 12 |
| log_quote_volume_168h                |                 12 |
| median_quote_volume_168h             |                 12 |
| open_interest_change_24h             |                 12 |
| liquidity_rank_active_universe       |                 12 |
| realized_vol_24h                     |                 12 |
| taker_buy_sell_volume_ratio_mean     |                 12 |
| taker_buy_volume                     |                 12 |
| taker_buy_sell_volume_ratio_last     |                 12 |
| trade_quote_volume                   |                 12 |
| trade_count_168h                     |                 12 |
| trade_volume                         |                 12 |
| volume_volatility_ratio_168h         |                 12 |

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
