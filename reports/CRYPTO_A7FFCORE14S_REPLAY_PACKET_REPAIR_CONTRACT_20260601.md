# CRYPTO A7FF-CORE14S REPLAY PACKET REPAIR CONTRACT

Generated: 2026-06-01T04:42:59Z

## Decision

`PASS_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_READY_FOR_CORE14SE`

A7FF-CORE14S defines a repair contract after CORE14E replay failure. It does not execute replay, formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core14se": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_READY_FOR_CORE14SE",
  "dominant_blocker": "control_and_cost_collapse",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T04:42:59Z",
  "next_allowed": "A7FF-CORE14SE repaired packet construction / bounded replay execution",
  "source_decision": "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S",
  "source_stage": "A7FF-CORE14R",
  "stage": "A7FF-CORE14S"
}
```

## Repair Rules

| rule_id                           | requirement                                                                                                | reason                                                                                                               |
|:----------------------------------|:-----------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|
| R0_no_gate_relaxation_as_solution | do not proceed by merely relaxing CORE14E pass gates                                                       | CORE14R max strict candidates under sensitivity is below 24; relaxed control thresholds do not create enough breadth |
| R1_split_first_packet_score       | CORE14SE packet score must prioritize candidates with validation and recent evidence separately            | CORE14E collapsed under validation+recent joint clean rule                                                           |
| R2_control_margin_first           | packet construction must rank by non-signflip max control margin before raw score                          | dominant blocker is control_and_cost_collapse                                                                        |
| R3_cost_floor                     | candidate packet must estimate 5bps cost survival before replay execution                                  | many candidates have positive raw spread but negative cost-adjusted spread                                           |
| R4_family_rebalance               | packet must cap any semantic/motif pair at 20 percent and include at least 6 semantic buckets and 5 motifs | CORE14E clean pool collapsed to one semantic and one motif                                                           |
| R5_no_same_packet_rerun           | CORE14E packet cannot be rerun unchanged                                                                   | same packet already executed bounded replay and failed clean pool gates                                              |

## Next Contract

```json
{
  "action": "build repaired replay packet and execute bounded replay only if packet gates pass",
  "clean_rule": "validation and recent both positive at 5bps with max non-signflip control_ratio < 1.0",
  "forbidden": [
    "same CORE14 packet rerun",
    "gate relaxation as pass",
    "formula search",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "max_packet": 128,
  "max_semantic_motif_pair_share": 0.2,
  "min_motif_buckets": 5,
  "min_packet": 96,
  "min_semantic_buckets": 6,
  "required_controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo"
  ],
  "source_pool": "CORE13E numeric clues plus CORE14R failure attribution; not CORE14E clean pool only",
  "stage": "A7FF-CORE14SE"
}
```

## Source Gate Sensitivity

|   cost_bps |   control_ratio_threshold |   either_validation_or_recent_candidates |   both_validation_and_recent_candidates |   both_semantic_count |   both_motif_count |
|-----------:|--------------------------:|-----------------------------------------:|----------------------------------------:|----------------------:|-------------------:|
|          0 |                       0.8 |                                       14 |                                       2 |                     1 |                  1 |
|          0 |                       1   |                                       29 |                                       5 |                     2 |                  2 |
|          0 |                       1.5 |                                       50 |                                       9 |                     2 |                  2 |
|          0 |                       2   |                                       64 |                                      12 |                     2 |                  2 |
|          2 |                       0.8 |                                        8 |                                       2 |                     1 |                  1 |
|          2 |                       1   |                                       21 |                                       5 |                     2 |                  2 |
|          2 |                       1.5 |                                       35 |                                       9 |                     2 |                  2 |
|          2 |                       2   |                                       43 |                                      11 |                     2 |                  2 |
|          5 |                       0.8 |                                        4 |                                       0 |                     0 |                  0 |
|          5 |                       1   |                                       11 |                                       2 |                     1 |                  1 |
|          5 |                       1.5 |                                       16 |                                       4 |                     2 |                  2 |
|          5 |                       2   |                                       17 |                                       4 |                     2 |                  2 |
|         10 |                       0.8 |                                        2 |                                       0 |                     0 |                  0 |
|         10 |                       1   |                                        4 |                                       0 |                     0 |                  0 |
|         10 |                       1.5 |                                        5 |                                       0 |                     0 |                  0 |
|         10 |                       2   |                                        5 |                                       0 |                     0 |                  0 |

## Source Control Dominance

| dominant_control           | semantic_bucket                      | motif_bucket       |   row_count |   candidate_count |   median_control_ratio |   median_cost_adjusted_spread |
|:---------------------------|:-------------------------------------|:-------------------|------------:|------------------:|-----------------------:|------------------------------:|
| wrong_lag_future_spread    | taker_flow_like\|basis_premium_like  | gated_sign         |          60 |                24 |               3.70427  |                  -0.000725351 |
| wrong_lag_future_spread    | liquidity_like                       | single             |          45 |                18 |               5.04795  |                  -0.000954736 |
| wrong_lag_future_spread    | open_interest_like\|positioning_like | delta_x_divergence |          42 |                22 |               7.17237  |                  -0.00109656  |
| wrong_lag_future_spread    | liquidity_like\|volatility_like      | liquidity_shock    |          33 |                21 |               1.75883  |                  -0.0011461   |
| wrong_lag_future_spread    | taker_flow_like\|open_interest_like  | flow_x_leverage    |          33 |                21 |               3.22015  |                  -0.00110292  |
| same_family_placebo_spread | liquidity_like\|volatility_like      | liquidity_shock    |          22 |                19 |               1.52353  |                  -0.000883965 |
| wrong_lag_stale_spread     | liquidity_like\|volatility_like      | liquidity_shock    |          17 |                14 |               1.04372  |                  -0.00104834  |
| time_shuffle_spread        | open_interest_like\|positioning_like | delta_x_divergence |          15 |                 9 |               3.75762  |                  -0.000827349 |
| wrong_lag_stale_spread     | open_interest_like\|positioning_like | delta_x_divergence |          15 |                12 |               1.39103  |                  -0.000678378 |
| wrong_lag_stale_spread     | taker_flow_like\|open_interest_like  | flow_x_leverage    |          12 |                 9 |               2.70213  |                  -0.00105252  |
| time_shuffle_spread        | taker_flow_like\|open_interest_like  | flow_x_leverage    |          10 |                 9 |               1.37322  |                  -0.00104663  |
| time_shuffle_spread        | liquidity_like\|volatility_like      | liquidity_shock    |           9 |                 8 |               0.876423 |                  -8.64066e-05 |
| symbol_shuffle_spread      | taker_flow_like\|open_interest_like  | flow_x_leverage    |           9 |                 8 |               2.10313  |                  -0.000808473 |
| same_family_placebo_spread | taker_flow_like\|basis_premium_like  | gated_sign         |           8 |                 6 |               1.48667  |                  -0.00033282  |
| same_family_placebo_spread | taker_flow_like\|open_interest_like  | flow_x_leverage    |           8 |                 8 |               2.44422  |                  -0.000906633 |
| same_family_placebo_spread | open_interest_like\|positioning_like | delta_x_divergence |           7 |                 6 |               1.36935  |                  -0.00086607  |
| wrong_lag_future_spread    | open_interest_like                   | single             |           7 |                 4 |               3.44798  |                  -0.00114232  |
| same_family_placebo_spread | liquidity_like                       | single             |           6 |                 6 |               1.00067  |                  -0.00131967  |
| symbol_shuffle_spread      | open_interest_like\|positioning_like | delta_x_divergence |           5 |                 4 |               1.8176   |                  -0.000586497 |
| wrong_lag_stale_spread     | liquidity_like                       | single             |           5 |                 4 |               0.98088  |                  -0.00123603  |
| wrong_lag_stale_spread     | taker_flow_like\|basis_premium_like  | gated_sign         |           4 |                 4 |               1.06169  |                  -0.000785917 |
| symbol_shuffle_spread      | liquidity_like\|volatility_like      | liquidity_shock    |           3 |                 3 |               2.51076  |                  -0.00102734  |
| time_shuffle_spread        | liquidity_like                       | single             |           3 |                 3 |               1.64921  |                  -0.00121442  |
| time_shuffle_spread        | open_interest_like                   | single             |           2 |                 2 |             100.454    |                  -0.000984078 |
| wrong_lag_stale_spread     | open_interest_like                   | single             |           2 |                 2 |               4.64849  |                  -0.00125151  |
| symbol_shuffle_spread      | liquidity_like                       | single             |           1 |                 1 |               2.06776  |                  -0.00116416  |
| same_family_placebo_spread | open_interest_like                   | single             |           1 |                 1 |              11.3922   |                  -0.00114424  |

## Blocked Tasks

| task                                | reason                                                             |
|:------------------------------------|:-------------------------------------------------------------------|
| A7FF-CORE15                         | blocked until repaired packet replay produces enough clean breadth |
| A7FF large search                   | blocked; CORE14E replay-clean pool has only two candidates         |
| same packet rerun                   | blocked; CORE14R attributes failure to control/cost/split collapse |
| alpha proof / shadow / paper / live | not authorized                                                     |
