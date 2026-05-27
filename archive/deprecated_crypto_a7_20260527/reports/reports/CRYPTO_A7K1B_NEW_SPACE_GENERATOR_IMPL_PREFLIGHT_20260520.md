# Crypto A7K-1B New-Space Generator Implementation Preflight

- generated_at: `2026-05-19T18:03:22Z`
- decision: `PASS_A7K1B_NEW_SPACE_GENERATOR_IMPL_PREFLIGHT`
- evidence_level: `generator_implementation_preflight_not_alpha_proof`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7k2_same_budget_smoke: `True`
- authorizes_alpha_proof: `False`
- blockers: `[]`

## Arm Counts

| arm | generated |
|---|---:|
| `K0_basis_premium_clean` | 250 |
| `K1_flow_liquidity_clean` | 250 |
| `K2_microstructure_lite_latency_robust` | 250 |
| `K3_placebo_random_control` | 250 |

## Feature Coverage

| feature | coverage_all | symbols >=95% | core12 pass |
|---|---:|---:|---:|
| `avg_trade_size_quote` | 1.0000 | 12/12 | `True` |
| `hl_range` | 1.0000 | 12/12 | `True` |
| `mark_index_ratio` | 1.0000 | 12/12 | `True` |
| `mark_minus_index` | 1.0000 | 12/12 | `True` |
| `number_of_trades` | 1.0000 | 12/12 | `True` |
| `premium_index` | 1.0000 | 12/12 | `True` |
| `quote_asset_volume` | 1.0000 | 12/12 | `True` |
| `quote_volume_mean_12` | 1.0000 | 12/12 | `True` |
| `quote_volume_mean_24` | 1.0000 | 12/12 | `True` |
| `realized_vol_12` | 0.9997 | 12/12 | `True` |
| `realized_vol_24` | 0.9994 | 12/12 | `True` |
| `realized_vol_6` | 0.9999 | 12/12 | `True` |
| `ret_12` | 0.9994 | 12/12 | `True` |
| `ret_24` | 0.9988 | 12/12 | `True` |
| `ret_3` | 0.9999 | 12/12 | `True` |
| `ret_6` | 0.9997 | 12/12 | `True` |
| `taker_imbalance` | 1.0000 | 12/12 | `True` |

## Family Quota

| scope | family | count | share | cap | pass |
|---|---|---:|---:|---:|---:|
| `generated_pool` | `basis_premium_clean` | 250 | 0.2500 | 0.25 | `True` |
| `generated_pool` | `flow_liquidity_clean` | 250 | 0.2500 | 0.25 | `True` |
| `generated_pool` | `microstructure_lite_latency_robust` | 250 | 0.2500 | 0.25 | `True` |
| `generated_pool` | `placebo_random_control` | 250 | 0.2500 | 0.25 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;liquidity` | 20 | 0.0800 | 0.50 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;liquidity;price` | 36 | 0.1440 | 0.50 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;liquidity;volatility` | 24 | 0.0960 | 0.50 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;price` | 77 | 0.3080 | 0.50 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;price;volatility` | 57 | 0.2280 | 0.50 | `True` |
| `K0_basis_premium_clean_field_family_combo` | `basis;volatility` | 36 | 0.1440 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `basis;liquidity` | 40 | 0.1600 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `basis;liquidity;price` | 36 | 0.1440 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `basis;liquidity;volatility` | 34 | 0.1360 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `liquidity;price` | 50 | 0.2000 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `liquidity;price;volatility` | 40 | 0.1600 | 0.50 | `True` |
| `K1_flow_liquidity_clean_field_family_combo` | `liquidity;volatility` | 50 | 0.2000 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `basis;liquidity;volatility` | 31 | 0.1240 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `basis;price;volatility` | 33 | 0.1320 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `basis;volatility` | 24 | 0.0960 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `liquidity;price;volatility` | 54 | 0.2160 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `liquidity;volatility` | 54 | 0.2160 | 0.50 | `True` |
| `K2_microstructure_lite_latency_robust_field_family_combo` | `price;volatility` | 54 | 0.2160 | 0.50 | `True` |
| `K3_placebo_random_control_field_family_combo` | `basis` | 52 | 0.2080 | 0.50 | `True` |
| `K3_placebo_random_control_field_family_combo` | `flow` | 50 | 0.2000 | 0.50 | `True` |
| `K3_placebo_random_control_field_family_combo` | `liquidity` | 48 | 0.1920 | 0.50 | `True` |
| `K3_placebo_random_control_field_family_combo` | `price` | 52 | 0.2080 | 0.50 | `True` |
| `K3_placebo_random_control_field_family_combo` | `volatility` | 48 | 0.1920 | 0.50 | `True` |

## Boundary

- This is a static implementation preflight only.
- It does not evaluate returns and does not create research candidates.
- May remains stress-only and is absent from candidate generation.
