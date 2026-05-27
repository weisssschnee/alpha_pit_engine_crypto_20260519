# Crypto A7M-2C Execution Authorization Revision

- generated_at: `2026-05-20T07:11:32Z`
- decision: `PASS_A7M2C_EQUAL_BUDGET_BAKEOFF_AUTHORIZATION_REVISION`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_equal_budget_a7m2_bakeoff: `True`
- authorizes_surrogate_driven_allocation: `False`
- authorizes_adaptive_large_search: `False`
- authorizes_alpha_proof: `False`
- stable_manifest_hash: `b8533d134123b899af47ac0ffd9e18d10db97337468dd11e07fb1b94490b848a`

## Blocker Reclassification

| blocker | new_classification | blocks_equal_budget | blocks_adaptive_allocation |
|---|---|---|---|
| `A7M1B_surrogate_cross_source_hold` | `allocation_mode_blocker` | `False` | `True` |
| `E3_AST_failure_aware_repair_not_executable` | `resolved` | `False` | `False` |
| `E4_CEM_adaptive_grammar_not_executable` | `resolved` | `False` | `False` |

## Confirmed

- A7M-1B surrogate cross-source HOLD blocks adaptive allocation, not equal-budget bakeoff.
- E5 surrogate-prioritized sampler can only be tested as an equal-budget engine arm.
- May remains stress-only and cannot enter ranking/reward/generator tuning/arm allocation.

## Still Not Authorized

- Adaptive large search.
- Alpha proof.
- Shadow, paper, live, or production deployment.
