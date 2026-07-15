# ADR 0006: Observed-archive 18-month train surface

- Status: Accepted for train-only development use
- Date: 2026-07-16
- Scope: data representation, field reconciliation, and train ingress
- Authorization: `USER_AUTHORIZED_TRAIN_SURFACE_QUALIFICATION_ONLY_20260716`

## Context

The earlier broad-universe epoch treated the six-month 2023H2 backfill and the
six-month native aggTrades core10 release as the available research surfaces.
That was too narrow.  The repository and data root also contain the Top498 v3
hourly replay used by the historical A7 path.  Its 2024 train block has
1,880,549 rows across 276 observed contracts; 176 contracts have all 8,784
hours.  The pre-2024 complete replay adds 668,590 rows across 176 contracts.

Physical data presence is not field authorization.  The two periods have
different column names and schema variants, while the Git inventory contains
5,388 field/spec identities, only ten of which are loaded by the current A7EFF2
runtime contract.

## Decision

Create one train-only adapter covering `2023-07-01T00:00:00Z` through
`2025-01-01T00:00:00Z` exclusive.

1. Normalize documented pre-2024 aliases into the Top498 v3 names.
2. Materialize the three current derived runtime fields only from their
   existing registered dependencies.
3. Activate exactly the ten current runtime fields by default.  A physical
   column or inventory row does not grant search authorization.
4. Return no legacy forward-label, execution, recent-patch, or stress column.
5. Bind the 2,140 contributing source files by SHA256 and persist the complete
   5,388-identity Git reconciliation.
6. Keep the universe explicitly scoped to observed official archive files from
   a current-seeded symbol list.  Do not claim historical delisted-contract
   completeness.

## Consequences

The observed-archive kline/derivatives train surface now has 18 continuous
months, 2,549,139 rows, 13,200 unique hours, 140 to 276 monthly active assets,
and ten of ten current runtime fields passing non-null and variance gates.  The
old 96-asset A7EFF2 numeric cache is a cache scope, not a physical panel limit.

This supersedes only the prior time-history shortage for the observed-archive
kline/derivatives train surface.  Survivorship/eligibility completeness,
native aggTrades order-field history, the explicit-core 24-month requirement,
and the compositional grammar bottleneck remain unresolved.  Formal search,
sealed evaluation, promotion, economic claims, and cross-sprint memory remain
forbidden.
