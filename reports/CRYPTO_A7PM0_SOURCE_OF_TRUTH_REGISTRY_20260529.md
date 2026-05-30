# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-05-30T18:21:53Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
 M reports/CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md
 M runtime/a7pm3_experiment_board/a7pm3_active_workstreams.csv
 M runtime/a7pm3_experiment_board/a7pm3_allowed_next_tasks.json
 M runtime/a7pm3_experiment_board/a7pm3_blocked_tasks.json
 M runtime/a7pm3_experiment_board/a7pm3_manifest.json
 M scripts/crypto_a7pm0_source_of_truth_registry.py
 M scripts/crypto_a7pm3_current_experiment_board.py
?? reports/CRYPTO_A7FF44_DEEP_FORENSIC_20260531.md
?? runtime/a7ff44_deep_forensic/
?? scripts/crypto_a7ff44_deep_forensic.py
HEAD=75523965624212236f4944f77ebcbf22e131b5cb
origin/main=75523965624212236f4944f77ebcbf22e131b5cb
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 2347,
  "authorization_record_count": 683,
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
  "generated_at": "2026-05-30T18:21:53Z",
  "head": "75523965624212236f4944f77ebcbf22e131b5cb",
  "head_equals_origin_main": true,
  "origin_main": "75523965624212236f4944f77ebcbf22e131b5cb",
  "stage": "A7PM-0",
  "stage_count": 241
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
| hold                         | hold                       |      41 |
| hold                         | diagnostic                 |       6 |
| hold                         | alpha_claim_check_required |       2 |
| hold                         | contract                   |       2 |
| not_authorized               | hold                       |       2 |
| superseded_diagnostic        | contract                   |       1 |
| valid_or_historical_record   | governance_or_audit        |     107 |
| valid_or_historical_record   | contract                   |      48 |
| valid_or_historical_record   | smoke                      |       8 |
| valid_or_historical_record   | diagnostic                 |       7 |
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
  "A7FF-41": "not authorized by A7FF-40 because selected control-strict non-L7 evidence is still single-family",
  "A7FF-43": "not authorized by A7FF-42 because selected control-strict non-L7 evidence is still single-family",
  "A7FF-45": "not authorized by A7FF-44 because bounded deep replay queue is single-family after reference/regime filtering",
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
  "A7FF-24R4": "repaired-queue numeric wave contract after A7FF-24R3 dense materializer preflight; no search",
  "A7FF-R9": "reference/regime repair after A7FF-44 bounded queue single-family hold; no search",
  "A7PM-0/3 maintenance": "keep source-of-truth and experiment board current"
}
```

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7AL-2P2 is superseded diagnostic; A7AL-2Q is not authorized.
A7AL-2Z0-Z9 are engineering diagnostics with signal hold.
```
