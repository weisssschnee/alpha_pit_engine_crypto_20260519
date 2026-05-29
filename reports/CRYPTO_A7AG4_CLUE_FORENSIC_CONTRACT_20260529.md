# CRYPTO A7AG-4 CLUE FORENSIC CONTRACT

Generated: 2026-05-29T08:41:21Z

## Decision

`PASS_A7AG4_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AG5`

A7AG-4 classifies A7AG-3 pilot clues by evidence role and defines the next forensic audit. It does not generate formulas, replay, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7ag5_clue_forensic_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "cost20_proxy_survivor_count": 8,
  "decision": "PASS_A7AG4_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AG5",
  "downside_risk_defense_clue_count": 19,
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:41:21Z",
  "input_a7ag3_decision": "PASS_A7AG3_NUMERIC_REPLAY_PILOT_CLUES_FOUND_EXECUTION_STILL_HOLD",
  "input_clue_count": 24,
  "near_control_boundary_count": 13,
  "ordinary_alpha_clue_count": 0,
  "stage": "A7AG-4",
  "uses_may": false,
  "vol_adjusted_diagnostic_count": 5
}
```

## Forensic Contract

```json
{
  "inputs": [
    "runtime\\a7ag3_numeric_replay_pilot\\a7ag3_replay_clues.csv",
    "runtime\\a7ag3_numeric_replay_pilot\\a7ag3_candidate_replay_metrics.csv"
  ],
  "not_authorized": [
    "formula_search_execution",
    "large_search",
    "alpha_proof",
    "shadow_paper_live"
  ],
  "ordinary_alpha_rule": "Only L0/L1 G0 clues can be ordinary alpha evidence. L5 vol-adjusted and L6 downside clues remain diagnostic or risk-defense only.",
  "required_a7ag5_audits": [
    "role_specific_label_translation",
    "symbol_month_latent_concentration",
    "cost_ladder_5_10_20bps",
    "expanded_negative_control_margin",
    "ordinary_alpha_vs_risk_defense_separation",
    "duplicate_skeleton_and_production_key_cap"
  ],
  "scope": "forensic contract only; no generation, no search, no alpha proof"
}
```

## Role Summary

| clue_role                             | track_id                        | label_family           |   clue_count |   seed_field_count |   interaction_field_count |   skeleton_count |   median_control_ratio |   max_control_ratio |   cost10_survivors |   cost20_survivors |   near_control_boundary |
|:--------------------------------------|:--------------------------------|:-----------------------|-------------:|-------------------:|--------------------------:|-----------------:|-----------------------:|--------------------:|-------------------:|-------------------:|------------------------:|
| basis_premium_vol_adjusted_diagnostic | G0_ordinary_alpha_basis_premium | L5_vol_adjusted_return |            2 |                  1 |                         2 |                1 |               0.909281 |            0.954276 |                  2 |                  2 |                       2 |
| downside_risk_defense_clue            | G2_downside_risk_defense        | L6_downside_avoidance  |           19 |                  5 |                         6 |               15 |               0.796129 |            0.92351  |                  8 |                  3 |                       9 |
| neutralized_vol_adjusted_diagnostic   | G1_neutralized_alpha_diagnostic | L5_vol_adjusted_return |            3 |                  1 |                         2 |                3 |               0.838747 |            0.86934  |                  3 |                  3 |                       2 |

## Concentration Summary

| value                                |   count |     share | axis              |
|:-------------------------------------|--------:|----------:|:------------------|
| realized_vol_24h                     |       5 | 0.208333  | interaction_field |
| oi_x_price_move_24h                  |       5 | 0.208333  | interaction_field |
| open_interest_last                   |       4 | 0.166667  | interaction_field |
| realized_vol_168h                    |       3 | 0.125     | interaction_field |
| global_long_short_account_ratio_last |       3 | 0.125     | interaction_field |
| L6_downside_avoidance                |      19 | 0.791667  | label_family      |
| L5_vol_adjusted_return               |       5 | 0.208333  | label_family      |
| 054842e76531                         |       1 | 0.0416667 | production_key    |
| f234bf6383ef                         |       1 | 0.0416667 | production_key    |
| 778d9e8c5729                         |       1 | 0.0416667 | production_key    |
| b487262c4de8                         |       1 | 0.0416667 | production_key    |
| 7516d60f5137                         |       1 | 0.0416667 | production_key    |
| top_long_short_account_ratio_last    |       7 | 0.291667  | seed_field        |
| oi_x_price_move_24h                  |       4 | 0.166667  | seed_field        |
| global_long_short_account_ratio_last |       4 | 0.166667  | seed_field        |
| premium_close_bps                    |       3 | 0.125     | seed_field        |
| mark_index_basis_bps                 |       2 | 0.0833333 | seed_field        |
| f848051eb175                         |       4 | 0.166667  | skeleton_key      |
| 2a637f242373                         |       3 | 0.125     | skeleton_key      |
| fd0e972f2ff5                         |       2 | 0.0833333 | skeleton_key      |
| d8c4d4e4947f                         |       2 | 0.0833333 | skeleton_key      |
| dfc506bdd709                         |       2 | 0.0833333 | skeleton_key      |

## Boundary

```text
A7AG-4 separates ordinary alpha evidence from vol-adjusted diagnostics and downside/risk-defense clues.
There are no ordinary raw/relative alpha clues unless ordinary_alpha_clue_count > 0.
Formula search, large search, alpha proof, shadow, paper, and live remain not authorized.
```
