# Crypto A7P-2 Runner Gate Preflight

- generated_at: `2026-05-20T18:17:59Z`
- decision: `PASS_A7P2A_A7P2B_RUNNER_PREFLIGHT`
- preflight_only: `True`
- authorizes_w2: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Checks

| check                                     | value   |
|:------------------------------------------|:--------|
| active_hour_count_in_split_metrics        | True    |
| active_hour_count_in_fold_metrics         | True    |
| strict_negative_control_blocker_triggered | True    |
| negative_control_dominance_audit_written  | True    |
| may_policy_unchanged                      | True    |

## Active-Hour Metric Audit

| artifact            |   rows | has_active_hour_count   |   min_active_hour_count |   max_active_hour_count |
|:--------------------|-------:|:------------------------|------------------------:|------------------------:|
| split_metrics       |   1440 | True                    |                       0 |                    7248 |
| fold_replay_metrics |   1248 | True                    |                       0 |                    7248 |

## Negative-Control Dominance Audit

| control_candidate_id   | control_cell_id   | control_signal_mode   | control_source_field_families   | dominance_scope                          |   matched_normal_count |   blocked_normal_count |   control_score | may_used_for_dominance   |
|:-----------------------|:------------------|:----------------------|:--------------------------------|:-----------------------------------------|-----------------------:|-----------------------:|----------------:|:-------------------------|
| a7o_l1_C0208_1344      | C0208             | wrong_lag_stale_24h   | liquidity;volatility            | same_cell                                |                      0 |                      0 |       -0.138524 | False                    |
| a7o_l1_C0208_1344      | C0208             | wrong_lag_stale_24h   | liquidity;volatility            | same_hypothesis_feature_operator_horizon |                      0 |                      0 |       -0.138524 | False                    |

## Boundary

A7P-2A/B preflight verifies runner instrumentation only. W2 remains blocked until A7P-2C/D/E complete.