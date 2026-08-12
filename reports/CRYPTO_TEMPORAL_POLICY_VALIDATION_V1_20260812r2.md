# Crypto Temporal Policy Development Validation V1

- Decision: `QUALIFY_20_20_60_FIXED_DEVELOPMENT_FLOW`
- Policy validation pass: `True`
- Evaluation lineage: reused the hash-bound 360-candidate full pass and the three completed r2 block ledgers; source-repair finalization performed zero market evaluations.
- Split: `1523` train effective hours / `1458` validation effective hours
- Boundary: development validation only; no OOS, holdout, promotion, optimizer feedback, or automatic search.

```json
{
  "temporal_program_cem": {
    "candidate_count": 120,
    "full_window_dual_net_positive_count": 34,
    "full_window_dual_net_positive_rate": 0.2833333333333333,
    "migrated_replicated_cluster_yield_per_1k": 20.1875,
    "replicated_2_of_3_count": 17,
    "replicated_2_of_3_rate": 0.14166666666666666,
    "replicated_lane_count": 4,
    "replicated_program_family_count": 1,
    "replicated_program_id_count": 13,
    "strict_evaluated_count": 108,
    "train_economic_cluster_yield_per_1k": 142.5,
    "validation_matched_positive_count": 0
  },
  "temporal_program_evolution": {
    "candidate_count": 120,
    "full_window_dual_net_positive_count": 53,
    "full_window_dual_net_positive_rate": 0.44166666666666665,
    "migrated_replicated_cluster_yield_per_1k": 50.2,
    "replicated_2_of_3_count": 12,
    "replicated_2_of_3_rate": 0.1,
    "replicated_lane_count": 4,
    "replicated_program_family_count": 2,
    "replicated_program_id_count": 7,
    "strict_evaluated_count": 108,
    "train_economic_cluster_yield_per_1k": 502.0,
    "validation_matched_positive_count": 3
  },
  "temporal_program_random": {
    "candidate_count": 120,
    "full_window_dual_net_positive_count": 39,
    "full_window_dual_net_positive_rate": 0.325,
    "migrated_replicated_cluster_yield_per_1k": 15.416666666666666,
    "replicated_2_of_3_count": 20,
    "replicated_2_of_3_rate": 0.16666666666666666,
    "replicated_lane_count": 4,
    "replicated_program_family_count": 2,
    "replicated_program_id_count": 12,
    "strict_evaluated_count": 111,
    "train_economic_cluster_yield_per_1k": 92.5,
    "validation_matched_positive_count": 1
  }
}
```
