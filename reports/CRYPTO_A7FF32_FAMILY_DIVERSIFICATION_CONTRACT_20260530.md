# CRYPTO A7FF-32 FAMILY DIVERSIFICATION CONTRACT

Generated: 2026-05-30T11:05:26Z

## Decision

`PASS_A7FF32_FAMILY_DIVERSIFICATION_CONTRACT_READY_FOR_A7FF33_DRY_GENERATION_NO_SEARCH_AUTH`

A7FF-32 responds to A7FF-31: the portfolio clue is not single-symbol or single-month dominated, but it is structurally concentrated in the basis/premium root with very high pairwise correlation. This contract allows a larger dry-generation asset build only if the next pool is root-family diversified.

## Manifest

```json
{
  "allowed_family_count": 7,
  "authorizes_a7ff33_family_diversified_dry_generation": true,
  "authorizes_alpha_proof": false,
  "authorizes_numeric_probe": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_pattern_count": 8,
  "blockers": [],
  "current_candidate_count": 6,
  "current_max_pairwise_corr_abs": 0.9999999999999998,
  "current_top_symbol_contribution_share": 0.05521294374079854,
  "decision": "PASS_A7FF32_FAMILY_DIVERSIFICATION_CONTRACT_READY_FOR_A7FF33_DRY_GENERATION_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:05:26Z",
  "source_a7ff24r3_decision": "PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH",
  "source_a7ff31_decision": "HOLD_A7FF31_PORTFOLIO_FORENSIC_CONCENTRATED_CLUE_NO_SEARCH_AUTH",
  "stage": "A7FF-32",
  "uses_may": false,
  "warnings": [
    "source_A7FF31_is_hold_by_design",
    "current_clue_pool_all_basis_premium_root"
  ]
}
```

## Current Concentrated Families

| feature_family                        | nearest_known_family   |   held_candidate_count |
|:--------------------------------------|:-----------------------|-----------------------:|
| basis_premium_like|volatility_like    | basis_premium_root     |                      3 |
| basis_premium_like|basis_premium_like | basis_premium_root     |                      2 |
| basis_premium_like                    | basis_premium_root     |                      1 |

## Allowed Family Quotas

| family_id                     | root_family                         | role                           |   min_generation_share |   max_generation_share |   max_selected_share | notes                                                                |
|:------------------------------|:------------------------------------|:-------------------------------|-----------------------:|-----------------------:|---------------------:|:---------------------------------------------------------------------|
| D0_basis_premium_reference    | basis_premium_like                  | reference_family_only          |                   0.05 |                   0.25 |                 0.2  | Existing clue root; cannot dominate next pool.                       |
| D1_open_interest_positioning  | open_interest_like|positioning_like | primary_diversification_target |                   0.15 |                   0.35 |                 0.3  | OI/positioning interaction, not direct OI-price rerun.               |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like  | primary_diversification_target |                   0.1  |                   0.25 |                 0.25 | Aggressive taker flow under leverage expansion/contraction.          |
| D3_liquidity_volatility_state | liquidity_like|volatility_like      | primary_diversification_target |                   0.1  |                   0.25 |                 0.25 | Liquidity/volatility state with strict control dominance gate.       |
| D4_regime_relative_value      | regime_state|price_return_like      | primary_diversification_target |                   0.1  |                   0.25 |                 0.25 | Upper-regime conditioned relative-value, not direct regime-as-alpha. |
| D5_funding_dense_state        | funding_like|basis_premium_like     | dense_materializer_target      |                   0.1  |                   0.25 |                 0.25 | Only dense funding fields; raw funding_rate tail is blocked.         |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state       | diagnostic_to_signal_bridge    |                   0.05 |                   0.15 |                 0.15 | Age/latent lifecycle interactions; must survive neutralization.      |

## Blocked Patterns

| pattern                      | rule                                                                             |
|:-----------------------------|:---------------------------------------------------------------------------------|
| basis_premium_root_only_pool | basis_premium_like selected share > 0.20 blocks progression                      |
| raw_funding_rate_tail        | raw funding_rate cannot be used in repaired tail; use dense funding state fields |
| same_skeleton_cluster        | single skeleton selected share > 0.15 blocks progression                         |
| SafeDiv_unbounded            | SafeDiv requires denominator guard and winsor/clip audit                         |
| L7_ranked_label_only         | ranked-return-only evidence remains diagnostic-only                              |
| control_dominated            | control_ratio >= 1.00 rejects; 0.80-1.00 warns                                   |
| May_in_selector              | May cannot enter generation, selector, ranking, weight update, or mutation       |
| direct_OI_price_rerun        | direct OI-price remains weak prior; no same-objective rerun                      |

## Generation Scale Policy

```json
{
  "company_shard_count": 18,
  "company_wave_queue_target": 3600,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_blueprint_target": 24000,
  "materialization_queue_target": 6000,
  "min_motif_count": 10,
  "min_non_basis_company_wave_share": 0.65,
  "min_non_basis_generation_share": 0.65,
  "min_root_family_count": 6,
  "notes": "Scale is deliberately larger than A7FF-24R, but it is still dry generation / asset construction only.",
  "stage": "A7FF-33",
  "type": "family_diversified_dry_generation_plan"
}
```

## Selector Diversity Policy

```json
{
  "max_selected_basis_premium_root_share": 0.2,
  "max_selected_single_production_key_share": 0.1,
  "max_selected_single_root_family_share": 0.3,
  "max_selected_single_skeleton_share": 0.15,
  "min_selected_root_family_count": 5,
  "min_selected_signal_vector_cluster_count": 8,
  "must_attach_negative_controls": true,
  "must_log_field_roles": true,
  "must_not_use_may": true,
  "must_use_response_backed_field_roles": true
}
```

## Boundary

```text
dry generation authorized: A7FF-33 only
numeric probe authorized: false
replay authorized: false
search authorized: false
alpha proof / shadow / paper / live: false
May usage: forbidden in generation, selector, ranking, mutation, and weight update
```
