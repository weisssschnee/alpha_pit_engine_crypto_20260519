# CRYPTO A7V3S1 Accepted Candidate Validation Pack

Generated: `2026-07-07T17:41:39Z`

## Decision

`PASS_A7V3S1_VALIDATION_PACK_BUILT`

This is a validation handoff for reward-accepted numeric probes. It is not alpha proof and does not authorize shadow, paper, or live trading.

## Counts

- accepted reward rows: `11`
- unique accepted blueprints: `11`
- next deep validation queue: `11`
- rejected from next validation: `0`

## Validation Decisions

| decision                       |   count |
|:-------------------------------|--------:|
| ADVANCE_DEEP_REPLAY_VALIDATION |      11 |

## Review Flags

_empty_

## Family Concentration

| semantic_pair               | motif                       | validation_decision            |   candidates |   median_recent_sortino |   median_min_oos_floor_sortino |   max_recent_sortino |
|:----------------------------|:----------------------------|:-------------------------------|-------------:|------------------------:|-------------------------------:|---------------------:|
| funding_dense|open_interest | shadow_selected_exact_probe | ADVANCE_DEEP_REPLAY_VALIDATION |            5 |                 12.6676 |                       0.497889 |              18.3882 |
| funding_dense|open_interest | shadow_selected_rank_wrap   | ADVANCE_DEEP_REPLAY_VALIDATION |            5 |                 12.6676 |                       0.497889 |              18.3882 |
| open_interest|positioning   | positive_prior_safe_div_abs | ADVANCE_DEEP_REPLAY_VALIDATION |            1 |                 16.2218 |                       1.06354  |              16.2218 |

## Top Deep Validation Queue

| validation_decision            | semantic_pair               | motif                       |   horizon_h |   recent_sortino |   min_oos_floor_sortino |   stress_sortino |   recent_control_ratio |   recent_shuffle_control_ratio | required_validation   | expression                                                                                                          |
|:-------------------------------|:----------------------------|:----------------------------|------------:|-----------------:|------------------------:|-----------------:|-----------------------:|-------------------------------:|:----------------------|:--------------------------------------------------------------------------------------------------------------------|
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_rank_wrap   |           8 |         18.3882  |                8.50321  |          6.50004 |               0.993638 |                      0.31691   |                       | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_exact_probe |           8 |         18.3882  |                8.50321  |          6.50004 |               0.993638 |                      0.398843  |                       | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         |
| ADVANCE_DEEP_REPLAY_VALIDATION | open_interest|positioning   | positive_prior_safe_div_abs |          24 |         16.2218  |                1.06354  |         16.7556  |               0.986889 |                      0.246905  |                       | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_rank_wrap   |          24 |         12.0121  |                0.497889 |         10.7251  |               0.987118 |                      0.0730941 |                       | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_exact_probe |          24 |         12.6676  |                0.318659 |         13.8177  |               0.987874 |                      0.171326  |                       | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_rank_wrap   |          24 |         12.6676  |                0.318659 |         13.8177  |               0.987874 |                      0.177144  |                       | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_rank_wrap   |          24 |         12.6676  |                0.318659 |         13.8177  |               0.987874 |                      0.204427  |                       | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_exact_probe |          24 |         12.0121  |                0.497889 |         10.7251  |               0.987118 |                      0.30089   |                       | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_exact_probe |          24 |         12.6676  |                0.318659 |         13.8177  |               0.987874 |                      0.293501  |                       | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_exact_probe |           8 |          4.08333 |                2.11649  |          8.84355 |               0.955353 |                      0.842827  |                       | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  |
| ADVANCE_DEEP_REPLAY_VALIDATION | funding_dense|open_interest | shadow_selected_rank_wrap   |           8 |          4.08333 |                2.11649  |          8.84355 |               0.972092 |                      0.972092  |                       | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          |

## Bias-Audit Notes

- `numeric_probe_only_not_factor` means reward passed a numeric probe but the candidate is not a promoted factor.
- `structural_listing_or_universe_state_dependency` means the candidate depends on listing age or active-universe state and needs PIT membership/listing audit before any promotion discussion.
- `matched_control_ratio_ge_1` means matched control is as strong or stronger on the recent slice and requires neutralized/control replay.
- Same-skeleton clusters are not independent discoveries; they require family dedupe before queue expansion.

## Outputs

- `candidate_review`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_candidate_review.csv`
- `duplicate_clusters`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_duplicate_cluster_audit.csv`
- `family_concentration`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_family_concentration.csv`
- `review_flag_summary`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_review_flag_summary.csv`
- `split_matrix`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_split_window_matrix.csv`
- `split_summary`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_split_window_summary.csv`
- `next_queue`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_next_deep_validation_queue.csv`
- `manifest`: `runtime\a7search8a_accepted_candidate_validation_20260708\a7v3s1_manifest.json`
