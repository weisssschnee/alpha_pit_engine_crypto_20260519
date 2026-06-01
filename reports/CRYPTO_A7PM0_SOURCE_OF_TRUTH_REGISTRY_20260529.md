# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-06-01T20:59:08Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
 M reports/CRYPTO_A7PM0_SOURCE_OF_TRUTH_REGISTRY_20260529.md
 M reports/CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md
 M runtime/a7pm0_source_of_truth_registry/a7pm0_artifact_registry.csv
 M runtime/a7pm0_source_of_truth_registry/a7pm0_authorization_matrix.csv
 M runtime/a7pm0_source_of_truth_registry/a7pm0_current_valid_records.json
 M runtime/a7pm0_source_of_truth_registry/a7pm0_manifest.json
 M runtime/a7pm0_source_of_truth_registry/a7pm0_stage_registry.csv
 M runtime/a7pm3_experiment_board/a7pm3_active_workstreams.csv
 M runtime/a7pm3_experiment_board/a7pm3_allowed_next_tasks.json
 M runtime/a7pm3_experiment_board/a7pm3_blocked_tasks.json
 M runtime/a7pm3_experiment_board/a7pm3_latest_source_of_truth.json
 M runtime/a7pm3_experiment_board/a7pm3_manifest.json
 M scripts/crypto_a7pm3_current_experiment_board.py
?? reports/CRYPTO_A7FFCORE43E_CONTROL_VECTOR_REBUILD_AUDIT_20260602.md
?? reports/CRYPTO_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_CONSTRUCTION_20260602.md
?? reports/CRYPTO_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_20260602.md
?? reports/CRYPTO_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_EXECUTION_20260602.md
?? reports/CRYPTO_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_20260602.md
?? reports/CRYPTO_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_20260602.md
?? reports/CRYPTO_A7FFCORE46_ORTHOGONAL_FAILURE_ROUTE_ARBITRATION_20260602.md
?? runtime/a7ffcore43e_control_vector_rebuild_audit/
?? runtime/a7ffcore44_orthogonal_score_packet_contract/
?? runtime/a7ffcore44e_orthogonal_score_packet_construction/
?? runtime/a7ffcore45_orthogonal_book_replay_contract/
?? runtime/a7ffcore45e_orthogonal_book_replay_execution/
?? runtime/a7ffcore45r_orthogonal_book_replay_forensic/
?? runtime/a7ffcore46_orthogonal_failure_route_arbitration/
?? scripts/crypto_a7ffcore43e_control_vector_rebuild_audit.py
?? scripts/crypto_a7ffcore44_orthogonal_score_packet_contract.py
?? scripts/crypto_a7ffcore44e_orthogonal_score_packet_construction.py
?? scripts/crypto_a7ffcore45_orthogonal_book_replay_contract.py
?? scripts/crypto_a7ffcore45e_orthogonal_book_replay_execution.py
?? scripts/crypto_a7ffcore45r_orthogonal_book_replay_forensic.py
?? scripts/crypto_a7ffcore46_orthogonal_failure_route_arbitration.py
HEAD=84a2c872a37a4bbd363bd8a93152626be3d51cf5
origin/main=84a2c872a37a4bbd363bd8a93152626be3d51cf5
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 3834,
  "authorization_record_count": 746,
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
  "generated_at": "2026-06-01T20:59:08Z",
  "head": "84a2c872a37a4bbd363bd8a93152626be3d51cf5",
  "head_equals_origin_main": true,
  "origin_main": "84a2c872a37a4bbd363bd8a93152626be3d51cf5",
  "stage": "A7PM-0",
  "stage_count": 400
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
| hold                         | hold                       |      78 |
| hold                         | diagnostic                 |       6 |
| hold                         | alpha_claim_check_required |       2 |
| hold                         | contract                   |       2 |
| not_authorized               | hold                       |       2 |
| superseded_diagnostic        | contract                   |       1 |
| valid_or_historical_record   | governance_or_audit        |     144 |
| valid_or_historical_record   | contract                   |     114 |
| valid_or_historical_record   | diagnostic                 |      26 |
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
