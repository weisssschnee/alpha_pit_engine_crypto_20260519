# CRYPTO A7AC-1 REPRESENTATIVE FORENSIC EXECUTION

Generated: 2026-05-29T06:51:05Z

## Decision

`HOLD_A7AC1_REPRESENTATIVE_FORENSIC_PARTIAL_BLOCKERS`

A7AC-1 audits A7AB-9 representatives using A7AB-8 full-window metrics. It does not generate formulas, run new replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac1r_representative_quarantine_contract": true,
  "authorizes_a7ac2_label_diversification_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_PARTIAL_BLOCKERS",
  "decision_counts": {
    "A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS": 7,
    "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED": 1
  },
  "diagnostic_pass_candidates": 6,
  "diagnostic_pass_clusters": 7,
  "diagnostic_pass_rows": 7,
  "executes_new_replay": false,
  "executes_representative_forensic": true,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:51:05Z",
  "hard_block_rows": 1,
  "input_a7ac0_decision": "PASS_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_READY_FOR_A7AC1_WITH_WARNINGS",
  "representative_rows": 8,
  "stage": "A7AC-1",
  "uses_may": false,
  "warning_pass_rows": 7,
  "warnings": [
    "diagnostic_pass_rows_have_warnings",
    "single_label_family_only",
    "same_candidate_multi_horizon"
  ]
}
```

## Decision Counts

| decision                                           |   count |
|:---------------------------------------------------|--------:|
| A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS |       7 |
| HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED         |       1 |

## Representative Forensic Audit

|   representative_rank | candidate_id           | label_family            |   horizon_h |   return_corr_cluster |   max_metric_parity_diff |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   cost20_recent_oriented |   max_control_ratio_by_split |   min_oriented_nonoverlap_median_tstat |   min_oriented_nonoverlap_min_tstat |   min_oriented_hourly_tstat | top_symbol   |   top_symbol_abs_contribution_share | top_month   |   top_month_abs_contribution_share | decision                                           | blockers                      | warnings                                               |
|----------------------:|:-----------------------|:------------------------|------------:|----------------------:|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|------------------------:|------------------------:|-------------------------:|-------------------------:|-----------------------------:|---------------------------------------:|------------------------------------:|----------------------------:|:-------------|------------------------------------:|:------------|-----------------------------------:|:---------------------------------------------------|:------------------------------|:-------------------------------------------------------|
|                     1 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 |                     2 |                        0 |                   0.0505124  |             0.0550301  |                0.0601275 |                     0.0593572 |               0.0600957 |               0.060048  |                0.0599685 |                0.0598095 |                     0.931427 |                                6.52493 |                            6.66569  |                    13.1159  | BTCUSDT      |                           0.0476837 | 2025-08     |                          0.0666756 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | control_ratio_warning_ge_0_80;ranked_return_label_only |
|                     2 | a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 |                     1 |                        0 |                   0.0325732  |             0.0358993  |                0.0320244 |                     0.0301622 |               0.0319926 |               0.0319449 |                0.0318653 |                0.0317062 |                     0.843594 |                                8.61184 |                            8.61184  |                     8.61184 | BTCUSDT      |                           0.0469047 | 2025-08     |                          0.0663701 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | control_ratio_warning_ge_0_80;ranked_return_label_only |
|                     3 | a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 |                     0 |                        0 |                   0.0237295  |             0.0317847  |                0.0358818 |                     0.0363595 |               0.0356476 |               0.0352964 |                0.034711  |                0.0335402 |                     0.671699 |                                3.96691 |                            4.62496  |                     7.99844 | 1000RATSUSDT |                           0.0297737 | 2025-10     |                          0.065268  | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | ranked_return_label_only                               |
|                     4 | a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 |                     5 |                        0 |                   0.0185042  |             0.0240427  |                0.0284546 |                     0.0252509 |               0.0283835 |               0.0282767 |                0.0280988 |                0.027743  |                     0.623753 |                                3.52965 |                            3.68087  |                     6.73423 | 1000RATSUSDT |                           0.0349647 | 2025-10     |                          0.0666161 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | ranked_return_label_only                               |
|                     5 | a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 |                     3 |                        0 |                   0.0169971  |             0.0171859  |                0.0285744 |                     0.0240342 |               0.028428  |               0.0282085 |                0.0278425 |                0.0271106 |                     0.359941 |                                3.3029  |                            3.6149   |                     6.29629 | 1000RATSUSDT |                           0.0341902 | 2025-10     |                          0.0663118 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | ranked_return_label_only                               |
|                     6 | a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 |                     4 |                        0 |                   0.01496    |             0.0163893  |                0.0176457 |                     0.0164682 |               0.0175782 |               0.017477  |                0.0173082 |                0.0169707 |                     0.324949 |                                5.37267 |                            5.37267  |                     5.37267 | 1000RATSUSDT |                           0.0344432 | 2025-10     |                          0.0667769 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | ranked_return_label_only                               |
|                     7 | a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 |                    19 |                        0 |                   0.0132668  |             0.0115049  |                0.0147868 |                     0.0136108 |               0.0147305 |               0.014646  |                0.0145053 |                0.0142237 |                     0.603111 |                                4.7092  |                            4.7092   |                     4.7092  | 1000RATSUSDT |                           0.0259285 | 2025-10     |                          0.0665965 | A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS | none                          | ranked_return_label_only                               |
|                     8 | a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 |                    15 |                        0 |                   0.00609494 |             0.00553958 |                0.0117063 |                     0.010573  |               0.0114438 |               0.01105   |                0.0103937 |                0.009081  |                     0.789442 |                                1.15543 |                           -0.280592 |                     2.49713 | 1000RATSUSDT |                           0.0427526 | 2026-01     |                          0.0663998 | HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED         | nonoverlap_tstat_not_positive | ranked_return_label_only                               |

## Control Dominance By Split

| candidate_id           | label_family            |   horizon_h | split                 |   original_abs_spread | strongest_control_variant   |   strongest_control_abs_spread |   control_ratio | control_hard_hold_ge_1   | control_warning_ge_0_80   |
|:-----------------------|:------------------------|------------:|:----------------------|----------------------:|:----------------------------|-------------------------------:|----------------:|:-------------------------|:--------------------------|
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 | validation_2025H1     |            0.0505124  | wrong_lag_future_1h         |                     0.0470486  |        0.931427 | False                    | True                      |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 | test_2025H2           |            0.0550301  | wrong_lag_future_1h         |                     0.0509843  |        0.926479 | False                    | True                      |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           4 | recent_oos_2026JanApr |            0.0601275  | wrong_lag_future_1h         |                     0.0559749  |        0.930936 | False                    | True                      |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 | validation_2025H1     |            0.0325732  | wrong_lag_future_1h         |                     0.0274786  |        0.843594 | False                    | True                      |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 | test_2025H2           |            0.0358993  | wrong_lag_future_1h         |                     0.0302542  |        0.84275  | False                    | True                      |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return |           1 | recent_oos_2026JanApr |            0.0320244  | wrong_lag_future_1h         |                     0.0268682  |        0.838992 | False                    | True                      |
| a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 | validation_2025H1     |            0.0237295  | wrong_lag_stale_24h         |                     0.0159391  |        0.671699 | False                    | False                     |
| a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 | test_2025H2           |            0.0317847  | wrong_lag_stale_24h         |                     0.0123829  |        0.389586 | False                    | False                     |
| a7ab3_4092255ee6888704 | L7_ranked_future_return |           4 | recent_oos_2026JanApr |            0.0358818  | wrong_lag_stale_24h         |                     0.0147992  |        0.412444 | False                    | False                     |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 | validation_2025H1     |            0.0185042  | wrong_lag_future_1h         |                     0.00903689 |        0.488369 | False                    | False                     |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 | test_2025H2           |            0.0240427  | wrong_lag_future_1h         |                     0.0102554  |        0.426552 | False                    | False                     |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return |           4 | recent_oos_2026JanApr |            0.0284546  | wrong_lag_stale_24h         |                     0.0177487  |        0.623753 | False                    | False                     |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 | validation_2025H1     |            0.0169971  | symbol_shuffle              |                     0.00611796 |        0.359941 | False                    | False                     |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 | test_2025H2           |            0.0171859  | wrong_lag_stale_24h         |                     0.00224964 |        0.1309   | False                    | False                     |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return |           4 | recent_oos_2026JanApr |            0.0285744  | wrong_lag_stale_24h         |                     0.00926952 |        0.324399 | False                    | False                     |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 | validation_2025H1     |            0.01496    | wrong_lag_future_1h         |                     0.00466086 |        0.311554 | False                    | False                     |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 | test_2025H2           |            0.0163893  | wrong_lag_future_1h         |                     0.00304887 |        0.186028 | False                    | False                     |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return |           1 | recent_oos_2026JanApr |            0.0176457  | wrong_lag_future_1h         |                     0.00573397 |        0.324949 | False                    | False                     |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 | validation_2025H1     |            0.0132668  | wrong_lag_future_1h         |                     0.00746537 |        0.562712 | False                    | False                     |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 | test_2025H2           |            0.0115049  | wrong_lag_future_1h         |                     0.00693872 |        0.603111 | False                    | False                     |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return |           1 | recent_oos_2026JanApr |            0.0147868  | wrong_lag_future_1h         |                     0.00885209 |        0.598649 | False                    | False                     |
| a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 | validation_2025H1     |            0.00609494 | symbol_shuffle              |                     0.0048116  |        0.789442 | False                    | False                     |
| a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 | test_2025H2           |            0.00553958 | wrong_lag_stale_24h         |                     0.0025701  |        0.463953 | False                    | False                     |
| a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return |           4 | recent_oos_2026JanApr |            0.0117063  | wrong_lag_stale_24h         |                     0.0070599  |        0.603085 | False                    | False                     |

## Label Summary

| label_family            |   horizon_h |   representative_rows |   diagnostic_pass_rows |   median_recent_spread |   median_control_ratio |   min_nonoverlap_min_tstat |
|:------------------------|------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|---------------------------:|
| L7_ranked_future_return |           4 |                     5 |                      4 |              0.0285744 |               0.671699 |                  -0.280592 |
| L7_ranked_future_return |           1 |                     3 |                      3 |              0.0176457 |               0.603111 |                   4.7092   |

## Cluster Summary

|   return_corr_cluster |   representative_rows |   diagnostic_pass_rows |   median_recent_spread |   median_control_ratio |
|----------------------:|----------------------:|-----------------------:|-----------------------:|-----------------------:|
|                     0 |                     1 |                      1 |              0.0358818 |               0.671699 |
|                     1 |                     1 |                      1 |              0.0320244 |               0.843594 |
|                     2 |                     1 |                      1 |              0.0601275 |               0.931427 |
|                     3 |                     1 |                      1 |              0.0285744 |               0.359941 |
|                     4 |                     1 |                      1 |              0.0176457 |               0.324949 |
|                     5 |                     1 |                      1 |              0.0284546 |               0.623753 |
|                    19 |                     1 |                      1 |              0.0147868 |               0.603111 |
|                    15 |                     1 |                      0 |              0.0117063 |               0.789442 |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_PARTIAL_BLOCKERS",
  "experiment_id": "20260529_a7ac1_representative_forensic_execution",
  "inputs": {
    "a7ab8_decisions": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab8_clue_forensic_execution\\a7ab8_forensic_decisions.csv",
    "a7ab8_metrics": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab8_clue_forensic_execution\\a7ab8_full_window_variant_metrics.csv",
    "a7ac0_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac0_representative_forensic_contract\\a7ac0_manifest.json",
    "representative_pool": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac0_representative_forensic_contract\\a7ac0_representative_input_pool.csv"
  },
  "mode": "light_forensic",
  "next_action": "A7AC-1R representative quarantine contract",
  "objective": "Execute artifact-level forensic checks on A7AB-9 representative survivors.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AC1_REPRESENTATIVE_FORENSIC_EXECUTION_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1_representative_forensic_execution"
  },
  "parameters": {
    "control_hard_gate": "control_ratio < 1.0",
    "control_warning_gate": "control_ratio >= 0.80",
    "cost_bps": [
      2,
      5,
      10,
      20
    ],
    "metric_source": "A7AB-8 full-window metrics",
    "new_formula_generation": false,
    "new_replay_execution": false
  },
  "status": "completed"
}
```
