# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-06-06T05:10:46Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream                  | current_stage   | status                         | next                                   |
|:----------------------------|:----------------|:-------------------------------|:---------------------------------------|
| governance                  | A7PM-0/1/2/3    | pass                           | keep registry as source-of-truth       |
| a7ff_family_diversification | A7LS-16         | local_schema_preflight_pass    | A7LS17 company sharded materialization |
| a7ls_scaled_search          | A7LS-14X        | scoped_large_search_authorized | A7LS15/A7LS16/A7LS17/A7LS18 pipeline   |
| a7ff_funding_tail           | A7FF-24R4       | contract_ready_no_execution    | A7FF-24R4E if explicitly authorized    |
| search_execution            | A7LS-16         | local_schema_preflight_pass    | A7LS17 company sharded materialization |

## Allowed Next Tasks

| task                                          | reason                                                                     |
|:----------------------------------------------|:---------------------------------------------------------------------------|
| A7LS17 company sharded materialization        | authorized by A7LS16; materialization_total <= 100,000                     |
| A7LS18 company sharded numeric wave           | authorized after A7LS17; numeric_total <= 25,000; 256 shards; checkpointed |
| A7LS19 checkpoint arbitration and lane resize | authorized after A7LS18 checkpoints; continue / kill / expand per lane     |
| A7PM-0/3 maintenance                          | keep A7LS scoped large-search authorization current                        |

## Blocked Tasks

| task                         | reason                                                             |
|:-----------------------------|:-------------------------------------------------------------------|
| large_search_outside_A7LS14  | blocked: A7LS-14X authorizes only checkpointed A7LS15-A7LS18 scope |
| unbounded_full_grammar       | blocked                                                            |
| single_lane_budget_capture   | blocked by A7LS14 quota/checkpoint policy                          |
| May-informed selector/reward | blocked                                                            |
| alpha proof                  | not authorized                                                     |
| shadow/paper/live            | not authorized                                                     |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-52E materialization is complete if present in the source-of-truth registry. Next A7FF step is contract-only unless explicitly authorized.
```
