# Crypto A7M-1B Surrogate Calibration + Inherited Engine Readiness

- generated_at: `2026-05-20T04:49:10Z`
- decision: `HOLD_A7M1B_SURROGATE_OR_ENGINE_READINESS_WEAK`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7m2_protocol_writing: `True`
- authorizes_a7m2_execution: `False`
- near_miss_lift_excluding_dry: `7.558442`
- cost20_lift_excluding_dry: `4.671003`
- lag1_lift_excluding_dry: `3.191835`
- leave_source_out_near_miss_lift_min: `0.465646`
- adapter_ready_count: `4`

## Engine Inventory

| engine | status | required adapter |
|---|---|---|
| `FormulaGenV2_crypto_adapter` | `adapter_ready` | field_dictionary_and_crypto_evaluator_adapter |
| `typed_AST_sampler_crypto_adapter` | `adapter_ready` | crypto_field_types_and_operator_timing_contract |
| `AST_failure_aware_repair` | `inventory_present_adapter_needed` | crypto_failure_taxonomy_and_repair_actions |
| `CEM_adaptive_grammar_crypto` | `inventory_present_adapter_needed` | crypto_CEM_candidate_ledger_and_production_weight_update |
| `surrogate_prioritized_sampler` | `adapter_ready` | A7M1_surrogate_score_to_generator_prior_interface |
| `cluster_registry_search_memory` | `adapter_ready` | crypto_return_corr_or_signal_cluster_memory |

## Boundary

A7M-1B may authorize writing an A7M-2 inherited-engine bakeoff protocol. It does not authorize executing A7M-2, large search, alpha proof, shadow, paper, or live deployment.
