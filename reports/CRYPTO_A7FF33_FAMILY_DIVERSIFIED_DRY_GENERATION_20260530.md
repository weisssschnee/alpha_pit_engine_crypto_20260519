# CRYPTO A7FF-33 FAMILY-DIVERSIFIED DRY GENERATION

Generated: 2026-05-30T11:12:33Z

## Decision

`PASS_A7FF33_FAMILY_DIVERSIFIED_DRY_GENERATION_BUILT_NO_NUMERIC_NO_SEARCH_AUTH`

A7FF-33 builds a larger family-diversified formula asset pool. It executes dry generation only; no numeric probe, replay, search, alpha proof, shadow, paper, or live execution is authorized.

## Manifest

```json
{
  "authorizes_a7ff34_queue_coverage_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_numeric_probe": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "blueprint_count": 24000,
  "company_shard_count": 18,
  "company_wave_basis_root_share": 0.14333333333333334,
  "company_wave_non_basis_share": 0.8566666666666667,
  "company_wave_queue_count": 3600,
  "decision": "PASS_A7FF33_FAMILY_DIVERSIFIED_DRY_GENERATION_BUILT_NO_NUMERIC_NO_SEARCH_AUTH",
  "executes_generation": true,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 7,
  "generated_at": "2026-05-30T11:12:33Z",
  "materialization_queue_count": 6000,
  "motif_count": 10,
  "source_a7ff32_decision": "PASS_A7FF32_FAMILY_DIVERSIFICATION_CONTRACT_READY_FOR_A7FF33_DRY_GENERATION_NO_SEARCH_AUTH",
  "stage": "A7FF-33",
  "uses_may": false,
  "warnings": []
}
```

## Family Summary

| family_id                     | root_family                           | level                          |   formula_count |   skeleton_count |   motif_count |   primary_field_count |   secondary_field_count |
|:------------------------------|:--------------------------------------|:-------------------------------|----------------:|-----------------:|--------------:|----------------------:|------------------------:|
| D0_basis_premium_reference    | basis_premium_like|basis_premium_like | L2_typed_two_field_interaction |            2518 |               60 |             7 |                     1 |                       4 |
| D0_basis_premium_reference    | basis_premium_like|basis_premium_like | L4_factor_candidate_probe      |            1082 |               36 |             3 |                     1 |                       4 |
| D1_open_interest_positioning  | open_interest_like|positioning_like   | L2_typed_two_field_interaction |            3357 |               60 |             7 |                     1 |                       5 |
| D1_open_interest_positioning  | open_interest_like|positioning_like   | L4_factor_candidate_probe      |            1443 |               36 |             3 |                     1 |                       5 |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like    | L2_typed_two_field_interaction |            2518 |               60 |             7 |                     1 |                       4 |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like    | L4_factor_candidate_probe      |            1082 |               36 |             3 |                     1 |                       4 |
| D3_liquidity_volatility_state | liquidity_like|volatility_like        | L2_typed_two_field_interaction |            2518 |               60 |             7 |                     1 |                       4 |
| D3_liquidity_volatility_state | liquidity_like|volatility_like        | L4_factor_candidate_probe      |            1082 |               36 |             3 |                     1 |                       4 |
| D4_regime_relative_value      | regime_state|price_return_like        | L3_state_conditioned_feature   |            2098 |               51 |             7 |                     1 |                       5 |
| D4_regime_relative_value      | regime_state|price_return_like        | L4_factor_candidate_probe      |             902 |               30 |             3 |                     1 |                       5 |
| D5_funding_dense_state        | funding_like|basis_premium_like       | L2_typed_two_field_interaction |            2518 |               60 |             7 |                     1 |                       4 |
| D5_funding_dense_state        | funding_like|basis_premium_like       | L4_factor_candidate_probe      |            1082 |               36 |             3 |                     1 |                       4 |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state         | L3_state_conditioned_feature   |            1260 |               51 |             7 |                     1 |                       3 |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state         | L4_factor_candidate_probe      |             540 |               30 |             3 |                     1 |                       3 |

## Company Queue Summary

| family_id                     | root_family                           |   company_wave_count |   skeleton_count |   motif_count |
|:------------------------------|:--------------------------------------|---------------------:|-----------------:|--------------:|
| D0_basis_premium_reference    | basis_premium_like|basis_premium_like |                  516 |               45 |            10 |
| D1_open_interest_positioning  | open_interest_like|positioning_like   |                  514 |               45 |            10 |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like    |                  514 |               45 |            10 |
| D3_liquidity_volatility_state | liquidity_like|volatility_like        |                  514 |               45 |            10 |
| D4_regime_relative_value      | regime_state|price_return_like        |                  514 |               38 |            10 |
| D5_funding_dense_state        | funding_like|basis_premium_like       |                  514 |               45 |            10 |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state         |                  514 |               38 |            10 |

## Shard Plan

| company_shard   |   row_count |   family_count |   motif_count |   skeleton_count |
|:----------------|------------:|---------------:|--------------:|-----------------:|
| shard_00        |         200 |              7 |            10 |               31 |
| shard_01        |         200 |              7 |            10 |               32 |
| shard_02        |         200 |              7 |            10 |               30 |
| shard_03        |         200 |              7 |            10 |               32 |
| shard_04        |         200 |              7 |            10 |               29 |
| shard_05        |         200 |              7 |            10 |               30 |
| shard_06        |         200 |              7 |            10 |               30 |
| shard_07        |         200 |              7 |            10 |               31 |
| shard_08        |         200 |              7 |            10 |               29 |
| shard_09        |         200 |              7 |            10 |               31 |
| shard_10        |         200 |              7 |            10 |               31 |
| shard_11        |         200 |              7 |            10 |               31 |
| shard_12        |         200 |              7 |            10 |               31 |
| shard_13        |         200 |              7 |            10 |               33 |
| shard_14        |         200 |              7 |            10 |               30 |
| shard_15        |         200 |              7 |            10 |               33 |
| shard_16        |         200 |              7 |            10 |               32 |
| shard_17        |         200 |              7 |            10 |               32 |

## Boundary

```text
dry generation executed: true
numeric probe executed: false
replay executed: false
search executed: false
May used: false
next if PASS: A7FF-34 queue coverage audit
```
