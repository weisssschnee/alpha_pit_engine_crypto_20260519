# CRYPTO A7AC-0 REPRESENTATIVE FORENSIC CONTRACT

Generated: 2026-05-29T06:46:22Z

## Decision

`PASS_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_READY_FOR_A7AC1_WITH_WARNINGS`

A7AC-0 defines the next forensic execution contract for A7AB-9 representative survivors. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac1_representative_forensic_execution": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_READY_FOR_A7AC1_WITH_WARNINGS",
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:46:22Z",
  "input_a7ab9_decision": "PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL_WITH_WARNINGS",
  "representative_candidate_count": 7,
  "representative_cluster_count": 8,
  "representative_rows": 8,
  "representatives_control_hard_hold_ge_1": 0,
  "representatives_control_warning_ge_0_80": 2,
  "source_survivor_rows": 15,
  "stage": "A7AC-0",
  "top_cluster_share_before_representative_freeze": 0.4,
  "top_label_share": 1.0,
  "uses_may": false,
  "warnings": [
    "representatives_with_control_ratio_warning_ge_0_80",
    "same_candidate_selected_in_multiple_horizons",
    "single_label_family_dominates",
    "top_return_corr_cluster_share_gt_35pct"
  ]
}
```

## Representative Label Summary

| label_family            |   horizon_h |   representative_rows |   median_control_ratio |   median_validation_spread |   median_test_spread |   median_recent_spread |
|:------------------------|------------:|----------------------:|-----------------------:|---------------------------:|---------------------:|-----------------------:|
| L7_ranked_future_return |           4 |                     5 |               0.671699 |                  0.0185042 |            0.0240427 |              0.0285744 |
| L7_ranked_future_return |           1 |                     3 |               0.603111 |                  0.01496   |            0.0163893 |              0.0176457 |

## Representative Cluster Summary

|   return_corr_cluster |   representative_rows |   median_control_ratio |   median_recent_spread |
|----------------------:|----------------------:|-----------------------:|-----------------------:|
|                     2 |                     1 |               0.931427 |              0.0601275 |
|                     0 |                     1 |               0.671699 |              0.0358818 |
|                     1 |                     1 |               0.843594 |              0.0320244 |
|                     3 |                     1 |               0.359941 |              0.0285744 |
|                     5 |                     1 |               0.623753 |              0.0284546 |
|                     4 |                     1 |               0.324949 |              0.0176457 |
|                    19 |                     1 |               0.603111 |              0.0147868 |
|                    15 |                     1 |               0.789442 |              0.0117063 |

## Representative Risk Flags

|   representative_rank | candidate_id           | label_family            |   horizon_h |   return_corr_cluster |   control_ratio_premay_max | top_symbol   | top_month   |   risk_flag_count | risk_flags                                                 |
|----------------------:|:-----------------------|:------------------------|------------:|----------------------:|---------------------------:|:-------------|:------------|------------------:|:-----------------------------------------------------------|
|                     1 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 |                     2 |                   0.931427 | BTCUSDT      | 2025-08     |                 2 | control_ratio_warning_ge_0_80;same_candidate_multi_horizon |
|                     2 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 |                     1 |                   0.843594 | BTCUSDT      | 2025-08     |                 2 | control_ratio_warning_ge_0_80;same_candidate_multi_horizon |
|                     3 | a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 |                     0 |                   0.671699 | 1000RATSUSDT | 2025-10     |                 1 | top_symbol_repeats_in_representative_pool                  |
|                     4 | a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 |                     5 |                   0.623753 | 1000RATSUSDT | 2025-10     |                 1 | top_symbol_repeats_in_representative_pool                  |
|                     5 | a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 |                     3 |                   0.359941 | 1000RATSUSDT | 2025-10     |                 1 | top_symbol_repeats_in_representative_pool                  |
|                     6 | a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 |                     4 |                   0.324949 | 1000RATSUSDT | 2025-10     |                 1 | top_symbol_repeats_in_representative_pool                  |
|                     7 | a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 |                    19 |                   0.603111 | 1000RATSUSDT | 2025-10     |                 1 | top_symbol_repeats_in_representative_pool                  |
|                     8 | a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 |                    15 |                   0.789442 | 1000RATSUSDT | 2026-01     |                 1 | top_symbol_repeats_in_representative_pool                  |

## Required Forensic Tests

| test                                   | purpose                                                                                                         | blocking   |
|:---------------------------------------|:----------------------------------------------------------------------------------------------------------------|:-----------|
| source_of_truth_provenance             | confirm every representative comes from A7AB-9 and no stale A7AB artifacts are reused                           | True       |
| full_window_metric_reproduction        | rerun representative metrics from expressions and compare with A7AB-8 values                                    | True       |
| control_dominance_by_split_and_type    | wrong-lag, stale, shuffle, sign-flip, random-field controls must remain weaker in train/validation/test/recent  | True       |
| nonoverlap_and_block_robust_stats      | replace naive overlapping-hour confidence with horizon-aware non-overlap and block bootstrap summaries          | True       |
| label_family_specificity               | all current representatives are L7 ranked-return clues; audit whether this is a label artifact                  | False      |
| field_native_lag_and_cost_ladder       | check one-bar execution and 2/5/10/20bps cost proxy survival without artificial two-hour delay policy           | True       |
| symbol_month_tier_concentration        | audit symbol, month, listing-age, meme, multiplier, major/alt, and latent-state concentration                   | True       |
| cluster_representative_independence    | verify one representative per return-corr cluster remains diverse after reproduction                            | True       |
| beta_liquidity_latent_neutral_survival | measure BTC/ETH beta, liquidity-tier, latent-state, meme, and multiplier neutral survival                       | True       |
| May_stress_label_only_if_available     | May can only be post-selection stress/veto/failure attribution; never selector, score, generation, or threshold | True       |

## Pass Gates

| gate                          | rule                                                                                                       |
|:------------------------------|:-----------------------------------------------------------------------------------------------------------|
| provenance_clean              | all representatives trace to A7AB-9 source-of-truth artifacts                                              |
| metric_reproduction_tolerance | reproduced validation/test/recent spreads match A7AB-8 within 1e-10 or documented rounding                 |
| control_hard_gate             | reject any representative with control_ratio >= 1.0 in any pre-May split                                   |
| control_warning_gate          | representatives with 0.80 <= control_ratio < 1.0 remain diagnostic only                                    |
| robust_stats_positive         | nonoverlap or block-robust statistics remain positive for validation/test/recent                           |
| lag_and_cost_survival         | one-bar lag and 10bps/20bps cost proxies remain positive                                                   |
| concentration_cap             | no single symbol, month, latent state, meme group, or multiplier group dominates surviving representatives |
| label_concentration_caveat    | single-label-family dominance blocks promotion beyond forensic until independently diversified             |
| no_may_leakage                | May remains stress-only and cannot enter selector, ranking, mutation, generation, or thresholds            |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "contract_only",
  "experiment_id": "20260529_a7ac0_representative_forensic_contract",
  "inputs": {
    "input_decision": "PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL_WITH_WARNINGS",
    "manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab9_survivor_freeze_contract\\a7ab9_manifest.json",
    "representative_pool": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab9_survivor_freeze_contract\\a7ab9_representative_survivor_pool.csv",
    "survivor_pool": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab9_survivor_freeze_contract\\a7ab9_survivor_pool.csv"
  },
  "mode": "light_contract",
  "next_action": "A7AC-1 representative forensic execution",
  "objective": "Define the forensic execution contract for A7AB-9 representative survivors.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac0_representative_forensic_contract"
  },
  "parameters": {
    "May_usage": "stress_only_if_available; not used by A7AC0",
    "formula_generation": false,
    "replay_execution": false,
    "search_execution": false
  },
  "status": "completed"
}
```
