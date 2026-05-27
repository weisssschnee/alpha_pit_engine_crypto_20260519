# Crypto A7P-0 Search-Cell Failure-Map Redesign Contract

- generated_at: `2026-05-20T17:58:20Z`
- objective: convert A7O-L1W1R HOLD into non-May cell redesign tasks
- executes_new_search: `False`
- executes_replay: `False`
- authorizes_w2: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Policy

- May remains stress-only: post-selection stress/veto/failure attribution.
- May is forbidden for ranking, reward, threshold tuning, generation, allocation, mutation, and surrogate targets.
- Cell redesign may use negative-control contamination, non-May raw/cost/lag/residual fragility, activity validity, and diversity.
- Control-contaminated cells cannot contribute to W2 continuation evidence.

## Task Registry

| task_id   | task                                                          | reason                                                 | required_before   | executes_search   | may_policy               | current_authorization   | parent_decision                                     |
|:----------|:--------------------------------------------------------------|:-------------------------------------------------------|:------------------|:------------------|:-------------------------|:------------------------|:----------------------------------------------------|
| A7P-2A    | instrument_active_hour_count_in_fold_and_split_artifacts      | stress_gate_v3_active_hour_count_unavailable           | W2                | False             | stress_only              | authorized              | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
| A7P-2B    | implement_negative_control_dominance_gate                     | wrong_lag_stale_24h_controls_passed_research_like_gate | W2                | False             | not_used                 | authorized              | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
| A7P-2C    | quarantine_control_contaminated_cells_C0208_C0223             | checkpoint_04_control_contamination                    | W2                | False             | not_used                 | authorized              | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
| A7P-2D    | build_control_clean_w2_cell_registry_from_non_may_failure_map | W1R_HOLD_and_W2_not_authorized                         | W2                | False             | may_not_rank_or_allocate | authorized              | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
| A7P-2E    | dry_run_w2_cell_registry_coverage_audit                       | verify_cell_mix_before_any_checkpoint_execution        | W2                | False             | not_used                 | authorized              | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
| A7P-3     | only_after_A7P2_pass_run_small_protected_w2_pilot             | W2_currently_not_authorized                            | none              | True              | stress_only              | blocked                 | PASS_A7P1_FAILURE_MAP_READY_FOR_A7P2_REDESIGN_TASKS |
