# CRYPTO A7FF-CORE13E NUMERIC RESPONSE EXECUTION

Generated: 2026-06-01T03:35:21Z

## Decision

`PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14`

A7FF-CORE13E executes numeric response over CORE12E temp subgraphs. It does not run replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core14": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 416,
  "decision": "PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14",
  "eval_error_count": 0,
  "executes_numeric": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T03:35:21Z",
  "motif_bucket_count_with_clues": 5,
  "next_allowed": "A7FF-CORE14 replay-preflight contract",
  "numeric_clue_candidate_count": 255,
  "numeric_clue_rows": 707,
  "response_rows": 4992,
  "sample_rows": 169243,
  "sample_timestamp_count": 512,
  "semantic_bucket_count_with_clues": 6,
  "source_decision": "PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E",
  "source_stage": "A7FF-CORE13",
  "stage": "A7FF-CORE13E"
}
```

## Label Summary

| label_id                           |   horizon |   rows |   numeric_clues |   candidate_count |   median_control_ratio |
|:-----------------------------------|----------:|-------:|----------------:|------------------:|-----------------------:|
| L1_cross_sectional_relative_return |         4 |    416 |              86 |               416 |                1.37147 |
| L3_liquidity_tier_relative_return  |         1 |    416 |              78 |               416 |                1.42895 |
| L1_cross_sectional_relative_return |         1 |    416 |              77 |               416 |                1.69405 |
| L1_cross_sectional_relative_return |         8 |    416 |              75 |               416 |                1.50082 |
| L1_cross_sectional_relative_return |        24 |    416 |              71 |               416 |                1.35577 |
| L3_liquidity_tier_relative_return  |         4 |    416 |              69 |               416 |                1.55307 |
| L3_liquidity_tier_relative_return  |        24 |    416 |              55 |               416 |                1.50148 |
| L3_liquidity_tier_relative_return  |         8 |    416 |              54 |               416 |                1.79899 |
| L5_vol_adjusted_return             |         1 |    416 |              47 |               416 |                2.5643  |
| L5_vol_adjusted_return             |         8 |    416 |              44 |               416 |                1.80426 |
| L5_vol_adjusted_return             |         4 |    416 |              35 |               416 |                2.55981 |
| L5_vol_adjusted_return             |        24 |    416 |              16 |               416 |                2.47531 |

## Family Summary

| semantic_bucket                      | motif_bucket       | generation_mode        |   rows |   numeric_clues |   candidate_count |   median_control_ratio |
|:-------------------------------------|:-------------------|:-----------------------|-------:|----------------:|------------------:|-----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_mul_delta   |    960 |             203 |                80 |                1.39212 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_mul_delta   |    840 |             184 |                70 |                2.01969 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_mul_delta   |    960 |             113 |                80 |                1.61577 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_mul_delta   |    420 |              92 |                35 |                1.47244 |
| liquidity_like                       | single             | seed_field_mul_delta   |    840 |              74 |                70 |                1.41118 |
| open_interest_like                   | single             | seed_field_mul_delta   |    192 |              16 |                16 |                1.86451 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_rank_spread |    420 |              12 |                35 |                2.1451  |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_safe_div    |    120 |               9 |                10 |                2.61605 |
| liquidity_like                       | single             | seed_field_rank_spread |    120 |               4 |                10 |                4.63166 |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_rank_spread |    120 |               0 |                10 |               11.7007  |
