# Crypto AlphaFactory Planning State

**Last updated:** 2026-06-29 10:45 Asia/Hong_Kong
**Status:** active search running; system hardening phase planned

## Current Source Of Truth

- Main branch is clean and aligned with `origin/main` at `1b13a43 fix search memory caps per shard`.
- Current durable planning output: `.planning/phases/01-crypto-search-hardening/01-PLAN.md`.
- Active remote run root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_20260628`.
- Active aggregate target: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_aggregate_20260629`.

## Confirmed System Components

- Field/search memory registry exists and is machine-readable:
  `runtime/a7mem0_search_memory_registry_20260628/a7mem0_next_search_prior.json`.
- Search generator is fail-closed on memory enforcement by default.
- Per-shard memory caps were fixed in commit `1b13a43`.
- A7MEM-1 smoke passed for duplicate expression rejection, skeleton caps, and prior detection.
- A7SEARCH4 completed 128/128 shards and produced 42 strict rows from 32,768 leaderboard rows.
- Reward validation is strict-gated and rejects high headline Sortino if train/OOS/control floors fail.

## Active Search State

As of the last company-machine check on 2026-06-29 10:33-10:36:

- A7SEARCH5_R2 reports: `40 / 128`
- Active shard count: `18`
- Active shards: `s040` through `s057`
- Supervisor: `D:\HermesWorker\runtime\a7search5_r2_takeover_20260629.ps1`
- CPU delta check: all 18 child Python workers are consuming CPU.
- Aggregate report: not yet generated.
- Current warnings: NumPy all-NaN / empty-slice warnings in invalid candidate branches, no fatal traceback observed.

## Important Boundaries

Allowed:

- Continue memory-enforced proxy search.
- Aggregate once all shards complete.
- Run strict reward gate and dedupe/cluster review after aggregate.
- Harden data/regime/reward/search plumbing.

Blocked:

- Alpha proof.
- Shadow, paper, or live.
- Treating proxy search output as production alpha.
- Disabling memory enforcement except for explicit legacy reproduction.

