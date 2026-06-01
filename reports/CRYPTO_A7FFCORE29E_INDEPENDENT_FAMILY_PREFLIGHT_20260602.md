# CRYPTO A7FF-CORE29E INDEPENDENT FAMILY PREFLIGHT

Generated: 2026-06-01T18:35:54Z

## Decision

`PASS_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_READY_FOR_CORE30_CONTRACT`

CORE29E builds a balanced blueprint preflight queue and validates field/schema availability. It does not execute numeric evaluation, replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- blueprint_count: `480`
- preflight_pass_count: `480`
- preflight_missing_count: `0`
- forbidden_pattern_hit_count: `0`

## Adapter Preflight

| adapter                          | dataset                       | required_fields_available   | status   |
|:---------------------------------|:------------------------------|:----------------------------|:---------|
| aggtrades_enhanced_field_adapter | core12_aggtrades_all_features | True                        | pass     |
| existing_top498_panel_fields     | top498_replay_v2              | True                        | pass     |
| balanced_queue_policy            | all                           | True                        | pass     |

## Family Balance

| family_id                         | dataset                       |   blueprint_count |   preflight_pass_count |   motif_count |   operator_count |
|:----------------------------------|:------------------------------|------------------:|-----------------------:|--------------:|-----------------:|
| F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |               160 |                    160 |             4 |                5 |
| F1b_taker_flow_market_panel       | top498_replay_v2              |               160 |                    160 |             4 |                5 |
| F2a_basis_funding_independent     | top498_replay_v2              |               160 |                    160 |             4 |                5 |

## Schema Availability

| dataset                       | field                              | available   |   schema_field_count |
|:------------------------------|:-----------------------------------|:------------|---------------------:|
| top498_replay_v2              | funding_rate                       | True        |                   54 |
| top498_replay_v2              | kline_taker_buy_quote_share        | True        |                   54 |
| top498_replay_v2              | mark_index_basis_bps               | True        |                   54 |
| top498_replay_v2              | premium_close                      | True        |                   54 |
| top498_replay_v2              | premium_close_bps                  | True        |                   54 |
| top498_replay_v2              | taker_buy_quote_volume             | True        |                   54 |
| top498_replay_v2              | trade_quote_volume                 | True        |                   54 |
| top498_replay_v2              | trade_volume                       | True        |                   54 |
| core12_aggtrades_all_features | agg_large_notional_ratio_100k_plus | True        |                  654 |
| core12_aggtrades_all_features | agg_max_trade_notional             | True        |                  654 |
| core12_aggtrades_all_features | agg_price_range_bps                | True        |                  654 |
| core12_aggtrades_all_features | agg_signed_aggressor_notional      | True        |                  654 |
| core12_aggtrades_all_features | agg_volume_imbalance               | True        |                  654 |
| core12_aggtrades_all_features | funding_rate                       | True        |                  654 |
| core12_aggtrades_all_features | mark_index_basis_bps               | True        |                  654 |
| core12_aggtrades_all_features | premium_index_bps                  | True        |                  654 |

## Forbidden Pattern Audit

| pattern                              |   hit_count |
|:-------------------------------------|------------:|
| open_interest_value_last,index_close |           0 |
| RawOKXBinance                        |           0 |
| SameBar                              |           0 |
| future_return                        |           0 |
| liquidation_                         |           0 |
| depth_imbalance                      |           0 |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core30_contract": true,
  "authorizes_large_search": false,
  "authorizes_numeric_probe": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blueprint_count": 480,
  "decision": "PASS_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_READY_FOR_CORE30_CONTRACT",
  "executes_generation": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "forbidden_pattern_hit_count": 0,
  "generated_at": "2026-06-01T18:35:54Z",
  "next_allowed": "A7FF-CORE30 independent family numeric probe contract",
  "preflight_missing_count": 0,
  "preflight_pass_count": 480,
  "source_decision": "PASS_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_READY_FOR_CORE29E",
  "source_stage": "A7FF-CORE29",
  "stage": "A7FF-CORE29E"
}
```
