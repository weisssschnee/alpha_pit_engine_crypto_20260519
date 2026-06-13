# CRYPTO A7V3S1 Accepted Candidate Validation Pack

Generated: `2026-06-13T13:33:28Z`

## Decision

`PASS_A7V3S1_VALIDATION_PACK_BUILT`

This is a validation handoff for reward-accepted numeric probes. It is not alpha proof and does not authorize shadow, paper, or live trading.

## Counts

- accepted reward rows: `40`
- unique accepted blueprints: `17`
- next deep validation queue: `17`
- rejected from next validation: `0`

## Validation Decisions

| decision                                  |   count |
|:------------------------------------------|--------:|
| ADVANCE_PIT_AND_REGIME_VALIDATION         |      12 |
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |       5 |

## Review Flags

| review_flags                                    |   count |
|:------------------------------------------------|--------:|
| matched_control_ratio_ge_1                      |      17 |
| numeric_probe_only_not_factor                   |      17 |
| stress_floor_non_positive                       |      13 |
| structural_listing_or_universe_state_dependency |      12 |
| stress_sortino_non_positive                     |       9 |
| same_skeleton_duplicate_cluster                 |       2 |

## Family Concentration

| semantic_pair              | motif                      | validation_decision                       |   candidates |   median_recent_sortino |   median_min_oos_floor_sortino |   max_recent_sortino |
|:---------------------------|:---------------------------|:------------------------------------------|-------------:|------------------------:|-------------------------------:|---------------------:|
| age|positioning            | smooth_mul                 | ADVANCE_PIT_AND_REGIME_VALIDATION         |            3 |                 7.66715 |                     0.381593   |             15.5909  |
| age|positioning            | safe_div_abs               | ADVANCE_PIT_AND_REGIME_VALIDATION         |            2 |                24.7706  |                     6.41663    |             24.7706  |
| positioning|universe_state | state_conditioned_signed   | ADVANCE_PIT_AND_REGIME_VALIDATION         |            2 |                15.6436  |                     2.62878    |             15.677   |
| age|positioning            | state_conditioned_signed   | ADVANCE_PIT_AND_REGIME_VALIDATION         |            2 |                15.2384  |                     1.71903    |             15.677   |
| positioning|universe_state | smooth_mul                 | ADVANCE_PIT_AND_REGIME_VALIDATION         |            1 |                15.677   |                     2.66725    |             15.677   |
| positioning|universe_state | spread_rank                | ADVANCE_PIT_AND_REGIME_VALIDATION         |            1 |                15.677   |                     2.66725    |             15.677   |
| positioning|universe_state | state_conditioned_rank_mul | ADVANCE_PIT_AND_REGIME_VALIDATION         |            1 |                15.6103  |                     2.59032    |             15.6103  |
| open_interest|positioning  | smooth_mul                 | ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |            1 |                15.028   |                     2.54495    |             15.028   |
| open_interest|positioning  | safe_div_abs               | ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |            1 |                12.3428  |                     1.86521    |             12.3428  |
| open_interest|positioning  | spread_rank                | ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |            1 |                 9.71647 |                     0.00251951 |              9.71647 |
| positioning|positioning    | signed_rank_gate           | ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |            1 |                 9.44374 |                     1.14392    |              9.44374 |
| open_interest|regime       | safe_div_abs               | ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION |            1 |                 4.33158 |                     1.79882    |              4.33158 |

## Top Deep Validation Queue

| validation_decision                       | semantic_pair              | motif                      |   horizon_h |   recent_sortino |   min_oos_floor_sortino |   stress_sortino |   recent_control_ratio |   recent_shuffle_control_ratio | required_validation                                                                                                                      | expression                                                                                                   |
|:------------------------------------------|:---------------------------|:---------------------------|------------:|-----------------:|------------------------:|-----------------:|-----------------------:|-------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------|
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION | open_interest|positioning  | smooth_mul                 |           4 |         15.028   |              2.54495    |        -0.733088 |                1.0343  |                       0.619522 | matched-control and neutralization rerun;deep replay before factor promotion                                                             | Mul(Decay(account_position_divergence,3),Abs(ZScore(Mean(open_interest_value_mean,4))))                      |
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION | open_interest|positioning  | safe_div_abs               |           4 |         12.3428  |              1.86521    |         0.251417 |                1.03898 |                       0.113104 | matched-control and neutralization rerun;deep replay before factor promotion                                                             | SafeDiv(ZScore(Mean(account_position_divergence,3)),Abs(Abs(ZScore(Mean(open_interest_mean,3)))))            |
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION | positioning|positioning    | signed_rank_gate           |          24 |          9.44374 |              1.14392    |         0.661862 |                1.02033 |                       0.794711 | matched-control and neutralization rerun;deep replay before factor promotion                                                             | Mul(CSRank(ZScore(Mean(top_global_account_divergence,3))),Sign(ZScore(Mean(account_position_divergence,3)))) |
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION | open_interest|regime       | safe_div_abs               |           4 |          4.33158 |              1.79882    |        -0.948636 |                1.028   |                       0.501499 | matched-control and neutralization rerun;deep replay before factor promotion                                                             | SafeDiv(Abs(ZScore(Mean(open_interest_value_last,336))),Abs(Decay(basis_dislocation_state,720)))             |
| ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION | open_interest|positioning  | spread_rank                |           4 |          9.71647 |              0.00251951 |         5.79797  |                1.10229 |                       0.182194 | matched-control and neutralization rerun;deep replay before factor promotion                                                             | Sub(CSRank(Decay(open_interest_value_mean,4)),CSRank(Abs(ZScore(Mean(account_position_divergence,3)))))      |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | safe_div_abs               |          24 |         24.7706  |              6.41663    |         9.84915  |                1.00851 |                       0.12484  | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion;formula family dedupe | SafeDiv(Sign(TSRank(listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                          |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | safe_div_abs               |          24 |         24.7706  |              6.41663    |         9.84915  |                1.00851 |                       0.175533 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion;formula family dedupe | SafeDiv(Sign(TSRank(sqrt_listing_age_days,8)),Abs(Decay(account_position_divergence,3)))                     |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | positioning|universe_state | smooth_mul                 |           4 |         15.677   |              2.66725    |        -0.417945 |                1.03252 |                       0.47458  | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(ZScore(Mean(account_position_divergence,3)),CSRank(active_universe_size))                                |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | positioning|universe_state | state_conditioned_rank_mul |           4 |         15.6103  |              2.59032    |        -0.4301   |                1.03433 |                       0.327495 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(CSRank(Decay(account_position_divergence,3)),CSRank(CSRank(active_universe_size)))                       |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | state_conditioned_signed   |           4 |         15.677   |              2.66725    |        -0.417945 |                1.03252 |                       0.618854 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(ZScore(Mean(account_position_divergence,3)),Sign(CSRank(log1p_listing_age_days)))                        |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | positioning|universe_state | spread_rank                |           4 |         15.677   |              2.66725    |        -0.417945 |                1.03252 |                       0.651853 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Sub(CSRank(Sign(TSRank(active_universe_size,6))),CSRank(ZScore(Mean(account_position_divergence,3))))        |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | positioning|universe_state | state_conditioned_signed   |           4 |         15.677   |              2.66725    |        -0.417945 |                1.03252 |                       0.682208 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(ZScore(Mean(account_position_divergence,3)),Sign(Sign(TSRank(active_universe_size,6))))                  |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | smooth_mul                 |           4 |         15.5909  |              2.54337    |        -0.358814 |                1.03417 |                       0.473492 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(Decay(log1p_listing_age_days,3),Decay(account_position_divergence,3))                                    |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | positioning|universe_state | state_conditioned_signed   |           4 |         15.6103  |              2.59032    |        -0.4301   |                1.03433 |                       0.589164 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(Decay(account_position_divergence,3),Sign(CSRank(active_universe_size)))                                 |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | state_conditioned_signed   |           4 |         14.7998  |              0.770809   |         4.99208  |                1.03236 |                       0.447177 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(Sign(TSRank(sqrt_listing_age_days,4)),Sign(ZScore(Mean(account_position_divergence,3))))                 |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | smooth_mul                 |          24 |          7.66715 |              0.381593   |         3.70441  |                1.01932 |                       0.307191 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(CSRank(log1p_listing_age_days),Abs(ZScore(Mean(account_position_divergence,3))))                         |
| ADVANCE_PIT_AND_REGIME_VALIDATION         | age|positioning            | smooth_mul                 |          24 |          7.66715 |              0.381593   |         3.70441  |                1.01932 |                       0.543095 | matched-control and neutralization rerun;PIT listing/universe membership audit;deep replay before factor promotion                       | Mul(Abs(ZScore(Mean(account_position_divergence,3))),CSRank(log1p_listing_age_days))                         |

## Bias-Audit Notes

- `numeric_probe_only_not_factor` means reward passed a numeric probe but the candidate is not a promoted factor.
- `structural_listing_or_universe_state_dependency` means the candidate depends on listing age or active-universe state and needs PIT membership/listing audit before any promotion discussion.
- `matched_control_ratio_ge_1` means matched control is as strong or stronger on the recent slice and requires neutralized/control replay.
- Same-skeleton clusters are not independent discoveries; they require family dedupe before queue expansion.

## Outputs

- `candidate_review`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_candidate_review.csv`
- `duplicate_clusters`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_duplicate_cluster_audit.csv`
- `family_concentration`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_family_concentration.csv`
- `review_flag_summary`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_review_flag_summary.csv`
- `split_matrix`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_split_window_matrix.csv`
- `split_summary`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_split_window_summary.csv`
- `next_queue`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_next_deep_validation_queue.csv`
- `manifest`: `runtime\a7v3s1_accepted_candidate_validation_20260613\a7v3s1_manifest.json`
