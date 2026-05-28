# CRYPTO A7AL-2T Company May-Stress Failure Attribution

Generated: 2026-05-28T14:40:46Z

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
  "authorizes_company_full_a7al2q2r": false,
  "authorizes_large_search": false,
  "authorizes_local_expansion": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "all_company_full_candidates_may_sign_flip",
    "all_company_full_candidates_may_control_dominated"
  ],
  "candidate_entry_rows": 28,
  "context": "company_full",
  "decision": "HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION",
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T14:40:46Z",
  "input_a7al2r_base_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\company_a7al2q2r_full_20260528\\runtime\\a7al2r_local_forensic",
  "input_a7al2s_base_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2s_company_full_followup_contract",
  "input_a7al2s_decision": "PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY",
  "may_control_dominated_rows": 28,
  "required_next": "Draft A7AL-2U objective/selector repair contract from company full failure attribution; do not run expansion.",
  "sign_flip_rows": 28,
  "unique_candidates": 14,
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false
}
```

## Candidate Failure Summary

| candidate_id            | entry_label     |   known_may2026_stress |   recent_oos_2026JanApr |   test_2025H2 |   validation_2025H1 |   premay_eval_min_spread |   premay_eval_mean_spread |   may_spread |   may_vs_premay_mean_delta | may_sign_flip   |   premay_max_control_ratio |   premay_hold_count |   premay_warning_count |   may_max_control_ratio |   may_hold_count | may_gates              | a7al2s_tier                                            | warnings      |   control_ratio_premay_max | expression                                                                              | fields                                | field_families       | pattern_id               |   oi_window |   price_window | source         | parent_seed_id          | a7al2t_failure_label                                       | may_used_for_selection   | eligible_for_expansion   |
|:------------------------|:----------------|-----------------------:|------------------------:|--------------:|--------------------:|-------------------------:|--------------------------:|-------------:|---------------------------:|:----------------|---------------------------:|--------------------:|-----------------------:|------------------------:|-----------------:|:-----------------------|:-------------------------------------------------------|:--------------|---------------------------:|:----------------------------------------------------------------------------------------|:--------------------------------------|:---------------------|:-------------------------|------------:|---------------:|:---------------|:------------------------|:-----------------------------------------------------------|:-------------------------|:-------------------------|
| a7al2q_0de0d41346741bd1 | label_t1_to_t25 |            -0.00183553 |              0.0019945  |    0.00186832 |          0.00138455 |               0.00138455 |                0.00174912 |  -0.00183553 |                -0.00358466 | True            |                   0.643831 |                   0 |                      0 |                 1.21572 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.643831 | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,24))))   | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          24 |             24 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_0de0d41346741bd1 | label_t2_to_t26 |            -0.00185283 |              0.00197836 |    0.00184945 |          0.00136829 |               0.00136829 |                0.00173203 |  -0.00185283 |                -0.00358486 | True            |                   0.657288 |                   0 |                      0 |                 1.16083 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.643831 | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,24))))   | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          24 |             24 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_100786d679e5b988 | label_t1_to_t25 |            -0.00160889 |              0.00183462 |    0.00138395 |          0.00136083 |               0.00136083 |                0.00152646 |  -0.00160889 |                -0.00313535 | True            |                   0.783719 |                   0 |                      0 |                 2.19575 |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated |               |                   0.783719 | Mul(Abs(ZScore(Mean(open_interest_value_last,4))),Abs(ZScore(Delta(index_close,72))))   | index_close\|open_interest_value_last | open_interest\|price | oi_abs_x_price_abs_delta |           4 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_100786d679e5b988 | label_t2_to_t26 |            -0.00168867 |              0.00183    |    0.00134209 |          0.0014002  |               0.00134209 |                0.0015241  |  -0.00168867 |                -0.00321277 | True            |                   0.732358 |                   0 |                      0 |                 2.10247 |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated |               |                   0.783719 | Mul(Abs(ZScore(Mean(open_interest_value_last,4))),Abs(ZScore(Delta(index_close,72))))   | index_close\|open_interest_value_last | open_interest\|price | oi_abs_x_price_abs_delta |           4 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_132c2a7c6c4a9142 | label_t1_to_t25 |            -0.00162821 |              0.00192054 |    0.00160048 |          0.00119135 |               0.00119135 |                0.00157079 |  -0.00162821 |                -0.003199   | True            |                   0.814765 |                   0 |                      2 |                 1.21923 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.814765 | Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(trade_close,504)))) | open_interest_value_mean\|trade_close | open_interest\|price | abs_level_gap            |         168 |            504 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 |            -0.00164263 |              0.00191278 |    0.00160201 |          0.00119039 |               0.00119039 |                0.00156839 |  -0.00164263 |                -0.00321103 | True            |                   0.847038 |                   0 |                      2 |                 1.20912 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.814765 | Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(trade_close,504)))) | open_interest_value_mean\|trade_close | open_interest\|price | abs_level_gap            |         168 |            504 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 |            -0.00184161 |              0.00202419 |    0.00188264 |          0.00139064 |               0.00139064 |                0.00176583 |  -0.00184161 |                -0.00360743 | True            |                   0.59779  |                   0 |                      0 |                 1.18447 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.59779  | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))    | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          24 |              8 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 |            -0.00186216 |              0.00200231 |    0.00185863 |          0.00137321 |               0.00137321 |                0.00174472 |  -0.00186216 |                -0.00360688 | True            |                   0.599961 |                   0 |                      0 |                 1.12989 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.59779  | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))    | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          24 |              8 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_2ec6136e6ff32eb3 | label_t1_to_t25 |            -0.00186245 |              0.00173523 |    0.00173132 |          0.00119992 |               0.00119992 |                0.00155549 |  -0.00186245 |                -0.00341794 | True            |                   0.928927 |                   0 |                      1 |                 1.17563 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.928927 | Sub(Abs(ZScore(Mean(open_interest_value_mean,96))),Abs(ZScore(Mean(mark_close,12))))    | mark_close\|open_interest_value_mean  | open_interest\|price | abs_level_gap            |          96 |             12 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_2ec6136e6ff32eb3 | label_t2_to_t26 |            -0.00189241 |              0.00174522 |    0.00172881 |          0.00120754 |               0.00120754 |                0.00156052 |  -0.00189241 |                -0.00345293 | True            |                   0.940786 |                   0 |                      1 |                 1.1624  |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.928927 | Sub(Abs(ZScore(Mean(open_interest_value_mean,96))),Abs(ZScore(Mean(mark_close,12))))    | mark_close\|open_interest_value_mean  | open_interest\|price | abs_level_gap            |          96 |             12 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_33d51890b0068eb6 | label_t1_to_t25 |            -0.00167385 |              0.00185967 |    0.00159128 |          0.00118794 |               0.00118794 |                0.0015463  |  -0.00167385 |                -0.00322015 | True            |                   1.63754  |                   1 |                      1 |                 1.41203 |                1 | HOLD_CONTROL_DOMINATED | hold_control_dominated__may_control_dominated          |               |                   1.63754  | Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(mark_close,336))))  | mark_close\|open_interest_value_mean  | open_interest\|price | abs_level_gap            |         168 |            336 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_33d51890b0068eb6 | label_t2_to_t26 |            -0.00169583 |              0.00185056 |    0.00159147 |          0.00118781 |               0.00118781 |                0.00154328 |  -0.00169583 |                -0.00323912 | True            |                   1.63667  |                   1 |                      1 |                 1.40528 |                1 | HOLD_CONTROL_DOMINATED | hold_control_dominated__may_control_dominated          |               |                   1.63754  | Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(mark_close,336))))  | mark_close\|open_interest_value_mean  | open_interest\|price | abs_level_gap            |         168 |            336 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 |            -0.00240636 |              0.0022963  |    0.00164686 |          0.00156461 |               0.00156461 |                0.00183592 |  -0.00240636 |                -0.00424228 | True            |                   0.820173 |                   0 |                      1 |                 1.5195  |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated | control_close |                   0.820173 | Mul(Abs(ZScore(Mean(open_interest_value_mean,12))),Abs(ZScore(Delta(mark_close,336))))  | mark_close\|open_interest_value_mean  | open_interest\|price | oi_abs_x_price_abs_delta |          12 |            336 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 |            -0.00248794 |              0.00231967 |    0.00159673 |          0.00151158 |               0.00151158 |                0.00180933 |  -0.00248794 |                -0.00429727 | True            |                   0.838551 |                   0 |                      2 |                 1.41945 |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated | control_close |                   0.820173 | Mul(Abs(ZScore(Mean(open_interest_value_mean,12))),Abs(ZScore(Delta(mark_close,336))))  | mark_close\|open_interest_value_mean  | open_interest\|price | oi_abs_x_price_abs_delta |          12 |            336 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 |            -0.00170477 |              0.00197616 |    0.00175702 |          0.00139898 |               0.00139898 |                0.00171072 |  -0.00170477 |                -0.00341549 | True            |                   0.782136 |                   0 |                      0 |                 2.04793 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.782136 | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(mark_close,504))))   | mark_close\|open_interest_value_last  | open_interest\|price | abs_level_gap            |          24 |            504 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 |            -0.00169815 |              0.00196197 |    0.00173291 |          0.00138379 |               0.00138379 |                0.00169289 |  -0.00169815 |                -0.00339104 | True            |                   0.785326 |                   0 |                      0 |                 2.04456 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.782136 | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(mark_close,504))))   | mark_close\|open_interest_value_last  | open_interest\|price | abs_level_gap            |          24 |            504 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 |            -0.00168807 |              0.00187861 |    0.0015938  |          0.00122872 |               0.00122872 |                0.00156704 |  -0.00168807 |                -0.00325511 | True            |                   0.890176 |                   0 |                      2 |                 1.13016 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.890176 | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap            |         168 |            336 | seed_exact     | a7al2k_0a247ec03472983b | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_6671d1fac5e57efe | label_t2_to_t26 |            -0.00170667 |              0.00186716 |    0.00159489 |          0.00122841 |               0.00122841 |                0.00156349 |  -0.00170667 |                -0.00327015 | True            |                   0.897048 |                   0 |                      2 |                 1.1284  |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.890176 | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap            |         168 |            336 | seed_exact     | a7al2k_0a247ec03472983b | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_69d146749c30da3c | label_t1_to_t25 |            -0.00172583 |              0.00208302 |    0.00197776 |          0.0014483  |               0.0014483  |                0.00183636 |  -0.00172583 |                -0.0035622  | True            |                   0.638674 |                   0 |                      0 |                 2.0475  |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.638674 | Sub(Abs(ZScore(Mean(open_interest_value_mean,8))),Abs(ZScore(Mean(index_close,12))))    | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap            |           8 |             12 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_69d146749c30da3c | label_t2_to_t26 |            -0.00180721 |              0.00206548 |    0.00196302 |          0.00143221 |               0.00143221 |                0.00182024 |  -0.00180721 |                -0.00362744 | True            |                   0.647136 |                   0 |                      0 |                 1.95723 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.638674 | Sub(Abs(ZScore(Mean(open_interest_value_mean,8))),Abs(ZScore(Mean(index_close,12))))    | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap            |           8 |             12 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_a4993fe3273bf0c8 | label_t1_to_t25 |            -0.00179313 |              0.00206872 |    0.00189821 |          0.00148381 |               0.00148381 |                0.00181692 |  -0.00179313 |                -0.00361005 | True            |                   0.955399 |                   0 |                      1 |                 1.63444 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.955399 | Sub(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Mean(trade_close,72))))   | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          12 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_a4993fe3273bf0c8 | label_t2_to_t26 |            -0.00185592 |              0.00204504 |    0.00188374 |          0.00147174 |               0.00147174 |                0.00180017 |  -0.00185592 |                -0.00365609 | True            |                   0.960052 |                   0 |                      1 |                 1.54074 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.955399 | Sub(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Mean(trade_close,72))))   | open_interest_value_last\|trade_close | open_interest\|price | abs_level_gap            |          12 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_ca72f5849cff347a | label_t1_to_t25 |            -0.00176346 |              0.00164639 |    0.00137492 |          0.0013379  |               0.0013379  |                0.00145307 |  -0.00176346 |                -0.00321653 | True            |                   0.918655 |                   0 |                      1 |                 1.72326 |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated | control_close |                   0.918655 | Mul(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Delta(mark_close,72))))   | mark_close\|open_interest_value_last  | open_interest\|price | oi_abs_x_price_abs_delta |          12 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_ca72f5849cff347a | label_t2_to_t26 |            -0.00187356 |              0.00165178 |    0.00132659 |          0.00136382 |               0.00132659 |                0.0014474  |  -0.00187356 |                -0.00332096 | True            |                   1.00022  |                   1 |                      0 |                 1.63383 |                1 | HOLD_CONTROL_DOMINATED | hold_timevarying_latent_fragile__may_control_dominated | control_close |                   0.918655 | Mul(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Delta(mark_close,72))))   | mark_close\|open_interest_value_last  | open_interest\|price | oi_abs_x_price_abs_delta |          12 |             72 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 |            -0.00165573 |              0.00185126 |    0.00191435 |          0.0012727  |               0.0012727  |                0.00167944 |  -0.00165573 |                -0.00333516 | True            |                   0.813863 |                   0 |                      1 |                 1.95778 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.813863 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap            |          48 |             12 | seed_exact     | a7al2k_046e806368e99c76 | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 |            -0.00166795 |              0.00184332 |    0.00192001 |          0.00125696 |               0.00125696 |                0.00167343 |  -0.00166795 |                -0.00334138 | True            |                   0.829293 |                   0 |                      1 |                 1.96561 |                1 | HOLD_CONTROL_DOMINATED | watchlist_control_close__may_control_dominated         | control_close |                   0.813863 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | abs_level_gap            |          48 |             12 | seed_exact     | a7al2k_046e806368e99c76 | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED\|PREMAY_CONTROL_CLOSE | False                    | False                    |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 |            -0.00153845 |              0.00182947 |    0.0018574  |          0.00124169 |               0.00124169 |                0.00164285 |  -0.00153845 |                -0.0031813  | True            |                   0.737129 |                   0 |                      0 |                 2.77616 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.737129 | Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))   | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap            |          48 |             96 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 |            -0.00155474 |              0.00181251 |    0.00185644 |          0.00121804 |               0.00121804 |                0.001629   |  -0.00155474 |                -0.00318374 | True            |                   0.762502 |                   0 |                      0 |                 2.74964 |                1 | HOLD_CONTROL_DOMINATED | primary_clean_premay__may_control_dominated            |               |                   0.737129 | Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))   | index_close\|open_interest_value_mean | open_interest\|price | abs_level_gap            |          48 |             96 | local_mutation |                         | MAY_SIGN_FLIP\|MAY_CONTROL_DOMINATED                       | False                    | False                    |

## Split Contrast

| candidate_id            | entry_label     | split                 |   mean_oriented_spread |   may_mean_oriented_spread |   stress_delta_vs_split |   stress_ratio_vs_split | sign_flip_to_may   |
|:------------------------|:----------------|:----------------------|-----------------------:|---------------------------:|------------------------:|------------------------:|:-------------------|
| a7al2q_69d146749c30da3c | label_t1_to_t25 | validation_2025H1     |             0.0014483  |                -0.00172583 |             -0.00317413 |               -1.19162  | True               |
| a7al2q_69d146749c30da3c | label_t1_to_t25 | test_2025H2           |             0.00197776 |                -0.00172583 |             -0.0037036  |               -0.872619 | True               |
| a7al2q_69d146749c30da3c | label_t1_to_t25 | recent_oos_2026JanApr |             0.00208302 |                -0.00172583 |             -0.00380886 |               -0.828523 | True               |
| a7al2q_69d146749c30da3c | label_t2_to_t26 | validation_2025H1     |             0.00143221 |                -0.00180721 |             -0.00323942 |               -1.26183  | True               |
| a7al2q_69d146749c30da3c | label_t2_to_t26 | test_2025H2           |             0.00196302 |                -0.00180721 |             -0.00377022 |               -0.920628 | True               |
| a7al2q_69d146749c30da3c | label_t2_to_t26 | recent_oos_2026JanApr |             0.00206548 |                -0.00180721 |             -0.00387269 |               -0.874958 | True               |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 | validation_2025H1     |             0.00156461 |                -0.00240636 |             -0.00397097 |               -1.53799  | True               |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 | test_2025H2           |             0.00164686 |                -0.00240636 |             -0.00405322 |               -1.46118  | True               |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 | recent_oos_2026JanApr |             0.0022963  |                -0.00240636 |             -0.00470266 |               -1.04793  | True               |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 | validation_2025H1     |             0.00151158 |                -0.00248794 |             -0.00399952 |               -1.64593  | True               |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 | test_2025H2           |             0.00159673 |                -0.00248794 |             -0.00408467 |               -1.55815  | True               |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 | recent_oos_2026JanApr |             0.00231967 |                -0.00248794 |             -0.00480761 |               -1.07254  | True               |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | validation_2025H1     |             0.00139064 |                -0.00184161 |             -0.00323225 |               -1.32429  | True               |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | test_2025H2           |             0.00188264 |                -0.00184161 |             -0.00372425 |               -0.978204 | True               |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | recent_oos_2026JanApr |             0.00202419 |                -0.00184161 |             -0.0038658  |               -0.909798 | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | validation_2025H1     |             0.00137321 |                -0.00186216 |             -0.00323538 |               -1.35606  | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | test_2025H2           |             0.00185863 |                -0.00186216 |             -0.00372079 |               -1.0019   | True               |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | recent_oos_2026JanApr |             0.00200231 |                -0.00186216 |             -0.00386447 |               -0.930008 | True               |
| a7al2q_a4993fe3273bf0c8 | label_t1_to_t25 | validation_2025H1     |             0.00148381 |                -0.00179313 |             -0.00327695 |               -1.20846  | True               |
| a7al2q_a4993fe3273bf0c8 | label_t1_to_t25 | test_2025H2           |             0.00189821 |                -0.00179313 |             -0.00369134 |               -0.944645 | True               |
| a7al2q_a4993fe3273bf0c8 | label_t1_to_t25 | recent_oos_2026JanApr |             0.00206872 |                -0.00179313 |             -0.00386186 |               -0.866782 | True               |
| a7al2q_a4993fe3273bf0c8 | label_t2_to_t26 | validation_2025H1     |             0.00147174 |                -0.00185592 |             -0.00332766 |               -1.26103  | True               |
| a7al2q_a4993fe3273bf0c8 | label_t2_to_t26 | test_2025H2           |             0.00188374 |                -0.00185592 |             -0.00373965 |               -0.985232 | True               |
| a7al2q_a4993fe3273bf0c8 | label_t2_to_t26 | recent_oos_2026JanApr |             0.00204504 |                -0.00185592 |             -0.00390096 |               -0.90752  | True               |
| a7al2q_0de0d41346741bd1 | label_t1_to_t25 | validation_2025H1     |             0.00138455 |                -0.00183553 |             -0.00322008 |               -1.32573  | True               |
| a7al2q_0de0d41346741bd1 | label_t1_to_t25 | test_2025H2           |             0.00186832 |                -0.00183553 |             -0.00370385 |               -0.982455 | True               |
| a7al2q_0de0d41346741bd1 | label_t1_to_t25 | recent_oos_2026JanApr |             0.0019945  |                -0.00183553 |             -0.00383003 |               -0.920299 | True               |
| a7al2q_0de0d41346741bd1 | label_t2_to_t26 | validation_2025H1     |             0.00136829 |                -0.00185283 |             -0.00322112 |               -1.35412  | True               |
| a7al2q_0de0d41346741bd1 | label_t2_to_t26 | test_2025H2           |             0.00184945 |                -0.00185283 |             -0.00370228 |               -1.00183  | True               |
| a7al2q_0de0d41346741bd1 | label_t2_to_t26 | recent_oos_2026JanApr |             0.00197836 |                -0.00185283 |             -0.00383118 |               -0.936549 | True               |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 | validation_2025H1     |             0.00139898 |                -0.00170477 |             -0.00310375 |               -1.21858  | True               |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 | test_2025H2           |             0.00175702 |                -0.00170477 |             -0.00346179 |               -0.970258 | True               |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 | recent_oos_2026JanApr |             0.00197616 |                -0.00170477 |             -0.00368093 |               -0.862666 | True               |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 | validation_2025H1     |             0.00138379 |                -0.00169815 |             -0.00308195 |               -1.22717  | True               |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 | test_2025H2           |             0.00173291 |                -0.00169815 |             -0.00343106 |               -0.979944 | True               |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 | recent_oos_2026JanApr |             0.00196197 |                -0.00169815 |             -0.00366012 |               -0.865535 | True               |
| a7al2q_132c2a7c6c4a9142 | label_t1_to_t25 | validation_2025H1     |             0.00119135 |                -0.00162821 |             -0.00281956 |               -1.3667   | True               |
| a7al2q_132c2a7c6c4a9142 | label_t1_to_t25 | test_2025H2           |             0.00160048 |                -0.00162821 |             -0.00322869 |               -1.01733  | True               |
| a7al2q_132c2a7c6c4a9142 | label_t1_to_t25 | recent_oos_2026JanApr |             0.00192054 |                -0.00162821 |             -0.00354875 |               -0.84779  | True               |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 | validation_2025H1     |             0.00119039 |                -0.00164263 |             -0.00283302 |               -1.37992  | True               |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 | test_2025H2           |             0.00160201 |                -0.00164263 |             -0.00324465 |               -1.02536  | True               |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 | recent_oos_2026JanApr |             0.00191278 |                -0.00164263 |             -0.00355541 |               -0.85877  | True               |
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
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | symbol_shuffle       |             0.00427499 |           0.00427499 |             11.4089  |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | symbol_shuffle       |             0.00427096 |           0.00427096 |             11.3254  |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 | wrong_lag_future_24h |            -0.00365645 |           0.00365645 |             -7.19565 |
| a7al2q_100786d679e5b988 | label_t2_to_t26 | wrong_lag_future_24h |            -0.00355037 |           0.00355037 |             -6.42547 |
| a7al2q_69d146749c30da3c | label_t2_to_t26 | symbol_shuffle       |             0.00353711 |           0.00353711 |             10.6749  |
| a7al2q_69d146749c30da3c | label_t1_to_t25 | symbol_shuffle       |             0.00353364 |           0.00353364 |             10.6782  |
| a7al2q_100786d679e5b988 | label_t1_to_t25 | wrong_lag_future_24h |            -0.00353271 |           0.00353271 |             -6.39597 |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 | wrong_lag_future_24h |            -0.0035315  |           0.0035315  |             -6.92065 |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 | symbol_shuffle       |            -0.00349125 |           0.00349125 |             -9.59397 |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 | symbol_shuffle       |            -0.00347198 |           0.00347198 |             -9.52557 |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | symbol_shuffle       |            -0.00327854 |           0.00327854 |             -8.23255 |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | symbol_shuffle       |            -0.00324154 |           0.00324154 |             -8.14318 |
| a7al2q_3abec814a5c6d0df | label_t2_to_t26 | symbol_shuffle       |            -0.00319195 |           0.00319195 |             -8.63085 |
| a7al2q_3abec814a5c6d0df | label_t1_to_t25 | symbol_shuffle       |            -0.00318629 |           0.00318629 |             -8.71609 |
| a7al2q_ca72f5849cff347a | label_t2_to_t26 | wrong_lag_future_24h |            -0.00306108 |           0.00306108 |             -5.48717 |
| a7al2q_ca72f5849cff347a | label_t1_to_t25 | wrong_lag_future_24h |            -0.0030389  |           0.0030389  |             -5.46158 |
| a7al2q_ca72f5849cff347a | label_t2_to_t26 | symbol_shuffle       |            -0.00303301 |           0.00303301 |             -9.23463 |
| a7al2q_69d146749c30da3c | label_t1_to_t25 | wrong_lag_future_24h |            -0.00300179 |           0.00300179 |             -6.09695 |
| a7al2q_ca72f5849cff347a | label_t1_to_t25 | symbol_shuffle       |            -0.00297752 |           0.00297752 |             -9.245   |
| a7al2q_69d146749c30da3c | label_t2_to_t26 | wrong_lag_future_24h |            -0.00295635 |           0.00295635 |             -5.96822 |
| a7al2q_a4993fe3273bf0c8 | label_t1_to_t25 | wrong_lag_future_24h |            -0.00293077 |           0.00293077 |             -5.9312  |
| a7al2q_a4993fe3273bf0c8 | label_t2_to_t26 | wrong_lag_future_24h |            -0.00285949 |           0.00285949 |             -5.7533  |
| a7al2q_33d51890b0068eb6 | label_t2_to_t26 | symbol_shuffle       |             0.00238312 |           0.00238312 |              5.25661 |
| a7al2q_33d51890b0068eb6 | label_t1_to_t25 | symbol_shuffle       |             0.00236353 |           0.00236353 |              5.21633 |
| a7al2q_5da100b2822dc1a6 | label_t1_to_t25 | wrong_lag_future_24h |            -0.0022381  |           0.0022381  |             -4.48134 |
| a7al2q_0de0d41346741bd1 | label_t1_to_t25 | wrong_lag_future_24h |            -0.0022315  |           0.0022315  |             -4.47979 |
| a7al2q_2ec6136e6ff32eb3 | label_t2_to_t26 | wrong_lag_future_24h |            -0.00219974 |           0.00219974 |             -4.27773 |
| a7al2q_2ec6136e6ff32eb3 | label_t1_to_t25 | wrong_lag_future_24h |            -0.00218955 |           0.00218955 |             -4.26542 |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | wrong_lag_future_24h |            -0.00218132 |           0.00218132 |             -4.38949 |
| a7al2q_5da100b2822dc1a6 | label_t2_to_t26 | wrong_lag_future_24h |            -0.0021711  |           0.0021711  |             -4.32773 |
| a7al2q_0de0d41346741bd1 | label_t2_to_t26 | wrong_lag_future_24h |            -0.00215082 |           0.00215082 |             -4.31595 |
| a7al2q_d6f7ebc0dbbdda7a | label_t2_to_t26 | wrong_lag_future_24h |            -0.0021397  |           0.0021397  |             -4.31321 |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | wrong_lag_future_24h |            -0.0021288  |           0.0021288  |             -4.29883 |
| a7al2q_1378ff7d2322adee | label_t2_to_t26 | wrong_lag_future_24h |            -0.00210403 |           0.00210403 |             -4.23246 |
| a7al2q_f00f22bbcc48dc2c | label_t2_to_t26 | wrong_lag_future_24h |            -0.0020544  |           0.0020544  |             -4.10161 |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | wrong_lag_future_24h |            -0.00204257 |           0.00204257 |             -4.0863  |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 | wrong_lag_future_24h |            -0.00198614 |           0.00198614 |             -4.13527 |
| a7al2q_132c2a7c6c4a9142 | label_t1_to_t25 | wrong_lag_future_24h |            -0.00198516 |           0.00198516 |             -4.1294  |
| a7al2q_132c2a7c6c4a9142 | label_t2_to_t26 | wrong_lag_stale_168h |            -0.0019392  |           0.0019392  |             -4.09639 |
| a7al2q_33d51890b0068eb6 | label_t2_to_t26 | wrong_lag_stale_168h |            -0.00193041 |           0.00193041 |             -4.08477 |

## May Symbol Concentration

| candidate_id            | split                |   rank | symbol    |   abs_contribution |   abs_contribution_share |
|:------------------------|:---------------------|-------:|:----------|-------------------:|-------------------------:|
| a7al2q_69d146749c30da3c | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.0604446 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      2 | ONDOUSDT  |           1.36634  |                0.049253  |
| a7al2q_69d146749c30da3c | known_may2026_stress |      3 | NEARUSDT  |           1.35799  |                0.0489518 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      4 | SUIUSDT   |           1.12613  |                0.040594  |
| a7al2q_69d146749c30da3c | known_may2026_stress |      5 | WLDUSDT   |           1.09694  |                0.0395416 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      6 | FILUSDT   |           1.06279  |                0.0383106 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      7 | ARBUSDT   |           0.911072 |                0.0328416 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      8 | UNIUSDT   |           0.861938 |                0.0310705 |
| a7al2q_69d146749c30da3c | known_may2026_stress |      9 | DODOXUSDT |           0.834684 |                0.0300881 |
| a7al2q_69d146749c30da3c | known_may2026_stress |     10 | ILVUSDT   |           0.789077 |                0.028444  |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      1 | ZECUSDT   |           1.67315  |                0.0569326 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      2 | DASHUSDT  |           1.40491  |                0.0478051 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      3 | NEARUSDT  |           1.3722   |                0.0466923 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      4 | ONDOUSDT  |           1.2207   |                0.0415369 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      5 | SUIUSDT   |           1.12473  |                0.0382713 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      6 | WLDUSDT   |           1.09331  |                0.0372023 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      7 | FILUSDT   |           1.06108  |                0.0361058 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      8 | DODOXUSDT |           0.879648 |                0.029932  |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      9 | UNIUSDT   |           0.859722 |                0.029254  |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |     10 | ARBUSDT   |           0.77758  |                0.0264589 |
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
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      1 | ZECUSDT   |           1.67682  |                0.06049   |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      2 | NEARUSDT  |           1.37333  |                0.0495421 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      3 | ONDOUSDT  |           1.35421  |                0.048852  |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      4 | SUIUSDT   |           1.12613  |                0.0406245 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      5 | WLDUSDT   |           1.09694  |                0.0395712 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      6 | FILUSDT   |           1.06279  |                0.0383393 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      7 | ARBUSDT   |           0.915409 |                0.0330227 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      8 | UNIUSDT   |           0.861938 |                0.0310938 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      9 | DODOXUSDT |           0.813395 |                0.0293426 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |     10 | ILVUSDT   |           0.789077 |                0.0284654 |

## May Latent Concentration

| candidate_id            | split                |   rank | raw_latent_state_id   |   abs_contribution |   abs_contribution_share |
|:------------------------|:---------------------|-------:|:----------------------|-------------------:|-------------------------:|
| a7al2q_69d146749c30da3c | known_may2026_stress |      1 | __missing__           |            27.7414 |                        1 |
| a7al2q_3abec814a5c6d0df | known_may2026_stress |      1 | __missing__           |            29.3882 |                        1 |
| a7al2q_1378ff7d2322adee | known_may2026_stress |      1 | __missing__           |            27.7253 |                        1 |
| a7al2q_a4993fe3273bf0c8 | known_may2026_stress |      1 | __missing__           |            27.7206 |                        1 |
| a7al2q_0de0d41346741bd1 | known_may2026_stress |      1 | __missing__           |            27.7369 |                        1 |
| a7al2q_5da100b2822dc1a6 | known_may2026_stress |      1 | __missing__           |            27.6985 |                        1 |
| a7al2q_132c2a7c6c4a9142 | known_may2026_stress |      1 | __missing__           |            27.5858 |                        1 |
| a7al2q_f00f22bbcc48dc2c | known_may2026_stress |      1 | __missing__           |            27.6785 |                        1 |
| a7al2q_d6f7ebc0dbbdda7a | known_may2026_stress |      1 | __missing__           |            27.719  |                        1 |
| a7al2q_6671d1fac5e57efe | known_may2026_stress |      1 | __missing__           |            27.6003 |                        1 |
| a7al2q_33d51890b0068eb6 | known_may2026_stress |      1 | __missing__           |            27.6148 |                        1 |
| a7al2q_100786d679e5b988 | known_may2026_stress |      1 | __missing__           |            28.5899 |                        1 |
| a7al2q_2ec6136e6ff32eb3 | known_may2026_stress |      1 | __missing__           |            27.8988 |                        1 |
| a7al2q_ca72f5849cff347a | known_may2026_stress |      1 | __missing__           |            28.652  |                        1 |

## Action Matrix

| action                           | status                       | reason                                                                                                         |
|:---------------------------------|:-----------------------------|:---------------------------------------------------------------------------------------------------------------|
| company_full_a7al2q2r            | COMPLETED                    | company full run is the current input                                                                          |
| local_mutation_expansion         | NOT_AUTHORIZED               | all candidates sign-flip and become control-dominated in May stress                                            |
| a7al2u_objective_repair_contract | AUTHORIZED_FOR_CONTRACT_ONLY | future selector may penalize pre-May structures that resemble stress-control behavior without using May labels |
| alpha_proof_shadow_paper_live    | NOT_AUTHORIZED               | known stress failure and local diagnostic-only evidence                                                        |

## Boundary

```text
Authorized:
  A7AL-2U objective-repair contract drafting only
  company full A7AL-2Q/2R if company path is available only for local context

Not authorized:
  local mutation expansion
  large search
  alpha proof
  shadow / paper / live
```
