# CRYPTO A7AL-2P1 Selector Feature Generation

Generated: 2026-05-27T17:56:14Z

## Decision

```text
PASS_A7AL2P1_SELECTOR_FEATURES_READY_FOR_P0R_RETRY
```

This stage upgrades selector inputs. It does not train, does not search, and does not authorize A7AL-2 execution. Derived features are first-class selector features when lineage and PIT rules are clean.

## Manifest

```json
{
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 10,
  "candidate_scope": "A7AL-2L replay-preflight clue candidates only",
  "decision": "PASS_A7AL2P1_SELECTOR_FEATURES_READY_FOR_P0R_RETRY",
  "decision_counts": {
    "A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE": 2,
    "HOLD_CONTROL_DOMINATED": 6,
    "HOLD_TIMEVARYING_LATENT_FRAGILE": 2
  },
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-27T17:56:14Z",
  "latent_coverage": {
    "loaded_rows": 3692531,
    "state_non_missing_share": 0.9703079075817397,
    "state_panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "state_seen_in_train_share": 0.7661959913546751
  },
  "required_next": "If eligible_count > 0, run a selector-reweighted mini replay/P0R retry; otherwise regenerate with time-varying latent survival in selector.",
  "selector_eligible_count": 2,
  "uses_may_in_selector": false,
  "warnings": []
}
```

## Decision Counts

| selector_decision                    |   count |
|:-------------------------------------|--------:|
| HOLD_CONTROL_DOMINATED               |       6 |
| A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |       2 |
| HOLD_TIMEVARYING_LATENT_FRAGILE      |       2 |

## Selector Feature Matrix

| candidate_id            | cell                        | family                      | field_families           | selector_decision                    |   selector_feature_score_no_may |   control_ratio_premay_max_by_split |   control_hard_hold_split_count |   latent_positive_premay_splits |   latent_min_premay_spread |   one_bar_lag_survival_recent |   formula_turnover_proxy |   formula_smoothing_score | lineage_feature_classes         |
|:------------------------|:----------------------------|:----------------------------|:-------------------------|:-------------------------------------|--------------------------------:|------------------------------------:|--------------------------------:|--------------------------------:|---------------------------:|------------------------------:|-------------------------:|--------------------------:|:--------------------------------|
| a7al2k_0cf817ef95787b3d | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity         | HOLD_CONTROL_DOMINATED               |                      0.00432367 |                            1.04108  |                               1 |                               2 |               -0.000862595 |                      0.968958 |                0.080327  |                  0.59269  | derived_rolling:1\|raw_source:1 |
| a7al2k_134ec76b5d7444f9 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity\|price         | HOLD_CONTROL_DOMINATED               |                      0.0036107  |                            1.06869  |                               1 |                               2 |               -0.000192527 |                      0.961596 |                0.292403  |                  0.547079 | raw_source:2                    |
| a7al2k_01bdc8d049fffe52 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity\|open_interest | HOLD_CONTROL_DOMINATED               |                      0.00298076 |                            1.22977  |                               1 |                               3 |                0.00126284  |                      0.972014 |                0.128475  |                  0.495493 | raw_source:2                    |
| a7al2k_046e806368e99c76 | J0_oi_derived_state         | derived_oi_price_state      | open_interest\|price     | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |                      0.00280803 |                            0.79335  |                               0 |                               3 |                0.000883556 |                      0.985509 |                0         |                  0.495493 | raw_source:2                    |
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity         | HOLD_TIMEVARYING_LATENT_FRAGILE      |                      0.00273101 |                            0.946342 |                               0 |                               1 |               -0.000646225 |                      0.978613 |                0.0759805 |                  0.607527 | raw_source:2                    |
| a7al2k_0a247ec03472983b | J0_oi_derived_state         | derived_oi_price_state      | open_interest\|price     | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |                      0.00265835 |                            0.88085  |                               0 |                               3 |                0.000137662 |                      0.989259 |                0         |                  0.575837 | raw_source:2                    |
| a7al2k_09e91fd6263c0156 | J0_oi_derived_state         | derived_oi_price_state      | open_interest\|price     | HOLD_CONTROL_DOMINATED               |                      0.00263274 |                            1.02337  |                               1 |                               3 |                0.000126017 |                      0.993134 |                0         |                  0.547079 | raw_source:2                    |
| a7al2k_0096829c83c908a8 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity\|open_interest | HOLD_CONTROL_DOMINATED               |                      0.00241138 |                            1.05137  |                               1 |                               3 |                0.000841381 |                      0.978343 |                0.080327  |                  0.59269  | raw_source:2                    |
| a7al2k_16eeb579c992bb45 | J3_basis_funding_derived    | derived_basis_funding_state | basis\|funding           | HOLD_CONTROL_DOMINATED               |                      0.00215384 |                            1.15123  |                               1 |                               0 |               -0.00114916  |                      0.719808 |                0.227941  |                  0.607527 | raw_source:2                    |
| a7al2k_01298a6b5902f416 | J0_oi_derived_state         | derived_oi_price_state      | open_interest            | HOLD_TIMEVARYING_LATENT_FRAGILE      |                      0.00193796 |                            0.932378 |                               0 |                               1 |               -0.000585113 |                      0.990979 |                0.151961  |                  0.607527 | raw_source:1                    |

## Split Control Gate

| candidate_id            | split                 |   original_abs_spread |   max_control_abs_spread |   control_ratio | control_gate           |
|:------------------------|:----------------------|----------------------:|-------------------------:|----------------:|:-----------------------|
| a7al2k_0096829c83c908a8 | validation_2025H1     |           0.000508861 |              0.000535001 |        1.05137  | HOLD_CONTROL_DOMINATED |
| a7al2k_0096829c83c908a8 | test_2025H2           |           0.0014315   |              0.00129225  |        0.902722 | WARN_CONTROL_CLOSE     |
| a7al2k_0096829c83c908a8 | recent_oos_2026JanApr |           0.00224684  |              0.00218392  |        0.971995 | WARN_CONTROL_CLOSE     |
| a7al2k_01bdc8d049fffe52 | validation_2025H1     |           0.00112037  |              0.00137779  |        1.22977  | HOLD_CONTROL_DOMINATED |
| a7al2k_01bdc8d049fffe52 | test_2025H2           |           0.00224767  |              0.00126274  |        0.561797 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01bdc8d049fffe52 | recent_oos_2026JanApr |           0.0027401   |              0.00202718  |        0.739818 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01759e5da72c472c | validation_2025H1     |           0.00123838  |              0.00117193  |        0.946342 | WARN_CONTROL_CLOSE     |
| a7al2k_01759e5da72c472c | test_2025H2           |           0.00303946  |              0.000473406 |        0.155753 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01759e5da72c472c | recent_oos_2026JanApr |           0.00195588  |              0.000847094 |        0.433101 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_0cf817ef95787b3d | validation_2025H1     |           0.0020818   |              0.00216733  |        1.04108  | HOLD_CONTROL_DOMINATED |
| a7al2k_0cf817ef95787b3d | test_2025H2           |           0.00449646  |              0.00376345  |        0.836979 | WARN_CONTROL_CLOSE     |
| a7al2k_0cf817ef95787b3d | recent_oos_2026JanApr |           0.00379066  |              0.000552914 |        0.145862 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_046e806368e99c76 | validation_2025H1     |           0.00128866  |              0.000754455 |        0.585459 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_046e806368e99c76 | test_2025H2           |           0.00191171  |              0.00151665  |        0.79335  | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_046e806368e99c76 | recent_oos_2026JanApr |           0.00186543  |              0.000897683 |        0.48122  | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_16eeb579c992bb45 | validation_2025H1     |           0.000706822 |              0.000813717 |        1.15123  | HOLD_CONTROL_DOMINATED |
| a7al2k_16eeb579c992bb45 | test_2025H2           |           0.00325996  |              0.00287469  |        0.881816 | WARN_CONTROL_CLOSE     |
| a7al2k_16eeb579c992bb45 | recent_oos_2026JanApr |           0.00157423  |              0.00104186  |        0.661824 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_09e91fd6263c0156 | validation_2025H1     |           0.00113968  |              0.00103417  |        0.907418 | WARN_CONTROL_CLOSE     |
| a7al2k_09e91fd6263c0156 | test_2025H2           |           0.00180176  |              0.00184387  |        1.02337  | HOLD_CONTROL_DOMINATED |
| a7al2k_09e91fd6263c0156 | recent_oos_2026JanApr |           0.00183545  |              0.00147922  |        0.805915 | WARN_CONTROL_CLOSE     |
| a7al2k_134ec76b5d7444f9 | validation_2025H1     |           0.00214053  |              0.00228757  |        1.06869  | HOLD_CONTROL_DOMINATED |
| a7al2k_134ec76b5d7444f9 | test_2025H2           |           0.00418491  |              0.00330251  |        0.789146 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_134ec76b5d7444f9 | recent_oos_2026JanApr |           0.00218342  |              0.00126939  |        0.581378 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_0a247ec03472983b | validation_2025H1     |           0.00122938  |              0.000894318 |        0.727455 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_0a247ec03472983b | test_2025H2           |           0.00159185  |              0.00140218  |        0.88085  | WARN_CONTROL_CLOSE     |
| a7al2k_0a247ec03472983b | recent_oos_2026JanApr |           0.00188517  |              0.00118045  |        0.626174 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01298a6b5902f416 | validation_2025H1     |           0.000830232 |              0.000774091 |        0.932378 | WARN_CONTROL_CLOSE     |
| a7al2k_01298a6b5902f416 | test_2025H2           |           0.00174322  |              0.00135875  |        0.779451 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01298a6b5902f416 | recent_oos_2026JanApr |           0.00159322  |              0.000555406 |        0.348605 | ELIGIBLE_DIAGNOSTIC    |

## Time-Varying Latent Neutralization

| candidate_id            | variant                          | entry_label     | split                 |   n_dates |   mean_oriented_spread |   hourly_tstat_naive |   positive_rate |
|:------------------------|:---------------------------------|:----------------|:----------------------|----------:|-----------------------:|---------------------:|----------------:|
| a7al2k_0096829c83c908a8 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.00110677  |             5.47873  |        0.537856 |
| a7al2k_0096829c83c908a8 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00155895  |             7.52465  |        0.576406 |
| a7al2k_0096829c83c908a8 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.000841381 |             2.46443  |        0.536953 |
| a7al2k_01bdc8d049fffe52 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.00165118  |             8.10628  |        0.566566 |
| a7al2k_01bdc8d049fffe52 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00154621  |             7.67264  |        0.584149 |
| a7al2k_01bdc8d049fffe52 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00126284  |             3.89495  |        0.557618 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000646225 |            -3.31291  |        0.481593 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00144539  |             7.3808   |        0.545206 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.000103753 |            -0.335747 |        0.520841 |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000862595 |            -4.17606  |        0.50081  |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00167556  |             9.63823  |        0.567752 |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00118772  |             4.29492  |        0.569177 |
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000883556 |             4.80468  |        0.544107 |
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.0013573   |             7.05361  |        0.530631 |
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00108431  |             2.90148  |        0.498774 |
| a7al2k_16eeb579c992bb45 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000812647 |            -3.99605  |        0.480667 |
| a7al2k_16eeb579c992bb45 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |           -0.000258948 |            -1.24225  |        0.490321 |
| a7al2k_16eeb579c992bb45 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.00114916  |            -3.6811   |        0.435727 |
| a7al2k_09e91fd6263c0156 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000126017 |             0.677184 |        0.517944 |
| a7al2k_09e91fd6263c0156 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00175801  |             8.87935  |        0.536324 |
| a7al2k_09e91fd6263c0156 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.000840733 |             2.26099  |        0.492469 |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000892006 |             4.03076  |        0.535772 |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00118454  |             6.95537  |        0.564564 |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.000192527 |            -0.696498 |        0.49352  |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000137662 |             0.736927 |        0.516786 |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00178999  |             8.94897  |        0.535869 |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00100666  |             2.65859  |        0.489667 |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000585113 |            -3.32559  |        0.497337 |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |           -0.000294195 |            -1.51284  |        0.50353  |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.000352243 |             1.35432  |        0.541506 |

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
