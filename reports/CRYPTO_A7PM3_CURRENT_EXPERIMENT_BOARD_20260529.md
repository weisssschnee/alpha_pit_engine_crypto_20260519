# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-06-06T07:08:40Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream                  | current_stage   | status                                         | next                                 |
|:----------------------------|:----------------|:-----------------------------------------------|:-------------------------------------|
| governance                  | A7PM-0/1/2/3    | pass                                           | keep registry as source-of-truth     |
| a7ff_family_diversification | A7LS-17         | company_materialization_pass_ready_for_numeric | A7LS18 company sharded numeric wave  |
| a7ls_scaled_search          | A7LS-14X        | scoped_large_search_authorized                 | A7LS15/A7LS16/A7LS17/A7LS18 pipeline |
| a7ff_funding_tail           | A7FF-24R4       | contract_ready_no_execution                    | A7FF-24R4E if explicitly authorized  |
| search_execution            | A7LS-17         | company_materialization_pass_ready_for_numeric | A7LS18 company sharded numeric wave  |

## Allowed Next Tasks

| task                                          | reason                                                                                                                    |
|:----------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------|
| A7LS18 company sharded numeric wave           | authorized by A7LS17 aggregate; numeric_total <= 100,000; checkpointed company-machine execution                          |
| A7LS19 checkpoint arbitration and lane resize | authorized after A7LS18 checkpoints; continue / kill / expand per lane                                                    |
| A7LS15X expansion queue generation            | authorized by A7LS16X if A7LS15 100k first wave is exhausted or checkpoint-positive; generated_total ceiling <= 4,000,000 |
| A7PM-0/3 maintenance                          | keep A7LS17/A7LS18 scoped large-search source-of-truth current                                                            |

## Blocked Tasks

| task                            | reason                                                                            |
|:--------------------------------|:----------------------------------------------------------------------------------|
| large_search_outside_A7LS_scope | blocked: A7LS-14X/A7LS-16X authorize only checkpointed A7LS company-machine scope |
| unbounded_full_grammar          | blocked                                                                           |
| single_lane_budget_capture      | blocked by A7LS14 quota/checkpoint policy                                         |
| May-informed selector/reward    | blocked                                                                           |
| alpha proof                     | not authorized                                                                    |
| shadow/paper/live               | not authorized                                                                    |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-52E materialization is complete if present in the source-of-truth registry. Next A7FF step is contract-only unless explicitly authorized.
```
