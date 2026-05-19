# Crypto A7F Decision Record

- decision: `HOLD_A7F_FUNDING_REGIME_FAILURE_UNRESOLVED`
- generated_at: `2026-05-19T13:50:57Z`
- blockers: `['predeclared_funding_gate_does_not_clear_fresh_may_failure']`
- warnings: `['core4_still_negative_under_predeclared_funding_gate']`

## Conclusion

A7F fixes no formulas and performs no search. It tests whether train-threshold funding/basis/volatility regimes can explain or reduce the fresh May failure.

## Current State

- Funding semantics are clean enough for research after A7E.
- FundingCore/Core4 remain blocked from alpha shadow proof unless fresh-forward and drawdown risks are cleared.
- Any gate found here is a research candidate only and must be forward-locked before evidence upgrade.
