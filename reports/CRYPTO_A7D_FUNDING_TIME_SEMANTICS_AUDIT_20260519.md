# Crypto A7D Funding Time-Semantics Audit

- generated_at: `2026-05-19T13:02:00Z`
- decision: `HOLD_A7D_FUNDING_SEMANTICS_UNRESOLVED`
- blockers: `['funding_event_detection_exact_match_misses_events']`
- warnings: `['wrong_lag_future_24h_diagnostic_much_stronger_than_observable', 'observable_fundingcore_fresh_may_negative']`
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

## Funding Lag Ladder

| object | split | ann mean | compounded DD | month pass | mean turnover |
|---|---|---:|---:|---:|---:|
| `F0_no_funding_cash` | `validation_2025H1` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F0_no_funding_cash` | `recent_oos_2025H2_2026Apr` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F0_no_funding_cash` | `fresh_forward_2026May` | 0.0000 | 0.0000 | 0.000 | 0.0000 |
| `F1_last_settled_stale_8h` | `validation_2025H1` | 0.3810 | -0.4505 | 0.667 | 0.0293 |
| `F1_last_settled_stale_8h` | `recent_oos_2025H2_2026Apr` | 0.4244 | -0.5974 | 0.600 | 0.0313 |
| `F1_last_settled_stale_8h` | `fresh_forward_2026May` | -4.4237 | -0.2258 | 0.000 | 0.0325 |
| `F2_latest_known_observable` | `validation_2025H1` | 1.9697 | -0.3767 | 0.833 | 0.0295 |
| `F2_latest_known_observable` | `recent_oos_2025H2_2026Apr` | 0.7863 | -0.6195 | 0.800 | 0.0314 |
| `F2_latest_known_observable` | `fresh_forward_2026May` | -2.8562 | -0.1808 | 0.000 | 0.0326 |
| `F3_delayed_1_funding_event_16h` | `validation_2025H1` | -0.2059 | -0.6547 | 0.500 | 0.0289 |
| `F3_delayed_1_funding_event_16h` | `recent_oos_2025H2_2026Apr` | 0.3213 | -0.5662 | 0.700 | 0.0313 |
| `F3_delayed_1_funding_event_16h` | `fresh_forward_2026May` | -3.3478 | -0.1491 | 0.000 | 0.0328 |
| `F4_future_next_funding_forbidden_8h` | `validation_2025H1` | 0.3933 | -0.4690 | 0.500 | 0.0285 |
| `F4_future_next_funding_forbidden_8h` | `recent_oos_2025H2_2026Apr` | -1.2058 | -0.7148 | 0.400 | 0.0314 |
| `F4_future_next_funding_forbidden_8h` | `fresh_forward_2026May` | -4.5498 | -0.2183 | 0.000 | 0.0324 |
| `F5_time_shuffled_funding` | `validation_2025H1` | -2.8140 | -0.7574 | 0.167 | 0.3204 |
| `F5_time_shuffled_funding` | `recent_oos_2025H2_2026Apr` | -2.2910 | -0.8545 | 0.200 | 0.3389 |
| `F5_time_shuffled_funding` | `fresh_forward_2026May` | -4.2638 | -0.1777 | 0.000 | 0.3425 |
| `F6_symbol_shuffled_funding` | `validation_2025H1` | -2.8283 | -0.7580 | 0.000 | 0.3233 |
| `F6_symbol_shuffled_funding` | `recent_oos_2025H2_2026Apr` | -2.9149 | -0.9114 | 0.000 | 0.3206 |
| `F6_symbol_shuffled_funding` | `fresh_forward_2026May` | -2.9006 | -0.1250 | 0.000 | 0.3370 |
| `F7_wrong_lag_future_24h` | `validation_2025H1` | 8.8849 | -0.1036 | 1.000 | 0.0307 |
| `F7_wrong_lag_future_24h` | `recent_oos_2025H2_2026Apr` | 5.8783 | -0.1675 | 1.000 | 0.0327 |
| `F7_wrong_lag_future_24h` | `fresh_forward_2026May` | 7.8291 | -0.0225 | 1.000 | 0.0331 |

## Funding Sign / Payment Decomposition

| object | split | ann mean | compounded DD |
|---|---|---:|---:|
| `net_current_long_only` | `validation_2025H1` | 7.4756 | -0.8674 |
| `net_current_long_only` | `recent_oos_2025H2_2026Apr` | 3.3578 | -0.9488 |
| `net_current_long_only` | `fresh_forward_2026May` | -11.1994 | -0.5446 |
| `net_full_signed` | `validation_2025H1` | 7.7537 | -0.8669 |
| `net_full_signed` | `recent_oos_2025H2_2026Apr` | 3.5273 | -0.9457 |
| `net_full_signed` | `fresh_forward_2026May` | -10.9727 | -0.5426 |
| `net_inverted_signed` | `validation_2025H1` | 6.6957 | -0.8717 |
| `net_inverted_signed` | `recent_oos_2025H2_2026Apr` | 3.0180 | -0.9504 |
| `net_inverted_signed` | `fresh_forward_2026May` | -11.4183 | -0.5476 |
| `gross_price_pnl` | `validation_2025H1` | 8.2482 | -0.8648 |
| `gross_price_pnl` | `recent_oos_2025H2_2026Apr` | 4.3082 | -0.9438 |
| `gross_price_pnl` | `fresh_forward_2026May` | -10.0949 | -0.5409 |
| `funding_full_signed_pnl` | `validation_2025H1` | 0.5290 | -0.0012 |
| `funding_full_signed_pnl` | `recent_oos_2025H2_2026Apr` | 0.2547 | -0.0007 |
| `funding_full_signed_pnl` | `fresh_forward_2026May` | 0.2228 | -0.0003 |

## Core4 Residual By Funding Version

| object | split | ann mean | compounded DD |
|---|---|---:|---:|
| `Core4_residual_vs_F1_last_settled_stale_8h` | `validation_2025H1` | 0.3596 | -0.3313 |
| `Core4_residual_vs_F1_last_settled_stale_8h` | `recent_oos_2025H2_2026Apr` | 0.4412 | -0.2601 |
| `Core4_residual_vs_F1_last_settled_stale_8h` | `fresh_forward_2026May` | 0.2832 | -0.0815 |
| `Core4_residual_vs_F2_latest_known_observable` | `validation_2025H1` | 0.1914 | -0.4068 |
| `Core4_residual_vs_F2_latest_known_observable` | `recent_oos_2025H2_2026Apr` | 0.4433 | -0.1492 |
| `Core4_residual_vs_F2_latest_known_observable` | `fresh_forward_2026May` | -0.6414 | -0.0673 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `validation_2025H1` | 0.0177 | -0.3507 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `recent_oos_2025H2_2026Apr` | 0.5627 | -0.1876 |
| `Core4_residual_vs_F4_future_next_funding_forbidden_8h` | `fresh_forward_2026May` | 0.9411 | -0.0519 |

## May 2026 Worst Symbol/Component Rows

| symbol | component | net full signed | price pnl | funding pnl | fee | turnover |
|---|---|---:|---:|---:|---:|---:|
| `BCHUSDT` | `funding_rate_h12` | -0.5290 | -0.5274 | 0.0013 | 0.0030 | 3.0000 |
| `BCHUSDT` | `funding_persistence_h12` | -0.4598 | -0.4591 | 0.0026 | 0.0035 | 3.5000 |
| `BCHUSDT` | `funding_rate_h6` | -0.2211 | -0.2191 | 0.0008 | 0.0030 | 3.0000 |
| `SOLUSDT` | `funding_rate_h12` | -0.2198 | -0.2156 | 0.0010 | 0.0052 | 5.1667 |
| `ADAUSDT` | `funding_persistence_h6` | -0.2174 | -0.2134 | 0.0020 | 0.0062 | 6.1667 |
| `ADAUSDT` | `funding_persistence_h12` | -0.2121 | -0.2094 | 0.0032 | 0.0058 | 5.8333 |
| `LINKUSDT` | `funding_persistence_h6` | -0.1827 | -0.1783 | 0.0004 | 0.0050 | 5.0000 |
| `DOGEUSDT` | `funding_persistence_h12` | -0.1819 | -0.1777 | 0.0003 | 0.0045 | 4.5000 |
| `BCHUSDT` | `funding_persistence_h6` | -0.1641 | -0.1624 | 0.0016 | 0.0035 | 3.5000 |
| `LINKUSDT` | `funding_persistence_h12` | -0.1381 | -0.1341 | 0.0008 | 0.0050 | 5.0000 |
| `AVAXUSDT` | `funding_rate_h12` | -0.1321 | -0.1263 | 0.0016 | 0.0073 | 7.3333 |
| `DOGEUSDT` | `funding_persistence_h6` | -0.1274 | -0.1232 | 0.0003 | 0.0045 | 4.5000 |

## Bias Audit Decision

- This is a linkage/data-semantics audit, not a new alpha search.
- Promotion remains blocked if event detection or funding payment semantics are unresolved.
- A clean result here would only allow further research; it would not imply paper/live readiness.
