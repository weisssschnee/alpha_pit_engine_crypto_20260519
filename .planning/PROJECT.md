# Crypto AlphaFactory Project Plan

**Last updated:** 2026-06-29 11:20 Asia/Hong_Kong
**Project status:** research/search system hardening
**Current phase:** Phase 1 - crypto-search-hardening

## Project Objective

Build a reproducible crypto alpha research and search system that can move from raw fields to candidate factors under strict data, reward, leakage, regime, and search-memory controls.

This project is not currently authorized for alpha proof, shadow, paper, or live trading.

## Project-Level Thesis

The project has progressed past basic formula generation. The main bottleneck is now system validity:

- whether data and field contracts are trustworthy;
- whether generated candidates add independent information instead of repeating the same exposure;
- whether reward gates reject headline-metric artifacts;
- whether train, validation, test, recent, stress, lag, shuffle, and control checks are consistently wired;
- whether search memory is used to steer large search without collapsing into narrow repeated motifs.

The current strategy is therefore:

```text
data and field integrity
-> reward and leakage gates
-> search memory
-> large proxy search
-> strict reward
-> cluster / information-source triage
-> next-search memory update
```

## Current System Map

The current system map is split across curated architecture and raw graph files:

- `.planning/graphs/CURRENT_ARCHITECTURE.md` - current active research/search architecture.
- `.planning/graphs/EVOLUTION_MAP.md` - phase evolution and supersession map.
- `.planning/graphs/ARCHITECTURE_BOUNDARY.md` - rules for interpreting architecture versus graphify artifacts.
- `.planning/graphs/graph.json` and `.planning/graphs/graph.html` - raw graphify code/navigation graph, not the current architecture.

## Completed Foundation Phases

The current project plan starts after several governance and infrastructure phases have already passed. These are prerequisites, not future work:

- A7PM-0/1/2/3: project source-of-truth registry, asset taxonomy, candidate lifecycle, and experiment board were built.
- A7AI-F0/F1/F2/F3: field contract ledger, engine enforcement audit, end-to-end role enforcement, and materialization/evaluator parity passed.
- A7AI-F4: response-backed ordinary-alpha seed promotion found at least one seed, but breadth remained limited.
- A7AA-0/1/2/3/4: label/feature response contract, primitive response map, feature role classification, selector rewrite contract, and response handoff passed.
- A7MEM-0/1: search memory registry and generator memory enforcement passed.
- A7SEARCH4: prior 128-shard proxy search completed with strict candidates.

These passes authorize controlled research/search continuation only. They do not authorize alpha proof, deployment, shadow, paper, or live trading.

### Data Layer

Current usable data includes:

- Binance universe 1h research panel used by the current search/reward stack.
- Additional pre-2024 backfill package covering 2023-07 to 2023-12, converted through silver 1m, gold 15m, and gold 1h.
- 2026 recent Binance patch with OI, metrics, funding, mark/index/premium fields.
- OKX x Binance CE overlay for recent cross-exchange experiments.

Open issues:

- The 2023-07 to 2023-12 package is an incremental backfill window, not the full dataset length.
- 1m/15m are available as data, but the current search and reward stack is still primarily wired for 1h.
- Regime/event coverage must be counted explicitly before treating stress tests as sufficient.
- Source trace/checksum audit is still required before any final proof claim.

### Feature And Formula Layer

Confirmed:

- Typed AST / formula generation exists.
- A7MEM search memory is machine-readable.
- Search generator now loads memory prior fail-closed by default.
- Per-shard memory cap bug was fixed.

Open issues:

- Derived-field use must be checked for independent information contribution.
- Repeated skeletons and economically equivalent candidates must be capped.
- Formula simplicity may reflect either true useful low-complexity structure or insufficient feature access; this remains an audit item.

### Reward Layer

Confirmed:

- Strict reward gate rejects candidates with weak train orientation, OOS floor failure, control dominance, shuffle dominance, lag/stale dominance, or invalid stress floors.
- Headline Sortino is not sufficient for acceptance.

Open issues:

- Reward and search are still operationally separated: proxy search produces a candidate surface, strict reward validates selected candidates.
- The project needs explicit reporting of train Sortino alongside validation/test/recent/stress metrics.
- Stress/regime definitions need enough event coverage, not just one fixed post-hoc window.

### Search Layer

Confirmed:

- A7SEARCH4 completed a 128-shard proxy search and produced strict candidates.
- A7SEARCH5_R2 is running as a 65,536-row memory-enforced search.
- Search policies include CEM/AST/UCT-style lanes plus raw/diversity lanes.

Open issues:

- Search memory must be updated from strict pass and rejection memory after each aggregate.
- Search policies must be compared on output quality, not just generated count.
- The project needs a stable project-level record of active run roots, aggregate reports, and next authorized tasks.

## Current Critical Path

1. Finish A7SEARCH5_R2.
2. Aggregate all 128 shards.
3. Apply strict reward and candidate triage.
4. Cluster/dedupe by expression, skeleton, motif, pair, and metric similarity.
5. Audit independent information-source contribution.
6. Update A7MEM with positive and rejection memory.
7. Decide whether the next wave is:
   - broader controlled proxy search,
   - strict reward on selected candidates,
   - data/regime repair,
   - or search algorithm bakeoff.

## Non-Negotiable Gates

- No future leakage.
- No same-bar leakage.
- No missing field contract bypass.
- No unlogged search memory bypass.
- No treating proxy selected rows as accepted candidates.
- No accepting candidates on headline Sortino only.
- No deployment-stage language.

## Durable Planning Files

- `.planning/PROJECT.md` - project-level plan and system thesis.
- `.planning/ROADMAP.md` - phase-level roadmap.
- `.planning/STATE.md` - current status snapshot.
- `.planning/phases/01-crypto-search-hardening/01-PLAN.md` - active phase execution plan.
