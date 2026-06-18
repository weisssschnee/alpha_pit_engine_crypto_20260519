# Crypto Verified Core 20260618

This directory is a curated component pack for the crypto alpha pipeline.
It does not claim alpha proof. It separates reusable, evidence-backed system
components from components that remain provisional or missing.

## Scope

Layers audited:

- data and data guards
- formula / feature algebra
- search-space construction and AST representation
- fast proxy evaluation
- strict reward evaluation
- sharded aggregation
- regime attribution
- governance registry

## Classification

- `PASS`: component has current code evidence and a recent successful use.
- `PROVISIONAL_PASS`: usable for controlled research, but still has known gaps.
- `HOLD`: do not use as a source of truth for search until the listed gaps are fixed.
- `MISSING`: expected system component is not present as a verified crypto core.

## Boundary

The verified core excludes runtime outputs, large data files, and ad hoc company
machine launchers. Runtime evidence is referenced in `component_registry.csv`.

Current key finding: the reward and proxy layers have usable components, but the
crypto repo does not yet have a verified integrated CEM/AST/MCTS search kernel
connected to strict reward. Current large-search work is mostly queue generation
plus proxy/reward sharding.

