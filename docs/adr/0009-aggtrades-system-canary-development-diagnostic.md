# ADR 0009: aggTrades fixed-cohort search-system canary

- Status: Accepted
- Date: 2026-07-27
- Authority: explicit user authorization in the active Codex task

## Decision

Authorize exactly one fresh-state, 2,000-candidate development diagnostic that
uses the delivered Binance aggTrades Top100 and ranks 101-200 compact releases
as an input carrier for Search Engine V1.

The canary reuses the existing `CandidateSpec`, typed compiler, matched control,
pair evaluator, Behavior Archive, CEM V2, Evolution V2, and checkpoint/restore
implementation. It may add only a runtime-local hourly `RawPanelStore` bridge
and a bounded campaign profile in the existing runner.

The frozen window is 2024-01-01 through 2024-07-01 exclusive. Every strict
candidate must use at least one aggTrades field. The three arms are canonical
typed random, Hierarchical Typed CEM V2, and Typed Evolution V2, allocated
200/400/400 per 1,000-candidate checkpoint across the same four seeds.

## Evidence authority

The run may answer only:

- whether the repaired search system completes fresh-state proposal,
  compilation, matched evaluation, archive update, and exact restore;
- whether CEM V2 or Evolution V2 changes proposal productivity, reward
  diagnostics, or behavior-family discovery relative to typed random at equal
  matched count;
- whether Evolution V2 executes verified effective-gene, skeleton, and
  homologous-crossover operations on the new field surface.

The fixed retrospective cohort is disclosed and accepted only for this system
diagnostic. Missing source coordinates remain missing. Candidate and control
share the exact same eligible mask.

## Boundaries

This decision does not authorize Alpha claims, research admission, OOS,
challenge, recent, May-stress, forward access, promotion, latent priority,
relational training, cross-sprint adaptive memory, a larger budget, or a second
run. No arm can qualify for a future Arena from this canary.

Liquidation and OI/mark are outside this run. The historical Search Engine V1
20k bundle and all of its policy/archive state remain immutable and spent.

## Consequences

The current `NEW_PERFORMANCE_SEARCH_FROZEN` boundary remains in force. A
completed canary is engineering evidence about the search system, not an
authority transition for data or economic research.
