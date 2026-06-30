# CRYPTO SYSTEM CORE INTERFACE CONTRACTS 20260630

Generated: `2026-06-30T12:54:47Z`

## Decision

`PASS_SYSTEM_CORE_INTERFACE_CONTRACTS_BUILT`

| interface | required | fail_closed_on | authorizes |
| --- | --- | --- | --- |
| DataPanelContract | symbol, timestamp, trade_close, trade_quote_volume | missing_timestamp, duplicate_symbol_timestamp, future_feature_available_time, unregistered_panel | field_materialization |
| FieldContractRegistry | field, semantic_type, role, pit_status, latency_status, allowed_routes | missing_contract, label_or_future_field, same_bar_timing_violation | formula_queue_generation |
| FormulaCandidateQueue | blueprint_id, expression, semantic_pair, motif, horizon_h, skeleton_key | missing_expression, memory_reject, forbidden_field, unsupported_operator | proxy_evaluation_only |
| ProxyEvaluationResult | blueprint_id, proxy_score, proxy_strict_pass, proxy_near_miss, proxy_selectable, hard_reject_reasons | eval_error_rows_nonzero, missing_shards, selected_rows_zero | bounded_full_reward |
| RewardGateResult | train_sortino, validation_sortino, test_sortino, recent_sortino, min_oos_floor_sortino, stress_floor_sortino, recent_shuffle_control_ratio | train_orientation_no_positive_edge, oos_floor_not_positive, control_dominated, lag_stale_dominated, shuffle_dominated | validation_pack |
| ValidationPackResult | canonical_accepted_rows, single_leg_accepted_rows, operator_ablation_accepted_rows, decision | eval_error_rows_nonzero, single_leg_dominates, canonical_failed | memory_triage_only |
| SearchMemoryUpdate | candidate_memory, cluster_memory, pair_motif_prior, rejection_memory, decision | missing_rejection_memory, missing_cluster_caps, not_required_for_next_large_search | next_queue_generation |
| RunManifest | stage, decision, generated_at, runtime, report, authorizes_alpha_proof, authorizes_shadow_paper_live | missing_decision, authorization_conflict, stale_source_of_truth | next_stage_if_explicit |
