# CRYPTO A7AL-2P1 Selector Feature Generation

Generated: 2026-05-28T02:37:26Z

## Decision

```text
HOLD_A7AL2P1_SELECTOR_FEATURES_BLOCKED
```

This stage upgrades selector inputs. It does not train, does not search, and does not authorize A7AL-2 execution. Derived features are first-class selector features when lineage and PIT rules are clean.

## Manifest

```json
{
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_selector_candidate_survives_timevarying_latent_gate"
  ],
  "candidate_count": 3,
  "candidate_scope": "A7AL-2L replay-preflight clue candidates only",
  "decision": "HOLD_A7AL2P1_SELECTOR_FEATURES_BLOCKED",
  "decision_counts": {
    "HOLD_CONTROL_DOMINATED": 2,
    "HOLD_TIMEVARYING_LATENT_FRAGILE": 1
  },
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T02:37:26Z",
  "latent_coverage": {
    "loaded_rows": 3692531,
    "state_non_missing_share": 0.9703079075817397,
    "state_panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "state_seen_in_train_share": 0.7661959913546751
  },
  "required_next": "If eligible_count > 0, run a selector-reweighted mini replay/P0R retry; otherwise regenerate with time-varying latent survival in selector.",
  "selector_eligible_count": 0,
  "uses_may_in_selector": false,
  "warnings": [
    "selector_eligible_pool_below_2"
  ]
}
```

## Decision Counts

| selector_decision               |   count |
|:--------------------------------|--------:|
| HOLD_CONTROL_DOMINATED          |       2 |
| HOLD_TIMEVARYING_LATENT_FRAGILE |       1 |

## Selector Feature Matrix

| candidate_id            | cell                        | family                     | field_families           | selector_decision               |   selector_feature_score_no_may |   control_ratio_premay_max_by_split |   control_hard_hold_split_count |   latent_positive_premay_splits |   latent_min_premay_spread |   one_bar_lag_survival_recent |   formula_turnover_proxy |   formula_smoothing_score | lineage_feature_classes   |
|:------------------------|:----------------------------|:---------------------------|:-------------------------|:--------------------------------|--------------------------------:|------------------------------------:|--------------------------------:|--------------------------------:|---------------------------:|------------------------------:|-------------------------:|--------------------------:|:--------------------------|
| a7al2k_01bdc8d049fffe52 | J4_upper_regime_interaction | derived_upper_regime_proxy | liquidity\|open_interest | HOLD_CONTROL_DOMINATED          |                      0.00298076 |                            1.22977  |                               1 |                               3 |                0.00126284  |                      0.972014 |                0.128475  |                  0.495493 | raw_source:2              |
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy | basis\|liquidity         | HOLD_TIMEVARYING_LATENT_FRAGILE |                      0.00273101 |                            0.946342 |                               0 |                               1 |               -0.000646225 |                      0.978613 |                0.0759805 |                  0.607527 | raw_source:2              |
| a7al2k_0096829c83c908a8 | J4_upper_regime_interaction | derived_upper_regime_proxy | liquidity\|open_interest | HOLD_CONTROL_DOMINATED          |                      0.00241138 |                            1.05137  |                               1 |                               3 |                0.000841381 |                      0.978343 |                0.080327  |                  0.59269  | raw_source:2              |

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

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
