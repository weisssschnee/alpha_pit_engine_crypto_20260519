# CRYPTO A7REGIME3 Candidate Regime Attribution 20260612

## Decision

`HOLD_A7REGIME3_ACCEPTED_QUEUE_REGIME_CONCENTRATED`

This is a regime attribution and robustness audit. It does not authorize alpha proof, shadow, paper, live execution, or formula search.

## Scope

- queue: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7reward1_portfolio_reward_model_20260610\a7reward1_accepted_for_next_search.csv`
- queue_rows: `6`
- state_metric_rows: `480`
- leave_state_out_rows: `480`
- error_rows: `0`
- hours_per_split: `0`
- train_hours_per_split: `0`

## Candidate Decisions

| blueprint_id            |   horizon_h |   concentrated_split_count |   max_top_abs_net_contribution_share | top_contribution_states                                      |   leave_state_out_fail_count | decision                 |
|:------------------------|------------:|---------------------------:|-------------------------------------:|:-------------------------------------------------------------|-----------------------------:|:-------------------------|
| a7ls30_c139d322017158f7 |          24 |                          4 |                              3.19615 | is_weekend|basis_dislocation_p95|funding_negative_extreme    |                           21 | HOLD_REGIME_CONCENTRATED |
| a7ls30_c139d322017158f7 |           8 |                          4 |                              1.76555 | is_weekend|funding_negative_extreme|basis_dislocation_p90    |                           13 | HOLD_REGIME_CONCENTRATED |
| a7ls30_32f8844234cc65fc |          24 |                          4 |                              1.56793 | is_weekend|basis_dislocation_p95|funding_negative_extreme    |                           14 | HOLD_REGIME_CONCENTRATED |
| a7ls30_32f8844234cc65fc |           8 |                          4 |                              1.07024 | is_weekend|funding_negative_extreme|basis_dislocation_p90    |                           12 | HOLD_REGIME_CONCENTRATED |
| a7ls30_32f8844234cc65fc |           4 |                          4 |                              1.0568  | is_weekend|funding_negative_extreme|funding_negative_extreme |                            9 | HOLD_REGIME_CONCENTRATED |
| a7ls30_c94e306c3e19bd08 |           8 |                          4 |                              1.04002 | is_weekend|basis_dislocation_p90|funding_negative_extreme    |                           11 | HOLD_REGIME_CONCENTRATED |

## Key Findings

The current accepted queue is not regime-broad. All six accepted rows are `open_interest_like|positioning_like / safe_div_abs` variants, and all six are held by the regime attribution layer.

The dominant contributors are:

```text
validation / test:
  funding_negative_extreme

recent_oos_2026JanApr:
  basis_dislocation_p90 / basis_dislocation_p95

known_may2026_stress:
  is_weekend, plus basis/taker/perp-pressure sensitivity
```

This means the reward gate found candidates with strong portfolio metrics, but A7REGIME-3 shows those metrics are still too dependent on specific market-mechanism states. The right response is not to discard the mechanism signal; it is to stop treating the accepted queue as a broad alpha seed pool until mechanism concentration is penalized or diversified.

## Highest Single-State Contribution Cases

| blueprint_id            |   horizon_h | split                 | top_contribution_state   |   top_abs_net_contribution_share |   top_state_hours | concentration_decision           |
|:------------------------|------------:|:----------------------|:-------------------------|---------------------------------:|------------------:|:---------------------------------|
| a7ls30_c139d322017158f7 |          24 | known_may2026_stress  | is_weekend               |                         3.19615  |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |           8 | known_may2026_stress  | is_weekend               |                         1.76555  |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |          24 | known_may2026_stress  | is_weekend               |                         1.56793  |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           8 | known_may2026_stress  | is_weekend               |                         1.07024  |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |           8 | validation_2025H1     | funding_negative_extreme |                         1.0702   |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |          24 | recent_oos_2026JanApr | basis_dislocation_p95    |                         1.06624  |              2427 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           4 | known_may2026_stress  | is_weekend               |                         1.0568   |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |          24 | validation_2025H1     | funding_negative_extreme |                         1.056    |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c94e306c3e19bd08 |           8 | known_may2026_stress  | is_weekend               |                         1.04002  |               192 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |          24 | recent_oos_2026JanApr | basis_dislocation_p95    |                         1.03795  |              2427 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |          24 | validation_2025H1     | funding_negative_extreme |                         1.01982  |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           4 | validation_2025H1     | funding_negative_extreme |                         1.01345  |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |           8 | recent_oos_2026JanApr | basis_dislocation_p90    |                         1.00906  |              2829 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           8 | validation_2025H1     | funding_negative_extreme |                         0.998523 |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           8 | recent_oos_2026JanApr | basis_dislocation_p90    |                         0.994254 |              2829 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c94e306c3e19bd08 |           8 | recent_oos_2026JanApr | basis_dislocation_p90    |                         0.992054 |              2829 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c94e306c3e19bd08 |           8 | validation_2025H1     | funding_negative_extreme |                         0.969643 |              2350 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           4 | recent_oos_2026JanApr | funding_negative_extreme |                         0.966474 |              2835 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |           8 | test_2025H2           | funding_negative_extreme |                         0.960714 |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           8 | test_2025H2           | funding_negative_extreme |                         0.959887 |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c94e306c3e19bd08 |           8 | test_2025H2           | funding_negative_extreme |                         0.95416  |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |           4 | test_2025H2           | funding_negative_extreme |                         0.952266 |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_32f8844234cc65fc |          24 | test_2025H2           | funding_negative_extreme |                         0.939266 |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |          24 | test_2025H2           | funding_negative_extreme |                         0.932218 |              4130 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |           8 | train_2024            | is_weekend               |                         0.911278 |              2496 | HOLD_SINGLE_REGIME_CONCENTRATION |
| a7ls30_c139d322017158f7 |          24 | train_2024            | extreme_vol_168h_p95     |                         0.586922 |               438 | PASS_NO_SINGLE_REGIME_DOMINANCE  |
| a7ls30_c94e306c3e19bd08 |           8 | train_2024            | extreme_vol_168h_p95     |                         0.351204 |               438 | PASS_NO_SINGLE_REGIME_DOMINANCE  |
| a7ls30_32f8844234cc65fc |           8 | train_2024            | extreme_vol_168h_p95     |                         0.32282  |               438 | PASS_NO_SINGLE_REGIME_DOMINANCE  |
| a7ls30_32f8844234cc65fc |           4 | train_2024            | extreme_vol_168h_p95     |                         0.322185 |               438 | PASS_NO_SINGLE_REGIME_DOMINANCE  |
| a7ls30_32f8844234cc65fc |          24 | train_2024            | extreme_vol_168h_p95     |                         0.277511 |               438 | PASS_NO_SINGLE_REGIME_DOMINANCE  |

## Interpretation

A candidate is treated as regime-fragile if too much of its OOS/stress net contribution comes from a single mechanism state or if leave-state-out removes the positive edge. This protects the search loop from mistaking a basis/taker/funding event fingerprint for general alpha.
