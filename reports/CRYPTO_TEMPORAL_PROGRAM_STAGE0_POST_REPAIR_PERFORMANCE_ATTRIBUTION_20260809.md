# Crypto Temporal Program Stage-0 Post-Repair Performance Attribution — 2026-08-09

## Decision

`MAPPING_CONTENTION_AND_LOW_PAIR_YIELD_CONFIRMED_NO_NEW_RUN`

The ten-worker repair is real, but worker count is no longer the primary
bottleneck. The q2 run filled the process pool, while stateful/sparse portfolio
mapping became slower under ten-way concurrency and 43.0% of submitted pair
tasks still terminated without a strict pair. No search, replay, validation,
OOS, reward change, mapping change, evaluator change, or dependency installation
was performed by this audit.

Authoritative inputs:

- post-repair q2: `runtime/crypto_temporal_mechanism_program_v1_20260809q2`
- compatible pre-repair comparator: `runtime/crypto_temporal_mechanism_program_v1_20260808r1`
- active source: `alphafactory_crypto/broad_search/temporal_program_search_v1.py`
- mapping source: `alphafactory_crypto/instrument_capability/mapping.py`
- pair evaluator source: `alphafactory_crypto/broad_search/pair18m.py`

## End-to-end result

| Measure | r1, five submitted tasks/batch | q2, ten submitted tasks/batch | Change |
|---|---:|---:|---:|
| Strict rows | 2,000 | 2,000 | same |
| Submitted pair tasks | 1,755 | 1,755 | same |
| Producer batches | 354 | 180 | -49.2% |
| Active wall seconds | 4,115.2875 | 3,556.4084 | -13.6% |
| Strict/hour | 1,749.5740 | 2,024.5144 | +15.7% |
| Successful-pair process CPU mean | 4.4036 s | 4.4563 s | +1.2% |
| Successful-pair wall mean | 9.8730 s | 16.9738 s | +71.9% |
| Static mapping mean | 3.6362 s | 7.0274 s | +93.3% |
| Temporal mapping mean | 3.1824 s | 4.7932 s | +50.6% |

All ten q2 worker initializers were observed. The producer submitted ten tasks
in 173 of 180 batches; the remaining seven were bounded lane/tail batches. For
the 178 post-initial batches containing at least one successful pair, the
median interval between batch receipts exceeded the slowest successful task in
that batch by only `0.153 s`. Proposal, coordinator, IPC receipt, and per-batch
status work therefore did not consume the missing capacity. The synchronous
batch barrier waited mainly on the slow mapping route.

Doubling concurrency reduced end-to-end wall time, so q2 does not justify an
arbitrary downgrade to five or eight workers. It does show a measured
contention counterfactual: nearly unchanged process CPU work became 71.9%
slower in wall time, concentrated in mapping. Host bandwidth/cache/allocator
telemetry was not recorded, so the exact hardware ceiling is not claimed.

## Candidate funnel

| Funnel edge | Count | Yield |
|---|---:|---:|
| Raw generation attempts | 2,061 | 100.0% |
| Proposal/type rejects | 296 | 14.36% of raw |
| Exact/replay rejects | 10 | 0.49% of raw |
| Submitted pair tasks | 1,755 | 85.15% of raw |
| Pair rejects | 755 | 43.02% of submitted |
| Successful pair tasks | 1,000 | 56.98% of submitted |
| Strict evaluated rows | 2,000 | two per successful pair |
| Behavior families | 1,993 | 99.65% of strict rows |

Pair-reject taxonomy:

| Reason | Count | Share of pair rejects |
|---|---:|---:|
| Primary/control behavior equal | 532 | 70.46% |
| Right-axis control behavior equal | 90 | 11.92% |
| Matched-control support differs | 89 | 11.79% |
| Slope window below legal minimum | 44 | 5.83% |

The two behavior-equality reasons total 622 tasks: 82.38% of pair rejects and
35.44% of all submitted tasks. They are data-dependent post-mapping rejects,
not exact-expression duplicates. Weakening the behavior gate would manufacture
throughput and is forbidden.

Family-local equal-success quotas exposed materially different supply costs:

| Program family | Raw attempts | Pair rejects | Proposal rejects | Successful pairs | Success/raw |
|---|---:|---:|---:|---:|---:|
| P1 position-state change | 301 | 49 | 0 | 250 | 83.06% |
| P2 recent crowding event | 589 | 194 | 144 | 250 | 42.44% |
| P3 flow-shock persistence | 312 | 57 | 0 | 250 | 80.13% |
| P4 multiscale routing | 859 | 455 | 152 | 250 | 29.10% |

P2 and P4 consumed 70.26% of raw attempts and 85.96% of pair rejects to obtain
the same 250 successful pairs per family. This is a real route-specific supply
and mapping burden, not an optimizer conclusion; Stage 0 used typed random only.

At the observed `1,776.5` submitted tasks/hour, the unchanged strict throughput
floor would require a 78.18% successful-pair yield versus the observed 56.98%
(+21.20 percentage points). At the observed yield, task throughput would need
to rise 37.21% to `2,437.5` tasks/hour. Both mapping time and pair yield must be
treated as first-class constraints.

## Successful-pair stage attribution

The following wall timers are summed across the static and temporal evaluation
inside one successful pair:

| Stage | Mean seconds/pair | Share of pair wall |
|---|---:|---:|
| Field reads | 0.0225 | 0.13% |
| DAG materialization | 0.6127 | 3.61% |
| Portfolio mapping | 11.8206 | 69.64% |
| Standalone evaluator | 0.1901 | 1.12% |
| Incremental sleeves | 0.4100 | 2.42% |
| Behavior descriptor | 1.0663 | 6.28% |
| Instrumented stages total | 14.1222 | 83.20% |
| Pair wall total | 16.9738 | 100.0% |

The dominant route is not Parquet I/O or the strict economic waterfall. The
active mapping implementation repeatedly performs train orientation maps,
final primary/control maps, behavior-provenance hashing/statistics, and either
Pandas ranking or Python stateful asset loops. Mean successful-pair wall by
family was:

- P1 / `CROSS_SECTIONAL_ZERO_NET`: `9.274 s`
- P2 / `SPARSE_EVENT_OR_CARRY`: `19.887 s`
- P3 / `TIME_SERIES_DIRECTIONAL_STATEFUL`: `19.383 s`
- P4: mostly sparse, `19.351 s`

The ledger records no worker CPU/wall fields for rejected tasks, so exact
rejected-task stage shares cannot be reconstructed. Source order and the batch
receipts show that behavior-degeneracy and support rejects can occur only after
materialization/mapping work; this audit does not invent a missing per-reject
timer.

## Runtime environment and acceleration reality

The retained q2 PC2 environment was queried read-only using the same Python and
overlay visible in the producer logs:

- interpreter: `D:\HermesWorker\python311\python.exe`, Python 3.11.9
- overlay: `D:\HermesWorker\runtime\crypto_search_py311_overlay_94b016fa\site-packages`

| Package | Version/status | Active role |
|---|---:|---|
| numpy | 2.1.3 | arrays and portfolio mathematics |
| pandas | 2.2.3 | cross-sectional rank, ledgers, aggregation |
| pyarrow | 19.0.1 | Parquet artifacts |
| numba | missing | not active |
| bottleneck | missing | not active |
| numexpr | missing | not active |
| polars | missing | not active |
| joblib | missing | not active |
| scikit-learn | missing | not active |

Active acceleration is limited to a persistent ten-process
`ProcessPoolExecutor`, one initialized `RawPanelStore`/typed registry per worker,
NumPy operations, and candidate-local expression reuse across matched controls.
The active path has no `use_fast_context`, `successive_halving`, JIT, Polars, or
Joblib execution. No new dependency is required to fix the measured Python and
duplicate-provenance hot path.

Successful-task peak RSS was `0.266 GiB` and peak private bytes were
`0.496 GiB`; no memory fallback occurred. Sum of successful-pair CPU divided by
active wall was 1.25 effective cores and sum of successful-pair wall divided by
active wall was 4.77 concurrent successful tasks. These are lower bounds because
the 755 rejected-task timings were discarded. A host saturated-compute fraction
cannot be honestly reconstructed from the retained artifacts.

## Source repair closure

The authorized source-only repair is implemented without changing a mapping
contract, behavior/control gate, evaluator, reward, candidate policy, worker
count, budget, or dependency:

- stateful and sparse per-asset transition logic now uses NumPy masks while
  retaining asset-order transition reasons and the exact state machine;
- repeated numeric identity/support scans for the same provenance array are
  reused inside one mapping receipt;
- future `PAIR_REJECTED` and worker `SYSTEM_ERROR` rows preserve the worker's
  already-computed process CPU, wall time, RSS and private bytes in the existing
  rejected ledger. Historical q2 reject timing remains unknowable.

The frozen local parity input was a `121 x 1,523` signal generated with seed
`20260809`, deterministic missing coordinates, train-orientation source, and
behavior provenance enabled. Every pre/post SHA256 remained exact for weights,
feasibility, transition reasons, diagnostics and provenance across all three
mapping families. Same-process, alternating-order five-run medians were:

| Mapping | Before | After | Local hot-path change |
|---|---:|---:|---:|
| Cross-sectional zero-net | 0.1839 s | 0.1872 s | within local noise |
| Time-series directional stateful | 0.8899 s | 0.2493 s | 3.57x faster |
| Sparse event/carry | 0.7221 s | 0.2752 s | 2.62x faster |

The focused mapping, acceleration-parity and temporal-program suite passed
`47/47`; the full repository suite passed `518/518` with the pre-existing NumPy
degrees-of-freedom warning. The frozen randomized parity test is committed so
future edits must preserve the same behavior identities and reason stream.

This is source and local-benchmark evidence only. It does not prove that PC2
end-to-end throughput now exceeds the frozen floor, and it does not authorize a
market rerun. Any separately authorized performance qualification must retain
ten workers, batch capacity ten, the 8-worker memory fallback only on the
existing fail-closed trigger, the `2,777.7778 strict/hour` floor, and the same
2,000-strict first checkpoint. No worker downgrade, behavior-gate weakening,
reward change, dependency installation, validation, OOS, or search expansion is
implied by this closure.

## PC2 checkpoint-only qualification addendum (2026-08-10)

The separately authorized fresh-state qualification is complete at
`runtime/crypto_temporal_mechanism_program_v1_20260810m1`. It used producer
`49010c89e840320a873accdb27fa15fa6ea9c320`, the unchanged seed, ten workers,
ten submitted tasks per full batch, the same target/mapping/cost/reward and a
hard `2,000` strict cap. It could not continue to the 10,000-strict family gate.

| Measure | q2 before mapping repair | m1 after mapping repair | Change |
|---|---:|---:|---:|
| Strict rows | 2,000 | 2,000 | same |
| Raw attempts | 2,061 | 2,061 | same |
| Active wall seconds | 3,556.4084 | 1,807.2817 | -49.2% |
| Strict/hour | 2,024.4987 | 3,983.8184 | +96.8% |
| Successful-pair wall median | 18.2825 s | 9.2357 s | 1.98x faster |
| Successful-pair mapping median, static plus temporal | 13.8233 s | 3.8058 s | 3.63x faster |

The observed `3,983.8184 strict/hour` exceeds the frozen
`2,777.7778 strict/hour` floor by 43.4%. All ten workers were observed, maximum
submitted tasks per batch was ten, memory fallback was not used, and process
evidence recorded zero system errors. The new rejected ledger retains CPU,
wall and memory fields for 755 worker-side rejects; its median rejected-pair
wall was `4.9104 s`.

PC2 and local independent checkers both pass artifact integrity and run
validity, reconcile all 2,061 attempts, and confirm zero sealed reads. The
one-time receipt is consumed. This qualifies the repaired mapping hot path and
Stage-0 execution capacity only. The cohort had zero matched-positive rows, but
the checkpoint-only contract explicitly forbids a temporal-family, optimizer,
Alpha, validation, OOS, or promotion conclusion from this run.
