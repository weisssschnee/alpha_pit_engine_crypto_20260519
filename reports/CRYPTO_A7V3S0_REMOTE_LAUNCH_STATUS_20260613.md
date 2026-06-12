# CRYPTO A7V3S0 Remote Launch Status 20260613

## Decision

`RUNNING_A7V3S0_COMPANY_MATERIALIZATION_WAVE`

A7V3S0 search contract was synchronized to the company machine, the v3 patch-age panel was rebuilt on the company machine, a 64-row remote smoke passed, and the 64-shard materialization wave was launched as a detached company task.

This authorizes only numeric materialization and downstream reward-gate follow-up. It does not authorize alpha proof, shadow, paper, or live use.

## Git / Contract

- launch contract commit: `5a6fbe3`
- remote data sync blocker record: `4e31571`
- timestamp normalization fix: `bad09b9`
- queue rows: `65536`
- shards: `64`
- rows per shard: `1024`
- launcher concurrency: `4`
- company task id: `job_20260613_031429_d99544`

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

## Detached Launch

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

## Runtime Monitoring Notes

At launch, the company machine was not idle; unrelated 1-minute sidecar evaluation processes were also running. After A7V3S0 started, four crypto materialization workers were active and consuming CPU/RAM. Free physical memory was approximately 4.5GB and free virtual memory approximately 8.4GB, so no additional crypto concurrency should be added until the first batch completes.

Current manifest count shortly after launch was `0/64`, which is expected because each shard writes its manifest only after completion.

## Next Check

Use:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_031429_d99544

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-tail `
  -TaskId job_20260613_031429_d99544 `
  -TailLines 120
```

Then count completed shard manifests:

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action exec `
  -Command "powershell -NoProfile -Command ""(Get-ChildItem 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613\shards' -Filter a7ls17_manifest.json -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count"""
```

When all 64 manifests are present, aggregate materialized results and run the strict A7REWARD gate. Do not read raw materialization hits as alpha results.
