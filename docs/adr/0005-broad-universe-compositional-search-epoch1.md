# ADR 0005: Gated broad-universe compositional-search epoch

- Status: Accepted for development-only qualification
- Date: 2026-07-15
- Scope: data-universe and representation qualification
- Authorization: `BOUNDED_DEVELOPMENT_ONLY_DATA_AND_REPRESENTATION_QUALIFICATION`

## Context

The existing native aggTrades canary contains ten assets and six development
months.  Its 9,576-candidate grammar applies one representation and one
primitive to exactly one field.  Neither property is sufficient authority for
a broad cross-sectional Alpha search.

The requested epoch defines two legal data modes, a compositional expression
surface, matched controls, and a large search budget.  It also preserves sealed
roles and forbids promotion.  Calling the large search "formal" would conflict
with the accepted CURRENT boundary, so this ADR interprets it as a bounded
development-only experiment.  Formal performance search remains forbidden.

## Decision

Run the work as ordered hard gates:

1. Inventory only registered local sources and admitted development dates.
2. Require either 40 assets over 18 continuous months with PIT-safe dynamic
   eligibility, or an explicit fixed core over 24 months.
3. Audit at least 2,000 current grammar candidates for exact, numeric, rank,
   mapped-weight, and behavior identities.
4. Keep the typed compositional DAG separate from the accepted canary grammar.
   It is lazy, unit-aware, domain-aware, and PIT-aware, but non-formal.
5. Run the 64-pair resource preflight and large search only after a data mode is
   qualified.  A failed data gate produces zero proposal and strict budgets.

The historical 176-symbol archive cannot establish a PIT universe by itself:
its symbol seed came from a 2026 current exchangeInfo snapshot and checkpoint
availability.  Official archive file presence identifies observed asset-months
but does not prove that delisted historical contracts were not omitted.

## Consequences

The epoch may establish a data or representation bottleneck without running an
economic search.  Empty search artifacts explicitly mean `NOT_RUN`, not zero
performance.  The typed DAG and matched-ablation contract remain
`EXPERIMENTAL_CURRENT_NON_FORMAL` until qualified data, resource preflight, and
runtime evidence exist.  Validation, holdout, test, recent, forward, challenge,
May stress, promotion, and cross-sprint adaptive memory remain unavailable.
