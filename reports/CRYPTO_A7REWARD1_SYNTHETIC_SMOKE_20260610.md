# CRYPTO A7REWARD1 Synthetic Reward Smoke

Generated: 2026-06-10T10:35:53Z

## Decision

`PASS_A7REWARD1_SYNTHETIC_SMOKE`

## Synthetic Smoke Leaderboard

| blueprint_id            | semantic_pair   | motif   | skeleton_key            | expression              |   horizon_h |   overall_reward |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   stress_sortino |   recent_sharpe |   recent_ic |   recent_rankic |   recent_net_mean |   recent_max_drawdown |   recent_avg_turnover |   recent_capacity_proxy |   recent_control_ratio |   recent_shuffle_control_ratio |   oos_positive_split_count | hard_reject   | hard_reject_reasons                                                                        | smoke_pass_expected   |
|:------------------------|:----------------|:--------|:------------------------|:------------------------|------------:|-----------------:|----------------:|---------------------:|---------------:|-----------------:|-----------------:|----------------:|------------:|----------------:|------------------:|----------------------:|----------------------:|------------------------:|-----------------------:|-------------------------------:|---------------------------:|:--------------|:-------------------------------------------------------------------------------------------|:----------------------|
| synthetic_true_positive | synthetic       | smoke   | synthetic_true_positive | synthetic_true_positive |          24 |         41.9371  |        59.928   |             81.8499  |       93.9834  |         67.919   |              nan |        26.5382  |  0.194962   |      0.191504   |       0.00195129  |           -0.00197588 |              0.668495 |                  219708 |                1.34259 |                       0.190546 |                          3 | False         |                                                                                            | True                  |
| synthetic_sign_flip     | synthetic       | smoke   | synthetic_sign_flip     | synthetic_sign_flip     |          24 |         41.9371  |        59.928   |             81.8499  |       93.9834  |         67.919   |              nan |        26.5382  |  0.194962   |      0.191504   |       0.00195129  |           -0.00197588 |              0.668495 |                  219708 |                1.34259 |                       0.207112 |                          3 | False         |                                                                                            | False                 |
| synthetic_shuffle_noise | synthetic       | smoke   | synthetic_shuffle_noise | synthetic_shuffle_noise |          24 |         -3.85782 |        -5.37741 |             -6.11401 |       -5.99695 |         -5.24687 |              nan |        -4.45622 |  0.00324438 |      0.00393429 |      -0.000287286 |           -0.0675048  |              0.664286 |                  214530 |                1.43405 |                       1.43405  |                          0 | True          | recent_sortino_non_positive;oos_net_mean_not_all_positive;shuffle_control_dominated_recent | False                 |

