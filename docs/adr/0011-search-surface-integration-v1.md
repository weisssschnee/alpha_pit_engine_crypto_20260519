# ADR 0011: Search Surface Integration V1

- Status: Accepted
- Date: 2026-07-28
- Authority: explicit user authorization in the active Codex task

## Context

Search Engine V1.2 proved compiler, proposal, matched-control, archive, and
checkpoint behavior on a six-month carrier containing Broad39 plus 21
aggTrades fields. It did not consume the independent Core3 81-token surface,
the delivered cross-venue OI/mark fields, or liquidation fields. Treating the
40 frozen Skeleton variants as if they described the delivered field surface
was therefore incorrect.

The existing pair evaluator already computes candidate-local support as the
point-in-time base eligibility intersected with finite values for exactly the
candidate's raw fields. The new-data admission pipeline nevertheless used
complete historical Top200 support as a global search-cache gate. That gate is
appropriate as a coverage diagnostic and research-admission condition, but it
must not hide whether a delivered field can be materialized, typed, compiled,
and matched on its actual observed coordinates.

## Decision

Implement a non-economic Search Surface Integration V1 with these independent
data planes:

- `BROAD_PANEL_BASELINE`: the existing Broad39 authority;
- `CORE3_MICROSTRUCTURE_PILOT`: the existing independent 81-token Core3
  contract, never concatenated into a joint 120-channel panel;
- `AGGTRADES_TOP200_DELIVERED`: delivered physical aggTrades fields with
  explicit missingness;
- `OI_MARK_RANKS51_200_DELIVERED`: venue-qualified schema-fixed OI/mark fields
  with explicit missingness;
- `LIQUIDATION_DELIVERED_QUARANTINED`: inventory and contract evidence only
  until the existing coverage and source gates pass.

Each active data plane receives:

1. an exact source and field identity;
2. a `FieldContract`;
3. deterministic typed-role and compatible-Skeleton resolution;
4. at least one compiler-validated and matched-control-constructible proof
   candidate for every reachable field;
5. explicit candidate-local support semantics:
   `base_eligible AND finite(all candidate raw fields)`.

`Active` is a per-field runtime state, not a synonym for schema declaration.
A declared field remains HOLD when its carrier does not materialize it, its
full delivered root has zero finite support, or no support-valid runtime proof
can be constructed. V1 therefore records 260 declared engineering fields,
235 runtime-active fields, and 25 explicit field holds. The existing
aggTrades bridge now uses its frozen `search_surface` mode to materialize all
44 delivered physical fields through the same `RawPanelStore`, hourly
aggregator, compiler, and evaluator path used by the 21-field canary. No
second builder, AST, compiler, or evaluator was introduced. The remaining 25
holds are OI/mark fields with zero finite support in the delivered source root;
they are classified as source-unavailable and are neither filled nor
synthesized.

An independent carrier is not required to satisfy roles used only by other
carriers. The generator selects only Skeletons whose typed roles are available
on that carrier. Full-Top200 support remains reported, but is not required for
engineering reachability on a dynamic observed intersection.

## Boundaries

This decision does not authorize a market search, reward evaluation, Alpha
claim, OOS, challenge, recent, May-stress, forward, promotion, latent priority,
relational training, cross-sprint adaptive memory, missing-value zero fill, or
state import from V1/V1.1/V1.2.

Instrument-identity and PIT-universe holds remain research blockers.
Liquidation remains quarantined. Top50 OI/mark raw data remains inventory-only
until a separately verified compact materializer exists.

No new AST, compiler, evaluator, database, Graph layer, scheduler, or
checkpoint service is introduced.

## Consequences

Future search authorization can distinguish:

- source present;
- field materialized;
- typed/compiled/matched reachable;
- dynamically evaluable on observed coordinates;
- research admitted.

No layer may infer the next one. Search policy work may resume only after the
intended carrier has an explicit reachability proof and separate authorization.
