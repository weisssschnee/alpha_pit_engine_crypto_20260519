# CRYPTO A7AB-1 SELECTOR REWRITE DRYRUN

Generated: 2026-05-29T05:38:10Z

## Decision

`PASS_A7AB1_SELECTOR_REWRITE_DRYRUN_READY_FOR_A7AB2_CONTRACT`

A7AB-1 constructs a dry-run selector queue from A7AA primitive response candidates. It does not generate formulas, run replay, train a model, or authorize search execution.

## Manifest

```json
{
  "authorizes_a7ab2_seed_constrained_micro_generation_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 11,
  "decision": "PASS_A7AB1_SELECTOR_REWRITE_DRYRUN_READY_FOR_A7AB2_CONTRACT",
  "eligible_count": 11,
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_selector_dryrun": true,
  "executes_training": false,
  "generated_at": "2026-05-29T05:38:10Z",
  "input_files": {
    "a7aa1_candidates": {
      "exists": true,
      "modified_time_utc": "2026-05-29T05:29:37Z",
      "path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7aa1_primitive_response_map\\a7aa1_primitive_response_candidates.csv",
      "size_bytes": 7764
    },
    "a7aa2_seeds": {
      "exists": true,
      "modified_time_utc": "2026-05-29T05:30:56Z",
      "path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7aa2_feature_role_classification\\a7aa2_selector_seed_fields.csv",
      "size_bytes": 1077
    },
    "a7aa3_contract": {
      "exists": true,
      "modified_time_utc": "2026-05-29T05:31:49Z",
      "path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7aa3_selector_rewrite_contract\\a7aa3_selector_rewrite_contract.json",
      "size_bytes": 1032
    },
    "a7ab0_manifest": {
      "exists": true,
      "modified_time_utc": "2026-05-29T05:36:23Z",
      "path": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ab0_selector_rewrite_dryrun_contract\\a7ab0_manifest.json",
      "size_bytes": 935
    }
  },
  "selected_count": 10,
  "selected_field_family_count": 3,
  "selected_max_control_ratio": 0.939507952084472,
  "selected_seed_field_count": 5,
  "selection_caps": {
    "max_per_family": 4,
    "max_per_field": 3,
    "max_selected": 10
  },
  "stage": "A7AB-1",
  "top_family_share": 0.4,
  "top_field_share": 0.3,
  "uses_may": false
}
```

## Bias / Leakage Boundary

- May is not used in selector score, thresholds, generation, mutation, or authorization.
- Inputs are primitive response diagnostics, not a tradable replay.
- Queue entries are blueprint seeds only; they are not alpha candidates.
- Formula search execution remains unauthorized.

## Selected Queue

|   selector_rank | candidate_id   | field_name           | field_family   | transform   | label_family                       |   label_horizon_h |   control_ratio_premay_max |   robust_tstat_floor |   selector_score | blueprint                                                                                               |
|----------------:|:---------------|:---------------------|:---------------|:------------|:-----------------------------------|------------------:|---------------------------:|---------------------:|-----------------:|:--------------------------------------------------------------------------------------------------------|
|               1 | a7ab1_seed_000 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 1 |                   0.254317 |              5.82858 |         0.880604 | primitive_response::trade_return_1h::level::L7_ranked_future_return::1h::short_high                     |
|               2 | a7ab1_seed_002 | trade_return_1h      | price_return   | cs_rank     | L7_ranked_future_return            |                 1 |                   0.254317 |              5.82858 |         0.880604 | primitive_response::trade_return_1h::cs_rank::L7_ranked_future_return::1h::short_high                   |
|               3 | a7ab1_seed_001 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 4 |                   0.267545 |              4.02451 |         0.842707 | primitive_response::trade_return_1h::level::L7_ranked_future_return::4h::short_high                     |
|               4 | a7ab1_seed_006 | realized_vol_168h    | volatility     | level       | L7_ranked_future_return            |                 1 |                   0.879498 |              2.58608 |         0.707708 | primitive_response::realized_vol_168h::level::L7_ranked_future_return::1h::short_high                   |
|               5 | a7ab1_seed_007 | realized_vol_168h    | volatility     | cs_rank     | L7_ranked_future_return            |                 1 |                   0.879498 |              2.58608 |         0.707708 | primitive_response::realized_vol_168h::cs_rank::L7_ranked_future_return::1h::short_high                 |
|               6 | a7ab1_seed_004 | realized_vol_24h     | volatility     | level       | L7_ranked_future_return            |                 1 |                   0.939508 |              2.20909 |         0.681396 | primitive_response::realized_vol_24h::level::L7_ranked_future_return::1h::short_high                    |
|               7 | a7ab1_seed_005 | realized_vol_24h     | volatility     | cs_rank     | L7_ranked_future_return            |                 1 |                   0.939508 |              2.20909 |         0.681396 | primitive_response::realized_vol_24h::cs_rank::L7_ranked_future_return::1h::short_high                  |
|               8 | a7ab1_seed_008 | premium_close_bps    | basis_premium  | delta_24h   | L7_ranked_future_return            |                 1 |                   0.791438 |              2.10327 |         0.620536 | primitive_response::premium_close_bps::delta_24h::L7_ranked_future_return::1h::short_high               |
|               9 | a7ab1_seed_010 | mark_index_basis_bps | basis_premium  | delta_24h   | L1_cross_sectional_relative_return |                 1 |                   0.785786 |              4.09822 |         0.579692 | primitive_response::mark_index_basis_bps::delta_24h::L1_cross_sectional_relative_return::1h::short_high |
|              10 | a7ab1_seed_009 | mark_index_basis_bps | basis_premium  | delta_24h   | L0_raw_forward_return              |                 1 |                   0.785786 |              4.09822 |         0.579692 | primitive_response::mark_index_basis_bps::delta_24h::L0_raw_forward_return::1h::short_high              |

## Scoreboard

| candidate_id   | field_name           | field_family   | transform   | label_family                       |   label_horizon_h | eligible   |   control_ratio_premay_max |   robust_tstat_floor |   selector_score | reject_reasons   |
|:---------------|:---------------------|:---------------|:------------|:-----------------------------------|------------------:|:-----------|---------------------------:|---------------------:|-----------------:|:-----------------|
| a7ab1_seed_000 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 1 | True       |                   0.254317 |              5.82858 |         0.880604 |                  |
| a7ab1_seed_002 | trade_return_1h      | price_return   | cs_rank     | L7_ranked_future_return            |                 1 | True       |                   0.254317 |              5.82858 |         0.880604 |                  |
| a7ab1_seed_001 | trade_return_1h      | price_return   | level       | L7_ranked_future_return            |                 4 | True       |                   0.267545 |              4.02451 |         0.842707 |                  |
| a7ab1_seed_003 | trade_return_1h      | price_return   | cs_rank     | L7_ranked_future_return            |                 4 | True       |                   0.267545 |              4.02451 |         0.842707 |                  |
| a7ab1_seed_006 | realized_vol_168h    | volatility     | level       | L7_ranked_future_return            |                 1 | True       |                   0.879498 |              2.58608 |         0.707708 |                  |
| a7ab1_seed_007 | realized_vol_168h    | volatility     | cs_rank     | L7_ranked_future_return            |                 1 | True       |                   0.879498 |              2.58608 |         0.707708 |                  |
| a7ab1_seed_004 | realized_vol_24h     | volatility     | level       | L7_ranked_future_return            |                 1 | True       |                   0.939508 |              2.20909 |         0.681396 |                  |
| a7ab1_seed_005 | realized_vol_24h     | volatility     | cs_rank     | L7_ranked_future_return            |                 1 | True       |                   0.939508 |              2.20909 |         0.681396 |                  |
| a7ab1_seed_008 | premium_close_bps    | basis_premium  | delta_24h   | L7_ranked_future_return            |                 1 | True       |                   0.791438 |              2.10327 |         0.620536 |                  |
| a7ab1_seed_010 | mark_index_basis_bps | basis_premium  | delta_24h   | L1_cross_sectional_relative_return |                 1 | True       |                   0.785786 |              4.09822 |         0.579692 |                  |
| a7ab1_seed_009 | mark_index_basis_bps | basis_premium  | delta_24h   | L0_raw_forward_return              |                 1 | True       |                   0.785786 |              4.09822 |         0.579692 |                  |

## Hard Gate Audit

| candidate_id   | seed_field   | premay_all_positive   | control_ratio_lt_1   | lag_ok   | label_allowed   | horizon_allowed   | no_may_used   | eligible   | reject_reasons   |
|:---------------|:-------------|:----------------------|:---------------------|:---------|:----------------|:------------------|:--------------|:-----------|:-----------------|
| a7ab1_seed_000 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_001 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_002 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_003 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_004 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_005 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_006 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_007 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_008 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_009 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
| a7ab1_seed_010 | True         | True                  | True                 | True     | True            | True              | True          | True       |                  |
