# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-05-29T13:53:58Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream        | current_stage               | status         | next                                  |
|:------------------|:----------------------------|:---------------|:--------------------------------------|
| governance        | A7PM-0/1/2/3                | pass           | keep registry as source-of-truth      |
| field_enforcement | A7AI-F0/F1                  | pass           | A7AI-F2 regression                    |
| replay_parity     | A7AR-2 plus pending A7AI-F3 | allowed_next   | materialization/evaluator parity      |
| response_map      | A7AA/A7AH                   | allowed_next   | primitive response and label adequacy |
| search_execution  | blocked                     | not_authorized | none                                  |

## Allowed Next Tasks

| task                   | reason                                    |
|:-----------------------|:------------------------------------------|
| A7AI-F2                | end-to-end field enforcement regression   |
| A7AI-F3                | materialization/evaluator parity sprint   |
| A7AA                   | primitive response / label adequacy audit |
| A7PM-1/2/3 maintenance | governance registry maintenance           |

## Blocked Tasks

| task                  | reason                                 |
|:----------------------|:---------------------------------------|
| A7AL-2Y generation    | not authorized                         |
| A7AL-3 large search   | not authorized                         |
| direct OI-price rerun | superseded weak prior / not authorized |
| A7AL-2Q               | not authorized by A7AL-2X0             |
| alpha proof           | not authorized                         |
| shadow/paper/live     | not authorized                         |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
The next technical work is A7AI-F2/F3 and A7AA response/label adequacy.
```
