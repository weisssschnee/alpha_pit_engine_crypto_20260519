# CRYPTO A7AL-2S Company Full Follow-Up Contract

Generated: 2026-05-28T14:40:43Z

## Decision

```text
PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY
```

This is a contract only. It executes no search, no training, no replay, and no proof. It converts the A7AL-2R forensic result into explicit next-step authorization.

## Manifest

```json
{
  "authorizes_a7al2t_may_stress_failure_attribution": true,
  "authorizes_alpha_proof": false,
  "authorizes_company_full_a7al2q2r": false,
  "authorizes_large_search": false,
  "authorizes_local_expansion_before_full_pool": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 14,
  "context": "company_full",
  "decision": "PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY",
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T14:40:43Z",
  "input_a7al2r_base_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\company_a7al2q2r_full_20260528\\runtime\\a7al2r_local_forensic",
  "input_a7al2r_decision": "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT",
  "primary_clean_premay_count": 5,
  "required_next": "Run A7AL-2T stress attribution on this company full pool; do not start expansion or large search.",
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false,
  "watchlist_control_close_count": 5
}
```

## Candidate Tiers

| candidate_id            | decision                      | reasons                    | warnings      |   label_t1_positive_premay_splits |   label_t2_positive_premay_splits |   one_bar_lag_positive_premay_splits |   latent_positive_premay_splits |   net_10bps_positive_premay_splits |   control_ratio_premay_max |   top_symbol_abs_contribution_share |   top_month_abs_contribution_share |   top_latent_abs_contribution_share |   pre_may_control_ratio_max | pre_may_control_gates                                         |   may_control_ratio_max | may_gate_max           |   premay_positive_split_count |   min_split_mean_spread |   max_split_mean_spread | a7al2s_tier                                            | allowed_as_seed_for_large_search   | allowed_as_seed_for_company_full_qr_comparison   | allowed_for_may_stress_failure_attribution   | allowed_for_local_expansion_before_full_pool   |
|:------------------------|:------------------------------|:---------------------------|:--------------|----------------------------------:|----------------------------------:|-------------------------------------:|--------------------------------:|-----------------------------------:|---------------------------:|------------------------------------:|-----------------------------------:|------------------------------------:|----------------------------:|:--------------------------------------------------------------|------------------------:|:-----------------------|------------------------------:|------------------------:|------------------------:|:-------------------------------------------------------|:-----------------------------------|:-------------------------------------------------|:---------------------------------------------|:-----------------------------------------------|
| a7al2q_69d146749c30da3c | A7AL2R_LOCAL_FORENSIC_PASS    |                            |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.638674 |                           0.0449619 |                           0.29699  |                            0.202941 |                    1.04903  | ELIGIBLE_DIAGNOSTIC;HOLD_CONTROL_DOMINATED                    |                 2.0475  | HOLD_CONTROL_DOMINATED |                             4 |              0.00135871 |              0.00208302 | primary_clean_premay__may_control_dominated            | False                              | False                                            | True                                         | False                                          |
| a7al2q_3abec814a5c6d0df | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile | control_close |                                 3 |                                 3 |                                    3 |                               2 |                                  3 |                   0.820173 |                           0.0430688 |                           0.31393  |                            0.201934 |                    0.838551 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.5195  | HOLD_CONTROL_DOMINATED |                             4 |              0.00156461 |              0.00242373 | hold_timevarying_latent_fragile__may_control_dominated | False                              | False                                            | True                                         | False                                          |
| a7al2q_1378ff7d2322adee | A7AL2R_LOCAL_FORENSIC_PASS    |                            |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.59779  |                           0.0445498 |                           0.289729 |                            0.20351  |                    0.871656 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.18447 | HOLD_CONTROL_DOMINATED |                             4 |              0.00139064 |              0.00202419 | primary_clean_premay__may_control_dominated            | False                              | False                                            | True                                         | False                                          |
| a7al2q_a4993fe3273bf0c8 | A7AL2R_LOCAL_FORENSIC_PASS    |                            | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.955399 |                           0.0445406 |                           0.296253 |                            0.20292  |                    1.0469   | ELIGIBLE_DIAGNOSTIC;HOLD_CONTROL_DOMINATED;WARN_CONTROL_CLOSE |                 1.63444 | HOLD_CONTROL_DOMINATED |                             4 |              0.0013505  |              0.00206872 | watchlist_control_close__may_control_dominated         | False                              | False                                            | True                                         | False                                          |
| a7al2q_0de0d41346741bd1 | A7AL2R_LOCAL_FORENSIC_PASS    |                            |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.643831 |                           0.0445558 |                           0.289273 |                            0.203613 |                    0.864621 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.21572 | HOLD_CONTROL_DOMINATED |                             4 |              0.00138455 |              0.0019945  | primary_clean_premay__may_control_dominated            | False                              | False                                            | True                                         | False                                          |
| a7al2q_5da100b2822dc1a6 | A7AL2R_LOCAL_FORENSIC_PASS    |                            |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.782136 |                           0.04449   |                           0.286533 |                            0.202893 |                    0.835726 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 2.04793 | HOLD_CONTROL_DOMINATED |                             4 |              0.00139898 |              0.00197616 | primary_clean_premay__may_control_dominated            | False                              | False                                            | True                                         | False                                          |
| a7al2q_132c2a7c6c4a9142 | A7AL2R_LOCAL_FORENSIC_PASS    |                            | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.814765 |                           0.0447031 |                           0.281888 |                            0.207234 |                    0.981212 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.21923 | HOLD_CONTROL_DOMINATED |                             4 |              0.00119135 |              0.00192054 | watchlist_control_close__may_control_dominated         | False                              | False                                            | True                                         | False                                          |
| a7al2q_f00f22bbcc48dc2c | A7AL2R_LOCAL_FORENSIC_PASS    |                            |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.737129 |                           0.0450271 |                           0.285236 |                            0.204626 |                    0.762502 | ELIGIBLE_DIAGNOSTIC                                           |                 2.77616 | HOLD_CONTROL_DOMINATED |                             4 |              0.00124169 |              0.00196769 | primary_clean_premay__may_control_dominated            | False                              | False                                            | True                                         | False                                          |
| a7al2q_d6f7ebc0dbbdda7a | A7AL2R_LOCAL_FORENSIC_PASS    |                            | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.813863 |                           0.0450585 |                           0.286532 |                            0.204604 |                    0.829293 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.96561 | HOLD_CONTROL_DOMINATED |                             4 |              0.0012727  |              0.00195989 | watchlist_control_close__may_control_dominated         | False                              | False                                            | True                                         | False                                          |
| a7al2q_6671d1fac5e57efe | A7AL2R_LOCAL_FORENSIC_PASS    |                            | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.890176 |                           0.0449655 |                           0.278788 |                            0.206986 |                    0.979674 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.13016 | HOLD_CONTROL_DOMINATED |                             4 |              0.00122872 |              0.00187861 | watchlist_control_close__may_control_dominated         | False                              | False                                            | True                                         | False                                          |
| a7al2q_33d51890b0068eb6 | HOLD_A7AL2R_CONTROL_DOMINATED | control_dominated          |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   1.63754  |                           0.0447281 |                           0.279237 |                            0.207028 |                    1.63754  | ELIGIBLE_DIAGNOSTIC;HOLD_CONTROL_DOMINATED;WARN_CONTROL_CLOSE |                 1.41203 | HOLD_CONTROL_DOMINATED |                             4 |              0.00118794 |              0.00185967 | hold_control_dominated__may_control_dominated          | False                              | False                                            | True                                         | False                                          |
| a7al2q_100786d679e5b988 | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile |               |                                 3 |                                 3 |                                    3 |                               2 |                                  3 |                   0.783719 |                           0.0435864 |                           0.334784 |                            0.205836 |                    0.841175 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 2.19575 | HOLD_CONTROL_DOMINATED |                             4 |              0.00136083 |              0.00250945 | hold_timevarying_latent_fragile__may_control_dominated | False                              | False                                            | True                                         | False                                          |
| a7al2q_2ec6136e6ff32eb3 | A7AL2R_LOCAL_FORENSIC_PASS    |                            | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.928927 |                           0.0446374 |                           0.283611 |                            0.207139 |                    0.940786 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE                        |                 1.17563 | HOLD_CONTROL_DOMINATED |                             4 |              0.00119992 |              0.00179759 | watchlist_control_close__may_control_dominated         | False                              | False                                            | True                                         | False                                          |
| a7al2q_ca72f5849cff347a | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile | control_close |                                 3 |                                 3 |                                    3 |                               2 |                                  3 |                   0.918655 |                           0.0431549 |                           0.338262 |                            0.206045 |                    1.00022  | ELIGIBLE_DIAGNOSTIC;HOLD_CONTROL_DOMINATED;WARN_CONTROL_CLOSE |                 1.72326 | HOLD_CONTROL_DOMINATED |                             4 |              0.0013379  |              0.00252834 | hold_timevarying_latent_fragile__may_control_dominated | False                              | False                                            | True                                         | False                                          |

## Action Authorization

| action                                       | status                       | reason                                                                                                      |
|:---------------------------------------------|:-----------------------------|:------------------------------------------------------------------------------------------------------------|
| a7al2t_company_may_stress_attribution        | AUTHORIZED                   | company full run produced a 14-candidate forensic pool; classify stress behavior before any expansion       |
| a7al2u_objective_or_selector_repair_contract | AUTHORIZED_FOR_CONTRACT_ONLY | control dominance remains high in fast replay and must feed selector/objective repair, not direct expansion |
| local_narrow_mutation_expansion              | NOT_AUTHORIZED               | company full results supersede local pilot and still require stress attribution                             |
| large_formula_search                         | NOT_AUTHORIZED               | company full run is diagnostic and not a proof object                                                       |
| alpha_proof_shadow_paper_live                | NOT_AUTHORIZED               | no append-only proof and stress attribution remains pending                                                 |

## Follow-Up Gates

| gate                   | requirement                                                               |
|:-----------------------|:--------------------------------------------------------------------------|
| full_pool_required     | A7AL-2Q/2R full 128 replay on company resources before expansion          |
| may_stress_only        | May can be failure attribution/veto only, never selector/ranking/mutation |
| control_close_handling | control_close candidates stay watchlist unless full-pool controls improve |
| primary_seed_handling  | no-warning candidates are diagnostic primary clues, not proof objects     |
| negative_controls      | wrong-lag, shuffle, same-family controls remain attached                  |
| artifact_chain         | use committed A7AL-2Q and A7AL-2R artifacts only                          |

## Boundary

```text
Authorized:
  A7AL-2T May-stress failure attribution
  company full A7AL-2Q/2R run when company path is available only for local context

Not authorized:
  local expansion before full-pool confirmation
  large formula search
  alpha proof
  shadow / paper / live
```
