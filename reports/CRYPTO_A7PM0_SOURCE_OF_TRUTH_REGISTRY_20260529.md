# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-06-03T02:08:35Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
 M reports/CRYPTO_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_20260603.md
D  reports/CRYPTO_A7FFCORE53IR_FACTOR_INPUT_REPAIR_CONTRACT_20260603.md
 M runtime/a7ffcore53ia_incremental_input_approval/a7ffcore53ia_manifest.json
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_authorization_matrix.json
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_current_snapshot.json
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_field_type_quota_policy.csv
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_manifest.json
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_pair_quota_policy.csv
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_queue_gate_policy.json
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_repair_actions.csv
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_source_base_field_usage.csv
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_source_field_type_usage.csv
D  runtime/a7ffcore53ir_factor_input_repair_contract/a7ffcore53ir_source_input_type_redundancy.csv
 M scripts/crypto_a7ffcore53ia_incremental_input_approval.py
D  scripts/crypto_a7ffcore53ir_factor_input_repair_contract.py
?? reports/CRYPTO_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_20260603.md
?? runtime/a7ffcore53iae_input_approval_filter_experiment/
?? scripts/crypto_a7ffcore53iae_input_approval_filter_experiment.py
HEAD=76acbcf100861507514e55d86910928d4dba5ee1
origin/main=76acbcf100861507514e55d86910928d4dba5ee1
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 4024,
  "authorization_record_count": 786,
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
  "generated_at": "2026-06-03T02:08:35Z",
  "head": "76acbcf100861507514e55d86910928d4dba5ee1",
  "head_equals_origin_main": true,
  "origin_main": "76acbcf100861507514e55d86910928d4dba5ee1",
  "stage": "A7PM-0",
  "stage_count": 425
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
| hold                         | hold                       |      83 |
| hold                         | diagnostic                 |       7 |
| hold                         | alpha_claim_check_required |       2 |
| hold                         | contract                   |       2 |
| not_authorized               | hold                       |       2 |
| superseded_diagnostic        | contract                   |       1 |
| valid_or_historical_record   | governance_or_audit        |     151 |
| valid_or_historical_record   | contract                   |     125 |
| valid_or_historical_record   | diagnostic                 |      27 |
| valid_or_historical_record   | smoke                      |       8 |
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
  "A7FF-24R4E execution": "pending explicit heavy-execution authorization; A7FF-24R4 contract is ready but does not execute numeric wave",
  "A7FF-41": "not authorized by A7FF-40 because selected control-strict non-L7 evidence is still single-family",
  "A7FF-43": "not authorized by A7FF-42 because selected control-strict non-L7 evidence is still single-family",
  "A7FF-45": "superseded by A7FF-47 label translation hold; bounded replay passed but did not translate beyond L5",
  "A7FF-48": "not authorized by A7FF-47 because frozen clues fail non-L5 label translation",
  "A7FF-50": "not authorized by A7FF-49 because existing maps have no non-reference non-L5 candidates",
  "A7FF-51 execution": "not authorized by A7FF-R11; only contract drafting is authorized",
  "A7FF-52E execution": "pending explicit materialization-preflight authorization; A7FF-52 contract is ready but does not execute materialization",
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
  "A7FF-24R4E repaired numeric wave execution option": "requires explicit user authorization; no search and no promotion",
  "A7FF-52E materialization preflight execution option": "requires explicit authorization; 1200 family-balanced rows; no numeric replay/search",
  "A7PM-0/3 maintenance": "keep source-of-truth and experiment board current"
}
```

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7AL-2P2 is superseded diagnostic; A7AL-2Q is not authorized.
A7AL-2Z0-Z9 are engineering diagnostics with signal hold.
```
