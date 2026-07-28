# ADR 0013: Explicit Semantic Authority Classes

- Status: Accepted
- Date: 2026-07-28

## Context

`semantic_authorities` already provided one component binding per semantic role, but it did not state whether the binding belonged to formal current architecture or a non-formal development lane. The generated renderer also labelled each node's canonical artifact as `authority`, allowing ACTIVE or qualified experimental components to be overread as formal project authority.

The `multi_paradigm_arena` node additionally referenced `docs/adr/0003-multi-paradigm-frontier-arena-and-artifact-contracts.md`, which is absent from the current tree. The actual ADR 0003 governs the bounded real-data lazy-search canary and must not be aliased to the Arena.

## Decision

1. Every semantic role binding declares `authority_class` as `FORMAL` or `NON_FORMAL`.
2. A node's `authority.path` is a canonical artifact reference, not a formal-authority grant.
3. Generated `active_authority` is derived only from a `FORMAL` role binding.
4. `multi_paradigm_arena` remains an ACTIVE development-only capability and holds the `development_arena` role as `NON_FORMAL`.
5. The Arena's canonical artifact is `alphafactory_crypto/frontier_v2/arena.py`; the nonexistent ADR path is removed.
6. The bounded real-data lazy-search canary, its candidate-admission component, and its mapped-cost evaluator remain `NON_FORMAL` while their nodes remain experimental. Formal gates, boundaries, data surfaces, primitive semantics, portfolio mappings, and source-ingress authorities retain only their existing scoped authority.

## Boundaries

This decision does not authorize a new Arena, candidate evaluation, search budget, OOS access, promotion, forward access, or cross-sprint adaptive memory. It changes classification and authority-reference continuity only.

## Consequences

CURRENT briefs and HTML can distinguish formal role holders from canonical implementations of non-formal development roles. Obsidian may project these bindings through native note properties and backlinks without becoming project authority.
