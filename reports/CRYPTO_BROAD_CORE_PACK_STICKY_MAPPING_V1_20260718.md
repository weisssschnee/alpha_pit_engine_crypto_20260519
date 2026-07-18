# Broad Core Pack information and fixed 2x2 development Arena

This is a frozen development-only comparison. It is not performance search, OOS evidence, or promotion authority.

- Source SHA: `7fee8559c1819a779f4a5fc22e2ee21e4d84e807`
- Status: `BROAD_CORE_PACK_INFORMATION_INCREMENT_COST_KILLED`
- Data adequacy: `DATA_ADEQUACY_PASS`
- Added fields with stable residual information: 13/29
- Control fields with stable residual information: 2/10
- Information gate: True
- Economic increment gate: False
- Cost-killed under frozen mapping: True
- Degenerate prediction/mapping pairs: 0
- Mapping repair: `PORTFOLIO_MAPPING_REPAIR_NOT_ESTABLISHED`
- Turnover-aware sticky mapping: `TURNOVER_AWARE_MAPPING_COST_REDUCTION_ONLY`

## Why entropy is not used alone

Quantile-binned H(X) is an adequacy check and approaches its maximum for nearly every non-degenerate field. The decision therefore uses block-matched mutual-information excess, residual information over the current 10-field Ridge, redundancy evidence, and fixed-model matched increments.

## Split increment summary

| split     |   gross_median |   net_median |   positive_net_ratio |
|:----------|---------------:|-------------:|---------------------:|
| selection |    3.5086e-05  | -6.77542e-05 |                    0 |
| stability |    5.17174e-06 | -8.648e-05   |                    0 |

## Mapping repair summary

| variant                               | split     |   gross_median |   net_median |   positive_net_ratio |
|:--------------------------------------|:----------|---------------:|-------------:|---------------------:|
| DIRECT_DELTA_SIGNAL_ZERO_NET          | selection |    4.76831e-05 | -3.17753e-05 |                    0 |
| HORIZON_4H_CAUSAL_MEAN_DELTA_ZERO_NET | selection |    4.12864e-05 | -1.27889e-05 |                    0 |
| DIRECT_DELTA_SIGNAL_ZERO_NET          | stability |    7.72014e-06 | -5.99934e-05 |                    0 |
| HORIZON_4H_CAUSAL_MEAN_DELTA_ZERO_NET | stability |    5.24448e-06 | -4.28393e-05 |                    0 |

## Turnover-aware sticky mapping summary

| split     |   matched_net_difference_median |   matched_positive_ratio |   delta_sleeve_net_median |   delta_sleeve_positive_ratio |   full_net_improvement_median |   control_net_improvement_median |   full_turnover_reduction_ratio_median |   control_turnover_reduction_ratio_median |
|:----------|--------------------------------:|-------------------------:|--------------------------:|------------------------------:|------------------------------:|---------------------------------:|---------------------------------------:|------------------------------------------:|
| selection |                     1.4382e-05  |                     0.75 |               1.36296e-05 |                          0.75 |                   2.33917e-05 |                      4.19588e-05 |                               0.337666 |                                  0.975108 |
| stability |                     5.27791e-06 |                     0.5  |               4.29068e-06 |                          0.5  |                   3.42081e-05 |                      4.38113e-05 |                               0.557209 |                                  0.989363 |

## Boundaries

No validation/test/recent/May-stress/forward/challenge role was read. No hyperparameter search or candidate promotion occurred.
