# Crypto A7B Funding Baseline Audit

- generated_at: `2026-05-19T13:11:46Z`
- decision: `HOLD_A7B_FUNDING_BASELINE_DOMINANCE_RISK`
- blockers: `['Core4_recent_not_above_funding_only', 'Core4_validation_not_above_funding_only']`
- risk_variant: `R3_vol_target_gross_0p5x_cap`

## 10bps Baseline Comparison

| object | split | ann mean | compounded DD | month pass | mean gross | mean turnover |
|---|---|---:|---:|---:|---:|---:|
| `B0_Core4` | `validation_2025H1` | 1.1978 | -0.4766 | 0.500 | 0.500 | 0.097 |
| `B0_Core4` | `recent_oos_2025H2_2026Apr` | 0.7165 | -0.5099 | 0.800 | 0.500 | 0.100 |
| `B0_Core4` | `fresh_forward_2026May` | -2.6313 | -0.1747 | 0.000 | 0.500 | 0.096 |
| `B1_funding_only` | `validation_2025H1` | 2.1062 | -0.3751 | 0.833 | 0.493 | 0.029 |
| `B1_funding_only` | `recent_oos_2025H2_2026Apr` | 0.9279 | -0.6068 | 0.800 | 0.495 | 0.031 |
| `B1_funding_only` | `fresh_forward_2026May` | -2.7061 | -0.1789 | 0.000 | 0.500 | 0.033 |
| `B2_price_only` | `validation_2025H1` | -1.3961 | -0.5280 | 0.167 | 0.500 | 0.141 |
| `B2_price_only` | `recent_oos_2025H2_2026Apr` | -1.2513 | -0.6477 | 0.000 | 0.500 | 0.157 |
| `B2_price_only` | `fresh_forward_2026May` | -1.3675 | -0.1144 | 0.000 | 0.500 | 0.152 |
| `B3_basis_only` | `validation_2025H1` | 0.0920 | -0.3597 | 0.333 | 0.500 | 0.172 |
| `B3_basis_only` | `recent_oos_2025H2_2026Apr` | -0.9534 | -0.5742 | 0.200 | 0.500 | 0.141 |
| `B3_basis_only` | `fresh_forward_2026May` | -3.8952 | -0.1636 | 0.000 | 0.500 | 0.142 |
| `B4_price_x_funding` | `validation_2025H1` | 1.1003 | -0.5494 | 0.667 | 0.500 | 0.090 |
| `B4_price_x_funding` | `recent_oos_2025H2_2026Apr` | 0.5867 | -0.4975 | 0.700 | 0.500 | 0.100 |
| `B4_price_x_funding` | `fresh_forward_2026May` | -2.3769 | -0.1734 | 0.000 | 0.500 | 0.094 |
| `B5_basis_x_funding` | `validation_2025H1` | 1.3119 | -0.3892 | 0.667 | 0.496 | 0.102 |
| `B5_basis_x_funding` | `recent_oos_2025H2_2026Apr` | 0.8406 | -0.5335 | 0.800 | 0.499 | 0.102 |
| `B5_basis_x_funding` | `fresh_forward_2026May` | -2.9161 | -0.1800 | 0.000 | 0.500 | 0.099 |
| `B6_Core4_residual_vs_funding` | `validation_2025H1` | 0.1050 | -0.4152 | 0.667 | 0.500 | 0.097 |
| `B6_Core4_residual_vs_funding` | `recent_oos_2025H2_2026Apr` | 0.3550 | -0.1540 | 0.700 | 0.500 | 0.100 |
| `B6_Core4_residual_vs_funding` | `fresh_forward_2026May` | -0.7373 | -0.0684 | 0.000 | 0.500 | 0.096 |

## May Failure Attribution

| object | May total | May ann proxy | worst hour | top3 loss sum | mean turnover |
|---|---:|---:|---:|---:|---:|
| `B0_Core4` | -0.1156 | -2.3013 | -0.0072 | -0.0196 | 0.0960 |
| `B1_funding_only` | -0.0990 | -1.9708 | -0.0081 | -0.0221 | 0.0331 |
| `B2_price_only` | -0.0811 | -1.6153 | -0.0071 | -0.0190 | 0.1496 |
| `B3_basis_only` | -0.1388 | -2.7626 | -0.0121 | -0.0286 | 0.1389 |
| `B4_price_x_funding` | -0.1069 | -2.1281 | -0.0074 | -0.0203 | 0.0927 |
| `B5_basis_x_funding` | -0.1252 | -2.4926 | -0.0070 | -0.0201 | 0.1001 |
| `B6_Core4_residual_vs_funding` | -0.0434 | -0.8637 | -0.0046 | -0.0113 | 0.0960 |

## Interpretation

- If Core4 does not beat funding-only under the same R3 scaling and costs, it cannot be promoted as independent alpha proof.
- Residual vs funding is computed using train-period linear residualization only.
- This audit does not search or tune new formulas.
