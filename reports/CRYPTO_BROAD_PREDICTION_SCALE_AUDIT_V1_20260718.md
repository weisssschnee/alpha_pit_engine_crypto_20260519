# Broad prediction-scale audit

This is a diagnostic over committed frozen predictions and sticky-mapping evidence. It does not retrain, tune, or open sealed roles.

- Status: `PREDICTION_SCALE_CALIBRATION_RISK_CONFIRMED`
- All-surface scale vs acceptance Spearman: `0.975`
- All-surface scale vs turnover Spearman: `0.973`
- All-surface scale vs net Spearman: `-0.125`
- Full-surface scale vs net Spearman: `-0.619`
- Full MLP acceptance range: `0.719`

Prediction amplitude almost determines whether the fixed cost gate trades, but it does not predict better net outcomes. The sticky result is therefore scale-sensitive and cannot justify threshold tuning or a component increment claim.

## Scope correlations

| scope    |   observations |   scale_vs_acceptance |   scale_vs_turnover |   scale_vs_net |   scale_vs_pearson |   scale_vs_spearman |
|:---------|---------------:|----------------------:|--------------------:|---------------:|-------------------:|--------------------:|
| all      |             16 |              0.974964 |            0.972774 |      -0.125092 |          -0.744118 |           -0.314706 |
| full     |              8 |              0.97619  |            0.97619  |      -0.619048 |          -0.47619  |           -0.47619  |
| control  |              8 |              0.963925 |            0.946125 |      -0.514979 |          -0.190476 |            0.5      |
| full_mlp |              6 |              0.942857 |            0.942857 |      -0.257143 |          -0.542857 |           -0.2      |

## Boundaries

No model was trained. No threshold was changed. No validation, test, recent, May-stress, forward, or challenge role was read.
