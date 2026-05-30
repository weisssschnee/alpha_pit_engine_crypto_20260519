# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD

Generated: 2026-05-30T10:18:13Z

## Decision

`PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT`

## Active Workstreams

| workstream              | current_stage   | status                                                     | next                                  |
|:------------------------|:----------------|:-----------------------------------------------------------|:--------------------------------------|
| governance              | A7PM-0/1/2/3    | pass                                                       | keep registry as source-of-truth      |
| a7ff_candidate_forensic | A7FF-29         | pass_portfolio_contract_allowed_with_concentration_warning | A7FF-30 portfolio replay contract     |
| a7ff_funding_tail       | A7FF-25R6       | pass_queue_repair_allowed                                  | A7FF-24R2 repaired queue tail rebuild |
| search_execution        | blocked         | not_authorized                                             | none                                  |

## Allowed Next Tasks

| task                 | reason                                                                                              |
|:---------------------|:----------------------------------------------------------------------------------------------------|
| A7FF-30              | portfolio replay contract for the frozen A7FF-29 six-candidate queue; no search                     |
| A7FF-24R2            | repaired company queue tail rebuild using dense funding-state fields or healthy backfill; no search |
| A7PM-0/3 maintenance | governance registry maintenance                                                                     |

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
The next technical work is A7FF-30 portfolio replay contract and A7FF-24R2 repaired queue tail rebuild.
```
