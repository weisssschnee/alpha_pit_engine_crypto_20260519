# Crypto A7F Funding Regime / Risk Failure Audit

- generated_at: `2026-05-19T13:22:30Z`
- decision: `HOLD_A7F_FUNDING_REGIME_FAILURE_UNRESOLVED`
- blockers: `['predeclared_funding_gate_does_not_clear_fresh_may_failure']`
- warnings: `['core4_still_negative_under_predeclared_funding_gate']`
- risk_variant: `R3_vol_target_gross_0p5x_cap`
- cost_tier: `stress_10bp`

## Scope

No new search, no formula changes, no gate promotion. This audit explains FundingCore/Core4 fresh May failure and tests only predeclared train-threshold gates.

## Gate Replay

| object | gate | split | ann mean | DD | active ratio | active mean | inactive missed mean | month pass |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `FundingCore` | `G0_no_gate` | `validation_2025H1` | 2.1062 | -0.3751 | 1.000 | 0.000240 | 0.000000 | 0.833 |
| `FundingCore` | `G0_no_gate` | `recent_oos_2025H2_2026Apr` | 0.9279 | -0.6068 | 1.000 | 0.000106 | 0.000000 | 0.800 |
| `FundingCore` | `G0_no_gate` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 1.000 | -0.000309 | 0.000000 | 0.000 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `validation_2025H1` | 1.6390 | -0.3922 | 0.976 | 0.000192 | 0.002182 | 0.833 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | 1.0504 | -0.5997 | 0.978 | 0.000123 | -0.000650 | 0.700 |
| `FundingCore` | `G1_avoid_high_funding_abs` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 1.000 | -0.000309 | 0.000000 | 0.000 |
| `FundingCore` | `G6_all_low_risk_intersection` | `validation_2025H1` | 0.9132 | -0.1297 | 0.211 | 0.000493 | 0.000173 | 0.833 |
| `FundingCore` | `G6_all_low_risk_intersection` | `recent_oos_2025H2_2026Apr` | 0.2799 | -0.4525 | 0.342 | 0.000093 | 0.000112 | 0.600 |
| `FundingCore` | `G6_all_low_risk_intersection` | `fresh_forward_2026May` | -0.4269 | -0.0829 | 0.329 | -0.000148 | -0.000388 | 0.000 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `validation_2025H1` | 0.4672 | -0.0384 | 0.024 | 0.002182 | 0.000192 | 0.833 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | -0.1225 | -0.1341 | 0.022 | -0.000650 | 0.000123 | 0.200 |
| `FundingCore` | `G7_inverted_avoid_high_funding_abs` | `fresh_forward_2026May` | 0.0000 | 0.0000 | 0.000 | 0.000000 | -0.000309 | 0.000 |
| `Core4` | `G0_no_gate` | `validation_2025H1` | 1.1978 | -0.4766 | 1.000 | 0.000137 | 0.000000 | 0.500 |
| `Core4` | `G0_no_gate` | `recent_oos_2025H2_2026Apr` | 0.7165 | -0.5099 | 1.000 | 0.000082 | 0.000000 | 0.800 |
| `Core4` | `G0_no_gate` | `fresh_forward_2026May` | -2.6313 | -0.1747 | 1.000 | -0.000300 | 0.000000 | 0.000 |
| `Core4` | `G1_avoid_high_funding_abs` | `validation_2025H1` | 0.7695 | -0.5336 | 0.976 | 0.000090 | 0.002001 | 0.500 |
| `Core4` | `G1_avoid_high_funding_abs` | `recent_oos_2025H2_2026Apr` | 0.8774 | -0.4788 | 0.978 | 0.000102 | -0.000853 | 0.800 |
| `Core4` | `G1_avoid_high_funding_abs` | `fresh_forward_2026May` | -2.6313 | -0.1747 | 1.000 | -0.000300 | 0.000000 | 0.000 |
| `Core4` | `G6_all_low_risk_intersection` | `validation_2025H1` | 0.5982 | -0.1240 | 0.211 | 0.000323 | 0.000087 | 0.667 |
| `Core4` | `G6_all_low_risk_intersection` | `recent_oos_2025H2_2026Apr` | 0.1709 | -0.3443 | 0.342 | 0.000057 | 0.000095 | 0.700 |
| `Core4` | `G6_all_low_risk_intersection` | `fresh_forward_2026May` | -0.3385 | -0.0741 | 0.329 | -0.000117 | -0.000390 | 0.000 |
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
| `basis_abs_mean_bucket` | `high` | `recent_oos_2025H2_2026Apr` | 0.8776 | -0.1288 | 0.515 | 0.0335 |
| `basis_abs_mean_bucket` | `low` | `recent_oos_2025H2_2026Apr` | 4.8696 | -0.0607 | 0.017 | 0.0269 |
| `basis_abs_mean_bucket` | `mid` | `recent_oos_2025H2_2026Apr` | 0.8415 | -0.5953 | 0.468 | 0.0293 |
| `basis_abs_mean_bucket` | `high` | `fresh_forward_2026May` | -4.0560 | -0.1096 | 0.584 | 0.0310 |
| `basis_abs_mean_bucket` | `mid` | `fresh_forward_2026May` | -0.8095 | -0.0913 | 0.416 | 0.0347 |
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
