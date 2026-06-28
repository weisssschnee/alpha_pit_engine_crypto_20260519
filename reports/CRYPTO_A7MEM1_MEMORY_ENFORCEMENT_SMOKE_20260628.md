# CRYPTO A7MEM-1 Memory Enforcement Smoke 20260628

## Decision

`PASS_A7MEM1_MEMORY_ENFORCEMENT_CONNECTED`

Boundary: memory enforcement smoke only. This does not run proxy evaluation, replay, alpha proof, shadow, paper, or live.

## Checks

- fail_closed_missing_prior: `True`
- duplicate_expression_rejected: `True`
- skeleton_cap_rejected: `True`
- promoted_rows: `2`
- downweighted_rows: `1`
- accepted_rows: `3`
- rejected_rows: `2`

## Next Gate

A7SEARCH queues must run with A7MEM prior loaded by default. `--no-memory-enforcement` is for legacy reproduction only.
