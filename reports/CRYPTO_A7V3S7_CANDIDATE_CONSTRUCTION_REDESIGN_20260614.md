# CRYPTO A7V3S7 Candidate Construction Redesign - 20260614

Decision: `PASS_A7V3S7_REDESIGNED_QUEUE_READY`

A7V3S7 redesigns the pre-reward candidate construction layer using A7V3S6 smoke failures. It does not execute reward and does not authorize alpha proof.

## Counts

- input_rows: `2963`
- tested_blueprint_count: `256`
- hard_block_pair_motif_count: `22`
- soft_deprioritize_pair_motif_count: `15`
- eligible_rows: `2074`
- selected_rows: `1024`
- selected_semantic_pair_count: `31`
- selected_motif_count: `9`

## Construction Filter Summary

| reason                             |   count |
|:-----------------------------------|--------:|
| tested_in_a7v3s6                   |     256 |
| hard_block_pair_motif              |     636 |
| same_family_pair                   |     291 |
| same_primary_secondary             |      99 |
| eligible_after_construction_filter |    2074 |
| selected                           |    1024 |

## Selected Pairs

| semantic_pair                 |   count |
|:------------------------------|--------:|
| basis\|funding_basis          |      48 |
| basis\|funding_dense          |      48 |
| basis\|positioning            |      48 |
| basis\|regime                 |      48 |
| basis\|premium                |      48 |
| funding_basis\|premium        |      48 |
| funding_basis\|open_interest  |      48 |
| funding_basis\|regime         |      48 |
| funding_dense\|open_interest  |      48 |
| liquidity\|taker_flow         |      48 |
| premium\|regime               |      48 |
| regime\|taker_flow            |      48 |
| premium\|taker_flow           |      48 |
| positioning\|regime           |      48 |
| funding_dense\|regime         |      48 |
| open_interest\|regime         |      48 |
| liquidity\|open_interest      |      43 |
| liquidity\|positioning        |      36 |
| funding_sparse\|open_interest |      30 |
| funding_dense\|taker_flow     |      28 |
| funding_dense\|positioning    |      25 |
| funding_dense\|liquidity      |      21 |
| liquidity\|regime             |      18 |
| basis\|taker_flow             |      17 |
| basis\|funding_sparse         |      13 |
| funding_dense\|premium        |       8 |
| positioning\|taker_flow       |       5 |
| open_interest\|positioning    |       4 |
| funding_sparse\|premium       |       4 |
| basis\|liquidity              |       3 |

## Selected Motifs

| motif                      |   count |
|:---------------------------|--------:|
| safe_div_abs               |     256 |
| signed_rank_gate           |     193 |
| smooth_mul                 |     187 |
| state_conditioned_signed   |     164 |
| state_conditioned_rank_mul |     141 |
| spread_rank                |      71 |
| funding_basis_delta_sign   |       4 |
| funding_basis_spread_24h   |       4 |
| oi_flow_delta_rank         |       4 |

## Hard Failure Rules

| semantic_pair                | motif                 |   rows |   unique_blueprints |   oos_floor_fail_rate |   stress_floor_fail_rate |   control_fail_rate |   lag_stale_fail_rate |   shuffle_fail_rate |   train_orientation_fail_rate |   max_recent_sortino |   median_min_oos_floor_sortino |   median_stress_floor_sortino | construction_decision   |
|:-----------------------------|:----------------------|-------:|--------------------:|----------------------:|-------------------------:|--------------------:|----------------------:|--------------------:|------------------------------:|---------------------:|-------------------------------:|------------------------------:|:------------------------|
| open_interest\|taker_flow    | signed_rank_gate      |     68 |                  17 |              0.985294 |                 0.852941 |            0.955882 |              0.941176 |            0.808824 |                      0.75     |            15.301    |                       -9.63121 |                      -8.05636 | HARD_BLOCK_A7V3S7       |
| open_interest\|premium       | spread_rank           |     56 |                  14 |              1        |                 0.982143 |            0.803571 |              0.75     |            0.767857 |                      0.732143 |             9.84683  |                      -10.9234  |                      -7.11398 | HARD_BLOCK_A7V3S7       |
| open_interest\|taker_flow    | oi_flow_scaled_spread |     52 |                  13 |              1        |                 1        |            1        |              0.980769 |            0.865385 |                      0.769231 |             5.54293  |                      -10.4598  |                     -10.1256  | HARD_BLOCK_A7V3S7       |
| open_interest\|taker_flow    | smooth_mul            |     52 |                  13 |              1        |                 0.846154 |            0.980769 |              0.980769 |            0.903846 |                      0.807692 |            16.1765   |                      -10.2755  |                      -9.24348 | HARD_BLOCK_A7V3S7       |
| open_interest\|taker_flow    | spread_rank           |     52 |                  13 |              1        |                 0.846154 |            0.980769 |              0.961538 |            0.730769 |                      0.75     |            16.4845   |                       -9.41118 |                      -4.45242 | HARD_BLOCK_A7V3S7       |
| basis\|open_interest         | signed_rank_gate      |     44 |                  11 |              1        |                 0.977273 |            0.704545 |              0.681818 |            0.568182 |                      0.727273 |             8.69916  |                       -7.9702  |                      -7.56535 | HARD_BLOCK_A7V3S7       |
| open_interest\|taker_flow    | safe_div_abs          |     36 |                   9 |              1        |                 1        |            0.972222 |              0.944444 |            0.916667 |                      0.972222 |             2.11478  |                      -12.3907  |                     -10.8991  | HARD_BLOCK_A7V3S7       |
| basis\|open_interest         | spread_rank           |     36 |                   9 |              1        |                 0.972222 |            0.722222 |              0.694444 |            0.611111 |                      0.75     |            10.7445   |                       -8.60456 |                      -7.67178 | HARD_BLOCK_A7V3S7       |
| liquidity\|positioning       | smooth_mul            |     28 |                   7 |              1        |                 0.857143 |            1        |              0.928571 |            0.785714 |                      0.607143 |            19.7233   |                       -9.52429 |                      -4.81167 | HARD_BLOCK_A7V3S7       |
| basis\|open_interest         | smooth_mul            |     28 |                   7 |              0.964286 |                 1        |            0.75     |              0.642857 |            0.5      |                      0.714286 |             9.51083  |                       -7.99354 |                      -6.20689 | HARD_BLOCK_A7V3S7       |
| positioning\|taker_flow      | signed_rank_gate      |     24 |                   6 |              1        |                 0.75     |            0.958333 |              0.833333 |            0.791667 |                      0.708333 |            15.7018   |                       -9.75735 |                      -5.01869 | HARD_BLOCK_A7V3S7       |
| basis\|basis                 | smooth_mul            |     24 |                   6 |              1        |                 0.958333 |            0.791667 |              0.75     |            0.5      |                      0.916667 |             4.52051  |                      -10.1034  |                      -9.17452 | HARD_BLOCK_A7V3S7       |
| basis\|open_interest         | oi_flow_scaled_spread |     24 |                   6 |              1        |                 1        |            0.791667 |              0.708333 |            0.708333 |                      0.75     |            12.4723   |                      -10.4665  |                      -7.2684  | HARD_BLOCK_A7V3S7       |
| basis\|taker_flow            | smooth_mul            |     24 |                   6 |              1        |                 0.958333 |            0.75     |              0.75     |            0.583333 |                      0.958333 |             6.44899  |                       -9.65059 |                      -7.91338 | HARD_BLOCK_A7V3S7       |
| liquidity\|taker_flow        | spread_rank           |     20 |                   5 |              1        |                 0.8      |            1        |              1        |            0.8      |                      0.9      |            22.7744   |                      -11.5008  |                      -9.16381 | HARD_BLOCK_A7V3S7       |
| open_interest\|open_interest | safe_div_abs          |     20 |                   5 |              1        |                 1        |            1        |              0.95     |            0.9      |                      0.5      |             3.46214  |                       -9.03052 |                      -7.60826 | HARD_BLOCK_A7V3S7       |
| positioning\|positioning     | spread_rank           |     20 |                   5 |              1        |                 0.95     |            1        |              1        |            0.85     |                      0.65     |            14.9427   |                      -10.8336  |                      -2.983   | HARD_BLOCK_A7V3S7       |
| basis\|premium               | safe_div_abs          |     20 |                   5 |              1        |                 1        |            0.8      |              0.75     |            0.6      |                      1        |             1.24864  |                      -10.9373  |                     -10.3914  | HARD_BLOCK_A7V3S7       |
| open_interest\|open_interest | smooth_mul            |     16 |                   4 |              1        |                 1        |            0.9375   |              0.875    |            0.75     |                      0.375    |             0.283967 |                      -10.3681  |                      -6.73809 | HARD_BLOCK_A7V3S7       |
| positioning\|premium         | smooth_mul            |     16 |                   4 |              1        |                 0.9375   |            0.9375   |              0.9375   |            0.75     |                      0.9375   |             6.32997  |                       -9.74276 |                      -5.03357 | HARD_BLOCK_A7V3S7       |
| positioning\|premium         | signed_rank_gate      |     16 |                   4 |              1        |                 0.9375   |            0.875    |              0.75     |            0.75     |                      1        |             1.95065  |                      -12.5546  |                      -8.50965 | HARD_BLOCK_A7V3S7       |
| positioning\|premium         | spread_rank           |     16 |                   4 |              1        |                 1        |            0.875    |              0.6875   |            0.875    |                      0.625    |            13.9401   |                      -10.6148  |                      -6.57278 | HARD_BLOCK_A7V3S7       |

## Interpretation

A7V3S7 is stricter than A7V3S5: it removes A7V3S6-tested blueprints, pair/motif patterns with severe OOS/stress/control failure, same-family pairs, and same primary/secondary field constructions. The selected queue is smaller but more diverse and more mechanism-oriented.

Allowed next: bounded strict reward smoke on `a7v3s7_redesigned_reward_prequeue.csv`.

Not allowed: full reward wave, alpha proof, shadow, paper, or live.
