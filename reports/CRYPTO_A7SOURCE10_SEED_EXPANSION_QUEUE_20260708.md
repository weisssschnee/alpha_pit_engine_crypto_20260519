# CRYPTO A7SOURCE10 Seed Expansion Queue

Generated: `2026-07-07T18:45:29Z`

## Decision

`PASS_A7SOURCE10_SEED_EXPANSION_QUEUE_BUILT`

Source10 expands only A7SOURCE9 incremental survivors into identity, rank-wrap, window-neighbor, operator-neighbor, single-leg-control, and field-pair-control probes.

## Counts

- seed_rows: `11`
- queue_rows: `3803`
- shards: `15`
- rows_per_shard: `256`

## Queue Summary

| semantic_pair                | motif                                                                                                                  |   horizon_h |   count |
|:-----------------------------|:-----------------------------------------------------------------------------------------------------------------------|------------:|--------:|
| funding_dense\|open_interest | source9_formula_identity_abs_wrap                                                                                      |           8 |      10 |
| funding_dense\|open_interest | source9_formula_identity_sign_wrap                                                                                     |           8 |      10 |
| funding_dense\|open_interest | source9_formula_identity_identity_lock                                                                                 |           8 |       9 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_240_to_336                                                                     |           8 |       8 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_240_to_72                                                                      |           8 |       8 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_240_to_96                                                                      |           8 |       8 |
| funding_dense\|open_interest | source9_operator_neighbor_op_csrank_to_zscore                                                                          |           8 |       8 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_240_to_168                                                                     |           8 |       8 |
| funding_dense\|open_interest | source9_formula_identity_double_rank_wrap                                                                              |           8 |       6 |
| funding_dense\|open_interest | source9_formula_identity_zscore_wrap                                                                                   |           8 |       6 |
| funding_dense\|open_interest | source9_operator_neighbor_op_tsrank_to_csrank                                                                          |           8 |       6 |
| funding_dense\|open_interest | source9_formula_identity_rank_wrap                                                                                     |           8 |       5 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_72_to_12                                                                       |           8 |       4 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_72_to_24                                                                       |           8 |       4 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_72_to_48                                                                       |           8 |       4 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_72_to_96                                                                       |           8 |       4 |
| funding_dense\|open_interest | source9_operator_neighbor_op_decay_to_mean                                                                             |           8 |       2 |
| funding_dense\|open_interest | source9_operator_neighbor_op_mean_to_decay                                                                             |           8 |       2 |
| funding_dense\|open_interest | source9_operator_neighbor_op_zscore_to_csrank                                                                          |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_12_to_24                                                                       |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_12_to_4                                                                        |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_12_to_48                                                                       |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_12_to_8                                                                        |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_24_to_12                                                                       |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_24_to_4                                                                        |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_24_to_48                                                                       |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_24_to_8                                                                        |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_336_to_168                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_336_to_240                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_336_to_504                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_336_to_96                                                                      |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_504_to_168                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_504_to_240                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_504_to_336                                                                     |           8 |       2 |
| funding_dense\|open_interest | source9_window_neighbor_window_neighbor_504_to_96                                                                      |           8 |       2 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_level      |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_12    |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_168   |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_24    |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_240   |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_336   |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_4     |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_48    |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_504   |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_72    |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_8     |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_mean_96    |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_sign       |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_tsrank_12  |           8 |       1 |
| funding_dense\|open_interest | source9_field_pair_control_field_pair_rank_mul_funding_rate_delta_state_24h_csrank_open_interest_value_last_tsrank_168 |           8 |       1 |

## Boundary

- Authorizes proxy search only.
- Does not authorize alpha proof, shadow, paper, live, or deployment.
