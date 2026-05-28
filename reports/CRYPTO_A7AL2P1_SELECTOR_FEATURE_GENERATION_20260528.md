# CRYPTO A7AL-2P1 Selector Feature Generation

Generated: 2026-05-28T07:19:02Z

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
  "candidate_count": 2,
  "candidate_scope": "A7AL-2L replay-preflight clue candidates only",
  "decision": "PASS_A7AL2P1_SELECTOR_FEATURES_READY_FOR_P0R_RETRY",
  "decision_counts": {
    "A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE": 2
  },
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T07:19:02Z",
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
| A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |       2 |

## Selector Feature Matrix

| candidate_id            | cell                | family                 | field_families       | selector_decision                    |   selector_feature_score_no_may |   control_ratio_premay_max_by_split |   control_hard_hold_split_count |   latent_positive_premay_splits |   latent_min_premay_spread |   one_bar_lag_survival_recent |   formula_turnover_proxy |   formula_smoothing_score | lineage_feature_classes   |
|:------------------------|:--------------------|:-----------------------|:---------------------|:-------------------------------------|--------------------------------:|------------------------------------:|--------------------------------:|--------------------------------:|---------------------------:|------------------------------:|-------------------------:|--------------------------:|:--------------------------|
| a7al2k_046e806368e99c76 | J0_oi_derived_state | derived_oi_price_state | open_interest\|price | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |                      0.00280803 |                             0.79335 |                               0 |                               3 |                0.000883556 |                      0.985509 |                        0 |                  0.495493 | raw_source:2              |
| a7al2k_0a247ec03472983b | J0_oi_derived_state | derived_oi_price_state | open_interest\|price | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE |                      0.00265835 |                             0.88085 |                               0 |                               3 |                0.000137662 |                      0.989259 |                        0 |                  0.575837 | raw_source:2              |

## Split Control Gate

| candidate_id            | split                 |   original_abs_spread |   max_control_abs_spread |   control_ratio | control_gate        |
|:------------------------|:----------------------|----------------------:|-------------------------:|----------------:|:--------------------|
| a7al2k_046e806368e99c76 | validation_2025H1     |            0.00128866 |              0.000754455 |        0.585459 | ELIGIBLE_DIAGNOSTIC |
| a7al2k_046e806368e99c76 | test_2025H2           |            0.00191171 |              0.00151665  |        0.79335  | ELIGIBLE_DIAGNOSTIC |
| a7al2k_046e806368e99c76 | recent_oos_2026JanApr |            0.00186543 |              0.000897683 |        0.48122  | ELIGIBLE_DIAGNOSTIC |
| a7al2k_0a247ec03472983b | validation_2025H1     |            0.00122938 |              0.000894318 |        0.727455 | ELIGIBLE_DIAGNOSTIC |
| a7al2k_0a247ec03472983b | test_2025H2           |            0.00159185 |              0.00140218  |        0.88085  | WARN_CONTROL_CLOSE  |
| a7al2k_0a247ec03472983b | recent_oos_2026JanApr |            0.00188517 |              0.00122051  |        0.647428 | ELIGIBLE_DIAGNOSTIC |

## Time-Varying Latent Neutralization

| candidate_id            | variant                          | entry_label     | split                 |   n_dates |   mean_oriented_spread |   hourly_tstat_naive |   positive_rate |
|:------------------------|:---------------------------------|:----------------|:----------------------|----------:|-----------------------:|---------------------:|----------------:|
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000883556 |             4.80468  |        0.544107 |
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.0013573   |             7.05361  |        0.530631 |
| a7al2k_046e806368e99c76 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00108431  |             2.90148  |        0.498774 |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000137662 |             0.736927 |        0.516786 |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00178999  |             8.94897  |        0.535869 |
| a7al2k_0a247ec03472983b | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00100666  |             2.65859  |        0.489667 |

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
