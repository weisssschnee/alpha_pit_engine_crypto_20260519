# Crypto Artifact Cleanup 20260705

## Decision

`PASS_CRYPTO_ARTIFACT_CLEANUP_DEPRECATED_RUNTIME_REMOVED`

## Scope

This cleanup applies the artifact lifecycle policy in:

```text
.planning/graphs/ARTIFACT_LIFECYCLE.md
```

The cleanup target was obsolete process output, not active source code, active contracts, current reports, or current runtime evidence.

## Removed From Working Tree

Ignored/generated local files:

```text
graphify-out/
alphafactory_crypto/**/__pycache__/
scripts/__pycache__/
tools/maintenance/__pycache__/
selected ignored CSV files under archive/deprecated_crypto_a7_20260527/runtime/
```

Untracked empty directories:

```text
docs/
runtime/a7fast0_local_halving_smoke_20260615/
runtime/a7ff55r5e_repaired_atlas_numeric_execution/
runtime/a7ffcore16he_second_pass_interaction_breadth/second_pass_family=H1_I5_deconcentration/
runtime/a7ffcore16he_second_pass_interaction_breadth/second_pass_family=H2_I4_near_miss_repair/
runtime/a7ffcore16he_second_pass_interaction_breadth/second_pass_family=H3_cross_family_bridge__chunk=0-of-6/
runtime/a7ffcore16he_second_pass_interaction_breadth/second_pass_family=H3_cross_family_bridge__chunk=1-of-6/
runtime/a7ffcore16he_second_pass_interaction_breadth/second_pass_family=H3_cross_family_bridge__chunk=2-of-6/
runtime/a7ffcore51e_filtered_replay_execution/
runtime/a7ffcore51p_optimized_replay_runner_smoke/
runtime/a7ls3_numeric_checkpoint_from_materialized/numeric_probe/
runtime/a7v3s9_prereward_oos_control_proxy_smoke_20260614/
```

Tracked deprecated runtime archive:

```text
archive/deprecated_crypto_a7_20260527/runtime/
```

This removed approximately `904.7 MB` and `893` tracked deprecated runtime files from the active checkout. The retained archive still includes deprecated scripts and reports.

## Retained

```text
archive/deprecated_crypto_a7_20260527/scripts/
archive/deprecated_crypto_a7_20260527/reports/
reports/CRYPTO_DEPRECATED_ACTIVE_TREE_ARCHIVE_20260527.md
```

Reason:

```text
scripts/reports are compact historical index evidence;
runtime payloads are bulky process outputs and not active architecture.
```

## Guardrails

```text
active source code deleted: false
active reports deleted: false
active current runtime deleted: false
company-machine active A7SEARCH7 run touched: false
alpha proof authorized: false
shadow/paper/live authorized: false
```

## Recovery

Removed tracked archive runtime payloads are recoverable from git history before this cleanup commit. They are not part of the active architecture or current source-of-truth chain.
