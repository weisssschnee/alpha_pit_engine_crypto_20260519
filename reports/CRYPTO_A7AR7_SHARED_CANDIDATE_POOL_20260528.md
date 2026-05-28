# CRYPTO A7AR-7 Shared Candidate Pool

Generated: 2026-05-28T14:58:46Z

## Decision

```text
PASS_A7AR7_SHARED_CANDIDATE_POOL_READY_FOR_A7AL2V
```

This stage builds a durable candidate ledger from existing A7AL-2Q/2R/2S/2T/2U artifacts. It executes no search, no replay, no training, and no proof.

## Manifest

```json
{
  "authorizes_a7al2v_selector_dryrun": true,
  "authorizes_alpha_proof": false,
  "authorizes_direct_expansion": false,
  "authorizes_large_search": false,
  "authorizes_same_objective_rerun": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 4000,
  "decision": "PASS_A7AR7_SHARED_CANDIDATE_POOL_READY_FOR_A7AL2V",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "fast_replay_count": 128,
  "forensic_count": 14,
  "generated_at": "2026-05-28T14:58:46Z",
  "generated_count": 4000,
  "may_retained_for_veto_or_attribution": true,
  "may_stress_failed_count": 14,
  "may_used_for_pool_construction": false,
  "premay_control_dominated_count": 115,
  "stress_attributed_count": 14
}
```

## Stage Summary

| shared_pool_stage   |   candidate_count |
|:--------------------|------------------:|
| fast_replay_scored  |               114 |
| generated_only      |              3872 |
| stress_attributed   |                14 |

## Decision Summary

| q_decision                                 | r_decision                    | s_a7al2s_tier                                          |   candidate_count |
|:-------------------------------------------|:------------------------------|:-------------------------------------------------------|------------------:|
| nan                                        | nan                           | nan                                                    |              3872 |
| HOLD_A7AL2Q_CONTROL_DOMINATED              | nan                           | nan                                                    |               114 |
| A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS    | watchlist_control_close__may_control_dominated         |                 5 |
| A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | A7AL2R_LOCAL_FORENSIC_PASS    | primary_clean_premay__may_control_dominated            |                 5 |
| A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | HOLD_A7AL2R_LATENT_FRAGILE    | hold_timevarying_latent_fragile__may_control_dominated |                 3 |
| A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE | HOLD_A7AL2R_CONTROL_DOMINATED | hold_control_dominated__may_control_dominated          |                 1 |

## Provenance Audit

| check                                          | pass   | detail                                                          |
|:-----------------------------------------------|:-------|:----------------------------------------------------------------|
| q_manifest_present                             | True   | PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD      |
| r_manifest_present                             | True   | PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT |
| s_manifest_present                             | True   | PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY                |
| t_manifest_present                             | True   | HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION           |
| u_manifest_present                             | True   | PASS_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_READY            |
| candidate_id_unique                            | True   | 0                                                               |
| all_fast_replay_candidates_in_generated_pool   | True   | 128                                                             |
| all_forensic_candidates_in_fast_replay_pool    | True   | 14                                                              |
| all_may_attributed_candidates_in_forensic_pool | True   | 14                                                              |

## Authorization

| action                              | status         | reason                                                           |
|:------------------------------------|:---------------|:-----------------------------------------------------------------|
| a7al2v_replay_aware_selector_dryrun | AUTHORIZED     | shared pool now available; no search/replay required             |
| same_objective_rerun                | NOT_AUTHORIZED | A7AL-2T stress attribution failed all company-full candidates    |
| direct_oi_price_expansion           | NOT_AUTHORIZED | A7AL-2U holds direct expansion until selector repair             |
| large_formula_search                | NOT_AUTHORIZED | candidate pool governance and replay-aware selector not complete |
| alpha_proof_shadow_paper_live       | NOT_AUTHORIZED | no stress-clean candidate pool                                   |

## Boundary

```text
Authorized:
  A7AL-2V replay-aware selector dry-run on the shared pool

Not authorized:
  same-objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
