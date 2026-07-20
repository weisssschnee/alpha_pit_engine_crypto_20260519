# Crypto Policy Upgrade PC2 Acceleration Audit

Date: 2026-07-20 Asia/Hong_Kong

## Outcome

The policy-upgrade process did not crash or exhaust memory. All 20 lanes and
2,560 adaptive pairs completed. The producer returned `1` after a qualification
gate treated two known coverage diagnostics from the lite evolutionary control
as a global implementation failure.

PC2 is not pagefile-bound. Windows already manages a 31,234 MiB
`C:\pagefile.sys`; current usage was 879 MiB and the boot peak was 3,515 MiB.
The pagefile remains system-managed. C: and D: are partitions on the same 1 TB
NVMe device, so moving the pagefile would not improve I/O.

## Runtime and packages

- host: `DESKTOP-A2H3A2G`
- CPU: Intel Core i7-12700, 12 physical cores / 20 logical processors
- physical memory: 34,116,284,416 bytes
- Python: `D:\HermesWorker\workspace\crypto_line\.venv_b251733\Scripts\python.exe`
- Python version: 3.11.9
- installed and used: NumPy 2.1.3, pandas 2.2.3, PyArrow 19.0.1,
  psutil 7.0.0, SciPy 1.17.1
- absent: Numba, Bottleneck, NumExpr, Polars, Joblib, scikit-learn

Installed packages are not counted as acceleration unless the active path calls
them. PyArrow writes the final Parquet evidence; the evaluator itself remains a
NumPy/pandas single-threaded process per lane.

## Active hot path

- eight `ProcessPoolExecutor` workers run one lane each;
- each worker opens the pinned NumPy memmap store independently;
- each pair repeatedly slices/converts the development block and constructs
  calendar groupings;
- expression materialization has a candidate-local cache;
- every pair calls `gc.collect()` and Windows `EmptyWorkingSet`, evicting useful
  memmap pages and increasing page faults/I/O;
- pandas rolling median, quantile, and rank operations are single-threaded;
- `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, and `NUMEXPR_NUM_THREADS` are fixed at 1.

The observed low total CPU was therefore expected: eight single-threaded workers
on 20 logical processors, plus deliberate working-set eviction. Peak worker RSS
was only 646,377,472 bytes against a 2 GiB limit; wall time was 6,844 seconds
against a 14,400-second limit.

A separate one-off remote status probe, not the Crypto producer, later expanded
live-log arrays and failed while Windows PowerShell 5.1 serialized them with
`ConvertTo-Json -Depth 8`. It caused the observed high-memory event after the
producer had finished. Future monitoring must use bounded log tails and scalar
status fields; a local SSH timeout alone is not a remote-process timeout.

## Changes applied

- retained the existing system-managed pagefile;
- switched PC2 from Balanced to the built-in High Performance power plan;
- retained the exact raw-cache, evaluator, policy, mapping, cost, and sealed-data
  semantics;
- recovered the complete producer evidence instead of rerunning 2,560 pairs.
- retired the unbounded live-log JSON probe pattern in favor of the bounded
  `pc2_status_33d44a5.ps1` status entry.

## Deliberately not applied

- no fixed-size or D:-hosted pagefile;
- no blind worker increase during the completed evidence run;
- no replacement of pandas rolling logic with JIT or approximate kernels;
- no selector/cache key relaxation and no read of report-only or sealed roles.

## Safe next-launch contract

- `use_fast_context`: not implemented; do not claim it is active;
- `global_worker_limit`: keep 8 until memory-trim parity is measured, then test
  10 and 12 workers with the same eight-pair expressions;
- `successive_halving`: not used;
- cache identity must continue to bind expression, evaluator/source SHA, raw
  cache bundle, field/compiler contract, development block, delay, mapping, and
  cost settings;
- first acceleration change: move `EmptyWorkingSet`/full GC from every pair to
  a measured RSS threshold or lane boundary, with exact candidate, reward,
  weight-hash, and replay parity before adoption;
- add atomic per-lane checkpoints before any future multi-wave run so a machine
  failure cannot discard completed lanes.

This audit changes execution guidance only. It creates no alpha, OOS, forward,
challenge, or promotion authority.
