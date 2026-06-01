# CRYPTO A7FF-CORE13 NUMERIC RESPONSE CONTRACT

Generated: 2026-06-01T01:47:49Z

## Decision

`PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E`

A7FF-CORE13 defines numeric response execution over CORE12E materialized temp subgraphs. It does not execute numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core13e": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "control_count": 5,
  "decision": "PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E",
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T01:47:49Z",
  "horizon_count": 4,
  "label_count": 3,
  "motif_bucket_count": 5,
  "next_allowed": "A7FF-CORE13E numeric response execution",
  "queue_count": 416,
  "semantic_bucket_count": 6,
  "shard_count": 4,
  "source_decision": "PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13",
  "source_stage": "A7FF-CORE12E",
  "stage": "A7FF-CORE13"
}
```

## Shard Plan

| shard_id   |   start_index |   end_index_exclusive |   candidate_count |
|:-----------|--------------:|----------------------:|------------------:|
| S00        |             0 |                   104 |               104 |
| S01        |           104 |                   208 |               104 |
| S02        |           208 |                   312 |               104 |
| S03        |           312 |                   416 |               104 |

## Label Contract

| label_id                           |   horizon | primary_non_l7   |
|:-----------------------------------|----------:|:-----------------|
| L1_cross_sectional_relative_return |         1 | True             |
| L1_cross_sectional_relative_return |         4 | True             |
| L1_cross_sectional_relative_return |         8 | True             |
| L1_cross_sectional_relative_return |        24 | True             |
| L3_liquidity_tier_relative_return  |         1 | True             |
| L3_liquidity_tier_relative_return  |         4 | True             |
| L3_liquidity_tier_relative_return  |         8 | True             |
| L3_liquidity_tier_relative_return  |        24 | True             |
| L5_vol_adjusted_return             |         1 | True             |
| L5_vol_adjusted_return             |         4 | True             |
| L5_vol_adjusted_return             |         8 | True             |
| L5_vol_adjusted_return             |        24 | True             |

## Control Contract

| control             | dominance_role                        |
|:--------------------|:--------------------------------------|
| wrong_lag_future    | hard_control                          |
| wrong_lag_stale     | hard_control                          |
| time_shuffle        | hard_control                          |
| symbol_shuffle      | hard_control                          |
| same_family_placebo | hard_control                          |
| sign_flip           | diagnostic_only_excluded_from_abs_max |
