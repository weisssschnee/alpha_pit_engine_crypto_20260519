# Crypto A7L-1 Search-Space Redesign Spec

- generated_at: `2026-05-20T00:12:30Z`
- decision: `PASS_A7L1_SEARCH_SPACE_REDESIGN_SPEC`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7l1b_implementation_preflight: `True`
- authorizes_budget_ladder_level1: `False`
- stable_contract_hash: `2c7d20285d9064ee1be2099136a94b3cff52d1119caf55af38f22b55995e5c2a`

## Source State

- A7L-0 decision: `HOLD_A7L0_BUDGET_LADDER_NOT_AUTHORIZED`
- A7L-0 blockers: `['a7k_preselection_pass_rate_below_10pct', 'a7k_zero_research_candidates', 'a7k_selected_candidates_may_failure_too_homogeneous']`

A7K did not falsify broader crypto formula search. It falsified the current narrow generator/gate combination and blocked same-generator blind budget expansion.

## Boundary

- May 2026 remains a known adversarial stress set.
- May is forbidden in ranking, reward, thresholds, weights, candidate selection, and generator tuning.
- A7L-1 only authorizes implementation preflight, not level-1 budget ladder search.

## Proposed Arms

| arm | purpose | primary families | blocked patterns |
|---|---|---|---|
| `L0_cost_aware_low_turnover` | Generate structures whose first objective is 20bps and 1bar-lag survival, not raw recent return. | `price;volatility;liquidity` | `high_turnover_near_close_edge;residual_only_hedge;zero_activity` |
| `L1_residual_orthogonal_basis` | Explore basis/premium expressions with mandatory residual value beyond FundingCore/Core4. | `basis;price;volatility;liquidity` | `spot_perp_basis_without_core6_lane;funding_beta_wrapper;basis_zero_activity` |
| `L2_cross_symbol_relative` | Test cross-symbol relative strength, dispersion, and crowding instead of single-field directional carry. | `cross_symbol;price;volatility;liquidity;basis` | `single_symbol_proxy;future_universe;current_constituent_survivorship` |
| `L3_regime_conditional_no_may` | Generate validation/recent-defined regime-conditioned candidates without using May for tuning. | `regime;volatility;liquidity;basis;price` | `may_tuned_gate;may_selected_threshold;too_low_active_ratio` |
| `L4_microstructure_lite_lag_stable` | Retest flow/volume/volatility interactions only when they survive 1bar lag and cost stress. | `flow;liquidity;volatility;price` | `taker_standalone;lag_fragile_flow;May_only_rescue` |
| `L5_placebo_random_control` | Negative control arm that must not produce comparable research candidates. | `placebo` | `any_research_candidate_is_blocker` |

## Budget Ladder

| level | generated_total | status | hard stop |
|---|---:|---|---|
| `L0_observed` | 1000 | `completed_hold` | A7L0 blockers remain unresolved |
| `L1_small_ladder` | 4000 | `not_authorized_until_A7L1B` | unique_expr_ratio<0.90 or preselection_rate<0.10 or placebo_research>0 |
| `L2_medium_ladder` | 16000 | `not_authorized` | cluster diversity stalls or selected May severe fail remains homogeneous |
| `L3_large_ladder` | 64000 | `not_authorized` | L2 repeats A7K failure modes |

## Level-1 Stop Rules

- unique expression ratio >= `0.9`
- field-family combo count >= `24`
- operator combo count >= `12`
- non-May preselection pass rate >= `0.1`
- placebo research candidates must remain 0.
- near-miss pool must be non-placebo, diverse, and not only flow/taker.
- return-corr cluster diversity must grow with budget.

## Decision

A7L-1 passes as a search-space redesign spec. It does not authorize a 4000-candidate run. The next valid work is A7L-1B implementation preflight.
