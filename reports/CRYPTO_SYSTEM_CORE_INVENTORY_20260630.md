# CRYPTO SYSTEM CORE INVENTORY 20260630

Generated: `2026-06-30T12:54:47Z`

## Decision

`PASS_SYSTEM_CORE_INVENTORY_BUILT`

## Summary

| subsystem | status | count |
| --- | --- | --- |
| aggregation_reporting | wrap_with_contract | 7 |
| feature_factory | legacy_reference | 2871 |
| feature_response | archive_only | 320 |
| field_contracts | archive_only | 246 |
| formula_generation | wrap_with_contract | 1 |
| planning | keep_core | 5 |
| proxy_evaluation | keep_core | 1 |
| reports | source_of_truth_evidence | 230 |
| reward_validation | keep_core | 1 |
| runtime_artifacts | source_of_truth_evidence | 1526 |
| search_generation | legacy_reference | 19 |
| search_generation | wrap_with_contract | 2 |
| search_memory | keep_core | 2 |
| search_memory | wrap_with_contract | 15 |
| unknown | legacy_reference | 215 |

## Key Core Candidates

| path | subsystem | status | evidence |
| --- | --- | --- | --- |
| .planning/phases/01-crypto-search-hardening/01-PLAN.md | planning | keep_core | current planning source of truth |
| .planning/phases/05-verified-core-extraction-or-new-repo-decision/05-PLAN.md | planning | keep_core | current planning source of truth |
| .planning/PROJECT.md | planning | keep_core | current planning source of truth |
| .planning/ROADMAP.md | planning | keep_core | current planning source of truth |
| .planning/STATE.md | planning | keep_core | current planning source of truth |
| alphafactory_crypto/engines/formula_gen_v2_adapter.py | formula_generation | wrap_with_contract | formula adapter exists; needs stable queue contract |
| alphafactory_crypto/engines/search_memory.py | search_memory | keep_core | A7MEM-0/1 pass; imported by search generation |
| alphafactory_crypto/engines/search_memory_enforcement.py | search_memory | keep_core | A7MEM-0/1 pass; imported by search generation |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_archive_pointer_map.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_candidate_memory.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_formula_cluster_memory.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_manifest.json | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_next_search_prior.json | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_pair_motif_prior.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_rejection_memory.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_search_run_registry.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem0_search_memory_registry_20260628/a7mem0_source_record_memory.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem1_memory_enforcement_smoke_20260628/a7mem1_manifest.json | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem1_memory_enforcement_smoke_20260628/a7mem1_smoke_accepted_rows.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem1_memory_enforcement_smoke_20260628/a7mem1_smoke_input_rows.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7mem1_memory_enforcement_smoke_20260628/a7mem1_smoke_trace.csv | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| runtime/a7search6_prepare_manifest_20260630.json | search_generation | wrap_with_contract | current running search; mechanism-seeded queue generator |
| runtime/a7v3s0_reward_sharded_720h_r2_aggregate_20260613/a7v3s0_reward_sharded_aggregate_manifest.json | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| runtime/a7v3s6_prefiltered_reward_smoke_aggregate_20260614/a7v3s0_reward_sharded_aggregate_manifest.json | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| runtime/a7v3s8_redesigned_reward_smoke_aggregate_20260614/a7v3s0_reward_sharded_aggregate_manifest.json | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| runtime/a7v3s9_prereward_oos_control_proxy_aggregate_20260614/a7v3s9_proxy_aggregate_manifest.json | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| runtime/a7v3s9_selected_full_reward_aggregate_20260614/a7v3s0_reward_sharded_aggregate_manifest.json | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| scripts/crypto_a7mem0_search_memory_registry.py | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| scripts/crypto_a7mem1_memory_enforcement_smoke.py | search_memory | wrap_with_contract | memory registry scripts produce current prior |
| scripts/crypto_a7reward1_portfolio_reward_model.py | reward_validation | keep_core | strict reward gate used by A7SEARCH5/A7SEARCH6 |
| scripts/crypto_a7search6_mechanism_memory_seed_search.py | search_generation | wrap_with_contract | current running search; mechanism-seeded queue generator |
| scripts/crypto_a7v3s0_reward_sharded_aggregate.py | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
| scripts/crypto_a7v3s9_prereward_oos_control_proxy.py | proxy_evaluation | keep_core | proxy evaluator used by large search waves |
| scripts/crypto_a7v3s9_proxy_aggregate.py | aggregation_reporting | wrap_with_contract | aggregate scripts are source-of-truth producers |
