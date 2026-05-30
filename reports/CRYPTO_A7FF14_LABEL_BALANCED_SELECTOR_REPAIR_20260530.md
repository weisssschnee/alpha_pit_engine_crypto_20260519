# CRYPTO A7FF-14 LABEL-BALANCED SELECTOR REPAIR

Generated: 2026-05-30T04:21:09Z

## Decision

`PASS_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_READY_FOR_A7FF15`

A7FF-14 repairs the A7FF selector target by dry-reranking the A7FF-12 numeric clue surface with explicit label-family quotas. It does not generate formulas, execute replay, run search, use May, or authorize alpha proof.

## Manifest

```json
{
  "authorizes_a7ff15_balanced_numeric_followup_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_rows": 461,
  "candidate_unique_blueprints": 121,
  "decision": "PASS_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_READY_FOR_A7FF15",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:21:09Z",
  "label_quota": 16,
  "motif_cap": 20,
  "selected_count": 64,
  "selected_label_families": 4,
  "selected_strict_priority_count": 25,
  "selected_top_label_share": 0.25,
  "selected_top_semantic_share": 0.3125,
  "selected_unique_blueprints": 64,
  "semantic_cap": 20,
  "skeleton_cap": 4,
  "source_a7ff13_decision": "HOLD_A7FF13_SELECTOR_LABEL_CONCENTRATION_AFTER_NUMERIC_SCALEUP",
  "stage": "A7FF-14-LABEL-BALANCED-SELECTOR-REPAIR",
  "target_total": 64,
  "uses_may": false
}
```

## Candidate Label Surface

| label_family                       |   label_horizon_h |   candidate_rows |   unique_blueprints |   strict_priority_rows |   median_control_ratio |   median_cost10 |
|:-----------------------------------|------------------:|-----------------:|--------------------:|-----------------------:|-----------------------:|----------------:|
| L0_raw_forward_return              |                 1 |               72 |                  72 |                      0 |               0.476149 |    -0.000917633 |
| L0_raw_forward_return              |                 4 |               22 |                  22 |                      7 |               0.819789 |     0.000136875 |
| L0_raw_forward_return              |                 8 |                4 |                   4 |                      1 |               0.714983 |    -0.000889708 |
| L1_cross_sectional_relative_return |                 1 |               75 |                  75 |                      0 |               0.402717 |    -0.000921427 |
| L1_cross_sectional_relative_return |                 4 |               25 |                  25 |                     10 |               0.805885 |     0.000783295 |
| L1_cross_sectional_relative_return |                 8 |                3 |                   3 |                      0 |               0.974187 |     0.000729595 |
| L1_cross_sectional_relative_return |                24 |                1 |                   1 |                      0 |               0.983213 |    -0.000923453 |
| L3_liquidity_tier_relative_return  |                 1 |               79 |                  79 |                      0 |               0.405811 |    -0.000957099 |
| L3_liquidity_tier_relative_return  |                 4 |               24 |                  24 |                      1 |               0.91798  |     0.000778103 |
| L3_liquidity_tier_relative_return  |                 8 |                3 |                   3 |                      0 |               0.790965 |    -0.000932912 |
| L5_vol_adjusted_return             |                 1 |               83 |                  83 |                     73 |               0.354593 |     0.104285    |
| L5_vol_adjusted_return             |                 4 |               39 |                  39 |                     25 |               0.729971 |     0.26243     |
| L5_vol_adjusted_return             |                 8 |               29 |                  29 |                     22 |               0.660834 |     0.339387    |
| L5_vol_adjusted_return             |                24 |                2 |                   2 |                      0 |               0.928149 |     0.162158    |

## Selected Label Surface

| label_family                       |   label_horizon_h |   selected_count |   strict_priority_count |   median_control_ratio |   median_cost10 |
|:-----------------------------------|------------------:|-----------------:|------------------------:|-----------------------:|----------------:|
| L0_raw_forward_return              |                 1 |                9 |                       0 |               0.314308 |    -0.00086165  |
| L0_raw_forward_return              |                 4 |                7 |                       7 |               0.760452 |     0.000854869 |
| L1_cross_sectional_relative_return |                 1 |                9 |                       0 |               0.318869 |    -0.000847171 |
| L1_cross_sectional_relative_return |                 4 |                7 |                       7 |               0.763523 |     0.000854869 |
| L3_liquidity_tier_relative_return  |                 1 |               16 |                       0 |               0.492572 |    -0.000981194 |
| L5_vol_adjusted_return             |                 1 |                9 |                       7 |               0.580525 |     0.0844458   |
| L5_vol_adjusted_return             |                 4 |                2 |                       0 |               0.89403  |     0.148223    |
| L5_vol_adjusted_return             |                 8 |                5 |                       4 |               0.645262 |     0.339387    |

## Selected Semantic Surface

| semantic_pair                          |   selected_count |   strict_priority_count |   median_control_ratio |
|:---------------------------------------|-----------------:|------------------------:|-----------------------:|
| basis_premium_like\|positioning_like   |               20 |                       3 |               0.489997 |
| basis_premium_like\|volatility_like    |               20 |                       6 |               0.418069 |
| basis_premium_like\|basis_premium_like |               19 |                      13 |               0.659917 |
| basis_premium_like\|price_like         |                5 |                       3 |               0.763523 |

## Selected Motif Surface

| motif              |   selected_count |
|:-------------------|-----------------:|
| safe_div_abs       |               19 |
| sub                |               16 |
| spread_rank        |                9 |
| gated_sign         |                8 |
| mul                |                8 |
| smooth_interaction |                3 |
| relative_shock     |                1 |

## Selected Queue

|   selector_rank | selector_tier               | blueprint_id            | label_family                       |   label_horizon_h | semantic_pair                          | motif              |   control_ratio_premay_max |   cost10_recent_oriented |   selector_score |
|----------------:|:----------------------------|:------------------------|:-----------------------------------|------------------:|:---------------------------------------|:-------------------|---------------------------:|-------------------------:|-----------------:|
|               1 | balanced_numeric_diagnostic | a7ff7e_42b9aa89029367d2 | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.314308 |             -0.000999724 |         12.2498  |
|               2 | balanced_numeric_diagnostic | a7ff7e_08deeb012a9bb0df | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.329077 |             -0.00104508  |         11.5201  |
|               3 | balanced_numeric_diagnostic | a7ff7e_bddf5c5d29f96eb6 | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.292022 |             -0.000810768 |         11.4561  |
|               4 | strict_priority             | a7ff7e_0f6554ac44a17024 | L0_raw_forward_return              |                 4 | basis_premium_like\|basis_premium_like | sub                |                   0.702234 |              0.000951658 |         11.1366  |
|               5 | strict_priority             | a7ff7e_89ed25c2f6fd341b | L0_raw_forward_return              |                 4 | basis_premium_like\|basis_premium_like | sub                |                   0.531153 |              0.000429428 |         11.0356  |
|               6 | balanced_numeric_diagnostic | a7ff7e_77ca3b839d710afd | L0_raw_forward_return              |                 1 | basis_premium_like\|positioning_like   | spread_rank        |                   0.233448 |             -0.000612206 |         10.9903  |
|               7 | strict_priority             | a7ff7e_03e03bed8d34ba2e | L0_raw_forward_return              |                 4 | basis_premium_like\|basis_premium_like | sub                |                   0.699088 |              0.000859444 |         10.9789  |
|               8 | strict_priority             | a7ff7e_31a152b5a6d123af | L0_raw_forward_return              |                 4 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.760452 |              0.000855378 |         10.7855  |
|               9 | strict_priority             | a7ff7e_f8a8d6cf8b654e64 | L0_raw_forward_return              |                 4 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.763523 |              0.000854869 |         10.7757  |
|              10 | strict_priority             | a7ff7e_5610169eff30fab5 | L0_raw_forward_return              |                 4 | basis_premium_like\|volatility_like    | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              11 | strict_priority             | a7ff7e_3a7e3ddbe5462bea | L0_raw_forward_return              |                 4 | basis_premium_like\|price_like         | sub                |                   0.769405 |              0.000852569 |         10.7552  |
|              12 | balanced_numeric_diagnostic | a7ff7e_66fc9f6699584033 | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.217419 |             -0.00086165  |         10.6854  |
|              13 | balanced_numeric_diagnostic | a7ff7e_46a835495a383c6e | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.41976  |             -0.00103986  |         10.5622  |
|              14 | balanced_numeric_diagnostic | a7ff7e_058a55fa679948ae | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.25252  |             -0.000873346 |         10.5037  |
|              15 | balanced_numeric_diagnostic | a7ff7e_6445196984a5b167 | L0_raw_forward_return              |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.524993 |             -0.000841548 |         10.4915  |
|              16 | balanced_numeric_diagnostic | a7ff7e_42cf23f63bb0ad8d | L0_raw_forward_return              |                 1 | basis_premium_like\|price_like         | mul                |                   0.671591 |             -0.000311241 |          9.75096 |
|              17 | strict_priority             | a7ff7e_2c50d60ccb24722c | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|volatility_like    | sub                |                   0.754509 |              0.000852452 |         10.7997  |
|              18 | strict_priority             | a7ff7e_f2c584fa86f74c10 | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|price_like         | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              19 | strict_priority             | a7ff7e_b5ca9f3f6b8f16d6 | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|basis_premium_like | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              20 | strict_priority             | a7ff7e_4b24420dd5d11e83 | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|volatility_like    | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              21 | strict_priority             | a7ff7e_f484f2e1a7036ff4 | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|basis_premium_like | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              22 | strict_priority             | a7ff7e_81476805533d6b2f | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|volatility_like    | gated_sign         |                   0.763523 |              0.000854869 |         10.7757  |
|              23 | strict_priority             | a7ff7e_f7464aff233896c8 | L1_cross_sectional_relative_return |                 4 | basis_premium_like\|price_like         | sub                |                   0.683095 |              0.000783295 |         10.4559  |
|              24 | balanced_numeric_diagnostic | a7ff7e_e76bd3133ec25361 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.255584 |             -0.000847171 |          9.55647 |
|              25 | balanced_numeric_diagnostic | a7ff7e_c879e0a27e94f6b7 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|volatility_like    | sub                |                   0.289387 |             -0.00083279  |          9.55033 |
|              26 | balanced_numeric_diagnostic | a7ff7e_72d1bbd3a38254c0 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.300784 |             -0.000960129 |          9.54541 |
|              27 | balanced_numeric_diagnostic | a7ff7e_175e58eb9e5404d5 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.256053 |             -0.000891111 |          9.45341 |
|              28 | balanced_numeric_diagnostic | a7ff7e_f05cfb85e23e4866 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.318869 |             -0.000831548 |          9.44252 |
|              29 | balanced_numeric_diagnostic | a7ff7e_5b5909ab9ba6fc5e | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|positioning_like   | spread_rank        |                   0.504701 |             -0.00104184  |          9.33818 |
|              30 | balanced_numeric_diagnostic | a7ff7e_ca3c03329ffd2edb | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|volatility_like    | mul                |                   0.725003 |             -0.000627961 |          9.32649 |
|              31 | balanced_numeric_diagnostic | a7ff7e_306cf26692372a73 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|volatility_like    | sub                |                   0.543022 |             -0.000810293 |          8.82985 |
|              32 | balanced_numeric_diagnostic | a7ff7e_ae49260ddd504924 | L1_cross_sectional_relative_return |                 1 | basis_premium_like\|volatility_like    | mul                |                   0.332112 |             -0.000906179 |          8.80128 |
|              33 | balanced_numeric_diagnostic | a7ff7e_2959fcddf1a8a931 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.327679 |             -0.000789949 |         12.5515  |
|              34 | balanced_numeric_diagnostic | a7ff7e_5201f3314c5dae1a | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.329307 |             -0.000802188 |         11.9649  |
|              35 | balanced_numeric_diagnostic | a7ff7e_4346ffb98ebf72fd | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | relative_shock     |                   0.230605 |             -0.00109987  |          9.07069 |
|              36 | balanced_numeric_diagnostic | a7ff7e_e6d01e672425fc7c | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.612349 |             -0.000787184 |          8.96596 |
|              37 | balanced_numeric_diagnostic | a7ff7e_0ebc522cfac9064b | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|basis_premium_like | safe_div_abs       |                   0.509851 |             -0.00123724  |          8.94956 |
|              38 | balanced_numeric_diagnostic | a7ff7e_ffdab637dbab0125 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.475293 |             -0.00096095  |          8.91788 |
|              39 | balanced_numeric_diagnostic | a7ff7e_f93323f3cf580b67 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | mul                |                   0.213061 |             -0.00109722  |          8.88088 |
|              40 | balanced_numeric_diagnostic | a7ff7e_ad5a4558bb28c147 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.405811 |             -0.001189    |          8.68045 |
|              41 | balanced_numeric_diagnostic | a7ff7e_6b5025690f81f80e | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|basis_premium_like | spread_rank        |                   0.863844 |             -0.00100525  |          8.67696 |
|              42 | balanced_numeric_diagnostic | a7ff7e_3a7fd6027d1b52ff | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|basis_premium_like | gated_sign         |                   0.336181 |             -0.00146105  |          8.6734  |
|              43 | balanced_numeric_diagnostic | a7ff7e_4e141259215570d3 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.801237 |             -0.000678327 |          8.64625 |
|              44 | balanced_numeric_diagnostic | a7ff7e_7ce3fc081e418e79 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.462849 |             -0.00100144  |          8.49534 |
|              45 | balanced_numeric_diagnostic | a7ff7e_0c7cd03187d0a1be | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.698038 |             -0.000865344 |          8.25212 |
|              46 | balanced_numeric_diagnostic | a7ff7e_e0cb06581d22fb61 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | sub                |                   0.710652 |             -0.000870888 |          8.20048 |
|              47 | balanced_numeric_diagnostic | a7ff7e_4fed0431f792f0c8 | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|positioning_like   | spread_rank        |                   0.722734 |             -0.00105532  |          8.18325 |
|              48 | balanced_numeric_diagnostic | a7ff7e_3746e01233c26dfb | L3_liquidity_tier_relative_return  |                 1 | basis_premium_like\|volatility_like    | mul                |                   0.785114 |             -0.000804183 |          8.02038 |
|              49 | strict_priority             | a7ff7e_b38081e93d4f200f | L5_vol_adjusted_return             |                 8 | basis_premium_like\|basis_premium_like | spread_rank        |                   0.428738 |              0.339387    |        434.705   |
|              50 | strict_priority             | a7ff7e_3f3c420268049cb3 | L5_vol_adjusted_return             |                 8 | basis_premium_like\|basis_premium_like | spread_rank        |                   0.597855 |              0.339387    |        434.198   |
|              51 | strict_priority             | a7ff7e_77104f0e768df207 | L5_vol_adjusted_return             |                 8 | basis_premium_like\|basis_premium_like | spread_rank        |                   0.659917 |              0.339387    |        434.012   |
|              52 | balanced_numeric_diagnostic | a7ff7e_a5d58d0a148c1372 | L5_vol_adjusted_return             |                 4 | basis_premium_like\|positioning_like   | safe_div_abs       |                   0.997919 |              0.217814    |        278.592   |
|              53 | strict_priority             | a7ff7e_01654e884fbd77b8 | L5_vol_adjusted_return             |                 8 | basis_premium_like\|positioning_like   | spread_rank        |                   0.645262 |              0.208326    |        269.318   |
|              54 | balanced_numeric_diagnostic | a7ff7e_6318fc22f34b1456 | L5_vol_adjusted_return             |                 8 | basis_premium_like\|basis_premium_like | spread_rank        |                   0.830062 |              0.182665    |        235.642   |
|              55 | strict_priority             | a7ff7e_baf8979f98b80ea5 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|volatility_like    | safe_div_abs       |                   0.416378 |              0.110277    |        151.141   |
|              56 | strict_priority             | a7ff7e_c0ec1785df986116 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | mul                |                   0.356331 |              0.0923476   |        127.576   |
|              57 | balanced_numeric_diagnostic | a7ff7e_329eb175f2d1969f | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | mul                |                   0.98345  |              0.0950186   |        126.54    |
|              58 | strict_priority             | a7ff7e_620758ad5441a864 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | mul                |                   0.748871 |              0.0884325   |        122.135   |
|              59 | strict_priority             | a7ff7e_96c197cefcf7d2f2 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|volatility_like    | smooth_interaction |                   0.466522 |              0.0844458   |        116.121   |
|              60 | strict_priority             | a7ff7e_10e4997b8ce12a81 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | smooth_interaction |                   0.580525 |              0.0805575   |        110.795   |
|              61 | balanced_numeric_diagnostic | a7ff7e_748bcf3bafd92fe7 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | smooth_interaction |                   0.842577 |              0.0799607   |        107.507   |
|              62 | strict_priority             | a7ff7e_6dd372cacc5ae787 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | sub                |                   0.559107 |              0.0769403   |        106.799   |
|              63 | balanced_numeric_diagnostic | a7ff7e_4a66980bed75d1d8 | L5_vol_adjusted_return             |                 4 | basis_premium_like\|price_like         | gated_sign         |                   0.79014  |              0.0786319   |        103.519   |
|              64 | strict_priority             | a7ff7e_600569f7d9453450 | L5_vol_adjusted_return             |                 1 | basis_premium_like\|basis_premium_like | sub                |                   0.632298 |              0.0731717   |        101.549   |

## Boundary

```text
No May is used.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-14 only authorizes a follow-up balanced numeric diagnostic contract.
```
