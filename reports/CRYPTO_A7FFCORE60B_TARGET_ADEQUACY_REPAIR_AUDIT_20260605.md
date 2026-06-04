# CRYPTO A7FF-CORE60B TARGET ADEQUACY REPAIR AUDIT

Generated: 2026-06-04T16:08:55Z

## Decision

`HOLD_CORE60B_TARGET_ADEQUACY_REPAIR_REQUIRED`

CORE60B audits target gate behavior from CORE59 outputs. It does not relax gates, search, replay, or promote candidates.

## Decision Record

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "premay_unstable_rate_gt_0_6",
    "control_dominated_rate_gt_0_25",
    "rank_label_gap_large"
  ],
  "control_dominated_rate": 0.27017001545595054,
  "decision": "HOLD_CORE60B_TARGET_ADEQUACY_REPAIR_REQUIRED",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T16:08:55Z",
  "l7_rank_label_rows": 341,
  "label_response_rows": 12940,
  "non_l7_rows": 6,
  "non_l7_target_count": 5,
  "premay_unstable_rate": 0.6820710973724884,
  "stage": "A7FF-CORE60B"
}
```

## Label Family Summary

| label_family                       |   rows |   unique_blueprints |   premay_unstable_rows |   control_dominated_rows |   rank_label_rows |   non_l7_rows |   median_control_ratio |   median_cost10 |   cost10_positive_rate |   non_l7_share |
|:-----------------------------------|-------:|--------------------:|-----------------------:|-------------------------:|------------------:|--------------:|-----------------------:|----------------:|-----------------------:|---------------:|
| L0_raw_forward_return              |   2588 |                 647 |                   1936 |                      606 |                 0 |             2 |                8.2328  |     -0.00202359 |              0.0703246 |       0.333333 |
| L5_vol_adjusted_return             |   2588 |                 647 |                   1970 |                      568 |                 0 |             2 |                7.52597 |     -0.00653192 |              0.470247  |       0.333333 |
| L1_cross_sectional_relative_return |   2588 |                 647 |                   1936 |                      610 |                 0 |             1 |                8.18029 |     -0.00202359 |              0.0703246 |       0.166667 |
| L3_liquidity_tier_relative_return  |   2588 |                 647 |                   1898 |                      646 |                 0 |             1 |                8.98096 |     -0.0019845  |              0.0780526 |       0.166667 |
| L7_ranked_future_return            |   2588 |                 647 |                   1086 |                     1066 |               341 |             0 |                2.5273  |      0.0121469  |              0.714838  |       0        |

## Target Summary

| label_family                       |   label_horizon_h |   rows |   unique_blueprints |   premay_unstable_rows |   control_dominated_rows |   rank_label_rows |   non_l7_rows |   median_control_ratio |   median_cost10 |   cost10_positive_rate |   premay_all_positive_rate |   robust_ok_rate |   lag_ok_rate |   premay_unstable_rate |   control_dominated_rate |   non_l7_rate |
|:-----------------------------------|------------------:|-------:|--------------------:|-----------------------:|-------------------------:|------------------:|--------------:|-----------------------:|----------------:|-----------------------:|---------------------------:|-----------------:|--------------:|-----------------------:|-------------------------:|--------------:|
| L5_vol_adjusted_return             |                 1 |    647 |                 647 |                    354 |                      249 |                 0 |             2 |                3.29346 |      0.0136793  |             0.608964   |                  0.452859  |        0.452859  |      0.432767 |               0.547141 |                0.384853  |    0.00309119 |
| L0_raw_forward_return              |                 4 |    647 |                 647 |                    513 |                      125 |                 0 |             1 |                6.67281 |     -0.00212464 |             0.00309119 |                  0.20711   |        0.197836  |      0.361669 |               0.79289  |                0.193199  |    0.0015456  |
| L0_raw_forward_return              |                24 |    647 |                 647 |                    503 |                      143 |                 0 |             1 |               16.4417  |     -0.00231591 |             0.242658   |                  0.222566  |        0.236476  |      0.455951 |               0.777434 |                0.22102   |    0.0015456  |
| L1_cross_sectional_relative_return |                 1 |    647 |                 647 |                    392 |                      219 |                 0 |             1 |                3.7714  |     -0.00190376 |             0          |                  0.394127  |        0.394127  |      0.454405 |               0.605873 |                0.338485  |    0.0015456  |
| L3_liquidity_tier_relative_return  |                 1 |    647 |                 647 |                    384 |                      227 |                 0 |             1 |                3.51403 |     -0.00188643 |             0          |                  0.406491  |        0.406491  |      0.437403 |               0.593509 |                0.35085   |    0.0015456  |
| L7_ranked_future_return            |                 4 |    647 |                 647 |                    296 |                      228 |               110 |             0 |                2.21885 |      0.0109672  |             0.714065   |                  0.542504  |        0.542504  |      0.729521 |               0.457496 |                0.352396  |    0          |
| L7_ranked_future_return            |                 1 |    647 |                 647 |                    296 |                      174 |               100 |             0 |                1.79142 |      0.00778002 |             0.693972   |                  0.542504  |        0.542504  |      0.632148 |               0.457496 |                0.268934  |    0          |
| L7_ranked_future_return            |                 8 |    647 |                 647 |                    255 |                      289 |                99 |             0 |                2.18071 |      0.0137503  |             0.741886   |                  0.605873  |        0.608964  |      0.757342 |               0.394127 |                0.446677  |    0          |
| L7_ranked_future_return            |                24 |    647 |                 647 |                    239 |                      375 |                32 |             0 |                4.92415 |      0.0159069  |             0.709428   |                  0.630603  |        0.605873  |      0.709428 |               0.369397 |                0.579598  |    0          |
| L0_raw_forward_return              |                 1 |    647 |                 647 |                    392 |                      219 |                 0 |             0 |                3.62344 |     -0.00190376 |             0          |                  0.394127  |        0.394127  |      0.454405 |               0.605873 |                0.338485  |    0          |
| L0_raw_forward_return              |                 8 |    647 |                 647 |                    528 |                      119 |                 0 |             0 |               10.44    |     -0.00217447 |             0.0355487  |                  0.183926  |        0.162287  |      0.383308 |               0.816074 |                0.183926  |    0          |
| L1_cross_sectional_relative_return |                 4 |    647 |                 647 |                    513 |                      128 |                 0 |             0 |                6.67255 |     -0.00212464 |             0.00309119 |                  0.20711   |        0.197836  |      0.361669 |               0.79289  |                0.197836  |    0          |
| L1_cross_sectional_relative_return |                 8 |    647 |                 647 |                    528 |                      119 |                 0 |             0 |               10.44    |     -0.00217447 |             0.0355487  |                  0.183926  |        0.162287  |      0.383308 |               0.816074 |                0.183926  |    0          |
| L1_cross_sectional_relative_return |                24 |    647 |                 647 |                    503 |                      144 |                 0 |             0 |               16.1924  |     -0.00231591 |             0.242658   |                  0.222566  |        0.236476  |      0.455951 |               0.777434 |                0.222566  |    0          |
| L3_liquidity_tier_relative_return  |                 4 |    647 |                 647 |                    510 |                      130 |                 0 |             0 |                7.52441 |     -0.00209166 |             0.0015456  |                  0.211747  |        0.183926  |      0.349304 |               0.788253 |                0.200927  |    0          |
| L3_liquidity_tier_relative_return  |                 8 |    647 |                 647 |                    534 |                      112 |                 0 |             0 |               11.5532  |     -0.00221462 |             0.0448223  |                  0.174652  |        0.14374   |      0.412674 |               0.825348 |                0.173107  |    0          |
| L3_liquidity_tier_relative_return  |                24 |    647 |                 647 |                    470 |                      177 |                 0 |             0 |               16.0246  |     -0.00174085 |             0.265842   |                  0.27357   |        0.250386  |      0.539413 |               0.72643  |                0.27357   |    0          |
| L5_vol_adjusted_return             |                 4 |    647 |                 647 |                    503 |                      138 |                 0 |             0 |                6.16495 |     -0.0175393  |             0.431221   |                  0.222566  |        0.214838  |      0.313756 |               0.777434 |                0.213292  |    0          |
| L5_vol_adjusted_return             |                 8 |    647 |                 647 |                    526 |                      121 |                 0 |             0 |                9.25275 |     -0.0183975  |             0.431221   |                  0.187017  |        0.196291  |      0.400309 |               0.812983 |                0.187017  |    0          |
| L5_vol_adjusted_return             |                24 |    647 |                 647 |                    587 |                       60 |                 0 |             0 |               16.4176  |     -0.0626089  |             0.409583   |                  0.0927357 |        0.0896445 |      0.431221 |               0.907264 |                0.0927357 |    0          |

## Target Decision Matrix

| label_family                       |   label_horizon_h | decision_class             |   rows |
|:-----------------------------------|------------------:|:---------------------------|-------:|
| L5_vol_adjusted_return             |                24 | pre_may_unstable           |    587 |
| L3_liquidity_tier_relative_return  |                 8 | pre_may_unstable           |    534 |
| L0_raw_forward_return              |                 8 | pre_may_unstable           |    528 |
| L1_cross_sectional_relative_return |                 8 | pre_may_unstable           |    528 |
| L5_vol_adjusted_return             |                 8 | pre_may_unstable           |    526 |
| L1_cross_sectional_relative_return |                 4 | pre_may_unstable           |    513 |
| L0_raw_forward_return              |                 4 | pre_may_unstable           |    513 |
| L3_liquidity_tier_relative_return  |                 4 | pre_may_unstable           |    510 |
| L5_vol_adjusted_return             |                 4 | pre_may_unstable           |    503 |
| L1_cross_sectional_relative_return |                24 | pre_may_unstable           |    503 |
| L0_raw_forward_return              |                24 | pre_may_unstable           |    503 |
| L3_liquidity_tier_relative_return  |                24 | pre_may_unstable           |    470 |
| L1_cross_sectional_relative_return |                 1 | pre_may_unstable           |    392 |
| L0_raw_forward_return              |                 1 | pre_may_unstable           |    392 |
| L3_liquidity_tier_relative_return  |                 1 | pre_may_unstable           |    384 |
| L7_ranked_future_return            |                24 | control_dominated          |    375 |
| L5_vol_adjusted_return             |                 1 | pre_may_unstable           |    354 |
| L7_ranked_future_return            |                 1 | pre_may_unstable           |    296 |
| L7_ranked_future_return            |                 4 | pre_may_unstable           |    296 |
| L7_ranked_future_return            |                 8 | control_dominated          |    289 |
| L7_ranked_future_return            |                 8 | pre_may_unstable           |    255 |
| L5_vol_adjusted_return             |                 1 | control_dominated          |    249 |
| L7_ranked_future_return            |                24 | pre_may_unstable           |    239 |
| L7_ranked_future_return            |                 4 | control_dominated          |    228 |
| L3_liquidity_tier_relative_return  |                 1 | control_dominated          |    227 |
| L0_raw_forward_return              |                 1 | control_dominated          |    219 |
| L1_cross_sectional_relative_return |                 1 | control_dominated          |    219 |
| L3_liquidity_tier_relative_return  |                24 | control_dominated          |    177 |
| L7_ranked_future_return            |                 1 | control_dominated          |    174 |
| L1_cross_sectional_relative_return |                24 | control_dominated          |    144 |
| L0_raw_forward_return              |                24 | control_dominated          |    143 |
| L5_vol_adjusted_return             |                 4 | control_dominated          |    138 |
| L3_liquidity_tier_relative_return  |                 4 | control_dominated          |    130 |
| L1_cross_sectional_relative_return |                 4 | control_dominated          |    128 |
| L0_raw_forward_return              |                 4 | control_dominated          |    125 |
| L5_vol_adjusted_return             |                 8 | control_dominated          |    121 |
| L0_raw_forward_return              |                 8 | control_dominated          |    119 |
| L1_cross_sectional_relative_return |                 8 | control_dominated          |    119 |
| L3_liquidity_tier_relative_return  |                 8 | control_dominated          |    112 |
| L7_ranked_future_return            |                 4 | rank_label_diagnostic_clue |    110 |

## Rank vs Non-L7 Target Gap

| semantic_pair                         | label_family                       |   rank_label_rows |   non_l7_rows |   rows |   median_control_ratio |   median_cost10 |   rank_to_non_l7_gap |
|:--------------------------------------|:-----------------------------------|------------------:|--------------:|-------:|-----------------------:|----------------:|---------------------:|
| basis_premium_like|price_like         | L7_ranked_future_return            |               172 |             0 |    920 |               2.5233   |     0.0116797   |                  172 |
| basis_premium_like|volatility_like    | L7_ranked_future_return            |                65 |             0 |    668 |               2.44887  |     0.0148475   |                   65 |
| basis_premium_like|basis_premium_like | L7_ranked_future_return            |                49 |             0 |    528 |               2.21885  |     0.00450117  |                   49 |
| price_like|volatility_like            | L7_ranked_future_return            |                28 |             0 |    172 |               3.30449  |     0.0174593   |                   28 |
| volatility_like|volatility_like       | L7_ranked_future_return            |                11 |             0 |     88 |               5.512    |     0.0257325   |                   11 |
| price_like                            | L7_ranked_future_return            |                 9 |             0 |     12 |               0.372995 |     0.0473044   |                    9 |
| volatility_like                       | L7_ranked_future_return            |                 6 |             0 |     56 |               2.2848   |     0.0290975   |                    6 |
| basis_premium_like                    | L7_ranked_future_return            |                 1 |             0 |    144 |               4.03144  |     0.0134003   |                    1 |
| basis_premium_like|basis_premium_like | L3_liquidity_tier_relative_return  |                 0 |             0 |    528 |               7.58677  |    -0.00198551  |                    0 |
| basis_premium_like|basis_premium_like | L1_cross_sectional_relative_return |                 0 |             0 |    528 |               7.13691  |    -0.00199796  |                    0 |
| basis_premium_like|basis_premium_like | L0_raw_forward_return              |                 0 |             0 |    528 |               7.09238  |    -0.00199796  |                    0 |
| basis_premium_like                    | L5_vol_adjusted_return             |                 0 |             0 |    144 |               4.26553  |    -0.0213924   |                    0 |
| basis_premium_like                    | L1_cross_sectional_relative_return |                 0 |             0 |    144 |               4.3518   |    -0.00248887  |                    0 |
| basis_premium_like                    | L3_liquidity_tier_relative_return  |                 0 |             0 |    144 |               4.53539  |    -0.00224142  |                    0 |
| basis_premium_like                    | L0_raw_forward_return              |                 0 |             0 |    144 |               4.3518   |    -0.00248887  |                    0 |
| basis_premium_like|basis_premium_like | L5_vol_adjusted_return             |                 0 |             0 |    528 |               6.19289  |    -0.000774152 |                    0 |
| price_like                            | L3_liquidity_tier_relative_return  |                 0 |             0 |     12 |               6.35121  |    -0.00148177  |                    0 |
| price_like                            | L1_cross_sectional_relative_return |                 0 |             0 |     12 |               7.07607  |    -0.00145572  |                    0 |
| price_like                            | L5_vol_adjusted_return             |                 0 |             0 |     12 |              12.0873   |     0.0360756   |                    0 |
| price_like|volatility_like            | L3_liquidity_tier_relative_return  |                 0 |             0 |    172 |              10.3193   |    -0.00191975  |                    0 |
| basis_premium_like|volatility_like    | L5_vol_adjusted_return             |                 0 |             0 |    668 |               9.17996  |    -0.0235365   |                    0 |
| basis_premium_like|volatility_like    | L3_liquidity_tier_relative_return  |                 0 |             0 |    668 |              13.0325   |    -0.0021115   |                    0 |
| basis_premium_like|volatility_like    | L1_cross_sectional_relative_return |                 0 |             0 |    668 |              11.8713   |    -0.00222996  |                    0 |
| price_like                            | L0_raw_forward_return              |                 0 |             0 |     12 |               7.07607  |    -0.00145572  |                    0 |
| volatility_like                       | L1_cross_sectional_relative_return |                 0 |             0 |     56 |               8.03101  |    -0.00221121  |                    0 |
| volatility_like                       | L0_raw_forward_return              |                 0 |             0 |     56 |              10.2991   |    -0.00221121  |                    0 |
| volatility_like                       | L5_vol_adjusted_return             |                 0 |             0 |     56 |               4.60485  |    -0.0646834   |                    0 |
| volatility_like                       | L3_liquidity_tier_relative_return  |                 0 |             0 |     56 |               9.22563  |    -0.00221329  |                    0 |
| volatility_like|volatility_like       | L0_raw_forward_return              |                 0 |             0 |     88 |              16.2656   |    -0.00122995  |                    0 |
| price_like|volatility_like            | L5_vol_adjusted_return             |                 0 |             0 |    172 |               6.66689  |    -0.00475205  |                    0 |
| price_like|volatility_like            | L1_cross_sectional_relative_return |                 0 |             0 |    172 |               9.9659   |    -0.00186602  |                    0 |
| price_like|volatility_like            | L0_raw_forward_return              |                 0 |             0 |    172 |               9.9659   |    -0.00186602  |                    0 |
| volatility_like|volatility_like       | L3_liquidity_tier_relative_return  |                 0 |             0 |     88 |              17.4191   |    -0.0011361   |                    0 |
| volatility_like|volatility_like       | L1_cross_sectional_relative_return |                 0 |             0 |     88 |              16.2656   |    -0.00122995  |                    0 |
| volatility_like|volatility_like       | L5_vol_adjusted_return             |                 0 |             0 |     88 |              27.9294   |     0.0270519   |                    0 |
| basis_premium_like|price_like         | L0_raw_forward_return              |                 0 |             1 |    920 |               6.24193  |    -0.00200252  |                   -1 |
| basis_premium_like|volatility_like    | L0_raw_forward_return              |                 0 |             1 |    668 |              11.7848   |    -0.00222996  |                   -1 |
| basis_premium_like|price_like         | L1_cross_sectional_relative_return |                 0 |             1 |    920 |               6.40187  |    -0.00200252  |                   -1 |
| basis_premium_like|price_like         | L3_liquidity_tier_relative_return  |                 0 |             1 |    920 |               7.16378  |    -0.00200124  |                   -1 |
| basis_premium_like|price_like         | L5_vol_adjusted_return             |                 0 |             2 |    920 |               6.70461  |    -0.00260565  |                   -2 |
