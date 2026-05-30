# CRYPTO A7FF-37 DEEP REPLAY CONTRACT

Generated: 2026-05-30T11:52:53Z

## Decision

`PASS_A7FF37_DEEP_REPLAY_CONTRACT_READY_FOR_A7FF37A_NO_SEARCH_AUTH`

A7FF-37 converts A7FF-36 non-L7 diversified clues into a bounded deep replay queue. Ranked-label-only selected rows are excluded. This is a contract stage only: no replay, no search, no alpha proof.

## Manifest

```json
{
  "authorizes_a7ff37a_bounded_deep_replay": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_block_count": 0,
  "control_warning_count": 1,
  "decision": "PASS_A7FF37_DEEP_REPLAY_CONTRACT_READY_FOR_A7FF37A_NO_SEARCH_AUTH",
  "deep_replay_candidate_count": 4,
  "deep_replay_family_count": 3,
  "deep_replay_motif_count": 4,
  "excluded_selected_count": 5,
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:52:53Z",
  "source_a7ff36_decision": "PASS_A7FF36_DIVERSIFIED_CLUES_READY_FOR_DEEP_REPLAY_CONTRACT_NO_SEARCH_AUTH",
  "stage": "A7FF-37",
  "uses_may": false,
  "warnings": [
    "control_warning_candidate_included",
    "rank_label_selected_rows_excluded"
  ]
}
```

## Deep Replay Queue

| level                          | family_id                  | root_family                           | primary_field                    | secondary_field      | primary_semantic   | secondary_semantic   | primary_route                  | secondary_route                | primary_transform   | secondary_transform   | motif         | expression                                                                  | semantic_pair                         | generation_priority   | candidate_role                                    | modifier_guard_required   | skeleton_key          | production_key        | blueprint_id            | company_shard   | label_family           |   label_horizon_h | forensic_decision         |   control_ratio_premay_max |   score_no_may | deep_replay_role        | control_margin_policy       |
|:-------------------------------|:---------------------------|:--------------------------------------|:---------------------------------|:---------------------|:-------------------|:---------------------|:-------------------------------|:-------------------------------|:--------------------|:----------------------|:--------------|:----------------------------------------------------------------------------|:--------------------------------------|:----------------------|:--------------------------------------------------|:--------------------------|:----------------------|:----------------------|:------------------------|:----------------|:-----------------------|------------------:|:--------------------------|---------------------------:|---------------:|:------------------------|:----------------------------|
| L4_factor_candidate_probe      | D0_basis_premium_reference | basis_premium_like|basis_premium_like | mark_index_basis_bps             | mark_index_basis_bps | basis_premium_like | basis_premium_like   | reference_family_only          | reference_family_only          | level               | delta_1h              | safe_div_clip | Clip(SafeDiv(mark_index_basis_bps,Abs(Delta(mark_index_basis_bps,1))),-5,5) | basis_premium_like|basis_premium_like | P1                    | ordinary_alpha_valid_family_diversification_probe | False                     | skel_6badd2926fa2941d | prod_697b9c1dabd7e8fd | a7ff33_dcdd07a710d41c9f | shard_07        | L5_vol_adjusted_return |                 1 | KEEP_DIAGNOSTIC           |                   0.366579 |        77.5233 | non_l7_diversified_clue | clean_margin_lt_0p80        |
| L3_state_conditioned_feature   | D4_regime_relative_value   | regime_state|price_return_like        | rolling_coverage_168h            | trade_return_1h      | regime_state       | price_return_like    | primary_diversification_target | primary_diversification_target | level               | delta_1h              | spread_rank   | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1)))         | regime_state|price_return_like        | P0                    | ordinary_alpha_valid_family_diversification_probe | True                      | skel_1a1b3fb29dff7328 | prod_ddc50dea71f2cf4f | a7ff33_fe3e0c6a7b32a1d7 | shard_02        | L5_vol_adjusted_return |                 4 | KEEP_WITH_CONTROL_WARNING |                   0.852468 |       103.409  | non_l7_diversified_clue | warning_margin_0p80_to_1p00 |
| L2_typed_two_field_interaction | D5_funding_dense_state     | funding_like|basis_premium_like       | funding_rate_state_last_ffill_8h | mark_index_basis_bps | funding_like       | basis_premium_like   | dense_materializer_target      | dense_materializer_target      | level               | delta_1h              | sub           | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,1))         | funding_like|basis_premium_like       | P1                    | ordinary_alpha_valid_family_diversification_probe | True                      | skel_f8484b844efd270f | prod_f8b57943809caddb | a7ff33_c8b780256ff30837 | shard_09        | L5_vol_adjusted_return |                 8 | KEEP_DIAGNOSTIC           |                   0.548552 |       180.414  | non_l7_diversified_clue | clean_margin_lt_0p80        |
| L4_factor_candidate_probe      | D5_funding_dense_state     | funding_like|basis_premium_like       | funding_rate_state_last_ffill_8h | mark_index_basis_bps | funding_like       | basis_premium_like   | dense_materializer_target      | dense_materializer_target      | level               | level                 | zspread       | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(mark_index_basis_bps))  | funding_like|basis_premium_like       | P1                    | ordinary_alpha_valid_family_diversification_probe | True                      | skel_293cae94cfd91548 | prod_ca17500d2eb777d8 | a7ff33_0c0da14842542e13 | shard_05        | L5_vol_adjusted_return |                 1 | KEEP_DIAGNOSTIC           |                   0.261017 |       129.655  | non_l7_diversified_clue | clean_margin_lt_0p80        |

## Queue Summary

| semantic_pair                         | motif         | label_family           |   replay_count |   max_control_ratio |   mean_score_no_may |
|:--------------------------------------|:--------------|:-----------------------|---------------:|--------------------:|--------------------:|
| basis_premium_like|basis_premium_like | safe_div_clip | L5_vol_adjusted_return |              1 |            0.366579 |             77.5233 |
| funding_like|basis_premium_like       | sub           | L5_vol_adjusted_return |              1 |            0.548552 |            180.414  |
| funding_like|basis_premium_like       | zspread       | L5_vol_adjusted_return |              1 |            0.261017 |            129.655  |
| regime_state|price_return_like        | spread_rank   | L5_vol_adjusted_return |              1 |            0.852468 |            103.409  |

## Excluded Selected Rows

| blueprint_id            | expression                                                                                              | semantic_pair                  | motif         | label_family            |   label_horizon_h |   orientation_from_train |   premay_positive_split_count | premay_all_positive   |   control_ratio_premay_max |   one_bar_lag_recent_oriented | lag_ok   |   robust_median_tstat_floor |   robust_min_tstat_floor | robust_ok   |   cost2_recent_oriented |   cost5_recent_oriented |   cost10_recent_oriented |   avg_n_obs_recent | decision                          |   train_2024_n |   train_2024_mean_spread |   train_2024_tstat |   train_2024_nonoverlap_median_tstat |   train_2024_nonoverlap_min_tstat |   train_2024_positive_rate |   validation_2025H1_n |   validation_2025H1_mean_spread |   validation_2025H1_tstat |   validation_2025H1_nonoverlap_median_tstat |   validation_2025H1_nonoverlap_min_tstat |   validation_2025H1_positive_rate |   test_2025H2_n |   test_2025H2_mean_spread |   test_2025H2_tstat |   test_2025H2_nonoverlap_median_tstat |   test_2025H2_nonoverlap_min_tstat |   test_2025H2_positive_rate |   recent_oos_2026JanApr_n |   recent_oos_2026JanApr_mean_spread |   recent_oos_2026JanApr_tstat |   recent_oos_2026JanApr_nonoverlap_median_tstat |   recent_oos_2026JanApr_nonoverlap_min_tstat |   recent_oos_2026JanApr_positive_rate |   non_l7_bonus |   score_no_may | skeleton_key          |   finite_share |   nonzero_share | is_rank_label_only   | is_non_l7   | control_warning   | control_block   | forensic_decision               | exclusion_reason                 |
|:------------------------|:--------------------------------------------------------------------------------------------------------|:-------------------------------|:--------------|:------------------------|------------------:|-------------------------:|------------------------------:|:----------------------|---------------------------:|------------------------------:|:---------|----------------------------:|-------------------------:|:------------|------------------------:|------------------------:|-------------------------:|-------------------:|:----------------------------------|---------------:|-------------------------:|-------------------:|-------------------------------------:|----------------------------------:|---------------------------:|----------------------:|--------------------------------:|--------------------------:|--------------------------------------------:|-----------------------------------------:|----------------------------------:|----------------:|--------------------------:|--------------------:|--------------------------------------:|-----------------------------------:|----------------------------:|--------------------------:|------------------------------------:|------------------------------:|------------------------------------------------:|---------------------------------------------:|--------------------------------------:|---------------:|---------------:|:----------------------|---------------:|----------------:|:---------------------|:------------|:------------------|:----------------|:--------------------------------|:---------------------------------|
| a7ff33_8f587010df0608c7 | Sub(rolling_coverage_168h,trade_return_1h)                                                              | regime_state|price_return_like | sub           | L7_ranked_future_return |                 1 |                        1 |                             3 | True                  |                   0.235941 |                     0.023036  | True     |                     6.23942 |                 6.23942  | True        |               0.0724315 |               0.0718315 |                0.0708315 |            95.8667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            719 |                0.0742998 |            9.6597  |                              9.6597  |                          9.6597   |                   0.632823 |                   719 |                       0.0447364 |                   6.23942 |                                     6.23942 |                                 6.23942  |                          0.620306 |             719 |                 0.0634821 |             9.62007 |                               9.62007 |                            9.62007 |                    0.670376 |                       719 |                           0.0728315 |                      10.8065  |                                        10.8065  |                                     10.8065  |                              0.666203 |              0 |        77.5956 | skel_337820bc5afcf6cc |       0.827348 |        1        | True                 | False       | False             | False           | HOLD_RANK_LABEL_DIAGNOSTIC_ONLY | rank_label_only_or_control_block |
| a7ff33_eccdfecdad4a4b5d | Mul(Sub(CSRank(rolling_coverage_168h),CSRank(trade_return_1h)),Sign(trade_return_1h))                   | regime_state|price_return_like | signed_spread | L7_ranked_future_return |                 8 |                        1 |                             3 | True                  |                   0.754188 |                     0.0551701 | True     |                     1.5268  |                 0.742179 | True        |               0.0563636 |               0.0557636 |                0.0547636 |            94.9333 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            712 |                0.047357  |            7.17586 |                              2.47106 |                          1.03872  |                   0.615169 |                   712 |                       0.029498  |                   4.34841 |                                     1.5268  |                                 0.742179 |                          0.55618  |             712 |                 0.0432641 |             7.12803 |                               2.3659  |                            2.0354  |                    0.599719 |                       712 |                           0.0567636 |                       8.95929 |                                         3.10533 |                                      2.42789 |                              0.641854 |              0 |        61.0094 | skel_e001e287e8d9140a |       0.827348 |        0.964146 | True                 | False       | False             | False           | HOLD_RANK_LABEL_DIAGNOSTIC_ONLY | rank_label_only_or_control_block |
| a7ff33_93a54d44f21957f9 | Mean(Mul(rolling_coverage_168h,trade_return_1h),4)                                                      | regime_state|price_return_like | smooth_mul    | L7_ranked_future_return |                 4 |                       -1 |                             3 | True                  |                   0.484123 |                     0.0279718 | True     |                     3.205   |                 3.92684  | True        |               0.0536623 |               0.0530623 |                0.0520623 |            95.4667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            713 |               -0.0673585 |           -8.66875 |                             -3.97716 |                         -6.05439  |                   0.371669 |                   716 |                      -0.0459314 |                  -6.33422 |                                    -3.205   |                                -3.92684  |                          0.402235 |             716 |                -0.0504243 |            -7.29009 |                              -3.52434 |                           -4.67591 |                    0.410615 |                       716 |                          -0.0540623 |                      -7.50716 |                                        -3.83389 |                                     -4.32976 |                              0.395251 |              0 |        58.5782 | skel_356a5f3fab58eb27 |       0.826487 |        0.999312 | True                 | False       | False             | False           | HOLD_RANK_LABEL_DIAGNOSTIC_ONLY | rank_label_only_or_control_block |
| a7ff33_20f0d2c26a4f61a2 | Mul(Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,1))),Sign(Delta(trade_return_1h,1))) | regime_state|price_return_like | signed_spread | L7_ranked_future_return |                 8 |                        1 |                             3 | True                  |                   0.757201 |                     0.0546979 | True     |                     1.06166 |                 0.603132 | True        |               0.0519368 |               0.0513368 |                0.0503368 |            94.9333 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            711 |                0.0474509 |            7.45153 |                              2.72068 |                          0.865473 |                   0.603376 |                   712 |                       0.0218891 |                   3.39846 |                                     1.06166 |                                 0.603132 |                          0.549157 |             712 |                 0.0409105 |             6.78726 |                               2.29241 |                            1.51809 |                    0.581461 |                       712 |                           0.0523368 |                       8.4077  |                                         2.76082 |                                      1.94942 |                              0.602528 |              0 |        56.5796 | skel_ab37051588d52fcc |       0.827061 |        0.994193 | True                 | False       | False             | False           | HOLD_RANK_LABEL_DIAGNOSTIC_ONLY | rank_label_only_or_control_block |
| a7ff33_31b8b42aa76b1572 | Mean(Mul(rolling_coverage_168h,Delta(trade_return_1h,1)),4)                                             | regime_state|price_return_like | smooth_mul    | L7_ranked_future_return |                 1 |                       -1 |                             3 | True                  |                   0.341654 |                     0.016946  | True     |                     3.18484 |                 3.18484  | True        |               0.04519   |               0.04459   |                0.04359   |            95.8667 | A7FF35_RANK_LABEL_DIAGNOSTIC_CLUE |            715 |               -0.0463369 |           -6.0986  |                             -6.0986  |                         -6.0986   |                   0.415385 |                   719 |                      -0.0221868 |                  -3.18484 |                                    -3.18484 |                                -3.18484  |                          0.447844 |             719 |                -0.0462369 |            -7.0142  |                              -7.0142  |                           -7.0142  |                    0.401947 |                       719 |                          -0.04559   |                      -6.84352 |                                        -6.84352 |                                     -6.84352 |                              0.368567 |              0 |        50.2483 | skel_644ba0ee0d0e38ee |       0.826199 |        0.993241 | True                 | False       | False             | False           | HOLD_RANK_LABEL_DIAGNOSTIC_ONLY | rank_label_only_or_control_block |

## Replay Plan

```json
{
  "candidate_count": 4,
  "hard_gates": {
    "control_ratio_block": "reject if >= 1.00 in any pre-May split",
    "control_ratio_warning": "flag if 0.80 <= ratio < 1.00",
    "eval_failure_count": 0,
    "may_in_scoring": false,
    "non_l7_required": true,
    "rank_label_only_promotion": false,
    "search_execution": false
  },
  "horizons_hours": [
    1,
    4,
    8,
    24
  ],
  "input_queue": "runtime/a7ff37_deep_replay_contract/a7ff37_deep_replay_queue.csv",
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
    "L7_ranked_future_return_diagnostic_only"
  ],
  "promotion_boundary": "deep replay can only produce research-clue forensic evidence, not alpha proof",
  "required_controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "sign_flip",
    "same_family_placebo"
  ],
  "stage": "A7FF-37A",
  "symbol_universe": "strict_full_history_181",
  "type": "bounded_deep_replay_execution"
}
```

## Boundary

```text
bounded deep replay authorized: true
replay executed: false
search executed: false
May used in scoring: false
alpha proof / shadow / paper / live: false
```
