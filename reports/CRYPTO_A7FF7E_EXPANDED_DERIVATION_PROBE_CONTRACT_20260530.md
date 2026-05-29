# CRYPTO A7FF-7E EXPANDED DERIVATION PROBE CONTRACT

Generated: 2026-05-29T16:24:01Z

## Decision

`PASS_A7FF7E_EXPANDED_DERIVATION_READY_FOR_A7FF8_NUMERIC_PROBE`

A7FF-7E deliberately expands derivation scale relative to A7FF-6. It creates a larger typed blueprint pool from one promoted signal seed plus regime/risk interaction inputs, but it still does not execute replay or search.

## Manifest

```json
{
  "authorizes_a7ff8_numeric_probe_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "blueprint_count": 9271,
  "decision": "PASS_A7FF7E_EXPANDED_DERIVATION_READY_FOR_A7FF8_NUMERIC_PROBE",
  "executes_generation": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:24:01Z",
  "motif_count": 8,
  "previous_a7ff6_decision": "HOLD_A7FF6_PORTFOLIO_MARGINAL_DRYRUN_NOT_PROMOTABLE",
  "selected_for_numeric_probe": 384,
  "selected_motif_count": 7,
  "selected_semantic_pair_count": 5,
  "semantic_pair_count": 5,
  "stage": "A7FF-7E",
  "uses_may": false
}
```

## Numeric Probe Plan

```json
{
  "control_probe_cap": 256,
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "sign_flip",
    "same_family_placebo"
  ],
  "deep_audit_cap": 64,
  "fast_numeric_probe_cap": 256,
  "horizons": [
    "1h",
    "4h",
    "8h",
    "24h"
  ],
  "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
    "L7_ranked_future_return_diagnostic_only"
  ],
  "materialize_cap": 384,
  "portfolio_marginal_probe_cap": 128,
  "promotion_blockers": [
    "L7-only cannot promote",
    "control_ratio >= 1.0 blocks",
    "single semantic_pair > 35pct blocks",
    "single skeleton > 15pct blocks",
    "numeric replay required before any search authorization"
  ],
  "required_outputs": [
    "a7ff8_materialization_metrics.csv",
    "a7ff8_label_response_metrics.csv",
    "a7ff8_control_dominance_metrics.csv",
    "a7ff8_nonoverlap_stats.csv",
    "a7ff8_portfolio_marginal_proxy.csv",
    "a7ff8_decision_record.json"
  ],
  "selected_blueprints": 384,
  "stage": "A7FF-8",
  "status": "contract_only_not_executed"
}
```

## Semantic Pair Summary

| semantic_pair                          | selected_for_a7ff8_numeric_probe   |   count |
|:---------------------------------------|:-----------------------------------|--------:|
| basis_premium_like                     | True                               |      15 |
| basis_premium_like\|basis_premium_like | False                              |    1300 |
| basis_premium_like\|basis_premium_like | True                               |      96 |
| basis_premium_like\|positioning_like   | False                              |    5408 |
| basis_premium_like\|positioning_like   | True                               |      96 |
| basis_premium_like\|price_like         | False                              |     879 |
| basis_premium_like\|price_like         | True                               |      81 |
| basis_premium_like\|volatility_like    | False                              |    1300 |
| basis_premium_like\|volatility_like    | True                               |      96 |

## Motif Summary

| motif              | selected_for_a7ff8_numeric_probe   |   count |
|:-------------------|:-----------------------------------|--------:|
| gated_sign         | False                              |    1264 |
| gated_sign         | True                               |      96 |
| mul                | False                              |    1172 |
| mul                | True                               |      96 |
| relative_shock     | False                              |    1264 |
| relative_shock     | True                               |      96 |
| safe_div_abs       | False                              |    1189 |
| safe_div_abs       | True                               |      11 |
| single             | True                               |      15 |
| smooth_interaction | False                              |    1298 |
| smooth_interaction | True                               |      62 |
| spread_rank        | False                              |    1352 |
| spread_rank        | True                               |       8 |
| sub                | False                              |    1348 |

## Selected Queue Sample

| blueprint_id            | layer                         | primary_field        | secondary_field                  | primary_transform   | secondary_transform   | motif      | semantic_pair                        | numeric_probe_priority   |
|:------------------------|:------------------------------|:---------------------|:---------------------------------|:--------------------|:----------------------|:-----------|:-------------------------------------|:-------------------------|
| a7ff7e_15ba28d7f1306b75 | F1_single_field_expanded      | mark_index_basis_bps |                                  | level               |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_2352f4afc86f9d62 | F1_single_field_expanded      | mark_index_basis_bps |                                  | zscore              |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_39970113ca76e295 | F1_single_field_expanded      | mark_index_basis_bps |                                  | delta_48h           |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_3ea8e79c7504f184 | F1_single_field_expanded      | mark_index_basis_bps |                                  | delta_4h            |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_436b541b33d083e6 | F1_single_field_expanded      | mark_index_basis_bps |                                  | csrank              |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_454b18e00e63d958 | F1_single_field_expanded      | mark_index_basis_bps |                                  | delta_12h           |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_5aa0e7a95e8f0f7f | F1_single_field_expanded      | mark_index_basis_bps |                                  | abs_zscore          |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_5aac42554cb19c48 | F1_single_field_expanded      | mark_index_basis_bps |                                  | delta_1h            |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_7e69ae852cf37229 | F1_single_field_expanded      | mark_index_basis_bps |                                  | winsor_zscore       |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_81f0e048570af6db | F1_single_field_expanded      | mark_index_basis_bps |                                  | decay_24h           |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_9c045a6f4fea31f7 | F1_single_field_expanded      | mark_index_basis_bps |                                  | decay_8h            |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_b43e221a6757fcbf | F1_single_field_expanded      | mark_index_basis_bps |                                  | delta_24h           |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_cdcf38bf2a58150c | F1_single_field_expanded      | mark_index_basis_bps |                                  | mean_4h             |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_e069ae2e1b7a109e | F1_single_field_expanded      | mark_index_basis_bps |                                  | mean_24h            |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_ea609aca7c31bd4e | F1_single_field_expanded      | mark_index_basis_bps |                                  | tsrank_24h          |                       | single     | basis_premium_like                   | P0                       |
| a7ff7e_0036a70175a3fc4d | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_00458b1756211ded | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_00db9c91e482de18 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_01a7c4db6a4c443a | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_0332925187994168 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_045c851a9508a546 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_09c74d60d25a4769 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_0a8af557650d4cf9 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | delta_1h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_0b479d31899791c3 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | level               | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_0d596b3d6cda062c | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_12h           | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_10292002161817c4 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1194937a763a8bd8 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | level               | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_18eac1b7714c5136 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | delta_1h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1a823396309e4dc7 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | delta_1h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1aa41a656165a9b9 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1c9b88500c7ca5ac | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1cefe876c0638992 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_1e16a045860c4689 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_2627a7a428d54d20 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_2d8f984e9a6828e2 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_2db929c4bbed3411 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | delta_24h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_303a085bd066346e | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_12h           | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_306abaa36ac72ce8 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_30b0a36e2f0d07c0 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_31b6ebedd8760de6 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_38536def0f5a502c | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3a21367110d300a2 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3ab1223528d2dfb0 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3de5984ae7a1281a | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3ecb7243abe7337b | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3f1137a35727a591 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_3f8c2bfce38c52be | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_414d6ca2994c9a60 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | level               | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_47cf35f52c0cecac | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_4cfa227198c17bb0 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_509f2b110954ea8b | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_12h           | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_51d560b3dd217cdf | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_523ba2cd18730994 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_5603f55a7b2e7d3c | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_5d6b53b77aa2e661 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_5fe1c377d4b70e22 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_6098c7774e8bdabe | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_612689182e898b28 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_681d8804ebd97cae | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_6927d0287435c6ac | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_6aea73fdf9264ab5 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | level               | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_6b29fc75102a0926 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | delta_1h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_6fc881861fc883c3 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | delta_24h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_733c54ee5a9e9007 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_77d52278c03cf651 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_78ae2edf402583da | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | delta_24h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_7c1842bb5bc9bb41 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_7cfb691def6acf14 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_48h           | csrank                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_8218988802fa8221 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | level               | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_829e15d78bf2c128 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_842ed84868772bb6 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | csrank              | delta_48h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_88f9e39368ead09b | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_24h           | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_8d78718453b030a5 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_4h            | zscore                | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_8d977922226182a4 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | delta_12h             | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_8f31949142a32fa4 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | delta_1h            | winsor_zscore         | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_8fc88cfd69d2032c | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | delta_4h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_988f0c0b85903a05 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_9df866ff735b5309 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | abs_zscore          | delta_1h              | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_a0f294e17621bb67 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | zscore              | sign_delta_24h        | gated_sign | basis_premium_like\|positioning_like | P0                       |
| a7ff7e_a7d03c292ec1b405 | F2_expanded_typed_interaction | mark_index_basis_bps | taker_buy_sell_volume_ratio_last | winsor_zscore       | level                 | gated_sign | basis_premium_like\|positioning_like | P0                       |

## Boundary

```text
This is a larger derivation and test contract, not alpha search.
A7FF-8 numeric probe is required before any replay/search authorization.
Risk-defense/regime fields are allowed as interaction inputs, not standalone alpha seeds.
L7 ranked-return remains diagnostic-only for promotion.
```
