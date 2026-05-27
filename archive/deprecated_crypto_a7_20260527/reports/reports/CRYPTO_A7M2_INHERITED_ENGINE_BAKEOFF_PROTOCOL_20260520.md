# Crypto A7M-2 Inherited-Engine Bakeoff Protocol

- generated_at: `2026-05-20T05:00:52Z`
- decision: `PASS_A7M2_INHERITED_ENGINE_BAKEOFF_PROTOCOL`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7m2_execution: `False`
- authorizes_large_search: `False`
- stable_protocol_hash: `f10ef34a8b99dd1bd328e8b7336a64ac1d1ed6e10d5676fde6d1945490da1ed1`

## Planned Budget If Separately Authorized

- engines: `8`
- seeds: `4`
- generated_per_engine_seed: `5000`
- total_generated: `160000`
- strict_replay_total: `4096`
- deep_audit_total: `512`

## Engine Matrix

| engine | readiness | purpose | blocker |
|---|---|---|---|
| `E0 current_A7L_manual_generator` | `executable` | Control arm representing current manual A7L generator space. |  |
| `E1 FormulaGenV2_crypto_adapter` | `adapter_ready` | Test typed motif formula generation with crypto field dictionary. |  |
| `E2 typed_AST_sampler_crypto_adapter` | `adapter_ready` | Test typed AST expression diversity under crypto field/operator contract. |  |
| `E3 AST_failure_aware_repair` | `blocked_adapter_needed` | Repair failed crypto candidates using failure taxonomy. | requires crypto failure taxonomy and repair-action adapter preflight |
| `E4 CEM_adaptive_grammar_crypto` | `blocked_adapter_needed` | Learn grammar production weights from non-May failure labels. | requires crypto CEM ledger, production weights, and May-exclusion preflight |
| `E5 surrogate_prioritized_sampler` | `adapter_ready` | Use non-May surrogate scores for cheap filtering and diversity-aware selection. |  |
| `E6 placebo_random_control` | `executable` | Detect false-positive replay/gate behavior. |  |
| `E7 adversarial_null_wrong_lag_control` | `executable` | Detect wrong-lag/future-sensitive artifact behavior. |  |

## Execution Blockers

- `A7M1B_surrogate_cross_source_hold`: leave_source_out_near_miss_lift_min=0.465646
- `E3_AST_failure_aware_repair_not_executable`: requires crypto failure taxonomy and repair-action adapter preflight
- `E4_CEM_adaptive_grammar_crypto_not_executable`: requires crypto CEM ledger, production weights, and May-exclusion preflight

## Boundary

- May remains stress-only and cannot enter ranking, reward, arm allocation, generator weights, or mutation priors.
- A7M-2 protocol does not authorize running the bakeoff.
- Highest possible output if later run is `A7M_RESEARCH_CANDIDATE_POOL`, not alpha proof.
