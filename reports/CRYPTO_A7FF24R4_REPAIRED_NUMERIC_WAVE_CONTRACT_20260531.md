# CRYPTO A7FF-24R4 REPAIRED NUMERIC WAVE CONTRACT

Generated: 2026-05-30T19:23:03Z

## Decision

`PASS_A7FF24R4_REPAIRED_NUMERIC_WAVE_CONTRACT_READY_NO_EXECUTION_AUTH`

This is a contract-only stage. It defines the repaired 2400-row numeric wave but does not start it.

## Contract

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric_wave_execution": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF24R4_CONTRACT_READY",
  "execution_budget_if_later_approved": {
    "max_reports": 1,
    "max_runtime_tables": 3,
    "max_scripts": 1,
    "queue_rows": 2400,
    "shards": 12
  },
  "hard_gates": {
    "control_ratio_max_for_candidates": "< 0.80",
    "eval_failure_count": 0,
    "missing_numeric_fields": 0,
    "non_l7_numeric_clue_rows": "> 0",
    "tail_raw_funding_rate_rows": 0
  },
  "hard_stop_before": [
    "formula search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "name": "repaired queue numeric wave execution contract",
  "preconditions_confirmed": {
    "dense_materializer_preflight_pass": true,
    "dense_tail_activity_ok_count": 78,
    "eval_failure_count": 0,
    "raw_funding_rate_tail_rows": 0
  },
  "purpose": "define repaired 2400-row numeric wave without starting it",
  "source": "A7FF-24R3",
  "stage": "A7FF-24R4"
}
```

## Boundary

```text
numeric wave executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
