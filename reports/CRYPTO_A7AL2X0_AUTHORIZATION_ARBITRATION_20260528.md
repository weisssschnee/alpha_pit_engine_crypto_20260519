# CRYPTO A7AL-2X0 Authorization Arbitration

Generated: 2026-05-28T15:54:47Z

## Decision

```text
PASS_A7AL2X0_AUTHORIZATION_ARBITRATION_COMPLETE
```

This stage resolves the authorization conflict between A7AL-2P2 and later A7AL-2Q/2R/2S/2T/2U/2V/AR8/2W evidence. It executes no search, no replay, no training, and no proof.

## Git Source-of-Truth Status

```text
local_head_before_commit: 9394520
origin_main_before_commit: 40620fe
origin_main...HEAD before commit: 0	11
```

Interpretation:

```text
Local main contains later evidence that origin/main does not yet show.
After this arbitration is committed, pushing local main is required for GitHub main to become the source of truth.
```

## Final Authorization

```json
{
  "a7al2p2_final_status": "SUPERSEDED_DIAGNOSTIC_CONTRACT",
  "a7al2q_local_execution": "NOT_AUTHORIZED",
  "a7al2x1_dry_rerank": "AUTHORIZED_AFTER_A7AL2X_CONTRACT",
  "a7al2x_objective_family_reset_contract": "AUTHORIZED_CONTRACT_ONLY",
  "alpha_proof": "NOT_AUTHORIZED",
  "decision": "PASS_A7AL2X0_AUTHORIZATION_ARBITRATION_COMPLETE",
  "direct_oi_price_expansion": "NOT_AUTHORIZED",
  "large_formula_search": "NOT_AUTHORIZED",
  "local_head_before_a7al2x0_commit": "9394520",
  "may_policy": {
    "may_allowed_for_generation": false,
    "may_allowed_for_mutation": false,
    "may_allowed_for_ranking": false,
    "may_allowed_for_selector": false,
    "may_allowed_for_veto_or_attribution": true,
    "may_allowed_for_weight_update": false
  },
  "origin_main_ahead_behind_before_a7al2x0_commit": "0\t11",
  "origin_main_before_a7al2x0_commit": "40620fe",
  "same_objective_rerun": "NOT_AUTHORIZED",
  "shadow_paper_live": "NOT_AUTHORIZED",
  "source_of_truth": "local_main_after_commit_pending_remote_push"
}
```

## Artifact Inventory

| record_id   | nominal_commit   | stage                              | manifest_exists   | report_exists   | decision                                                        | generated_at         | authorizes_execution   | authorizes_contract   | selected_count   | selected_stress_clean_count   | stress_clean_count   | blockers                                                                                     |   precedence |
|:------------|:-----------------|:-----------------------------------|:------------------|:----------------|:----------------------------------------------------------------|:---------------------|:-----------------------|:----------------------|:-----------------|:------------------------------|:---------------------|:---------------------------------------------------------------------------------------------|-------------:|
| A7AL-2P2    | 40620fe          | local_oi_price_contract            | True              | True            | PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q    | 2026-05-28T07:27:54Z | True                   | False                 |                  |                               |                      |                                                                                              |           10 |
| A7AL-2Q     | f2f8c3b          | company_local_oi_price_execution   | True              | True            | PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD      | 2026-05-28T14:17:23Z | False                  | False                 |                  |                               |                      |                                                                                              |           20 |
| A7AL-2R     | f2f8c3b          | company_local_forensic             | True              | True            | PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT | 2026-05-28T14:27:47Z | False                  | False                 |                  |                               |                      |                                                                                              |           30 |
| A7AL-2S     | 2d1efd3          | company_full_followup_contract     | True              | True            | PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY                | 2026-05-28T14:40:43Z | False                  | False                 |                  |                               |                      |                                                                                              |           40 |
| A7AL-2T     | c8cb2ae          | company_may_stress_attribution     | True              | True            | HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION           | 2026-05-28T14:40:46Z | False                  | False                 |                  |                               |                      | all_company_full_candidates_may_sign_flip\|all_company_full_candidates_may_control_dominated |           50 |
| A7AL-2U     | 7e34b48          | objective_selector_repair_contract | True              | True            | PASS_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_READY            | 2026-05-28T14:42:42Z | False                  | True                  |                  |                               |                      |                                                                                              |           60 |
| A7AR-7      | 52b6e46          | shared_candidate_pool              | True              | True            | PASS_A7AR7_SHARED_CANDIDATE_POOL_READY_FOR_A7AL2V               | 2026-05-28T14:58:46Z | False                  | True                  |                  |                               |                      |                                                                                              |           70 |
| A7AL-2V     | 52b6e46          | replay_aware_selector_dryrun       | True              | True            | HOLD_A7AL2V_SELECTED_POOL_STRESS_VETO_NO_EXPANSION              | 2026-05-28T14:59:47Z | False                  | False                 | 4                | 0                             |                      | selected_pool_may_stress_veto                                                                |           80 |
| A7AR-8      | 55f40b9          | signal_vector_cluster_registry     | True              | True            | HOLD_A7AR8_SELECTED_QUEUE_STRESS_VETO_NO_EXPANSION              | 2026-05-28T15:10:04Z | False                  | False                 | 4                | 0                             |                      | selected_queue_pairwise_corr_high\|selected_queue_may_stress_veto                            |           90 |
| A7AL-2W     | 9394520          | signal_vector_selector_repair      | True              | True            | HOLD_A7AL2W_SELECTOR_DIVERSITY_REPAIRED_BUT_STRESS_VETO         | 2026-05-28T15:23:36Z | False                  | True                  | 2                | 0                             |                      | selected_queue_may_stress_veto                                                               |          100 |

## Decision Precedence

| record_id   | decision                                                     | superseded_by                              | final_status                   | reason                                                                                                                                                      |
|:------------|:-------------------------------------------------------------|:-------------------------------------------|:-------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A7AL-2P2    | PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q | A7AL-2T\|A7AL-2U\|A7AL-2V\|A7AR-8\|A7AL-2W | SUPERSEDED_DIAGNOSTIC_CONTRACT | Later company execution, stress attribution, replay-aware selector, signal-vector registry, and selector repair show zero stress-clean selected candidates. |
| A7AL-2Q     | previously_authorized_by_A7AL-2P2                            | A7AL-2X0                                   | NOT_AUTHORIZED                 | Same objective direct OI x price path is stress-vetoed after later evidence.                                                                                |
| A7AL-2X     | objective_family_reset_contract                              |                                            | AUTHORIZED_CONTRACT_ONLY       | Move from direct OI x price weak prior to broader OI/positioning interaction contract; no search execution.                                                 |

## Superseded Records

| superseded_record   | superseded_authorization          | new_status               | superseding_record   | evidence                                                                                                                   |
|:--------------------|:----------------------------------|:-------------------------|:---------------------|:---------------------------------------------------------------------------------------------------------------------------|
| A7AL-2P2            | authorizes_a7al2q_local_execution | suspended_not_authorized | A7AL-2X0             | A7AL-2V selected_stress_clean=0; A7AR-8 selected_queue stress veto; A7AL-2W repaired diversity but selected_stress_clean=0 |

## Required Next

```json
{
  "a7al2x_scope": [
    "direct OI x price becomes stress-vetoed weak prior",
    "allow OI/positioning interaction families only",
    "require shared candidate pool as source of truth",
    "require signal-vector cluster cap",
    "May remains post-selection veto/attribution only"
  ],
  "must_not_do": [
    "execute A7AL-2Q under superseded P2 authorization",
    "rerun same direct OI x price objective",
    "start large formula search",
    "authorize alpha proof/shadow/paper/live"
  ],
  "next_stage": "A7AL-2X objective family reset contract"
}
```

## Boundary

```text
Superseded:
  A7AL-2P2 authorization to execute A7AL-2Q local direct OI x price search

Authorized:
  A7AL-2X objective family reset contract only
  A7AL-2X1 dry rerank only after A7AL-2X contract passes

Not authorized:
  A7AL-2Q execution under P2
  same-objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
