# CRYPTO A7AL-2N Derived Deep Audit

Generated: 2026-05-27T13:34:32Z

## Decision

```text
PASS_A7AL2N_DEEP_AUDIT_DIAGNOSTIC_CANDIDATES_FOUND
```

This audits the four A7AL-2M deep-audit derived clues for concentration, beta, taxonomy exposure, control-margin, and month/symbol dependence. It does not authorize alpha proof, large search, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7al2o_candidate_mini_replay": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_eval_errors": 0,
  "decision": "PASS_A7AL2N_DEEP_AUDIT_DIAGNOSTIC_CANDIDATES_FOUND",
  "decision_counts": {
    "A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS": 4
  },
  "deep_audit_candidates": 4,
  "diagnostic_pass_count": 4,
  "executes_alpha_proof": false,
  "executes_deep_audit": true,
  "executes_formula_generation": false,
  "generated_at": "2026-05-27T13:34:32Z",
  "input_clue_file": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2m_derived_clue_forensic\\a7al2m_clue_shortlist.csv",
  "latency_policy": "field_native_one_bar_lag_inherited_from_a7al2l_no_blanket_plus2h",
  "may_usage": "stress_label_only_not_used_for_orientation_or_selection",
  "orientation_policy": "pre_may_validation_test_recent_mean_sign_only",
  "strict_symbols": 181,
  "timestamps": 21025,
  "warnings": {
    "train_oriented_spread_nonpositive": 2
  }
}
```

## Decision Counts

| deep_audit_label                  |   count |
|:----------------------------------|--------:|
| A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS |       4 |

## Candidate Summary

| candidate_id            | cell                        | family                      | field_families   |   orientation_from_premay | deep_audit_label                  | reasons   | warnings                          |   oriented_spread__validation_2025H1 |   oriented_spread__test_2025H2 |   oriented_spread__recent_oos_2026JanApr |   oriented_spread__known_may2026_stress |   top_symbol_abs_contribution_share |   top3_symbol_abs_contribution_share |   pre_may_top_month_abs_share |
|:------------------------|:----------------------------|:----------------------------|:-----------------|--------------------------:|:----------------------------------|:----------|:----------------------------------|-------------------------------------:|-------------------------------:|-----------------------------------------:|----------------------------------------:|------------------------------------:|-------------------------------------:|------------------------------:|
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity |                        -1 | A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS |           |                                   |                          0.00123838  |                     0.00303946 |                               0.00195588 |                              0.00338678 |                           0.0313376 |                            0.0746338 |                      0.150363 |
| a7al2k_0cf817ef95787b3d | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity |                        -1 | A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS |           |                                   |                          0.0020818   |                     0.00449646 |                               0.00379066 |                              0.00648685 |                           0.0269333 |                            0.0716224 |                      0.136147 |
| a7al2k_134ec76b5d7444f9 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity\|price |                        -1 | A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS |           | train_oriented_spread_nonpositive |                          0.00214053  |                     0.00418491 |                               0.00218342 |                              0.00385336 |                           0.04182   |                            0.112532  |                      0.167858 |
| a7al2k_01298a6b5902f416 | J0_oi_derived_state         | derived_oi_price_state      | open_interest    |                        -1 | A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS |           | train_oriented_spread_nonpositive |                          0.000830232 |                     0.00174322 |                               0.00159322 |                              0.00171216 |                           0.0304445 |                            0.0884809 |                      0.136724 |

## Split Summary

| candidate_id            | split                 |   n_dates |   mean_oriented_spread_24h |   spread_tstat |   positive_spread_rate |   avg_top_count |   avg_bottom_count |
|:------------------------|:----------------------|----------:|---------------------------:|---------------:|-----------------------:|----------------:|-------------------:|
| a7al2k_01759e5da72c472c | train_2024            |      8737 |                0.00160885  |       9.16841  |               0.552592 |         18.9112 |            18.9112 |
| a7al2k_01759e5da72c472c | validation_2025H1     |      4320 |                0.00123838  |       5.85029  |               0.534722 |         19      |            19      |
| a7al2k_01759e5da72c472c | test_2025H2           |      4392 |                0.00303946  |      12.6475   |               0.569217 |         18.9677 |            18.9677 |
| a7al2k_01759e5da72c472c | recent_oos_2026JanApr |      2856 |                0.00195588  |       6.95185  |               0.54902  |         19      |            19      |
| a7al2k_01759e5da72c472c | known_may2026_stress  |       576 |                0.00338678  |       5.57578  |               0.546875 |         19      |            19      |
| a7al2k_0cf817ef95787b3d | train_2024            |      8737 |                0.000834166 |       4.62323  |               0.538514 |         18.9112 |            18.9112 |
| a7al2k_0cf817ef95787b3d | validation_2025H1     |      4320 |                0.0020818   |       9.44864  |               0.561574 |         19      |            19      |
| a7al2k_0cf817ef95787b3d | test_2025H2           |      4392 |                0.00449646  |      18.1692   |               0.632286 |         18.7163 |            18.7163 |
| a7al2k_0cf817ef95787b3d | recent_oos_2026JanApr |      2856 |                0.00379066  |      11.5038   |               0.595238 |         18.8071 |            18.8071 |
| a7al2k_0cf817ef95787b3d | known_may2026_stress  |       576 |                0.00648685  |      12.0823   |               0.715278 |         19      |            19      |
| a7al2k_134ec76b5d7444f9 | train_2024            |      8664 |               -0.0019385   |      -8.28271  |               0.509926 |         18.8135 |            18.8135 |
| a7al2k_134ec76b5d7444f9 | validation_2025H1     |      4320 |                0.00214053  |       8.86509  |               0.538194 |         18.8111 |            18.8111 |
| a7al2k_134ec76b5d7444f9 | test_2025H2           |      4392 |                0.00418491  |      19.3997   |               0.615437 |         19      |            19      |
| a7al2k_134ec76b5d7444f9 | recent_oos_2026JanApr |      2856 |                0.00218342  |       7.57352  |               0.570378 |         19      |            19      |
| a7al2k_134ec76b5d7444f9 | known_may2026_stress  |       576 |                0.00385336  |       9.11855  |               0.734375 |         19      |            19      |
| a7al2k_01298a6b5902f416 | train_2024            |      8569 |               -0.000105822 |      -0.523353 |               0.514296 |         18.9094 |            18.9094 |
| a7al2k_01298a6b5902f416 | validation_2025H1     |      4320 |                0.000830232 |       3.97582  |               0.530787 |         19      |            19      |
| a7al2k_01298a6b5902f416 | test_2025H2           |      4392 |                0.00174322  |       9.65716  |               0.5699   |         19      |            19      |
| a7al2k_01298a6b5902f416 | recent_oos_2026JanApr |      2856 |                0.00159322  |       6.48864  |               0.532563 |         19      |            19      |
| a7al2k_01298a6b5902f416 | known_may2026_stress  |       576 |                0.00171216  |       5.02368  |               0.605903 |         19      |            19      |

## Beta Exposure

| candidate_id            | group                | benchmark_symbol   |   n_dates |        corr |        beta |
|:------------------------|:---------------------|:-------------------|----------:|------------:|------------:|
| a7al2k_01759e5da72c472c | pre_may_oos          | BTCUSDT            |     11568 |  0.157787   |  0.101753   |
| a7al2k_01759e5da72c472c | pre_may_oos          | ETHUSDT            |     11568 |  0.178749   |  0.0702097  |
| a7al2k_01759e5da72c472c | known_may2026_stress | BTCUSDT            |       576 |  0.147879   |  0.154416   |
| a7al2k_01759e5da72c472c | known_may2026_stress | ETHUSDT            |       576 |  0.121451   |  0.101813   |
| a7al2k_0cf817ef95787b3d | pre_may_oos          | BTCUSDT            |     11568 |  0.0496211  |  0.0342734  |
| a7al2k_0cf817ef95787b3d | pre_may_oos          | ETHUSDT            |     11568 |  0.00354928 |  0.00149317 |
| a7al2k_0cf817ef95787b3d | known_may2026_stress | BTCUSDT            |       576 |  0.0484783  |  0.0447444  |
| a7al2k_0cf817ef95787b3d | known_may2026_stress | ETHUSDT            |       576 |  0.0510258  |  0.037809   |
| a7al2k_134ec76b5d7444f9 | pre_may_oos          | BTCUSDT            |     11568 | -0.23788    | -0.155502   |
| a7al2k_134ec76b5d7444f9 | pre_may_oos          | ETHUSDT            |     11568 | -0.280822   | -0.111812   |
| a7al2k_134ec76b5d7444f9 | known_may2026_stress | BTCUSDT            |       576 | -0.166338   | -0.12084    |
| a7al2k_134ec76b5d7444f9 | known_may2026_stress | ETHUSDT            |       576 | -0.148282   | -0.0864816  |
| a7al2k_01298a6b5902f416 | pre_may_oos          | BTCUSDT            |     11568 |  0.154568   |  0.0859634  |
| a7al2k_01298a6b5902f416 | pre_may_oos          | ETHUSDT            |     11568 |  0.0785391  |  0.0266048  |
| a7al2k_01298a6b5902f416 | known_may2026_stress | BTCUSDT            |       576 |  0.382541   |  0.224134   |
| a7al2k_01298a6b5902f416 | known_may2026_stress | ETHUSDT            |       576 |  0.39054    |  0.1837     |

## Boundary

```text
Allowed next step if diagnostic candidates pass:
  A7AL-2O candidate-specific mini replay / neutralization audit.

Not authorized:
  formula search execution
  alpha proof
  shadow / paper / live
```
