# CRYPTO A7LS-26 Numeric Wave Launch (20260608)

## Decision

`PASS_A7LS26_NUMERIC_WAVE_LAUNCHED_ON_COMPANY_MACHINE`

## Scope

- upstream materialization: A7LS25
- materialized activity-ok input rows: 33,971
- numeric queue rows: 4,096
- shard count: 64
- rows per shard: 64
- company concurrency: 2
- semantic pairs: 12
- motifs: 17
- skeletons: 89

## Runtime

- remote root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26_numeric_wave_20260608`
- runner: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607\run_a7ls26_numeric_wave_remote.ps1`
- status script: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26_numeric_wave_20260608\status_a7ls26_remote.ps1`

## Current Status At Launch Check

- queue built successfully
- only one active A7LS26 worker set retained
- duplicate worker set from a manual retry was stopped
- active workers: 2 Python numeric processes
- active shards at check: `a7ls26_num_s000`, `a7ls26_num_s001`

## Boundaries

- May is not used.
- This is numeric replay, not alpha proof.
- Search, shadow, paper, and live remain blocked.

## Next

After completion:

1. Pull remote `a7ls26_numeric_wave_summary.json`.
2. Aggregate shard manifests and selected queues.
3. Produce A7LS27 numeric aggregate / clue arbitration.
