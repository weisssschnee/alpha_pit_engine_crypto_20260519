# ADR 0012: Unified Field Management Compiled View

- Status: Accepted
- Date: 2026-07-28
- Authority: explicit user authorization in the active Codex task

## Context

Field identity and eligibility facts already have separate authorities:

- the 5,388-row runtime inventory and lineage ledger;
- the 81-row ontology and 36-row input-approval registry;
- the 5,211 existing derived recipes;
- the Broad and Core3 token contracts;
- the four independent Search Surface Integration V1 carrier contracts;
- `FieldContract`, `TypedExpressionRegistry`, `CandidateSpec`, and the existing
  materializers.

These authorities overlap but serve different purposes. Re-entering their
facts into a new ontology, approval registry, carrier registry, AST, or
materializer would create conflicting sources of truth. The existing
`field_information_qualification_v0` CURRENT node already owns the compiled
field-information view, but did not expose carrier bindings, deterministic
canonical identities, derived recipes, provenance-only exclusions, or
authority conflicts in one navigable artifact.

## Decision

Extend that existing logical capability with a deterministic, read-only
management compiler. It discovers the current authority files declared in
`config/crypto_unified_field_management_v1.json` and produces:

- one canonical management record per discovered field or derived view;
- scoped source-to-canonical bindings;
- the existing lazy derived recipes and their deterministic identities;
- an independent carrier-by-field matrix;
- typed search-role bindings resolved by the existing frozen role resolver;
- a fail-closed authority-conflict table;
- a compact summary and content-bound manifest.

Canonical management identities do not replace executable field IDs.
`CandidateSpec`, expression hashes, carrier field IDs, compiler behavior, and
replay identities remain unchanged. Exact duplicate field contracts may bind
to one canonical identity, while carrier membership remains a separate scoped
row. Venue-qualified names, units, statistics, lags, and instrument semantics
are never collapsed by heuristic similarity.

The following Core3 receipt/time identifiers are explicitly provenance-only
and cannot receive search roles:

- `agg_first_agg_trade_id`
- `agg_last_agg_trade_id`
- `agg_first_transact_time_ms`
- `agg_last_transact_time_ms`

## Boundaries

The compiled view is not an ontology, approval authority, lineage authority,
feature store, materializer registry, search registry, evaluator, or database.
It cannot activate a field, merge carrier contexts, authorize research
admission, modify a candidate identity, run a market search, read reward or
sealed evidence, or promote a candidate.

No third Graph layer or parallel management hierarchy is created. CURRENT
continues to use the existing `field_information_qualification_v0` logical
node, updated with this management/navigation contract.

## Consequences

Authority drift and contract conflicts now fail closed before the compiled
view is published. New source registries can be added by declaring their
authority path and recompiling; their fields do not require duplicate manual
catalog entries. Search reachability and research admission remain separate
decisions owned by their existing authorities.
