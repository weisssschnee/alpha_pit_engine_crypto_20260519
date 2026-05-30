# CRYPTO A7FF-52 MATERIALIZATION PREFLIGHT CONTRACT

Generated: 2026-05-30T19:36:38Z

## Decision

`PASS_A7FF52_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_NO_EXECUTION_AUTH`

This is a contract-only stage for the A7FF51E 50,000-blueprint queue. It does not start materialization, numeric replay, or search.

## Contract

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_materialization_preflight_execution": false,
  "authorizes_numeric_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF52_CONTRACT_READY",
  "execution_budget_if_later_approved": {
    "family_balanced": true,
    "max_reports": 1,
    "max_runtime_tables": 3,
    "max_scripts": 1,
    "min_rows_per_semantic_family": 100,
    "sample_rows": 1200
  },
  "hard_gates": {
    "activity_ok_rate": ">= 0.60",
    "eval_failure_count": 0,
    "families_retained": ">= 6",
    "missing_field_count": 0,
    "reference_family_primary_rows": 0,
    "unsupported_operator_count": 0
  },
  "hard_stop_before": [
    "numeric replay",
    "formula search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "input_queue": "runtime/a7ff51e_non_l5_heavy_generation/a7ff51e_blueprint_queue.csv",
  "name": "materialization preflight contract for A7FF51E blueprints",
  "purpose": "define bounded materialization preflight before any numeric replay",
  "source": "A7FF-51E",
  "stage": "A7FF-52"
}
```

## Boundary

```text
materialization executed: false
numeric replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
