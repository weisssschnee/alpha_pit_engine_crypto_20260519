# Crypto A7H-0 Non-Funding Residual Smoke

- generated_at: `2026-05-19T14:40:37Z`
- decision: `PASS_A7H_METHOD_SMOKE_CANDIDATE`
- evidence_level: `method_smoke_only_not_alpha_proof`
- pass_candidate_count: `2`
- candidate_count: `15`

## Contract Boundary

- No search expansion, no formula tuning, no promotion.
- Every candidate is measured raw, residual vs FundingCore, residual vs Core4, and against wrong-lag future funding diagnostic.
- FundingCore/Core4 remain mandatory residual baselines.

## Top Candidate Summary

| candidate | family | val residual funding | recent residual funding | May raw | May residual funding | May residual Core4 | recent funding beta | wrong-lag corr | pass |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `a7h_liquidity_size_h12` | `flow_liquidity` | 1.0254 | 1.5319 | -1.6261 | 0.6827 | 0.1070 | 0.2079 | 0.0994 | `True` |
| `a7h_flow_rank_taker_imbalance_h6` | `flow_liquidity` | 0.4687 | 0.2214 | -2.9743 | 0.5604 | 0.5425 | -0.0353 | -0.0037 | `True` |
| `a7h_micro_ret_range_interaction_h12` | `microstructure_lite` | 4.8546 | 3.9618 | -11.1398 | -5.6207 | -6.1755 | 0.3670 | 0.0604 | `False` |
| `a7h_micro_ret_vol_interaction_h6` | `microstructure_lite` | 1.6216 | 2.6278 | -5.7476 | -1.9402 | -2.3632 | 0.2248 | 0.0522 | `False` |
| `a7h_flow_ret_interaction_h6` | `flow_liquidity` | 1.9880 | 2.0178 | -5.3773 | -0.7019 | -0.8045 | 0.0024 | -0.0856 | `False` |
| `a7h_micro_rank_realized_vol_h12` | `microstructure_lite` | 0.9780 | 1.7287 | -5.9040 | -3.0739 | -3.7500 | 0.5012 | 0.1196 | `False` |
| `a7h_basis_ret_interaction_h6` | `basis_premium` | 1.8338 | 1.6515 | -5.7333 | -2.2261 | -2.0487 | 0.0796 | -0.1361 | `False` |
| `a7h_micro_rank_hl_range_h6` | `microstructure_lite` | 1.4447 | 1.4904 | -3.7426 | 0.4239 | -0.1642 | 0.2590 | 0.1288 | `False` |
| `a7h_micro_rank_absret_h6` | `microstructure_lite` | 0.9552 | 1.0828 | -4.8857 | -0.4028 | -0.7237 | 0.1361 | 0.0918 | `False` |
| `a7h_basis_rank_mark_ratio_h6` | `basis_premium` | 0.6884 | 0.2563 | -3.2153 | -0.6011 | -0.2962 | 0.0668 | -0.1060 | `False` |
| `a7h_basis_z_mark_ratio_h12` | `basis_premium` | 1.5437 | 0.1801 | -4.1961 | -1.7661 | -1.3373 | 0.1154 | -0.0754 | `False` |
| `a7h_flow_rank_quote_volume_h6` | `flow_liquidity` | -0.1014 | -0.0561 | -0.5508 | 0.1471 | -0.0561 | 0.1289 | 0.0658 | `False` |
| `a7h_basis_rank_mark_minus_h6` | `basis_premium` | 0.4367 | -0.1034 | -3.5943 | -3.3228 | -2.8537 | 0.1767 | 0.0172 | `False` |
| `a7h_flow_z_taker_imbalance_h12` | `flow_liquidity` | -0.1271 | -0.2069 | -2.5387 | -0.0418 | -0.0074 | 0.0236 | -0.0103 | `False` |
| `a7h_basis_rank_premium_h12` | `basis_premium` | -0.0024 | -0.4488 | -3.9374 | -2.1175 | -1.7846 | 0.1402 | -0.0603 | `False` |

## Decision

- PASS here only means a non-funding residual candidate exists for further audit.
- HOLD means this fixed non-funding smoke did not find a candidate independent enough from FundingCore/Core4.
- This report does not authorize A7.3, shadow, paper, live, or production claims.
