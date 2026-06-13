# CRYPTO A7V3S3 Strict Reward Launch 20260613

## Decision

`RUNNING_A7V3S3_STRICT_REWARD_GATE`

A7V3S3 starts a larger strict reward pass after A7V3S2 showed that all 17 A7V3S0 accepted blueprints were blocked by lag/stale controls, OOS control dominance, or stress weakness.

This stage does not authorize alpha proof, shadow, paper, or live use.

## Why This Run Exists

A7V3S0 produced reward-accepted numeric probes, but A7V3S2 found:

- `advance_deep_replay_count = 0`
- `lag_or_stale_dominated = 17 / 17`
- `control_dominated_oos_majority = 12 / 17`
- `stress_floor_not_positive = 13 / 17`

Therefore the reward gate was tightened before launching another broad pass.

## Strict Reward Gate Changes

The reward model now requires:

- `min_oos_sortino > 0`
- `min_oos_floor_sortino > 0`
- `stress_floor_sortino > 0` when stress samples exist
- `recent_shuffle_control_ratio < 1`
- `oos_control_dominated_count == 0`
- `oos_lag_stale_dominated_count == 0`

Synthetic smoke passed both locally and on the company machine.

## Prequeue

Input activity-ok queue:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_aggregate_20260613\a7ls17_activity_ok_queue.csv
```

Strict prequeue runtime:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s3_strict_reward_prequeue_20260613
```

Prequeue result:

```text
input_activity_ok_rows: 60,640
structural_excluded_rows: 9,187
strict_pool_rows: 51,453
selected_rows: 4,096
lane_count: 4
semantic_pair_count: 38
motif_count: 7
skeleton_count: 3,613
```

Structural fields excluded:

```text
listing_age_days
sqrt_listing_age_days
log1p_listing_age_days
age_percentile_active_universe
active_universe_size
```

## Sharded Reward Run

Reward runtime:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s3_strict_reward_sharded_720h_20260613
```

Shard plan:

```text
queue_rows: 4,096
rows_per_shard: 16
shard_count: 256
concurrency: 3
timeout_seconds_per_shard: 2,400
```

Company task:

```text
main task_id: job_20260613_215932_4a95b1
main launcher: D:\HermesWorker\runtime\a7v3s3_strict_reward_launcher_20260613.ps1
```

Initial process check:

```text
first shards started: s000, s001, s002
crypto reward workers: 3
free physical memory after launch: about 13.5GB
```

Supplemental tasks were added after the first shards showed steady progress and memory remained safe:

```text
supplemental task_id: job_20260613_221203_4367f3
range: s064-s127
concurrency: 3

supplemental task_id: job_20260613_221211_843c95
range: s128-s255
concurrency: 3
```

After supplemental launch:

```text
crypto reward workers: about 9
free physical memory: about 10.6GB
first main shards progressed to 8/16
```

## Monitoring

```powershell
powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_215932_4a95b1

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_221203_4367f3

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-status `
  -TaskId job_20260613_221211_843c95

powershell -ExecutionPolicy Bypass -File G:\Chengbo\tools\company-remote\company-remote.ps1 `
  -Action task-tail `
  -TaskId job_20260613_215932_4a95b1 `
  -TailLines 120
```

Count completed shard manifests:

```powershell
ssh -F G:\Chengbo\company-pc-ssh-config.stable company-pc-via-hermes-stable `
  "cmd /c ""dir /s /b D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s3_strict_reward_sharded_720h_20260613\shards\*\reward_runtime\a7reward1_manifest.json 2>nul | find /c /v """""""""
```

## Next Step

When the 256 shard manifests complete, aggregate the strict reward run, then apply A7V3S1/A7V3S2 style validation. Do not use raw reward accepted rows directly as alpha candidates.
