# Broad Core Pack information and fixed 2x2 development Arena

This is a frozen development-only comparison. It is not performance search, OOS evidence, or promotion authority.

- Source SHA: `43ee6c22a1b376d28b9790855f1cc7bc62eed80c`
- Status: `BROAD_CORE_PACK_INFORMATION_INCREMENT_ONLY`
- Data adequacy: `DATA_ADEQUACY_PASS`
- Added fields with stable residual information: 13/29
- Control fields with stable residual information: 2/10
- Information gate: True
- Economic increment gate: False

## Why entropy is not used alone

Quantile-binned H(X) is an adequacy check and approaches its maximum for nearly every non-degenerate field. The decision therefore uses block-matched mutual-information excess, residual information over the current 10-field Ridge, redundancy evidence, and fixed-model matched increments.

## Split increment summary

| split     |   gross_median |   net_median |   positive_net_ratio |
|:----------|---------------:|-------------:|---------------------:|
| selection |    3.5086e-05  | -6.77542e-05 |                    0 |
| stability |    5.17174e-06 | -8.648e-05   |                    0 |

## Boundaries

No validation/test/recent/May-stress/forward/challenge role was read. No hyperparameter search or candidate promotion occurred.
