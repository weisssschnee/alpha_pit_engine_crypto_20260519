# CRYPTO A7AC-3 LABEL DIVERSIFICATION DIAGNOSTIC

Generated: 2026-05-29T07:09:24Z

## Decision

`HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION`

A7AC-3 evaluates A7AC-1R representatives across required labels and neutralization modes. It does not generate formulas, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac4_neutralized_representative_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 6,
  "decision": "HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION",
  "decision_counts": {
    "A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS": 33,
    "HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED": 75
  },
  "executes_formula_generation": false,
  "executes_label_diagnostic": true,
  "executes_search": false,
  "executes_training": false,
  "full_timestamps_before_subset": 21025,
  "generated_at": "2026-05-29T07:09:24Z",
  "horizons": [
    1,
    4
  ],
  "input_a7ac2_decision": "PASS_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_READY_FOR_A7AC3",
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L7_ranked_future_return"
  ],
  "latent_group_status": "deferred_dynamic_latent_neutralization_not_run_in_A7AC3",
  "metric_rows": 3780,
  "neutralization_modes": [
    "global_rank",
    "liquidity_tier_neutral",
    "meme_multiplier_neutral"
  ],
  "neutralized_pass_candidates": 6,
  "non_rank_pass_candidates": 1,
  "pass_rows": 33,
  "stage": "A7AC-3",
  "symbols_loaded": 96,
  "timestamps": 21025,
  "uses_may": false
}
```

## Decision Counts

| decision                                      |   count |
|:----------------------------------------------|--------:|
| HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED    |      75 |
| A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS |      33 |

## Label / Neutralization Summary

| label_family                       | neutralization_mode     |   rows |   pass_rows |   candidates |   pass_candidates |   median_control_ratio |
|:-----------------------------------|:------------------------|-------:|------------:|-------------:|------------------:|-----------------------:|
| L7_ranked_future_return            | meme_multiplier_neutral |     12 |          11 |            6 |                 6 |               0.80194  |
| L7_ranked_future_return            | global_rank             |     12 |          10 |            6 |                 6 |               0.741759 |
| L7_ranked_future_return            | liquidity_tier_neutral  |     12 |          10 |            6 |                 5 |               0.835858 |
| L0_raw_forward_return              | liquidity_tier_neutral  |     12 |           1 |            6 |                 1 |               5.49078  |
| L1_cross_sectional_relative_return | liquidity_tier_neutral  |     12 |           1 |            6 |                 1 |               5.49078  |
| L0_raw_forward_return              | global_rank             |     12 |           0 |            6 |                 0 |               9.84335  |
| L0_raw_forward_return              | meme_multiplier_neutral |     12 |           0 |            6 |                 0 |               8.59269  |
| L1_cross_sectional_relative_return | global_rank             |     12 |           0 |            6 |                 0 |               9.84335  |
| L1_cross_sectional_relative_return | meme_multiplier_neutral |     12 |           0 |            6 |                 0 |               8.59269  |

## Candidate Summary

| candidate_id           |   pass_rows |   label_families |   neutralization_modes |   non_rank_pass_rows |
|:-----------------------|------------:|-----------------:|-----------------------:|---------------------:|
| a7ab3_6e301587da1c1fa3 |           8 |                3 |                      3 |                    2 |
| a7ab3_04daf24ce962db97 |           6 |                1 |                      3 |                    0 |
| a7ab3_0bc78809db3a1428 |           6 |                1 |                      3 |                    0 |
| a7ab3_6eb23cd8ce4aeef1 |           6 |                1 |                      3 |                    0 |
| a7ab3_165c7d8966b27a17 |           4 |                1 |                      3 |                    0 |
| a7ab3_4092255ee6888704 |           3 |                1 |                      2 |                    0 |

## Non-Ranked Pass Rows

| candidate_id           | label_family                       |   horizon_h | neutralization_mode    |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   control_ratio_premay_max |   min_oriented_nonoverlap_min_tstat | decision                                      | blockers   | warnings                                       |
|:-----------------------|:-----------------------------------|------------:|:-----------------------|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|---------------------------:|------------------------------------:|:----------------------------------------------|:-----------|:-----------------------------------------------|
| a7ab3_6e301587da1c1fa3 | L0_raw_forward_return              |           4 | liquidity_tier_neutral |                       -1 |                  0.000589099 |            0.000314148 |              0.000483984 |                   0.000474023 |                   0.870285 |                              1.6182 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;neutralized_mode |
| a7ab3_6e301587da1c1fa3 | L1_cross_sectional_relative_return |           4 | liquidity_tier_neutral |                       -1 |                  0.000589099 |            0.000314148 |              0.000483984 |                   0.000474023 |                   0.870285 |                              1.6182 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;neutralized_mode |

## Neutralized Pass Rows

| candidate_id           | label_family                       |   horizon_h | neutralization_mode     |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   one_bar_lag_recent_oriented |   control_ratio_premay_max |   min_oriented_nonoverlap_min_tstat | decision                                      | blockers   | warnings                                                           |
|:-----------------------|:-----------------------------------|------------:|:------------------------|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|------------------------------:|---------------------------:|------------------------------------:|:----------------------------------------------|:-----------|:-------------------------------------------------------------------|
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           1 | liquidity_tier_neutral  |                        1 |                  0.0119056   |            0.0108147   |              0.00856902  |                   0.00824298  |                   0.47151  |                             4.03367 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           1 | meme_multiplier_neutral |                        1 |                  0.00990433  |            0.0109672   |              0.0106533   |                   0.00874489  |                   0.475155 |                             4.45657 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           4 | liquidity_tier_neutral  |                        1 |                  0.015716    |            0.0155258   |              0.0168433   |                   0.0165995   |                   0.813349 |                             3.2668  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                        1 |                  0.0141697   |            0.0165569   |              0.0184764   |                   0.0165906   |                   0.738185 |                             3.09126 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return            |           1 | liquidity_tier_neutral  |                       -1 |                  0.00793545  |            0.00852962  |              0.00790654  |                   0.00575258  |                   0.873816 |                             3.80508 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return            |           4 | liquidity_tier_neutral  |                       -1 |                  0.0109734   |            0.00986846  |              0.0133766   |                   0.0109857   |                   0.434994 |                             3.58264 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                       -1 |                  0.0123112   |            0.012615    |              0.0186258   |                   0.0158544   |                   0.437014 |                             3.85544 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           1 | liquidity_tier_neutral  |                       -1 |                  0.00696435  |            0.00877934  |              0.00802519  |                   0.00788035  |                   0.704857 |                             4.13712 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           1 | meme_multiplier_neutral |                       -1 |                  0.00739859  |            0.00805324  |              0.0103288   |                   0.00988388  |                   0.689058 |                             3.99087 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           4 | liquidity_tier_neutral  |                       -1 |                  0.0113848   |            0.0109714   |              0.0148463   |                   0.0135228   |                   0.858366 |                             3.4156  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                       -1 |                  0.0132962   |            0.0112817   |              0.0181112   |                   0.0171338   |                   0.854848 |                             3.24873 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           1 | liquidity_tier_neutral  |                       -1 |                  0.00994465  |            0.0110085   |              0.00826649  |                   0.00604069  |                   0.431655 |                             3.96483 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           1 | meme_multiplier_neutral |                       -1 |                  0.00958251  |            0.0125338   |              0.00986487  |                   0.00930193  |                   0.524777 |                             4.18066 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           4 | liquidity_tier_neutral  |                       -1 |                  0.0129154   |            0.0149791   |              0.0151423   |                   0.013394    |                   0.67203  |                             3.87899 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                       -1 |                  0.0135542   |            0.017989    |              0.0188838   |                   0.0173311   |                   0.749031 |                             3.72636 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | ranked_return_label;neutralized_mode                               |
| a7ab3_4092255ee6888704 | L7_ranked_future_return            |           1 | meme_multiplier_neutral |                       -1 |                  0.0140121   |            0.0146523   |              0.0145324   |                   0.0157552   |                   0.873089 |                             6.34024 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_4092255ee6888704 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                       -1 |                  0.0221665   |            0.0268727   |              0.0281587   |                   0.0279786   |                   0.892684 |                             5.22254 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_6e301587da1c1fa3 | L0_raw_forward_return              |           4 | liquidity_tier_neutral  |                       -1 |                  0.000589099 |            0.000314148 |              0.000483984 |                   0.000474023 |                   0.870285 |                             1.6182  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;neutralized_mode                     |
| a7ab3_6e301587da1c1fa3 | L1_cross_sectional_relative_return |           4 | liquidity_tier_neutral  |                       -1 |                  0.000589099 |            0.000314148 |              0.000483984 |                   0.000474023 |                   0.870285 |                             1.6182  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;neutralized_mode                     |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           1 | liquidity_tier_neutral  |                       -1 |                  0.0210315   |            0.0233637   |              0.0193825   |                   0.0196485   |                   0.890471 |                             8.14761 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           1 | meme_multiplier_neutral |                       -1 |                  0.022624    |            0.0257196   |              0.0229341   |                   0.0227012   |                   0.887688 |                             7.81382 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           4 | liquidity_tier_neutral  |                       -1 |                  0.0340899   |            0.035567    |              0.0390909   |                   0.0383126   |                   0.945036 |                             6.88065 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           4 | meme_multiplier_neutral |                       -1 |                  0.0366114   |            0.0400188   |              0.0445298   |                   0.0441944   |                   0.947269 |                             6.58101 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | none       | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION",
  "experiment_id": "20260529_a7ac3_label_diversification_diagnostic",
  "inputs": {
    "a7ab8_clue_augmented": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab8_clue_forensic_execution\\a7ab8_clue_augmented.csv",
    "a7ac2_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac2_label_diversification_contract\\a7ac2_manifest.json",
    "a7ac2_subset": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac2_label_diversification_contract\\a7ac2_diagnostic_subset_input.csv",
    "latent_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "meme_taxonomy": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ak_lv3r_contract_meme_taxonomy_audit\\a7ak_lv3r_contract_meme_taxonomy.csv",
    "symbol_classification": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al_universe498_replay_acceptance\\a7am_symbol_classification.csv"
  },
  "mode": "light_diagnostic",
  "next_action": "HOLD; do not expand formula search",
  "objective": "Test whether A7AC-1R representatives survive non-ranked labels and neutralization modes.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AC3_LABEL_DIVERSIFICATION_DIAGNOSTIC_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac3_label_diversification_diagnostic"
  },
  "parameters": {
    "May_usage": "not used",
    "horizons": [
      1,
      4
    ],
    "labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L7_ranked_future_return"
    ],
    "min_active_symbols": 30,
    "min_group_symbols": 8,
    "neutralization_modes": [
      "global_rank",
      "liquidity_tier_neutral",
      "meme_multiplier_neutral"
    ]
  },
  "status": "completed"
}
```
