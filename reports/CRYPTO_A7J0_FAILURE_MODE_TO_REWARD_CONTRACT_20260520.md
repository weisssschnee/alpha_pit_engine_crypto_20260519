# Crypto A7J-0 Failure-Mode-to-Reward Contract

- generated_at: `2026-05-19T17:07:13Z`
- decision: `PASS_A7J0_FAILURE_MODE_TO_REWARD_CONTRACT`
- executes_search: `False`
- authorizes_a7j1: `True`
- authorizes_a7j2: `False`
- authorizes_alpha_proof: `False`

## Hard Boundary

- May 2026 is a known adversarial stress set.
- May cannot enter ranking, reward score, threshold tuning, weight selection, candidate selection, or generator tuning.
- May may only appear as post-selection stress label / veto / failure attribution.

## Reward Redesign

Positive terms: raw validation/recent, residual vs FundingCore/Core4, 20bps cost survival, 1bar lag survival, symbol/month stability.

Penalty terms: FundingCore/Core4 beta, turnover/cost, drawdown, top-loss concentration, duplicate family concentration.

## Expected Known-Object Classification

| object | expected classification |
|---|---|
| `FundingCore` | `MANDATORY_BASELINE_NOT_CANDIDATE` |
| `Core4` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` |
| `Rank(taker_imbalance)` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` |
| `i2_microstructure_lite_113` | `A7J_CLUE_ONLY_COST_LAG_MAY_FRAGILE` |
| `placebo_random` | `NEGATIVE_CONTROL` |

## Next

Run A7J-1 redesigned runner preflight. Do not run A7J-2 until known-object classification and May-exclusion checks pass.
