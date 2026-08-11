# ADR 0023: Temporal 30K-to-50K Successor Execution Mode

- Status: Accepted
- Date: 2026-08-11
- Amends: ADR 0015 for this one artifact-bound development successor only

## Context

The historical adaptive-broad runtime is invalid as a whole, but its economic
prefix through completion ordinal 30,000 is independently reconstructed and
qualified.  The suffix beginning at 30,001 is invalid.  The canonical Temporal
Program runner previously had no physical path that could consume the frozen
successor specification, restore the valid prefix, or distinguish an additional
20,000 strict budget from a fresh 0-to-50,000 campaign.

## Decision

The existing canonical `temporal_program_search_v1.py` runner gains one explicit
`30K_TO_50K_SUCCESSOR` mode.  It reuses the existing market loader, compiler,
AST, evaluator, mapping, reward, archive and worker path.  It does not create a
second search engine.

Before market access, the mode must independently verify the frozen successor
receipt, reconstruction report, adaptive-policy bundle, source artifact hashes,
economic and program-catalog identities, implementation component bundle, one
unconsumed authorization and a fresh fixed runtime root.  Any mismatch is
`FAIL_CLOSED_BEFORE_MARKET_READ`.

The mode restores only state attributable to completion ordinals 1 through
30,000: evaluated ledger and lineage, attempted exact identities, Behavior
Archive and champions, family counters, policy-local family counts, and the
four CEM plus four Evolution learning lanes.  The historical Random RNG is not
resumed.  Four deterministic lanes under
`FRESH_RANDOM_CONTROL_AFTER_30K` are frozen before market access.  Any state
needed for admission or mutation that cannot be reconstructed from the valid
prefix blocks execution.

Successor decisions occur only after complete 5,000-additional-strict tranches.
The initial allocation is Random 20%, Evolution 60%, CEM 20%.  Random remains a
20% control floor; when one adaptive arm exits, the complete 80% adaptive share
is assigned deterministically to the survivor.  If both adaptive arms exit the
run stops for economic futility.  Family concentration remains diagnostic only.
The run mechanically stops at 20,000 additional strict or 50,000 cumulative
valid strict, whichever representation is used.

The sole authorization artifact is
`config/crypto_temporal_program_30k_to_50k_successor_v1_authorization.json`.
Its committed default is `IMPLEMENTED_NOT_AUTHORIZED`.  An external decision may
atomically transition that one artifact to
`RUN_AUTHORIZED_ONE_TIME_30K_TO_50K_DEVELOPMENT_SUCCESSOR`, binding the accepted
implementation commit, exact component hashes and one fixed runtime identity.
That authorization-only transition must be committed before execution.  A
second launch, a non-fresh output root, a terminal resume, or a consumed
authorization fails closed.

## Boundaries

This ADR accepts implementation readiness; it does not authorize the market
continuation.  It does not reactivate the old consumed receipt or historical
runtime.  Validation, OOS, holdout, forward, promotion, automatic expansion,
parameter tuning, rescue rerun and sealed reads remain forbidden.  Readiness is
not market evidence and creates no new formal economic authority.

