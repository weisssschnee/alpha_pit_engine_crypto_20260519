# CRYPTO A7FF-CORE14 REPLAY-PREFLIGHT CONTRACT

Generated: 2026-06-01T03:38:58Z

## Decision

`PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E`

A7FF-CORE14 builds a bounded replay packet from CORE13E numeric clues. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core14e": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T03:38:58Z",
  "motif_bucket_count": 5,
  "next_allowed": "A7FF-CORE14E bounded replay execution",
  "numeric_clue_candidate_count": 255,
  "packet_candidate_count": 128,
  "semantic_bucket_count": 6,
  "source_decision": "PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14",
  "source_stage": "A7FF-CORE13E",
  "stage": "A7FF-CORE14",
  "top_motif_share": 0.21875,
  "top_semantic_share": 0.21875
}
```

## Gates

| gate                       | pass   |
|:---------------------------|:-------|
| packet_count_gte_64        | True   |
| semantic_buckets_gte_5     | True   |
| motif_buckets_gte_5        | True   |
| top_semantic_share_lte_035 | True   |
| top_motif_share_lte_035    | True   |

## Family Summary

| semantic_bucket                      | motif_bucket       | generation_mode        |   candidate_count |   median_control_ratio |
|:-------------------------------------|:-------------------|:-----------------------|------------------:|-----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    | seed_field_mul_delta   |                28 |               0.35921  |
| open_interest_like\|positioning_like | delta_x_divergence | seed_field_mul_delta   |                28 |               0.420031 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    | seed_field_mul_delta   |                24 |               0.475126 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_mul_delta   |                21 |               0.54807  |
| liquidity_like                       | single             | seed_field_mul_delta   |                20 |               0.38038  |
| open_interest_like                   | single             | seed_field_mul_delta   |                 4 |               0.491251 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_safe_div    |                 2 |               0.453816 |
| taker_flow_like\|basis_premium_like  | gated_sign         | seed_field_rank_spread |                 1 |               0.534344 |

## Label Summary

| label_id                           |   horizon |   candidate_count |   clue_rows |   median_control_ratio |
|:-----------------------------------|----------:|------------------:|------------:|-----------------------:|
| L1_cross_sectional_relative_return |         4 |                68 |          68 |               0.639617 |
| L1_cross_sectional_relative_return |         8 |                59 |          59 |               0.607831 |
| L1_cross_sectional_relative_return |         1 |                56 |          56 |               0.539985 |
| L1_cross_sectional_relative_return |        24 |                53 |          53 |               0.620123 |
| L3_liquidity_tier_relative_return  |         1 |                53 |          53 |               0.54807  |
| L3_liquidity_tier_relative_return  |         4 |                52 |          52 |               0.557914 |
| L3_liquidity_tier_relative_return  |        24 |                49 |          49 |               0.603277 |
| L3_liquidity_tier_relative_return  |         8 |                46 |          46 |               0.616478 |
| L5_vol_adjusted_return             |         1 |                28 |          28 |               0.67824  |
| L5_vol_adjusted_return             |         8 |                28 |          28 |               0.683163 |
| L5_vol_adjusted_return             |         4 |                23 |          23 |               0.601281 |
| L5_vol_adjusted_return             |        24 |                 9 |           9 |               0.629327 |
