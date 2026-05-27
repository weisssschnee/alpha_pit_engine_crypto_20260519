# CRYPTO A7AF-0 Core39 Selected-Field Replay Contract

Generated: 2026-05-22T15:03:15Z

## Decision

```text
PASS_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_READY
```

This stage reads the core39 selected-field data and prepares a small controlled replay smoke. It does not run replay and does not run search.

## Authorization

```json
{
  "authorizes_a7af1_small_controlled_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_READY",
  "may_policy": "May 2026 stress-only; not ranking, generation, threshold, weight selection, or authorization",
  "warnings": [
    "some_first_smoke_fields_have_low_min_symbol_coverage",
    "ret_1_forward_proxy_replay_not_execution_grade_open_to_open",
    "may_2026_is_stress_only_not_ranking_or_selection"
  ]
}
```

## Manifest

```json
{
  "columns_read": 25,
  "decision": "PASS_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_READY",
  "duplicate_keys": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T15:03:15Z",
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7af0_core39_selected_field_replay_contract",
  "panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_core39_all_features_metrics_v3_market_structure_v1.parquet",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_20260522.md",
  "rows": 815818,
  "symbols": 39,
  "timestamp_max": "2026-05-22 00:00:00+00:00",
  "timestamp_min": "2024-01-01 00:00:00+00:00"
}
```

## Split Manifest

| split                 | start                     | end                       | usage                      |   rows |   symbols |   expected_rows_if_full |   row_coverage | may_allowed_for_ranking   | feature_time_rule                       | execution_rule                                     |
|:----------------------|:--------------------------|:--------------------------|:---------------------------|-------:|----------:|------------------------:|---------------:|:--------------------------|:----------------------------------------|:---------------------------------------------------|
| train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 | selection_training_only    | 342163 |        39 |                  342576 |       0.998794 | True                      | 1h features available at timestamp + 1h | execution_time >= next 1h bar; lag stress required |
| validation_2025H1     | 2025-01-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 | ranking_allowed_non_may    | 169416 |        39 |                  169416 |       1        | True                      | 1h features available at timestamp + 1h | execution_time >= next 1h bar; lag stress required |
| recent_2025H2_2026Apr | 2025-07-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | ranking_allowed_non_may    | 284544 |        39 |                  284544 |       1        | True                      | 1h features available at timestamp + 1h | execution_time >= next 1h bar; lag stress required |
| may_2026_stress       | 2026-05-01T00:00:00+00:00 | 2026-05-21T23:00:00+00:00 | post_selection_stress_only |  19656 |        39 |                   19656 |       1        | False                     | 1h features available at timestamp + 1h | execution_time >= next 1h bar; lag stress required |

## First Smoke Field List

| field_name                                  | present   |   non_null_rate |   min_symbol_rate |   median_symbol_rate |   max_symbol_rate |
|:--------------------------------------------|:----------|----------------:|------------------:|---------------------:|------------------:|
| open_interest_change_24h                    | True      |        0.998522 |       0.997419    |             0.998518 |          0.998709 |
| open_interest_zscore_168h                   | True      |        0.9989   |       0.998899    |             0.998901 |          0.998901 |
| open_interest_value_zscore_168h             | True      |        0.9989   |       0.998899    |             0.998901 |          0.998901 |
| global_long_short_account_ratio_zscore_168h | True      |        0.9989   |       0.998899    |             0.998901 |          0.998901 |
| top_long_short_account_ratio_zscore_168h    | True      |        0.998805 |       0.998804    |             0.998805 |          0.998805 |
| top_long_short_position_ratio_zscore_168h   | True      |        0.9989   |       0.998899    |             0.998901 |          0.998901 |
| taker_buy_sell_volume_ratio_zscore_168h     | True      |        0.9989   |       0.998899    |             0.998901 |          0.998901 |
| mark_index_basis_change_24h                 | True      |        0.953057 |       0           |             0.998805 |          0.998805 |
| mark_index_basis_zscore_168h                | True      |        0.952265 |       0           |             0.997992 |          0.997992 |
| premium_index_change_24h                    | True      |        0.958619 |       0.21349     |             0.998805 |          0.998805 |
| premium_index_bps                           | True      |        0.959767 |       0.214637    |             0.999952 |          0.999952 |
| funding_rate_bps                            | True      |        0.74043  |       0.00109948  |             0.999952 |          0.999952 |
| funding_rate_change_3obs                    | True      |        0.740286 |       0.000956069 |             0.999809 |          0.999809 |

## Selected Field Contract With Availability

| source_family    | field_name                         | field_type                          | scope      | status             | usage_note                                                          |   present |   non_null_rate |   min_symbol_rate |   median_symbol_rate |
|:-----------------|:-----------------------------------|:------------------------------------|:-----------|:-------------------|:--------------------------------------------------------------------|----------:|----------------:|------------------:|---------------------:|
| metrics_source   | open_interest                      | independent                         | core39     | allowed            | source field; use level/change/zscore variants only after selection |         1 |        1        |       1           |             1        |
| metrics_source   | open_interest_value                | independent                         | core39     | allowed            | source field; stale-level controls required                         |         1 |        1        |       1           |             1        |
| metrics_source   | global_long_short_account_ratio    | independent                         | core39     | allowed            | crowding/account state source                                       |         1 |        1        |       1           |             1        |
| metrics_source   | top_long_short_account_ratio       | independent                         | core39     | allowed            | crowding/account state source                                       |         1 |        0.999904 |       0.999904    |             0.999904 |
| metrics_source   | top_long_short_position_ratio      | independent                         | core39     | allowed            | position crowding source                                            |         1 |        1        |       1           |             1        |
| metrics_source   | taker_buy_sell_volume_ratio        | independent                         | core39     | allowed            | vendor 5m metrics source, not aggTrades                             |         1 |        1        |       1           |             1        |
| market_structure | mark_index_basis_bps               | independent_derived_from_mark_index | core39     | allowed            | basis level from mark/index source                                  |         1 |        0.954175 |       0           |             0.999952 |
| market_structure | mark_index_basis_change_24h        | derived                             | core39     | allowed            | basis dynamic; preferred over static basis for stale-control risk   |         1 |        0.953057 |       0           |             0.998805 |
| market_structure | mark_index_basis_zscore_168h       | derived                             | core39     | allowed            | basis state                                                         |         1 |        0.952265 |       0           |             0.997992 |
| market_structure | premium_index_bps                  | independent_derived_from_premium    | core39     | allowed            | premium source state                                                |         1 |        0.959767 |       0.214637    |             0.999952 |
| market_structure | premium_index_change_24h           | derived                             | core39     | allowed            | premium dynamic                                                     |         1 |        0.958619 |       0.21349     |             0.998805 |
| market_structure | premium_minus_funding_bps          | derived                             | core39     | caution            | missing can be high; funding asof semantics required                |         1 |        0.700244 |       0.00109948  |             0.999952 |
| market_structure | funding_rate_bps                   | independent_asof                    | core39     | benchmark_only     | mandatory baseline/control; not promotable standalone               |         1 |        0.74043  |       0.00109948  |             0.999952 |
| market_structure | funding_rate_change_3obs           | derived_asof                        | core39     | benchmark_only     | funding family benchmark/control                                    |         1 |        0.740286 |       0.000956069 |             0.999809 |
| aggtrades_core3  | agg_signed_flow_z_24h              | independent_aggtrades               | core3_only | allowed_core3_only | order-flow state; not core39-wide                                   |       nan |      nan        |     nan           |           nan        |
| aggtrades_core3  | agg_flow_imbalance_notional_24h    | independent_aggtrades               | core3_only | allowed_core3_only | signed aggressor flow                                               |       nan |      nan        |     nan           |           nan        |
| aggtrades_core3  | agg_large_notional_share_24h       | independent_aggtrades               | core3_only | allowed_core3_only | large trade intensity                                               |       nan |      nan        |     nan           |           nan        |
| aggtrades_core3  | agg_cross_symbol_signed_flow_share | derived_cross_symbol_core3          | core3_only | allowed_core3_only | core3 relative flow only                                            |       nan |      nan        |     nan           |           nan        |
| aggtrades_core3  | agg_notional_accel_4h_vs_24h       | derived_aggtrades                   | core3_only | allowed_core3_only | flow acceleration                                                   |       nan |      nan        |     nan           |           nan        |

## Boundary

- A7AF-1 may run only a small controlled replay smoke.
- `ret_1` forward proxy is acceptable for method smoke but not execution-grade proof.
- May 2026 is stress-only and cannot affect ranking or selection.
- Funding fields remain benchmark/control only.
- No formula search, large search, alpha proof, shadow, paper, or live is authorized.
