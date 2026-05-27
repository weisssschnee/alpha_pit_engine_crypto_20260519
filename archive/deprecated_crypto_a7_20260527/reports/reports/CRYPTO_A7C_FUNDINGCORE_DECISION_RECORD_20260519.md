# Crypto A7C FundingCore Decision Record

- decision: `HOLD_FUNDINGCORE_ALPHA_SHADOW_PROOF`
- status: `fundingcore_research_baseline_only`
- generated_at: `2026-05-19T13:11:42Z`

## Summary

- validation 10bps annualized: `2.106167645859684`
- recent OOS 10bps annualized: `0.9279025035074226`
- fresh May 10bps annualized: `-2.7060542933901917`
- validation 20bps annualized: `1.8477683004786287`
- recent OOS 20bps annualized: `0.6528964955906105`
- recent symbol LOO positive rate: `1.0`

## Decision

FundingCore is retained as the mandatory crypto benchmark and a simpler research baseline.

It is not promoted to alpha shadow proof if fresh May remains negative or drawdown risk remains unresolved.

## Confirmed

- Funding-only structure is the dominant simple explanation for Core4.
- FundingCore must be included in all future crypto reward/bakeoff comparisons.
- A6 dry-shadow remains engineering telemetry only.

## Not Confirmed

- paper/live readiness
- production execution
- independent Core4 alpha proof
- crypto generator/reward maturity

## Required Next Action

If FundingCore remains blocked, redesign crypto reward around funding-baseline residual edge before any generator bakeoff.
