# Crypto A7J Final Decision Record

- decision: `HOLD_CRYPTO_A7J_NO_RESEARCH_CANDIDATE`
- generated_at: `2026-05-20`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- shadow_status: `NOT_AUTHORIZED`
- paper_status: `NOT_AUTHORIZED`
- live_status: `NOT_AUTHORIZED`

## Stage Results

| stage | decision | meaning |
|---|---|---|
| A7J-0 | `PASS_A7J0_FAILURE_MODE_TO_REWARD_CONTRACT` | A7I failure modes were translated into reward/generator constraints. May is stress-only. |
| A7J-1 | `PASS_A7J1_REDESIGNED_RUNNER_PREFLIGHT` | Known objects classify correctly; May is excluded from score/ranking/selection. |
| A7J-2 | `HOLD_A7J2_INSUFFICIENT_RESEARCH_CANDIDATES` | Same-budget redesigned smoke produced 0 research candidates and 0 placebo candidates. |

## A7J-2 Summary

- candidate pool: `A7I1B frozen 1000-candidate pool`
- arms: `4`
- generated per arm: `250`
- selected per arm: `64`
- total selected: `256`
- research candidates: `0`
- placebo research candidates: `0`
- non-flow research candidates: `0`

Arm result:

| arm | selected | research | clue_only |
|---|---:|---:|---:|
| I0_basis_premium | 64 | 0 | 12 |
| I1_flow_liquidity | 64 | 0 | 64 |
| I2_microstructure_lite | 64 | 0 | 64 |
| I3_placebo_random | 64 | 0 | 0 |

Dominant rejection reasons:

- `may_stress_severe_fail`: 139
- `cost20_recent_negative`: 122
- `may_residual_funding_negative`: 119
- `lag1_recent_negative`: 89
- `raw_recent_nonpositive`: 84
- `raw_validation_nonpositive`: 71
- `raw_validation_insufficient_gross_exposure`: 52
- `raw_recent_insufficient_gross_exposure`: 52

## Interpretation

A7J succeeded as a validation redesign: it removed the false A7J-2 spot-basis zero-activity passes by requiring sample/activity coverage, kept May out of ranking, and prevented placebo promotion.

A7J failed as an alpha discovery smoke: under the stricter cost/lag/residual/activity gates, the frozen 1000-candidate pool contains no research candidate.

## Final Boundary

A7J does not authorize:

- alpha proof
- A7.3 generator bakeoff promotion
- dry-shadow alpha evidence
- paper trading
- live trading
- production claims

## Next Valid Work

Do not expand the same generator budget immediately. The valid next step is:

`A7K_GENERATOR_SPACE_REDESIGN_OR_FORWARD_WAIT`

Two acceptable branches:

1. Redesign generator space away from current weak families:
   - remove zero-activity spot-basis artifacts unless coverage is explicit;
   - add pre-selection coverage/activity gates;
   - add cost20 and lag1 robustness before replay selection;
   - keep May stress-only.

2. Freeze the A7J runner/reward contract and wait for append-only data:
   - use future data after contract freeze as proof input;
   - do not use May 2026 as fresh proof.

Until one branch passes, crypto remains a research-method line with no validated alpha object.
