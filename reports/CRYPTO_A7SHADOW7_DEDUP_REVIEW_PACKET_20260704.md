# CRYPTO A7SHADOW7 Dedup Review Packet

Generated: 2026-07-03T18:10:01Z

## Decision

`PASS_A7SHADOW7_DEDUP_REVIEW_PACKET_BUILT`

A7SHADOW-7 converts the A7SHADOW-4 R3 engineering packet into a deduplicated review packet. It does not run search, replay, alpha proof, shadow, paper, or live trading.

## Counts

- input_candidate_rows: `4`
- overlap_cluster_count: `2`
- selected_count: `2`
- rejected_overlap_variant_count: `2`
- max_selected_abs_signal_corr: `0.0100151181711994`
- max_selected_abs_recent_net_return_corr: `0.0532733154551249`
- selected_family_counts: `{"funding": 1, "open_interest": 2, "premium_basis": 1}`

## Selected Review Packet

| blueprint_id   | expression                                                                                          |   horizon_h |   pareto_rank |   objective_pass_count |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_avg_turnover |   recent_capacity_proxy |   recent_control_ratio |   recent_shuffle_control_ratio | source_lag_policy_status   | candidate_key      |   recent_sortino_20bps |   recent_sharpe_20bps |   recent_max_drawdown_20bps |   recent_avg_turnover_20bps |   recent_sortino_30bps |   recent_sharpe_30bps |   recent_max_drawdown_30bps |   recent_avg_turnover_30bps |   stress_sortino_20bps |   stress_sharpe_20bps |   stress_sortino_30bps |   stress_sharpe_30bps |   dedup_score | field_family_counts                      | overlap_cluster_id    |
|:---------------|:----------------------------------------------------------------------------------------------------|------------:|--------------:|-----------------------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|----------------------:|------------------------:|-----------------------:|-------------------------------:|:---------------------------|:-------------------|-----------------------:|----------------------:|----------------------------:|----------------------------:|-----------------------:|----------------------:|----------------------------:|----------------------------:|-----------------------:|----------------------:|-----------------------:|----------------------:|--------------:|:-----------------------------------------|:----------------------|
| a7shadow2_c007 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |           8 |             1 |                     12 |         2.44731 |             15.8815  |       11.8745  |          18.3882 |                 8.50321 |                1.27322 |            0.0638847  |             5.81101e+06 |               0.993638 |                       0.398843 | SOURCE_LAG_REQUIRED_PASS   | a7shadow2_c007|h8  |               16.481   |               8.62448 |                   -0.108777 |                  0.0638847  |               15.2784  |               8.10375 |                   -0.1127   |                  0.0638847  |                4.25643 |               3.06034 |                2.93345 |               2.14559 |      15.2784  | {"funding": 1, "open_interest": 1}       | a7shadow7_cluster_001 |
| a7shadow2_c002 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |          24 |             1 |                     13 |         2.70245 |              7.71697 |        2.92514 |           5.9645 |                 1.90384 |                3.87699 |            0.00441653 |             1.09718e+07 |               1.01621  |                       0.186508 | SOURCE_LAG_REQUIRED_PASS   | a7shadow2_c002|h24 |                5.54803 |               2.35631 |                   -0.295644 |                  0.00441653 |                5.51729 |               2.34511 |                   -0.295797 |                  0.00441653 |                6.35872 |               4.22102 |                6.29119 |               4.18147 |       5.51729 | {"open_interest": 1, "premium_basis": 1} | a7shadow7_cluster_000 |

## Overlap Components

| overlap_cluster_id    |   member_count | selected_key       |   selected_score | members                               |
|:----------------------|---------------:|:-------------------|-----------------:|:--------------------------------------|
| a7shadow7_cluster_000 |              2 | a7shadow2_c002|h24 |          5.51729 | a7shadow2_c002|h24|a7shadow2_c006|h24 |
| a7shadow7_cluster_001 |              2 | a7shadow2_c007|h8  |         15.2784  | a7shadow2_c007|h4|a7shadow2_c007|h8   |

## Overlap Rejections

| candidate_key      | blueprint_id   |   horizon_h | expression                                                                                          | overlap_cluster_id    | selected_key       | reject_reason                      |   dedup_score |   selected_score |
|:-------------------|:---------------|------------:|:----------------------------------------------------------------------------------------------------|:----------------------|:-------------------|:-----------------------------------|--------------:|-----------------:|
| a7shadow2_c006|h24 | a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 | a7shadow7_cluster_000 | a7shadow2_c002|h24 | overlap_cluster_non_representative |       2.60968 |          5.51729 |
| a7shadow2_c007|h4  | a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | a7shadow7_cluster_001 | a7shadow2_c007|h8  | overlap_cluster_non_representative |       9.43019 |         15.2784  |

## Interpretation

The hard field-coverage blocker is repaired upstream, but this packet is intentionally small after overlap collapse. It is suitable for forward-locked adapter probing and search-memory feedback, not for book construction.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_live_adapter_probe": true,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7SHADOW7_DEDUP_REVIEW_PACKET_BUILT",
  "generated_at": "2026-07-03T18:10:01Z",
  "input_candidate_rows": 4,
  "input_queue": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow3_execution_realism_summary_20260703\\a7shadow3_execution_accepted.csv",
  "input_shadow4_decision": "PASS_A7SHADOW4_ENGINEERING_REVIEW_PACKET_BUILT",
  "input_shadow4_runtime": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow4_live_capacity_correlation_r3_20260704",
  "max_selected_abs_recent_net_return_corr": 0.0532733154551249,
  "max_selected_abs_signal_corr": 0.0100151181711994,
  "next_required": [
    "Run A7LIVE-0 forward-locked adapter probe on the selected review packet.",
    "Do not treat this packet as a book; selected_count remains small and family concentration remains.",
    "Use the overlap rejection map as memory for the next family-diversified search."
  ],
  "overlap_cluster_count": 2,
  "rejected_overlap_variant_count": 2,
  "selected_count": 2,
  "selected_family_counts": {
    "funding": 1,
    "open_interest": 2,
    "premium_basis": 1
  },
  "stage": "A7SHADOW-7",
  "warnings": [
    "selected_packet_open_interest_concentrated",
    "selected_packet_too_small_for_book"
  ]
}
```
