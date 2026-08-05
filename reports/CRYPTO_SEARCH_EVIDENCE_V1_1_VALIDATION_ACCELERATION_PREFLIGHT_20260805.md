# Crypto Search Evidence V1.1 Validation — PC2 Acceleration Preflight

- Scope: one exact 49-candidate, no-feedback development validation; no candidate generation or repeated market canary.
- Host: PC2 (`DESKTOP-A2H3A2G`), 20 logical CPUs, 31.77 GiB physical RAM.
- Available before launch: 20.78 GiB RAM, 23.72 GiB virtual memory, C: 369.18 GiB free, D: 1.94 GiB free.
- Contention: zero Python processes and zero active crypto-search processes at preflight.
- Runtime: retained `D:\HermesWorker\python311\python.exe` with the retained overlay; no dependency installation.
- Active packages: NumPy 2.4.6, pandas 3.0.3, PyArrow 24.0.0. Optional Numba/Bottleneck/NumExpr/Polars/joblib/scikit-learn accelerators are absent and are not installed because the active path is the existing NumPy/PyArrow process evaluator.
- Reused caches: aligned 115-field carrier 600,048,231 bytes; Binance target 10,170,182 bytes. Both metadata files are present.
- Hot path: existing `ProcessPoolExecutor`, one read-only carrier/target store per worker, retained typed compiler, existing pair evaluator, and existing economic-path/provenance projection.
- Worker contract: 10 workers; 8 only after an in-run `MemoryError`; 12 forbidden.
- Storage decision: new workspace/runtime on C. D is not used for heavy output.
- Budget: exactly 49 frozen candidates, one 49-row atomic checkpoint, one hour wall limit, minimum 128 pair evaluations/hour.
- Waste controls: no new proposal generation, no warm-up market canary, no backfill, no successful-candidate replay, no reseed/tuning/restart/rescue run, and no local heavy compute.

Decision: `PASS_READY_FOR_ONE_EXACT_PC2_VALIDATION`.
