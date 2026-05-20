# Crypto A7M-2 Equal-Budget Inherited-Engine Bakeoff

- generated_at: `2026-05-20T09:29:49Z`
- decision: `HOLD_A7M2_ENGINE_BAKEOFF_BLOCKED`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- equal_budget: `True`
- authorizes_adaptive_large_search: `False`
- authorizes_alpha_proof: `False`
- generated_count: `160000`
- strict_replay_count: `4096`
- deep_audit_count: `512`
- research_candidate_count: `0`
- deep_survivor_or_near_miss_count: `379`
- inherited_engine_advantage_count: `2`
- return_corr_cluster_count: `11`
- blockers: `['single_cluster_contributes_over_35pct']`
- stable_manifest_hash: `004c91e010fdab43bc23ab9655a33e075d7fd2384b30581338c12b3810b529a5`

## Engine Summary

| engine | strict | research | survivor/near-miss | rate | beats E0 | clusters |
|---|---:|---:|---:|---:|---|---:|
| `E0_current_A7L_manual_generator` | 512 | 0 | 152 | 0.2969 | `False` | 4 |
| `E1_FormulaGenV2_crypto_adapter` | 512 | 0 | 139 | 0.2715 | `False` | 5 |
| `E2_typed_AST_sampler_crypto_adapter` | 512 | 0 | 137 | 0.2676 | `False` | 4 |
| `E3_AST_failure_aware_repair` | 512 | 0 | 355 | 0.6934 | `True` | 4 |
| `E4_CEM_adaptive_grammar_crypto` | 512 | 0 | 113 | 0.2207 | `False` | 9 |
| `E5_surrogate_prioritized_sampler` | 512 | 0 | 219 | 0.4277 | `True` | 3 |
| `E6_placebo_random_control` | 512 | 0 | 0 | 0.0000 | `False` | 0 |
| `E7_adversarial_null_wrong_lag_control` | 512 | 0 | 0 | 0.0000 | `False` | 0 |

## Boundary

- This is an inherited-engine bakeoff, not alpha proof.
- E5 surrogate-prioritized sampler is tested as an equal-budget arm only.
- May remains stress-only and is not used for generation, ranking, reward, arm allocation, or mutation priors.
- PASS can only authorize consideration of A7M-3; it cannot authorize shadow/paper/live.
