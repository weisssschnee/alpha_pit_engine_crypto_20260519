# ADR 0002: Capability-only search-instrument authority

Status: Accepted for deterministic capability qualification
Date: 2026-07-15

## Context

The accepted Frontier closure proves that historical B1S/Epoch implementations
used ambiguous temporal primitive names, one implicit cross-sectional mapping,
and feedback that was not fully aligned with strict feasibility. Those Epoch
modules are retained on the immutable closure line and are not executable files
on current `main`.

The repair must not rewrite historical Epochs, run market search, read sealed
roles, integrate new data, or turn a synthetic capability result into economic
evidence.

## Decision

Add one small capability-only path under
`alphafactory_crypto/instrument_capability/`:

1. one canonical implementation for the thirteen requested temporal primitive
   IDs, with source-qualified legacy aliases;
2. three explicit mappings: `CROSS_SECTIONAL_ZERO_NET`,
   `TIME_SERIES_DIRECTIONAL_STATEFUL`, and `SPARSE_EVENT_OR_CARRY`;
3. a mapping-aware evaluator using full-L1 turnover and a fixed 5 bps cost;
4. frozen lexicographic strict-feasibility feedback with wrong-lag and semantic
   conflicts blocked before strict evaluation;
5. a deterministic planted-mechanism harness covering a canonical typed
   sampler, CEM-like policy, UCT/UCB-like policy, and evolutionary
   parent/mutation path.

Historical B1S/Epoch code remains a commit-bound proposal/parity source. A
legacy alias cannot become canonical through parity. `typed_random` and
`typed_ast` remain one sampler identity, and the historical B1S adaptive labels
remain classified as degenerate rather than promoted to independent algorithms.

## Consequences

- Every capability candidate carries an explicit mapping contract and mapping
  content hash before evaluation.
- Final position caps are checked on final weights. Gross is explicitly reduced
  when a cross-sectional gross/cap request is infeasible.
- Directional and sparse mappings are not subjected to a universal
  cross-sectional IC or five-active-asset gate.
- Evidence is deterministic, non-market, fixed-seed, and reproducible through a
  single `build/check` entrypoint.
- A capability-qualified result authorizes neither development search nor data
  integration, challenge/forward/recent/May-stress access, promotion, or
  cross-sprint memory.
- Lifecycle changes in CURRENT remain explicit decisions; tests may refresh
  assurance but cannot open a forbidden boundary.
