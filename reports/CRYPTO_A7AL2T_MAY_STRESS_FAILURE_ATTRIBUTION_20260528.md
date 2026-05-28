# CRYPTO A7AL-2T May-Stress Failure Attribution

Generated: 2026-05-28T13:29:34Z

## Decision

```text
HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION
```

This stage performs attribution only. It uses May as a post-selection stress/failure label, not as a selector, ranker, mutation prior, or training target.

## Manifest

```json
{
  "authorizes_a7al2u_objective_repair_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_company_full_a7al2q2r": true,
  "authorizes_large_search": false,
  "authorizes_local_expansion": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "all_local_candidates_may_sign_flip",
    "all_local_candidates_may_control_dominated"
  ],
  "candidate_entry_rows": 8,
  "decision": "HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION",
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T13:29:34Z",
  "input_a7al2s_decision": "PASS_A7AL2S_LOCAL_FOLLOWUP_CONTRACT_READY",
  "may_control_dominated_rows": 8,
  "required_next": "Prefer company full A7AL-2Q/2R. If unavailable, draft A7AL-2U objective-repair contract; do not run local expansion.",
  "sign_flip_rows": 8,
  "unique_candidates": 4,
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false
}
```

## Candidate Failure Summary

| candidate_id            | entry_label     |   known_may2026_stress |   recent_oos_2026JanApr |   test_2025H2 |   validation_2025H1 |   premay_eval_min_spread |   premay_eval_mean_spread |   may_spread |   may_vs_premay_mean_delta | may_sign_flip   |   premay_max_control_ratio |   premay_hold_count |   premay_warning_count |   may_max_control_ratio |   may_hold_count | may_gates              | a7al2s_tier                                    | warnings      |   control_ratio_premay_max | expression                                                                              | fields                                | field_families       | pattern_id    |   oi_window |   price_window | source         | parent_seed_id          | a7al2t_failure_label                                       | may_used_for_selection   | eligible_for_expansion   |
|:------------------------|:----------------|-----------------------:|------------------------:|--------------:|--------------------:|-------------------------:|--------------------------:|-------------:|---------------------------:|:----------------|---------------------------:|--------------------:|-----------------------:|------------------------:|-----------------:|:-----------------------|:-----------------------------------------------|:--------------|---------------------------:|:----------------------------------------------------------------------------------------|:--------------------------------------|:---------------------|:--------------|------------:|---------------:|:---------------|:------------------------|:-----------------------------------------------------------|:-------------------------|:-------------------------|
| a7al2q_1378ff7d2322adee | label_t1_to_t25 |            -0.00184161 |              0.00202419 |    0.00188264 |          0.00139064 |               0.00139064 |                0.00176583 |  -0.00184161 |                -0.00360743 | True            |                   0.59779  |                   0 |                      0 |                 1.84561 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated    |               |                   0.59779  | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))    | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap |          24 |              8 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 |            -0.00186216 |              0.00200231 |    0.00185863 |          0.00137321 |               0.00137321 |                0.00174472 |  -0.00186216 |                -0.00360688 | True            |                   0.599961 |                   0 |                      0 |                 1.8128  |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated    |               |                   0.59779  | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))    | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap |          24 |              8 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 |            -0.00168807 |              0.00187861 |    0.0015938  |          0.00122872 |               0.00122872 |                0.00156704 |  -0.00168807 |                -0.00325511 | True            |                   0.890176 |                   0 |                      1 |                 1.13016 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated | control_close |                   0.890176 | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap |         168 |            336 | seed_exact     | a7al2k_0a247ec03472983b | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 |            -0.00170667 |              0.00186716 |    0.00159489 |          0.00122841 |               0.00122841 |                0.00156349 |  -0.00170667 |                -0.00327015 | True            |                   0.897048 |                   0 |                      1 |                 1.1284  |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated | control_close |                   0.890176 | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap |         168 |            336 | seed_exact     | a7al2k_0a247ec03472983b | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 |            -0.00165573 |              0.00185126 |    0.00191435 |          0.0012727  |               0.0012727  |                0.00167944 |  -0.00165573 |                -0.00333516 | True            |                   0.813863 |                   0 |                      1 |                 1.28572 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated | control_close |                   0.813863 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap |          48 |             12 | seed_exact     | a7al2k_046e806368e99c76 | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 |            -0.00166795 |              0.00184332 |    0.00192001 |          0.00125696 |               0.00125696 |                0.00167343 |  -0.00166795 |                -0.00334138 | True            |                   0.829293 |                   0 |                      1 |                 1.28283 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated | control_close |                   0.813863 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap |          48 |             12 | seed_exact     | a7al2k_046e806368e99c76 | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 |            -0.00153845 |              0.00182947 |    0.0018574  |          0.00124169 |               0.00124169 |                0.00164285 |  -0.00153845 |                -0.0031813  | True            |                   0.737129 |                   0 |                      0 |                 1.42987 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated    |               |                   0.737129 | Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))   | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap |          48 |             96 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 |            -0.00155474 |              0.00181251 |    0.00185644 |          0.00121804 |               0.00121804 |                0.001629   |  -0.00155474 |                -0.00318374 | True            |                   0.762502 |                   0 |                      0 |                 1.4027  |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated    |               |                   0.737129 | Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))   | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap |          48 |             96 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |

## Split Contrast

| candidate_id            | entry_label     | split                 |   mean_oriented_spread |   may_mean_oriented_spread |   stress_delta_vs_split |   stress_ratio_vs_split | sign_flip_to_may   |
|:------------------------|:----------------|:----------------------|-----------------------:|---------------------------:|------------------------:|------------------------:|:-------------------|
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | validation_2025H1     |             0.00139064 |                -0.00184161 |             -0.00323225 |               -1.32429  | True               |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | test_2025H2           |             0.00188264 |                -0.00184161 |             -0.00372425 |               -0.978204 | True               |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | recent_oos_2026JanApr |             0.00202419 |                -0.00184161 |             -0.0038658  |               -0.909798 | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | validation_2025H1     |             0.00137321 |                -0.00186216 |             -0.00323538 |               -1.35606  | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | test_2025H2           |             0.00185863 |                -0.00186216 |             -0.00372079 |               -1.0019   | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | recent_oos_2026JanApr |             0.00200231 |                -0.00186216 |             -0.00386447 |               -0.930008 | True               |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | validation_2025H1     |             0.00124169 |                -0.00153845 |             -0.00278014 |               -1.23899  | True               |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | test_2025H2           |             0.0018574  |                -0.00153845 |             -0.00339585 |               -0.828278 | True               |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | recent_oos_2026JanApr |             0.00182947 |                -0.00153845 |             -0.00336791 |               -0.840926 | True               |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | validation_2025H1     |             0.00121804 |                -0.00155474 |             -0.00277278 |               -1.27643  | True               |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | test_2025H2           |             0.00185644 |                -0.00155474 |             -0.00341119 |               -0.837484 | True               |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | recent_oos_2026JanApr |             0.00181251 |                -0.00155474 |             -0.00336726 |               -0.857783 | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | validation_2025H1     |             0.0012727  |                -0.00165573 |             -0.00292843 |               -1.30096  | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | test_2025H2           |             0.00191435 |                -0.00165573 |             -0.00357008 |               -0.864903 | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | recent_oos_2026JanApr |             0.00185126 |                -0.00165573 |             -0.00350699 |               -0.894376 | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | validation_2025H1     |             0.00125696 |                -0.00166795 |             -0.00292491 |               -1.32698  | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | test_2025H2           |             0.00192001 |                -0.00166795 |             -0.00358796 |               -0.868721 | True               |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | recent_oos_2026JanApr |             0.00184332 |                -0.00166795 |             -0.00351127 |               -0.904863 | True               |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | validation_2025H1     |             0.00122872 |                -0.00168807 |             -0.00291679 |               -1.37384  | True               |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | test_2025H2           |             0.0015938  |                -0.00168807 |             -0.00328186 |               -1.05915  | True               |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | recent_oos_2026JanApr |             0.00187861 |                -0.00168807 |             -0.00356668 |               -0.898573 | True               |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | validation_2025H1     |             0.00122841 |                -0.00170667 |             -0.00293508 |               -1.38933  | True               |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | test_2025H2           |             0.00159489 |                -0.00170667 |             -0.00330156 |               -1.07008  | True               |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | recent_oos_2026JanApr |             0.00186716 |                -0.00170667 |             -0.00357383 |               -0.914044 | True               |

## May Control Mode Failure

| candidate_id            | entry_label     | variant              |   mean_oriented_spread |   abs_control_spread |   hourly_tstat_naive |
|:------------------------|:----------------|:---------------------|-----------------------:|---------------------:|---------------------:|
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | symbol_shuffle       |             0.0033989  |           0.0033989  |             10.3053  |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | symbol_shuffle       |             0.00337572 |           0.00337572 |             10.2316  |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | symbol_shuffle       |            -0.00219977 |           0.00219977 |             -5.2555  |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | wrong_lag_future_24h |            -0.00218132 |           0.00218132 |             -4.38949 |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | symbol_shuffle       |            -0.00218083 |           0.00218083 |             -5.1987  |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | wrong_lag_future_24h |            -0.0021397  |           0.0021397  |             -4.31321 |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | wrong_lag_future_24h |            -0.0021288  |           0.0021288  |             -4.29883 |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | wrong_lag_future_24h |            -0.00210403 |           0.00210403 |             -4.23246 |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | wrong_lag_future_24h |            -0.0020544  |           0.0020544  |             -4.10161 |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | wrong_lag_future_24h |            -0.00204257 |           0.00204257 |             -4.0863  |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | wrong_lag_stale_168h |            -0.0019258  |           0.0019258  |             -4.07917 |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | wrong_lag_stale_168h |            -0.00190779 |           0.00190779 |             -4.04747 |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | wrong_lag_future_24h |            -0.00190059 |           0.00190059 |             -4.00593 |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | wrong_lag_future_24h |            -0.00189871 |           0.00189871 |             -4.00763 |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | wrong_lag_stale_168h |            -0.00181752 |           0.00181752 |             -3.8469  |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | wrong_lag_stale_168h |            -0.00179171 |           0.00179171 |             -3.79532 |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | wrong_lag_stale_168h |            -0.00178315 |           0.00178315 |             -3.76559 |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | wrong_lag_stale_168h |            -0.00176158 |           0.00176158 |             -3.72539 |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | wrong_lag_stale_168h |            -0.00148448 |           0.00148448 |             -3.17547 |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 | symbol_shuffle       |             0.00145433 |           0.00145433 |              5.06907 |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | wrong_lag_stale_168h |            -0.00143928 |           0.00143928 |             -3.08165 |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | symbol_shuffle       |             0.00141095 |           0.00141095 |              4.9053  |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | symbol_shuffle       |             0.00138024 |           0.00138024 |              4.40017 |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | symbol_shuffle       |             0.00136813 |           0.00136813 |              4.39205 |

## May Symbol Concentration

| candidate_id            | split                |   rank | symbol    |   abs_contribution |   abs_contribution_share |
|:------------------------|:---------------------|-------:|:----------|-------------------:|-------------------------:|
| a7al2q_1378ff7d2322adee | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.0604797 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      2 | NEARUSDT  |           1.38101  |                0.0498106 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      3 | ONDOUSDT  |           1.32977  |                0.0479624 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      4 | SUIUSDT   |           1.12613  |                0.0406176 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      5 | WLDUSDT   |           1.09694  |                0.0395645 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      6 | FILUSDT   |           1.06279  |                0.0383328 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      7 | ARBUSDT   |           0.917609 |                0.0330965 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      8 | UNIUSDT   |           0.861938 |                0.0310885 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      9 | DODOXUSDT |           0.835462 |                0.0301336 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |     10 | ILVUSDT   |           0.789077 |                0.0284605 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.060582  |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      2 | NEARUSDT  |           1.38101  |                0.0498948 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      3 | ONDOUSDT  |           1.19597  |                0.0432095 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      4 | SUIUSDT   |           1.12613  |                0.0406863 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      5 | WLDUSDT   |           1.09694  |                0.0396314 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      6 | FILUSDT   |           1.06279  |                0.0383976 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      7 | DODOXUSDT |           0.934989 |                0.0337804 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      8 | ARBUSDT   |           0.917609 |                0.0331524 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      9 | UNIUSDT   |           0.861938 |                0.0311411 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |     10 | FETUSDT   |           0.818587 |                0.0295749 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.0604935 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      2 | NEARUSDT  |           1.38101  |                0.0498219 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      3 | ONDOUSDT  |           1.26265  |                0.0455518 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      4 | SUIUSDT   |           1.12613  |                0.0406268 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      5 | WLDUSDT   |           1.09694  |                0.0395735 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      6 | FILUSDT   |           1.06279  |                0.0383416 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      7 | ARBUSDT   |           0.917609 |                0.033104  |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      8 | DODOXUSDT |           0.905042 |                0.0326506 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      9 | UNIUSDT   |           0.861938 |                0.0310956 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |     10 | FETUSDT   |           0.818587 |                0.0295317 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.0607535 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      2 | NEARUSDT  |           1.38101  |                0.0500361 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      3 | SUIUSDT   |           1.12613  |                0.0408015 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      4 | WLDUSDT   |           1.09694  |                0.0397436 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      5 | FILUSDT   |           1.06279  |                0.0385064 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      6 | ONDOUSDT  |           1.03344  |                0.0374431 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      7 | DODOXUSDT |           0.991421 |                0.0359206 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      8 | ARBUSDT   |           0.917609 |                0.0332463 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      9 | UNIUSDT   |           0.861938 |                0.0312293 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |     10 | FETUSDT   |           0.804217 |                0.0291379 |

## May Latent Concentration

| candidate_id            | split                |   rank | raw_latent_state_id   |   abs_contribution |   abs_contribution_share |
|:------------------------|:---------------------|-------:|:----------------------|-------------------:|-------------------------:|
| a7al2q_1378ff7d2322adee | known_may2026_stress |      1 | __missing__           |            27.7253 |                        1 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      1 | __missing__           |            27.6785 |                        1 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      1 | __missing__           |            27.719  |                        1 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      1 | __missing__           |            27.6003 |                        1 |

## Action Matrix

| action                           | status                                   | reason                                                                                                         |
|:---------------------------------|:-----------------------------------------|:---------------------------------------------------------------------------------------------------------------|
| company_full_a7al2q2r            | PREFERRED_NEXT_IF_COMPANY_PATH_AVAILABLE | local run only deep-audited 16; full 128 replay should test whether May failure is local-pilot artifact        |
| local_mutation_expansion         | NOT_AUTHORIZED                           | all candidates sign-flip and become control-dominated in May stress                                            |
| a7al2u_objective_repair_contract | AUTHORIZED_FOR_CONTRACT_ONLY             | future selector may penalize pre-May structures that resemble stress-control behavior without using May labels |
| alpha_proof_shadow_paper_live    | NOT_AUTHORIZED                           | known stress failure and local diagnostic-only evidence                                                        |

## Boundary

```text
Authorized:
  company full A7AL-2Q/2R if company path is available
  A7AL-2U objective-repair contract drafting only

Not authorized:
  local mutation expansion
  large search
  alpha proof
  shadow / paper / live
```
