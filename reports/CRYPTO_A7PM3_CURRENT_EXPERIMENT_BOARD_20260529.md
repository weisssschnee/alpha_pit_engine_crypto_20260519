# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-05-30T09:09:18Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream        | current_stage   | status                        | next                                      |
|:------------------|:----------------|:------------------------------|:------------------------------------------|
| governance        | A7PM-0/1/2/3    | pass                          | keep registry as source-of-truth          |
| a7ff_numeric_wave | A7FF-25R4       | pass_repair_required          | A7FF-25R5 funding-state tail queue repair |
| a7ff_clue_triage  | A7FF-26         | pass_replay_preflight_allowed | A7FF-27 replay preflight                  |
| search_execution  | blocked         | not_authorized                | none                                      |

## Allowed Next Tasks

| task                 | reason                                                                 |
|:---------------------|:-----------------------------------------------------------------------|
| A7FF-27              | replay preflight for promotion-ready numeric research clues; no search |
| A7FF-25R5            | funding-state tail queue repair contract; no search                    |
| A7PM-0/3 maintenance | governance registry maintenance                                        |

## Blocked Tasks

| task                  | reason                                                          |
|:----------------------|:----------------------------------------------------------------|
| A7FF search execution | numeric wave has clues but still no replay/search authorization |
| A7AL-2Y generation    | not authorized                                                  |
| A7AL-3 large search   | not authorized                                                  |
| direct OI-price rerun | superseded weak prior / not authorized                          |
| A7AL-2Q               | not authorized by A7AL-2X0                                      |
| alpha proof           | not authorized                                                  |
| shadow/paper/live     | not authorized                                                  |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
The next technical work is A7AI-F2/F3 and A7AA response/label adequacy.
```
