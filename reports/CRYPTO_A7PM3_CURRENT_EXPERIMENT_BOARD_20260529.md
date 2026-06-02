# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-06-02T02:23:57Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream                  | current_stage   | status                                         | next                                                         |
|:----------------------------|:----------------|:-----------------------------------------------|:-------------------------------------------------------------|
| governance                  | A7PM-0/1/2/3    | pass                                           | keep registry as source-of-truth                             |
| a7ff_family_diversification | A7FF-CORE51PR   | local_replay_runner_blocked_use_company_shards | A7FF-CORE51PX company-machine sharded replay runner contract |
| a7ff_funding_tail           | A7FF-24R4       | contract_ready_no_execution                    | A7FF-24R4E if explicitly authorized                          |
| search_execution            | blocked         | not_authorized                                 | none                                                         |

## Allowed Next Tasks

| task                                                         | reason                                                                                                                     |
|:-------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|
| A7FF-24R4E repaired numeric wave execution option            | requires explicit user authorization; no search and no promotion                                                           |
| A7PM-0/3 maintenance                                         | governance registry maintenance                                                                                            |
| A7FF-CORE51PX company-machine sharded replay runner contract | contract/deployment design only; move filtered replay to company-machine shards with compact frame and incremental outputs |

## Blocked Tasks

| task                                | reason                                                                                                                |
|:------------------------------------|:----------------------------------------------------------------------------------------------------------------------|
| A7FF-24R4E execution                | pending explicit heavy-execution authorization; A7FF-24R4 contract is ready but numeric wave execution is not started |
| A7FF-51 execution                   | not authorized by A7FF-R11; only contract drafting is allowed                                                         |
| A7FF-50                             | not authorized by A7FF-49; no non-reference non-L5 candidates exist in current maps                                   |
| A7FF-48                             | not authorized by A7FF-47; frozen clues fail non-L5 label translation                                                 |
| A7FF-45 continuation                | bounded replay passed but is superseded by A7FF-47 L5-only translation hold                                           |
| A7FF-43 deep forensic               | not authorized by A7FF-42; selected control-strict non-L7 evidence remains single-family                              |
| A7FF-41 control-strict expansion    | not authorized by A7FF-40; selected control-strict non-L7 evidence remains single-family                              |
| A7FF search execution               | numeric wave has clues but still no replay/search authorization                                                       |
| A7AL-2Y generation                  | not authorized                                                                                                        |
| A7AL-3 large search                 | not authorized                                                                                                        |
| direct OI-price rerun               | superseded weak prior / not authorized                                                                                |
| A7AL-2Q                             | not authorized by A7AL-2X0                                                                                            |
| alpha proof                         | not authorized                                                                                                        |
| shadow/paper/live                   | not authorized                                                                                                        |
| A7FF-CORE51E local runner retry     | blocked: local naive and dense-matrix smokes timed out                                                                |
| A7FF large search                   | blocked: replay runner must move to company-machine shards first                                                      |
| A7FF formula search                 | blocked                                                                                                               |
| alpha proof / shadow / paper / live | not authorized                                                                                                        |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-52E materialization is complete if present in the source-of-truth registry. Next A7FF step is contract-only unless explicitly authorized.
```
