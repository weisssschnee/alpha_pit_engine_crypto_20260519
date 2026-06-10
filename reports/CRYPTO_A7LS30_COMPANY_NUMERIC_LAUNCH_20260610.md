# CRYPTO A7LS30 Company Numeric Launch 20260610

## Decision

`RUNNING_A7LS30_PRODUCTIVE_NUMERIC_WAVE`

A7LS30 was launched on the company machine after the A7LS30 queue and field gate passed locally.

## Launch

- task_id: `job_20260610_092408_f72cb4`
- remote_run_root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_numeric_wave_20260610`
- remote_queue: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_numeric_wave_20260610\a7ls30_productive_followup_queue.csv`
- queue_rows: 8192
- rows_per_shard: 512
- shard_count: 16
- launch_concurrency: 4
- field_gate_decision: `PASS_A7LS_FIELD_GATE_CURRENT_QUEUE_CLEAN`

## Initial Verification

At launch verification, `a7ls30_num_s000` through `a7ls30_num_s003` had started. The first shard log showed the runner loading 96 symbols and evaluating 512 blueprints over 9241 selected timestamps. Four heavy Python workers were active, each roughly 0.75-0.93 GB working set, plus lightweight wrapper processes.

## Boundary

```text
This launches numeric probes only.
It does not authorize formula search, alpha proof, shadow, paper, or live execution.
If any shard fails with ArrayMemoryError, retry only missing shards at lower concurrency.
```
