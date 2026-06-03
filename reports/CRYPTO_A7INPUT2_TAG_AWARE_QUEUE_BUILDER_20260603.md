# CRYPTO A7INPUT-2 TAG-AWARE QUEUE BUILDER

Generated: 2026-06-03T02:54:55Z

## Decision

`PASS_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_READY_FOR_CORE54`

A7INPUT-2 converts the independent input approval tags into concrete ordinary-alpha, interaction-alpha, and rescue-lane queues. It does not execute replay, formula search, alpha proof, or live/paper/shadow routing.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core54_queue_builder_contract": true,
  "authorizes_core55_numeric_preflight": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_READY_FOR_CORE54",
  "executes_replay": false,
  "executes_search": false,
  "formula_index_rows": 20599,
  "generated_at": "2026-06-03T02:54:55Z",
  "interaction_candidate_count_before_caps": 4720,
  "interaction_queue_count": 1815,
  "interaction_top_semantic_pair_share": 0.19834710743801653,
  "no_condition_only_ordinary_alpha_accepted": true,
  "no_hard_blocked_fields_accepted": true,
  "ordinary_alpha_candidate_count_before_caps": 8177,
  "ordinary_alpha_queue_count": 1875,
  "ordinary_top_info_cluster_share": 0.256,
  "ordinary_top_semantic_pair_share": 0.192,
  "ordinary_top_semantic_type_share": 0.4362666666666667,
  "queue_pass_thresholds": {
    "interaction_top_semantic_pair_share_lte": 0.2,
    "ordinary_top_info_cluster_share_lte": 0.3,
    "ordinary_top_semantic_pair_share_lte": 0.2,
    "ordinary_top_semantic_type_share_lte": 0.45
  },
  "rejected_route_rows": 46871,
  "rescue_candidate_count_before_caps": 2029,
  "rescue_queue_count": 300,
  "source_decisions": [
    "PASS_A7INPUT0_INPUT_APPROVAL_PACKAGE_READY",
    "PASS_A7INPUT1_INPUT_ROUTING_INTEGRATION_SMOKE"
  ],
  "source_stages": [
    "A7INPUT-0",
    "A7INPUT-1",
    "A7FF-v20260530"
  ],
  "stage": "A7INPUT-2"
}
```

## Queue Summary

| queue             |   row_count |   semantic_type_count |   semantic_pair_count |   info_cluster_count |   skeleton_count |   top_semantic_type_share |   top_semantic_pair_share |   top_info_cluster_share |   top_skeleton_share |
|:------------------|------------:|----------------------:|----------------------:|---------------------:|-----------------:|--------------------------:|--------------------------:|-------------------------:|---------------------:|
| ordinary_alpha    |        1875 |                     5 |                    10 |                   16 |               42 |                  0.436267 |                  0.192    |                 0.256    |            0.0490667 |
| interaction_alpha |        1815 |                     5 |                     7 |                   15 |               36 |                  0.581818 |                  0.198347 |                 0.330579 |            0.0589532 |
| rescue_lane       |         300 |                     1 |                     2 |                    1 |               32 |                  1        |                  0.79     |                 1        |            0.0633333 |

## Mode Filter Summary

| mode              | mode_decision   | mode_reason                            |   row_count |
|:------------------|:----------------|:---------------------------------------|------------:|
| interaction_alpha | accept          | interaction_route                      |        4720 |
| interaction_alpha | reject          | interaction_tag_not_allowed            |       12006 |
| interaction_alpha | reject          | interaction_requires_pair_or_condition |        3463 |
| interaction_alpha | reject          | no_approved_input_field                |         410 |
| ordinary_alpha    | accept          | ordinary_alpha_route                   |        8177 |
| ordinary_alpha    | reject          | ordinary_alpha_blocked_tag             |       12012 |
| ordinary_alpha    | reject          | no_approved_input_field                |         410 |
| rescue_lane       | accept          | rescue_lane_route                      |        2029 |
| rescue_lane       | reject          | rescue_requires_only_rescue_tags       |       18160 |
| rescue_lane       | reject          | no_approved_input_field                |         410 |

## Info Cluster Cap Audit

| queue             | info_cluster_id   |   row_count |   queue_rows |      share |
|:------------------|:------------------|------------:|-------------:|-----------:|
| interaction_alpha | ic_005            |         600 |         3630 | 0.165289   |
| interaction_alpha | ic_013            |         600 |         3630 | 0.165289   |
| interaction_alpha | ic_021            |         600 |         3630 | 0.165289   |
| interaction_alpha | ic_015            |         536 |         3630 | 0.147658   |
| interaction_alpha | ic_016            |         486 |         3630 | 0.133884   |
| interaction_alpha | ic_000            |         292 |         3630 | 0.0804408  |
| interaction_alpha | ic_003            |         280 |         3630 | 0.077135   |
| interaction_alpha | ic_014            |          92 |         3630 | 0.0253444  |
| interaction_alpha | ic_004            |          45 |         3630 | 0.0123967  |
| interaction_alpha | ic_006            |          24 |         3630 | 0.00661157 |
| interaction_alpha | ic_019            |          20 |         3630 | 0.00550964 |
| interaction_alpha | ic_008            |          16 |         3630 | 0.00440771 |
| interaction_alpha | ic_018            |          15 |         3630 | 0.00413223 |
| interaction_alpha | ic_020            |          12 |         3630 | 0.00330579 |
| interaction_alpha | ic_023            |          12 |         3630 | 0.00330579 |
| ordinary_alpha    | ic_005            |         480 |         3142 | 0.152769   |
| ordinary_alpha    | ic_013            |         480 |         3142 | 0.152769   |
| ordinary_alpha    | ic_015            |         480 |         3142 | 0.152769   |
| ordinary_alpha    | ic_021            |         480 |         3142 | 0.152769   |
| ordinary_alpha    | ic_016            |         459 |         3142 | 0.146085   |
| ordinary_alpha    | ic_003            |         288 |         3142 | 0.0916614  |
| ordinary_alpha    | ic_000            |         267 |         3142 | 0.0849777  |
| ordinary_alpha    | ic_008            |          70 |         3142 | 0.0222788  |
| ordinary_alpha    | ic_014            |          35 |         3142 | 0.0111394  |
| ordinary_alpha    | ic_006            |          24 |         3142 | 0.00763845 |
| ordinary_alpha    | ic_004            |          23 |         3142 | 0.00732018 |
| ordinary_alpha    | ic_022            |          19 |         3142 | 0.0060471  |
| ordinary_alpha    | ic_020            |          12 |         3142 | 0.00381922 |
| ordinary_alpha    | ic_023            |          12 |         3142 | 0.00381922 |
| ordinary_alpha    | ic_019            |           9 |         3142 | 0.00286442 |
| ordinary_alpha    | ic_018            |           4 |         3142 | 0.00127307 |
| rescue_lane       | ic_009            |         300 |          300 | 1          |

## Field Family Balance

| queue             | semantic_pair                         | motif               |   row_count |
|:------------------|:--------------------------------------|:--------------------|------------:|
| interaction_alpha | basis_premium_like|price_like         | smooth_mul          |         129 |
| interaction_alpha | basis_premium_like|volatility_like    | smooth_mul          |         109 |
| interaction_alpha | basis_premium_like|basis_premium_like | smooth_mul          |          92 |
| interaction_alpha | basis_premium_like|volatility_like    | spread_rank         |          92 |
| interaction_alpha | basis_premium_like|positioning_like   | signed_spread       |          79 |
| interaction_alpha | basis_premium_like|positioning_like   | smooth_mul          |          73 |
| interaction_alpha | basis_premium_like|positioning_like   | mean_reversion_gate |          72 |
| interaction_alpha | price_like|volatility_like            | smooth_mul          |          71 |
| interaction_alpha | basis_premium_like|volatility_like    | mul                 |          59 |
| interaction_alpha | basis_premium_like|price_like         | spread_rank         |          58 |
| interaction_alpha | volatility_like|volatility_like       | smooth_mul          |          56 |
| interaction_alpha | basis_premium_like|volatility_like    | gated_sign          |          54 |
| interaction_alpha | basis_premium_like|basis_premium_like | spread_rank         |          49 |
| interaction_alpha | basis_premium_like|price_like         | mul                 |          46 |
| interaction_alpha | basis_premium_like|price_like         | gated_sign          |          44 |
| interaction_alpha | price_like|volatility_like            | spread_rank         |          44 |
| interaction_alpha | basis_premium_like|price_like         | sub                 |          42 |
| interaction_alpha | basis_premium_like|positioning_like   | relative_shock      |          41 |
| interaction_alpha | basis_premium_like|price_like         | safe_div_abs        |          41 |
| interaction_alpha | basis_premium_like|positioning_like   | spread_rank         |          37 |
| interaction_alpha | price_like|volatility_like            | mul                 |          35 |
| interaction_alpha | price_like|volatility_like            | gated_sign          |          31 |
| interaction_alpha | volatility_like|volatility_like       | gated_sign          |          31 |
| interaction_alpha | volatility_like|volatility_like       | mul                 |          31 |
| interaction_alpha | volatility_like|volatility_like       | safe_div_abs        |          31 |
| interaction_alpha | volatility_like|volatility_like       | spread_rank         |          31 |
| interaction_alpha | volatility_like|volatility_like       | sub                 |          31 |
| interaction_alpha | price_like|volatility_like            | sub                 |          30 |
| interaction_alpha | price_like|volatility_like            | safe_div_abs        |          29 |
| interaction_alpha | basis_premium_like|basis_premium_like | mul                 |          27 |
| interaction_alpha | basis_premium_like|volatility_like    | sub                 |          26 |
| interaction_alpha | basis_premium_like|basis_premium_like | gated_sign          |          24 |
| interaction_alpha | basis_premium_like|basis_premium_like | sub                 |          24 |
| interaction_alpha | basis_premium_like|basis_premium_like | safe_div_abs        |          20 |
| interaction_alpha | basis_premium_like|volatility_like    | safe_div_abs        |          20 |
| interaction_alpha | basis_premium_like|positioning_like   | sub                 |          18 |
| interaction_alpha | basis_premium_like|positioning_like   | safe_div_abs        |          15 |
| interaction_alpha | basis_premium_like|positioning_like   | gated_sign          |          13 |
| interaction_alpha | basis_premium_like|positioning_like   | mul                 |          12 |
| interaction_alpha | liquidity_like|volatility_like        | mean_reversion_gate |          12 |
| interaction_alpha | liquidity_like|volatility_like        | signed_spread       |          12 |
| interaction_alpha | liquidity_like|volatility_like        | smooth_mul          |          12 |
| interaction_alpha | liquidity_like|volatility_like        | spread_rank         |          12 |
| ordinary_alpha    | basis_premium_like|price_like         | smooth_mul          |         113 |
| ordinary_alpha    | basis_premium_like|positioning_like   | signed_spread       |          85 |
| ordinary_alpha    | volatility_like                       | single              |          84 |
| ordinary_alpha    | basis_premium_like|volatility_like    | smooth_mul          |          82 |
| ordinary_alpha    | basis_premium_like|positioning_like   | mean_reversion_gate |          80 |
| ordinary_alpha    | basis_premium_like|volatility_like    | spread_rank         |          79 |
| ordinary_alpha    | basis_premium_like|positioning_like   | smooth_mul          |          67 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | smooth_mul          |          66 |
| ordinary_alpha    | basis_premium_like|price_like         | spread_rank         |          60 |
| ordinary_alpha    | volatility_like|volatility_like       | smooth_mul          |          56 |
| ordinary_alpha    | basis_premium_like|volatility_like    | mul                 |          55 |
| ordinary_alpha    | basis_premium_like|volatility_like    | gated_sign          |          50 |
| ordinary_alpha    | price_like|volatility_like            | smooth_mul          |          47 |
| ordinary_alpha    | basis_premium_like|positioning_like   | relative_shock      |          43 |
| ordinary_alpha    | basis_premium_like|price_like         | gated_sign          |          41 |
| ordinary_alpha    | basis_premium_like|price_like         | mul                 |          40 |
| ordinary_alpha    | basis_premium_like|price_like         | safe_div_abs        |          40 |
| ordinary_alpha    | basis_premium_like                    | single              |          39 |
| ordinary_alpha    | basis_premium_like|price_like         | sub                 |          39 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | spread_rank         |          38 |
| ordinary_alpha    | basis_premium_like|positioning_like   | spread_rank         |          38 |
| ordinary_alpha    | price_like                            | single              |          34 |
| ordinary_alpha    | price_like|volatility_like            | spread_rank         |          34 |
| ordinary_alpha    | volatility_like|volatility_like       | gated_sign          |          31 |
| ordinary_alpha    | volatility_like|volatility_like       | mul                 |          31 |
| ordinary_alpha    | volatility_like|volatility_like       | safe_div_abs        |          31 |
| ordinary_alpha    | volatility_like|volatility_like       | spread_rank         |          31 |
| ordinary_alpha    | volatility_like|volatility_like       | sub                 |          31 |
| ordinary_alpha    | liquidity_like|volatility_like        | mean_reversion_gate |          30 |
| ordinary_alpha    | liquidity_like|volatility_like        | signed_spread       |          30 |
| ordinary_alpha    | basis_premium_like|volatility_like    | mean_reversion_gate |          29 |
| ordinary_alpha    | liquidity_like|volatility_like        | smooth_mul          |          24 |
| ordinary_alpha    | liquidity_like|volatility_like        | spread_rank         |          24 |
| ordinary_alpha    | price_like|volatility_like            | gated_sign          |          24 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | mul                 |          21 |
| ordinary_alpha    | basis_premium_like|volatility_like    | sub                 |          21 |
| ordinary_alpha    | basis_premium_like|volatility_like    | signed_spread       |          20 |

## Reject Reason Summary

| mode              | mode_reason                            |   row_count |
|:------------------|:---------------------------------------|------------:|
| interaction_alpha | interaction_tag_not_allowed            |       12006 |
| interaction_alpha | interaction_requires_pair_or_condition |        3463 |
| interaction_alpha | no_approved_input_field                |         410 |
| ordinary_alpha    | ordinary_alpha_blocked_tag             |       12012 |
| ordinary_alpha    | no_approved_input_field                |         410 |
| rescue_lane       | rescue_requires_only_rescue_tags       |       18160 |
| rescue_lane       | no_approved_input_field                |         410 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE54 input-tag-aware queue builder contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "numeric_replay": true,
    "shadow_paper_live": true
  }
}
```
