# Crypto A7M-1 Surrogate Policy Preflight

- generated_at: `2026-05-20T03:45:48Z`
- decision: `PASS_A7M1_SURROGATE_PREFLIGHT`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7m2_adaptive_search: `False`
- training_rows: `2250`
- scored_rows: `3417`

## Method

A7M-1 uses a Laplace-smoothed empirical group model over family, arm, field-family signature, operator signature, horizon, and depth. It is a preflight surrogate, not an alpha model.

## May Boundary

- May stress labels are not policy targets.
- May stress labels are not features.
- May stress labels may only remain in the dataset for reporting/veto/failure attribution.

## Target Lift

| target | base_rate | top_decile_rate | lift |
|---|---:|---:|---:|
| `raw_survive` | 0.236994 | 0.61597 | 2.599091 |
| `residual_survive` | 0.587669 | 0.943262 | 1.605092 |
| `cost20_survive` | 0.213487 | 0.540268 | 2.53068 |
| `lag1_survive` | 0.27052 | 0.636042 | 2.351182 |
| `near_miss` | 0.04817 | 0.340351 | 7.065684 |
| `research_candidate` | 0.000385 | 0.003817 | 9.90458 |

## Decision

A7M-1 is only a surrogate preflight. It does not authorize adaptive large search. A7M-2 still requires an explicit protocol and budget approval.
