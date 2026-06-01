# CRYPTO A7FF-CORE14SER REPAIRED REPLAY FORENSIC

Generated: 2026-06-01T07:07:18Z

## Decision

`PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION`

A7FF-CORE14SER freezes the repaired-packet bounded replay result. It does not authorize CORE15, formula search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15_contract": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 128,
  "clean_candidate_count": 1,
  "clean_family_concentration": 1.0,
  "clean_motif_bucket_count": 1,
  "clean_semantic_bucket_count": 1,
  "completed_shard_count": 16,
  "decision": "PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION",
  "dominant_failure": "objective_surface_not_replay_stable",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T07:07:18Z",
  "max_candidates_under_relaxed_sensitivity": 22,
  "next_allowed": "A7FF-CORE15X objective-surface reset / replay-stability repair contract",
  "source_decision": "HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE",
  "source_stage": "A7FF-CORE14SEE",
  "stage": "A7FF-CORE14SER"
}
```

## Gate Sensitivity

|   cost_bps |   control_ratio_threshold |   both_validation_recent_candidates |   semantic_count |   motif_count |
|-----------:|--------------------------:|------------------------------------:|-----------------:|--------------:|
|          0 |                       0.8 |                                   1 |                1 |             1 |
|          0 |                       1   |                                   2 |                1 |             1 |
|          0 |                       1.5 |                                   7 |                3 |             3 |
|          0 |                       2   |                                  10 |                4 |             4 |
|          0 |                       3   |                                  22 |                5 |             5 |
|          2 |                       0.8 |                                   1 |                1 |             1 |
|          2 |                       1   |                                   2 |                1 |             1 |
|          2 |                       1.5 |                                   5 |                3 |             3 |
|          2 |                       2   |                                   5 |                3 |             3 |
|          2 |                       3   |                                   9 |                4 |             4 |
|          5 |                       0.8 |                                   0 |                0 |             0 |
|          5 |                       1   |                                   1 |                1 |             1 |
|          5 |                       1.5 |                                   2 |                2 |             2 |
|          5 |                       2   |                                   2 |                2 |             2 |
|          5 |                       3   |                                   4 |                3 |             3 |
|         10 |                       0.8 |                                   0 |                0 |             0 |
|         10 |                       1   |                                   0 |                0 |             0 |
|         10 |                       1.5 |                                   0 |                0 |             0 |
|         10 |                       2   |                                   0 |                0 |             0 |
|         10 |                       3   |                                   2 |                2 |             2 |

## Family Summary

| semantic_bucket                      | motif_bucket       |   candidate_count |   clean_candidate_count |   near_miss_count |   median_min_control_ratio |   median_cost_adjusted_spread |   max_tstat |
|:-------------------------------------|:-------------------|------------------:|------------------------:|------------------:|---------------------------:|------------------------------:|------------:|
| taker_flow_like\|basis_premium_like  | gated_sign         |                25 |                       1 |                 2 |                   1.51876  |                  -0.000276485 |     3.55001 |
| open_interest_like\|positioning_like | delta_x_divergence |                25 |                       0 |                 3 |                   1.92332  |                  -0.000485551 |     2.45004 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                25 |                       0 |                 3 |                   1.25665  |                  -0.000721968 |     3.39132 |
| liquidity_like\|volatility_like      | liquidity_shock    |                25 |                       0 |                 2 |                   0.973382 |                  -0.000595055 |     2.51255 |
| open_interest_like                   | single             |                 5 |                       0 |                 1 |                   0.914855 |                  -0.000818321 |     1.67578 |
| liquidity_like                       | single             |                23 |                       0 |                 0 |                   2.13067  |                  -0.000943595 |     1.59168 |

## Split Summary

| split      | semantic_bucket                      | motif_bucket       |   candidate_count |   positive_rows |   control_clean_rows |   median_cost_adjusted_spread |   median_control_ratio |
|:-----------|:-------------------------------------|:-------------------|------------------:|----------------:|---------------------:|------------------------------:|-----------------------:|
| recent     | taker_flow_like\|open_interest_like  | flow_x_leverage    |                25 |               9 |                    4 |                  -0.000867637 |                2.23029 |
| train      | taker_flow_like\|open_interest_like  | flow_x_leverage    |                25 |               9 |                    3 |                  -0.000864159 |                1.92237 |
| train      | liquidity_like\|volatility_like      | liquidity_shock    |                25 |               8 |                   10 |                  -0.00107449  |                1.17386 |
| recent     | open_interest_like\|positioning_like | delta_x_divergence |                25 |               8 |                    4 |                  -0.000907003 |                3.07177 |
| validation | liquidity_like\|volatility_like      | liquidity_shock    |                25 |               8 |                    2 |                  -0.000792922 |                2.36831 |
| train      | open_interest_like\|positioning_like | delta_x_divergence |                25 |               5 |                    5 |                  -0.000752691 |                2.1591  |
| recent     | taker_flow_like\|basis_premium_like  | gated_sign         |                25 |               5 |                    4 |                  -0.000318999 |                2.73274 |
| validation | taker_flow_like\|open_interest_like  | flow_x_leverage    |                25 |               5 |                    1 |                  -0.00121416  |                2.64465 |
| train      | taker_flow_like\|basis_premium_like  | gated_sign         |                25 |               4 |                    1 |                  -0.000923262 |                5.23604 |
| validation | liquidity_like                       | single             |                23 |               4 |                    1 |                  -0.00112674  |                6.21438 |
| validation | taker_flow_like\|basis_premium_like  | gated_sign         |                25 |               3 |                    6 |                  -0.0004827   |                1.62642 |
| recent     | liquidity_like\|volatility_like      | liquidity_shock    |                25 |               3 |                    5 |                  -0.000869653 |                1.76978 |
| validation | open_interest_like\|positioning_like | delta_x_divergence |                25 |               3 |                    0 |                  -0.000697159 |                2.70847 |
| recent     | open_interest_like                   | single             |                 5 |               2 |                    1 |                  -0.000667754 |                3.44798 |
| train      | liquidity_like                       | single             |                23 |               1 |                    4 |                  -0.00171972  |                3.77462 |
| validation | open_interest_like                   | single             |                 5 |               0 |                    2 |                  -0.00114232  |                1.38306 |
| train      | open_interest_like                   | single             |                 5 |               0 |                    1 |                  -0.00140996  |                3.64713 |
| recent     | liquidity_like                       | single             |                23 |               0 |                    0 |                  -0.00102773  |                3.55721 |

## Clean Candidates

| candidate_id                   | semantic_bucket                     | motif_bucket   |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |   shard_id |
|:-------------------------------|:------------------------------------|:---------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|-----------:|
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like | gated_sign     |            12 |      0.00102972 |                  -3.83035e-05 |     2.85705 |            0.660905 |                                2 | True           |          9 |
