# CRYPTO A7FF-CORE11 SMALL GATE-NATIVE EXPANSION CONTRACT

Generated: 2026-06-01T00:11:24Z

## Decision

`PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E`

A7FF-CORE11 defines a small gate-native formula expansion from replay-clean seeds. It does not execute generation, materialization, numeric response, replay, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core11e": true,
  "authorizes_large_search": false,
  "authorizes_materialization_execution": false,
  "authorizes_numeric_execution": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E",
  "executes_search": false,
  "generated_at": "2026-06-01T00:11:24Z",
  "generated_total_budget": 4000,
  "motif_bucket_count": 6,
  "next_allowed": "A7FF-CORE11E small gate-native dry generation",
  "seed_candidate_count": 23,
  "semantic_bucket_count": 8,
  "source_decision": "PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT",
  "source_stage": "A7FF-CORE10E",
  "stage": "A7FF-CORE11"
}
```

## Family Budget

| semantic_bucket                      | motif_bucket       |   seed_count |   max_tstat |   median_control_ratio |   generated_budget |
|:-------------------------------------|:-------------------|-------------:|------------:|-----------------------:|-------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    |            7 |     2.87115 |               0.395994 |               1216 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |            4 |     1.94236 |               0.388235 |                696 |
| open_interest_like                   | single             |            3 |     2.73639 |               0.184241 |                522 |
| liquidity_like                       | single             |            2 |     3.03917 |               0.261978 |                348 |
| volatility_like                      | single             |            2 |     2.33048 |               0.438186 |                348 |
| open_interest_like\|positioning_like | delta_x_divergence |            2 |     1.24115 |               0.373554 |                348 |
| taker_flow_like                      | single             |            1 |     2.40812 |               0.275308 |                174 |
| taker_flow_like\|basis_premium_like  | gated_sign         |            1 |     2.38193 |               0.752219 |                174 |
| liquidity_like\|volatility_like      | safe_div_abs       |            1 |     2.30678 |               0.1645   |                174 |

## Grammar Contract

```json
{
  "allowed_transforms": [
    "Mean",
    "Delta",
    "ZScore",
    "Rank",
    "CSRank",
    "TSRank",
    "SafeDiv",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "Clip",
    "Decay"
  ],
  "allowed_window_set": [
    4,
    8,
    12,
    24,
    48,
    72,
    168,
    336
  ],
  "forbidden": [
    "raw expression construction bypassing typed AST gate",
    "legacy quarantined generator entrypoints",
    "May-informed thresholds or masks",
    "label/future/target fields",
    "sign_flip as max-control dominance",
    "full open FormulaGenV2 grammar",
    "large search budget"
  ],
  "mutation_modes": [
    "window_neighbor",
    "operator_neighbor",
    "seed_field_sibling",
    "semantic_pair_preserving_interaction",
    "motif_preserving_simplification",
    "motif_preserving_complexification_depth_lte_4"
  ]
}
```

## Execution Plan

```json
{
  "bounded_replay": 64,
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo"
  ],
  "cost_bps": [
    0,
    2,
    5,
    10
  ],
  "generated_total": 4000,
  "horizons": [
    1,
    4,
    8,
    24
  ],
  "materialization_preflight": 512,
  "numeric_response": 256,
  "primary_labels": [
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "selection_caps": {
    "top_motif_bucket_share": 0.35,
    "top_semantic_bucket_share": 0.35,
    "top_signal_vector_cluster_share": 0.25,
    "top_skeleton_share": 0.2
  }
}
```
