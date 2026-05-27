# Crypto A7D Funding Time-Semantics Audit

- generated_at: `2026-05-19T13:14:32Z`
- decision: `PASS_A7D_FUNDING_SEMANTICS_FOR_RESEARCH`
- blockers: `[]`
- warnings: `['exact_match_event_detection_misses_ms_offset_events', 'legacy_long_only_funding_model_materially_differs_from_full_signed_model', 'wrong_lag_future_24h_diagnostic_much_stronger_than_observable', 'observable_fundingcore_fresh_may_negative']`
- field_contract: `G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_A7D_FUNDING_FIELD_CONTRACT_20260519.json`

## Field Contract Summary

- `latest_known_funding_rate` is treated as a backward-asof settled/exchange-reported funding field, not a next funding prediction.
- `next_funding_rate` is not present and remains forbidden for signal use.
- Signal use is only allowed when `fundingTime_ms <= feature_available_time`.

## Timestamp Alignment

- rows: `250368`
- feature_before_execution violations: `0`
- funding_before_feature violations: `0`
- exact event detection rate: `0.6602760736196319`
- within 1h event visibility rate: `1.0`
- observable change event detection rate: `1.0`

## Funding Lag Ladder

| object | split | ann mean | compounded DD | month pass | mean turnover |
|---|---|---:|---:|---:|---:|
| `F0_no_funding_cash` | `validation_2025H1` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F0_no_funding_cash` | `recent_oos_2025H2_2026Apr` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F0_no_funding_cash` | `fresh_forward_2026May` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F1_last_settled_stale_8h` | `validation_2025H1` | 0.5239 | -0.4312 | 0.667 | 0.0293 |
| `F1_last_settled_stale_8h` | `recent_oos_2025H2_2026Apr` | 0.5842 | -0.5898 | 0.700 | 0.0313 |
| `F1_last_settled_stale_8h` | `fresh_forward_2026May` | -4.2579 | -0.2232 | 0.000 | 0.0325 |
| `F2_latest_known_observable` | `validation_2025H1` | 2.1062 | -0.3751 | 0.833 | 0.0295 |
| `F2_latest_known_observable` | `recent_oos_2025H2_2026Apr` | 0.9279 | -0.6068 | 0.800 | 0.0314 |
| `F2_latest_known_observable` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 0.000 | 0.0326 |
| `F3_delayed_1_funding_event_16h` | `validation_2025H1` | -0.0641 | -0.6457 | 0.500 | 0.0289 |
| `F3_delayed_1_funding_event_16h` | `recent_oos_2025H2_2026Apr` | 0.4780 | -0.5623 | 0.700 | 0.0313 |
| `F3_delayed_1_funding_event_16h` | `fresh_forward_2026May` | -3.1980 | -0.1465 | 0.000 | 0.0328 |
| `F4_future_next_funding_forbidden_8h` | `validation_2025H1` | 0.5376 | -0.4642 | 0.667 | 0.0285 |
| `F4_future_next_funding_forbidden_8h` | `recent_oos_2025H2_2026Apr` | -1.0441 | -0.7006 | 0.400 | 0.0314 |
| `F4_future_next_funding_forbidden_8h` | `fresh_forward_2026May` | -4.3751 | -0.2128 | 0.000 | 0.0324 |
| `F5_time_shuffled_funding` | `validation_2025H1` | -2.6934 | -0.7426 | 0.167 | 0.3204 |
| `F5_time_shuffled_funding` | `recent_oos_2025H2_2026Apr` | -2.1927 | -0.8422 | 0.200 | 0.3389 |
| `F5_time_shuffled_funding` | `fresh_forward_2026May` | -4.1878 | -0.1749 | 0.000 | 0.3425 |
| `F6_symbol_shuffled_funding` | `validation_2025H1` | -2.7938 | -0.7559 | 0.000 | 0.3233 |
| `F6_symbol_shuffled_funding` | `recent_oos_2025H2_2026Apr` | -2.8788 | -0.9087 | 0.000 | 0.3206 |
| `F6_symbol_shuffled_funding` | `fresh_forward_2026May` | -2.8549 | -0.1232 | 0.000 | 0.3370 |
| `F7_wrong_lag_future_24h` | `validation_2025H1` | 8.7746 | -0.1034 | 1.000 | 0.0307 |
| `F7_wrong_lag_future_24h` | `recent_oos_2025H2_2026Apr` | 5.7721 | -0.1665 | 1.000 | 0.0327 |
| `F7_wrong_lag_future_24h` | `fresh_forward_2026May` | 7.6980 | -0.0229 | 1.000 | 0.0331 |

## Funding Sign / Payment Decomposition

| object | split | ann mean | compounded DD |
|---|---|---:|---:|
| `net_current_long_only` | `validation_2025H1` | 7.5995 | -0.8667 |
| `net_current_long_only` | `recent_oos_2025H2_2026Apr` | 3.5038 | -0.9497 |
| `net_current_long_only` | `fresh_forward_2026May` | -11.0223 | -0.5444 |
| `net_full_signed` | `validation_2025H1` | 7.9920 | -0.8659 |
| `net_full_signed` | `recent_oos_2025H2_2026Apr` | 3.8730 | -0.9437 |
| `net_full_signed` | `fresh_forward_2026May` | -10.6142 | -0.5403 |
| `net_inverted_signed` | `validation_2025H1` | 6.4574 | -0.8727 |
| `net_inverted_signed` | `recent_oos_2025H2_2026Apr` | 2.6722 | -0.9526 |
| `net_inverted_signed` | `fresh_forward_2026May` | -11.7768 | -0.5499 |
| `gross_price_pnl` | `validation_2025H1` | 8.2482 | -0.8648 |
| `gross_price_pnl` | `recent_oos_2025H2_2026Apr` | 4.3082 | -0.9438 |
| `gross_price_pnl` | `fresh_forward_2026May` | -10.0949 | -0.5409 |
| `funding_full_signed_pnl` | `validation_2025H1` | 0.7673 | -0.0012 |
| `funding_full_signed_pnl` | `recent_oos_2025H2_2026Apr` | 0.6004 | -0.0013 |
| `funding_full_signed_pnl` | `fresh_forward_2026May` | 0.5813 | -0.0003 |

## Core4 Residual By Funding Version

| object | split | ann mean | compounded DD |
|---|---|---:|---:|
| `Core4_residual_vs_F1_last_settled_stale_8h` | `validation_2025H1` | 0.2666 | -0.3384 |
| `Core4_residual_vs_F1_last_settled_stale_8h` | `recent_oos_2025H2_2026Apr` | 0.3515 | -0.2683 |
| `Core4_residual_vs_F1_last_settled_stale_8h` | `fresh_forward_2026May` | 0.1848 | -0.0826 |
| `Core4_residual_vs_F2_latest_known_observable` | `validation_2025H1` | 0.1050 | -0.4152 |
| `Core4_residual_vs_F2_latest_known_observable` | `recent_oos_2025H2_2026Apr` | 0.3550 | -0.1540 |
| `Core4_residual_vs_F2_latest_known_observable` | `fresh_forward_2026May` | -0.7373 | -0.0684 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `validation_2025H1` | -0.0728 | -0.3704 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `recent_oos_2025H2_2026Apr` | 0.4761 | -0.1977 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `fresh_forward_2026May` | 0.8500 | -0.0525 |

## May 2026 Worst Symbol/Component Rows

| symbol | component | net full signed | price pnl | funding pnl | fee | turnover |
|---|---|---:|---:|---:|---:|---:|
| `BCHUSDT` | `funding_rate_h12` | -0.5178 | -0.5274 | 0.0125 | 0.0030 | 3.0000 |
| `BCHUSDT` | `funding_persistence_h12` | -0.4482 | -0.4591 | 0.0142 | 0.0035 | 3.5000 |
| `SOLUSDT` | `funding_rate_h12` | -0.2176 | -0.2156 | 0.0032 | 0.0052 | 5.1667 |
| `ADAUSDT` | `funding_persistence_h6` | -0.2153 | -0.2134 | 0.0042 | 0.0062 | 6.1667 |
| `BCHUSDT` | `funding_rate_h6` | -0.2151 | -0.2191 | 0.0068 | 0.0030 | 3.0000 |
| `ADAUSDT` | `funding_persistence_h12` | -0.2087 | -0.2094 | 0.0066 | 0.0058 | 5.8333 |
| `LINKUSDT` | `funding_persistence_h6` | -0.1822 | -0.1783 | 0.0010 | 0.0050 | 5.0000 |
| `DOGEUSDT` | `funding_persistence_h12` | -0.1795 | -0.1777 | 0.0027 | 0.0045 | 4.5000 |
| `BCHUSDT` | `funding_persistence_h6` | -0.1577 | -0.1624 | 0.0080 | 0.0035 | 3.5000 |
| `LINKUSDT` | `funding_persistence_h12` | -0.1368 | -0.1341 | 0.0021 | 0.0050 | 5.0000 |
| `AVAXUSDT` | `funding_rate_h12` | -0.1328 | -0.1263 | 0.0008 | 0.0073 | 7.3333 |
| `DOGEUSDT` | `funding_persistence_h6` | -0.1263 | -0.1232 | 0.0014 | 0.0045 | 4.5000 |

## Bias Audit Decision

- This is a linkage/data-semantics audit, not a new alpha search.
- Promotion remains blocked if event detection or funding payment semantics are unresolved.
- A clean result here would only allow further research; it would not imply paper/live readiness.
