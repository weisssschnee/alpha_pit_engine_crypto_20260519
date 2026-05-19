# Crypto A7K-0 Generator-Space Redesign Contract

- generated_at: `2026-05-19T17:38:13Z`
- decision: `PASS_A7K0_GENERATOR_SPACE_REDESIGN_CONTRACT`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7k1: `True`
- authorizes_a7k2: `False`
- authorizes_alpha_proof: `False`
- stable_contract_hash: `78ec7710a6c028b7726e711b697c20eedb2497294ec7ecbbe7172b61556758df`

## Boundary

- A7J is frozen as method success / alpha discovery failure.
- A7K cannot expand the same generator budget directly.
- May 2026 remains stress-only and cannot enter ranking, reward, threshold tuning, candidate selection, or generator tuning.

## Generator Space

| arm | status | key required gate |
|---|---|---|
| `K0_basis_premium_clean` | `allowed_with_coverage_and_residual_gates` | `basis_field_contract_centered, core12_coverage_or_explicit_core6_lane, residual_vs_fundingcore` |
| `K1_flow_liquidity_clean` | `allowed_but_not_taker_standalone` | `raw_viability_before_residual_credit, cost20_survival, lag1_survival` |
| `K2_microstructure_lite_latency_robust` | `allowed_with_execution_lag_gate` | `execution_lag1_validation_recent_nonnegative, cost20_validation_recent_nonnegative, top_loss_concentration_audit` |
| `K3_placebo_random_control` | `mandatory_negative_control` | `zero_research_candidate` |

## Preselection Gates

- Coverage/activity gate rejects zero-activity and low-exposure candidates before selection.
- Raw validation/recent, 20bps validation/recent, and 1bar-lag validation/recent must be viable before research labeling.
- Residual vs FundingCore/Core4 is mandatory, but residual-only hedge clues are not standalone alphas.

## Next

Run A7K-1 generator-space preflight. Do not run A7K-2 until A7K-1 confirms coverage/activity, cost/lag, residual, family diversity, and May-exclusion checks.
