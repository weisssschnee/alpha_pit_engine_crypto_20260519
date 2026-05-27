# Crypto A7M-2A AST Repair Adapter Preflight

- generated_at: `2026-05-20T07:11:17Z`
- decision: `PASS_A7M2A_AST_REPAIR_ADAPTER_PREFLIGHT`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7m2_execution: `False`
- stable_manifest_hash: `e0164cdc39e3039992d40cdc1079101f428104356818796cd32b0468811aaf83`

## Confirmed

- Crypto failure taxonomy is mapped to repair policies.
- Repair actions are limited to non-May, timing-aware, low-risk transformations.
- Raw failures and residual-only clues cannot be directly promoted.
- FundingCore/Core4/taker packaging is blocked from standalone alpha promotion.

## Failure Taxonomy

| failure_type | observed_count | repair_policy | repair_allowed |
|---|---:|---|---|
| `raw_fail` | 2705 | `negative_label_only` | `False` |
| `residual_fail` | 1608 | `orthogonalize_or_penalize` | `True` |
| `cost20_fail` | 2779 | `reduce_turnover_and_smooth` | `True` |
| `lag1_fail` | 2631 | `increase_latency_stability` | `True` |
| `activity_coverage_fail` | 52 | `remove_zero_activity_artifacts` | `True` |
| `beta_fail` | 41 | `beta_penalty_or_reject` | `True` |
| `residual_only_clue` | 204 | `diagnostic_only` | `False` |
| `near_miss` | 125 | `targeted_non_may_mutation` | `True` |

## Boundary

- This is an adapter preflight only.
- It does not generate formulas, run replay, produce research candidates, or authorize alpha proof/shadow/paper/live.
