# CRYPTO A7FF-11 SELECTED QUEUE TRIAGE

Generated: 2026-05-30T03:12:47Z

## Decision

`PASS_A7FF11_TRIAGE_READY_FOR_A7FF12_NUMERIC_WAVE_WITH_LABEL_DIVERSITY_WARNING`

A7FF-11 triages the 40 selected A7FF-10 numeric-probe rows. It does not generate formulas, execute replay, run search, or authorize alpha proof.

## Manifest

```json
{
  "authorizes_a7ff12_numeric_wave_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF11_TRIAGE_READY_FOR_A7FF12_NUMERIC_WAVE_WITH_LABEL_DIVERSITY_WARNING",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T03:12:47Z",
  "input_selected_rows": 40,
  "non_l7_selected_rows": 26,
  "priority_followup_count": 13,
  "priority_label_families": 1,
  "priority_semantic_pairs": 5,
  "rank_label_diagnostic_rows": 14,
  "source_decision": "PASS_A7FF10_COMPANY_PARALLEL_NUMERIC_AGGREGATE_BUILT",
  "source_stage": "A7FF-10-COMPANY-PARALLEL-AGGREGATE",
  "stage": "A7FF-11-SELECTED-QUEUE-TRIAGE",
  "top_semantic_pair_share": 0.35,
  "top_skeleton_share": 0.05,
  "unique_blueprints": 40,
  "uses_may": false,
  "warnings": [
    "priority_queue_label_concentrated"
  ],
  "watchlist_count": 13
}
```

## Triage Buckets

| triage_bucket                  |   count |   median_control_ratio |   median_cost10 |   median_score_no_may |
|:-------------------------------|--------:|-----------------------:|----------------:|----------------------:|
| rank_label_diagnostic_only     |      14 |               0.641134 |      0.0313835  |              37.9459  |
| priority_non_l7_control_clean  |      13 |               0.648499 |      0.124624   |             132.222   |
| watchlist_control_margin_weak  |       8 |               0.888801 |      0.12451    |             131.631   |
| watchlist_cost_or_overlap_weak |       5 |               0.968969 |     -0.00116067 |               6.03103 |

## Label / Horizon

| label_family                      |   label_horizon_h |   count |   priority_count |   median_control_ratio |   median_cost10 |
|:----------------------------------|------------------:|--------:|-----------------:|-----------------------:|----------------:|
| L5_vol_adjusted_return            |                 1 |      11 |                8 |               0.692549 |     0.0899459   |
| L5_vol_adjusted_return            |                 4 |       6 |                3 |               0.773834 |     0.241387    |
| L5_vol_adjusted_return            |                 8 |       4 |                2 |               0.809309 |     0.208502    |
| L7_ranked_future_return           |                 8 |       7 |                0 |               0.609766 |     0.0437495   |
| L0_raw_forward_return             |                 1 |       4 |                0 |               0.968969 |    -0.00116067  |
| L7_ranked_future_return           |                 1 |       4 |                0 |               0.876034 |     0.0258728   |
| L7_ranked_future_return           |                 4 |       3 |                0 |               0.562605 |     0.0398986   |
| L3_liquidity_tier_relative_return |                 1 |       1 |                0 |               0.971789 |    -0.000772623 |

## Semantic / Motif

| semantic_pair                          | motif              |   count |   priority_count |   median_control_ratio |   median_score_no_may |
|:---------------------------------------|:-------------------|--------:|-----------------:|-----------------------:|----------------------:|
| basis_premium_like\|volatility_like    | mul                |      14 |                5 |               0.757258 |             131.451   |
| basis_premium_like\|positioning_like   | gated_sign         |       7 |                3 |               0.968969 |               6.03103 |
| basis_premium_like\|price_like         | smooth_interaction |       8 |                2 |               0.54774  |              49.3061  |
| basis_premium_like\|basis_premium_like | relative_shock     |       4 |                1 |               0.809309 |             101.444   |
| basis_premium_like\|basis_premium_like | safe_div_abs       |       2 |                1 |               0.698822 |             126.952   |
| basis_premium_like                     | single             |       1 |                1 |               0.790958 |             395.457   |
| basis_premium_like\|basis_premium_like | mul                |       1 |                0 |               0.474764 |              37.8977  |
| basis_premium_like\|positioning_like   | mul                |       1 |                0 |               0.98703  |              51.5775  |
| basis_premium_like\|price_like         | relative_shock     |       1 |                0 |               0.652947 |              21.3128  |
| basis_premium_like\|price_like         | spread_rank        |       1 |                0 |               0.964187 |              33.5952  |

## Priority Follow-Up Queue

|   shard | blueprint_id            | expression                                                                                    | semantic_pair                          | motif              | label_family           |   label_horizon_h | triage_bucket                 | next_action                                     |   orientation_from_train |   premay_positive_split_count |   control_ratio_premay_max |   one_bar_lag_recent_oriented |   robust_min_tstat_floor |   cost10_recent_oriented |   score_no_may | skeleton_key          |   finite_share |   nonzero_share | is_priority_followup   |
|--------:|:------------------------|:----------------------------------------------------------------------------------------------|:---------------------------------------|:-------------------|:-----------------------|------------------:|:------------------------------|:------------------------------------------------|-------------------------:|------------------------------:|---------------------------:|------------------------------:|-------------------------:|-------------------------:|---------------:|:----------------------|---------------:|----------------:|:-----------------------|
|       0 | a7ff7e_454b18e00e63d958 | Delta(mark_index_basis_bps,12)                                                                | basis_premium_like                     | single             | L5_vol_adjusted_return |                 8 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.790958 |                     0.247474  |                  2.32574 |                0.388248  |       395.457  | skel_1d39996e97d5ace0 |       0.996265 |        0.998429 | True                   |
|       0 | a7ff7e_debf48d0ab3ed5aa | Mul(Delta(mark_index_basis_bps,12),Sign(taker_buy_sell_volume_ratio_last))                    | basis_premium_like\|positioning_like   | gated_sign         | L5_vol_adjusted_return |                 4 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.49226  |                     0.139538  |                  2.27243 |                0.272193  |       279.701  | skel_136259b72205469f |       0.996265 |        0.99806  | True                   |
|       0 | a7ff7e_303a085bd066346e | Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(taker_buy_sell_volume_ratio_last)))            | basis_premium_like\|positioning_like   | gated_sign         | L5_vol_adjusted_return |                 4 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.394847 |                     0.139179  |                  2.30347 |                0.271911  |       279.517  | skel_069f2015163fa7ef |       0.996265 |        0.998429 | True                   |
|       1 | a7ff7e_0401884a75b317df | Mul(Delta(mark_index_basis_bps,12),CSRank(realized_vol_168h))                                 | basis_premium_like\|volatility_like    | mul                | L5_vol_adjusted_return |                 4 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.666807 |                     0.133438  |                  1.59092 |                0.246653  |       253.986  | skel_136259b72205469f |       0.823901 |        0.998297 | True                   |
|       1 | a7ff7e_a88d2c050432e450 | Mul(ZScore(mark_index_basis_bps),TSRank(realized_vol_168h,24))                                | basis_premium_like\|volatility_like    | mul                | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.757258 |                     0.0433533 |                  5.52875 |                0.126968  |       134.211  | skel_e47b3d7310e98dd5 |       0.820741 |        1        | True                   |
|       1 | a7ff7e_dbde891548032719 | Mul(Clip(ZScore(mark_index_basis_bps),-3,3),TSRank(realized_vol_168h,24))                     | basis_premium_like\|volatility_like    | mul                | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.757258 |                     0.0433533 |                  5.52875 |                0.126968  |       134.211  | skel_b04640f9c6171dfc |       0.820741 |        1        | True                   |
|       1 | a7ff7e_4802e16816d12d83 | Mul(CSRank(mark_index_basis_bps),realized_vol_168h)                                           | basis_premium_like\|volatility_like    | mul                | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.401921 |                     0.0324845 |                  5.26038 |                0.124624  |       132.222  | skel_37ba6246678096b3 |       0.827348 |        1        | True                   |
|       2 | a7ff7e_cc00b6733f9dc5b8 | Mul(Delta(CSRank(mark_index_basis_bps),4),ZScore(Abs(ZScore(mark_trade_basis_bps))))          | basis_premium_like\|basis_premium_like | relative_shock     | L5_vol_adjusted_return |                 8 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.795925 |                     0.0616889 |                  1.90152 |                0.0955361 |       102.74   | skel_212ff8a4592ba496 |       0.998564 |        0.976086 | True                   |
|       1 | a7ff7e_b1c7f75458ff1db4 | Mul(CSRank(mark_index_basis_bps),CSRank(realized_vol_168h))                                   | basis_premium_like\|volatility_like    | mul                | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.425914 |                     0.0246106 |                  3.65808 |                0.0899459 |        97.52   | skel_293cae94cfd91548 |       0.827348 |        1        | True                   |
|       0 | a7ff7e_b542fd793bf96942 | Mul(Delta(mark_index_basis_bps,12),Sign(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))) | basis_premium_like\|positioning_like   | gated_sign         | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                        1 |                             3 |                   0.648499 |                     0.0280105 |                  1.95299 |                0.0799071 |        87.2586 | skel_6a3533b4d89c4d45 |       0.996265 |        0.998429 | True                   |
|       3 | a7ff7e_1f6ec704fe6f7419 | Mean(Mul(Delta(mark_index_basis_bps,1),CSRank(trade_return_1h)),4)                            | basis_premium_like\|price_like         | smooth_interaction | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.692549 |                     0.0193734 |                  2.93568 |                0.073029  |        80.3364 | skel_1128a9bc5ebfee1a |       0.997415 |        0.999886 | True                   |
|       3 | a7ff7e_18a915f55caf51fd | SafeDiv(mark_index_basis_bps,Abs(Abs(ZScore(mark_trade_basis_bps))))                          | basis_premium_like\|basis_premium_like | safe_div_abs       | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.456486 |                     0.0264879 |                  3.99506 |                0.0701239 |        77.6674 | skel_6a4becaf6b891485 |       0.999713 |        0.98741  | True                   |
|       3 | a7ff7e_17916475944c441b | Mean(Mul(Delta(mark_index_basis_bps,12),TSRank(trade_return_1h,24)),4)                        | basis_premium_like\|price_like         | smooth_interaction | L5_vol_adjusted_return |                 1 | priority_non_l7_control_clean | eligible_for_a7ff12_numeric_followup_not_search |                       -1 |                             3 |                   0.413343 |                     0.0396934 |                  2.49799 |                0.0654652 |        73.0519 | skel_8a80c8785bbf365b |       0.984487 |        0.999985 | True                   |

## Operational Interpretation

```text
The A7FF-10 selected queue has enough non-L7, control-clean numeric clues to justify a larger numeric wave.
However, the priority queue is concentrated in L5_vol_adjusted_return and basis/premium-related semantic pairs.
A7FF-12 must expand numeric probing with explicit label-family and semantic-pair diversity; this still is not formula search.
```

## Boundary

```text
May is not used.
No formula generation, replay execution, search execution, alpha proof, shadow, paper, or live execution is authorized.
A7FF-11 only authorizes drafting/running a broader numeric wave under the same non-search boundary.
```
