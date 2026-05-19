# Crypto A7I Residual-Aware Small Generator Design

- design_status: `READY_FOR_REVIEW_NOT_EXECUTION`
- generated_at: `2026-05-19`
- prerequisite: `CRYPTO_A7H_FINAL_DECISION_RECORD_20260519`
- scope: small matched-budget method test only
- forbidden_scope:
  - alpha shadow proof
  - paper/live
  - production
  - large search
  - old reward reuse

## Objective

A7I tests whether crypto AlphaFactory can generate candidates with incremental value beyond the known funding family.

The goal is not to maximize raw return. The goal is to find candidates that survive:

```text
raw standalone replay
+ residual vs FundingCore
+ residual vs Core4
+ cost stress
+ placebo / wrong-lag
+ masked symbol LOO
+ fresh May behavior
```

## Mandatory Baselines

Every candidate must be compared against:

- `FundingCore`
- `Core4`
- `Rank(taker_imbalance)` as residual hedge/overlay clue
- random/placebo generator

FundingCore remains the primary residualization baseline.

## Candidate Families

A7I may use four small arms.

| arm | purpose | examples |
|---|---|---|
| `I0_basis_premium` | non-funding basis/premium structures | mark-index basis, premium compression, basis reversal |
| `I1_flow_liquidity` | flow/liquidity structures | taker imbalance, volume shock, average trade size, quote volume |
| `I2_microstructure_lite` | OHLCV microstructure-lite structures | range state, realized vol state, open-to-open behavior |
| `I3_placebo_random` | negative control | shuffled fields, random transforms, wrong-lag variants |

No positioning recent-only fields are allowed for 2024-2026 historical proof.

## Matched Budget

First A7I run should be deliberately small:

```text
generated candidates per arm: 250
tradable replay candidates per arm: 64
global cluster cap: required
frequency: 1h only
cost primary: 10bps
cost stress: 20bps
```

Do not run 5m until 1h method evidence is valid.

## Required Candidate Metrics

Each candidate must output:

- raw validation/recent/fresh-May performance,
- residual vs FundingCore,
- residual vs Core4,
- funding beta and correlation,
- Core4 beta and correlation,
- wrong-lag future-funding diagnostic,
- sign flip,
- row shuffle,
- time shuffle,
- symbol shuffle where applicable,
- 10bps and 20bps results,
- masked symbol LOO,
- month leave-one-out,
- top loss hour concentration,
- source feature lineage,
- feature/execution/label timing contract.

## Promotion Gate

A candidate can be labelled `A7I_RESEARCH_CANDIDATE` only if:

- raw 10bps validation > 0,
- raw 10bps recent > 0,
- raw 10bps fresh May is not strongly negative,
- residual vs FundingCore validation > 0,
- residual vs FundingCore recent > 0,
- residual vs FundingCore fresh May >= 0,
- residual vs Core4 recent > 0,
- funding beta does not explain the majority of return,
- sign flip is not positive,
- row/time shuffle are materially weaker,
- wrong-lag future diagnostic is not stronger than the real signal,
- recent masked symbol LOO positive rate >= 75%,
- fresh May masked symbol LOO positive rate >= 50%,
- 20bps does not fully collapse,
- top loss hours are not overly concentrated.

## Rejection Rules

Reject or downgrade if:

- raw standalone is negative but residual is positive,
- the candidate only works as a hedge against FundingCore,
- performance is explained by FundingCore/Core4 beta,
- fresh May repeats the funding-family failure,
- one symbol or one month dominates,
- 20bps cost destroys all edge,
- placebo or wrong-lag signal is comparable to original.

## Decision Labels

Allowed labels:

- `A7I_RESEARCH_CANDIDATE`
- `HOLD_RESIDUAL_ONLY_HEDGE_CLUE`
- `HOLD_FUNDING_EXPLAINED`
- `HOLD_COST_FAIL`
- `HOLD_SYMBOL_OR_MONTH_CONCENTRATED`
- `REJECT_PLACEBO_FAIL`
- `REJECT_TIMING_OR_LEAKAGE`

Forbidden labels:

- `ALPHA_PROOF`
- `SHADOW_READY`
- `PAPER_READY`
- `PRODUCTION_READY`

## Success Criteria

A7I succeeds as a method smoke if:

- at least 2 non-placebo candidates become `A7I_RESEARCH_CANDIDATE`,
- placebo arm produces 0 comparable candidates,
- at least one candidate is not flow/taker related,
- no candidate relies on FundingCore/Core4 beta,
- results are reproducible with fixed seed and frozen data.

If A7I fails, crypto line remains:

```text
data/evaluator/research infrastructure validated;
no crypto alpha proof object yet.
```

