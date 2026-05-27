# CRYPTO A7AE-1 Field Selection Contract

Generated: 2026-05-22T14:58:59Z

## Decision

```text
PASS_A7AE1_FIELD_SELECTION_CONTRACT_READY
```

This stage defines which newly received fields can enter controlled experiments. It does not run replay or search.

## Authorization

```json
{
  "authorizes_a7af0_core39_selected_field_contract": true,
  "authorizes_a7af1_replay": false,
  "authorizes_alpha_proof": false,
  "authorizes_core3_aggtrades_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AE1_FIELD_SELECTION_CONTRACT_READY"
}
```

## Selected Field Contract

| source_family    | field_name                         | field_type                          | scope      | status             | usage_note                                                          |
|:-----------------|:-----------------------------------|:------------------------------------|:-----------|:-------------------|:--------------------------------------------------------------------|
| metrics_source   | open_interest                      | independent                         | core39     | allowed            | source field; use level/change/zscore variants only after selection |
| metrics_source   | open_interest_value                | independent                         | core39     | allowed            | source field; stale-level controls required                         |
| metrics_source   | global_long_short_account_ratio    | independent                         | core39     | allowed            | crowding/account state source                                       |
| metrics_source   | top_long_short_account_ratio       | independent                         | core39     | allowed            | crowding/account state source                                       |
| metrics_source   | top_long_short_position_ratio      | independent                         | core39     | allowed            | position crowding source                                            |
| metrics_source   | taker_buy_sell_volume_ratio        | independent                         | core39     | allowed            | vendor 5m metrics source, not aggTrades                             |
| market_structure | mark_index_basis_bps               | independent_derived_from_mark_index | core39     | allowed            | basis level from mark/index source                                  |
| market_structure | mark_index_basis_change_24h        | derived                             | core39     | allowed            | basis dynamic; preferred over static basis for stale-control risk   |
| market_structure | mark_index_basis_zscore_168h       | derived                             | core39     | allowed            | basis state                                                         |
| market_structure | premium_index_bps                  | independent_derived_from_premium    | core39     | allowed            | premium source state                                                |
| market_structure | premium_index_change_24h           | derived                             | core39     | allowed            | premium dynamic                                                     |
| market_structure | premium_minus_funding_bps          | derived                             | core39     | caution            | missing can be high; funding asof semantics required                |
| market_structure | funding_rate_bps                   | independent_asof                    | core39     | benchmark_only     | mandatory baseline/control; not promotable standalone               |
| market_structure | funding_rate_change_3obs           | derived_asof                        | core39     | benchmark_only     | funding family benchmark/control                                    |
| aggtrades_core3  | agg_signed_flow_z_24h              | independent_aggtrades               | core3_only | allowed_core3_only | order-flow state; not core39-wide                                   |
| aggtrades_core3  | agg_flow_imbalance_notional_24h    | independent_aggtrades               | core3_only | allowed_core3_only | signed aggressor flow                                               |
| aggtrades_core3  | agg_large_notional_share_24h       | independent_aggtrades               | core3_only | allowed_core3_only | large trade intensity                                               |
| aggtrades_core3  | agg_cross_symbol_signed_flow_share | derived_cross_symbol_core3          | core3_only | allowed_core3_only | core3 relative flow only                                            |
| aggtrades_core3  | agg_notional_accel_4h_vs_24h       | derived_aggtrades                   | core3_only | allowed_core3_only | flow acceleration                                                   |

## Blocked Pattern Registry

| pattern                        | status          | reason                                                                    |
|:-------------------------------|:----------------|:--------------------------------------------------------------------------|
| static_oi_level_x_realized_vol | blocked_initial | A7AD wrong-lag controls dominated static OI x volatility/trend motifs     |
| raw_603_column_blind_search    | blocked         | core39 all-features table is derived-wide; field selection required first |
| core3_agg_projected_to_core39  | blocked         | aggTrades coverage is BTC/ETH/SOL only                                    |
| funding_standalone_promotion   | blocked         | funding family remains benchmark/control after A7D/A7B history            |
| liquidity_volatility_uncapped  | blocked         | previous A7M/A7O collapse risk                                            |

## Next Experiment Contract

| stage   | name                                         | scope                                                     |
|:--------|:---------------------------------------------|:----------------------------------------------------------|
| A7AF0   | core39 selected-field replay contract        | no replay; build selected field panel/schema and controls |
| A7AF1   | core39 selected-field small controlled smoke | <=120 candidates; controls mandatory; no May ranking      |
| A7AG0   | core3 aggtrades integration contract         | core3-only order-flow diagnostics, separate from core39   |

## Boundary

- Do not feed all 603 core39 columns into generator/search.
- Keep core39 selected-field smoke separate from core3 aggTrades diagnostics.
- Keep funding as benchmark/control only.
- Static OI level x realized volatility/trend motifs require redesign before any replay because wrong-lag controls dominated A7AD.
- No large search, alpha proof, shadow, paper, or live is authorized.
