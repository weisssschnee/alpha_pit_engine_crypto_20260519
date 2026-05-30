# CRYPTO A7FF-11R COMPANY RUNNER CONTRACT

Generated: 2026-05-30T03:15:04Z

## Decision

`PASS_A7FF11R_COMPANY_RUNNER_CONTRACT_READY_WITH_MANIFEST_POLLING_REQUIRED`

A7FF-11R records the company-machine launch contract for heavier A7FF numeric waves. It does not run search, replay, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_a7ff12_company_numeric_wave": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF11R_COMPANY_RUNNER_CONTRACT_READY_WITH_MANIFEST_POLLING_REQUIRED",
  "generated_at": "2026-05-30T03:15:04Z",
  "issues_recorded": 2,
  "launcher_rows": 4,
  "log_rows": 4,
  "requires_manifest_polling": true,
  "source_decision": "PASS_A7FF10_COMPANY_PARALLEL_NUMERIC_AGGREGATE_BUILT",
  "source_stage": "A7FF-10-COMPANY-PARALLEL-AGGREGATE",
  "stage": "A7FF-11R-COMPANY-RUNNER-CONTRACT"
}
```

## Runner Issues

| issue                                              | evidence                                                                                     | fix_applied                                                                                   | status                    |
|:---------------------------------------------------|:---------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------|:--------------------------|
| background_launch_log_not_reliable_source_of_truth | At least one shard log does not contain final PASS even though final runtime manifest exists | Treat shard manifest and pulled report as source-of-truth; require per-shard manifest polling | requires_runner_hardening |
| company_machine_resource_preflight_required        | Heavy shards share the machine with unrelated Python jobs                                    | A7FF-12 launch must check free memory and heavy Python process count before starting          | required_next_launch_gate |

## Log Scan

| log           | exists   |   bytes | has_pass_decision   | has_traceback   | has_tabulate_error   | has_missing_numpy   | has_missing_data_root   |
|:--------------|:---------|--------:|:--------------------|:----------------|:---------------------|:--------------------|:------------------------|
| a7ff10s00.log | True     |    7134 | False               | False           | False                | False               | False                   |
| a7ff10s01.log | True     |    7512 | False               | False           | False                | False               | False                   |
| a7ff10s02.log | True     |    7506 | False               | False           | False                | False               | False                   |
| a7ff10s03.log | True     |    7512 | False               | False           | False                | False               | False                   |

## Launch Contract

```json
{
  "background_start_process_status": "not_reliable_enough_for_unattended_scale_without_manifest_polling",
  "data_root": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData",
  "max_initial_parallel_shards": 2,
  "must_not_do": [
    "use D:/Python311/python.exe for numeric probes",
    "assume G:/AlphaFactory_CryptoData exists on company machine",
    "treat a process id in launch_manifest as completion evidence",
    "treat logs as source-of-truth when runtime manifests disagree"
  ],
  "preflight_checks": [
    "python imports numpy/pandas/pyarrow",
    "base panel path exists",
    "meme taxonomy metadata exists",
    "free memory >= 8GB before starting 1 shard, >= 14GB before starting 2 shards",
    "no unrelated high-memory Python job unless running single-shard foreground",
    "per-shard manifest path is absent or explicitly quarantined before rerun"
  ],
  "recommended_execution_mode": "managed_foreground_or_manifest_polled_jobs",
  "remote_host": "company-pc-via-hermes-stable",
  "remote_python": "D:/HermesWorker/venvs/phase3z33/Scripts/python.exe",
  "remote_repo": "D:/HermesWorker/GDrive/Project_V7_Rotation/alpha_pit_engine_crypto_20260519_remote",
  "required_env": {
    "A7AL_BASE_PANEL_ROOT": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527",
    "ALPHAFACTORY_CRYPTO_DATA_ROOT": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData"
  },
  "safe_fallback": "run shards sequentially via SSH foreground and pull manifests after each shard"
}
```

## Boundary

```text
A7FF-12 may use the company machine for numeric-wave scale-up only after preflight checks pass.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
