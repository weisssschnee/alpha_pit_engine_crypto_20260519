# Crypto A7O-1 Fold Replay Kernel Audit

- generated_at: `2026-05-20T12:49:20Z`
- decision: `PASS_A7O1_FOLD_REPLAY_KERNEL_AUDIT`
- sample_candidates: `45`
- May usage: `0`

## Fold Definition Audit

| fold_id                    |    n | start                     | end                       | may_allowed   | kernel_status   |
|:---------------------------|-----:|:--------------------------|:--------------------------|:--------------|:----------------|
| F0_validation_2025H1       | 4296 | 2025-01-02 00:00:00+00:00 | 2025-06-29 23:00:00+00:00 | False         | PASS            |
| F0_recent_2025H2_2026Apr   | 7248 | 2025-07-02 00:00:00+00:00 | 2026-04-29 23:00:00+00:00 | False         | PASS            |
| F1_high_realized_vol       | 3463 | 2025-01-07 15:00:00+00:00 | 2026-04-14 06:00:00+00:00 | False         | PASS            |
| F2_low_liquidity           | 3463 | 2025-01-02 00:00:00+00:00 | 2026-04-29 14:00:00+00:00 | False         | PASS            |
| F3_high_liquidity_high_vol | 3341 | 2025-01-07 15:00:00+00:00 | 2026-04-17 21:00:00+00:00 | False         | PASS            |
| F4_basis_dislocation       | 3463 | 2025-01-07 15:00:00+00:00 | 2026-04-29 23:00:00+00:00 | False         | PASS            |
| F5_funding_neutral         | 5775 | 2025-01-09 16:00:00+00:00 | 2026-04-29 23:00:00+00:00 | False         | PASS            |
| F6_cross_symbol_dispersion | 3463 | 2025-01-02 00:00:00+00:00 | 2026-04-29 14:00:00+00:00 | False         | PASS            |
| F7_trend_reversal          | 4178 | 2025-01-02 15:00:00+00:00 | 2026-04-29 22:00:00+00:00 | False         | PASS            |
| F8_low_vol_high_liquidity  |  478 | 2025-01-06 16:00:00+00:00 | 2026-03-17 11:00:00+00:00 | False         | PASS            |
| F9_liquidity_shock         | 2886 | 2025-01-02 00:00:00+00:00 | 2026-04-29 18:00:00+00:00 | False         | PASS            |
| F10_volatility_compression | 4041 | 2025-01-02 12:00:00+00:00 | 2026-04-29 02:00:00+00:00 | False         | PASS            |
| F11_cross_symbol_crowding  | 3463 | 2025-01-02 07:00:00+00:00 | 2026-04-29 04:00:00+00:00 | False         | PASS            |

## Metrics Produced

- fold_replay_metric_rows: `2925`
- residual_metric_rows: `1170`
- cost_lag_metric_rows: `1170`