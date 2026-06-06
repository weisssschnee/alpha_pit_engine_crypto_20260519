# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-06-06T05:11:05Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
 M reports/CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md
 M runtime/a7pm3_experiment_board/a7pm3_active_workstreams.csv
 M runtime/a7pm3_experiment_board/a7pm3_allowed_next_tasks.json
 M runtime/a7pm3_experiment_board/a7pm3_latest_source_of_truth.json
 M runtime/a7pm3_experiment_board/a7pm3_manifest.json
 M scripts/crypto_a7pm3_current_experiment_board.py
?? reports/CRYPTO_A7LS16_LOCAL_PREFLIGHT_20260606.md
?? runtime/a7ls16_local_preflight/
?? scripts/crypto_a7ls16_local_preflight.py
HEAD=7d5aa8bde69930edb438bc778a9ddb283819b21d
origin/main=7d5aa8bde69930edb438bc778a9ddb283819b21d
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 4513,
  "authorization_record_count": 851,
  "authorizes_a7pm1": true,
  "authorizes_a7pm2": true,
  "authorizes_a7pm3": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": true,
  "authorizes_search": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-06-06T05:11:05Z",
  "head": "7d5aa8bde69930edb438bc778a9ddb283819b21d",
  "head_equals_origin_main": true,
  "origin_main": "7d5aa8bde69930edb438bc778a9ddb283819b21d",
  "stage": "A7PM-0",
  "stage_count": 472
}
```

## Current Status Summary

| current_status                                | evidence_level             |   count |
|:----------------------------------------------|:---------------------------|--------:|
| current_valid_governance                      | governance_or_audit        |       3 |
| current_valid_governance                      | contract                   |       1 |
| current_valid_scoped_large_search_arbitration | governance_or_audit        |       1 |
| current_valid_scoped_large_search_contract    | contract                   |       1 |
| engineering_pass_signal_hold                  | hold                       |       6 |
| engineering_pass_signal_hold                  | contract                   |       4 |
| engineering_pass_signal_hold                  | diagnostic                 |       3 |
| hold                                          | hold                       |      95 |
| hold                                          | diagnostic                 |       7 |
| hold                                          | alpha_claim_check_required |       2 |
| hold                                          | contract                   |       2 |
| not_authorized                                | hold                       |       2 |
| superseded_diagnostic                         | contract                   |       1 |
| valid_or_historical_record                    | governance_or_audit        |     178 |
| valid_or_historical_record                    | contract                   |     126 |
| valid_or_historical_record                    | diagnostic                 |      29 |
| valid_or_historical_record                    | smoke                      |       9 |
| valid_or_historical_record                    | alpha_claim_check_required |       2 |

## Supersession Map

| stage_id              | supersedes                                 | superseded_by   | current_status                                | notes                                                                                                 |
|:----------------------|:-------------------------------------------|:----------------|:----------------------------------------------|:------------------------------------------------------------------------------------------------------|
| A7AL-2P2              |                                            | A7AL-2X0        | superseded_diagnostic                         | A7AL-2P2 superseded by A7AL-2X0 arbitration                                                           |
| A7AL-2Q               |                                            | A7AL-2X0        | not_authorized                                | A7AL-2Q local execution not authorized                                                                |
| A7LS-14               |                                            | A7LS-14X        | current_valid_scoped_large_search_contract    | A7LS-14 authorizes only checkpointed multi-axis A7LS15-A7LS18 large search; proof/live remain blocked |
| A7LS-14X              | global_large_search_block_for_a7ls14_scope |                 | current_valid_scoped_large_search_arbitration | A7LS-14X resolves old global no-large-search record for A7LS14 scope only                             |
| COMPANY-A7AL2Q2R-FULL |                                            | A7AL-2X0        | not_authorized                                | A7AL-2Q local execution not authorized                                                                |

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
  "formula_search_outside_A7LS14": "not authorized",
  "large_search_outside_A7LS14": "not authorized; A7LS-14X authorizes only checkpointed A7LS15-A7LS18 scoped large search",
  "shadow_paper_live": "not authorized"
}
```

## Next Allowed Tasks

```json
{
  "A7FF-24R4E repaired numeric wave execution option": "requires explicit user authorization; no search and no promotion",
  "A7FF-52E materialization preflight execution option": "requires explicit authorization; 1200 family-balanced rows; no numeric replay/search",
  "A7LS15 million-scale multi-axis blueprint generation": "authorized by A7LS-14X scoped large-search arbitration; generated_total <= 1,000,000",
  "A7LS16 local preflight and materialization smoke": "authorized by A7LS-14X before company materialization",
  "A7LS17 company sharded materialization": "authorized after A7LS16 preflight; materialization_total <= 100,000",
  "A7LS18 company sharded numeric wave": "authorized after materialization; numeric_total <= 25,000 with checkpoints",
  "A7PM-0/3 maintenance": "keep source-of-truth and experiment board current"
}
```

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7AL-2P2 is superseded diagnostic; A7AL-2Q is not authorized.
A7AL-2Z0-Z9 are engineering diagnostics with signal hold.
```
