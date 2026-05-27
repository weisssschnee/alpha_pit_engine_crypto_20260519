# Crypto A7G-0 Regime Feature Contract Audit

- generated_at: `2026-05-19T13:49:51Z`
- decision: `PASS_A7G0_FIELD_CONTRACT_A7F_CORRECTION_REQUIRED`
- blockers: `[]`
- warnings: `[]`

## Contract

- `mark_index_ratio = mark_close / index_close - 1.0`; it is already centered around zero.
- Correct absolute basis proxy: `abs(mark_index_ratio)`.
- Incorrect A7F proxy: `abs(mark_index_ratio - 1.0)`.

## Key Metrics

- train basis_abs_v0 median: `1.0002057058894396`
- train basis_abs_v1 median: `0.0004608692034395734`
- train basis_abs_v2 median: `0.000460869203439575`
- train v0/v1 bucket match rate: `0.2689635535307517`
- train v1/v2 bucket match rate: `1.0`

## Decision

A7F's old `basis_abs_mean` used an invalid centered-ratio transform. Old G6 remains a diagnostic only and cannot be used as A7G design evidence.

Required next step: rerun A7F with `basis_abs_mean = abs(mark_index_ratio)` before any funding-regime redesign.
