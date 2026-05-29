# CRYPTO A7AB-2 SEED-CONSTRAINED MICRO-GENERATION CONTRACT

Generated: 2026-05-29T05:39:48Z

## Decision

`PASS_A7AB2_SEED_CONSTRAINED_MICRO_GENERATION_CONTRACT_READY_FOR_A7AB3_DRY_GENERATION`

A7AB-2 is a contract only. It does not generate formulas, run replay, execute search, train a model, or authorize alpha proof.

## Manifest

```json
{
  "authorizes_a7ab3_seed_constrained_dry_generation": true,
  "authorizes_alpha_proof": false,
  "authorizes_fast_replay": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB2_SEED_CONSTRAINED_MICRO_GENERATION_CONTRACT_READY_FOR_A7AB3_DRY_GENERATION",
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T05:39:48Z",
  "quota": {
    "future_deep_audit_cap_if_later_authorized": 16,
    "future_fast_replay_cap_if_later_authorized": 128,
    "generated_total_cap": 4096,
    "max_depth": 4,
    "max_interaction_nodes": 1,
    "max_per_family_share": 0.35,
    "max_per_seed_field_share": 0.25,
    "max_same_skeleton_share": 0.15,
    "min_family_count_static_queue": 3,
    "min_seed_field_count_static_queue": 5,
    "static_selected_cap": 512
  },
  "seed_families": [
    "basis_premium",
    "price_return",
    "volatility"
  ],
  "seed_family_count": 3,
  "seed_field_count": 5,
  "seed_fields": [
    "mark_index_basis_bps",
    "premium_close_bps",
    "realized_vol_168h",
    "realized_vol_24h",
    "trade_return_1h"
  ],
  "stage": "A7AB-2",
  "uses_may": false
}
```

## Allowed Generation Families

| family_id                    | required_seed_family                  | allowed_seed_fields                                                                           | mechanism                                                                             | allowed_transforms                                            | allowed_interactions                    |
|:-----------------------------|:--------------------------------------|:----------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:--------------------------------------------------------------|:----------------------------------------|
| G0_price_return_reversal     | price_return                          | trade_return_1h                                                                               | recent cross-sectional winners mean-revert over ranked future return labels           | level\|cs_rank\|zscore\|winsor\|tsrank\|decay                 | volatility_state\|basis_premium_state   |
| G1_volatility_state_reversal | volatility                            | realized_vol_24h\|realized_vol_168h                                                           | high realized volatility state is tested as risk/reversal state, not standalone proof | level\|cs_rank\|zscore\|winsor\|tsrank\|decay\|horizon_spread | price_return_state\|basis_premium_state |
| G2_basis_premium_dislocation | basis_premium                         | premium_close_bps\|mark_index_basis_bps                                                       | basis/premium change is tested as dislocation/reversion state                         | delta_24h\|cs_rank\|zscore\|winsor\|tsrank\|decay             | price_return_state\|volatility_state    |
| G3_seed_pair_interaction     | price_return+volatility+basis_premium | mark_index_basis_bps\|premium_close_bps\|realized_vol_168h\|realized_vol_24h\|trade_return_1h | only pairwise seed interactions with clean primitive-response lineage                 | Mul\|Sub\|SafeDiv\|Rank\|ZScore\|Clip\|Winsor                 | price_x_vol\|price_x_basis\|basis_x_vol |

## Transform Contract

| operator                 | allowed   | constraint                                      |
|:-------------------------|:----------|:------------------------------------------------|
| Rank                     | True      | cross-sectional per timestamp only              |
| ZScore                   | True      | rolling or cross-sectional; no future fit       |
| TSRank                   | True      | lookback in 24\|72\|168 only                    |
| Delta                    | True      | lookback in 1\|4\|24 only                       |
| Mean                     | True      | lookback in 4\|24\|72\|168 only                 |
| Decay                    | True      | lookback in 4\|12\|24 only                      |
| Sub                      | True      | seed fields only                                |
| Mul                      | True      | max one interaction node                        |
| SafeDiv                  | True      | bounded denominator; no raw price ratio overlay |
| Clip                     | True      | fixed train-only or symmetric constants         |
| Winsor                   | True      | fixed train-only or symmetric constants         |
| SignedPower              | False     | forbidden in A7AB-2                             |
| deep_nested_conditionals | False     | forbidden in A7AB-2                             |

## Hard Gates

| gate                             | rule                                                                                |
|:---------------------------------|:------------------------------------------------------------------------------------|
| seed_lineage_required            | every expression must trace to an A7AB-1 selected seed                              |
| primitive_response_role_required | seed field must be predictive_signal_candidate in A7AA-2                            |
| no_may                           | May cannot enter generation, mutation, selector score, thresholds, or authorization |
| negative_controls_attached       | wrong-lag/stale/shuffle/random controls must be generated with each family          |
| latency_native                   | field-native latency only; no artificial +2h stress policy                          |
| skeleton_diversity               | same skeleton share <= 15% in static queue                                          |
| field_family_diversity           | same family share <= 35% in static queue                                            |

## Forbidden

| item                                     | reason                                                             |
|:-----------------------------------------|:-------------------------------------------------------------------|
| full_open_grammar                        | A7AB-2 is seed-constrained only                                    |
| OI_or_positioning_reactivation           | A7AA response map did not classify OI/positioning as selector seed |
| A7V_activity_liquidity_self_reproduction | previous family failed control/May attribution                     |
| liquidity_x_volatility_old_cluster       | previous cluster concentration failure                             |
| raw_OKX_Binance_direct_price_comparison  | canonical alias risk                                               |
| stale_J5_overlay_aliases                 | previous overlay alias risk                                        |
| May_in_selector_generation_mutation      | May remains post-selection stress only                             |

## Seed Queue Input

|   selector_rank | field_name           | field_family   | transform   | label_family                       |   label_horizon_h |   control_ratio_premay_max | blueprint                                                                                               |
|----------------:|:---------------------|:---------------|:------------|:-----------------------------------|------------------:|---------------------------:|:--------------------------------------------------------------------------------------------------------|
|               1 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 1 |                   0.254317 | primitive_response::trade_return_1h::level::L7_ranked_future_return::1h::short_high                     |
|               2 | trade_return_1h      | price_return   | cs_rank     | L7_ranked_future_return            |                 1 |                   0.254317 | primitive_response::trade_return_1h::cs_rank::L7_ranked_future_return::1h::short_high                   |
|               3 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 4 |                   0.267545 | primitive_response::trade_return_1h::level::L7_ranked_future_return::4h::short_high                     |
|               4 | realized_vol_168h    | volatility     | level       | L7_ranked_future_return            |                 1 |                   0.879498 | primitive_response::realized_vol_168h::level::L7_ranked_future_return::1h::short_high                   |
|               5 | realized_vol_168h    | volatility     | cs_rank     | L7_ranked_future_return            |                 1 |                   0.879498 | primitive_response::realized_vol_168h::cs_rank::L7_ranked_future_return::1h::short_high                 |
|               6 | realized_vol_24h     | volatility     | level       | L7_ranked_future_return            |                 1 |                   0.939508 | primitive_response::realized_vol_24h::level::L7_ranked_future_return::1h::short_high                    |
|               7 | realized_vol_24h     | volatility     | cs_rank     | L7_ranked_future_return            |                 1 |                   0.939508 | primitive_response::realized_vol_24h::cs_rank::L7_ranked_future_return::1h::short_high                  |
|               8 | premium_close_bps    | basis_premium  | delta_24h   | L7_ranked_future_return            |                 1 |                   0.791438 | primitive_response::premium_close_bps::delta_24h::L7_ranked_future_return::1h::short_high               |
|               9 | mark_index_basis_bps | basis_premium  | delta_24h   | L1_cross_sectional_relative_return |                 1 |                   0.785786 | primitive_response::mark_index_basis_bps::delta_24h::L1_cross_sectional_relative_return::1h::short_high |
|              10 | mark_index_basis_bps | basis_premium  | delta_24h   | L0_raw_forward_return              |                 1 |                   0.785786 | primitive_response::mark_index_basis_bps::delta_24h::L0_raw_forward_return::1h::short_high              |
