# Crypto A7I-0 Runner Contract Audit

- generated_at: `2026-05-19T15:36:26Z`
- decision: `PASS_A7I0_RUNNER_CONTRACT_AUDIT`
- executes_search: `False`
- authorizes_a7i1: `True`
- authorizes_alpha_proof: `False`
- blockers: `[]`

## Scope

A7I-0 verifies that the residual-aware small generator contract is explicit before any A7I-1 search/smoke is run.

## Required Contract Checks

| group | checks | pass count | total |
|---|---:|---:|---:|
| `blocked_promotions` |  | 4 | 4 |
| `budget` |  | 5 | 5 |
| `execution_lag` |  | 2 | 2 |
| `may_boundary` |  | 4 | 4 |
| `placebo` |  | 4 | 4 |
| `residual_baselines` |  | 3 | 3 |

## Unit Contract Tests

| test | expected | pass |
|---|---|---:|
| `FundingCore_classified_as_mandatory_baseline` | `MANDATORY_BASELINE_NOT_CANDIDATE` | `True` |
| `Core4_classified_as_research_benchmark` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` | `True` |
| `Taker_imbalance_classified_as_overlay_clue` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` | `True` |
| `Placebo_arm_required` | `NEGATIVE_CONTROL` | `True` |
| `May_not_used_for_ranking` | `CONTRACT_PASS` | `True` |

## Decision Boundary

- PASS allows implementing A7I-1 small matched-budget residual-aware generator smoke.
- PASS does not authorize alpha proof, A7.3 old bakeoff, shadow, paper, or live.
- May 2026 is locked as known adversarial stress and cannot be used for ranking.
