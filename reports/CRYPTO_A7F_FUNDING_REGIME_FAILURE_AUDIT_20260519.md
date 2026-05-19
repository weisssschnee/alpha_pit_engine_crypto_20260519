# Crypto A7F Funding Regime / Risk Failure Audit

- generated_at: `2026-05-19T13:50:57Z`
- decision: `HOLD_A7F_FUNDING_REGIME_FAILURE_UNRESOLVED`
- blockers: `['predeclared_funding_gate_does_not_clear_fresh_may_failure']`
- warnings: `['core4_still_negative_under_predeclared_funding_gate']`
- risk_variant: `R3_vol_target_gross_0p5x_cap`
- cost_tier: `stress_10bp`

## Scope

No new search, no formula changes, no gate promotion. This audit explains FundingCore/Core4 fresh May failure and tests only predeclared train-threshold gates.

Regime basis proxy uses corrected `basis_abs_mean = abs(mark_index_ratio)`. `mark_index_ratio` is already centered as `mark_close / index_close - 1.0`.

## Gate Replay

| object | gate | split | ann mean | DD | active ratio | active mean | inactive missed mean | month pass |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `FundingCore` | `G0_no_gate` | `validation_2025H1` | 2.1062 | -0.3751 | 1.000 | 0.000240 | 0.000000 | 0.833 |
| `FundingCore` | `G0_no_gate` | `recent_oos_2025H2_2026Apr` | 0.9279 | -0.6068 | 1.000 | 0.000106 | 0.000000 | 0.800 |
| `FundingCore` | `G0_no_gate` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 1.000 | -0.000309 | 0.000000 | 0.000 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `validation_2025H1` | 1.6390 | -0.3922 | 0.976 | 0.000192 | 0.002182 | 0.833 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | 1.0504 | -0.5997 | 0.978 | 0.000123 | -0.000650 | 0.700 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 1.000 | -0.000309 | 0.000000 | 0.000 |
| `FundingCore` | `G6_all_low_risk_intersection` | `validation_2025H1` | 1.1177 | -0.3409 | 0.517 | 0.000247 | 0.000233 | 0.667 |
| `FundingCore` | `G6_all_low_risk_intersection` | `recent_oos_2025H2_2026Apr` | 0.5870 | -0.4810 | 0.572 | 0.000117 | 0.000091 | 0.700 |
| `FundingCore` | `G6_all_low_risk_intersection` | `fresh_forward_2026May` | -1.6811 | -0.1282 | 0.574 | -0.000334 | -0.000275 | 0.000 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `validation_2025H1` | 0.4672 | -0.0384 | 0.024 | 0.002182 | 0.000192 | 0.833 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | -0.1225 | -0.1341 | 0.022 | -0.000650 | 0.000123 | 0.200 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `fresh_forward_2026May` | 0.0000 | 0.0000 | 0.000 | 0.000000 | -0.000309 | 0.000 |
| `Core4` | `G0_no_gate` | `validation_2025H1` | 1.1978 | -0.4766 | 1.000 | 0.000137 | 0.000000 | 0.500 |
| `Core4` | `G0_no_gate` | `recent_oos_2025H2_2026Apr` | 0.7165 | -0.5099 | 1.000 | 0.000082 | 0.000000 | 0.800 |
| `Core4` | `G0_no_gate` | `fresh_forward_2026May` | -2.6313 | -0.1747 | 1.000 | -0.000300 | 0.000000 | 0.000 |
| `Core4` | `G1_avoid_high_funding_abs` | `validation_2025H1` | 0.7695 | -0.5336 | 0.976 | 0.000090 | 0.002001 | 0.500 |
| `Core4` | `G1_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | 0.8774 | -0.4788 | 0.978 | 0.000102 | -0.000853 | 0.800 |
| `Core4` | `G1_avoid_high_funding_abs` | `fresh_forward_2026May` | -2.6313 | -0.1747 | 1.000 | -0.000300 | 0.000000 | 0.000 |
| `Core4` | `G6_all_low_risk_intersection` | `validation_2025H1` | 0.7175 | -0.3803 | 0.517 | 0.000159 | 0.000113 | 0.500 |
| `Core4` | `G6_all_low_risk_intersection` | `recent_oos_2025H2_2026Apr` | 0.3693 | -0.3720 | 0.572 | 0.000074 | 0.000093 | 0.700 |
| `Core4` | `G6_all_low_risk_intersection` | `fresh_forward_2026May` | -1.4633 | -0.1205 | 0.574 | -0.000291 | -0.000313 | 0.000 |
| `Core4` | `G7_inverted_avoid_high_funding_abs` | `validation_2025H1` | 0.4284 | -0.0205 | 0.024 | 0.002001 | 0.000090 | 0.833 |
| `Core4` | `G7_inverted_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | -0.1609 | -0.1343 | 0.022 | -0.000853 | 0.000102 | 0.200 |
| `Core4` | `G7_inverted_avoid_high_funding_abs` | `fresh_forward_2026May` | 0.0000 | 0.0000 | 0.000 | 0.000000 | -0.000300 | 0.000 |

## FundingCore Bucket Replay

| bucket field | bucket | split | ann mean | DD | active ratio | turnover |
|---|---|---|---:|---:|---:|---:|
| `funding_abs_mean_bucket` | `high` | `recent_oos_2025H2_2026Apr` | -5.6933 | -0.1341 | 0.022 | 0.0353 |
| `funding_abs_mean_bucket` | `low` | `recent_oos_2025H2_2026Apr` | 1.6556 | -0.2335 | 0.771 | 0.0328 |
| `funding_abs_mean_bucket` | `mid` | `recent_oos_2025H2_2026Apr` | -1.0837 | -0.5182 | 0.208 | 0.0257 |
| `funding_abs_mean_bucket` | `low` | `fresh_forward_2026May` | -1.6783 | -0.1393 | 0.916 | 0.0335 |
| `funding_abs_mean_bucket` | `mid` | `fresh_forward_2026May` | -13.8863 | -0.0529 | 0.084 | 0.0228 |
| `basis_abs_mean_bucket` | `high` | `recent_oos_2025H2_2026Apr` | -0.3456 | -0.1189 | 0.211 | 0.0367 |
| `basis_abs_mean_bucket` | `low` | `recent_oos_2025H2_2026Apr` | 0.0591 | -0.5028 | 0.273 | 0.0266 |
| `basis_abs_mean_bucket` | `mid` | `recent_oos_2025H2_2026Apr` | 1.9101 | -0.1993 | 0.516 | 0.0318 |
| `basis_abs_mean_bucket` | `high` | `fresh_forward_2026May` | -3.1241 | -0.0485 | 0.293 | 0.0274 |
| `basis_abs_mean_bucket` | `low` | `fresh_forward_2026May` | 2.6863 | -0.0218 | 0.089 | 0.0323 |
| `basis_abs_mean_bucket` | `mid` | `fresh_forward_2026May` | -3.2873 | -0.1223 | 0.617 | 0.0350 |
| `vol_ret12_abs_mean_bucket` | `high` | `recent_oos_2025H2_2026Apr` | 1.4767 | -0.2523 | 0.278 | 0.0321 |
| `vol_ret12_abs_mean_bucket` | `low` | `recent_oos_2025H2_2026Apr` | 0.3060 | -0.3369 | 0.448 | 0.0312 |
| `vol_ret12_abs_mean_bucket` | `mid` | `recent_oos_2025H2_2026Apr` | 1.3892 | -0.2622 | 0.274 | 0.0310 |
| `vol_ret12_abs_mean_bucket` | `high` | `fresh_forward_2026May` | -0.7896 | -0.0369 | 0.173 | 0.0322 |
| `vol_ret12_abs_mean_bucket` | `low` | `fresh_forward_2026May` | -2.9859 | -0.1404 | 0.587 | 0.0358 |
| `vol_ret12_abs_mean_bucket` | `mid` | `fresh_forward_2026May` | -3.4078 | -0.0529 | 0.240 | 0.0249 |

## Random Active-Hour Placebo

| split | reference gate | iterations | mean ann | p95 ann |
|---|---|---:|---:|---:|
| `fresh_forward_2026May` | `G1_avoid_high_funding_abs` | 200 | -2.3074 | -1.6559 |
| `recent_oos_2025H2_2026Apr` | `G1_avoid_high_funding_abs` | 200 | 0.7878 | 0.9355 |

## Decision

- Passing A7F would only justify further regime/risk research.
- It does not promote FundingCore/Core4 to shadow proof.
- Generator bakeoff remains blocked while fresh-forward failure and drawdown remain unresolved.
