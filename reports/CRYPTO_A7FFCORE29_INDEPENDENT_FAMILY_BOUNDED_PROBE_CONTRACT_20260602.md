# CRYPTO A7FF-CORE29 INDEPENDENT FAMILY BOUNDED PROBE CONTRACT

Generated: 2026-06-01T18:32:18Z

## Decision

`PASS_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_READY_FOR_CORE29E`

CORE29 is a contract. It defines a bounded independent-family generation/preflight envelope but does not execute generation, numeric replay, search, large search, alpha proof, shadow, paper, or live.

## Family Contract

| family_id                         | scope                | role                                  | allowed_motifs                                                                                                   | blocked_motifs                                                                    | required_adapter                 |   max_blueprints |   preflight_rows |   numeric_probe_rows |
|:----------------------------------|:---------------------|:--------------------------------------|:-----------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|:---------------------------------|-----------------:|-----------------:|---------------------:|
| F1a_aggtrades_flow_microstructure | core12_bounded       | independent_flow_state_interaction    | signed_flow_reversal; large_trade_shock; flow_x_basis_or_funding_state; flow_x_low_turnover                      | A7V activity/liquidity self-reproduction; standalone volume/trade_count rank      | aggtrades_enhanced_field_adapter |              800 |              160 |                   80 |
| F1b_taker_flow_market_panel       | top498_listing_aware | top498_flow_interaction               | taker_share_x_basis; taker_share_x_volatility_compression; taker_share_x_liquidity_tier; low_turnover_flow_state | standalone taker-share rank; standalone activity/liquidity rank                   | existing_top498_panel_fields     |              800 |              160 |                   80 |
| F2a_basis_funding_independent     | top498_listing_aware | basis_funding_dislocation_interaction | basis_delta_x_funding_abs; basis_dislocation_x_flow; funding_persistence_x_low_turnover; H8_H24_dislocation      | basis-only wrapper; funding-only wrapper; direct S0 positioning-price-basis rerun | existing_top498_panel_fields     |              800 |              160 |                   80 |

## Budget Plan

| budget_item                    |   value | notes                                      |
|:-------------------------------|--------:|:-------------------------------------------|
| max_total_blueprints           | 2400    | contract cap; no generation executed here  |
| materialization_preflight_rows |  480    | balanced 160 rows per family               |
| numeric_probe_rows             |  240    | only after adapter/preflight pass          |
| min_family_count               |    3    | all CORE28E candidate families represented |
| max_single_family_share        |    0.34 | preflight and numeric queue cap            |
| max_single_motif_share         |    0.2  | prevent motif collapse                     |

## Allowed Field Tokens

| field_token                 | family_id                         | role              |
|:----------------------------|:----------------------------------|:------------------|
| signed_aggressor_notional   | F1a_aggtrades_flow_microstructure | flow              |
| signed_aggressor_quantity   | F1a_aggtrades_flow_microstructure | flow              |
| volume_imbalance            | F1a_aggtrades_flow_microstructure | flow_state        |
| max_trade_notional          | F1a_aggtrades_flow_microstructure | large_trade_state |
| kline_taker_buy_quote_share | F1b_taker_flow_market_panel       | taker_flow        |
| kline_quote_volume          | F1b_taker_flow_market_panel       | liquidity_state   |
| realized_vol_168h           | F1b_taker_flow_market_panel       | volatility_state  |
| mark_index_basis_bps        | F2a_basis_funding_independent     | basis             |
| premium_close_bps           | F2a_basis_funding_independent     | premium           |
| funding_rate                | F2a_basis_funding_independent     | funding           |
| funding_rate_abs_168h       | F2a_basis_funding_independent     | funding_state     |

## Forbidden Patterns

| pattern                                         | reason                                                         |
|:------------------------------------------------|:---------------------------------------------------------------|
| direct_OI_price_rerun                           | S0 was single-lane only and superseded as diagnostic reference |
| basis_only_wrapper                              | basis-only promotion collapsed to narrow surface               |
| funding_only_wrapper                            | funding-only wrapper is not independent family evidence        |
| activity_liquidity_self_reproduction            | A7V activity/liquidity family remains blocked                  |
| raw_OKX_Binance_direct_price_comparison         | requires canonical contract-unit fields                        |
| forward_only_cross_exchange_as_historical_proof | cross-exchange overlay is diagnostic/recent only               |
| liquidation_orderbook_without_PIT_contract      | new data source contract required                              |

## Adapter Requirements

| adapter                          | required_for                      | must_check                                                                               | blocking_if_missing   |
|:---------------------------------|:----------------------------------|:-----------------------------------------------------------------------------------------|:----------------------|
| aggtrades_enhanced_field_adapter | F1a_aggtrades_flow_microstructure | field existence; timestamp after-hour availability; core12 coverage; NaN/inf; role trace | True                  |
| existing_top498_panel_fields     | F1b/F2a                           | field contract; materialization parity; label alignment; no S0-only queue dominance      | True                  |
| control_attachment               | all                               | row shuffle; time shuffle; wrong lag; stale; same-family placebo                         | True                  |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE29E independent family dry-generation/materialization adapter preflight": true,
    "A7FF-CORE29E numeric probe": false
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_generation_execution_beyond_contract": true,
    "large_search": true,
    "search": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core29e_preflight": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_numeric_probe": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_READY_FOR_CORE29E",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "generated_at": "2026-06-01T18:32:18Z",
  "materialization_preflight_rows": 480,
  "max_total_blueprints": 2400,
  "next_allowed": "A7FF-CORE29E independent family dry-generation/materialization adapter preflight",
  "numeric_probe_rows_after_preflight": 240,
  "source_decision": "PASS_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_READY_FOR_CORE29_CONTRACT",
  "source_stage": "A7FF-CORE28E",
  "stage": "A7FF-CORE29"
}
```
