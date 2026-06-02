# CRYPTO A7FF-CORE51PXH COMPANY EXECUTION HANDOFF

Generated: 2026-06-02T02:55:43Z

## Decision

`PASS_A7FFCORE51PXH_COMPANY_EXECUTION_HANDOFF_READY`

This is the execution handoff for company-machine sharded replay. It does not run replay itself.

## Execution Steps

|   step | name                            | command                                                                                                                                                                                                                                  | purpose                                                                          |
|-------:|:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------|
|      1 | run_orchestrator                | powershell -ExecutionPolicy Bypass -File G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_company_execution_commands.ps1                                 | build compact frame and run 16 replay shards with jobs=8                         |
|      2 | check_status                    | py G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/scripts/crypto_a7ffcore51pxe_company_status.py --out G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602                                 | inspect shard completion and missing manifests                                   |
|      3 | aggregate_if_needed             | py G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/scripts/crypto_a7ffcore51pxe_company_result_aggregator.py --out G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602 --expected-shards 16 | rebuild aggregate summary if orchestrator completed but summary is stale/missing |
|      4 | import_to_repo_after_completion | py G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/scripts/crypto_a7ffcore51pxe_import_company_results.py --out G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602                         | copy aggregate summaries into repo runtime for CORE52 arbitration                |

## Acceptance Gates

| gate                   | pass_condition                               |
|:-----------------------|:---------------------------------------------|
| completed_shards       | 16/16 shard manifests PASS                   |
| eval_failures          | aggregate eval_failure_count == 0            |
| metric_rows            | aggregate metric_rows > 0                    |
| import_manifest        | repo runtime import decision PASS            |
| authorization_boundary | no formula search / proof / promotion / live |

## Failure Policy

| failure                  | action                                                                 |
|:-------------------------|:-----------------------------------------------------------------------|
| single_shard_timeout     | rerun only that shard with --force after checking compact frame exists |
| compact_frame_build_fail | check base/latent panel availability and field contract                |
| multiple_shard_failures  | freeze CORE51PXE as runner/data issue and open forensic; do not search |
| control_clean_zero       | still aggregate/import; CORE52 decides signal route                    |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core51pxe_execution": true,
  "authorizes_shadow_paper_live": false,
  "command_file": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_company_execution_commands.ps1",
  "decision": "PASS_A7FFCORE51PXH_COMPANY_EXECUTION_HANDOFF_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T02:55:43Z",
  "next_allowed": "A7FF-CORE51PXE company-machine sharded replay execution",
  "output_dir": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602",
  "source_decision": "PASS_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_READY",
  "source_stage": "A7FF-CORE51PXV",
  "stage": "A7FF-CORE51PXH"
}
```
