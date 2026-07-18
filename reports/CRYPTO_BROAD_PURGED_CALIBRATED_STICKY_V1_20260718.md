# Broad Core Pack purged model-fit / calibration development Arena

This is a frozen development-only comparison. It is not performance search, OOS evidence, or promotion authority.

- Source SHA: `35546635450cba974457e90c0b0a3d0257689cd4`
- Status: `BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED`
- Data adequacy: `DATA_ADEQUACY_PASS`
- Added fields with stable residual information: 12/29
- Control fields with stable residual information: 1/10
- Information gate: True
- Economic increment gate: False
- Cost-killed under frozen mapping: False
- Degenerate prediction/mapping pairs: 0
- Mapping repair: `PORTFOLIO_MAPPING_REPAIR_NOT_ESTABLISHED`
- Turnover-aware sticky mapping: `TURNOVER_AWARE_MAPPING_COST_REDUCTION_ONLY`
- Train-only calibrated sticky mapping: `TURNOVER_AWARE_MAPPING_COST_REDUCTION_ONLY`
- Calibration-fit degenerate arms: 1 (retained as gate failures)
- Bias audit: `PASS`

## Why entropy is not used alone

Quantile-binned H(X) is an adequacy check and approaches its maximum for nearly every non-degenerate field. The decision therefore uses block-matched mutual-information excess, residual information over the current 10-field Ridge, redundancy evidence, and fixed-model matched increments.

## Split increment summary

| split     |   gross_median |   net_median |   positive_net_ratio |
|:----------|---------------:|-------------:|---------------------:|
| selection |    1.44838e-05 | -0.00010241  |                    0 |
| stability |   -6.30296e-06 | -0.000121709 |                    0 |

## Mapping repair summary

| variant                               | split     |   gross_median |   net_median |   positive_net_ratio |
|:--------------------------------------|:----------|---------------:|-------------:|---------------------:|
| DIRECT_DELTA_SIGNAL_ZERO_NET          | selection |    1.62079e-05 | -8.25721e-05 |                    0 |
| HORIZON_4H_CAUSAL_MEAN_DELTA_ZERO_NET | selection |    9.07206e-06 | -5.90419e-05 |                    0 |
| DIRECT_DELTA_SIGNAL_ZERO_NET          | stability |    7.61722e-06 | -8.0305e-05  |                    0 |
| HORIZON_4H_CAUSAL_MEAN_DELTA_ZERO_NET | stability |    6.39535e-06 | -4.63187e-05 |                    0 |

## Turnover-aware sticky mapping summary

| split     |   arm_count |   degenerate_pair_count |   matched_net_difference_median |   matched_positive_ratio |   delta_sleeve_net_median |   delta_sleeve_positive_ratio |   full_net_improvement_median |   control_net_improvement_median |   full_turnover_reduction_ratio_median |   control_turnover_reduction_ratio_median |
|:----------|------------:|------------------------:|--------------------------------:|-------------------------:|--------------------------:|------------------------------:|------------------------------:|---------------------------------:|---------------------------------------:|------------------------------------------:|
| selection |           4 |                       0 |                    -5.96958e-05 |                     0.25 |              -6.24826e-05 |                          0.25 |                   3.51289e-05 |                      6.26317e-05 |                               0.291948 |                                  0.970055 |
| stability |           4 |                       0 |                    -9.02044e-06 |                     0    |              -1.02631e-05 |                          0    |                   4.16769e-05 |                      2.70184e-05 |                               0.506714 |                                  0.987545 |

## Train-only calibrated sticky summary

| split     |   arm_count |   degenerate_pair_count |   matched_net_difference_median |   matched_positive_ratio |   delta_sleeve_net_median |   delta_sleeve_positive_ratio |   full_net_improvement_median |   control_net_improvement_median |   full_turnover_reduction_ratio_median |   control_turnover_reduction_ratio_median |
|:----------|------------:|------------------------:|--------------------------------:|-------------------------:|--------------------------:|------------------------------:|------------------------------:|---------------------------------:|---------------------------------------:|------------------------------------------:|
| selection |           4 |                       1 |                     6.39729e-06 |                     0.25 |               5.71142e-06 |                          0.25 |                   4.46976e-05 |                     -1.76139e-05 |                                      1 |                                  0.729396 |
| stability |           4 |                       1 |                     0           |                     0    |               0           |                          0    |                   2.39827e-05 |                      5.0417e-06  |                                      1 |                                  0.903976 |

## Boundary repair

The former train role is split once into model-fit (2023-07 through 2023-12) and held-out calibration (2024-01 through 2024-02). Every model-fit, calibration, selection, and stability block purges its final 6 hours, equal to the 2h execution delay plus 4h target horizon. Prior unpurged prediction identities are retained only as superseded evidence.

Ridge plus three MLP seeds are robustness arms, not independent samples. Selection and stability are already-spent development evidence; hourly LCBs are descriptive because 4h labels overlap and returns are serially dependent.

## Boundaries

No validation/test/recent/May-stress/forward/challenge role was read. No hyperparameter search or candidate promotion occurred.
