# CRYPTO A7V3S10 Accepted Candidate Validation Pack 20260614

Decision: `HOLD_RESEARCH`

## Candidate Factor Review

- factor_id: `a7v3s0_37b921db0b74a15a`
- provenance: A7V3S9 proxy-selected candidate, then A7V3S9 bounded full reward accepted.
- formula: `Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))`
- operator path: `premium_abs_state -> Decay(336)` times `mark_trade_basis_bps -> Mean(168) -> ZScore -> Abs`.
- data source: Binance universe 498 v3 1h replay panel with recent patch/age fields; reward model uses PIT-style evaluator and control variants.
- feature family: `basis|premium`, `smooth_mul`.
- expected mechanism: premium/basis dislocation magnitude interacting with slow premium state.

## Bias Audit

- discovery status: discovery/search output; not replay proof.
- frequency/horizon: 1h panel, accepted horizon 24h.
- windows used by reward: train_2024, validation_2025H1, test_2025H2, recent_oos_2026JanApr, known_may2026_stress.
- cost model: 5 bps in reward command.
- controls: one_bar_lag, stale_168h, sign_flip, time_shuffle, symbol_shuffle and matched-control counts in reward output.
- OOS sample grade: basic per split windows, stronger only when considered as multi-split evidence; not promotion-grade proof.

## Accepted Candidate Summary

| blueprint_id            | semantic_pair   | motif      |   horizon_h |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_control_ratio |   recent_shuffle_control_ratio | gate_pass   | hard_reject   | expression                                                                    |
|:------------------------|:----------------|:-----------|------------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-----------------------:|-------------------------------:|:------------|:--------------|:------------------------------------------------------------------------------|
| a7v3s0_37b921db0b74a15a | basis|premium   | smooth_mul |          24 |         1.20055 |              6.33048 |        5.51086 |          1.81475 |                 0.85222 |                6.49772 |               0.981467 |                       0.356316 | True        | False         | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168)))) |

## Accepted Original Split Attribution

| split                 |   n_obs |    net_mean |   sharpe |   sortino |   nonoverlap_floor_sortino |   max_drawdown |   positive_rate |    avg_cost |   avg_turnover |    ic_mean |   rankic_mean |
|:----------------------|--------:|------------:|---------:|----------:|---------------------------:|---------------:|----------------:|------------:|---------------:|-----------:|--------------:|
| train_2024            |    8784 | 0.000216037 | 0.851847 |   1.25002 |                   0.655207 |      -0.757881 |        0.503529 | 2.15805e-05 |      0.043161  | 0.00469891 |    0.00938974 |
| validation_2025H1     |     720 | 0.00064814  | 4.09922  |   6.60204 |                   4.97102  |      -0.277741 |        0.636111 | 1.69973e-05 |      0.0339946 | 0.0277208  |    0.0180375  |
| test_2025H2           |     720 | 0.000705213 | 3.10126  |   5.14539 |                   1.95231  |      -0.272196 |        0.584722 | 1.38506e-05 |      0.0277012 | 0.00631641 |   -0.00982399 |
| recent_oos_2026JanApr |     720 | 0.000476274 | 1.2901   |   1.74544 |                   0.85222  |      -0.62144  |        0.538889 | 1.74359e-05 |      0.0348717 | 0.0292898  |    0.0391217  |
| known_may2026_stress  |     601 | 0.00131514  | 6.59982  |  11.0577  |                   6.49772  |      -0.203023 |        0.647255 | 1.8569e-05  |      0.0371379 | 0.0423561  |    0.0356849  |

## Accepted Control Split Snapshot

| variant        | split                 |   n_obs |     net_mean |     sharpe |    sortino |   nonoverlap_floor_sortino |   max_drawdown |   positive_rate |    avg_cost |   avg_turnover |      ic_mean |   rankic_mean |
|:---------------|:----------------------|--------:|-------------:|-----------:|-----------:|---------------------------:|---------------:|----------------:|------------:|---------------:|-------------:|--------------:|
| one_bar_lag    | train_2024            |    8784 |  0.000216786 |  0.854945  |  1.25323   |                   0.698185 |      -0.759363 |        0.50444  | 2.15785e-05 |      0.0431571 |  0.00474602  |   0.00950134  |
| one_bar_lag    | validation_2025H1     |     720 |  0.000638909 |  4.05866   |  6.50848   |                   4.55586  |      -0.278252 |        0.630556 | 1.69997e-05 |      0.0339994 |  0.0276293   |   0.0181416   |
| one_bar_lag    | test_2025H2           |     720 |  0.000708406 |  3.1006    |  5.16357   |                   1.60069  |      -0.272799 |        0.577778 | 1.38545e-05 |      0.0277091 |  0.00642704  |  -0.00932039  |
| one_bar_lag    | recent_oos_2026JanApr |     720 |  0.000467447 |  1.26633   |  1.70502   |                   0.578542 |      -0.624867 |        0.536111 | 1.7435e-05  |      0.0348699 |  0.0289713   |   0.0390513   |
| one_bar_lag    | known_may2026_stress  |     601 |  0.00132789  |  6.6655    | 11.1645    |                   5.80061  |      -0.203002 |        0.663894 | 1.85621e-05 |      0.0371242 |  0.0425435   |   0.0357854   |
| stale_168h     | train_2024            |    8784 |  0.000216292 |  0.920726  |  1.40735   |                   1.00583  |      -0.757052 |        0.480077 | 2.11041e-05 |      0.0422082 |  0.0041928   |   0.00663313  |
| stale_168h     | validation_2025H1     |     720 |  0.000276484 |  1.85606   |  2.65402   |                   0.704842 |      -0.173222 |        0.529167 | 1.89836e-05 |      0.0379672 |  0.0177111   |  -0.0114963   |
| stale_168h     | test_2025H2           |     720 |  1.9962e-06  |  0.0103585 |  0.0164456 |                  -1.99916  |      -0.436948 |        0.466667 | 1.48006e-05 |      0.0296013 | -0.00797532  |  -0.0194613   |
| stale_168h     | recent_oos_2026JanApr |     720 | -0.000143914 | -0.423831  | -0.527522  |                  -2.25576  |      -0.588263 |        0.559722 | 1.61901e-05 |      0.0323803 |  0.0145754   |   0.00424639  |
| stale_168h     | known_may2026_stress  |     601 |  0.000771255 |  3.08306   |  4.56293   |                   0.666282 |      -0.328348 |        0.59401  | 1.84646e-05 |      0.0369292 |  0.0198873   |   0.0222437   |
| sign_flip      | train_2024            |    8784 | -0.000259198 | -1.02185   | -1.38442   |                  -1.97462  |      -0.967045 |        0.487477 | 2.15805e-05 |      0.043161  | -0.00469891  |  -0.00938974  |
| sign_flip      | validation_2025H1     |     720 | -0.000682134 | -4.313     | -5.26785   |                  -6.9509   |      -0.393148 |        0.325    | 1.69973e-05 |      0.0339946 | -0.0277208   |  -0.0180375   |
| sign_flip      | test_2025H2           |     720 | -0.000732915 | -3.22368   | -3.94527   |                  -5.82068  |      -0.520152 |        0.380556 | 1.38506e-05 |      0.0277012 | -0.00631641  |   0.00982399  |
| sign_flip      | recent_oos_2026JanApr |     720 | -0.000511146 | -1.38443   | -2.03889   |                  -3.14896  |      -0.525512 |        0.426389 | 1.74359e-05 |      0.0348717 | -0.0292898   |  -0.0391217   |
| sign_flip      | known_may2026_stress  |     601 | -0.00135228  | -6.78691   | -7.7206    |                  -9.35905  |      -0.558454 |        0.30782  | 1.8569e-05  |      0.0371379 | -0.0423561   |  -0.0356849   |
| time_shuffle   | train_2024            |    8784 | -0.00034288  | -1.42197   | -1.9025    |                  -3.7152   |      -0.961833 |        0.461749 | 0.000290754 |      0.581508  | -0.00198126  |  -0.00390993  |
| time_shuffle   | validation_2025H1     |     720 | -0.000426778 | -2.62597   | -3.19556   |                  -7.86805  |      -0.301456 |        0.472222 | 0.000289624 |      0.579249  |  0.000653026 |  -0.00783271  |
| time_shuffle   | test_2025H2           |     720 | -0.000733742 | -3.72756   | -4.86181   |                 -10.2845   |      -0.498194 |        0.365278 | 0.00029156  |      0.583119  | -0.0246451   |  -0.030009    |
| time_shuffle   | recent_oos_2026JanApr |     720 | -0.000153844 | -0.484905  | -0.628949  |                  -6.27229  |      -0.360727 |        0.495833 | 0.000292614 |      0.585228  |  0.00704964  |  -0.000463234 |
| time_shuffle   | known_may2026_stress  |     601 |  0.000702202 |  3.39323   |  5.39236   |                  -1.69913  |      -0.124412 |        0.552413 | 0.000290774 |      0.581548  |  0.0285549   |   0.0269288   |
| symbol_shuffle | train_2024            |    8784 | -0.000260626 | -1.16807   | -1.52045   |                  -1.8446   |      -0.972364 |        0.482013 | 2.15805e-05 |      0.043161  | -0.00383882  |  -0.00502784  |
| symbol_shuffle | validation_2025H1     |     720 |  0.000382229 |  2.65435   |  4.33329   |                   2.19259  |      -0.202045 |        0.527778 | 1.69973e-05 |      0.0339946 |  0.0128548   |   0.0180081   |
| symbol_shuffle | test_2025H2           |     720 | -0.000127426 | -0.78672   | -1.24536   |                  -2.9673   |      -0.319128 |        0.423611 | 1.38506e-05 |      0.0277012 | -0.0104919   |   0.00497505  |
| symbol_shuffle | recent_oos_2026JanApr |     720 | -0.000169704 | -0.688883  | -0.925175  |                  -3.61768  |      -0.399662 |        0.473611 | 1.74359e-05 |      0.0348717 |  0.00511831  |   0.0282897   |
| symbol_shuffle | known_may2026_stress  |     601 |  0.000154628 |  0.878132  |  1.33853   |                  -4.30927  |      -0.242109 |        0.494176 | 1.8569e-05  |      0.0371379 | -0.000394906 |   0.00180193  |

## Baseline / Ablation Reward Results

These test whether the accepted formula is just a single-leg basis/premium primitive.

| blueprint_id                    | semantic_pair   | motif               |   horizon_h |   train_sortino |   validation_sortino |   test_sortino |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_control_ratio |   recent_shuffle_control_ratio | gate_pass   | hard_reject   | hard_reject_reasons                                                                                                                                                                                                                                           | expression                                                                   |
|:--------------------------------|:----------------|:--------------------|------------:|----------------:|---------------------:|---------------:|-----------------:|------------------------:|-----------------------:|-----------------------:|-------------------------------:|:------------|:--------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|
| a7v3s10_ablation_shorter_basis  | basis|premium   | smooth_mul_ablation |          24 |       0.554551  |             0.670943 |        4.68966 |        0.589186  |               -2.13739  |               4.84677  |               5.84248  |                       5.84248  | False       | True          | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent                                                                                                                        | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_component_premium_decay | premium         | component           |           8 |       2.40021   |            -5.31094  |       -3.54667 |        1.8688    |               -5.66176  |               1.86992  |               0.991491 |                       0.630824 | False       | True          | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive                                                                                                                                                   | Decay(premium_abs_state,336)                                                 |
| a7v3s10_component_premium_decay | premium         | component           |           1 |       1.82228   |            -6.7052   |       -4.71814 |        1.33222   |               -6.7052   |               2.49969  |              14.0505   |                      14.0505   | False       | True          | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                                                  | Decay(premium_abs_state,336)                                                 |
| a7v3s10_component_basis_z       | basis           | component           |           8 |       1.30824   |             1.19199  |        6.49511 |        0.197253  |               -0.172715 |              -2.95744  |              18.5509   |                      18.5509   | False       | True          | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent                                                                                              | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_component_basis_z       | basis           | component           |          24 |       1.47047   |             1.39407  |        6.63513 |        0.201581  |               -0.655037 |              -1.49927  |              15.1598   |                      14.9681   | False       | True          | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;shuffle_control_dominated_recent                                                                                                                    | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_ablation_shorter_basis  | basis|premium   | smooth_mul_ablation |           4 |      -0.0276275 |            -0.996265 |       -1.86524 |        0.931026  |               -2.84527  |              13.4588   |               9.42786  |                       9.42786  | False       | True          | train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                       | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_ablation_shorter_basis  | basis|premium   | smooth_mul_ablation |           8 |       0.560029  |            -0.513584 |       -0.75397 |        1.36102   |               -2.95212  |              11.3144   |               1.10419  |                       1.04686  | False       | True          | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                          | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_component_premium_decay | premium         | component           |           4 |       2.37555   |            -5.87713  |       -4.08535 |        2.13272   |               -6.24336  |               2.62123  |               2.31697  |                       2.31697  | False       | True          | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                          | Decay(premium_abs_state,336)                                                 |
| a7v3s10_component_basis_abs_z   | basis           | component           |          24 |       0.400216  |             8.3706   |        7.10349 |       -1.60311   |               -3.0358   |               5.99732  |               0.915032 |                       0.656797 | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive                                                                                               | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_premium_decay | premium         | component           |          24 |       2.46005   |            -4.62515  |       -2.86516 |        1.70395   |               -5.27305  |              -0.261339 |               1.21553  |                       1.21553  | False       | True          | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                | Decay(premium_abs_state,336)                                                 |
| a7v3s10_ablation_no_abs         | basis|premium   | smooth_mul_ablation |           8 |       1.17753   |             1.19316  |        7.76237 |       -1.02358   |               -1.74024  |               0.528904 |               8.11685  |                       8.11685  | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                    | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_ablation_no_abs         | basis|premium   | smooth_mul_ablation |           4 |       0.949105  |             0.48789  |        7.24831 |       -1.54368   |               -1.92244  |               1.26358  |               5.25565  |                       5.25565  | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_ablation_no_abs         | basis|premium   | smooth_mul_ablation |          24 |       1.26567   |             1.58705  |        6.89795 |       -1.36374   |               -2.24451  |               1.99968  |               2.78233  |                       2.78233  | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_component_basis_abs_z   | basis           | component           |           8 |       0.109864  |            10.0191   |        6.2467  |       -2.43828   |               -3.64249  |               4.14997  |               1.40687  |                       1.40687  | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_basis_abs_z   | basis           | component           |           1 |      -2.41743   |             4.8379   |        2.57478 |       -3.7593    |               -3.7593   |               5.6929   |               8.2362   |                       8.2362   | False       | True          | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                           | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_basis_abs_z   | basis           | component           |           4 |      -0.297959  |             9.10767  |        5.47074 |       -3.60374   |               -3.79621  |               5.05297  |               2.06333  |                       2.06333  | False       | True          | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                 | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_ablation_shorter_basis  | basis|premium   | smooth_mul_ablation |           1 |      -3.85985   |            -6.72284  |       -4.54164 |       -1.30849   |               -6.72284  |               7.51706  |              14.7394   |                      14.7394   | False       | True          | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                           | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_component_basis_z       | basis           | component           |           4 |       1.09499   |             0.586427 |        5.68725 |       -0.0368597 |               -0.433903 |              -1.91136  |             296.714    |                     296.714    | False       | True          | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                          | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_component_basis_z       | basis           | component           |           1 |      -0.496442  |            -1.06473  |        3.73408 |       -1.37265   |               -1.37265  |              -3.32617  |              16.939    |                      16.939    | False       | True          | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_ablation_no_abs         | basis|premium   | smooth_mul_ablation |           1 |      -0.589503  |            -1.05183  |        5.44913 |       -2.42518   |               -2.42518  |              -0.590924 |               9.90033  |                       9.90033  | False       | True          | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |

## Baseline Accepted Rows

`<empty>`

## Rejection Reasons

Full reward selected queue:

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_control_dominated              |      15 |
| oos_lag_stale_dominated            |      13 |
| stress_floor_not_positive          |      11 |
| shuffle_control_dominated_recent   |       8 |
| oos_shuffle_dominated              |       6 |
| oos_nonoverlap_floor_not_positive  |       3 |
| train_orientation_no_positive_edge |       2 |

Baseline / ablation queue:

| blueprint_id                    |   horizon_h | hard_reject_reasons                                                                                                                                                                                                                                           | expression                                                                   |
|:--------------------------------|------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------|
| a7v3s10_component_premium_decay |           8 | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive                                                                                                                                                   | Decay(premium_abs_state,336)                                                 |
| a7v3s10_ablation_shorter_basis  |          24 | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent                                                                                                                        | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_component_premium_decay |           1 | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                                                  | Decay(premium_abs_state,336)                                                 |
| a7v3s10_component_premium_decay |           4 | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                          | Decay(premium_abs_state,336)                                                 |
| a7v3s10_ablation_shorter_basis  |           8 | oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                          | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_ablation_shorter_basis  |           4 | train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                       | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_component_basis_z       |          24 | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;shuffle_control_dominated_recent                                                                                                                    | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_component_basis_z       |           8 | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent                                                                                              | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_component_premium_decay |          24 | oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                | Decay(premium_abs_state,336)                                                 |
| a7v3s10_component_basis_abs_z   |          24 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive                                                                                               | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_ablation_no_abs         |           8 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                                                    | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_ablation_shorter_basis  |           1 | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                           | Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,72)))) |
| a7v3s10_ablation_no_abs         |          24 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_ablation_no_abs         |           4 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |
| a7v3s10_component_basis_abs_z   |           8 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                              | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_basis_abs_z   |           4 | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                 | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_basis_abs_z   |           1 | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                           | Abs(ZScore(Mean(mark_trade_basis_bps,168)))                                  |
| a7v3s10_component_basis_z       |           4 | recent_sortino_non_positive;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent                                                          | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_component_basis_z       |           1 | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent | ZScore(Mean(mark_trade_basis_bps,168))                                       |
| a7v3s10_ablation_no_abs         |           1 | recent_sortino_non_positive;train_orientation_no_positive_edge;oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;shuffle_control_dominated_recent | Mul(Decay(premium_abs_state,336),ZScore(Mean(mark_trade_basis_bps,168)))     |

## Issues

- No single-leg/ablation baseline passed full reward; composite has incremental evidence over tested primitives.
- Train Sortino is modest; OOS strength may be regime/local rather than broad in-sample edge.

## Decision

`HOLD_RESEARCH`

This validation pack authorizes only keep-review / broader search feedback. It does not authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "accepted_blueprint_id": "a7v3s0_37b921db0b74a15a",
  "accepted_expression": "Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))",
  "accepted_horizon_h": 24,
  "authorizes_alpha_proof": false,
  "authorizes_next_action": "information_increment_or_broader_search_feedback_only",
  "authorizes_shadow_paper_live": false,
  "baseline_accepted_rows": 0,
  "baseline_queue_rows": 5,
  "baseline_reward_rows": 20,
  "decision": "HOLD_RESEARCH",
  "full_reward_accepted_rows": 1,
  "issues": [
    "No single-leg/ablation baseline passed full reward; composite has incremental evidence over tested primitives.",
    "Train Sortino is modest; OOS strength may be regime/local rather than broad in-sample edge."
  ],
  "report": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\reports\\CRYPTO_A7V3S10_ACCEPTED_CANDIDATE_VALIDATION_PACK_20260614.md",
  "runtime": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7v3s10_accepted_candidate_validation_20260614",
  "stage": "A7V3S10_ACCEPTED_CANDIDATE_VALIDATION_PACK"
}
```
