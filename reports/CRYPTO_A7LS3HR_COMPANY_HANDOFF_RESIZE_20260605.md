# CRYPTO A7LS-3HR COMPANY HANDOFF RESIZE

Generated: 2026-06-05T06:21:34Z

## Decision

`PASS_A7LS3HR_COMPANY_HANDOFF_RESIZED_64_READY`

A7LS-3HR resizes the company numeric handoff from 32 rows/shard to 64 rows/shard while preserving a 32-row fallback plan. It does not execute numeric probe locally.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_company_numeric_async_64": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7LS3HR_COMPANY_HANDOFF_RESIZED_64_READY",
  "executes_numeric_probe": false,
  "executes_search": false,
  "fallback_rows_per_shard": 32,
  "fallback_shard_count": 32,
  "generated_at": "2026-06-05T06:21:34Z",
  "max_parallelism_if_memory_headroom_confirmed": 12,
  "primary_rows_per_shard": 64,
  "primary_shard_count": 16,
  "queue_rows": 1024,
  "recommended_parallelism": 8,
  "source_decision": "PASS_A7LS3H_COMPANY_NUMERIC_HANDOFF_READY",
  "source_stage": "A7LS-3H",
  "stage": "A7LS-3HR"
}
```

## Company Launcher

Primary company execution launcher:

```text
scripts/crypto_a7ls3hr_company_parallel_launcher.ps1
```

Default execution shape:

```text
rows_per_shard: 64
shard_count: 16
max_parallel: 8
optional_max_parallel_if_memory_headroom_confirmed: 12
```

The launcher is checkpoint-aware: shards with an existing manifest are skipped. It writes per-shard queues and logs under:

```text
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls3hr_company_numeric
D:\HermesWorker\GDrive\AlphaFactory_CryptoData\logs
```

## Arm Summary

| a7ls_arm   |   rows |   semantic_pair_count |   motif_count |   skeleton_count |
|:-----------|-------:|----------------------:|--------------:|-----------------:|
| A7LS_A     |    303 |                     1 |             2 |               24 |
| A7LS_B     |    367 |                    14 |             2 |               17 |
| A7LS_C     |     66 |                     1 |             1 |                3 |
| A7LS_D     |    288 |                     4 |             2 |               19 |

## Primary 64-Row Shard Plan

| company_numeric_shard   |   rows |   arm_count |   semantic_pair_count |   motif_count |   skeleton_count |
|:------------------------|-------:|------------:|----------------------:|--------------:|-----------------:|
| a7ls3hr_s000            |     64 |           1 |                     1 |             2 |               11 |
| a7ls3hr_s001            |     64 |           1 |                     1 |             1 |                7 |
| a7ls3hr_s002            |     64 |           1 |                     1 |             2 |               14 |
| a7ls3hr_s003            |     64 |           1 |                     1 |             2 |               12 |
| a7ls3hr_s004            |     64 |           1 |                     5 |             2 |               16 |
| a7ls3hr_s005            |     64 |           1 |                     7 |             2 |               12 |
| a7ls3hr_s006            |     64 |           1 |                     8 |             2 |               10 |
| a7ls3hr_s007            |     64 |           1 |                     7 |             2 |                7 |
| a7ls3hr_s008            |     64 |           1 |                     1 |             1 |                3 |
| a7ls3hr_s009            |     64 |           2 |                     4 |             2 |                9 |
| a7ls3hr_s010            |     64 |           1 |                     3 |             2 |                9 |
| a7ls3hr_s011            |     64 |           1 |                     3 |             2 |               11 |
| a7ls3hr_s012            |     64 |           1 |                     2 |             2 |               13 |
| a7ls3hr_s013            |     64 |           2 |                     8 |             3 |               13 |
| a7ls3hr_s014            |     64 |           2 |                     6 |             2 |                8 |
| a7ls3hr_s015            |     64 |           2 |                     2 |             2 |               17 |

## Fallback 32-Row Shard Plan

| company_numeric_shard   |   rows |   arm_count |   semantic_pair_count |   motif_count |   skeleton_count |
|:------------------------|-------:|------------:|----------------------:|--------------:|-----------------:|
| a7ls3hr_s000            |     32 |           1 |                     1 |             1 |                6 |
| a7ls3hr_s001            |     32 |           1 |                     1 |             2 |                9 |
| a7ls3hr_s002            |     32 |           1 |                     1 |             1 |                6 |
| a7ls3hr_s003            |     32 |           1 |                     1 |             1 |                7 |
| a7ls3hr_s004            |     32 |           1 |                     1 |             1 |                9 |
| a7ls3hr_s005            |     32 |           1 |                     1 |             2 |               10 |
| a7ls3hr_s006            |     32 |           1 |                     1 |             1 |                7 |
| a7ls3hr_s007            |     32 |           1 |                     1 |             2 |               11 |
| a7ls3hr_s008            |     32 |           1 |                     3 |             2 |               13 |
| a7ls3hr_s009            |     32 |           1 |                     4 |             2 |               11 |
| a7ls3hr_s010            |     32 |           1 |                     7 |             2 |               11 |
| a7ls3hr_s011            |     32 |           1 |                     7 |             2 |                6 |
| a7ls3hr_s012            |     32 |           1 |                     6 |             2 |                9 |
| a7ls3hr_s013            |     32 |           1 |                     8 |             2 |                7 |
| a7ls3hr_s014            |     32 |           1 |                     6 |             2 |                6 |
| a7ls3hr_s015            |     32 |           1 |                     6 |             2 |                6 |
| a7ls3hr_s016            |     32 |           1 |                     1 |             1 |                3 |
| a7ls3hr_s017            |     32 |           1 |                     1 |             1 |                2 |
| a7ls3hr_s018            |     32 |           2 |                     4 |             2 |                5 |
| a7ls3hr_s019            |     32 |           1 |                     2 |             2 |                7 |
| a7ls3hr_s020            |     32 |           1 |                     3 |             2 |                5 |
| a7ls3hr_s021            |     32 |           1 |                     2 |             2 |                8 |
| a7ls3hr_s022            |     32 |           1 |                     2 |             2 |                6 |
| a7ls3hr_s023            |     32 |           1 |                     3 |             2 |                8 |
| a7ls3hr_s024            |     32 |           1 |                     2 |             2 |                8 |
| a7ls3hr_s025            |     32 |           1 |                     2 |             2 |               10 |
| a7ls3hr_s026            |     32 |           2 |                     6 |             3 |                9 |
| a7ls3hr_s027            |     32 |           1 |                     7 |             2 |               11 |
| a7ls3hr_s028            |     32 |           1 |                     4 |             1 |                2 |
| a7ls3hr_s029            |     32 |           2 |                     5 |             2 |                8 |
| a7ls3hr_s030            |     32 |           2 |                     2 |             2 |               11 |
| a7ls3hr_s031            |     32 |           2 |                     2 |             2 |               12 |

## Command Template

```json
{
  "checkpoint_policy": "first run 2-4 primary shards, inspect runtime/memory, then scale to parallelism 8-12",
  "fallback_plan": {
    "queue_file": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls3hr_company_handoff_resize/a7ls3hr_company_numeric_queue_32_fallback.csv",
    "recommended_parallelism": 4,
    "rows_per_shard": 32,
    "shard_count": 32,
    "shard_plan_file": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls3hr_company_handoff_resize/a7ls3hr_company_shard_plan_32_fallback.csv"
  },
  "per_shard_env_primary": {
    "A7FF8_AUTH_DECISION": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
    "A7FF8_AUTH_MANIFEST": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls2_sharded_materialization_wave/a7ls2_manifest.json",
    "A7FF8_FAST_NUMERIC_CAP": "64",
    "A7FF8_FILE_PREFIX": "a7ls3hr_${SHARD}",
    "A7FF8_MATERIALIZE_CAP": "64",
    "A7FF8_PORTFOLIO_CAP": "96",
    "A7FF8_QUEUE_LIMIT": "64",
    "A7FF8_QUEUE_PATH": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}/queue.csv",
    "A7FF8_REPORT": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}/A7LS3HR_NUMERIC_DETAIL.md",
    "A7FF8_RUNTIME": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}",
    "A7FF8_STAGE": "A7LS-3HR-${SHARD}",
    "A7FF8_WRITE_CONTROL_DETAIL": "1"
  },
  "primary_plan": {
    "max_parallelism_if_memory_headroom_confirmed": 12,
    "queue_file": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls3hr_company_handoff_resize/a7ls3hr_company_numeric_queue_64.csv",
    "recommended_parallelism": 8,
    "rows_per_shard": 64,
    "shard_count": 16,
    "shard_plan_file": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls3hr_company_handoff_resize/a7ls3hr_company_shard_plan_64.csv"
  },
  "resume_rule": "skip shard when manifest exists and process returncode == 0",
  "stage": "A7LS-3HR"
}
```
