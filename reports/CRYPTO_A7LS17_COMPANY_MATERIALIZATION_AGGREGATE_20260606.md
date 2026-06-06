# CRYPTO A7LS-17 COMPANY MATERIALIZATION AGGREGATE

Generated: 2026-06-06T06:53:20Z

## Decision

`PASS_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_READY_FOR_A7LS18`

## Summary

- completed_shards: 100 / 100
- total_rows: 100,000
- eval_success_count: 100,000
- eval_failure_count: 0
- activity_ok_count: 75,379
- activity_ok_rate: 0.7538
- lane_count: 4
- semantic_pair_count: 125
- motif_count: 19

## Lane Summary

| a7ls_lane   |   rows |   eval_success |   activity_ok |   semantic_pairs |   motifs |   finite_share_median |   nonzero_share_median |   eval_success_rate |   activity_ok_rate |
|:------------|-------:|---------------:|--------------:|-----------------:|---------:|----------------------:|-----------------------:|--------------------:|-------------------:|
| A7LS14_A    |  32000 |          32000 |         24226 |               71 |       18 |              0.956858 |               0.999915 |                   1 |           0.757062 |
| A7LS14_B    |  32000 |          32000 |         24354 |               55 |       10 |              0.957458 |               0.999939 |                   1 |           0.761062 |
| A7LS14_C    |  24000 |          24000 |         19009 |                9 |       11 |              0.957418 |               1        |                   1 |           0.792042 |
| A7LS14_D    |  12000 |          12000 |          7790 |                7 |        6 |              0.956858 |               0.999989 |                   1 |           0.649167 |

## Top Semantic Pairs

| a7ls_lane   | semantic_pair                         |   rows |   eval_success |   activity_ok |   motifs |   activity_ok_rate |
|:------------|:--------------------------------------|-------:|---------------:|--------------:|---------:|-------------------:|
| A7LS14_A    | basis_premium_like|listing_age_like   |   3613 |           3613 |          2928 |        6 |           0.810407 |
| A7LS14_A    | basis_premium_like|liquidity_like     |   3614 |           3614 |          2851 |       11 |           0.788877 |
| A7LS14_A    | basis_premium_like|price_like         |   3614 |           3614 |          2851 |       11 |           0.788877 |
| A7LS14_A    | basis_premium_like|volatility_like    |   3614 |           3614 |          2851 |       11 |           0.788877 |
| A7LS14_A    | basis_premium_like|positioning_like   |   3613 |           3613 |          2850 |       11 |           0.788818 |
| A7LS14_A    | basis_premium_like                    |   4117 |           4117 |          2788 |       12 |           0.677192 |
| A7LS14_C    | listing_age_like|liquidity_like       |   2844 |           2844 |          2674 |        6 |           0.940225 |
| A7LS14_C    | open_interest_like|positioning_like   |   2813 |           2813 |          2579 |       11 |           0.916815 |
| A7LS14_C    | open_interest_like|taker_flow_like    |   2813 |           2813 |          2579 |       11 |           0.916815 |
| A7LS14_C    | positioning_like|taker_flow_like      |   2813 |           2813 |          2579 |       11 |           0.916815 |
| A7LS14_C    | positioning_like|basis_premium_like   |   2845 |           2845 |          2242 |       11 |           0.788049 |
| A7LS14_C    | open_interest_like|funding_state_like |   2845 |           2845 |          2197 |       11 |           0.772232 |
| A7LS14_C    | funding_state_like|basis_premium_like |   2844 |           2844 |          1892 |       11 |           0.66526  |
| A7LS14_D    | volatility_like|liquidity_like        |   1994 |           1994 |          1838 |        5 |           0.921765 |
| A7LS14_D    | placebo|price_like                    |   1893 |           1893 |          1747 |        5 |           0.922874 |
| A7LS14_D    | placebo|basis_premium_like            |   1918 |           1918 |          1504 |        5 |           0.78415  |
| A7LS14_C    | listing_age_like|basis_premium_like   |   1637 |           1637 |          1343 |        6 |           0.820403 |
| A7LS14_B    | open_interest_like                    |   1073 |           1073 |           985 |        9 |           0.917987 |
| A7LS14_D    | low_prior_axes|price_like             |   1994 |           1994 |           965 |        5 |           0.483952 |
| A7LS14_C    | open_interest_like|regime_state       |   2546 |           2546 |           924 |        6 |           0.362922 |
| A7LS14_D    | regime_state|price_like               |   1991 |           1991 |           834 |        5 |           0.418885 |
| A7LS14_D    | low_prior_axes|basis_premium_like     |   1994 |           1994 |           821 |        5 |           0.411735 |
| A7LS14_B    | taker_flow_like                       |    856 |            856 |           782 |        9 |           0.913551 |
| A7LS14_B    | funding_state_like                    |   1073 |           1073 |           766 |        9 |           0.713886 |
| A7LS14_B    | listing_age_like                      |    568 |            568 |           540 |        6 |           0.950704 |
| A7LS14_B    | open_interest_like|listing_age_like   |    569 |            569 |           537 |        6 |           0.943761 |
| A7LS14_A    | liquidity_like                        |    576 |            576 |           536 |        1 |           0.930556 |
| A7LS14_A    | positioning_like                      |    576 |            576 |           536 |        1 |           0.930556 |
| A7LS14_B    | positioning_like|listing_age_like     |    569 |            569 |           536 |        6 |           0.942004 |
| A7LS14_B    | liquidity_like|listing_age_like       |    568 |            568 |           535 |        6 |           0.941901 |

## Authorization

- A7LS18 company numeric wave: authorized only if decision is PASS
- alpha proof / shadow / paper / live: not authorized
