# Crypto Temporal Adaptive Broad V1 acceleration preflight

## Launch envelope

- PC2 Python: `C:\HermesWorker\workspace\.venv\Scripts\python.exe`
- Search surface: existing aligned 115-field carrier, 4h Binance USD-M target
- Active families: P1 position-state change and P4 multiscale state-transition routing
- Arms: fresh-state typed random, typed CEM and typed Evolution
- Maximum: 50,000 strict evaluations, 250,000 raw attempts, 18 active hours
- Checkpoints: 2,000 strict; continuation decisions at 10k, 20k, 30k and 40k; terminal at 50k
- Workers: 10; fail-closed in-run fallback to 8 only on memory error; 12 forbidden
- Throughput floor: 2,777.7778 strict/hour after the first immutable checkpoint

## Measured capacity reused

The immediately preceding 10,000-strict PC2 Stage-0 run used the same carrier,
compiler, evaluator, mapping, cost and paired-task worker context. It completed at
3,959.8469 strict/hour with all ten workers and ten submitted tasks per full batch,
zero system errors and no memory fallback. The mapping hot path had already been
repaired with exact before/after weight and provenance parity. This exceeds the new
campaign floor by about 42.6%; no additional runtime optimization or dependency is
justified before launch.

## Runtime acceleration and safety

- Existing process-pool initialization shares immutable input/cache identities per worker.
- Proposal batches submit up to the configured worker count and retain process evidence.
- Exact and behavior dedupe remain enabled; the raw-attempt cap is unchanged.
- CEM and Evolution use campaign-local state only; no prior candidates, Archive,
  distribution, population or policy state is imported.
- P2/P3 receive only the existing 10% diagnostic slice of the random arm; adaptive
  comparisons exclude those inactive-family diagnostics from the random control.
- No approximate evaluator, target, mapping, reward, cost or search-semantic shortcut is used.

## Stop rules

Stop at the first system error, throughput-floor failure, memory failure at eight
workers, raw-attempt limit, active-wall limit, frozen adaptive gate failure, or
50,000 strict evaluations. Do not restart, reseed, tune or rescue rerun.
