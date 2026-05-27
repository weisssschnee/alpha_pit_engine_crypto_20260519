# Crypto A7I-1b Matched-Budget Smoke

- generated_at: `2026-05-19T16:19:08Z`
- decision: `HOLD_A7I1_INSUFFICIENT_RESEARCH_CANDIDATES`
- executes_search: `True`
- generated_per_arm: `250`
- replay_selected_per_arm: `64`
- authorizes_alpha_proof: `False`
- blockers: `['fewer_than_2_non_placebo_research_candidates']`

## Arm Summary

| arm | generated | selected | research candidates |
|---|---:|---:|---:|
| `I0_basis_premium` | 250 | 64 | 0 |
| `I1_flow_liquidity` | 250 | 64 | 0 |
| `I2_microstructure_lite` | 250 | 64 | 1 |
| `I3_placebo_random` | 250 | 64 | 0 |

## Research Candidate Shortlist

| candidate | arm | family | rank score | expression |
|---|---|---|---:|---|
| `i2_microstructure_lite_113` | `I2_microstructure_lite` | `microstructure_lite` | 1.846817 | `Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))` |

## Decision Boundary

- PASS_A7I1_METHOD_SMOKE would only produce A7I_RESEARCH_CANDIDATE objects.
- This report never authorizes alpha proof, shadow, paper, or live.
- `symbol_month_loo` is an explicit placeholder in this smoke and must be run before alpha proof.
