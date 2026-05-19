# Crypto A7K Final Decision Record

- decision: `HOLD_CRYPTO_A7K_NO_ALPHA_PROOF`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- shadow_paper_live_status: `NOT_AUTHORIZED`
- same_generator_budget_expansion: `NOT_RECOMMENDED`

## Stage Results

| stage | decision | role |
|---|---|---|
| `A7K-0` | `PASS_A7K0_GENERATOR_SPACE_REDESIGN_CONTRACT` | freezes the generator-space redesign contract |
| `A7K-1` | `HOLD_A7K1_PREFLIGHT_BLOCKED` | old A7I/A7J pool still has family-concentrated pass-through |
| `A7K-1B` | `PASS_A7K1B_NEW_SPACE_GENERATOR_IMPL_PREFLIGHT` | new static generator implementation passes coverage, dedup, family quota, and May-exclusion checks |
| `A7K-2` | `HOLD_A7K2_INSUFFICIENT_RESEARCH_CANDIDATES` | new-space same-budget smoke produces zero research candidates |

## A7K-2 Key Numbers

- generated: `1000`
- selected after non-May preselection: `64`
- research_candidate_count: `0`
- placebo_research_candidate_count: `0`
- non_flow_research_candidate_count: `0`

Arm summary:

| arm | generated | preselection pass | selected | research | clue only | shortfall |
|---|---:|---:|---:|---:|---:|---:|
| `K0_basis_premium_clean` | 250 | 3 | 3 | 0 | 3 | 61 |
| `K1_flow_liquidity_clean` | 250 | 28 | 28 | 0 | 28 | 36 |
| `K2_microstructure_lite_latency_robust` | 250 | 33 | 33 | 0 | 33 | 31 |
| `K3_placebo_random_control` | 250 | 0 | 0 | 0 | 0 | 64 |

The only selected non-placebo candidates are `clue_only`. Final veto reasons are broad:

- `may_stress_severe_fail`: 64
- `may_residual_funding_negative`: 64

May is not used for ranking or selection. It is applied only after selection as stress/veto labeling.

## Confirmed

- The A7K static generator can avoid the A7J zero-activity and duplicate-formula implementation failure.
- The A7K static generator can enforce family quota before evaluation.
- The May boundary remains intact.
- The placebo arm does not produce research candidates.
- The new generator space still does not produce crypto alpha proof under the current strict gates.

## Blockers

- `fewer_than_2_non_placebo_research_candidates`
- `no_non_flow_non_taker_research_candidate`
- `arm_preselection_shortfall`
- broad May stress failure among the selected clue-only candidates

## Not Authorized

- alpha proof
- dry-shadow alpha evidence
- paper trading
- live trading
- production
- old A7.3 bakeoff
- expanded same-generator budget search

## Next Valid Paths

1. `A7L_SEARCH_SPACE_COVERAGE_AND_SCALING_LAW_AUDIT`: measure grammar, feature-family, horizon, diversity, and gate-attrition coverage before any larger run.
2. `FORWARD-WAIT`: freeze the A7J/A7K contracts and wait for truly new append-only data after the contract freeze.
3. `DATA_OR_FEATURE_LAYER_RETHINK`: inspect whether the current 1h OHLCV/funding/basis feature set is structurally insufficient. Potential future work must preserve May stress-only and must include a new preflight before any smoke.

Current recommendation: stop same-generator blind budget expansion. Do not treat A7K as evidence that broader crypto formula search is exhausted. A7K shows the validation framework is functioning and that the current narrow 1h feature/generator distribution is weak under strict gates.
