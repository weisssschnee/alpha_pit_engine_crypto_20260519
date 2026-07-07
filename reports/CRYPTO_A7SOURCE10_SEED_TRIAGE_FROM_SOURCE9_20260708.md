# CRYPTO A7SOURCE7 Seed Triage And Next Search Contract

Generated: `2026-07-07T18:42:40Z`

## Decision

`PASS_A7SOURCE7_SEED_TRIAGE_READY`

A7SOURCE7 promotes only A7SOURCE6 survivors whose canonical formulas re-pass strict reward while single-leg and operator-neighbor controls do not pass.

## Counts

- promoted_seed_count: `11`
- failed_or_blocked_count: `0`
- source6_decision: `PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND`
- source6_reward_decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

## Promoted Seeds

| source_blueprint_id        | validation_group   | blueprint_id                                      |   horizon_h |   rows |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | formula                                                                                                             | semantic_pair                | motif                                  | skeleton_key   | expression                                                                                                          | decision                              |   seed_rank | seed_role                          | allowed_next_use                                    | blocked_next_use                                       | required_next_checks                                                                                                                                           |
|:---------------------------|:-------------------|:--------------------------------------------------|------------:|-------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------|:-----------------------------|:---------------------------------------|:---------------|:--------------------------------------------------------------------------------------------------------------------|:--------------------------------------|------------:|:-----------------------------------|:----------------------------------------------------|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search7_1579560a060d20ec | canonical          | a7search6_vp_a7search7_1579560a060d20ec_canonical |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.355241  | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         | funding_dense\|open_interest | shadow_selected_exact_probe_validation | canonical      | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           1 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_9168babaa32dc76c | canonical          | a7search6_vp_a7search7_9168babaa32dc76c_canonical |           8 |      1 |        2.44731  |             15.8815  |       11.8745  |         18.3882  |                8.50321  |               1.27322  |                      0.398843  | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) | funding_dense\|open_interest | shadow_selected_rank_wrap_validation   | canonical      | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           2 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_f57e92c650f903b6 | canonical          | a7search6_vp_a7search7_f57e92c650f903b6_canonical |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.510444  | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          | funding_dense\|open_interest | shadow_selected_rank_wrap_validation   | canonical      | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           3 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_fa2bcb9f82277249 | canonical          | a7search6_vp_a7search7_fa2bcb9f82277249_canonical |           8 |      1 |        2.22076  |              7.78013 |        8.33728 |          4.08333 |                2.11649  |               0.860626 |                      0.458351  | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  | funding_dense\|open_interest | shadow_selected_exact_probe_validation | canonical      | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           4 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_4e22e196bfeb8bce | canonical          | a7search6_vp_a7search7_4e22e196bfeb8bce_canonical |          24 |      1 |        1.89712  |              3.60958 |        5.47024 |         16.2218  |                1.06354  |               8.19878  |                      0.58279   | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             | open_interest\|positioning   | positive_prior_safe_div_abs_validation | canonical      | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           5 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_52353a2ad0ece8e8 | canonical          | a7search6_vp_a7search7_52353a2ad0ece8e8_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.28347   | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               | funding_dense\|open_interest | shadow_selected_rank_wrap_validation   | canonical      | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           6 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_e7180b1ba6a1df1a | canonical          | a7search6_vp_a7search7_e7180b1ba6a1df1a_canonical |          24 |      1 |        3.19775  |              3.43001 |        9.55872 |         12.0121  |                0.497889 |               6.40622  |                      0.240769  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       | funding_dense\|open_interest | shadow_selected_exact_probe_validation | canonical      | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           7 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_124582cf9a6d54a0 | canonical          | a7search6_vp_a7search7_124582cf9a6d54a0_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.0671119 | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       | funding_dense\|open_interest | shadow_selected_rank_wrap_validation   | canonical      | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           8 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_8ecc4a9a053a0d59 | canonical          | a7search6_vp_a7search7_8ecc4a9a053a0d59_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.127296  | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        | funding_dense\|open_interest | shadow_selected_rank_wrap_validation   | canonical      | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        | PASS_INCREMENTAL_INTERACTION_EVIDENCE |           9 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_b2e42dec52899bd0 | canonical          | a7search6_vp_a7search7_b2e42dec52899bd0_canonical |          24 |      1 |        0.944611 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.497411  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                | funding_dense\|open_interest | shadow_selected_exact_probe_validation | canonical      | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                | PASS_INCREMENTAL_INTERACTION_EVIDENCE |          10 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |
| a7search7_d404a68b39d27dbd | canonical          | a7search6_vp_a7search7_d404a68b39d27dbd_canonical |          24 |      1 |        0.997506 |              4.20618 |        4.95853 |         12.6676  |                0.318659 |               7.40948  |                      0.177144  | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               | funding_dense\|open_interest | shadow_selected_exact_probe_validation | canonical      | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               | PASS_INCREMENTAL_INTERACTION_EVIDENCE |          11 | source_lag_proven_incremental_seed | small_mechanism_expansion_and_control_strict_search | alpha_proof\|shadow\|paper\|live\|single_leg_promotion | formula_identity_lock\|source_lag_inheritance\|single_leg_recheck\|operator_neighbor_recheck\|walk_forward_2026_holdout\|capacity_turnover_realism\|family_cap |

## Failed Or Blocked

`<empty>`

## Semantic Pair Summary

| semantic_pair                |   count |     share |
|:-----------------------------|--------:|----------:|
| funding_dense\|open_interest |      10 | 0.909091  |
| open_interest\|positioning   |       1 | 0.0909091 |

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
