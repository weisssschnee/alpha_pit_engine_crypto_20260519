# Crypto A7H Final Decision Record

- decision: `HOLD_CRYPTO_ALPHA_PROOF_AFTER_A7H`
- evidence_level: `method_validated_research_only`
- generated_at: `2026-05-19`
- alpha_shadow_proof: `NOT_CONFIRMED`
- generator_bakeoff: `BLOCKED`
- shadow_paper_live: `BLOCKED`

## Confirmed

- Funding data time semantics are research-usable after A7D/A7E repair.
- `mark_index_ratio` is centered basis: `mark_close / index_close - 1.0`.
- Old A7F basis gate used an invalid `abs(mark_index_ratio - 1.0)` transform.
- Corrected A7F remains HOLD; funding/basis/vol risk gates do not clear fresh May failure.
- A7G-1 shows May failure is broad across components and multiple symbols, not a top-hour cleanup problem.
- A7H found one non-funding residual clue:
  - `a7h_flow_rank_taker_imbalance_h6`
  - `Rank(taker_imbalance)`

## Not Confirmed

- No crypto alpha proof object exists yet.
- Core4 is not promoted beyond research benchmark.
- FundingCore is not promoted beyond mandatory benchmark.
- Taker imbalance is not standalone alpha.
- No A7.3 generator/reward bakeoff is authorized.
- No shadow/paper/live evidence can be counted as alpha proof.

## Current Object Status

| object | status | reason |
|---|---|---|
| `Core4` | `research_benchmark_only` | A7B/A7C/A7F/G showed funding-baseline dominance risk, drawdown, and fresh May failure. |
| `FundingCore` | `mandatory_baseline_only` | Semantics usable, but fresh May and risk profile block alpha proof. |
| `Rank(taker_imbalance)` | `hedge_overlay_clue_only` | Residual vs FundingCore/Core4 is positive, but raw standalone 10bps is negative in recent and May; symbol contribution is weak. |
| `Rank(avg_trade_size_quote)` | `rejected_for_now` | Residual annualized looked strong, but residual drawdown and May masked-LOO tail risk are too large. |

## Key Evidence

### Funding / Core4

- A7G-1 decision: `PASS_A7G1_FORENSIC_COMPLETED_HOLD_FUNDING_LINE`
- A7G-1 status:
  - `alpha_proof_status = HOLD_ALPHA_SHADOW_PROOF`
  - `risk_gate_status = NOT_PASSED`
- May failure:
  - FundingCore negative components: `4 / 4`
  - Core4 negative components: `4 / 4`
  - FundingCore negative symbols: `7`
  - Core4 negative symbols: `7`
  - FundingCore top10 loss share: `0.1474`
  - Core4 top10 loss share: `0.1382`

### Non-Funding Residual Line

A7H-0:

- decision: `PASS_A7H_METHOD_SMOKE_CANDIDATE`
- candidates tested: `15`
- candidates passing method smoke: `2`
- warning: all non-funding candidates had negative raw fresh May performance.

A7H-1:

- decision: `PASS_A7H1_RESIDUAL_CANDIDATE_AUDIT`
- candidates audited: `2`
- candidates passing masked LOO audit: `1`
- surviving candidate: `Rank(taker_imbalance)`

A7H-2:

- decision: `HOLD_A7H2_TAKER_IMBALANCE_UNRESOLVED`
- blockers:
  - `standalone_raw_10bp_negative_recent_or_may`
  - `standalone_recent_symbol_contribution_weak`
  - `standalone_may_symbol_contribution_weak`
- residual-only evidence:
  - validation residual vs FundingCore ann: `0.4687`
  - recent residual vs FundingCore ann: `0.2214`
  - fresh May residual vs FundingCore ann: `0.5604`
- raw standalone evidence:
  - recent raw 10bps ann: `-3.3143`
  - fresh May raw 10bps ann: `-2.9743`

## Decision

Crypto A7H does not produce an alpha proof object.

The correct interpretation is:

```text
The crypto data/evaluator/audit chain is now materially stronger.
FundingCore/Core4 remain mandatory benchmarks, not tradable candidates.
Taker imbalance is a hedge/overlay clue, not standalone alpha.
Future crypto search must be residual-aware from the start.
```

## Blocked Actions

- Do not run A7.3 generator/reward bakeoff using the old reward.
- Do not promote Core4, FundingCore, or taker imbalance to shadow alpha proof.
- Do not paper/live trade these objects.
- Do not treat A6 dry-shadow telemetry as alpha evidence.
- Do not expand search before the residual-aware reward contract is written.

## Required Next Step

Proceed to `A7I residual-aware small generator design`.

The next generator must require:

- positive raw standalone evidence,
- positive residual vs FundingCore,
- positive residual vs Core4,
- funding beta disclosure,
- wrong-lag/future-funding diagnostic,
- 10bps and 20bps cost stress,
- masked symbol LOO,
- month stability,
- fresh May behavior,
- explicit rejection of residual-only hedge clues as alpha candidates.

