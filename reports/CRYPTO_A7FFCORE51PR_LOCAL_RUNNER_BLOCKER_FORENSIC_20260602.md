# CRYPTO A7FF-CORE51PR LOCAL RUNNER BLOCKER FORENSIC

Generated: 2026-06-02T02:21:41Z

## Decision

`HOLD_A7FFCORE51PR_LOCAL_REPLAY_RUNNER_INSUFFICIENT_USE_COMPANY_SHARDS`

The filtered replay candidate pool is not rejected. Local pandas replay execution is rejected after both naive and dense-matrix 16-candidate smokes timed out. Next work must move to a company-machine sharded runner with compact frame and incremental outputs.

## Attempts

| attempt_id             |   candidate_count |   timeout_seconds | result   | dominant_issue                                                                                |
|:-----------------------|------------------:|------------------:|:---------|:----------------------------------------------------------------------------------------------|
| A0_naive_runner        |                16 |              1200 | timeout  | repeated full-frame groupby/rank                                                              |
| A1_dense_matrix_runner |                16 |               900 | timeout  | full-frame load/materialization plus dense control matrix construction still too slow locally |

## Route Decision

| route_id                          | decision   | reason                                                                                    |
|:----------------------------------|:-----------|:------------------------------------------------------------------------------------------|
| R0_local_pandas_retry             | REJECT     | two 16-candidate smokes timed out; local retry wastes time                                |
| R1_company_machine_sharded_runner | SELECT     | parallel shard execution and higher memory are required for 384-candidate filtered replay |
| R2_compact_replay_frame           | REQUIRED   | prebuild compact label/feature frame and per-shard candidate files before replay          |

## Company Runner Requirements

| requirement         | value                                                          |
|:--------------------|:---------------------------------------------------------------|
| shard_count         | at least 16 candidate shards, <=24 candidates/shard            |
| compact_frame       | symbol/timestamp/trade_close/split/needed feature columns only |
| incremental_outputs | write per-shard metrics before aggregation; resume-safe        |
| controls            | original/stale/time/symbol/sign controls required              |
| authorization       | no search/proof/promotion; replay diagnostics only             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE51PX company-machine sharded replay runner contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "local_runner_retry": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core51px_company_sharded_runner_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE51PR_LOCAL_REPLAY_RUNNER_INSUFFICIENT_USE_COMPANY_SHARDS",
  "dominant_failure": "local_runner_timeout_after_naive_and_dense_attempts",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T02:21:41Z",
  "next_allowed": "A7FF-CORE51PX company-machine sharded replay runner contract",
  "source_decision": "HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER",
  "source_stage": "A7FF-CORE51ER",
  "stage": "A7FF-CORE51PR"
}
```
