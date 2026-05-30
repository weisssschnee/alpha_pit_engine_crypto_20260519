# CRYPTO A7FF-15 COST-TIERED BALANCED FOLLOWUP

Generated: 2026-05-30T04:29:15Z

## Decision

`PASS_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_READY_FOR_A7FF16_WITH_L3_COST_WARNING`

A7FF-15 expands the A7FF-14 balanced selector repair into a cost-tiered follow-up queue. It uses the existing A7FF-12 numeric clue surface and does not generate formulas, execute replay, run search, use May, or authorize alpha proof.

## Manifest

```json
{
  "a7ff14_selected_rows": 64,
  "authorizes_a7ff16_cost_tiered_numeric_followup": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF15_COST_TIERED_BALANCED_FOLLOWUP_READY_FOR_A7FF16_WITH_L3_COST_WARNING",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:29:15Z",
  "input_candidate_rows": 461,
  "input_unique_blueprints": 121,
  "l3_strict_cost10_rows": 0,
  "label_quota": 40,
  "min_acceptable_total": 144,
  "selected_cost5_or_better_rows": 119,
  "selected_label_families": 4,
  "selected_rows": 152,
  "selected_strict_cost10_rows": 37,
  "selected_top_label_share": 0.2631578947368421,
  "selected_top_motif_share": 0.3026315789473684,
  "selected_top_semantic_share": 0.3157894736842105,
  "selected_unique_blueprints": 96,
  "source_a7ff14_decision": "PASS_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_READY_FOR_A7FF15",
  "stage": "A7FF-15-COST-TIERED-BALANCED-FOLLOWUP",
  "target_total": 160,
  "uses_may": false,
  "warnings": [
    "L3_liquidity_tier_relative_return_has_no_strict_cost10_rows"
  ]
}
```

## Candidate Label / Cost Tier Surface

| label_family                       |   label_horizon_h | cost_tier                |   candidate_rows |   unique_blueprints |   median_control_ratio |   median_cost2 |   median_cost5 |   median_cost10 |
|:-----------------------------------|------------------:|:-------------------------|-----------------:|--------------------:|-----------------------:|---------------:|---------------:|----------------:|
| L0_raw_forward_return              |                 1 | cost2_numeric_diagnostic |               29 |                  29 |               0.613425 |    0.000365321 |   -0.000234679 |    -0.00123468  |
| L0_raw_forward_return              |                 1 | cost5_followup           |               43 |                  43 |               0.314308 |    0.00078531  |    0.00018531  |    -0.00081469  |
| L0_raw_forward_return              |                 4 | cost2_numeric_diagnostic |                7 |                   7 |               0.842552 |    0.00058102  |   -1.89795e-05 |    -0.00101898  |
| L0_raw_forward_return              |                 4 | cost5_followup           |                8 |                   8 |               0.872004 |    0.00193149  |    0.00133149  |     0.000331492 |
| L0_raw_forward_return              |                 4 | strict_cost10            |                7 |                   7 |               0.760452 |    0.00245487  |    0.00185487  |     0.000854869 |
| L0_raw_forward_return              |                 8 | cost2_numeric_diagnostic |                1 |                   1 |               0.692094 |    0.000292405 |   -0.000307595 |    -0.0013076   |
| L0_raw_forward_return              |                 8 | cost5_followup           |                2 |                   2 |               0.714983 |    0.000710292 |    0.000110292 |    -0.000889708 |
| L0_raw_forward_return              |                 8 | strict_cost10            |                1 |                   1 |               0.784453 |    0.00232959  |    0.00172959  |     0.000729595 |
| L1_cross_sectional_relative_return |                 1 | cost2_numeric_diagnostic |               32 |                  32 |               0.599108 |    0.000358118 |   -0.000241882 |    -0.00124188  |
| L1_cross_sectional_relative_return |                 1 | cost5_followup           |               43 |                  43 |               0.324917 |    0.00078531  |    0.00018531  |    -0.00081469  |
| L1_cross_sectional_relative_return |                 4 | cost2_numeric_diagnostic |               10 |                  10 |               0.878044 |    0.000523986 |   -7.60137e-05 |    -0.00107601  |
| L1_cross_sectional_relative_return |                 4 | cost5_followup           |                5 |                   5 |               0.880436 |    0.00244429  |    0.00184429  |     0.000844294 |
| L1_cross_sectional_relative_return |                 4 | strict_cost10            |               10 |                  10 |               0.763523 |    0.00245487  |    0.00185487  |     0.000854869 |
| L1_cross_sectional_relative_return |                 8 | cost2_numeric_diagnostic |                2 |                   2 |               0.985717 |    0.00250945  |    0.00190945  |     0.000909453 |
| L1_cross_sectional_relative_return |                 8 | cost5_followup           |                1 |                   1 |               0.714983 |    0.000710292 |    0.000110292 |    -0.000889708 |
| L1_cross_sectional_relative_return |                24 | cost2_numeric_diagnostic |                1 |                   1 |               0.983213 |    0.000676547 |    7.65471e-05 |    -0.000923453 |
| L3_liquidity_tier_relative_return  |                 1 | cost2_numeric_diagnostic |               36 |                  36 |               0.609194 |    0.000399394 |   -0.000200606 |    -0.00120061  |
| L3_liquidity_tier_relative_return  |                 1 | cost5_followup           |               43 |                  43 |               0.312086 |    0.000810051 |    0.000210051 |    -0.000789949 |
| L3_liquidity_tier_relative_return  |                 4 | cost2_numeric_diagnostic |               18 |                  18 |               0.91798  |    0.0023853   |    0.0017853   |     0.000785305 |
| L3_liquidity_tier_relative_return  |                 4 | cost5_followup           |                5 |                   5 |               0.803129 |    0.00122064  |    0.00062064  |    -0.00037936  |
| L3_liquidity_tier_relative_return  |                 4 | strict_cost10            |                1 |                   1 |               0.573569 |    0.00192507  |    0.00132507  |     0.00032507  |
| L3_liquidity_tier_relative_return  |                 8 | cost2_numeric_diagnostic |                1 |                   1 |               0.907722 |    0.0020776   |    0.0014776   |     0.000477598 |
| L3_liquidity_tier_relative_return  |                 8 | cost5_followup           |                2 |                   2 |               0.746102 |    0.000667088 |    6.70881e-05 |    -0.000932912 |
| L5_vol_adjusted_return             |                 1 | cost2_numeric_diagnostic |                2 |                   2 |               0.968769 |    0.0706889   |    0.0700889   |     0.0690889   |
| L5_vol_adjusted_return             |                 1 | cost5_followup           |                8 |                   8 |               0.835933 |    0.0739413   |    0.0733413   |     0.0723413   |
| L5_vol_adjusted_return             |                 1 | strict_cost10            |               73 |                  73 |               0.317327 |    0.110607    |    0.110007    |     0.109007    |
| L5_vol_adjusted_return             |                 4 | cost2_numeric_diagnostic |               10 |                  10 |               0.945387 |    0.206345    |    0.205745    |     0.204745    |
| L5_vol_adjusted_return             |                 4 | cost5_followup           |                4 |                   4 |               0.869744 |    0.273386    |    0.272786    |     0.271786    |
| L5_vol_adjusted_return             |                 4 | strict_cost10            |               25 |                  25 |               0.571003 |    0.273078    |    0.272478    |     0.271478    |
| L5_vol_adjusted_return             |                 8 | cost2_numeric_diagnostic |                1 |                   1 |               0.972648 |    0.320306    |    0.319706    |     0.318706    |
| L5_vol_adjusted_return             |                 8 | cost5_followup           |                6 |                   6 |               0.844463 |    0.266029    |    0.265429    |     0.264429    |
| L5_vol_adjusted_return             |                 8 | strict_cost10            |               22 |                  22 |               0.643013 |    0.342714    |    0.342114    |     0.341114    |
| L5_vol_adjusted_return             |                24 | cost2_numeric_diagnostic |                1 |                   1 |               0.990454 |    0.146461    |    0.145861    |     0.144861    |
| L5_vol_adjusted_return             |                24 | cost5_followup           |                1 |                   1 |               0.865845 |    0.181056    |    0.180456    |     0.179456    |

## Selected Label / Cost Tier Surface

| label_family                       |   label_horizon_h | cost_tier                |   selected_rows |   unique_blueprints |   median_control_ratio |   median_cost2 |   median_cost5 |   median_cost10 |
|:-----------------------------------|------------------:|:-------------------------|----------------:|--------------------:|-----------------------:|---------------:|---------------:|----------------:|
| L0_raw_forward_return              |                 1 | cost5_followup           |              29 |                  29 |               0.288    |    0.000789827 |    0.000189827 |    -0.000810173 |
| L0_raw_forward_return              |                 4 | cost5_followup           |               3 |                   3 |               0.86289  |    0.00245245  |    0.00185245  |     0.000852452 |
| L0_raw_forward_return              |                 4 | strict_cost10            |               7 |                   7 |               0.760452 |    0.00245487  |    0.00185487  |     0.000854869 |
| L0_raw_forward_return              |                 8 | strict_cost10            |               1 |                   1 |               0.784453 |    0.00232959  |    0.00172959  |     0.000729595 |
| L1_cross_sectional_relative_return |                 1 | cost2_numeric_diagnostic |               5 |                   5 |               0.41976  |    0.000554916 |   -4.50844e-05 |    -0.00104508  |
| L1_cross_sectional_relative_return |                 1 | cost5_followup           |              27 |                  27 |               0.332112 |    0.000744506 |    0.000144506 |    -0.000855494 |
| L1_cross_sectional_relative_return |                 4 | strict_cost10            |               7 |                   7 |               0.763523 |    0.00245487  |    0.00185487  |     0.000854869 |
| L1_cross_sectional_relative_return |                 8 | cost5_followup           |               1 |                   1 |               0.714983 |    0.000710292 |    0.000110292 |    -0.000889708 |
| L3_liquidity_tier_relative_return  |                 1 | cost2_numeric_diagnostic |              23 |                  23 |               0.527031 |    0.000453117 |   -0.000146883 |    -0.00114688  |
| L3_liquidity_tier_relative_return  |                 1 | cost5_followup           |              12 |                  12 |               0.543821 |    0.000731884 |    0.000131884 |    -0.000868116 |
| L3_liquidity_tier_relative_return  |                 4 | cost2_numeric_diagnostic |               1 |                   1 |               0.541388 |    0.000228222 |   -0.000371778 |    -0.00137178  |
| L3_liquidity_tier_relative_return  |                 4 | cost5_followup           |               3 |                   3 |               0.619237 |    0.000717404 |    0.000117404 |    -0.000882596 |
| L3_liquidity_tier_relative_return  |                 8 | cost5_followup           |               1 |                   1 |               0.790965 |    0.000667088 |    6.70881e-05 |    -0.000932912 |
| L5_vol_adjusted_return             |                 1 | cost2_numeric_diagnostic |               2 |                   2 |               0.968769 |    0.0706889   |    0.0700889   |     0.0690889   |
| L5_vol_adjusted_return             |                 1 | cost5_followup           |               5 |                   5 |               0.840804 |    0.0715486   |    0.0709486   |     0.0699486   |
| L5_vol_adjusted_return             |                 1 | strict_cost10            |              16 |                  16 |               0.551919 |    0.0795804   |    0.0789804   |     0.0779804   |
| L5_vol_adjusted_return             |                 4 | cost2_numeric_diagnostic |               2 |                   2 |               0.825701 |    0.0790046   |    0.0784046   |     0.0774046   |
| L5_vol_adjusted_return             |                 4 | strict_cost10            |               1 |                   1 |               0.762656 |    0.0983182   |    0.0977182   |     0.0967182   |
| L5_vol_adjusted_return             |                 8 | cost5_followup           |               1 |                   1 |               0.830062 |    0.184265    |    0.183665    |     0.182665    |
| L5_vol_adjusted_return             |                 8 | strict_cost10            |               5 |                   5 |               0.63639  |    0.340987    |    0.340387    |     0.339387    |

## Selected Semantic Surface

| semantic_pair                          |   selected_rows |   unique_blueprints |   median_control_ratio |
|:---------------------------------------|----------------:|--------------------:|-----------------------:|
| basis_premium_like\|positioning_like   |              48 |                  29 |               0.534209 |
| basis_premium_like\|volatility_like    |              47 |                  28 |               0.416378 |
| basis_premium_like\|basis_premium_like |              40 |                  28 |               0.58919  |
| basis_premium_like\|price_like         |              17 |                  11 |               0.683095 |

## Selected Motif Surface

| motif              |   selected_rows |   unique_blueprints |
|:-------------------|----------------:|--------------------:|
| safe_div_abs       |              46 |                  27 |
| sub                |              35 |                  20 |
| gated_sign         |              24 |                  14 |
| mul                |              22 |                  15 |
| spread_rank        |              16 |                  12 |
| smooth_interaction |               7 |                   6 |
| relative_shock     |               2 |                   2 |

## Selected Blueprint Surface

| blueprint_id            |   selected_rows |   label_families |   horizons |   best_cost_tier_rank | semantic_pair                          | motif              |
|:------------------------|----------------:|-----------------:|-----------:|----------------------:|:---------------------------------------|:-------------------|
| a7ff7e_b38081e93d4f200f |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | spread_rank        |
| a7ff7e_3f3c420268049cb3 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | spread_rank        |
| a7ff7e_77104f0e768df207 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | spread_rank        |
| a7ff7e_f93323f3cf580b67 |               2 |                2 |          2 |                     3 | basis_premium_like\|positioning_like   | mul                |
| a7ff7e_6318fc22f34b1456 |               2 |                1 |          2 |                     3 | basis_premium_like\|basis_premium_like | spread_rank        |
| a7ff7e_49154ed0f73733d8 |               2 |                2 |          2 |                     3 | basis_premium_like\|volatility_like    | mul                |
| a7ff7e_2959fcddf1a8a931 |               2 |                2 |          1 |                     3 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_5201f3314c5dae1a |               2 |                2 |          1 |                     3 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_baf8979f98b80ea5 |               2 |                2 |          1 |                     3 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_c0ec1785df986116 |               2 |                2 |          1 |                     3 | basis_premium_like\|basis_premium_like | mul                |
| a7ff7e_620758ad5441a864 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | mul                |
| a7ff7e_96c197cefcf7d2f2 |               1 |                1 |          1 |                     3 | basis_premium_like\|volatility_like    | smooth_interaction |
| a7ff7e_10e4997b8ce12a81 |               2 |                2 |          1 |                     3 | basis_premium_like\|basis_premium_like | smooth_interaction |
| a7ff7e_e6421f87ddaf0f10 |               1 |                1 |          1 |                     3 | basis_premium_like\|volatility_like    | smooth_interaction |
| a7ff7e_6dd372cacc5ae787 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | sub                |
| a7ff7e_600569f7d9453450 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | sub                |
| a7ff7e_aef81eb72a86f0cd |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | safe_div_abs       |
| a7ff7e_588389ab6a9c3f30 |               1 |                1 |          1 |                     3 | basis_premium_like\|volatility_like    | smooth_interaction |
| a7ff7e_6f14a06b714ad55d |               1 |                1 |          1 |                     3 | basis_premium_like\|volatility_like    | relative_shock     |
| a7ff7e_3a7fd6027d1b52ff |               2 |                2 |          1 |                     3 | basis_premium_like\|basis_premium_like | gated_sign         |
| a7ff7e_54b8a4f1ea2e3687 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | safe_div_abs       |
| a7ff7e_e1ed56d08d58ea65 |               1 |                1 |          1 |                     3 | basis_premium_like\|basis_premium_like | smooth_interaction |
| a7ff7e_0f6554ac44a17024 |               2 |                1 |          2 |                     3 | basis_premium_like\|basis_premium_like | sub                |
| a7ff7e_03e03bed8d34ba2e |               2 |                2 |          2 |                     3 | basis_premium_like\|basis_premium_like | sub                |
| a7ff7e_89ed25c2f6fd341b |               2 |                1 |          2 |                     3 | basis_premium_like\|basis_premium_like | sub                |
| a7ff7e_31a152b5a6d123af |               2 |                1 |          2 |                     3 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_4b24420dd5d11e83 |               2 |                2 |          2 |                     3 | basis_premium_like\|volatility_like    | gated_sign         |
| a7ff7e_5610169eff30fab5 |               2 |                1 |          2 |                     3 | basis_premium_like\|volatility_like    | gated_sign         |
| a7ff7e_81476805533d6b2f |               2 |                2 |          2 |                     3 | basis_premium_like\|volatility_like    | gated_sign         |
| a7ff7e_b0946aa9e40dd3c9 |               2 |                2 |          2 |                     3 | basis_premium_like\|basis_premium_like | gated_sign         |
| a7ff7e_b5ca9f3f6b8f16d6 |               2 |                2 |          2 |                     3 | basis_premium_like\|basis_premium_like | gated_sign         |
| a7ff7e_f2c584fa86f74c10 |               2 |                2 |          2 |                     3 | basis_premium_like\|price_like         | gated_sign         |
| a7ff7e_f484f2e1a7036ff4 |               2 |                2 |          2 |                     3 | basis_premium_like\|basis_premium_like | gated_sign         |
| a7ff7e_f8a8d6cf8b654e64 |               2 |                1 |          2 |                     3 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_3a7e3ddbe5462bea |               2 |                1 |          2 |                     3 | basis_premium_like\|price_like         | sub                |
| a7ff7e_f7464aff233896c8 |               2 |                2 |          2 |                     3 | basis_premium_like\|price_like         | sub                |
| a7ff7e_6445196984a5b167 |               2 |                1 |          2 |                     3 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_748bcf3bafd92fe7 |               1 |                1 |          1 |                     2 | basis_premium_like\|basis_premium_like | smooth_interaction |
| a7ff7e_3f00678c83674dd0 |               1 |                1 |          1 |                     2 | basis_premium_like\|basis_premium_like | mul                |
| a7ff7e_4a9c51c5031a59db |               1 |                1 |          1 |                     2 | basis_premium_like\|basis_premium_like | spread_rank        |
| a7ff7e_cf92b3fc367ac0b5 |               1 |                1 |          1 |                     2 | basis_premium_like\|volatility_like    | spread_rank        |
| a7ff7e_538b538596429abc |               1 |                1 |          1 |                     2 | basis_premium_like\|price_like         | mul                |
| a7ff7e_42b9aa89029367d2 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_bddf5c5d29f96eb6 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_77ca3b839d710afd |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | spread_rank        |
| a7ff7e_058a55fa679948ae |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_66fc9f6699584033 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | safe_div_abs       |
| a7ff7e_42cf23f63bb0ad8d |               2 |                2 |          1 |                     2 | basis_premium_like\|price_like         | mul                |
| a7ff7e_306cf26692372a73 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | sub                |
| a7ff7e_c879e0a27e94f6b7 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | sub                |
| a7ff7e_72d1bbd3a38254c0 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_af0cebc89db56866 |               2 |                2 |          1 |                     2 | basis_premium_like\|basis_premium_like | gated_sign         |
| a7ff7e_0c55e3731792d3b1 |               2 |                1 |          2 |                     2 | basis_premium_like\|price_like         | gated_sign         |
| a7ff7e_e76bd3133ec25361 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_f05cfb85e23e4866 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_175e58eb9e5404d5 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_ca3c03329ffd2edb |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | mul                |
| a7ff7e_2c50d60ccb24722c |               2 |                1 |          2 |                     2 | basis_premium_like\|volatility_like    | sub                |
| a7ff7e_878c45afac73b914 |               2 |                2 |          2 |                     2 | basis_premium_like\|price_like         | sub                |
| a7ff7e_e6d01e672425fc7c |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_18ccfc7e12a1d2ad |               1 |                1 |          1 |                     2 | basis_premium_like\|price_like         | mul                |
| a7ff7e_61b1bfe0a04f3dff |               1 |                1 |          1 |                     2 | basis_premium_like\|basis_premium_like | safe_div_abs       |
| a7ff7e_4ffa4d3edf3aac3d |               1 |                1 |          1 |                     2 | basis_premium_like\|volatility_like    | mul                |
| a7ff7e_ffdab637dbab0125 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_ae49260ddd504924 |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | mul                |
| a7ff7e_4e141259215570d3 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_0c7cd03187d0a1be |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_e0cb06581d22fb61 |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_3746e01233c26dfb |               2 |                2 |          1 |                     2 | basis_premium_like\|volatility_like    | mul                |
| a7ff7e_48b6b8b9c90e4284 |               1 |                1 |          1 |                     2 | basis_premium_like\|positioning_like   | mul                |
| a7ff7e_ddea9f3dc39ed8de |               2 |                2 |          1 |                     2 | basis_premium_like\|positioning_like   | sub                |
| a7ff7e_4245e17a292cff68 |               2 |                1 |          2 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_01654e884fbd77b8 |               2 |                1 |          2 |                     2 | basis_premium_like\|positioning_like   | spread_rank        |
| a7ff7e_6b00c1ad2539dbea |               1 |                1 |          1 |                     2 | basis_premium_like\|volatility_like    | gated_sign         |
| a7ff7e_cf79e50562e65c3a |               2 |                1 |          2 |                     2 | basis_premium_like\|positioning_like   | safe_div_abs       |
| a7ff7e_329eb175f2d1969f |               1 |                1 |          1 |                     1 | basis_premium_like\|basis_premium_like | mul                |
| a7ff7e_4a66980bed75d1d8 |               1 |                1 |          1 |                     1 | basis_premium_like\|price_like         | gated_sign         |
| a7ff7e_5426d008450afbae |               1 |                1 |          1 |                     1 | basis_premium_like\|price_like         | gated_sign         |
| a7ff7e_7821662bd6bd603d |               1 |                1 |          1 |                     1 | basis_premium_like\|price_like         | gated_sign         |
| a7ff7e_08deeb012a9bb0df |               2 |                2 |          1 |                     1 | basis_premium_like\|volatility_like    | safe_div_abs       |

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
