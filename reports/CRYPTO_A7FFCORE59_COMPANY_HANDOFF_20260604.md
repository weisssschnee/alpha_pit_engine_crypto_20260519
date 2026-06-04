# CRYPTO A7FF-CORE59 COMPANY HANDOFF

Generated: 2026-06-04T13:42:30Z

## Purpose

CORE59 is a heavy numeric repair execution over the CORE58 failure-aware queue. It should run on the company machine, not the local workstation.

This handoff provides checkpoint-safe execution. It does not authorize replay, formula search, large search, alpha proof, shadow, paper, or live.

## Current Local Checkpoint

```text
complete_existing:
  s00
  s01
  s02
  s03

queued_partial:
  s04

not_started:
  s05
```

Checkpoint files:

```text
runtime/a7ffcore59_numeric_repair_execution/a7ffcore59_checkpoint_manifest.json
runtime/a7ffcore59_numeric_repair_execution/a7ffcore59_checkpoint_status.csv
G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/a7ffcore59_checkpoint_status.csv
```

## Company Machine Execution

If company machine has access to the existing external runtime directory with `shard_00` to `shard_03`, run only missing shards:

```powershell
cd G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519
git pull
$env:A7FFCORE59_EXTERNAL='G:\AlphaFactory_CryptoData\research_runtime\a7ffcore59_numeric_repair_execution_20260604'
$env:A7FFCORE59_ROWS_PER_SHARD='200'
$env:A7FFCORE59_SHARDS='4,5'
py scripts\crypto_a7ffcore59_numeric_repair_execution.py
```

If company machine does not have the existing local shard outputs, run all shards:

```powershell
cd G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519
git pull
$env:A7FFCORE59_EXTERNAL='G:\AlphaFactory_CryptoData\research_runtime\a7ffcore59_numeric_repair_execution_20260604'
$env:A7FFCORE59_ROWS_PER_SHARD='200'
py scripts\crypto_a7ffcore59_numeric_repair_execution.py
```

The runner reuses any shard with an existing `a7ffcore59_sXX_manifest.json` unless forced.

## Checkpoint Only

To inspect checkpoint without running numeric work:

```powershell
$env:A7FFCORE59_CHECKPOINT_ONLY='1'
py scripts\crypto_a7ffcore59_numeric_repair_execution.py
Remove-Item Env:\A7FFCORE59_CHECKPOINT_ONLY -ErrorAction SilentlyContinue
```

## Resume Rules

```text
completed shard:
  shard directory contains a7ffcore59_sXX_manifest.json

partial shard:
  shard directory contains queue/logs but no manifest

rerun partial shard:
  include its shard index in A7FFCORE59_SHARDS

force rerun completed shards:
  set A7FFCORE59_FORCE_RERUN=1
```

## Boundary

```text
numeric probe execution: authorized by CORE58
replay execution: not authorized
formula search: not authorized
large search: not authorized
alpha proof / shadow / paper / live: not authorized
```
