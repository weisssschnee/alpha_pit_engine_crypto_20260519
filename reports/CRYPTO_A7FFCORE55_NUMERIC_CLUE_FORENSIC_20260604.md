# CRYPTO A7FF-CORE55 NUMERIC CLUE FORENSIC

Generated: 2026-06-04T07:21:52Z

## Decision

`PASS_A7FFCORE55_REPLAY_READY_PACKET_BUILT`

CORE55 consolidates CORE54E numeric clues into a replay-ready packet. It filters L7-only, control-dominated, lag/robust fragile, duplicate production, and over-concentrated semantic/skeleton structures. It does not execute replay or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core56_bounded_replay_preflight": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE55_REPLAY_READY_PACKET_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T07:21:52Z",
  "non_l7_clue_rows": 348,
  "replay_packet_label_family_count": 4,
  "replay_packet_selected_overlap_count": 44,
  "replay_packet_semantic_pair_count": 9,
  "replay_packet_top_semantic_pair_share": 0.2807017543859649,
  "replay_ready_packet_count": 114,
  "response_rows": 41420,
  "source_decision": "PASS_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION_READY_FOR_CORE55",
  "source_stage": "A7FF-CORE54E",
  "stage": "A7FF-CORE55",
  "unique_candidate_count": 120,
  "uses_may": false
}
```

## Label Summary

| label_family                       |   label_horizon_h |   row_count |
|:-----------------------------------|------------------:|------------:|
| L5_vol_adjusted_return             |                 1 |          57 |
| L1_cross_sectional_relative_return |                 1 |          49 |
| L3_liquidity_tier_relative_return  |                 1 |          49 |
| L0_raw_forward_return              |                 1 |          43 |
| L1_cross_sectional_relative_return |                 4 |          29 |
| L0_raw_forward_return              |                 4 |          26 |
| L3_liquidity_tier_relative_return  |                 4 |          25 |
| L5_vol_adjusted_return             |                 4 |          21 |
| L5_vol_adjusted_return             |                 8 |          17 |
| L3_liquidity_tier_relative_return  |                 8 |          12 |
| L0_raw_forward_return              |                 8 |          10 |
| L1_cross_sectional_relative_return |                 8 |           7 |
| L5_vol_adjusted_return             |                24 |           2 |
| L3_liquidity_tier_relative_return  |                24 |           1 |

## Replay Packet Semantic Summary

| semantic_pair                         | best_label_family                  |   row_count |
|:--------------------------------------|:-----------------------------------|------------:|
| basis_premium_like|price_like         | L5_vol_adjusted_return             |          24 |
| basis_premium_like|volatility_like    | L5_vol_adjusted_return             |          19 |
| basis_premium_like|basis_premium_like | L5_vol_adjusted_return             |          15 |
| price_like|volatility_like            | L5_vol_adjusted_return             |           7 |
| basis_premium_like|volatility_like    | L3_liquidity_tier_relative_return  |           6 |
| basis_premium_like                    | L5_vol_adjusted_return             |           5 |
| price_like                            | L5_vol_adjusted_return             |           5 |
| basis_premium_like|positioning_like   | L5_vol_adjusted_return             |           4 |
| basis_premium_like|price_like         | L0_raw_forward_return              |           4 |
| basis_premium_like|basis_premium_like | L1_cross_sectional_relative_return |           4 |
| basis_premium_like                    | L3_liquidity_tier_relative_return  |           3 |
| basis_premium_like|basis_premium_like | L3_liquidity_tier_relative_return  |           3 |
| basis_premium_like|basis_premium_like | L0_raw_forward_return              |           2 |
| basis_premium_like|price_like         | L3_liquidity_tier_relative_return  |           2 |
| price_like|volatility_like            | L1_cross_sectional_relative_return |           2 |
| liquidity_like|volatility_like        | L3_liquidity_tier_relative_return  |           2 |
| basis_premium_like|price_like         | L1_cross_sectional_relative_return |           2 |
| basis_premium_like|volatility_like    | L0_raw_forward_return              |           1 |
| basis_premium_like|volatility_like    | L1_cross_sectional_relative_return |           1 |
| price_like                            | L3_liquidity_tier_relative_return  |           1 |
| price_like|volatility_like            | L0_raw_forward_return              |           1 |
| volatility_like                       | L1_cross_sectional_relative_return |           1 |

## Selected Overlap Audit

| selected_overlap   | semantic_pair                         |   row_count |
|:-------------------|:--------------------------------------|------------:|
| False              | basis_premium_like|price_like         |          25 |
| False              | basis_premium_like|volatility_like    |          16 |
| False              | basis_premium_like|basis_premium_like |          15 |
| True               | basis_premium_like|price_like         |          13 |
| True               | basis_premium_like|volatility_like    |          11 |
| True               | basis_premium_like|basis_premium_like |           9 |
| False              | basis_premium_like                    |           7 |
| False              | price_like                            |           5 |
| False              | price_like|volatility_like            |           5 |
| True               | price_like|volatility_like            |           5 |
| True               | basis_premium_like|positioning_like   |           4 |
| False              | liquidity_like|volatility_like        |           2 |
| True               | basis_premium_like                    |           1 |
| False              | volatility_like                       |           1 |
| True               | price_like                            |           1 |

## Reject Reason Summary

| reject_reason     |   row_count |
|:------------------|------------:|
| semantic_pair_cap |           6 |

## Replay Ready Packet Preview

| blueprint_id             | semantic_pair                         | motif        | best_label_family                 |   best_label_horizon_h |   best_control_ratio |   score | selected_overlap   |
|:-------------------------|:--------------------------------------|:-------------|:----------------------------------|-----------------------:|---------------------:|--------:|:-------------------|
| a7ff24r_858ff2210f276fcf | basis_premium_like                    | single       | L5_vol_adjusted_return            |                      8 |             0.619643 | 46.9822 | True               |
| a7ff24r_650915032f2a5979 | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return            |                      8 |             0.692411 | 46.2545 | True               |
| a7ff24r_1e19db32c95dfcc4 | basis_premium_like|positioning_like   | smooth_mul   | L5_vol_adjusted_return            |                      8 |             0.455168 | 38.7305 | True               |
| a7ff24r_010c17f20813e83d | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return            |                      1 |             0.182    | 38.5409 | True               |
| a7ff24r_503edc81504e964a | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return            |                     24 |             0.675618 | 35.3751 | True               |
| a7ff24r_892545e2049b6eba | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.42915  | 32.3174 | True               |
| a7ff24r_12f75c2e2796dd6e | basis_premium_like|positioning_like   | mul          | L5_vol_adjusted_return            |                      8 |             0.327663 | 32.0263 | True               |
| a7ff24r_146a079f1808397b | basis_premium_like|positioning_like   | safe_div_abs | L5_vol_adjusted_return            |                      8 |             0.550424 | 31.5974 | True               |
| a7ff24r_5ee045650ebd8b30 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.238595 | 29.9781 | True               |
| a7ff24r_0e8cf4f2d2d653c7 | basis_premium_like|positioning_like   | spread_rank  | L5_vol_adjusted_return            |                      4 |             0.339857 | 29.9454 | True               |
| a7ff24r_129519e7eda158fa | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.302899 | 29.6195 | True               |
| a7ff24r_62921caa01dbd001 | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.316995 | 28.3523 | True               |
| a7ff24r_1e349d20bff26d23 | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.316688 | 26.8347 | True               |
| a7ff24r_8d906801b8dec4c0 | basis_premium_like|basis_premium_like | mul          | L5_vol_adjusted_return            |                      1 |             0.600993 | 26.5286 | True               |
| a7ff24r_20b072602eeb21eb | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return            |                      8 |             0.705129 | 25.7569 | True               |
| a7ff24r_1c490f81c21f5f03 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.474078 | 25.5943 | True               |
| a7ff24r_2fff7c49f91def0b | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return            |                      1 |             0.423862 | 25.4856 | True               |
| a7ff24r_2f417cea53e275b6 | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return            |                      8 |             0.718569 | 25.4636 | True               |
| a7ff24r_7affd59d06f0cdfa | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return            |                      8 |             0.718569 | 25.4636 | True               |
| a7ff24r_072721eac2a0cfd3 | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return            |                      4 |             0.600021 | 23.869  | True               |
| a7ff24r_48f9f812cd8214e5 | basis_premium_like|basis_premium_like | gated_sign   | L5_vol_adjusted_return            |                      1 |             0.836802 | 23.1103 | True               |
| a7ff24r_14bb4d389b4b94f0 | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return            |                      1 |             0.798537 | 20.4097 | True               |
| a7ff24r_7b8607bc81201fb8 | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return            |                      1 |             0.654717 | 19.887  | True               |
| a7ff24r_c223ee324263786f | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.674115 | 19.8331 | True               |
| a7ff24r_145e2d58adad4f4a | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return            |                      4 |             0.78766  | 19.7793 | True               |
| a7ff24r_7a6f873cfe7bc14d | basis_premium_like|volatility_like    | mul          | L5_vol_adjusted_return            |                      8 |             0.979541 | 19.7713 | True               |
| a7ff24r_b74c05b6f58309a0 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.500841 | 19.4471 | True               |
| a7ff24r_0f7490654a6a7b63 | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return            |                      1 |             0.73417  | 18.9798 | True               |
| a7ff24r_2896b670ebf3967c | price_like|volatility_like            | mul          | L5_vol_adjusted_return            |                      1 |             0.76241  | 18.5573 | True               |
| a7ff24r_389e925b81a0c645 | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return            |                      4 |             0.877285 | 18.4189 | True               |
| a7ff24r_ff9b56ccd0b1474f | price_like                            | single       | L5_vol_adjusted_return            |                      4 |             0.608639 | 18.3777 | True               |
| a7ff24r_28c1f862a15e5d51 | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.841929 | 17.5779 | True               |
| a7ff24r_8931a4d48577eac9 | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return            |                      1 |             0.791905 | 16.9418 | True               |
| a7ff24r_0d2e211c74b8ab69 | price_like|volatility_like            | mul          | L5_vol_adjusted_return            |                      1 |             0.871767 | 16.2604 | True               |
| a7ff24r_75f3e9364180854b | price_like|volatility_like            | mul          | L5_vol_adjusted_return            |                      1 |             0.896893 | 16.1915 | True               |
| a7ff24r_5c84c80e5b76b421 | basis_premium_like|price_like         | sub          | L3_liquidity_tier_relative_return |                      1 |             0.565218 | 14.9646 | True               |
| a7ff24r_87748aaea3a33f95 | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.819602 | 14.4581 | True               |
| a7ff24r_89f2b5ee0732b53d | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return            |                      1 |             0.715081 | 13.678  | True               |
| a7ff24r_b6c425eb5d65f76a | basis_premium_like|price_like         | mul          | L5_vol_adjusted_return            |                      1 |             0.804253 | 11.4568 | True               |
| a7ff24r_2353c3ae1292b858 | basis_premium_like|basis_premium_like | spread_rank  | L3_liquidity_tier_relative_return |                      4 |             0.538545 | 11.2772 | True               |

## Boundary

```text
replay executed: false
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
