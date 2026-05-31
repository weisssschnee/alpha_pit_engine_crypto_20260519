# CRYPTO A7FF-55R2 ATLAS FIELD-FAMILY GENERATION REPAIR

Generated: 2026-05-31T11:51:09Z

## Decision

`PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC`

A7FF-55R2 repairs the generation atlas contract after A7FF-55R1 showed missing open-interest and taker-flow families. It does not execute dry generation, numeric evaluation, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC",
  "executes_generation": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "field_repairs": 18,
  "generated_at": "2026-05-31T11:51:09Z",
  "next_allowed": "A7FF-55R3 repaired atlas dry generation using repaired seed/pair preview",
  "repaired_liquidity_seed_count": 9,
  "repaired_open_interest_seed_count": 5,
  "repaired_taker_flow_seed_count": 4,
  "required_pair_patch_rows": 5,
  "source_decision": "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL",
  "source_stage": "A7FF-55R1",
  "stage": "A7FF-55R2",
  "uses_may": false
}
```

## Semantic / Route Repair Map

| field_name                       | old_semantic_type_v3   | new_semantic_type_v3   | old_seed_route     | new_seed_route          | semantic_repair_reason                         | route_repair_reason                                        |
|:---------------------------------|:-----------------------|:-----------------------|:-------------------|:------------------------|:-----------------------------------------------|:-----------------------------------------------------------|
| open_interest_last               | positioning_like       | open_interest_like     | modifier_only_seed | exploratory_signal_seed | split_open_interest_from_positioning           | promote_from_modifier_to_exploratory_signal_seed           |
| open_interest_mean               | positioning_like       | open_interest_like     | modifier_only_seed | exploratory_signal_seed | split_open_interest_from_positioning           | promote_from_modifier_to_exploratory_signal_seed           |
| open_interest_value_last         | positioning_like       | open_interest_like     | modifier_only_seed | exploratory_signal_seed | split_open_interest_from_positioning           | promote_from_modifier_to_exploratory_signal_seed           |
| open_interest_value_mean         | positioning_like       | open_interest_like     | modifier_only_seed | exploratory_signal_seed | split_open_interest_from_positioning           | promote_from_modifier_to_exploratory_signal_seed           |
| taker_buy_quote_volume           | liquidity_like         | taker_flow_like        | modifier_only_seed | exploratory_signal_seed | split_taker_flow_from_positioning_or_liquidity | promote_from_modifier_to_exploratory_signal_seed           |
| taker_buy_sell_volume_ratio_last | positioning_like       | taker_flow_like        | modifier_only_seed | exploratory_signal_seed | split_taker_flow_from_positioning_or_liquidity | promote_from_modifier_to_exploratory_signal_seed           |
| taker_buy_sell_volume_ratio_mean | positioning_like       | taker_flow_like        | modifier_only_seed | exploratory_signal_seed | split_taker_flow_from_positioning_or_liquidity | promote_from_modifier_to_exploratory_signal_seed           |
| trade_count                      | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| trade_quote_volume               | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| trade_volume                     | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| age_x_liquidity                  | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| liquidity_rank_active_universe   | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| log_quote_volume_168h            | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| median_quote_volume_168h         | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| open_interest_change_24h         | positioning_like       | open_interest_like     | modifier_only_seed | exploratory_signal_seed | split_open_interest_from_positioning           | promote_from_modifier_to_exploratory_signal_seed           |
| taker_buy_volume                 | liquidity_like         | taker_flow_like        | modifier_only_seed | exploratory_signal_seed | split_taker_flow_from_positioning_or_liquidity | promote_from_modifier_to_exploratory_signal_seed           |
| trade_count_168h                 | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |
| volume_volatility_ratio_168h     | liquidity_like         | liquidity_like         | modifier_only_seed | exploratory_signal_seed | keep_liquidity_activity                        | promote_liquidity_from_modifier_to_exploratory_signal_seed |

## Old Seed Summary

| semantic_type_v3   | a7ff23r_seed_route      |   field_count |
|:-------------------|:------------------------|--------------:|
| basis_premium_like | exploratory_signal_seed |             1 |
| basis_premium_like | modifier_only_seed      |            18 |
| basis_premium_like | primary_signal_seed     |             1 |
| funding_like       | modifier_only_seed      |             6 |
| generic_numeric    | modifier_only_seed      |             9 |
| liquidity_like     | modifier_only_seed      |            11 |
| positioning_like   | modifier_only_seed      |            15 |
| price_like         | exploratory_signal_seed |             1 |
| price_like         | modifier_only_seed      |             2 |
| state_or_taxonomy  | modifier_only_seed      |             8 |
| volatility_like    | exploratory_signal_seed |             2 |
| volatility_like    | modifier_only_seed      |             4 |

## Repaired Seed Summary

| semantic_type_v3   | a7ff23r_seed_route      |   field_count |
|:-------------------|:------------------------|--------------:|
| basis_premium_like | exploratory_signal_seed |             1 |
| basis_premium_like | modifier_only_seed      |            18 |
| basis_premium_like | primary_signal_seed     |             1 |
| funding_like       | modifier_only_seed      |             6 |
| generic_numeric    | modifier_only_seed      |             9 |
| liquidity_like     | exploratory_signal_seed |             9 |
| open_interest_like | exploratory_signal_seed |             5 |
| positioning_like   | modifier_only_seed      |             8 |
| price_like         | exploratory_signal_seed |             1 |
| price_like         | modifier_only_seed      |             2 |
| state_or_taxonomy  | modifier_only_seed      |             8 |
| taker_flow_like    | exploratory_signal_seed |             4 |
| volatility_like    | exploratory_signal_seed |             2 |
| volatility_like    | modifier_only_seed      |             4 |

## Required Pair Policy Patch

| semantic_pair                        | left_semantic_type_v3   | right_semantic_type_v3   | a7ff55r2_pair_route   | motif_priority                                | reason                                                                   |
|:-------------------------------------|:------------------------|:-------------------------|:----------------------|:----------------------------------------------|:-------------------------------------------------------------------------|
| open_interest_like\|positioning_like | open_interest_like      | positioning_like         | generation_priority   | delta_x_divergence\|signed_spread\|smooth_mul | recover OI-positioning interaction absent from current atlas             |
| taker_flow_like\|open_interest_like  | taker_flow_like         | open_interest_like       | generation_priority   | flow_x_leverage\|relative_shock\|gated_sign   | recover taker-flow leverage state absent from current atlas              |
| liquidity_like\|volatility_like      | liquidity_like          | volatility_like          | generation_priority   | liquidity_shock\|vol_compression\|smooth_mul  | make existing liquidity formulas materialization-eligible                |
| open_interest_like\|price_like       | open_interest_like      | price_like               | probe_priority        | oi_delta_x_price_move\|mean_reversion_gate    | diagnostic OI-price interaction without direct OI-price standalone rerun |
| taker_flow_like\|basis_premium_like  | taker_flow_like         | basis_premium_like       | probe_priority        | flow_x_basis_dislocation\|relative_shock      | test aggressive-flow response under basis/premium dislocation            |

## Existing Pair Source Summary

| semantic_pair                          | a7ff23r_pair_route              |   pair_rows |
|:---------------------------------------|:--------------------------------|------------:|
| basis_premium_like\|positioning_like   | exploratory_generation_priority |         281 |
| basis_premium_like\|funding_like       | exploratory_generation_priority |         118 |
| basis_premium_like\|volatility_like    | exploratory_generation_priority |         110 |
| funding_like\|positioning_like         | exploratory_generation_priority |          90 |
| basis_premium_like\|price_like         | exploratory_generation_priority |          54 |
| liquidity_like\|volatility_like        | exploratory_generation_priority |          52 |
| basis_premium_like\|positioning_like   | generation_priority             |          19 |
| basis_premium_like\|liquidity_like     | generation_priority             |          15 |
| liquidity_like\|volatility_like        | generation_priority             |          14 |
| basis_premium_like\|basis_premium_like | generation_priority             |          14 |
| positioning_like\|volatility_like      | generation_priority             |          12 |
| basis_premium_like\|volatility_like    | generation_priority             |          10 |
| volatility_like\|volatility_like       | generation_priority             |           7 |
| price_like\|volatility_like            | generation_priority             |           6 |
| basis_premium_like\|generic_numeric    | generation_priority             |           6 |
| basis_premium_like\|price_like         | generation_priority             |           6 |
| generic_numeric\|volatility_like       | generation_priority             |           6 |
| basis_premium_like\|state_or_taxonomy  | generation_priority             |           6 |
| state_or_taxonomy\|volatility_like     | generation_priority             |           4 |
| basis_premium_like\|funding_like       | generation_priority             |           2 |
| funding_like\|volatility_like          | generation_priority             |           2 |
| liquidity_like\|price_like             | generation_priority             |           2 |
| price_like\|price_like                 | generation_priority             |           1 |

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
