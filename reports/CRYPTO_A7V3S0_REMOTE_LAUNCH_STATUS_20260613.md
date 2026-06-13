# CRYPTO A7V3S0 Remote Launch Status 20260613

## Decision

`RUNNING_A7V3S0_REWARD_SHARDED_GATE`

A7V3S0 search contract was synchronized to the company machine, the v3 patch-age panel was rebuilt on the company machine, and a 64-row remote smoke passed. The initial 4-concurrency materialization wave was stopped after shard metrics showed MemoryError-driven eval failures under concurrent company-machine load. A replacement 2-concurrency materialization wave completed cleanly. A 1,024-row diversified reward prequeue was built from the 60,640 activity-ok materialized candidates, and a sharded reward gate is now running.

This authorizes only numeric materialization and downstream reward-gate follow-up. It does not authorize alpha proof, shadow, paper, or live use.

## Git / Contract

- launch contract commit: `5a6fbe3`
- remote data sync blocker record: `4e31571`
- timestamp normalization fix: `bad09b9`
- queue rows: `65536`
- shards: `64`
- rows per shard: `1024`
- initial launcher concurrency: `4`
- initial company task id: `job_20260613_031429_d99544`
- replacement launcher concurrency: `2`
- replacement company task id: `job_20260613_033314_a7c523`
- reward sharded task id: `job_20260613_122208_f4fd42`

## Company Sync

Remote paths now present:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613\a7v3s0_large_search_queue.csv
D:\HermesWorker\runtime\run_a7v3s0_company_materialization.ps1
```

Remote v3 rebuild output:

```text
PASS_A7DATA_RECENT_PATCH_MERGED_PANEL_READY_FOR_CONTROLLED_EXPERIMENT
PATCH_FILES=498
V3_FILES=498
QUEUE_EXISTS=True
RUNNER_EXISTS=True
```

The remote builder initially exposed mixed timezone handling between local and remote CSV/parquet inputs. That was fixed by normalizing timestamps with `utc=True` and removing timezone metadata before merge comparisons.

## Remote Smoke

Remote smoke command:

```powershell
powershell -ExecutionPolicy Bypass -File D:\HermesWorker\runtime\a7v3s0_remote_smoke_20260613.ps1
```

Smoke result:

```text
decision: PASS_A7LS17_SHARD_MATERIALIZATION_COMPLETE
queue_rows: 64
eval_success_count: 64
eval_failure_count: 0
activity_ok_count: 59
activity_ok_rate: 0.921875
field_count: 35
operator_count: 11
semantic_pair_count: 39
uses_may: false
```

The smoke produced only known numpy empty-slice warnings from sparse cross-sectional samples; these did not cause eval failures.

## Initial Detached Launch

Launch command:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action start-detached `
  -DetachedCommand "powershell -ExecutionPolicy Bypass -File D:\HermesWorker\runtime\run_a7v3s0_company_materialization.ps1"
```

Detached task:

```text
TASK_ID=job_20260613_031429_d99544
STATUS=D:\HermesWorker\runtime\jobs\job_20260613_031429_d99544.status.json
LOG=D:\HermesWorker\runtime\jobs\job_20260613_031429_d99544.log
```

Initial launcher log:

```text
BEGIN 2026-06-13T03:14:16
[A7V3S0] start a7v3s0_s000 rows=0:1024
[A7V3S0] start a7v3s0_s001 rows=1024:2048
[A7V3S0] start a7v3s0_s002 rows=2048:3072
[A7V3S0] start a7v3s0_s003 rows=3072:4096
```

The initial 4-concurrency wave was stopped and preserved as failure evidence. It completed 8 shard manifests before intervention; shard `a7v3s0_s000` had `eval_success_count=671`, `eval_failure_count=353`, and `344` of those failures were `MemoryError((96, 4096), dtype('float64'))`. This was a resource allocation failure caused by the concurrency setting and concurrent company-machine load, not an alpha result and not a successful materialization wave.

## Replacement C2 Launch

Replacement launch command:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action start-detached `
  -DetachedCommand "powershell -ExecutionPolicy Bypass -File D:\HermesWorker\runtime\a7v3s0_company_materialization_c2_20260613.ps1"
```

Replacement detached task:

```text
TASK_ID=job_20260613_033314_a7c523
STATUS=D:\HermesWorker\runtime\jobs\job_20260613_033314_a7c523.status.json
LOG=D:\HermesWorker\runtime\jobs\job_20260613_033314_a7c523.log
RUNTIME=D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_20260613
```

First C2 shard checks:

```text
a7v3s0_c2_s000: rows=1024, eval_success=1024, eval_failure=0, activity_ok=925, elapsed=248.01s
a7v3s0_c2_s001: rows=1024, eval_success=1024, eval_failure=0, activity_ok=949, elapsed=244.07s
```

This confirms the replacement wave is materially cleaner than the initial 4-concurrency wave. Keep concurrency at `2` unless the company machine becomes much freer and a new canary proves no MemoryError.

Final C2 materialization aggregate:

```text
decision: PASS_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_READY_FOR_A7LS18
completed_shards: 64 / 64
total_rows: 65,536
eval_success_count: 65,536
eval_failure_count: 0
activity_ok_count: 60,640
activity_ok_rate: 0.925293
lane_count: 4
semantic_pair_count: 78
motif_count: 10
```

## Reward Gate

Reward prequeue:

```text
decision: PASS_A7V3S0_REWARD_PREQUEUE_READY
input_activity_ok_rows: 60,640
selected_rows: 1,024
lane_count: 4
semantic_pair_count: 46
motif_count: 9
skeleton_count: 865
```

The first single-process reward diagnostic showed that reward evaluation can be blocked by slow candidates, so the full 1,024-row gate was switched to a 64-shard design:

```text
runtime: D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_reward_sharded_720h_r2_20260613
shards: 64
rows_per_shard: 16
concurrency: 2
hours_per_split: 720
cost_bps: 5.0
per_shard_timeout_seconds: 1800
task_id: job_20260613_122208_f4fd42
```

The earlier bad sharded run root `a7v3s0_reward_sharded_720h_20260613` is invalid because its generated PowerShell shard scripts lost line-continuation markers and failed immediately. Use only the `r2` run root.

## Runtime Monitoring Notes

At launch, the company machine was not idle; unrelated 1-minute sidecar evaluation processes were also running. The initial 4-concurrency run drove free memory too low and produced MemoryError eval failures. After switching to C2, first-batch eval failures dropped to zero while memory remained in a safer range.

Do not use the initial 4-concurrency runtime as a result source. It is diagnostic evidence for sizing. Use only the C2 runtime for downstream aggregation and strict reward-gate follow-up.

## Next Check

For reward gate monitoring, use:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_122208_f4fd42

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-tail `
  -TaskId job_20260613_122208_f4fd42 `
  -TailLines 120
```

For materialization records, use:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_033314_a7c523

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-tail `
  -TaskId job_20260613_033314_a7c523 `
  -TailLines 120
```

Then count completed shard manifests:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action exec `
  -Command "powershell -NoProfile -Command ""(Get-ChildItem 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_20260613\shards' -Filter a7ls17_manifest.json -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count"""
```

When all 64 manifests are present, aggregate materialized results and run the strict A7REWARD gate. Do not read raw materialization hits as alpha results.
