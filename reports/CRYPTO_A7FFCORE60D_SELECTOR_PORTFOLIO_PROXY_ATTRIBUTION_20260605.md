# CRYPTO A7FF-CORE60D SELECTOR / PORTFOLIO PROXY ATTRIBUTION

Generated: 2026-06-04T16:08:56Z

## Decision

`HOLD_CORE60D_SELECTOR_STILL_RANK_BIASED`

CORE60D audits selected queue attribution from CORE59. It does not search, replay, or promote candidates.

## Decision Record

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "selected_non_l7_lt_12",
    "selected_l7_share_gt_0_65"
  ],
  "decision": "HOLD_CORE60D_SELECTOR_STILL_RANK_BIASED",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T16:08:56Z",
  "selected_l7_share": 0.9772727272727273,
  "selected_non_l7_rows": 1,
  "selected_rows": 44,
  "selected_semantic_pair_count": 8,
  "stage": "A7FF-CORE60D",
  "top_selected_semantic_share": 0.29545454545454547
}
```

## Selected Distribution

| semantic_pair                         | label_family            | motif        |   rows |   unique_blueprints |   median_score_no_may |   median_control_ratio |   median_cost10 |   non_l7_rows |
|:--------------------------------------|:------------------------|:-------------|-------:|--------------------:|----------------------:|-----------------------:|----------------:|--------------:|
| basis_premium_like|volatility_like    | L7_ranked_future_return | spread_rank  |      6 |                   6 |               71.5197 |               0.795561 |      0.0653729  |             0 |
| basis_premium_like|price_like         | L7_ranked_future_return | mul          |      4 |                   4 |               41.778  |               0.505653 |      0.0351673  |             0 |
| basis_premium_like|price_like         | L7_ranked_future_return | spread_rank  |      4 |                   4 |               40.9201 |               0.619695 |      0.0345192  |             0 |
| basis_premium_like|price_like         | L7_ranked_future_return | smooth_mul   |      3 |                   3 |               45.6875 |               0.515508 |      0.0392031  |             0 |
| basis_premium_like|basis_premium_like | L7_ranked_future_return | smooth_mul   |      3 |                   3 |               27.1265 |               0.757668 |      0.0208841  |             0 |
| price_like                            | L7_ranked_future_return | single       |      3 |                   3 |               75.5566 |               0.254317 |      0.0688109  |             0 |
| basis_premium_like|basis_premium_like | L7_ranked_future_return | mul          |      2 |                   2 |               51.1679 |               0.457187 |      0.0446251  |             0 |
| basis_premium_like|volatility_like    | L7_ranked_future_return | smooth_mul   |      2 |                   2 |               64.4072 |               0.915885 |      0.0583231  |             0 |
| volatility_like                       | L7_ranked_future_return | single       |      2 |                   2 |               39.4607 |               0.909503 |      0.0333702  |             0 |
| basis_premium_like|basis_premium_like | L7_ranked_future_return | spread_rank  |      2 |                   2 |               26.4927 |               0.494045 |      0.0199868  |             0 |
| volatility_like|volatility_like       | L7_ranked_future_return | smooth_mul   |      2 |                   2 |               71.4981 |               0.914362 |      0.0654125  |             0 |
| basis_premium_like|price_like         | L5_vol_adjusted_return  | safe_div_abs |      1 |                   1 |               56.7963 |               0.842278 |      0.0496386  |             1 |
| basis_premium_like                    | L7_ranked_future_return | single       |      1 |                   1 |               23.6264 |               0.434986 |      0.0170614  |             0 |
| basis_premium_like|basis_premium_like | L7_ranked_future_return | sub          |      1 |                   1 |               13.3801 |               0.878864 |      0.00725894 |             0 |
| basis_premium_like|volatility_like    | L7_ranked_future_return | gated_sign   |      1 |                   1 |               45.4397 |               0.834578 |      0.0392743  |             0 |
| basis_premium_like|volatility_like    | L7_ranked_future_return | mul          |      1 |                   1 |               60.0434 |               0.877184 |      0.0539205  |             0 |
| basis_premium_like|price_like         | L7_ranked_future_return | gated_sign   |      1 |                   1 |               38.0381 |               0.5919   |      0.03163    |             0 |
| price_like|volatility_like            | L7_ranked_future_return | gated_sign   |      1 |                   1 |               37.3343 |               0.434331 |      0.0307686  |             0 |
| price_like|volatility_like            | L7_ranked_future_return | smooth_mul   |      1 |                   1 |               11.1444 |               0.840844 |      0.00498525 |             0 |
| price_like|volatility_like            | L7_ranked_future_return | mul          |      1 |                   1 |               67.1306 |               0.250131 |      0.0603808  |             0 |
| volatility_like|volatility_like       | L7_ranked_future_return | gated_sign   |      1 |                   1 |               40.2742 |               0.879498 |      0.0341537  |             0 |
| volatility_like|volatility_like       | L7_ranked_future_return | mul          |      1 |                   1 |              106.201  |               0.826419 |      0.100027   |             0 |

## L7 Pressure By Semantic Pair

| semantic_pair                         |   selected_rows |   l7_rows |   non_l7_rows |   median_score_no_may |   l7_share |
|:--------------------------------------|----------------:|----------:|--------------:|----------------------:|-----------:|
| basis_premium_like|volatility_like    |              10 |        10 |             0 |               65.0035 |   1        |
| basis_premium_like|basis_premium_like |               8 |         8 |             0 |               28.0382 |   1        |
| volatility_like|volatility_like       |               4 |         4 |             0 |               73.0668 |   1        |
| price_like                            |               3 |         3 |             0 |               75.5566 |   1        |
| price_like|volatility_like            |               3 |         3 |             0 |               37.3343 |   1        |
| volatility_like                       |               2 |         2 |             0 |               39.4607 |   1        |
| basis_premium_like                    |               1 |         1 |             0 |               23.6264 |   1        |
| basis_premium_like|price_like         |              13 |        12 |             1 |               45.6875 |   0.923077 |

## Pool vs Selected By Semantic / Motif

| semantic_pair                         | motif        |   label_rows |   unique_blueprints |   rank_label_rows |   non_l7_rows |   selected_blueprint_rows |   median_control_ratio |   median_cost10 |   selected_rate_vs_rank |   non_l7_rate_vs_selected_rows |
|:--------------------------------------|:-------------|-------------:|--------------------:|------------------:|--------------:|--------------------------:|-----------------------:|----------------:|------------------------:|-------------------------------:|
| basis_premium_like|volatility_like    | spread_rank  |         1160 |                  58 |                50 |             0 |                       120 |                9.20684 |    -0.00209864  |                2.4      |                         0      |
| basis_premium_like|price_like         | spread_rank  |         1020 |                  51 |                65 |             0 |                        80 |                4.14689 |    -0.00212464  |                1.23077  |                         0      |
| basis_premium_like|price_like         | mul          |          580 |                  29 |                43 |             1 |                        80 |                5.08929 |    -0.00177413  |                1.86047  |                         0.0125 |
| basis_premium_like|price_like         | smooth_mul   |         1420 |                  71 |                27 |             0 |                        60 |                6.24732 |    -0.00196235  |                2.22222  |                         0      |
| basis_premium_like|basis_premium_like | smooth_mul   |         1020 |                  51 |                20 |             0 |                        60 |                7.81444 |    -0.00207858  |                3        |                         0      |
| price_like                            | single       |           60 |                   3 |                 9 |             0 |                        60 |                1.34143 |    -0.00110768  |                6.66667  |                         0      |
| basis_premium_like|basis_premium_like | spread_rank  |          580 |                  29 |                14 |             0 |                        40 |                4.24928 |    -0.00162001  |                2.85714  |                         0      |
| basis_premium_like|basis_premium_like | mul          |          340 |                  17 |                 6 |             0 |                        40 |                5.62386 |    -0.00174116  |                6.66667  |                         0      |
| basis_premium_like|volatility_like    | smooth_mul   |          440 |                  22 |                 6 |             0 |                        40 |                9.9569  |    -0.0019846   |                6.66667  |                         0      |
| volatility_like                       | single       |          280 |                  14 |                 6 |             0 |                        40 |                6.67139 |    -0.00249015  |                6.66667  |                         0      |
| volatility_like|volatility_like       | smooth_mul   |          180 |                   9 |                 6 |             0 |                        40 |                7.79817 |     0.00635485  |                6.66667  |                         0      |
| basis_premium_like|price_like         | gated_sign   |          660 |                  33 |                33 |             0 |                        20 |                5.20462 |    -0.00188156  |                0.606061 |                         0      |
| price_like|volatility_like            | smooth_mul   |          280 |                  14 |                17 |             0 |                        20 |                7.70993 |    -0.00197426  |                1.17647  |                         0      |
| price_like|volatility_like            | gated_sign   |           80 |                   4 |                 8 |             0 |                        20 |                5.58538 |    -0.00209049  |                2.5      |                         0      |
| basis_premium_like|volatility_like    | gated_sign   |          720 |                  36 |                 6 |             0 |                        20 |                8.67688 |    -0.0019692   |                3.33333  |                         0      |
| basis_premium_like|basis_premium_like | sub          |          200 |                  10 |                 5 |             0 |                        20 |                3.58097 |    -0.00110383  |                4        |                         0      |
| basis_premium_like|price_like         | safe_div_abs |          420 |                  21 |                 4 |             3 |                        20 |                5.17162 |    -0.00188     |                5        |                         0.15   |
| volatility_like|volatility_like       | mul          |           20 |                   1 |                 4 |             0 |                        20 |                7.13755 |     0.00552924  |                5        |                         0      |
| basis_premium_like|volatility_like    | mul          |          700 |                  35 |                 3 |             1 |                        20 |                8.95927 |    -0.00142319  |                6.66667  |                         0.05   |
| price_like|volatility_like            | mul          |          100 |                   5 |                 3 |             0 |                        20 |                4.12506 |    -0.00164038  |                6.66667  |                         0      |
| basis_premium_like                    | single       |          720 |                  36 |                 1 |             0 |                        20 |                4.32794 |    -0.00229963  |               20        |                         0      |
| volatility_like|volatility_like       | gated_sign   |           20 |                   1 |                 1 |             0 |                        20 |                5.67208 |     0.000253033 |               20        |                         0      |
| basis_premium_like|basis_premium_like | gated_sign   |          300 |                  15 |                 2 |             0 |                         0 |                5.39555 |    -0.00189718  |                0        |                       nan      |
| basis_premium_like|basis_premium_like | safe_div_abs |          200 |                  10 |                 2 |             0 |                         0 |                4.94835 |    -0.00281338  |                0        |                       nan      |
| basis_premium_like|price_like         | sub          |          500 |                  25 |                 0 |             1 |                         0 |                6.93624 |    -0.0012031   |              nan        |                       nan      |
| basis_premium_like|volatility_like    | safe_div_abs |           60 |                   3 |                 0 |             0 |                         0 |                3.91942 |    -0.00427585  |              nan        |                       nan      |
| basis_premium_like|volatility_like    | sub          |          260 |                  13 |                 0 |             0 |                         0 |                9.18452 |    -0.00135768  |              nan        |                       nan      |
| price_like|volatility_like            | spread_rank  |          380 |                  19 |                 0 |             0 |                         0 |               10.1778  |    -0.00150548  |              nan        |                       nan      |
| price_like|volatility_like            | sub          |           20 |                   1 |                 0 |             0 |                         0 |                2.11604 |    -0.00232235  |              nan        |                       nan      |
| volatility_like|volatility_like       | safe_div_abs |           20 |                   1 |                 0 |             0 |                         0 |               44.6406  |     0.00514583  |              nan        |                       nan      |
| volatility_like|volatility_like       | spread_rank  |          180 |                   9 |                 0 |             0 |                         0 |               27.5214  |    -0.00197388  |              nan        |                       nan      |
| volatility_like|volatility_like       | sub          |           20 |                   1 |                 0 |             0 |                         0 |               60.6199  |    -0.0018278   |              nan        |                       nan      |
