# CRYPTO A7RAW0 Company Numeric Launch 20260610

## Decision

`RUNNING_A7RAW0_LIGHT_GOVERNED_NUMERIC_WAVE`

A7RAW0 was launched on the company machine after the large-space queue and field gate passed locally.

## Launch

- task_id: `job_20260610_173358_727a0e`
- remote_run_root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7raw0_light_governed_numeric_wave_20260610`
- remote_queue: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7raw0_light_governed_numeric_wave_20260610\a7raw0_light_governed_queue.csv`
- queue_rows: 16384
- rows_per_shard: 512
- shard_count: 32
- launch_concurrency: 4
- field_gate_decision: `PASS_A7LS_FIELD_GATE_CURRENT_QUEUE_CLEAN`

## Initial Verification

At launch verification, `a7raw0_num_s000` through `a7raw0_num_s003` had started. Four heavy Python workers were active at roughly 0.74-0.76 GB working set each, plus lightweight wrapper processes.

## Boundary

```text
This launches numeric probes only.
It does not authorize formula search, alpha proof, shadow, paper, or live execution.
If any shard fails with ArrayMemoryError, retry only missing shards at lower concurrency.
```
