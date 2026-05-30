# CRYPTO A7 NIGHT TASKFLOW 20260531

Generated: 2026-05-30T19:26:25Z

## Decision

`PASS_A7NIGHT_TASKFLOW_READY`

This night taskflow packages the currently authorized long-task direction without starting unauthorized generation or search. It keeps artifacts compact.

## Manifest

```json
{
  "approval_required_for_heavy_execution": true,
  "artifact_budget": {
    "reports": 1,
    "runtime_files": 4,
    "scripts": 1
  },
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "contract_work_can_continue_without_approval": true,
  "contracts": [
    "A7FF-51",
    "A7FF-24R4"
  ],
  "decision": "PASS_A7NIGHT_TASKFLOW_READY",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T19:26:25Z",
  "recommended_approval": "APPROVE_A7FF51E_NON_L5_FIRST_HEAVY_GENERATION_ONLY",
  "stage": "A7NIGHT-20260531"
}
```

## Contracts

```json
{
  "A7FF-24R4": {
    "artifact_budget": {
      "max_new_reports": 1,
      "max_new_runtime_tables": 3,
      "required_manifest": true
    },
    "execution_authorized": false,
    "hard_gates": {
      "before_full_wave": [
        "queue coverage by shard and semantic pair",
        "no missing numeric fields",
        "no eval failures in preflight sample",
        "raw funding rate must remain absent from dense tail"
      ]
    },
    "name": "repaired-queue numeric wave contract",
    "preconditions": {
      "dense_materializer_preflight_pass": true,
      "dense_tail_activity_ok_count": 78,
      "eval_failure_count": 0,
      "raw_funding_rate_tail_rows": 0
    },
    "search_authorized": false,
    "source": "A7FF-24R3",
    "status": "contract_ready"
  },
  "A7FF-51": {
    "artifact_budget": {
      "max_new_reports": 1,
      "max_new_runtime_tables": 3,
      "required_manifest": true
    },
    "execution_authorized": false,
    "hard_gates": {
      "control_ratio_max": 0.8,
      "min_non_reference_families_before_replay": 2,
      "min_non_reference_rows_before_replay": 6,
      "reference_family_cannot_count_as_primary": true
    },
    "name": "compact non-L5-first derived generation contract",
    "primary_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return"
    ],
    "search_authorized": false,
    "source": "A7FF-R11",
    "status": "contract_ready"
  }
}
```

## Self Check

| check                                           | value   | detail                                                                                          | pass   |
|:------------------------------------------------|:--------|:------------------------------------------------------------------------------------------------|:-------|
| git_head_equals_origin_main_before_night_commit | True    | head=560477682a668ae7546a1ce9370daee5163cd487; origin=560477682a668ae7546a1ce9370daee5163cd487  | True   |
| working_tree_has_only_expected_night_artifacts  | True    | only A7NIGHT self artifacts are dirty                                                           | True   |
| a7ff51_path_present_in_pm3                      | True    | requires explicit user authorization; no search and hard stop before numeric replay             | True   |
| a7ff24r4_path_present_in_pm3                    | True    | requires explicit user authorization; no search and no promotion                                | True   |
| a7ffr11_authorizes_contract_only                | True    | PASS_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_READY_FOR_A7FF51_CONTRACT_NO_SEARCH_AUTH             | True   |
| a7ff24r3_authorizes_contract_only               | True    | PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH | True   |
| global_search_not_authorized                    | True    | A7FF-R11 and A7FF-24R3 both deny search                                                         | True   |

## Approval Required

I did not start a heavy run because the current source-of-truth only authorizes contracts. Contract drafting can continue without approval; heavy generation or numeric-wave execution requires one explicit execution option:

```json
{
  "contract_work_can_continue_without_approval": true,
  "explicit_user_approval_required_for_heavy_execution": true,
  "options": {
    "APPROVE_A7FF24R4_REPAIRED_QUEUE_NUMERIC_WAVE": {
      "budget": {
        "max_queue_rows": 2400,
        "max_reports": 1,
        "max_runtime_tables": 3,
        "shards": 12
      },
      "hard_stop_before": [
        "full search",
        "alpha proof",
        "shadow/paper/live"
      ],
      "success_gate": {
        "control_ratio_max_for_candidates": "< 0.80",
        "eval_failure_count": 0,
        "missing_numeric_fields": 0,
        "non_l7_numeric_clue_rows": "> 0"
      },
      "what_runs": [
        "bounded numeric wave over repaired A7FF-24R queue",
        "shard coverage audit",
        "failure-map only, no promotion"
      ]
    },
    "APPROVE_A7FF51E_NON_L5_FIRST_HEAVY_GENERATION_ONLY": {
      "budget": {
        "blueprint_target": 50000,
        "max_reports": 1,
        "max_runtime_tables": 3
      },
      "hard_stop_before": [
        "numeric replay",
        "formula search",
        "alpha proof",
        "shadow/paper/live"
      ],
      "success_gate": {
        "non_reference_non_l5_rows_before_replay": ">= 200 static candidates",
        "reference_family_counts_as_primary": false,
        "semantic_pair_families": ">= 6",
        "top_family_share": "<= 0.30"
      },
      "what_runs": [
        "non-L5-first derived blueprint generation",
        "static materialization-readiness audit",
        "queue coverage and family balance audit"
      ]
    },
    "APPROVE_BOTH_SEQUENTIAL": {
      "order": [
        "A7FF51E",
        "A7FF24R4"
      ],
      "reason": "keeps non-L5 objective reset as primary, with repaired queue numeric wave as secondary audit",
      "stop_rule": "if A7FF51E fails artifact or coverage gates, do not start A7FF24R4"
    },
    "DO_NOT_RUN_OVERNIGHT": {
      "reason": "keep repo frozen at contract-only state",
      "what_runs": []
    }
  },
  "recommended": "APPROVE_A7FF51E_NON_L5_FIRST_HEAVY_GENERATION_ONLY"
}
```

## Execution Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
