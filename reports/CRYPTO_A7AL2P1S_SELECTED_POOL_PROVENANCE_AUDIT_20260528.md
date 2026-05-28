# CRYPTO A7AL-2P1S Selected Pool Provenance Audit

Generated: 2026-05-28T07:25:16Z

## Decision

```text
PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN
```

This audit checks whether the two A7AL-2P1R selected candidates are traceable to the repaired J5/canonical A7AL-2K/L/P0R chain. It does not run training, search, or replay.

## Summary

```json
{
  "authorizes_a7al2p2": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 2,
  "current_l_clue_count": 2,
  "decision": "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN",
  "generated_at": "2026-05-28T07:25:16Z",
  "j5_repair_commit": "eb62bda",
  "j5_repair_commit_time": "2026-05-28T00:00:51+08:00",
  "p0r_canonical_alias_code_fail": false,
  "p0r_repaired_l_clue_count": 3,
  "p0r_stale_alias_artifact_count": 0,
  "p1_candidate_count": 2,
  "p1_generated_after_j5_repair": true,
  "p1_p1r_recomputed_metrics_present": true,
  "p1r_generated_after_j5_repair": true,
  "required_next": "Draft A7AL-2P2 as a local OI-price seed search contract only; do not authorize execution, alpha proof, or shadow/paper/live.",
  "selected_candidates_have_no_blocked_overlay_alias": true,
  "target_candidates": [
    "a7al2k_046e806368e99c76",
    "a7al2k_0a247ec03472983b"
  ]
}
```

## Candidate Provenance

| candidate_id            | expression                                                                              | fields                                | field_families       | skeleton_key              | production_key                                                                   | expression_key        | p1_selector_decision                 | p1r_decision                                 | p1_fields_column_available   | in_current_a7al2k_generated   | in_current_a7al2k_selected   | in_current_a7al2l_decisions   | in_current_a7al2l_clue_pool   | in_p0r_a7ar5_selector_snapshot   | blocked_overlay_aliases   |   blocked_overlay_alias_count | expression_match_current_k   | fields_match_current_k   | skeleton_match_current_k   | production_key_match_current_k   | current_k_generated_at   | current_l_generated_at   | p0r_repaired_k_generated_at   | p0r_repaired_l_generated_at   | current_l_target_replay_mode   | current_l_target_ids                             | leaked_from_old_a7al2l_10_clue_pool   |   p1_control_rows_recomputed |   p1_timevarying_latent_rows_recomputed |   p1r_variant_split_rows_recomputed |
|:------------------------|:----------------------------------------------------------------------------------------|:--------------------------------------|:---------------------|:--------------------------|:---------------------------------------------------------------------------------|:----------------------|:-------------------------------------|:---------------------------------------------|:-----------------------------|:------------------------------|:-----------------------------|:------------------------------|:------------------------------|:---------------------------------|:--------------------------|------------------------------:|:-----------------------------|:-------------------------|:---------------------------|:---------------------------------|:-------------------------|:-------------------------|:------------------------------|:------------------------------|:-------------------------------|:-------------------------------------------------|:--------------------------------------|-----------------------------:|----------------------------------------:|------------------------------------:|
| a7al2k_046e806368e99c76 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | skeleton-746e1c41665c2005 | a7al2k_derived_generator::derived_oi_price_state::open_interest\|price::12\|48   | expr-d6f7ebc0dbbdda7a | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | False                        | True                          | True                         | True                          | True                          | False                            |                           |                             0 | True                         | True                     | True                       | True                             | 2026-05-28T01:45:32Z     | 2026-05-28T07:12:23Z     | 2026-05-27T16:45:04Z          | 2026-05-27T17:35:24Z          | True                           | a7al2k_046e806368e99c76\|a7al2k_0a247ec03472983b | False                                 |                            3 |                                       5 |                                  50 |
| a7al2k_0a247ec03472983b | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | skeleton-746e1c41665c2005 | a7al2k_derived_generator::derived_oi_price_state::open_interest\|price::168\|336 | expr-6671d1fac5e57efe | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | False                        | True                          | True                         | True                          | True                          | False                            |                           |                             0 | True                         | True                     | True                       | True                             | 2026-05-28T01:45:32Z     | 2026-05-28T07:12:23Z     | 2026-05-27T16:45:04Z          | 2026-05-27T17:35:24Z          | True                           | a7al2k_046e806368e99c76\|a7al2k_0a247ec03472983b | False                                 |                            3 |                                       5 |                                  50 |

## Repaired Chain Membership

| candidate_id            | required_in_repaired_a7al2k_generated_pool   | required_in_repaired_a7al2l_clue_pool   | repaired_candidate_level_k_artifact_available   | repaired_candidate_level_l_artifact_available   | verified_in_repaired_a7al2k_generated_pool   | verified_in_repaired_a7al2l_clue_pool   | verified_in_repaired_p0r_a7ar5_snapshot   | current_k_artifact_is_older_than_p0r_repaired_k   | current_l_artifact_is_older_than_p0r_repaired_l   | current_l_is_old_10_clue_pool   | current_l_target_replay_mode   | current_l_target_ids                             |   p0r_repaired_l_clue_count |   current_l_clue_count |   p1_candidate_pool_count | membership_status                  | reason                                                                                       |
|:------------------------|:---------------------------------------------|:----------------------------------------|:------------------------------------------------|:------------------------------------------------|:---------------------------------------------|:----------------------------------------|:------------------------------------------|:--------------------------------------------------|:--------------------------------------------------|:--------------------------------|:-------------------------------|:-------------------------------------------------|----------------------------:|-----------------------:|--------------------------:|:-----------------------------------|:---------------------------------------------------------------------------------------------|
| a7al2k_046e806368e99c76 | True                                         | True                                    | True                                            | True                                            | True                                         | True                                    | False                                     | False                                             | False                                             | False                           | True                           | a7al2k_046e806368e99c76\|a7al2k_0a247ec03472983b |                           3 |                      2 |                         2 | VERIFIED_IN_CURRENT_REPAIRED_CHAIN | candidate exists in current post-repair K generated pool and current post-repair L clue pool |
| a7al2k_0a247ec03472983b | True                                         | True                                    | True                                            | True                                            | True                                         | True                                    | False                                     | False                                             | False                                             | False                           | True                           | a7al2k_046e806368e99c76\|a7al2k_0a247ec03472983b |                           3 |                      2 |                         2 | VERIFIED_IN_CURRENT_REPAIRED_CHAIN | candidate exists in current post-repair K generated pool and current post-repair L clue pool |

## Stale Artifact Audit

| check                                                         | status   | detail                                                                                        |
|:--------------------------------------------------------------|:---------|:----------------------------------------------------------------------------------------------|
| j5_repair_commit_time_available                               | PASS     | eb62bda commit_time=2026-05-28T00:00:51+08:00                                                 |
| p1_generated_after_j5_repair                                  | PASS     | p1_generated_at=2026-05-28T07:19:02Z; j5_repair_commit_time=2026-05-28T00:00:51+08:00         |
| p1r_generated_after_j5_repair                                 | PASS     | p1r_generated_at=2026-05-28T07:23:21Z; j5_repair_commit_time=2026-05-28T00:00:51+08:00        |
| current_k_artifact_after_repaired_k                           | PASS     | current_k_generated_at=2026-05-28T01:45:32Z; p0r_repaired_k_generated_at=2026-05-27T16:45:04Z |
| current_l_artifact_after_repaired_l                           | PASS     | current_l_generated_at=2026-05-28T07:12:23Z; p0r_repaired_l_generated_at=2026-05-27T17:35:24Z |
| p1_pool_matches_repaired_l_clue_count                         | PASS     | p1_candidate_count=2; repaired_l_clue_count=3; current_l_clue_count=2                         |
| current_l_target_replay_ids_match_selected_candidates         | PASS     | target_replay_mode=True; target_ids=a7al2k_046e806368e99c76\|a7al2k_0a247ec03472983b          |
| p0r_canonical_alias_code_pass                                 | PASS     | p0r_canonical_alias_code_fail=False; p0_alias_fail_count=0                                    |
| p0r_stale_alias_count_zero                                    | PASS     | p0r_stale_alias_artifact_count=0; current_p0_stale_alias_rows=164                             |
| selected_candidates_have_no_blocked_alias                     | PASS     | blocked_alias_count=0                                                                         |
| selected_candidates_recomputed_in_p1_p1r                      | PASS     | P1 control/latent and P1R split variants are present for both selected candidates.            |
| selected_candidates_verified_in_repaired_candidate_level_pool | PASS     | selected candidates are verified in current post-repair K/L candidate-level artifacts         |

## Interpretation

```text
P1/P1R themselves were generated after the J5 repair commit and recomputed selector/control/latent/cost metrics for the two candidates.

The selected candidates are evidenced from current post-repair A7AL-2K/L artifacts:
  current A7AL-2K generated_at = 2026-05-28T01:45:32Z
  current A7AL-2L generated_at = 2026-05-28T07:12:23Z
  current A7AL-2L target_replay_mode = True
  current A7AL-2L target_ids = a7al2k_046e806368e99c76|a7al2k_0a247ec03472983b

P0R's older repaired rerun manifest remains recorded for audit context:
  repaired A7AL-2K generated_at = 2026-05-27T16:45:04Z
  repaired A7AL-2L generated_at = 2026-05-27T17:35:24Z

The current chain is a local target replay for the two OI-price seeds, not a full A7AL-2L replay pool.
```

## Authorization

```text
Authorized:
  A7AL-2P2 local OI-price seed search contract drafting

Not authorized:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```

Required next action:

```text
Draft A7AL-2P2 as a local OI-price seed search contract only; do not authorize execution, alpha proof, or shadow/paper/live.
```
