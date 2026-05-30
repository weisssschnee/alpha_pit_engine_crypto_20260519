# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY

Generated: 2026-05-30T05:52:38Z

## Decision

`PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT`

A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.

## Git State

```text
## main...origin/main
?? reports/CRYPTO_A7FFR0_DERIVED_GENERATION_FAILURE_FREEZE_20260530.md
?? reports/CRYPTO_A7FFR1_FIELD_ONTOLOGY_V3_20260530.md
?? reports/CRYPTO_A7FFR2_OPERATOR_PROBING_V2_20260530.md
?? reports/CRYPTO_A7FFR3_FEATURE_PAIR_POLICY_V2_20260530.md
?? reports/CRYPTO_A7FFR4_COARSE_TO_FINE_GENERATION_REDESIGN_20260530.md
?? reports/CRYPTO_A7FFR5_RESPONSE_BACKED_PROMOTION_REDESIGN_20260530.md
?? runtime/a7ffr0_derived_generation_failure_freeze/
?? runtime/a7ffr1_field_ontology_v3/
?? runtime/a7ffr2_operator_probing_v2/
?? runtime/a7ffr3_feature_pair_policy_v2/
?? runtime/a7ffr4_coarse_to_fine_generation_redesign/
?? runtime/a7ffr5_response_backed_promotion_redesign/
?? scripts/crypto_a7ffr_derived_generation_redesign.py
HEAD=1427c3470f64688646bb92bb4c4446562d5f103e
origin/main=1427c3470f64688646bb92bb4c4446562d5f103e
HEAD == origin/main: True
```

## Manifest

```json
{
  "artifact_count": 1702,
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
  "generated_at": "2026-05-30T05:52:38Z",
  "head": "1427c3470f64688646bb92bb4c4446562d5f103e",
  "head_equals_origin_main": true,
  "origin_main": "1427c3470f64688646bb92bb4c4446562d5f103e",
  "stage": "A7PM-0",
  "stage_count": 205
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
| hold                         | hold                       |      38 |
| hold                         | diagnostic                 |       4 |
| hold                         | alpha_claim_check_required |       2 |
| hold                         | contract                   |       2 |
| not_authorized               | hold                       |       2 |
| superseded_diagnostic        | contract                   |       1 |
| valid_or_historical_record   | governance_or_audit        |      87 |
| valid_or_historical_record   | contract                   |      40 |
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
