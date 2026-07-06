# CRYPTO A7SOURCE7 Seed Triage And Next Search Contract

Generated: `2026-07-06T05:56:45Z`

## Decision

`PASS_A7SOURCE7_SEED_TRIAGE_READY`

A7SOURCE7 promotes only A7SOURCE6 survivors whose canonical formulas re-pass strict reward while single-leg and operator-neighbor controls do not pass.

## Counts

- promoted_seed_count: `5`
- failed_or_blocked_count: `1`
- source6_decision: `PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND`
- source6_reward_decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Promoted Seeds

| source_blueprint_id                                  | validation_group   | blueprint_id                                                                |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | formula                                                                                                     | semantic_pair                | motif                                                    | skeleton_key   | expression                                                                                                  | decision                              |   seed_rank | seed_role                          | allowed_next_use                                    | blocked_next_use                                       | required_next_checks                                                                                                                                           |
|:-----------------------------------------------------|:-------------------|:----------------------------------------------------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:------------------------------------------------------------------------------------------------------------|:-----------------------------|:---------------------------------------------------------|:---------------|:------------------------------------------------------------------------------------------------------------|:--------------------------------------|------------:|:-----------------------------------|:----------------------------------------------------|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical  | canonical          | a7search6_vp_a7search7_vp_a7search7_3ac1a9eafa18b95f_8_canonical_canonical  |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.398843  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))) | funding_dense\|open_interest | shadow_selected_rank_wrap_strict_validation_validation   | canonical      | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))) | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           1 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical  | canonical          | a7search6_vp_a7search7_vp_a7search7_dec97465aedf9ce9_8_canonical_canonical  |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.880889  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))          | open_interest\|positioning   | positive_prior_safe_div_abs_strict_validation_validation | canonical      | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))          | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           2 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_1c97b872a07e39dc_24_canonical_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.0730941 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))               | basis\|open_interest         | positive_prior_signed_rank_strict_validation_validation  | canonical      | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))               | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           3 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_vp_a7search7_3e5555ac440970e9_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_3e5555ac440970e9_24_canonical_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.488939  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))       | basis\|open_interest         | positive_prior_signed_rank_strict_validation_validation  | canonical      | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))       | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           4 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_vp_a7search7_58ba8c206cc57999_24_canonical | canonical          | a7search6_vp_a7search7_vp_a7search7_58ba8c206cc57999_24_canonical_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.107433  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                        | open_interest\|premium       | positive_prior_signed_rank_strict_validation_validation  | canonical      | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                        | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           5 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |

## Failed Or Blocked

| source_blueprint_id                                  |   source_rank |   canonical_accepted_rows |   single_leg_accepted_rows |   operator_neighbor_accepted_rows |   accepted_rows | decision                      |
|:-----------------------------------------------------|--------------:|--------------------------:|---------------------------:|----------------------------------:|----------------:|:------------------------------|
| a7search7_vp_a7search7_1e4d0178e8251298_24_canonical |             4 |                         0 |                          0 |                                 0 |               0 | HOLD_CANONICAL_DID_NOT_REPASS |

## Semantic Pair Summary

| semantic_pair                |   count |   share |
|:-----------------------------|--------:|--------:|
| basis\|open_interest         |       2 |     0.4 |
| funding_dense\|open_interest |       1 |     0.2 |
| open_interest\|positioning   |       1 |     0.2 |
| open_interest\|premium       |       1 |     0.2 |

## Search Constraints

```json
{
  "allowed": [
    "mechanism-local expansion around promoted seeds",
    "formula identity locked rerun",
    "source-lag inherited validation only when formula+horizon matches",
    "strict reward gate with controls"
  ],
  "blocked": [
    "alpha proof",
    "shadow/paper/live",
    "single-leg promotion",
    "large raw search without family caps",
    "source-lag proof inheritance for mutated formulas"
  ],
  "family_caps": {
    "max_open_interest_family_share": 0.6,
    "max_semantic_pair_share": 0.4,
    "require_non_open_interest_new_seed_attempts": true
  },
  "next_required": [
    "A7SOURCE8 formula identity and source-lag inheritance lock",
    "A7SEARCH8 controlled seed expansion with caps",
    "A7VAL walk-forward 2026 holdout and execution realism"
  ],
  "stage": "A7SOURCE7-SEED-TRIAGE"
}
```

## Boundary

- Authorizes controlled seed expansion only.
- Does not authorize alpha proof, shadow, paper, live, or deployment.
