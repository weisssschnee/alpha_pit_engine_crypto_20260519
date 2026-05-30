# CRYPTO A7FF-49 EXISTING-MAP NON-L5 MINING

Generated: 2026-05-30T18:39:23Z

## Decision

`HOLD_A7FF49_NO_NON_REFERENCE_NON_L5_CANDIDATES`

A7FF-49 mines existing numeric maps for strict non-L5 evidence. It does not generate formulas, run numeric probes, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_next_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "non_reference_non_l5_rows_below_6",
    "non_reference_non_l5_family_count_below_2"
  ],
  "decision": "HOLD_A7FF49_NO_NON_REFERENCE_NON_L5_CANDIDATES",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T18:39:23Z",
  "source_a7ffr10_decision": "PASS_A7FFR10_LABEL_FEATURE_TARGET_REDESIGN_READY_FOR_A7FF49_NO_SEARCH_AUTH",
  "stage": "A7FF-49",
  "strict_non_l5_non_reference_family_count": 0,
  "strict_non_l5_non_reference_rows": 0,
  "strict_non_l5_reference_rows": 4,
  "strict_non_l5_rows": 4,
  "uses_may": false,
  "warnings": [
    "non_l5_evidence_exists_only_as_reference_family"
  ]
}
```

## Non-L5 Candidate Summary

| candidate_role              | semantic_pair                         | label_family                       |   rows |   blueprints |   motifs |   median_control_ratio |   min_cost10 |   min_robust_floor |
|:----------------------------|:--------------------------------------|:-----------------------------------|-------:|-------------:|---------:|-----------------------:|-------------:|-------------------:|
| reference_non_l5_diagnostic | basis_premium_like|basis_premium_like | L0_raw_forward_return              |      2 |            2 |        1 |               0.636908 |  6.79017e-05 |            1.39731 |
| reference_non_l5_diagnostic | basis_premium_like|basis_premium_like | L1_cross_sectional_relative_return |      2 |            2 |        1 |               0.636908 |  6.79017e-05 |            1.39731 |

## Non-Reference Non-L5 Candidates

`<empty>`

## Reference Non-L5 Diagnostics

| blueprint_id            | expression                                                                   | semantic_pair                         | motif         | label_family                       |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision            |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate | is_non_l7   | is_numeric_clue   | is_non_l5_target   | is_reference_family   | strict_non_l5_candidate   | candidate_role              |
|:------------------------|:-----------------------------------------------------------------------------|:--------------------------------------|:--------------|:-----------------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:--------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|:------------|:------------------|:-------------------|:----------------------|:--------------------------|:----------------------------|
| a7ff33_cbeab61121c2f170 | Clip(SafeDiv(mark_index_basis_bps,Abs(Mean(mark_index_basis_bps,24))),-5,5)  | basis_premium_like|basis_premium_like | safe_div_clip | L0_raw_forward_return              |                 4 |                       -1 |                             3 | True                  |                   0.598809 |                   0.00127026  | True     |                     1.40245 |                  1.79188 | True        |              0.00199501 |              0.00139501 |              0.000395006 |            95.4667 | A7FF42_NUMERIC_CLUE |            677 |             -0.000218823 |          -0.690855 |                            -0.417925 |                          -1.47053 |                   0.488922 |                   716 |                    -0.000588522 |                  -2.5673  |                                    -1.46189 |                                 -1.79188 |                          0.425978 |             716 |              -0.000761144 |            -2.81898 |                              -1.40245 |                           -1.83017 |                    0.434358 |                       716 |                         -0.00239501 |                      -4.97349 |                                        -2.33758 |                                     -3.31301 |                              0.432961 | True        | True              | True               | True                  | True                      | reference_non_l5_diagnostic |
| a7ff33_cbeab61121c2f170 | Clip(SafeDiv(mark_index_basis_bps,Abs(Mean(mark_index_basis_bps,24))),-5,5)  | basis_premium_like|basis_premium_like | safe_div_clip | L1_cross_sectional_relative_return |                 4 |                       -1 |                             3 | True                  |                   0.598809 |                   0.00127026  | True     |                     1.40245 |                  1.79188 | True        |              0.00199501 |              0.00139501 |              0.000395006 |            95.4667 | A7FF42_NUMERIC_CLUE |            677 |             -0.000218823 |          -0.690855 |                            -0.417925 |                          -1.47053 |                   0.488922 |                   716 |                    -0.000588522 |                  -2.5673  |                                    -1.46189 |                                 -1.79188 |                          0.425978 |             716 |              -0.000761144 |            -2.81898 |                              -1.40245 |                           -1.83017 |                    0.434358 |                       716 |                         -0.00239501 |                      -4.97349 |                                        -2.33758 |                                     -3.31301 |                              0.432961 | True        | True              | True               | True                  | True                      | reference_non_l5_diagnostic |
| a7ff33_2c8641837b7d8288 | Clip(SafeDiv(mark_index_basis_bps,Abs(Decay(mark_index_basis_bps,24))),-5,5) | basis_premium_like|basis_premium_like | safe_div_clip | L0_raw_forward_return              |                 4 |                       -1 |                             3 | True                  |                   0.675006 |                   0.000986721 | True     |                     1.05838 |                  1.39731 | True        |              0.0016679  |              0.0010679  |              6.79017e-05 |            95.4667 | A7FF42_NUMERIC_CLUE |            683 |             -0.000168553 |          -0.548516 |                            -0.189533 |                          -1.52798 |                   0.483163 |                   716 |                    -0.000698608 |                  -2.95564 |                                    -1.61464 |                                 -2.4438  |                          0.417598 |             716 |              -0.000529429 |            -1.93515 |                              -1.05838 |                           -1.39731 |                    0.434358 |                       716 |                         -0.0020679  |                      -4.61356 |                                        -2.14084 |                                     -3.75671 |                              0.445531 | True        | True              | True               | True                  | True                      | reference_non_l5_diagnostic |
| a7ff33_2c8641837b7d8288 | Clip(SafeDiv(mark_index_basis_bps,Abs(Decay(mark_index_basis_bps,24))),-5,5) | basis_premium_like|basis_premium_like | safe_div_clip | L1_cross_sectional_relative_return |                 4 |                       -1 |                             3 | True                  |                   0.675006 |                   0.000986721 | True     |                     1.05838 |                  1.39731 | True        |              0.0016679  |              0.0010679  |              6.79017e-05 |            95.4667 | A7FF42_NUMERIC_CLUE |            683 |             -0.000168553 |          -0.548516 |                            -0.189533 |                          -1.52798 |                   0.483163 |                   716 |                    -0.000698608 |                  -2.95564 |                                    -1.61464 |                                 -2.4438  |                          0.417598 |             716 |              -0.000529429 |            -1.93515 |                              -1.05838 |                           -1.39731 |                    0.434358 |                       716 |                         -0.0020679  |                      -4.61356 |                                        -2.14084 |                                     -3.75671 |                              0.445531 | True        | True              | True               | True                  | True                      | reference_non_l5_diagnostic |

## Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
