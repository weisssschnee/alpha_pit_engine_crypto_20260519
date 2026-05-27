# Crypto A7I-1c Failure Attribution

- generated_at: `2026-05-19T16:42:56Z`
- decision: `HOLD_A7I1C_MAY_STRESS_BROAD_FAIL`
- executes_search: `False`
- authorizes_alpha_proof: `False`
- generated_count: `1000`
- selected_count: `256`
- research_candidate_count: `1`
- placebo_research_candidate_count: `0`
- dominant_selected_reject_reason: `raw_may_severely_negative`
- unique_candidate_fragile: `True`

## Funnel By Arm

| arm | generated | selected | research | median score |
|---|---:|---:|---:|---:|
| `I0_basis_premium` | 250 | 64 | 0 | -2.7709 |
| `I1_flow_liquidity` | 250 | 64 | 0 | -5.0071 |
| `I2_microstructure_lite` | 250 | 64 | 1 | -1.5664 |
| `I3_placebo_random` | 250 | 64 | 0 | -6.4713 |

## Top Selected Reject Reasons

| arm | reason | count |
|---|---|---:|
| `I1_flow_liquidity` | `raw_may_severely_negative` | 64 |
| `I3_placebo_random` | `placebo_arm` | 64 |
| `I2_microstructure_lite` | `raw_may_severely_negative` | 63 |
| `I0_basis_premium` | `raw_recent_nonpositive` | 62 |
| `I2_microstructure_lite` | `raw_validation_nonpositive` | 55 |
| `I0_basis_premium` | `raw_validation_nonpositive` | 54 |
| `I2_microstructure_lite` | `residual_funding_may_negative` | 54 |
| `I1_flow_liquidity` | `residual_funding_may_negative` | 52 |
| `I2_microstructure_lite` | `raw_recent_nonpositive` | 47 |
| `I0_basis_premium` | `raw_may_severely_negative` | 44 |
| `I2_microstructure_lite` | `cost20_recent_collapse` | 41 |
| `I0_basis_premium` | `residual_funding_may_negative` | 40 |

## Single Candidate Fragility

| candidate | expression | raw May | 20bps recent | lag May | notes |
|---|---|---:|---:|---:|---|
| `i2_microstructure_lite_113` | `Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))` | -0.4979 | -0.2332 | -1.0388 | `raw_may_near_severe_cutoff;cost20_recent_negative;lag_may_below_minus_1` |

## Interpretation

- A7I-1b did not fail because placebo contaminated the run; placebo research candidates remain zero.
- The blocker is insufficient non-placebo candidate count.
- The only surviving candidate is near the May severe cutoff and weak under 20bps / lag stress, so it is not ready for promotion.

## Decision Boundary

- This attribution does not authorize alpha proof, shadow, paper, or live.
- Next valid step is a narrow A7I-2 deep audit only if the single microstructure-lite clue is worth inspecting.
