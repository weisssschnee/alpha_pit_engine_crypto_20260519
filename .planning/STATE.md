# Crypto AlphaFactory Planning State

**Last updated:** 2026-06-29 21:28 Asia/Hong_Kong
**Status:** active search running; system hardening phase planned

## Current Source Of Truth

- Main branch is clean and aligned with `origin/main` at `1b13a43 fix search memory caps per shard`.
- Project-level plan: `.planning/PROJECT.md`.
- Project roadmap: `.planning/ROADMAP.md`.
- Current durable planning output: `.planning/phases/01-crypto-search-hardening/01-PLAN.md`.
- Active remote run root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_20260628`.
- Active aggregate target: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_aggregate_20260629`.

## Confirmed System Components

- Prior governance and infrastructure phases are already passed: A7PM-0/1/2/3, A7AI-F0/F1/F2/F3/F4, A7AA-0/1/2/3/4, A7MEM-0/1, and A7SEARCH4.
- Field/search memory registry exists and is machine-readable:
  `runtime/a7mem0_search_memory_registry_20260628/a7mem0_next_search_prior.json`.
- Search generator is fail-closed on memory enforcement by default.
- Per-shard memory caps were fixed in commit `1b13a43`.
- A7MEM-1 smoke passed for duplicate expression rejection, skeleton caps, and prior detection.
- A7SEARCH4 completed 128/128 shards and produced 42 strict rows from 32,768 leaderboard rows.
- Reward validation is strict-gated and rejects high headline Sortino if train/OOS/control floors fail.

## Active Search State

As of the last company-machine check on 2026-06-29 21:22-21:26:

- A7SEARCH5_R2 reports: `72 / 128`
- Active shard count: `10`
- Active shards: `s072` through `s081`
- Supervisor: `D:\HermesWorker\runtime\a7search5_r2_lockaware_supervisor_20260629.ps1`
- Supervisor task id: `job_20260629_120926_3f21c9`
- CPU delta check confirmed active workers are consuming CPU.
- Aggregate report: not yet generated.
- Prior takeover supervisor was stopped after repeated restarts of `s064` and `s067`.
- `s064` and `s067` showed `pyarrow read_table` `MemoryError`; lock-aware supervisor now uses `max_parallel=12`, `min_free_gb_to_start=18`, fresh locks, and max attempt holds.
- Current memory guard status: free memory was `14.6GB` to `15.4GB`, so no new shards are started until memory recovers.
- Duplicate old worker groups for `s073` and `s074` were found and stopped; current `s073`/`s074` each have one lock-aware worker group.
- Current warnings: NumPy all-NaN / empty-slice warnings in invalid candidate branches; confirmed fatal issue so far is memory pressure, not formula traceback.

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
