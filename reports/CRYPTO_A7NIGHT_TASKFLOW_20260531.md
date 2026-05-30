# CRYPTO A7 NIGHT TASKFLOW 20260531

Generated: 2026-05-30T19:13:49Z

## Decision

`PASS_A7NIGHT_TASKFLOW_READY`

This night taskflow packages the currently authorized long-task direction without starting unauthorized generation or search. It keeps artifacts compact.

## Manifest

```json
{
  "artifact_budget": {
    "reports": 1,
    "runtime_files": 3,
    "scripts": 1
  },
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "contracts": [
    "A7FF-51",
    "A7FF-24R4"
  ],
  "decision": "PASS_A7NIGHT_TASKFLOW_READY",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T19:13:49Z",
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
| git_head_equals_origin_main_before_night_commit | True    | head=91a4732d1204d6d91fbca6913e1764a334a20ef1; origin=91a4732d1204d6d91fbca6913e1764a334a20ef1  | True   |
| working_tree_has_only_expected_night_artifacts  | True    | only A7NIGHT self artifacts are dirty                                                           | True   |
| a7ff51_contract_allowed_by_pm3                  | True    | compact non-L5-first derived generation contract after A7FF-R11; no execution/search            | True   |
| a7ff24r4_allowed_by_pm3                         | True    | repaired-queue numeric wave contract after A7FF-24R3 dense materializer preflight; no search    | True   |
| a7ffr11_authorizes_contract_only                | True    | PASS_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_READY_FOR_A7FF51_CONTRACT_NO_SEARCH_AUTH             | True   |
| a7ff24r3_authorizes_contract_only               | True    | PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH | True   |
| global_search_not_authorized                    | True    | A7FF-R11 and A7FF-24R3 both deny search                                                         | True   |

## Execution Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
