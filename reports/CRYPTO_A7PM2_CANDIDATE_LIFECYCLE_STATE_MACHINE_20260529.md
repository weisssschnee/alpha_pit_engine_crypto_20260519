# CRYPTO A7PM-2 CANDIDATE LIFECYCLE STATE MACHINE

Generated: 2026-05-29T13:53:58Z

## Decision

`PASS_A7PM2_CANDIDATE_LIFECYCLE_STATE_MACHINE_BUILT`

## State Dictionary

| state                | definition                                           |
|:---------------------|:-----------------------------------------------------|
| generated            | formula/expression exists but has no evidence        |
| materialized         | expression evaluated into numeric signal             |
| fast_replayed        | candidate passed fast replay diagnostic              |
| control_clean        | matched controls are weaker                          |
| neutralization_clean | survives required neutralization                     |
| latency_clean        | field-native timing and wrong-lag checks pass        |
| overlap_robust       | overlap-robust/non-overlap statistics pass           |
| cluster_registered   | signal-vector/formula cluster recorded               |
| deep_audited         | deep audit completed                                 |
| diagnostic_clue      | diagnostic evidence only; no promotion               |
| research_candidate   | research-stage candidate after all non-trading gates |
| rejected             | blocked by any hard gate                             |
| superseded           | replaced by newer source-of-truth arbitration        |
| paper_candidate      | future paper authorization only                      |
| shadow_candidate     | future shadow authorization only                     |
| live_candidate       | future live authorization only                       |

## Forbidden Transitions

| from_state         | to_state           | reason                                                          |
|:-------------------|:-------------------|:----------------------------------------------------------------|
| diagnostic_clue    | shadow_candidate   | diagnostic cannot skip research/paper gates                     |
| diagnostic_clue    | live_candidate     | diagnostic cannot skip research/paper/shadow gates              |
| generated          | research_candidate | must materialize/replay/audit first                             |
| control_clean      | research_candidate | must pass neutralization/latency/cluster/deep audit             |
| superseded         | generated          | superseded artifacts cannot be selector source-of-truth         |
| rejected           | research_candidate | rejected candidates require fresh generation and full gate path |
| deep_audited       | shadow_candidate   | deep audit is not trading authorization                         |
| research_candidate | live_candidate     | must pass paper/shadow gates                                    |

## Promotion Gates

| gate                   | required_for         | hard_fail_state             |
|:-----------------------|:---------------------|:----------------------------|
| field_role_enforcement | materialized         | rejected                    |
| control_dominance      | control_clean        | rejected                    |
| neutralization         | neutralization_clean | diagnostic_clue_or_rejected |
| latency_wrong_lag      | latency_clean        | rejected                    |
| overlap_robust_stats   | overlap_robust       | diagnostic_clue_or_rejected |
| cluster_diversity      | cluster_registered   | diagnostic_clue             |
| deep_audit             | research_candidate   | diagnostic_clue_or_rejected |
| explicit_authorization | paper/shadow/live    | not_authorized              |

## Boundary

```text
diagnostic_clue cannot directly become shadow/live.
control dominated candidates cannot become research_candidate.
stress-vetoed or superseded artifacts cannot seed expansion unless a new contract explicitly reclassifies them.
```
