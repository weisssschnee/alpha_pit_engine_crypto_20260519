# Crypto Temporal Representation Successor V1 — Launch Acceleration Audit

Status: `READY_WITH_FIXED_8_WORKER_ENVELOPE`

This audit changes no target, mapping, cost, evaluator, reward, temporal grammar,
or tournament allocation. It only binds the execution envelope for the new
20,000-strict train-only tournament.

## Runtime and package reality

- PC2: `DESKTOP-A2H3A2G`, 20 logical CPUs.
- Official Python: `D:\HermesWorker\workspace\crypto_line\.venv_b251733\Scripts\python.exe`.
- Python 3.11.9; numpy 2.1.3; pandas 2.2.3; pyarrow 19.0.1.
- numba, bottleneck, numexpr, polars, joblib, and sklearn are absent in the
  official environment. None is required or claimed as an active accelerator.
- Active hot path: `ProcessPoolExecutor -> search_engine_v1._worker_evaluate ->
  pair18m.evaluate_pair`. The evaluator uses the existing pandas/numpy path;
  no alternate approximate evaluator is present.

## PC2 resource preflight

- Physical memory: 34,116,284,416 bytes.
- Free physical memory before launch: 22,000,099,328 bytes.
- Free virtual memory: 72,872,808,448 bytes.
- Pagefile: 54,718 MB allocated; 976 MB current; 20,672 MB prior peak.
- Active Python workers: 0.

The prior valid Realization V2 canary used 10 workers and completed 10,000
strict evaluations in 8,796.86 seconds: about 4,092 actual evaluated pairs/hour.
The new tournament requires 20,000 actual evaluations. At that measured rate,
the evaluator-only projection is 4.89 hours. Semantic completion adds proposal
CPU, so the operational wall-clock budget is 10 hours.

## Candidate funnel and scheduler

Each arm is independently refilled until it reaches exactly 10,000 strict rows:

`raw asks -> legal compile -> exact unique -> PAIR_EVALUATED`

- Raw-attempt cap: 100,000 per arm.
- Batch size: 8.
- Worker limit: 8 (40% of logical CPUs, with a larger memory reserve than V2).
- Independent per-arm exact memory, QD state, policies, and archive.
- Five immutable 2,000-strict checkpoints per arm.
- 10,000 total strict is diagnostic only; throughput or yield cannot terminate
  the scientific tournament.

At every checkpoint, record attempts, strict count, exact rejects, proposal
rejects, pair rejects, process CPU, wall time, and actual pairs/hour. If recent
throughput falls below 1,500 actual pairs/hour, treat it as a repairable
engineering fault: inspect proposal serialization, evaluator fill, worker
errors, memory, and pagefile, then resume from the last immutable checkpoint.
Do not change the arm probabilities, raw-attempt cap, evaluator, or budget.

## Acceleration mechanisms actually used

- Existing process-local market store and registry initialization.
- Eight parallel existing strict evaluator workers.
- Bounded proposal refill against per-arm exact memory.
- Immutable checkpoint/resume at 2,000 strict intervals.
- Existing candidate replay and receipt verification before evaluation.

No cache was added because no new cache key could be justified without risking
semantic drift. `use_fast_context`, `global_worker_limit`, and
`successive_halving` are not active on this execution path. No validation/OOS
cache exists or is read.

## Launch contract

- Wall budget: 10 hours; diagnostic throughput floor: 1,500 actual
  `PAIR_EVALUATED`/hour.
- Pair batch / worker limit: 8 / 8.
- Minimum free physical-memory reserve before launch: 8 GiB.
- Raw-attempt ceiling: 100,000 per arm; no cross-arm borrowing.
- No early scientific stop at 10,000 total strict.
- No semantics-changing tuning after launch.
- validation/OOS/holdout/forward/promotion/sealed reads remain zero.
