# Crypto AlphaFactory Planning State

**Last updated:** 2026-06-30 16:22 Asia/Hong_Kong
**Status:** A7SEARCH6 memory-seeded mechanism proxy search running; Phase 5 system rectification plan created

## Current Source Of Truth

- Local main has unpushed commits beyond `origin/main` because GitHub HTTPS push is currently failing with connection reset / port 443 errors.
- Local latest commit before this planning update: `a365155 add a7search6 mechanism seed proxy search`.
- Remote `origin/main` remains at `b158ce4 add a7search5 validation pack` until push succeeds.
- Project-level plan: `.planning/PROJECT.md`.
- Project roadmap: `.planning/ROADMAP.md`.
- Current durable planning output: `.planning/phases/01-crypto-search-hardening/01-PLAN.md`.
- System rectification planning output: `.planning/phases/05-verified-core-extraction-or-new-repo-decision/05-PLAN.md`.
- Active remote run root: `H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630`.
- Active aggregate target: `H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_aggregate_20260630`.

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

## Latest Validation Pack State

As of 2026-06-30 15:42:

- Validation report: `reports/CRYPTO_A7SEARCH5_VALIDATION_PACK_20260630.md`
- Remote validation root: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630`
- Remote validation manifest: `H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630\a7search5_validation_manifest.json`
- Local manifest mirror: `runtime/a7search5_validation_pack_manifest_20260630.json`
- Decision: `HOLD_A7SEARCH5_CANONICAL_NOT_UNIQUE_INCREMENT`
- Queue rows: `16`
- Leaderboard rows: `64`
- Split metric rows: `1920`
- Eval error rows: `0`
- Accepted rows: `11`
- Accepted unique blueprints: `6`
- Canonical accepted rows: `2`
- Single-leg accepted rows: `0`
- Operator-ablation accepted rows: `4`
- Interpretation: the accepted OI value / top-account positioning structure is not explained by single-leg OI or positioning alone, but `SafeDiv(ZScore(OI),CSRank(positioning))` without `Abs` also passes. Treat the signal as a broader OI/positioning relative-scaling mechanism, not as a unique `Abs(SafeDiv)` discovery.
- Boundary: this authorizes memory-seed triage and dedupe/neutralization follow-up only, not alpha proof or deployment.

## Active A7SEARCH6 State

As of 2026-06-30 15:54-16:00:

- Prepare report: `reports/CRYPTO_A7SEARCH6_MECHANISM_MEMORY_SEED_PROXY_CONTRACT_20260630.md`
- Local prepare manifest: `runtime/a7search6_prepare_manifest_20260630.json`
- Remote run root: `H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630`
- Supervisor: `H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630\a7search6_proxy_supervisor.ps1`
- Detached task id: `job_20260630_155424_765773`
- Booster task id: `job_20260630_160107_15cb00`
- Second booster task id: `job_20260630_160408_46f4d8`
- Decision: `PASS_A7SEARCH6_MECHANISM_QUEUE_READY`
- Queue rows: `65,536`
- Shards: `128` x `512`
- Semantic pairs: `13`
- Motifs: `19`
- Skeletons: `1,165`
- Lanes:
  - `adjacent_mechanism_cross`: `30,866`
  - `validated_oi_positioning_scale`: `12,288`
  - `regime_conditioned_mechanism`: `12,142`
  - `operator_ablation_surface`: `10,240`
- Memory enforcement accepted rows: `65,536`; rejected attempts: `202,931`.
- Company memory status at startup: total physical memory about `31.6GB`, free physical memory about `13.7GB` after first workers started.
- Active workers at startup: `4` proxy shards, with supervisor configured as `max_parallel=12`, `min_free_gb=16`.
- Booster supervisor was added at 2026-06-30 16:01 to avoid underutilization. It uses directory-lock skipping, starts only shards without an existing shard directory, and adds shards `s004-s007`.
- Second booster was added at 2026-06-30 16:04 using the same directory-lock skipping and adds shards `s008-s011`.
- Current effective workers after boosters: about `12` proxy workers; free physical memory about `9.7GB`.
- Do not add more workers unless free physical memory remains above `8GB` after sustained progress; the company machine has about `31.6GB` total physical memory.
- Boundary: A7SEARCH6 is proxy-only. If proxy aggregate later passes, it may authorize bounded full reward only.

## Phase 5 System Rectification Plan

As of 2026-06-30 16:22:

- Phase plan: `.planning/phases/05-verified-core-extraction-or-new-repo-decision/05-PLAN.md`
- Roadmap status: Phase 5 is `planned, PLAN.md ready`.
- Purpose: separate verified reusable core components from historical research scripts and decide whether to continue in the existing repo or create a clean successor repo.
- Execution should start with Wave 1 while A7SEARCH6 runs:
  - freeze current system state;
  - build verified-core inventory;
  - define core interface contracts.
- Execution must not stop active A7SEARCH6 workers.
- Stronger execution waves should consume A7SEARCH6 aggregate once available.

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
