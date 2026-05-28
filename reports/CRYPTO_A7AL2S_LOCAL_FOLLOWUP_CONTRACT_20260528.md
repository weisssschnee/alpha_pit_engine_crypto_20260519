# CRYPTO A7AL-2S Local Follow-Up Contract

Generated: 2026-05-28T13:24:54Z

## Decision

```text
PASS_A7AL2S_LOCAL_FOLLOWUP_CONTRACT_READY
```

This is a contract only. It executes no search, no training, no replay, and no proof. It converts the A7AL-2R local forensic result into explicit next-step authorization.

## Manifest

```json
{
  "authorizes_a7al2t_may_stress_failure_attribution": true,
  "authorizes_alpha_proof": false,
  "authorizes_company_full_a7al2q2r": true,
  "authorizes_large_search": false,
  "authorizes_local_expansion_before_full_pool": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 4,
  "decision": "PASS_A7AL2S_LOCAL_FOLLOWUP_CONTRACT_READY",
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T13:24:54Z",
  "input_a7al2r_decision": "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT",
  "primary_clean_premay_count": 2,
  "required_next": "Run company full A7AL-2Q/2R when company data path is mounted, or run A7AL-2T May stress failure attribution; do not start large search.",
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false,
  "watchlist_control_close_count": 2
}
```

## Candidate Tiers

| candidate_id            | decision                   | reasons   | warnings      |   label_t1_positive_premay_splits |   label_t2_positive_premay_splits |   one_bar_lag_positive_premay_splits |   latent_positive_premay_splits |   net_10bps_positive_premay_splits |   control_ratio_premay_max |   top_symbol_abs_contribution_share |   top_month_abs_contribution_share |   top_latent_abs_contribution_share |   pre_may_control_ratio_max | pre_may_control_gates                  |   may_control_ratio_max | may_gate_max           |   premay_positive_split_count |   min_split_mean_spread |   max_split_mean_spread | a7al2s_tier                                    | allowed_as_seed_for_large_search   | allowed_as_seed_for_company_full_qr_comparison   | allowed_for_may_stress_failure_attribution   | allowed_for_local_expansion_before_full_pool   |
|:------------------------|:---------------------------|:----------|:--------------|----------------------------------:|----------------------------------:|-------------------------------------:|--------------------------------:|-----------------------------------:|---------------------------:|------------------------------------:|-----------------------------------:|------------------------------------:|----------------------------:|:---------------------------------------|------------------------:|:-----------------------|------------------------------:|------------------------:|------------------------:|:-----------------------------------------------|:-----------------------------------|:-------------------------------------------------|:---------------------------------------------|:-----------------------------------------------|
| a7al2q_1378ff7d2322adee | A7AL2R_LOCAL_FORENSIC_PASS |           |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.59779  |                           0.0445498 |                           0.289729 |                            0.20351  |                    0.871656 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE |                 1.84561 | HOLD_CONTROL_DOMINATED |                             4 |              0.00139064 |              0.00202419 | primary_clean_premay__may_control_dominated    | False                              | True                                             | True                                         | False                                          |
| a7al2q_f00f22bbcc48dc2c | A7AL2R_LOCAL_FORENSIC_PASS |           |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.737129 |                           0.0450271 |                           0.285236 |                            0.204626 |                    0.762502 | ELIGIBLE_DIAGNOSTIC                    |                 1.42987 | HOLD_CONTROL_DOMINATED |                             4 |              0.00124169 |              0.00196769 | primary_clean_premay__may_control_dominated    | False                              | True                                             | True                                         | False                                          |
| a7al2q_d6f7ebc0dbbdda7a | A7AL2R_LOCAL_FORENSIC_PASS |           | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.813863 |                           0.0450585 |                           0.286532 |                            0.204604 |                    0.829293 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE |                 1.28572 | HOLD_CONTROL_DOMINATED |                             4 |              0.0012727  |              0.00195989 | watchlist_control_close__may_control_dominated | False                              | True                                             | True                                         | False                                          |
| a7al2q_6671d1fac5e57efe | A7AL2R_LOCAL_FORENSIC_PASS |           | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.890176 |                           0.0449655 |                           0.278788 |                            0.206986 |                    0.979674 | ELIGIBLE_DIAGNOSTIC;WARN_CONTROL_CLOSE |                 1.13016 | HOLD_CONTROL_DOMINATED |                             4 |              0.00122872 |              0.00187861 | watchlist_control_close__may_control_dominated | False                              | True                                             | True                                         | False                                          |

## Action Authorization

| action                                | status                               | reason                                                                                                                              |
|:--------------------------------------|:-------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------|
| company_full_a7al2q2r                 | AUTHORIZED_IF_COMPANY_PATH_AVAILABLE | local pilot executed only 16 replay candidates; full 128 replay/deep pass should be checked off local memory path                   |
| a7al2t_may_stress_failure_attribution | AUTHORIZED                           | all four local forensic candidates are pre-May positive but May/control dominated; classify failure without using May for selection |
| local_narrow_mutation_expansion       | HOLD_UNTIL_FULL_QR_OR_A7AL2T         | avoid amplifying a four-candidate local pilot before full-pool confirmation                                                         |
| large_formula_search                  | NOT_AUTHORIZED                       | current evidence is local diagnostic only                                                                                           |
| alpha_proof_shadow_paper_live         | NOT_AUTHORIZED                       | May stress remains negative/control dominated and no append-only proof exists                                                       |

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
  company full A7AL-2Q/2R run when company path is available
  A7AL-2T May-stress failure attribution

Not authorized:
  local expansion before full-pool confirmation
  large formula search
  alpha proof
  shadow / paper / live
```
