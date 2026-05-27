# Crypto A7C FundingCore Narrow Audit

- generated_at: `2026-05-19T13:11:42Z`
- decision: `HOLD_FUNDINGCORE_ALPHA_SHADOW_PROOF`
- status: `fundingcore_research_baseline_only`
- blockers: `['fresh_may_10bp_negative']`
- warnings: `['validation_drawdown_large', 'recent_oos_drawdown_large', 'fresh_may_drawdown_large', 'future_wrong_lag_diagnostic_stronger_than_live_lag']`
- risk_variant: `R3_vol_target_gross_0p5x_cap`
- purge_embargo_bars: `24`

## Candidate Factor Review

- factor_id: `FundingCore_v1`
- provenance: A7B simple baseline, not new search
- operator path: cross-sectional z-score/rank of latest-known funding rate and 3-step funding persistence; top/bottom 3 long-short basket; next-open execution proxy
- data source: Binance core12 futures 1h gold panel plus funding history
- feature family: funding/carry regime
- discovery status: diagnostic/reproduction of A7B baseline, no discovery credit

## FundingCore Fixed-Split Performance

| cost | split | ann mean | compounded DD | month pass | mean gross | mean turnover |
|---|---|---:|---:|---:|---:|---:|
| `normal_5bp` | `validation_2025H1` | 2.2354 | -0.3726 | 0.833 | 0.493 | 0.029 |
| `normal_5bp` | `recent_oos_2025H2_2026Apr` | 1.0654 | -0.6006 | 0.800 | 0.495 | 0.031 |
| `normal_5bp` | `fresh_forward_2026May` | -2.5635 | -0.1779 | 0.000 | 0.500 | 0.033 |
| `stress_10bp` | `validation_2025H1` | 2.1062 | -0.3751 | 0.833 | 0.493 | 0.029 |
| `stress_10bp` | `recent_oos_2025H2_2026Apr` | 0.9279 | -0.6068 | 0.800 | 0.495 | 0.031 |
| `stress_10bp` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 0.000 | 0.500 | 0.033 |
| `severe_20bp` | `validation_2025H1` | 1.8478 | -0.3841 | 0.833 | 0.493 | 0.029 |
| `severe_20bp` | `recent_oos_2025H2_2026Apr` | 0.6529 | -0.6214 | 0.700 | 0.495 | 0.031 |
| `severe_20bp` | `fresh_forward_2026May` | -2.9912 | -0.1809 | 0.000 | 0.500 | 0.033 |

## Placebo / Wrong-Lag Audit

| object | split | ann mean | compounded DD | month pass |
|---|---|---:|---:|---:|
| `sign_flip` | `validation_2025H1` | -1.8432 | -0.7217 | 0.333 |
| `sign_flip` | `recent_oos_2025H2_2026Apr` | -1.7241 | -0.8043 | 0.100 |
| `sign_flip` | `fresh_forward_2026May` | 2.6452 | -0.1674 | 1.000 |
| `wrong_lag_stale_24h` | `validation_2025H1` | 0.6763 | -0.6210 | 0.667 |
| `wrong_lag_stale_24h` | `recent_oos_2025H2_2026Apr` | 0.2146 | -0.5293 | 0.500 |
| `wrong_lag_stale_24h` | `fresh_forward_2026May` | -5.2124 | -0.2170 | 0.000 |
| `wrong_lag_future_24h_diagnostic` | `validation_2025H1` | 8.8223 | -0.1035 | 1.000 |
| `wrong_lag_future_24h_diagnostic` | `recent_oos_2025H2_2026Apr` | 5.8239 | -0.1663 | 1.000 |
| `wrong_lag_future_24h_diagnostic` | `fresh_forward_2026May` | 7.7682 | -0.0224 | 1.000 |
| `row_shuffle` | `validation_2025H1` | -2.0797 | -0.6719 | 0.167 |
| `row_shuffle` | `recent_oos_2025H2_2026Apr` | -2.9323 | -0.9129 | 0.000 |
| `row_shuffle` | `fresh_forward_2026May` | -2.9213 | -0.1231 | 0.000 |
| `time_shuffle` | `validation_2025H1` | -2.4515 | -0.7069 | 0.000 |
| `time_shuffle` | `recent_oos_2025H2_2026Apr` | -2.6523 | -0.8898 | 0.000 |
| `time_shuffle` | `fresh_forward_2026May` | -2.8862 | -0.1221 | 0.000 |

## Component Standalone Audit

| component | split | ann mean | compounded DD | month pass |
|---|---|---:|---:|---:|
| `funding_rate_h6` | `validation_2025H1` | 1.3093 | -0.3549 | 0.667 |
| `funding_rate_h6` | `recent_oos_2025H2_2026Apr` | 0.9113 | -0.4644 | 0.800 |
| `funding_rate_h6` | `fresh_forward_2026May` | -1.9728 | -0.1196 | 0.000 |
| `funding_rate_h12` | `validation_2025H1` | 2.4435 | -0.4894 | 0.500 |
| `funding_rate_h12` | `recent_oos_2025H2_2026Apr` | 1.7619 | -0.6783 | 0.800 |
| `funding_rate_h12` | `fresh_forward_2026May` | -2.9840 | -0.2491 | 0.000 |
| `funding_persistence_h6` | `validation_2025H1` | 1.9951 | -0.3767 | 0.833 |
| `funding_persistence_h6` | `recent_oos_2025H2_2026Apr` | 0.2717 | -0.4509 | 0.600 |
| `funding_persistence_h6` | `fresh_forward_2026May` | -1.1630 | -0.1232 | 0.000 |
| `funding_persistence_h12` | `validation_2025H1` | 2.5909 | -0.5344 | 0.833 |
| `funding_persistence_h12` | `recent_oos_2025H2_2026Apr` | 0.9294 | -0.7236 | 0.600 |
| `funding_persistence_h12` | `fresh_forward_2026May` | -3.7818 | -0.2284 | 0.000 |

## May 2026 Failure Attribution

| object | May total | May ann proxy | worst hour | top3 loss sum | mean turnover |
|---|---:|---:|---:|---:|---:|
| `FundingCore` | -0.0990 | -1.9708 | -0.0081 | -0.0221 | 0.0331 |

## Symbol LOO Summary

- recent_oos_symbol_loo_positive_rate: `1.0`
- recent_oos_symbol_loo_min_ann: `2.1922634631177518`

## Bias Audit Decision

- lookahead: latest-known funding only; A7.0 split/linkage ledger applies
- costs: 5/10/20bps included; 10bps is primary
- OOS: validation, recent OOS, fresh May, symbol LOO
- status: HOLD unless fresh-forward and drawdown issues are cleared

## Interpretation

- FundingCore is a necessary benchmark for crypto reward design.
- This audit does not search, tune, or promote paper/live trading.
- If FundingCore beats Core4 but fails fresh May or drawdown, it remains a research baseline, not an alpha shadow proof.
