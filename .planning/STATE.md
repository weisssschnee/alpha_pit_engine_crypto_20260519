# Crypto AlphaFactory Planning State

**Last updated:** 2026-06-30 14:55 Asia/Hong_Kong
**Status:** A7SEARCH5_R2 proxy search and bounded full reward completed; validation/triage next

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

As of the last company-machine check on 2026-06-30 14:27-14:29:

- A7SEARCH5_R2 reports: `128 / 128`
- Missing reports: `0`
- Active shard count: `0`
- Active shards: none
- Supervisor: stopped after completion
- Supervisor task id: `job_20260629_120926_3f21c9`
- Aggregate report: `reports/CRYPTO_A7SEARCH5_MEMORY_ENFORCED_PROXY_R2_AGGREGATE_STATUS_20260630.md`
- Remote aggregate report: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7SEARCH5_MEMORY_ENFORCED_PROXY_R2_AGGREGATE_20260629.md`
- Remote aggregate root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_aggregate_20260629`
- Prior takeover supervisor was stopped after repeated restarts of `s064` and `s067`.
- `s064` and `s067` showed `pyarrow read_table` `MemoryError`; lock-aware supervisor now uses `max_parallel=12`, `min_free_gb_to_start=18`, fresh locks, and max attempt holds.
- Aggregate first failed under direct script execution because `from scripts...` could not resolve `scripts`; rerun with `PYTHONPATH=$Repo` and `python -m scripts.crypto_a7v3s9_proxy_aggregate` succeeded.
- Aggregate decision: `PASS_A7V3S9_PROXY_AGGREGATE_SELECTED`.
- Aggregate counts: `32768` leaderboard rows, `42` strict pass rows, `323` near-miss rows, `0` eval error rows, `2` selected rows, `2` selected unique blueprints.
- Selected pair/motif: `open_interest|positioning` / `safe_div_abs`.
- Boundary: aggregate authorizes bounded full reward only; no alpha proof, shadow, paper, or live.
- No duplicate active shard groups were observed at completion.

## Latest Full Reward State

As of 2026-06-30 14:51:

- Full reward report: `reports/CRYPTO_A7SEARCH5_SELECTED_FULL_REWARD_R3_AGGREGATE_STATUS_20260630.md`
- Remote full reward root: `H:\AlphaFactory_CryptoData_archive\a7search5_selected_full_reward_r3_20260630`
- Remote full reward aggregate root: `H:\AlphaFactory_CryptoData_archive\a7search5_selected_full_reward_r3_aggregate_20260630`
- Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`
- Input proxy-selected candidates: `2`
- Reward rows: `8`
- Split metric rows: `240`
- Eval error rows: `0`
- Accepted rows: `3`
- Accepted unique blueprints: `2`
- Accepted pair/motif: `open_interest|positioning` / `safe_div_abs`
- Accepted horizons: `4h` and `8h`
- Boundary: authorizes validation/triage only, not alpha proof or deployment.
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
