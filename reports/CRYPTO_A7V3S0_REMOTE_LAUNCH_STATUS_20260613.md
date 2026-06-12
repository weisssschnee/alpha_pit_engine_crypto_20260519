# CRYPTO A7V3S0 Remote Launch Status 20260613

## Decision

`HOLD_A7V3S0_COMPANY_LAUNCH_BLOCKED_BY_REMOTE_DATA_SYNC`

A7V3S0 search contract and local materialization smoke are ready, but the company machine launch is intentionally not started because the remote machine does not currently have the v3 merged panel or recent patch data roots required by the contract.

## Local Readiness

- contract commit: `5a6fbe3`
- queue rows: `65536`
- shards: `64`
- rows per shard: `1024`
- local materialization smoke: `PASS_A7LS17_SHARD_MATERIALIZATION_COMPLETE`
- smoke queue rows: `64`
- smoke eval success: `64`
- smoke activity ok: `59`
- smoke lanes: `4`

## Company Machine Probe

Observed through `company-remote.ps1`:

```text
OK      1574  D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote
MISSING 0     D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613
OK      498   D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527
MISSING 0     D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612
```

The company repo path also behaved like a file mirror rather than a normal git working tree during the probe, so GitHub pull cannot be assumed there.

## Why Launch Was Blocked

The launcher is configured to run against:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613
```

That root is absent on the company machine. Starting the 64-shard materialization wave would either fail immediately or silently evaluate against the wrong panel if environment handling were changed. That would waste compute and contaminate the search ledger.

## Required Next Action

Sync one of these before launch:

1. Preferred: copy the local v3 merged panel root to the same company path.
2. Alternative: copy both the local v2 panel and recent patch roots, then rebuild v3 on company with the same builder.

Required company paths:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613\a7v3s0_large_search_queue.csv
D:\HermesWorker\runtime\run_a7v3s0_company_materialization.ps1
```

## Launch Rule

Only start the company materialization after the v3 panel root exists and a 64-row remote smoke passes on company. Then start detached:

```powershell
powershell -ExecutionPolicy Bypass -File D:\HermesWorker\runtime\run_a7v3s0_company_materialization.ps1
```

This launch authorizes only numeric materialization and reward-gate follow-up. It does not authorize alpha proof, shadow, paper, or live use.
