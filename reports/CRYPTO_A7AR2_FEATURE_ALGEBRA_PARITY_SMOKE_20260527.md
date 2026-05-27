# Crypto A7AR-2 Feature Algebra Parity Smoke

## Decision

PASS_A7AR2_FEATURE_ALGEBRA_PARITY_SMOKE

## Scope

- Evaluates A7AR-1 generated formulas on a strict_full_history top498 sample.
- Tests crypto-safe operator execution for Mean, Delta, ZScore, Rank, Mul, Sub, Neg.
- Audits +1h/+2h timing feasibility, NaN/inf, active signal coverage, and control-evaluation feasibility.
- Does not run alpha replay, ranking, formula search, or candidate promotion.

## Results

- symbols: 32
- panel_rows: 419205
- evaluated_candidates: 96
- eval_failures: 0
- plus2_active_candidates: 86
- inf_candidate_count: 0
- timing_violations: 0
- field_contract_missing: 0
- control_eval_failures: 0

## Authorization

- A7AR-3 fresh memory/dedup smoke is authorized if this decision is PASS.
- A7AL-2 formula search remains not authorized.