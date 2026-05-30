# CRYPTO A7FF-26 NUMERIC CLUE FORENSIC

Generated: 2026-05-30T09:07:19Z

## Decision

`PASS_A7FF26_NUMERIC_RESEARCH_CLUES_READY_FOR_REPLAY_PREFLIGHT_NO_SEARCH_AUTH`

A7FF-26 triages the A7FF-25R3 selected numeric queue. It does not generate, replay, search, or prove alpha. It may authorize a replay-preflight stage for promotion-ready numeric research clues.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_replay_preflight": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF26_NUMERIC_RESEARCH_CLUES_READY_FOR_REPLAY_PREFLIGHT_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:07:19Z",
  "non_l7_selected_count": 25,
  "prior_decision": "PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_WITH_WARNINGS_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-25R3",
  "promotion_ready_count": 14,
  "promotion_semantic_pair_count": 5,
  "promotion_skeleton_count": 8,
  "promotion_thresholds": {
    "control_ratio_premay_max_lt": 0.8,
    "cost10_recent_oriented_gt": 0.0,
    "label_family_not": "L7_ranked_future_return",
    "one_bar_lag_recent_oriented_gt": 0.0,
    "premay_all_positive": true,
    "robust_min_tstat_floor_gte": 1.5
  },
  "rank_label_diagnostic_count": 46,
  "selected_input_count": 71,
  "stage": "A7FF-26",
  "uses_may": false,
  "warnings": [
    "rank_label_diagnostic_selected_majority"
  ]
}
```

## Promotion Candidate Queue

|   shard | blueprint_id             | expression                                                            | semantic_pair                         | motif        | skeleton_key          | label_family           |   label_horizon_h | decision                 | triage_status                         |   control_ratio_premay_max |   one_bar_lag_recent_oriented |   robust_min_tstat_floor |   cost10_recent_oriented |   score_no_may |   finite_share |   nonzero_share |
|--------:|:-------------------------|:----------------------------------------------------------------------|:--------------------------------------|:-------------|:----------------------|:-----------------------|------------------:|:-------------------------|:--------------------------------------|---------------------------:|------------------------------:|-------------------------:|-------------------------:|---------------:|---------------:|----------------:|
|       0 | a7ff24r_858ff2210f276fcf | Delta(mark_index_basis_bps,12)                                        | basis_premium_like                    | single       | skel_1d39996e97d5ace0 | L5_vol_adjusted_return |                 8 | A7FF25R3S00_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.664665 |                     0.247474  |                  2.32574 |                0.388248  |       395.583  |       0.996265 |        0.998429 |
|       4 | a7ff24r_650915032f2a5979 | Mul(Delta(mark_index_basis_bps,12),Sign(realized_vol_24h))            | basis_premium_like|volatility_like    | gated_sign   | skel_136259b72205469f | L5_vol_adjusted_return |                 8 | A7FF25R3S04_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.777635 |                     0.247474  |                  2.32574 |                0.388248  |       395.47   |       0.823901 |        0.998297 |
|       5 | a7ff24r_389e925b81a0c645 | Mean(Mul(Delta(mark_index_basis_bps,1),realized_vol_168h),4)          | basis_premium_like|volatility_like    | smooth_mul   | skel_8184698cb7b24c02 | L5_vol_adjusted_return |                 8 | A7FF25R3S05_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.552241 |                     0.11202   |                  2.51434 |                0.191482  |       198.93   |       0.826199 |        0.99983  |
|       2 | a7ff24r_bcc3435cf539d883 | Sub(mark_index_basis_bps,Mean(premium_close_bps,12))                  | basis_premium_like|basis_premium_like | sub          | skel_f8484b844efd270f | L5_vol_adjusted_return |                 1 | A7FF25R3S02_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.193843 |                     0.0416174 |                  7.11992 |                0.151206  |       159.012  |       0.996553 |        0.999111 |
|       0 | a7ff24r_145e2d58adad4f4a | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,12)))) | basis_premium_like|basis_premium_like | safe_div_abs | skel_c80f62c274b367a9 | L5_vol_adjusted_return |                 4 | A7FF25R3S00_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.78766  |                     0.0448436 |                  2.27988 |                0.135293  |       142.506  |       0.996553 |        0.987385 |
|       0 | a7ff24r_8d906801b8dec4c0 | Mul(mark_index_basis_bps,Mean(premium_close_bps,2))                   | basis_premium_like|basis_premium_like | mul          | skel_f8484b844efd270f | L5_vol_adjusted_return |                 1 | A7FF25R3S00_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.600993 |                     0.0296296 |                  4.12286 |                0.111928  |       119.327  |       0.999425 |        0.811898 |
|       5 | a7ff24r_62921caa01dbd001 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,12)))) | basis_premium_like|volatility_like    | safe_div_abs | skel_c80f62c274b367a9 | L5_vol_adjusted_return |                 1 | A7FF25R3S05_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.316995 |                     0.0249224 |                  4.59621 |                0.0922978 |        99.9808 |       0.824188 |        0.987078 |
|       1 | a7ff24r_09dc2d7e51641cb0 | Sub(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | sub          | skel_0994b3a36a4d53ba | L5_vol_adjusted_return |                 1 | A7FF25R3S01_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.590707 |                     0.0271568 |                  4.24674 |                0.0840884 |        91.4977 |       0.997415 |        0.997849 |
|       5 | a7ff24r_c223ee324263786f | SafeDiv(premium_close_bps,Abs(realized_vol_168h))                     | basis_premium_like|volatility_like    | safe_div_abs | skel_d9d4f69744bac825 | L5_vol_adjusted_return |                 1 | A7FF25R3S05_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.674115 |                     0.039465  |                  2.53115 |                0.0841199 |        91.4458 |       0.827348 |        0.672833 |
|       3 | a7ff24r_b74c05b6f58309a0 | SafeDiv(premium_close_bps,Abs(ZScore(Mean(trade_return_1h,12))))      | basis_premium_like|price_like         | safe_div_abs | skel_c80f62c274b367a9 | L5_vol_adjusted_return |                 1 | A7FF25R3S03_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.50332  |                     0.0563378 |                  1.67993 |                0.0799569 |        87.4536 |       0.993105 |        0.663907 |
|       1 | a7ff24r_14bb4d389b4b94f0 | Sub(ZScore(Mean(mark_index_basis_bps,8)),premium_close_bps)           | basis_premium_like|basis_premium_like | sub          | skel_97ea9710bb50e137 | L5_vol_adjusted_return |                 1 | A7FF25R3S01_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.798537 |                     0.0258773 |                  3.71359 |                0.0786787 |        85.8802 |       0.997702 |        1        |
|       2 | a7ff24r_809e5867ebe18c47 | SafeDiv(premium_close_bps,Abs(ZScore(Mean(trade_return_1h,8))))       | basis_premium_like|price_like         | safe_div_abs | skel_c80f62c274b367a9 | L5_vol_adjusted_return |                 1 | A7FF25R3S02_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.764264 |                     0.0409409 |                  1.69292 |                0.0681169 |        75.3526 |       0.995404 |        0.663952 |
|       0 | a7ff24r_f695d065dec8c1ad | Mul(Delta(mark_index_basis_bps,8),premium_close_bps)                  | basis_premium_like|basis_premium_like | mul          | skel_0994b3a36a4d53ba | L5_vol_adjusted_return |                 1 | A7FF25R3S00_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.643964 |                     0.0153525 |                  2.28389 |                0.0414972 |        48.8533 |       0.997415 |        0.663888 |
|       6 | a7ff24r_4f5fad181e850eac | Mul(realized_vol_168h,Sign(ZScore(Mean(trade_return_1h,2))))          | price_like|volatility_like            | gated_sign   | skel_c80f62c274b367a9 | L5_vol_adjusted_return |                 1 | A7FF25R3S06_NUMERIC_CLUE | promotion_ready_numeric_research_clue |                   0.733619 |                     0.0105909 |                  1.99126 |                0.0382802 |        45.5466 |       0.827061 |        1        |

## Control Risk Summary

| triage_status                         |   rows |   control_ratio_median |   control_ratio_max |   robust_min_tstat_median |   cost10_median |   score_median |
|:--------------------------------------|-------:|-----------------------:|--------------------:|--------------------------:|----------------:|---------------:|
| rank_label_diagnostic_only            |     46 |               0.76143  |            0.998945 |                   1.64159 |       0.0430028 |        49.4961 |
| promotion_ready_numeric_research_clue |     14 |               0.654315 |            0.798537 |                   2.42004 |       0.0882089 |        95.7392 |
| watchlist_control_margin_thin         |      8 |               0.910439 |            0.995829 |                   1.9378  |       0.106245  |       113.359  |
| watchlist_robustness_thin             |      3 |               0.474289 |            0.75357  |                   1.48338 |       0.103658  |       111.217  |

## Label Triage Summary

| label_family            | triage_status                         |   count |
|:------------------------|:--------------------------------------|--------:|
| L5_vol_adjusted_return  | promotion_ready_numeric_research_clue |      14 |
| L5_vol_adjusted_return  | watchlist_control_margin_thin         |       8 |
| L5_vol_adjusted_return  | watchlist_robustness_thin             |       3 |
| L7_ranked_future_return | rank_label_diagnostic_only            |      46 |

## Family Label Summary

| triage_status                         | semantic_pair                         | motif        | label_family            |   count |
|:--------------------------------------|:--------------------------------------|:-------------|:------------------------|--------:|
| promotion_ready_numeric_research_clue | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return  |       3 |
| promotion_ready_numeric_research_clue | basis_premium_like|basis_premium_like | mul          | L5_vol_adjusted_return  |       2 |
| promotion_ready_numeric_research_clue | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return  |       2 |
| promotion_ready_numeric_research_clue | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return  |       2 |
| promotion_ready_numeric_research_clue | basis_premium_like                    | single       | L5_vol_adjusted_return  |       1 |
| promotion_ready_numeric_research_clue | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return  |       1 |
| promotion_ready_numeric_research_clue | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return  |       1 |
| promotion_ready_numeric_research_clue | basis_premium_like|volatility_like    | smooth_mul   | L5_vol_adjusted_return  |       1 |
| promotion_ready_numeric_research_clue | price_like|volatility_like            | gated_sign   | L5_vol_adjusted_return  |       1 |
| rank_label_diagnostic_only            | basis_premium_like|price_like         | spread_rank  | L7_ranked_future_return |       7 |
| rank_label_diagnostic_only            | price_like|volatility_like            | smooth_mul   | L7_ranked_future_return |       6 |
| rank_label_diagnostic_only            | basis_premium_like|basis_premium_like | spread_rank  | L7_ranked_future_return |       5 |
| rank_label_diagnostic_only            | basis_premium_like|price_like         | smooth_mul   | L7_ranked_future_return |       5 |
| rank_label_diagnostic_only            | basis_premium_like|volatility_like    | spread_rank  | L7_ranked_future_return |       5 |
| rank_label_diagnostic_only            | basis_premium_like|basis_premium_like | smooth_mul   | L7_ranked_future_return |       3 |
| rank_label_diagnostic_only            | basis_premium_like|volatility_like    | smooth_mul   | L7_ranked_future_return |       3 |
| rank_label_diagnostic_only            | price_like                            | single       | L7_ranked_future_return |       3 |
| rank_label_diagnostic_only            | volatility_like|volatility_like       | smooth_mul   | L7_ranked_future_return |       2 |
| rank_label_diagnostic_only            | basis_premium_like|price_like         | gated_sign   | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | basis_premium_like|price_like         | mul          | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | basis_premium_like|volatility_like    | gated_sign   | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | basis_premium_like|volatility_like    | mul          | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | volatility_like                       | single       | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | volatility_like|volatility_like       | gated_sign   | L7_ranked_future_return |       1 |
| rank_label_diagnostic_only            | volatility_like|volatility_like       | mul          | L7_ranked_future_return |       1 |
| watchlist_control_margin_thin         | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return  |       2 |
| watchlist_control_margin_thin         | basis_premium_like|basis_premium_like | gated_sign   | L5_vol_adjusted_return  |       1 |
| watchlist_control_margin_thin         | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return  |       1 |
| watchlist_control_margin_thin         | basis_premium_like|price_like         | mul          | L5_vol_adjusted_return  |       1 |
| watchlist_control_margin_thin         | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return  |       1 |
| watchlist_control_margin_thin         | price_like|volatility_like            | gated_sign   | L5_vol_adjusted_return  |       1 |
| watchlist_control_margin_thin         | price_like|volatility_like            | mul          | L5_vol_adjusted_return  |       1 |
| watchlist_robustness_thin             | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return  |       1 |
| watchlist_robustness_thin             | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return  |       1 |
| watchlist_robustness_thin             | price_like                            | single       | L5_vol_adjusted_return  |       1 |

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
L7 ranked-return rows are diagnostic-only.
This stage authorizes at most A7FF-27 replay preflight on promotion-ready numeric research clues.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
