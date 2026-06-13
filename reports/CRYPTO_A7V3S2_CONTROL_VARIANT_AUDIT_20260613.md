# CRYPTO A7V3S2 Control Variant Audit

Generated: `2026-06-13T13:37:45Z`

## Decision

`PASS_A7V3S2_CONTROL_VARIANT_AUDIT_BUILT`

This audit checks whether reward-accepted numeric probes beat lag, stale, time-shuffle, symbol-shuffle, and sign-flip variants on OOS and stress windows.

## Counts

- audited candidates: `17`
- advance deep replay: `0`

## Control Decisions

| decision               |   count |
|:-----------------------|--------:|
| HOLD_CONTROL_DOMINATED |      12 |
| HOLD_STRESS_WEAK       |       5 |

## Control Flags

| control_audit_flags            |   count |
|:-------------------------------|--------:|
| lag_or_stale_dominated         |      17 |
| stress_floor_not_positive      |      13 |
| control_dominated_oos_majority |      12 |
| shuffle_dominated              |       7 |
| control_dominated_oos_partial  |       5 |

## Pair/Motif Summary

| semantic_pair              | motif                      | control_audit_decision   |   candidates |   median_control_margin |   min_stress_floor |
|:---------------------------|:---------------------------|:-------------------------|-------------:|------------------------:|-------------------:|
| positioning|universe_state | state_conditioned_signed   | HOLD_CONTROL_DOMINATED   |            2 |             -0.157327   |          -1.11613  |
| age|positioning            | smooth_mul                 | HOLD_CONTROL_DOMINATED   |            2 |             -0.260206   |          -0.966633 |
| age|positioning            | safe_div_abs               | HOLD_CONTROL_DOMINATED   |            2 |             -0.438301   |           5.59519  |
| age|positioning            | state_conditioned_signed   | HOLD_CONTROL_DOMINATED   |            2 |             -0.560769   |          -1.11613  |
| age|positioning            | smooth_mul                 | HOLD_STRESS_WEAK         |            1 |              0.0410169  |          -0.12939  |
| positioning|universe_state | smooth_mul                 | HOLD_STRESS_WEAK         |            1 |              0.0336798  |          -1.11613  |
| positioning|universe_state | spread_rank                | HOLD_STRESS_WEAK         |            1 |              0.0336798  |          -1.11613  |
| positioning|positioning    | signed_rank_gate           | HOLD_STRESS_WEAK         |            1 |              0.0223943  |          -1.4255   |
| open_interest|regime       | safe_div_abs               | HOLD_STRESS_WEAK         |            1 |              0.00426486 |          -1.1405   |
| open_interest|positioning  | smooth_mul                 | HOLD_CONTROL_DOMINATED   |            1 |             -0.0670335  |          -1.34229  |
| open_interest|positioning  | safe_div_abs               | HOLD_CONTROL_DOMINATED   |            1 |             -0.152036   |          -0.396593 |
| open_interest|positioning  | spread_rank                | HOLD_CONTROL_DOMINATED   |            1 |             -0.164608   |           5.53063  |
| positioning|universe_state | state_conditioned_rank_mul | HOLD_CONTROL_DOMINATED   |            1 |             -0.307305   |          -0.979968 |

## Candidate Audit

| control_audit_decision   | semantic_pair              | motif                      |   horizon_h |   min_oos_original_floor_sortino |   median_oos_control_margin_floor_sortino |   stress_floor_sortino |   dominated_oos_split_count | control_audit_flags                                                                               | expression                                                                                                   |
|:-------------------------|:---------------------------|:---------------------------|------------:|---------------------------------:|------------------------------------------:|-----------------------:|----------------------------:|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------|
| HOLD_CONTROL_DOMINATED   | open_interest|positioning  | smooth_mul                 |           4 |                       2.54495    |                               -0.0670335  |              -1.34229  |                           2 | control_dominated_oos_majority;lag_or_stale_dominated;stress_floor_not_positive                   | Mul(Decay(account_position_divergence,3),Abs(ZScore(Mean(open_interest_value_mean,4))))                      |
| HOLD_CONTROL_DOMINATED   | open_interest|positioning  | safe_div_abs               |           4 |                       1.86521    |                               -0.152036   |              -0.396593 |                           2 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive | SafeDiv(ZScore(Mean(account_position_divergence,3)),Abs(Abs(ZScore(Mean(open_interest_mean,3)))))            |
| HOLD_STRESS_WEAK         | positioning|positioning    | signed_rank_gate           |          24 |                       1.14392    |                                0.0223943  |              -1.4255   |                           1 | control_dominated_oos_partial;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive  | Mul(CSRank(ZScore(Mean(top_global_account_divergence,3))),Sign(ZScore(Mean(account_position_divergence,3)))) |
| HOLD_STRESS_WEAK         | open_interest|regime       | safe_div_abs               |           4 |                       1.79882    |                                0.00426486 |              -1.1405   |                           1 | control_dominated_oos_partial;lag_or_stale_dominated;stress_floor_not_positive                    | SafeDiv(Abs(ZScore(Mean(open_interest_value_last,336))),Abs(Decay(basis_dislocation_state,720)))             |
| HOLD_CONTROL_DOMINATED   | open_interest|positioning  | spread_rank                |           4 |                       0.00251951 |                               -0.164608   |               5.53063  |                           2 | control_dominated_oos_majority;lag_or_stale_dominated                                             | Sub(CSRank(Decay(open_interest_value_mean,4)),CSRank(Abs(ZScore(Mean(account_position_divergence,3)))))      |
| HOLD_CONTROL_DOMINATED   | age|positioning            | safe_div_abs               |          24 |                       6.41663    |                               -0.782789   |               5.59519  |                           3 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated                           | SafeDiv(Sign(TSRank(listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                          |
| HOLD_CONTROL_DOMINATED   | age|positioning            | safe_div_abs               |          24 |                       6.41663    |                               -0.0938138  |               5.59519  |                           2 | control_dominated_oos_majority;lag_or_stale_dominated                                             | SafeDiv(Sign(TSRank(sqrt_listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                     |
| HOLD_STRESS_WEAK         | positioning|universe_state | smooth_mul                 |           4 |                       2.66725    |                                0.0336798  |              -1.11613  |                           1 | control_dominated_oos_partial;lag_or_stale_dominated;stress_floor_not_positive                    | Mul(ZScore(Mean(account_position_divergence,3)),CSRank(active_universe_size))                                |
| HOLD_CONTROL_DOMINATED   | positioning|universe_state | state_conditioned_rank_mul |           4 |                       2.59032    |                               -0.307305   |              -0.979968 |                           2 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive | Mul(CSRank(Decay(account_position_divergence,3)),CSRank(CSRank(active_universe_size)))                       |
| HOLD_CONTROL_DOMINATED   | age|positioning            | state_conditioned_signed   |           4 |                       2.66725    |                               -0.093637   |              -1.11613  |                           2 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive | Mul(ZScore(Mean(account_position_divergence,3)),Sign(CSRank(log1p_listing_age_days)))                        |
| HOLD_STRESS_WEAK         | positioning|universe_state | spread_rank                |           4 |                       2.66725    |                                0.0336798  |              -1.11613  |                           1 | control_dominated_oos_partial;lag_or_stale_dominated;stress_floor_not_positive                    | Sub(CSRank(Sign(TSRank(active_universe_size,6))),CSRank(ZScore(Mean(account_position_divergence,3))))        |
| HOLD_CONTROL_DOMINATED   | positioning|universe_state | state_conditioned_signed   |           4 |                       2.66725    |                               -0.093637   |              -1.11613  |                           2 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive | Mul(ZScore(Mean(account_position_divergence,3)),Sign(Sign(TSRank(active_universe_size,6))))                  |
| HOLD_CONTROL_DOMINATED   | age|positioning            | smooth_mul                 |           4 |                       2.54337    |                               -0.28741    |              -0.966633 |                           2 | control_dominated_oos_majority;lag_or_stale_dominated;stress_floor_not_positive                   | Mul(Decay(log1p_listing_age_days,3),Decay(account_position_divergence,3))                                    |
| HOLD_CONTROL_DOMINATED   | positioning|universe_state | state_conditioned_signed   |           4 |                       2.59032    |                               -0.221017   |              -0.979968 |                           2 | control_dominated_oos_majority;lag_or_stale_dominated;stress_floor_not_positive                   | Mul(Decay(account_position_divergence,3),Sign(CSRank(active_universe_size)))                                 |
| HOLD_CONTROL_DOMINATED   | age|positioning            | state_conditioned_signed   |           4 |                       0.770809   |                               -1.0279     |               4.04345  |                           2 | control_dominated_oos_majority;lag_or_stale_dominated                                             | Mul(Sign(TSRank(sqrt_listing_age_days,4)),Sign(ZScore(Mean(account_position_divergence,3))))                 |
| HOLD_CONTROL_DOMINATED   | age|positioning            | smooth_mul                 |          24 |                       0.381593   |                               -0.233001   |              -0.12939  |                           2 | control_dominated_oos_majority;shuffle_dominated;lag_or_stale_dominated;stress_floor_not_positive | Mul(CSRank(log1p_listing_age_days),Abs(ZScore(Mean(account_position_divergence,3))))                         |
| HOLD_STRESS_WEAK         | age|positioning            | smooth_mul                 |          24 |                       0.381593   |                                0.0410169  |              -0.12939  |                           1 | control_dominated_oos_partial;lag_or_stale_dominated;stress_floor_not_positive                    | Mul(Abs(ZScore(Mean(account_position_divergence,3))),CSRank(log1p_listing_age_days))                         |

## Interpretation

- `ADVANCE_DEEP_REPLAY` requires positive OOS floor, no OOS majority control domination, and positive stress floor.
- `HOLD_CONTROL_DOMINATED` means controls explain the candidate at least as well on most OOS windows or original OOS floor is non-positive.
- `HOLD_STRESS_WEAK` means OOS may pass but May/stress floor fails.

## Outputs

- `control_audit`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_control_variant_audit.csv`
- `decision_summary`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_control_decision_summary.csv`
- `flag_summary`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_control_flag_summary.csv`
- `pair_summary`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_control_pair_summary.csv`
- `advance_queue`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_advance_deep_replay_queue.csv`
- `manifest`: `runtime\a7v3s2_control_variant_audit_20260613\a7v3s2_manifest.json`
