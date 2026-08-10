# Crypto Temporal Adaptive Broad Gate — 2026-08-10

## Status

`ENGINE_RUN_INVALID / RESEARCH_HOLD`

The one authorized fresh-state P1/P4 adaptive-only development campaign ran on
PC2 at producer SHA `6450be52f7ff85385ac7de86e1d62819a48c1e66` and task
`job_20260810_101654_098175`. It used the frozen Binance USD-M target, 4h
horizon, dual-axis matched controls, existing mapping, 5 bps cost, 115-field
carrier, four fresh seeds, 10 workers, and initial Random/CEM/Evolution
allocation of 20/40/40. No prior candidate, policy, distribution, population or
Archive state was imported. Validation, OOS and holdout were not read.

## Frozen gate observations

At 10,000 strict rows, Evolution remained active while CEM moved to diagnostic.
At equal count, Evolution produced 217.58 dual-axis net-positive rows and 78.46
2-of-3 replicated rows per 1k, versus Random's 119.09 and 45.63. CEM did not
establish a productivity or breadth increment.

At 20,000, CEM exited. Evolution's density increased to 514.21 dual-axis
net-positive and 290.81 replicated rows per 1k versus Random's 125.35 and 39.55,
but its top positive program-family share rose to 77.79%, so it moved to the
diagnostic floor.

At 30,000, Evolution reached 605 dual-axis net-positive and 393 replicated rows
per 1k versus Random's 126 and 43. Its top-decile reward was `0.9287` versus
`0.0358`, but 86.12% of positive rows came from one program family. Breadth
failed again, Evolution exited, and the frozen gate wrote
`STOP_ALL_ADAPTIVE_ARMS_EXITED`.

These are development diagnostics, not Alpha qualification. CEM did not qualify.
Evolution found a dense but increasingly concentrated pocket and did not qualify
as a broad search policy. No arm is admitted to validation, OOS or promotion.

## Stop-authority failure

After the 30k decision, the producer incorrectly continued as Random-only. The
gate had correctly assigned the stop status to `terminal_reason`, but the next
throughput-qualification call returned `None` and overwrote it unconditionally.
The monitor observed 36,277 strict rows before intervention; checkpoint 017
preserves exactly 36,000 rows. The 6,000 checkpointed rows after the 30k boundary
are excluded from all economic conclusions, and the 277 uncheckpointed rows are
discarded.

The exact producer tree was stopped without restart or rescue. The independent
checker correctly returned `FAIL` because a killed producer cannot create the
normal `final_decision.json` and `run_manifest.json`. The one-time receipt is
consumed as `ENGINE_RUN_INVALID`.

The retained compact evidence bundle is 269,356,189 bytes with SHA256
`EFBDBB7FA492A1AB96D1FC19C32E668584F5F7A2DB2D0E15F9A99A03D56FA542`.
Checkpoint 017 records 36,000 strict rows from 59,084 generation attempts.
The full compact bundle is retained outside Git at
`G:/AlphaFactory_CryptoData/deliveries/crypto_temporal_adaptive_broad_20260810/`;
the repository retains its hash index and the small terminal/gate artifacts.

## Source repair

Checkpoint qualification now preserves any earlier market/gate terminal reason
and applies a throughput terminal reason only when none already exists. A
regression test binds `STOP_ALL_ADAPTIVE_ARMS_EXITED` against a following `None`
qualification result. The focused temporal-program suite passes 32/32.

The repair changes no target, mapping, cost, reward, data, seeds, budget,
optimizer, AST, compiler or evaluator. No rerun is authorized.

## Evidence boundary

- Frozen 10k/20k/30k gate metrics: retained as development diagnostics.
- Post-30k candidate rows: contamination evidence only, excluded from research.
- Runtime validity: invalid because frozen stop authority was not enforced.
- Sealed reads: zero.
- Validation/OOS/promotion/new Arena: not run and not authorized.
