# CRYPTO A7AC-1R REPRESENTATIVE QUARANTINE CONTRACT

Generated: 2026-05-29T06:51:08Z

## Decision

`PASS_A7AC1R_DIAGNOSTIC_SUBSET_FROZEN_READY_FOR_A7AC2_WITH_WARNINGS`

A7AC-1R quarantines A7AC-1 blocked representatives and freezes a diagnostic-only subset. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac2_label_diversification_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_rows": 1,
  "decision": "PASS_A7AC1R_DIAGNOSTIC_SUBSET_FROZEN_READY_FOR_A7AC2_WITH_WARNINGS",
  "diagnostic_candidates": 6,
  "diagnostic_clusters": 7,
  "diagnostic_control_warning_rows": 2,
  "diagnostic_label_families": 1,
  "diagnostic_rows": 7,
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:51:08Z",
  "input_a7ac1_decision": "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_PARTIAL_BLOCKERS",
  "input_representative_rows": 8,
  "stage": "A7AC-1R",
  "uses_may": false,
  "warnings": [
    "diagnostic_subset_has_control_warning_rows",
    "single_label_family_only",
    "same_candidate_multi_horizon"
  ]
}
```

## Diagnostic Representative Subset

|   diagnostic_rank |   representative_rank | candidate_id           | label_family            |   horizon_h |   return_corr_cluster |   max_metric_parity_diff |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   cost20_recent_oriented |   max_control_ratio_by_split |   min_oriented_nonoverlap_median_tstat |   min_oriented_nonoverlap_min_tstat |   min_oriented_hourly_tstat | top_symbol   |   top_symbol_abs_contribution_share | top_month   |   top_month_abs_contribution_share | decision                                           | blockers   | warnings                                               |
|------------------:|----------------------:|:-----------------------|:------------------------|------------:|----------------------:|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|------------------------:|------------------------:|-------------------------:|-------------------------:|-----------------------------:|---------------------------------------:|------------------------------------:|----------------------------:|:-------------|------------------------------------:|:------------|-----------------------------------:|:---------------------------------------------------|:-----------|:-------------------------------------------------------|
|                 1 |                     6 | a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 |                     4 |                        0 |                    0.01496   |              0.0163893 |                0.0176457 |                     0.0164682 |               0.0175782 |               0.017477  |                0.0173082 |                0.0169707 |                     0.324949 |                                5.37267 |                             5.37267 |                     5.37267 | 1000RATSUSDT |                           0.0344432 | 2025-10     |                          0.0667769 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | ranked_return_label_only                               |
|                 2 |                     5 | a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 |                     3 |                        0 |                    0.0169971 |              0.0171859 |                0.0285744 |                     0.0240342 |               0.028428  |               0.0282085 |                0.0278425 |                0.0271106 |                     0.359941 |                                3.3029  |                             3.6149  |                     6.29629 | 1000RATSUSDT |                           0.0341902 | 2025-10     |                          0.0663118 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | ranked_return_label_only                               |
|                 3 |                     7 | a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 |                    19 |                        0 |                    0.0132668 |              0.0115049 |                0.0147868 |                     0.0136108 |               0.0147305 |               0.014646  |                0.0145053 |                0.0142237 |                     0.603111 |                                4.7092  |                             4.7092  |                     4.7092  | 1000RATSUSDT |                           0.0259285 | 2025-10     |                          0.0665965 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | ranked_return_label_only                               |
|                 4 |                     4 | a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 |                     5 |                        0 |                    0.0185042 |              0.0240427 |                0.0284546 |                     0.0252509 |               0.0283835 |               0.0282767 |                0.0280988 |                0.027743  |                     0.623753 |                                3.52965 |                             3.68087 |                     6.73423 | 1000RATSUSDT |                           0.0349647 | 2025-10     |                          0.0666161 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | ranked_return_label_only                               |
|                 5 |                     3 | a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 |                     0 |                        0 |                    0.0237295 |              0.0317847 |                0.0358818 |                     0.0363595 |               0.0356476 |               0.0352964 |                0.034711  |                0.0335402 |                     0.671699 |                                3.96691 |                             4.62496 |                     7.99844 | 1000RATSUSDT |                           0.0297737 | 2025-10     |                          0.065268  | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | ranked_return_label_only                               |
|                 6 |                     2 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 |                     1 |                        0 |                    0.0325732 |              0.0358993 |                0.0320244 |                     0.0301622 |               0.0319926 |               0.0319449 |                0.0318653 |                0.0317062 |                     0.843594 |                                8.61184 |                             8.61184 |                     8.61184 | BTCUSDT      |                           0.0469047 | 2025-08     |                          0.0663701 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label_only |
|                 7 |                     1 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 |                     2 |                        0 |                    0.0505124 |              0.0550301 |                0.0601275 |                     0.0593572 |               0.0600957 |               0.060048  |                0.0599685 |                0.0598095 |                     0.931427 |                                6.52493 |                             6.66569 |                    13.1159  | BTCUSDT      |                           0.0476837 | 2025-08     |                          0.0666756 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label_only |

## Quarantined Representatives

|   representative_rank | candidate_id           | label_family            |   horizon_h |   return_corr_cluster |   max_metric_parity_diff |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   cost20_recent_oriented |   max_control_ratio_by_split |   min_oriented_nonoverlap_median_tstat |   min_oriented_nonoverlap_min_tstat |   min_oriented_hourly_tstat | top_symbol   |   top_symbol_abs_contribution_share | top_month   |   top_month_abs_contribution_share | decision                                   | blockers                      | warnings                 |
|----------------------:|:-----------------------|:------------------------|------------:|----------------------:|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|------------------------:|------------------------:|-------------------------:|-------------------------:|-----------------------------:|---------------------------------------:|------------------------------------:|----------------------------:|:-------------|------------------------------------:|:------------|-----------------------------------:|:-------------------------------------------|:------------------------------|:-------------------------|
|                     8 | a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 |                    15 |                        0 |                   0.00609494 |             0.00553958 |                0.0117063 |                      0.010573 |               0.0114438 |                 0.01105 |                0.0103937 |                 0.009081 |                     0.789442 |                                1.15543 |                           -0.280592 |                     2.49713 | 1000RATSUSDT |                           0.0427526 | 2026-01     |                          0.0663998 | HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED | nonoverlap_tstat_not_positive | ranked_return_label_only |

## Warning Summary

| warning_key                                            |   rows |   candidates |
|:-------------------------------------------------------|-------:|-------------:|
| ranked_return_label_only                               |      5 |            5 |
| control_ratio_warning_ge_0_80;ranked_return_label_only |      2 |            1 |

## Blocker Summary

| blocker_key                   |   rows |   candidates |
|:------------------------------|-------:|-------------:|
| nonoverlap_tstat_not_positive |      1 |            1 |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "PASS_A7AC1R_DIAGNOSTIC_SUBSET_FROZEN_READY_FOR_A7AC2_WITH_WARNINGS",
  "experiment_id": "20260529_a7ac1r_representative_quarantine_contract",
  "inputs": {
    "a7ac1_audit": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1_representative_forensic_execution\\a7ac1_representative_forensic_audit.csv",
    "a7ac1_control": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1_representative_forensic_execution\\a7ac1_control_dominance_by_split.csv",
    "a7ac1_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1_representative_forensic_execution\\a7ac1_manifest.json"
  },
  "mode": "light_contract",
  "next_action": "A7AC-2 label-diversification and neutralization contract",
  "objective": "Quarantine A7AC-1 blocked representatives and freeze a diagnostic-only subset.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AC1R_REPRESENTATIVE_QUARANTINE_CONTRACT_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1r_representative_quarantine_contract"
  },
  "parameters": {
    "May_usage": "not used",
    "blocked_decision": "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED",
    "minimum_diagnostic_clusters": 4,
    "minimum_diagnostic_rows": 4
  },
  "status": "completed"
}
```
