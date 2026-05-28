# CRYPTO A7AL-2U Objective / Selector Repair Contract

Generated: 2026-05-28T14:42:42Z

## Decision

```text
PASS_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_READY
```

This is a contract only. It executes no formula search, no training, no replay, and no proof.

## Manifest

```json
{
  "authorizes_a7al2v_selector_dryrun": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "company_full_may_control_dominated_rows": 28,
  "company_full_sign_flip_rows": 28,
  "company_full_unique_candidates": 14,
  "decision": "PASS_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_READY",
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T14:42:42Z",
  "input_a7al2q_decision": "PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD",
  "input_a7al2r_decision": "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT",
  "input_a7al2s_decision": "PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY",
  "input_a7al2t_decision": "HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION",
  "required_next": "Implement A7AL-2V replay-aware selector dry-run using non-May selector features; do not rerun same Q objective.",
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selector": false,
  "uses_may_for_veto_or_attribution": true
}
```

## Failure Mode Summary

| metric                       |   value | interpretation                                                   |
|:-----------------------------|--------:|:-----------------------------------------------------------------|
| q_generated_total            |    4000 | local OI x price search budget executed on company machine       |
| q_executed_fast_replay       |     128 | fast replay candidates scored before deep forensic               |
| q_diagnostic_candidates      |      14 | pre-May diagnostic candidates before deep forensic               |
| q_control_dominated          |     114 | selector allowed many variants that controls could explain       |
| r_forensic_pass              |      10 | pre-May deep forensic pass count                                 |
| t_unique_candidates          |      14 | company full pool sent to May stress attribution                 |
| t_sign_flip_rows             |      28 | all candidate-entry rows flip sign in May                        |
| t_may_control_dominated_rows |      28 | all candidate-entry rows are weaker than matched controls in May |

## Pre-May Robust Candidate Summary

| candidate_id            |   premay_min_newey_west_tstat |   premay_min_block_bootstrap_tstat |   premay_min_mean_spread | decision                      | reasons                    | warnings      |   control_ratio_premay_max |   latent_positive_premay_splits |
|:------------------------|------------------------------:|-----------------------------------:|-------------------------:|:------------------------------|:---------------------------|:--------------|---------------------------:|--------------------------------:|
| a7al2q_0de0d41346741bd1 |                       1.98762 |                            2.02942 |               0.00138455 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | nan           |                   0.643831 |                               3 |
| a7al2q_100786d679e5b988 |                       1.75782 |                            1.77476 |               0.00136083 | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile | nan           |                   0.783719 |                               2 |
| a7al2q_132c2a7c6c4a9142 |                       1.79899 |                            1.84519 |               0.00119135 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | control_close |                   0.814765 |                               3 |
| a7al2q_1378ff7d2322adee |                       1.99924 |                            2.04361 |               0.00139064 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | nan           |                   0.59779  |                               3 |
| a7al2q_2ec6136e6ff32eb3 |                       1.73089 |                            1.77357 |               0.00119992 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | control_close |                   0.928927 |                               3 |
| a7al2q_33d51890b0068eb6 |                       1.79155 |                            1.8366  |               0.00118794 | HOLD_A7AL2R_CONTROL_DOMINATED | control_dominated          | nan           |                   1.63754  |                               3 |
| a7al2q_3abec814a5c6d0df |                       2.04433 |                            1.98556 |               0.00156461 | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile | control_close |                   0.820173 |                               2 |
| a7al2q_5da100b2822dc1a6 |                       2.03145 |                            2.07132 |               0.00139898 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | nan           |                   0.782136 |                               3 |
| a7al2q_6671d1fac5e57efe |                       1.84489 |                            1.88064 |               0.00122872 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | control_close |                   0.890176 |                               3 |
| a7al2q_69d146749c30da3c |                       2.06648 |                            2.07992 |               0.0014483  | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | nan           |                   0.638674 |                               3 |
| a7al2q_a4993fe3273bf0c8 |                       2.13412 |                            2.17026 |               0.00148381 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | control_close |                   0.955399 |                               3 |
| a7al2q_ca72f5849cff347a |                       1.7621  |                            1.78665 |               0.0013379  | HOLD_A7AL2R_LATENT_FRAGILE    | timevarying_latent_fragile | control_close |                   0.918655 |                               2 |
| a7al2q_d6f7ebc0dbbdda7a |                       1.82082 |                            1.8551  |               0.0012727  | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | control_close |                   0.813863 |                               3 |
| a7al2q_f00f22bbcc48dc2c |                       1.78649 |                            1.81729 |               0.00124169 | A7AL2R_LOCAL_FORENSIC_PASS    | nan                        | nan           |                   0.737129 |                               3 |

## Selector Feature Contract

| feature_group      | required_features                                                                                                 | may_allowed          | purpose                                                       |
|:-------------------|:------------------------------------------------------------------------------------------------------------------|:---------------------|:--------------------------------------------------------------|
| formula_lineage    | expression_key;skeleton_key;production_key;operator_signature;field_family_set;window_signature;parent_seed_id    | False                | dedup, diversity, and narrow-family cap                       |
| replay_alignment   | label_t1_spread_by_split;label_t2_spread_by_split;entry_label_agreement;min_split_spread;split_dispersion         | False                | avoid one-entry alignment artifacts                           |
| control_dominance  | max_control_ratio_by_premay_split;control_margin_by_mode;control_close_count;control_hold_count                   | False                | reduce 114/128 control-dominated replay waste                 |
| latency_cost       | one_bar_lag_spread_by_split;net_2bps;net_5bps;net_10bps;turnover_proxy                                            | False                | penalize timing and cost fragility without blanket +2h stress |
| neutralization     | timevarying_latent_spread;latent_positive_split_count;liquidity_tier_neutral_spread;age_or_listing_state_coverage | False                | avoid latent-state-only artifacts                             |
| robust_statistics  | newey_west_tstat_lag24;block_bootstrap_tstat_block24;nonoverlap_offset_min_tstat                                  | False                | replace naive overlapping hourly t-stat in selector           |
| concentration      | top_symbol_share;top_month_share;top_latent_share;top_skeleton_share;top_field_family_share                       | False                | cap single symbol/month/state/skeleton dominance              |
| stress_attribution | may_spread;may_control_ratio;may_sign_flip;may_failure_label                                                      | veto_and_report_only | never selector score; only post-selection attribution/veto    |

## Selector Gate Contract

| gate                               | rule                                                                                                            | applies_to            | uses_may   |
|:-----------------------------------|:----------------------------------------------------------------------------------------------------------------|:----------------------|:-----------|
| premay_control_dominance_hard_gate | reject if any pre-May split control_ratio >= 1.00                                                               | selector and forensic | False      |
| premay_control_close_penalty       | penalize 0.80 <= control_ratio < 1.00 instead of treating as clean seed                                         | selector score        | False      |
| entry_alignment_gate               | require label_t1 and label_t2 positive in validation/test/recent; require small dispersion between entry labels | selector score        | False      |
| latent_survival_gate               | require time-varying latent-neutral positive in all pre-May evaluation splits                                   | selector score        | False      |
| robust_tstat_gate                  | rank by min(Newey-West, block-bootstrap, non-overlap offset) not naive hourly t-stat                            | selector score        | False      |
| family_diversity_gate              | top skeleton <= 15%, top production key <= 20%, top field-family <= 25% in selected replay pool                 | selector pool         | False      |
| direct_oi_price_expansion_hold     | do not expand direct OI x price seeds until a repaired selector passes dry-run and control audit                | authorization         | veto_only  |

## Authorization Matrix

| action                              | status         | reason                                                                          |
|:------------------------------------|:---------------|:--------------------------------------------------------------------------------|
| a7al2v_replay_aware_selector_dryrun | AUTHORIZED     | repair selector features and dry-run on existing Q/R/T artifacts without search |
| a7al2q_rerun_same_objective         | NOT_AUTHORIZED | same objective produced all-candidate May sign flip/control domination          |
| direct_oi_price_local_expansion     | NOT_AUTHORIZED | A7AL-2T company full stress attribution failed for all candidates               |
| large_formula_search                | NOT_AUTHORIZED | selector/objective failure is unresolved                                        |
| alpha_proof_shadow_paper_live       | NOT_AUTHORIZED | diagnostic only; no append-only proof                                           |

## Boundary

```text
Authorized:
  A7AL-2V replay-aware selector dry-run on existing artifacts

Not authorized:
  same-objective A7AL-2Q rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live

May:
  allowed only as post-selection veto/attribution
  forbidden for selector score, ranking, mutation, generation, and training target
```
