# CRYPTO A7AD-1 RANKED LABEL TRANSLATION AUDIT

Generated: 2026-05-29T07:31:44Z

## Decision

`HOLD_A7AD1_RANKED_LABEL_TRANSLATION_TOO_NARROW`

A7AD-1 audits whether A7AC ranked-return passes translate into raw or cross-sectional relative PnL proxy. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ad2_translated_candidate_forensic_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7AD1_RANKED_LABEL_TRANSLATION_TOO_NARROW",
  "executes_label_translation_audit": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T07:31:44Z",
  "input_a7ad0_decision": "PASS_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_READY_FOR_A7AD1",
  "l7_pass_candidates": 6,
  "l7_pass_rows": 31,
  "positive_but_blocked_rows": 26,
  "stage": "A7AD-1",
  "translated_candidates": 1,
  "translated_non_global_candidates": 1,
  "translated_rows": 1,
  "translation_rows": 31,
  "uses_may": false
}
```

## Translation Status Summary

| translation_status             | neutralization_mode     |   rows |   candidates |   median_l7_control_ratio |   median_translated_control_ratio |
|:-------------------------------|:------------------------|-------:|-------------:|--------------------------:|----------------------------------:|
| no_raw_or_relative_translation | global_rank             |      2 |            1 |                  0.733409 |                        nan        |
| no_raw_or_relative_translation | liquidity_tier_neutral  |      1 |            1 |                  0.434994 |                        nan        |
| no_raw_or_relative_translation | meme_multiplier_neutral |      1 |            1 |                  0.437014 |                        nan        |
| positive_but_blocked           | meme_multiplier_neutral |     10 |            5 |                  0.80194  |                          6.95349  |
| positive_but_blocked           | global_rank             |      8 |            5 |                  0.647726 |                          6.26243  |
| positive_but_blocked           | liquidity_tier_neutral  |      8 |            5 |                  0.759103 |                          4.84135  |
| translated_to_non_ranked       | liquidity_tier_neutral  |      1 |            1 |                  0.945036 |                          0.870285 |

## Candidate Translation Summary

| candidate_id           |   l7_pass_rows |   translated_rows |   positive_blocked_rows |   neutralization_modes |   median_l7_control_ratio |
|:-----------------------|---------------:|------------------:|------------------------:|-----------------------:|--------------------------:|
| a7ab3_6e301587da1c1fa3 |              6 |                 1 |                       5 |                      3 |                  0.910949 |
| a7ab3_0bc78809db3a1428 |              6 |                 0 |                       6 |                      3 |                  0.574265 |
| a7ab3_6eb23cd8ce4aeef1 |              6 |                 0 |                       6 |                      3 |                  0.60667  |
| a7ab3_04daf24ce962db97 |              6 |                 0 |                       4 |                      3 |                  0.779852 |
| a7ab3_4092255ee6888704 |              3 |                 0 |                       3 |                      2 |                  0.873089 |
| a7ab3_165c7d8966b27a17 |              4 |                 0 |                       2 |                      3 |                  0.436004 |

## Translated Rows

| candidate_id           |   horizon_h | neutralization_mode    |   l7_recent_spread |   l7_control_ratio |   l7_min_nonoverlap_tstat | l7_decision                                   | l7_warnings                                                        | translation_status       | translated_label      |   translated_control_ratio |   translated_recent_spread | translated_neutralization_mode   | translated_blockers   | translated_warnings                            |
|:-----------------------|------------:|:-----------------------|-------------------:|-------------------:|--------------------------:|:----------------------------------------------|:-------------------------------------------------------------------|:-------------------------|:----------------------|---------------------------:|---------------------------:|:---------------------------------|:----------------------|:-----------------------------------------------|
| a7ab3_6e301587da1c1fa3 |           4 | liquidity_tier_neutral |          0.0390909 |           0.945036 |                   6.88065 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | translated_to_non_ranked | L0_raw_forward_return |                   0.870285 |                0.000483984 | liquidity_tier_neutral           | none                  | control_ratio_warning_ge_0_80;neutralized_mode |

## Positive But Blocked Rows

| candidate_id           |   horizon_h | neutralization_mode     |   l7_recent_spread |   l7_control_ratio |   l7_min_nonoverlap_tstat | l7_decision                                   | l7_warnings                                                        | translation_status   | translated_label                   |   translated_control_ratio |   translated_recent_spread | translated_neutralization_mode   | translated_blockers                              | translated_warnings   |
|:-----------------------|------------:|:------------------------|-------------------:|-------------------:|--------------------------:|:----------------------------------------------|:-------------------------------------------------------------------|:---------------------|:-----------------------------------|---------------------------:|---------------------------:|:---------------------------------|:-------------------------------------------------|:----------------------|
| a7ab3_6eb23cd8ce4aeef1 |           1 | global_rank             |         0.0176457  |           0.324949 |                   5.37267 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label                                                | positive_but_blocked | L0_raw_forward_return              |                    9.32552 |                0.000208477 | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_6eb23cd8ce4aeef1 |           1 | liquidity_tier_neutral  |         0.00856902 |           0.47151  |                   4.03367 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                   13.663   |                5.76745e-05 | liquidity_tier_neutral           | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_6eb23cd8ce4aeef1 |           1 | meme_multiplier_neutral |         0.0106533  |           0.475155 |                   4.45657 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                   12.2962  |                8.66676e-05 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_6eb23cd8ce4aeef1 |           4 | global_rank             |         0.0312989  |           0.811818 |                   2.87229 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label                  | positive_but_blocked | L0_raw_forward_return              |                    2.09397 |                0.000407265 | global_rank                      | nonoverlap_tstat_not_positive;control_ratio_ge_1 | none                  |
| a7ab3_6eb23cd8ce4aeef1 |           4 | liquidity_tier_neutral  |         0.0168433  |           0.813349 |                   3.2668  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L1_cross_sectional_relative_return |                    3.26603 |                0.000110994 | liquidity_tier_neutral           | nonoverlap_tstat_not_positive;control_ratio_ge_1 | neutralized_mode      |
| a7ab3_6eb23cd8ce4aeef1 |           4 | meme_multiplier_neutral |         0.0184764  |           0.738185 |                   3.09126 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    3.5671  |                0.000152794 | meme_multiplier_neutral          | nonoverlap_tstat_not_positive;control_ratio_ge_1 | neutralized_mode      |
| a7ab3_165c7d8966b27a17 |           1 | liquidity_tier_neutral  |         0.00790654 |           0.873816 |                   3.80508 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L0_raw_forward_return              |                   42.3556  |                5.86431e-05 | liquidity_tier_neutral           | control_ratio_ge_1;one_bar_lag_fail              | neutralized_mode      |
| a7ab3_165c7d8966b27a17 |           4 | global_rank             |         0.0285744  |           0.324399 |                   3.6149  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label                                                | positive_but_blocked | L1_cross_sectional_relative_return |                   27.0662  |                0.000271806 | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_04daf24ce962db97 |           1 | liquidity_tier_neutral  |         0.00802519 |           0.704857 |                   4.13712 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    4.69033 |                5.50547e-05 | liquidity_tier_neutral           | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_04daf24ce962db97 |           1 | meme_multiplier_neutral |         0.0103288  |           0.689058 |                   3.99087 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                   10.3256  |                6.72772e-05 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_04daf24ce962db97 |           4 | liquidity_tier_neutral  |         0.0148463  |           0.858366 |                   3.4156  | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L0_raw_forward_return              |                    3.08649 |                0.000134958 | liquidity_tier_neutral           | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_04daf24ce962db97 |           4 | meme_multiplier_neutral |         0.0181112  |           0.854848 |                   3.24873 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L1_cross_sectional_relative_return |                    5.58006 |                0.000246294 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_0bc78809db3a1428 |           1 | global_rank             |         0.0163876  |           0.347775 |                   4.92407 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label                                                | positive_but_blocked | L0_raw_forward_return              |                   11.975   |                0.000148022 | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_0bc78809db3a1428 |           1 | liquidity_tier_neutral  |         0.00826649 |           0.431655 |                   3.96483 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    9.5039  |                5.86067e-05 | liquidity_tier_neutral           | control_ratio_ge_1;one_bar_lag_fail              | neutralized_mode      |
| a7ab3_0bc78809db3a1428 |           1 | meme_multiplier_neutral |         0.00986487 |           0.524777 |                   4.18066 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    8.32692 |                7.34953e-05 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_0bc78809db3a1428 |           4 | global_rank             |         0.0284546  |           0.623753 |                   3.68087 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label                                                | positive_but_blocked | L0_raw_forward_return              |                    3.19934 |                0.000262909 | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_0bc78809db3a1428 |           4 | liquidity_tier_neutral  |         0.0151423  |           0.67203  |                   3.87899 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    4.99238 |                9.74209e-05 | liquidity_tier_neutral           | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_0bc78809db3a1428 |           4 | meme_multiplier_neutral |         0.0188838  |           0.749031 |                   3.72636 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label;neutralized_mode                               | positive_but_blocked | L0_raw_forward_return              |                    3.2688  |                0.000160416 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_4092255ee6888704 |           1 | meme_multiplier_neutral |         0.0145324  |           0.873089 |                   6.34024 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L0_raw_forward_return              |                   19.2279  |                0.000122368 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_4092255ee6888704 |           4 | global_rank             |         0.0358818  |           0.671699 |                   4.62496 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | ranked_return_label                                                | positive_but_blocked | L0_raw_forward_return              |                   81.0994  |                0.00100272  | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_4092255ee6888704 |           4 | meme_multiplier_neutral |         0.0281587  |           0.892684 |                   5.22254 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L0_raw_forward_return              |                    8.85846 |                0.000623389 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_6e301587da1c1fa3 |           1 | global_rank             |         0.0320244  |           0.843594 |                   8.61184 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label                  | positive_but_blocked | L0_raw_forward_return              |                    1.3224  |                0.000292995 | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_6e301587da1c1fa3 |           1 | liquidity_tier_neutral  |         0.0193825  |           0.890471 |                   8.14761 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L1_cross_sectional_relative_return |                    2.01014 |                0.000135695 | liquidity_tier_neutral           | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_6e301587da1c1fa3 |           1 | meme_multiplier_neutral |         0.0229341  |           0.887688 |                   7.81382 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L0_raw_forward_return              |                    1.45302 |                0.00015694  | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |
| a7ab3_6e301587da1c1fa3 |           4 | global_rank             |         0.0601275  |           0.931427 |                   6.66569 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label                  | positive_but_blocked | L0_raw_forward_return              |                    1.04482 |                0.00101868  | global_rank                      | control_ratio_ge_1                               | none                  |
| a7ab3_6e301587da1c1fa3 |           4 | meme_multiplier_neutral |         0.0445298  |           0.947269 |                   6.58101 | A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS | control_ratio_warning_ge_0_80;ranked_return_label;neutralized_mode | positive_but_blocked | L1_cross_sectional_relative_return |                    1.10459 |                0.000611994 | meme_multiplier_neutral          | control_ratio_ge_1                               | neutralized_mode      |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "HOLD_A7AD1_RANKED_LABEL_TRANSLATION_TOO_NARROW",
  "experiment_id": "20260529_a7ad1_ranked_label_translation_audit",
  "inputs": {
    "a7ac3_decisions": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac3_label_diversification_diagnostic\\a7ac3_label_neutralization_decisions.csv",
    "a7ad0_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ad0_ranked_label_translation_contract\\a7ad0_manifest.json"
  },
  "mode": "light_diagnostic",
  "next_action": "A7AE non-ranked objective redesign contract",
  "objective": "Audit whether L7 ranked-return passes translate into raw or cross-sectional relative PnL proxy.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AD1_RANKED_LABEL_TRANSLATION_AUDIT_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ad1_ranked_label_translation_audit"
  },
  "parameters": {
    "May_usage": "not used",
    "minimum_non_global_translated_candidates": 2,
    "minimum_translated_candidates": 2,
    "source_label": "L7_ranked_future_return",
    "target_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return"
    ]
  },
  "status": "completed"
}
```
