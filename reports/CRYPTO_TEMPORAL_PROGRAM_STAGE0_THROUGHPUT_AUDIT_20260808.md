# Crypto Temporal Program Stage-0 Throughput Audit — 2026-08-08

## Decision

`SOURCE_REPAIR_COMPLETE_NO_MARKET_RUN`

The Stage-0 producer configured ten worker processes but submitted at most five paired tasks per batch. A paired task already evaluates both the static and temporal representations sequentially inside one worker, so dividing worker count by two left half of the process pool unused. The throughput floor remains unchanged because `2,777.7778 strict/hour` is the frozen `50,000 / 18 hours` end-to-end requirement.

## Recomputed baseline

Authoritative runtime: `runtime/crypto_temporal_mechanism_program_v1_20260808r1`

| Measure | Recomputed value |
|---|---:|
| Strict rows | 2,000 |
| Successful pair tasks | 1,000 |
| Submitted pair tasks | 1,755 |
| Producer batches | 354 |
| Configured workers | 10 |
| Observed worker PIDs | 5 |
| Maximum tasks submitted in one batch | 5 |
| Active wall seconds | 4,115.3155 |
| Observed strict/hour | 1,749.5621 |
| Pair process CPU seconds | 4,403.6406 |
| Sum of pair-task wall seconds | 9,873.0250 |
| Effective concurrent pair tasks | 2.3991 |
| Process CPU saturation vs five observed workers | 21.40% |
| Process CPU saturation vs ten configured workers | 10.70% |
| Maximum worker RSS | 0.283 GiB |
| Maximum worker private bytes | 1.677 GiB |

The old artifact now produces `producer_batch_worker_capacity_underfilled` when independently checked against its declared ten-worker capacity.

## Active acceleration inventory

Exact interpreter: `G:\PythonProject\.venv\Scripts\python.exe`, Python 3.11.9.

| Package | Version | Active role |
|---|---:|---|
| numpy | 2.1.3 | array evaluation and portfolio mathematics |
| pandas | 2.2.3 | ledgers, checkpoints, and aggregation |
| pyarrow | 19.0.1 | Parquet artifacts |
| numba | 0.64.0 | installed; not used by this hot path |
| bottleneck | 1.6.0 | installed; indirect pandas/numpy support only |
| numexpr | 2.14.1 | installed; no explicit temporal hot-path call |
| polars | 1.41.0 | installed; not used by this hot path |
| joblib | 1.4.2 | installed; not used by this hot path |
| scikit-learn | 1.6.1 | installed; not used by this hot path |

The active path uses `ProcessPoolExecutor`, one initialized `RawPanelStore` and typed registry per worker, numpy-based materialization, and a candidate-local expression cache shared across primary and matched controls. No dependency installation or runtime optimization was performed.

## Applied repair

- Stage-0 batch capacity is now exactly the configured worker-process count: 10 normally and 8 only after the existing fail-closed memory fallback.
- Each pair task remains unchanged and still evaluates exactly two strict representations with the same target, data, PIT, mapping, cost, reward, controls, and evaluator.
- Producer status now separates configured processes, paired-task capacity, and strict-row capacity.
- Final artifacts record initial/final configured workers, observed worker PIDs, maximum submitted tasks, and total submitted tasks.
- The independent checker now rejects systematic half-pool submission and reconciles recorded worker accounting with process evidence.
- A deterministic scheduling test proves that changing batch capacity from 5 to 10 preserves the Stage-0 lane proposal sequence while reducing a rejection-free 1,000-pair checkpoint from 200 to 100 batches.

## Deliberately not applied

- No market search, replay, validation, OOS, or holdout read.
- No worker count increase beyond the frozen 10/8 contract.
- No change to throughput floor, budget, seeds, target, mapping, cost, reward, search policy, AST, compiler, or evaluator.
- No rolling refill scheduler: completion-driven refill could make lane eligibility depend on nondeterministic worker completion order. Fixed full-capacity batches retain deterministic replay.
- No claimed speedup: the repair removes a proven capacity defect; realized throughput requires a separately authorized future run.

## Verification

- Focused temporal program tests: `20 passed`.
- Full suite: `510 passed, 1 warning` in `153.14s`; the warning is the existing
  NumPy degrees-of-freedom warning in
  `test_future_volatility_uses_only_post_execution_returns`.
- Historical artifact recomputation: 5 observed workers, maximum batch submission 5, underfill detected.

## Future launch contract

Any separately authorized run must keep the frozen 10-worker default and 8-worker memory fallback, require a full ten-task batch whenever at least ten tasks are available, retain end-to-end throughput measurement, and fail closed if process evidence reports underfilled capacity. This repair does not authorize such a run.
