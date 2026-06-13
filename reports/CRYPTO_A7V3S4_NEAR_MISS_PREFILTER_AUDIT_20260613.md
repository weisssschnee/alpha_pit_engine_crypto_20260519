# CRYPTO A7V3S4 Near-Miss Prefilter Audit - 20260613

## Decision

`PASS_A7V3S4_PREFILTER_RULES_BUILT`

A7V3S4 audits the A7V3S3 strict-reward early-stop rejections and converts the failure pattern into a pre-reward search-space filter. It does not authorize alpha proof, shadow, paper, or live execution.

## Input

- Rejection rows: `1152`
- Mechanism keep probes: `0`
- Control-polluted near misses: `10`
- Hard-block pair/motif rules: `30`
- Redesign-not-reward-as-is pair/motif rules: `6`

## Rejection Reasons

| reason                             |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |    1103 |
| oos_net_mean_not_all_positive      |    1049 |
| oos_control_dominated              |    1035 |
| oos_lag_stale_dominated            |     999 |
| oos_shuffle_dominated              |     836 |
| stress_floor_not_positive          |     823 |
| shuffle_control_dominated_recent   |     789 |
| recent_sortino_non_positive        |     647 |
| train_orientation_no_positive_edge |     596 |
| non_finite_diagnostic_composite    |       8 |

## Prefilter Classes

| prefilter_class            |   count |
|:---------------------------|--------:|
| dead_or_no_recent_edge     |     639 |
| recent_only_artifact       |     456 |
| stress_fragile_artifact    |      39 |
| control_polluted_near_miss |      10 |
| non_finite_invalid         |       8 |

## Pair/Motif Decisions

| semantic_pair                | motif                      |   rows |   mechanism_keep_probe |   control_polluted_near_miss |   control_dom_rate |   lag_stale_dom_rate |   median_min_oos_floor_sortino | prefilter_decision                    |
|:-----------------------------|:---------------------------|-------:|-----------------------:|-----------------------------:|-------------------:|---------------------:|-------------------------------:|:--------------------------------------|
| positioning\|positioning     | safe_div_abs               |     40 |                      0 |                            3 |           1        |             1        |                       -3.66428 | REDESIGN_NOT_REWARD_AS_IS             |
| open_interest\|positioning   | spread_rank                |      8 |                      0 |                            2 |           0.875    |             0.875    |                       -3.20111 | REDESIGN_NOT_REWARD_AS_IS             |
| basis\|taker_flow            | safe_div_abs               |     52 |                      0 |                            2 |           0.980769 |             0.942308 |                       -5.00396 | REDESIGN_NOT_REWARD_AS_IS             |
| positioning\|taker_flow      | safe_div_abs               |     84 |                      0 |                            1 |           1        |             0.952381 |                       -5.41251 | REDESIGN_NOT_REWARD_AS_IS             |
| basis\|positioning           | safe_div_abs               |     44 |                      0 |                            1 |           0.863636 |             0.840909 |                       -5.22597 | REDESIGN_NOT_REWARD_AS_IS             |
| basis\|basis                 | safe_div_abs               |     24 |                      0 |                            1 |           0.458333 |             0.416667 |                       -6.33297 | REDESIGN_NOT_REWARD_AS_IS             |
| liquidity\|open_interest     | signed_rank_gate           |      8 |                      0 |                            0 |           1        |             1        |                       -3.37157 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| funding_dense\|open_interest | smooth_mul                 |     16 |                      0 |                            0 |           1        |             1        |                       -5.37407 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| positioning\|positioning     | signed_rank_gate           |     16 |                      0 |                            0 |           1        |             1        |                       -5.93304 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| taker_flow\|taker_flow       | safe_div_abs               |      8 |                      0 |                            0 |           1        |             1        |                       -5.65146 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| liquidity\|liquidity         | smooth_mul                 |      4 |                      0 |                            0 |           1        |             1        |                       -4.86868 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| liquidity\|taker_flow        | safe_div_abs               |     24 |                      0 |                            0 |           0.875    |             0.833333 |                       -3.89498 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| funding_dense\|open_interest | spread_rank                |      4 |                      0 |                            0 |           1        |             1        |                       -2.77221 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| funding_dense\|premium       | spread_rank                |    100 |                      0 |                            0 |           0.91     |             0.87     |                       -7.23077 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| basis\|funding_dense         | spread_rank                |     56 |                      0 |                            0 |           0.803571 |             0.75     |                       -4.46753 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| funding_dense\|premium       | smooth_mul                 |     52 |                      0 |                            0 |           0.942308 |             0.903846 |                       -9.38117 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| funding_dense\|premium       | signed_rank_gate           |     48 |                      0 |                            0 |           0.895833 |             0.875    |                       -8.87985 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| liquidity\|positioning       | safe_div_abs               |     48 |                      0 |                            0 |           0.916667 |             0.895833 |                       -5.93723 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| funding_dense\|premium       | safe_div_abs               |     16 |                      0 |                            0 |           1        |             0.9375   |                       -7.4059  | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| liquidity\|premium           | signed_rank_gate           |     16 |                      0 |                            0 |           1        |             1        |                       -3.05578 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| positioning\|positioning     | smooth_mul                 |      8 |                      0 |                            0 |           1        |             1        |                       -4.50126 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| basis\|funding_dense         | signed_rank_gate           |      4 |                      0 |                            0 |           0.75     |             0.75     |                       -5.54585 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| funding_dense\|open_interest | safe_div_abs               |      4 |                      0 |                            0 |           1        |             1        |                       -3.56764 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| premium\|regime              | signed_rank_gate           |      4 |                      0 |                            0 |           1        |             1        |                       -5.90152 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| premium\|regime              | state_conditioned_rank_mul |      4 |                      0 |                            0 |           1        |             1        |                       -5.90152 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| open_interest\|positioning   | smooth_mul                 |     28 |                      0 |                            0 |           0.857143 |             0.821429 |                       -9.87469 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| open_interest\|premium       | spread_rank                |      8 |                      0 |                            0 |           0.75     |             0.75     |                       -8.78637 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| basis\|regime                | safe_div_abs               |      4 |                      0 |                            0 |           1        |             1        |                       -6.62564 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| open_interest\|open_interest | smooth_mul                 |      4 |                      0 |                            0 |           1        |             1        |                      -10.6776  | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| positioning\|regime          | safe_div_abs               |      4 |                      0 |                            0 |           1        |             1        |                       -6.43455 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| liquidity\|open_interest     | safe_div_abs               |     40 |                      0 |                            0 |           1        |             1        |                       -6.64191 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| open_interest\|positioning   | safe_div_abs               |     28 |                      0 |                            0 |           1        |             0.928571 |                       -8.45335 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| premium\|regime              | spread_rank                |     24 |                      0 |                            0 |           0.916667 |             0.916667 |                       -7.11369 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| liquidity\|liquidity         | safe_div_abs               |     20 |                      0 |                            0 |           0.95     |             0.95     |                       -7.90088 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| premium\|regime              | smooth_mul                 |     20 |                      0 |                            0 |           1        |             1        |                       -9.40992 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| premium\|regime              | state_conditioned_signed   |     20 |                      0 |                            0 |           0.55     |             0.55     |                      -10.2855  | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| basis\|liquidity             | safe_div_abs               |     16 |                      0 |                            0 |           1        |             0.9375   |                       -6.92566 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| basis\|open_interest         | spread_rank                |     16 |                      0 |                            0 |           0.6875   |             0.625    |                       -8.24412 | LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE |
| open_interest\|positioning   | oi_flow_scaled_spread      |     16 |                      0 |                            0 |           1        |             1        |                       -8.80417 | HARD_BLOCK_CONTROL_STALE_PATTERN      |
| liquidity\|premium           | spread_rank                |     12 |                      0 |                            0 |           1        |             0.916667 |                       -6.78098 | HARD_BLOCK_CONTROL_STALE_PATTERN      |

## Field Failure Summary

| field                                |   rows |   mechanism_keep_probe |   control_polluted_near_miss |   control_dom_rate |   lag_stale_dom_rate |   oos_floor_clean_rate |   stress_floor_clean_rate |
|:-------------------------------------|-------:|-----------------------:|-----------------------------:|-------------------:|---------------------:|-----------------------:|--------------------------:|
| mark_index_basis_bps                 |    120 |                      0 |                            4 |           0.7      |             0.65     |              0.0666667 |                 0.191667  |
| account_position_divergence          |    144 |                      0 |                            3 |           0.902778 |             0.847222 |              0.208333  |                 0.145833  |
| top_long_short_account_ratio_last    |     72 |                      0 |                            3 |           0.986111 |             0.972222 |              0.0416667 |                 0.402778  |
| global_long_short_account_ratio_last |     24 |                      0 |                            3 |           0.958333 |             0.958333 |              0.166667  |                 0.5       |
| open_interest_value_mean             |    108 |                      0 |                            2 |           0.953704 |             0.925926 |              0.0555556 |                 0.287037  |
| taker_buy_sell_volume_ratio_last     |     60 |                      0 |                            2 |           0.983333 |             0.966667 |              0.05      |                 0.5       |
| mark_trade_basis_bps                 |    168 |                      0 |                            1 |           0.833333 |             0.785714 |              0.0357143 |                 0.440476  |
| kline_taker_buy_quote_share          |     64 |                      0 |                            1 |           0.890625 |             0.8125   |              0.015625  |                 0.25      |
| premium_close_bps                    |    300 |                      0 |                            0 |           0.88     |             0.846667 |              0.0133333 |                 0.143333  |
| funding_rate_update_age_hours        |    224 |                      0 |                            0 |           0.888393 |             0.857143 |              0         |                 0.450893  |
| top_global_account_divergence        |    168 |                      0 |                            0 |           0.952381 |             0.928571 |              0.0357143 |                 0.238095  |
| trade_quote_volume                   |    156 |                      0 |                            0 |           0.935897 |             0.910256 |              0.0512821 |                 0.166667  |
| open_interest_mean                   |    140 |                      0 |                            0 |           0.878571 |             0.85     |              0.0214286 |                 0.0714286 |
| premium_abs_state                    |    120 |                      0 |                            0 |           0.941667 |             0.933333 |              0         |                 0.491667  |
| funding_rate_state_last_ffill_8h     |     84 |                      0 |                            0 |           0.916667 |             0.857143 |              0.0595238 |                 0.452381  |
| quote_volume_z_168h                  |     84 |                      0 |                            0 |           0.964286 |             0.964286 |              0         |                 0.297619  |
| taker_buy_sell_volume_ratio_mean     |     76 |                      0 |                            0 |           0.960526 |             0.907895 |              0.0657895 |                 0.421053  |
| stress_proxy_state                   |     44 |                      0 |                            0 |           0.909091 |             0.909091 |              0         |                 0.409091  |
| basis_dislocation_state              |     40 |                      0 |                            0 |           0.8      |             0.8      |              0         |                 0.025     |
| top_long_short_position_ratio_last   |     32 |                      0 |                            0 |           0.96875  |             0.96875  |              0.15625   |                 0.1875    |
| open_interest_value_last             |     16 |                      0 |                            0 |           1        |             1        |              0         |                 0.75      |
| open_interest_last                   |      8 |                      0 |                            0 |           1        |             1        |              0         |                 0.5       |

## Interpretation

The A7V3S3 queue is not merely under-sampled. Its early rejected candidates are dominated by OOS floor failure, control dominance, and lag/stale dominance. A7V3S4 therefore moves these constraints upstream: candidate generation should not send known control/stale-dominated pair/motif patterns into expensive reward evaluation.

Mechanism keep probes, if any, should be carried forward only under reduced caps. Control-polluted near misses should be redesigned, not rewarded as-is.

## Outputs

- Runtime: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7v3s4_near_miss_prefilter_audit_20260613`
- `a7v3s4_rejection_classification.csv`
- `a7v3s4_pair_motif_prefilter_summary.csv`
- `a7v3s4_field_failure_summary.csv`
- `a7v3s4_near_miss_candidates.csv`
- `a7v3s4_search_space_prefilter_rules.json`
- `a7v3s4_manifest.json`

## Authorization

Allowed next: build a prefiltered candidate queue using `a7v3s4_search_space_prefilter_rules.json`.

Not allowed: continue the same A7V3S3 queue, alpha proof, shadow, paper, or live execution.
