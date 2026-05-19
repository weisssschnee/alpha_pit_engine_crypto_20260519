# Crypto A7I Final Decision Record

- decision: `HOLD_CRYPTO_A7I_NO_ALPHA_PROOF`
- generated_at: `2026-05-20`
- scope: `residual-aware small generator method smoke`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- shadow_status: `NOT_AUTHORIZED`
- paper_status: `NOT_AUTHORIZED`
- live_status: `NOT_AUTHORIZED`

## Stage Results

| stage | decision | meaning |
|---|---|---|
| A7I-0 | `PASS_A7I0_RUNNER_CONTRACT_AUDIT` | Contract terms are explicit; May 2026 is a known adversarial stress set, not ranking input. |
| A7I-1a | `PASS_A7I1A_RUNNER_PREFLIGHT` | Runner mechanics passed: May columns do not affect ranking/selection; residualization and lag stress are wired. |
| A7I-1b | `HOLD_A7I1_INSUFFICIENT_RESEARCH_CANDIDATES` | Matched-budget smoke produced only 1 non-placebo research candidate; placebo produced 0. |
| A7I-1c | `HOLD_A7I1C_MAY_STRESS_BROAD_FAIL` | Failure attribution shows broad May stress failure and weak candidate depth, not placebo contamination. |
| A7I-2 | `HOLD_A7I2_COST_LAG_MAY_FRAGILE` | The only survivor is fragile under May, 20bps cost, and 1bar lag stress. |

## What A7I Confirmed

- Placebo arm did not produce comparable candidates.
- May 2026 was successfully isolated from ranking and replay selection.
- Residual-aware runner can classify FundingCore/Core4/taker/placebo objects according to contract.
- The current small generator set does not trivially hallucinate alpha under the stricter A7I gate.

## What A7I Rejected

- `i2_microstructure_lite_113` is not promoted.
- Expression: `Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))`
- Reason: positive validation/recent 10bps and positive residual-vs-FundingCore are outweighed by:
  - raw May stress ann 10bps: `-0.4979`
  - raw recent ann 20bps: `-0.2332`
  - raw May ann lag1 10bps: `-1.0388`
  - May symbol LOO raw positive rate: `0.083`

## Final Boundary

A7I does not authorize:

- alpha proof
- A7.3 generator bakeoff promotion
- dry-shadow alpha evidence
- paper trading
- live trading
- production claims

## Next Valid Work

The next valid work is not budget expansion. It is either:

1. `A7J_REWARD_GENERATOR_REDESIGN_FROM_FAILURE_MODES`
   - Use A7I-1c failure attribution to redesign reward/generator constraints.
   - Keep May as stress-only, not ranking input.
   - Add stronger cost/lag robustness before replay selection.

2. `A7_FORWARD_LOCKED_OBSERVATION`
   - Freeze candidate/reward contract and wait for genuinely new append-only data.
   - Use future data after contract freeze as proof input.

Until one of those passes, crypto remains a research-method line with no alpha proof object.
