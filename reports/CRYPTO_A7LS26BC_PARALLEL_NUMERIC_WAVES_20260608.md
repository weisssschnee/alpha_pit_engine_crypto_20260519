# CRYPTO A7LS-26B/C Parallel Numeric Waves - 20260608

## Decision

```text
PASS_A7LS26BC_PARALLEL_NUMERIC_WAVES_DEPLOYED
```

## Purpose

A7LS-26 completed the first 4,096-row numeric wave from the A7LS-25 large-search materialization pool.  The company machine was then redeployed into two additional numeric waves:

```text
A7LS-26B:
  remaining activity-ok materialized pool, excluding A7LS-26.

A7LS-26C:
  raw-diverse / raw_multi_axis_reserved numeric wave, excluding A7LS-26 and A7LS-26B.
```

The intent is to keep company compute active while preventing a single narrow selector path from consuming all overnight runtime.

## Remote Runtime

```text
A7LS-26B:
  D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26b_numeric_wave_20260608

A7LS-26C:
  D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26c_raw_diverse_numeric_wave_20260608
```

## Deployment Snapshot

```text
A7LS-26B queue:
  numeric_queue_rows: 8192
  excluded_previous_a7ls26_rows: 4096
  materialized_activity_ok_remaining_rows: 29875
  axis_count: 2
  semantic_pair_count: 2
  motif_count: 11
  skeleton_count: 151

A7LS-26C queue:
  numeric_queue_rows: 4096
  excluded_previous_rows: 12288
  materialized_activity_ok_remaining_rows: 21683
  raw_axis_available_rows: 21683
  axis_count: 2
  semantic_pair_count: 2
  motif_count: 11
  skeleton_count: 137
```

## Status Notes

Both waves were confirmed to have active shard workers on the company machine.  A7LS-26B had already completed initial shards and advanced to the next pair.  A7LS-26C required a synchronous trigger after the first detached start produced an empty master process; the synchronous trigger successfully created the queue and started shard workers.

The low semantic-pair count in both B and C is a search-space contraction warning, not a deployment failure.  It means the A7LS-25 activity-ok materialized remainder is narrower than the original large-search atlas after field/evaluator/activity constraints.

## Authorization

```text
authorized:
  continue A7LS-26B/C numeric waves
  aggregate completed numeric outputs
  audit queue contraction / semantic-pair collapse

not authorized:
  alpha proof
  shadow / paper / live
  treating numeric clue rows as production candidates
```

