# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-05-29T20:09:52Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
 M reports/CRYPTO_A7PM0_SOURCE_OF_TRUTH_REGISTRY_20260529.md
 M runtime/a7pm0_source_of_truth_registry/a7pm0_artifact_registry.csv
 M runtime/a7pm0_source_of_truth_registry/a7pm0_current_valid_records.json
 M runtime/a7pm0_source_of_truth_registry/a7pm0_manifest.json
 M runtime/a7pm0_source_of_truth_registry/a7pm0_stage_registry.csv
 M scripts/crypto_a7ff8_expanded_numeric_probe.py
?? reports/CRYPTO_A7FF10S00_COMPANY_NUMERIC_PROBE_20260530.md
?? reports/CRYPTO_A7FF10S01_COMPANY_NUMERIC_PROBE_20260530.md
?? reports/CRYPTO_A7FF10S02_COMPANY_NUMERIC_PROBE_20260530.md
?? reports/CRYPTO_A7FF10S03_COMPANY_NUMERIC_PROBE_20260530.md
?? reports/CRYPTO_A7FF10_COMPANY_PARALLEL_AGGREGATE_20260530.md
?? runtime/a7ff10_company_numeric_probe_shard_00/
?? runtime/a7ff10_company_numeric_probe_shard_01/
?? runtime/a7ff10_company_numeric_probe_shard_02/
?? runtime/a7ff10_company_numeric_probe_shard_03/
?? runtime/a7ff10_company_parallel/
?? runtime/a7ff10_company_parallel_aggregate/
?? scripts/crypto_a7ff10_company_parallel_aggregate.py
?? scripts/crypto_a7ff10_company_parallel_launcher.ps1
HEAD=d64e4e31e9f7ebb0fdc6065b3a2f4914f13b5910
origin/main=d64e4e31e9f7ebb0fdc6065b3a2f4914f13b5910
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 1367,
  "authorization_record_count": 638,
  "authorizes_a7pm1": true,
  "authorizes_a7pm2": true,
  "authorizes_a7pm3": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T20:09:52Z",
  "head": "d64e4e31e9f7ebb0fdc6065b3a2f4914f13b5910",
  "head_equals_origin_main": true,
  "origin_main": "d64e4e31e9f7ebb0fdc6065b3a2f4914f13b5910",
  "stage": "A7PM-0",
  "stage_count": 168
}
```

## Current Status Summary

| current_status               | evidence_level             |   count |
|:-----------------------------|:---------------------------|--------:|
| current_valid_governance     | contract                   |       1 |
| current_valid_governance     | governance_or_audit        |       1 |
| engineering_pass_signal_hold | hold                       |       6 |
| engineering_pass_signal_hold | contract                   |       4 |
| engineering_pass_signal_hold | diagnostic                 |       3 |
| hold                         | hold                       |      33 |
| hold                         | diagnostic                 |       4 |
| hold                         | alpha_claim_check_required |       2 |
| hold                         | contract                   |       2 |
| not_authorized               | hold                       |       2 |
| superseded_diagnostic        | contract                   |       1 |
| valid_or_historical_record   | governance_or_audit        |      59 |
| valid_or_historical_record   | contract                   |      36 |
| valid_or_historical_record   | smoke                      |       7 |
| valid_or_historical_record   | diagnostic                 |       5 |
| valid_or_historical_record   | alpha_claim_check_required |       2 |

## Supersession Map

| stage_id              | supersedes   | superseded_by   | current_status        | notes                                       |
|:----------------------|:-------------|:----------------|:----------------------|:--------------------------------------------|
| A7AL-2P2              |              | A7AL-2X0        | superseded_diagnostic | A7AL-2P2 superseded by A7AL-2X0 arbitration |
| A7AL-2Q               |              | A7AL-2X0        | not_authorized        | A7AL-2Q local execution not authorized      |
| COMPANY-A7AL2Q2R-FULL |              | A7AL-2X0        | not_authorized        | A7AL-2Q local execution not authorized      |

## Blocked Tasks

```json
{
  "A7AL-2Q": "superseded/not_authorized by A7AL-2X0",
  "A7AL-2Y": "formula generation/search execution not authorized",
  "A7AL-3": "large search not authorized",
  "alpha_proof": "not authorized",
  "direct_OI_price_rerun": "same objective rerun not authorized",
  "formula_search": "not authorized",
  "large_search": "not authorized",
  "shadow_paper_live": "not authorized"
}
```

## Next Allowed Tasks

```json
{
  "A7AA": "primitive response / label adequacy continuation",
  "A7AI-F2": "end-to-end field enforcement regression audit",
  "A7AI-F3": "materialization/evaluator parity sprint",
  "A7PM-1": "asset taxonomy and modularization plan",
  "A7PM-2": "candidate lifecycle state machine",
  "A7PM-3": "current experiment board"
}
```

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7AL-2P2 is superseded diagnostic; A7AL-2Q is not authorized.
A7AL-2Z0-Z9 are engineering diagnostics with signal hold.
```
