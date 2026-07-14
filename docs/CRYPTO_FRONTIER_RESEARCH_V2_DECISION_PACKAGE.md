# Crypto Frontier Research V2 decision package

Status: `CRYPTO_FRONTIER_RESEARCH_COMPLETED` through result route B. Economic selection remains `HOLD`.

## Rebuilt causal model

The prior Main path was effectively:

`qualified hourly core fields -> delayed one-day return -> formula/program state -> score -> cross-sectional rank weights -> turnover cost -> generic evaluator -> development evidence`

V2 makes the previously collapsed layers explicit:

`hash/PIT-qualified release -> representation adapter -> native target and horizon -> native model/search -> forecast or direct portfolio artifact -> native portfolio mapping -> native evaluator + common bridge -> development-only evidence -> sealed OOS proof gate`

The system now supports both forecast-first/stateful holdings and direct multi-step portfolio allocation. Native results and bridge results are separate artifacts.

## Native reproductions

| System | Native input, target and horizon | Training | Portfolio mapping | Native evaluator | Matched control | Fixed budget |
|---|---|---|---|---|---|---|
| Microsoft Qlib v0.9.7, commit `da920b7` | Official Alpha158 daily expressions; `Ref($close,-2)/Ref($close,-1)-1`; one-day execution delay | Official processors and LGBModel workflow, train/valid, deterministic one thread | Actual TopKDropout state, cash and retained positions; core10 adaptation uses top3/drop1 | IC/RankIC and 238-day benchmark-excess risk analysis with native 5/15 bps order costs | First 13 official features; same label, processors, model, executor and dates | 2 fits |
| DeepDow v0.2.3, commit `384e18a` | `X=(156,4,20,10)`, `y=(156,4,5,10)`; 20-day lookback, one-day gap, five-day future path | Upstream InRAMDataset, RigidDataLoader, KeynesNet, Run and composable losses; seeds 1701/1709 | Native long-only fully-invested SoftmaxAllocator weights | Per-sample five-day buy-and-hold Sharpe/mean-return/max-drawdown losses; no native cross-sample transaction cost | Flow channels rotated across assets; same return channel, splits, model, loss, epochs and seeds | 4 fits |

The Qlib run is a native code-path reproduction with crypto adaptations, not a CSI300 benchmark reproduction. DeepDow is a framework workflow reproduction, not a claim that a published market benchmark was reproduced.

## Common bridge and evidence

All six systems use the same 23 June development decision dates, one-day delayed returns, actual portfolio weights, 5 bps per unit L1 turnover, 365-day annualization and a fixed five-day moving-block bootstrap.

| System | Net mean | 95% LCB | Mean turnover | Annualized Sharpe |
|---|---:|---:|---:|---:|
| Internal 20-day momentum | -0.008754 | -0.017237 | 0.30435 | -7.6094 |
| Qlib full Alpha158 | -0.004319 | -0.015256 | 0.05123 | -3.3270 |
| Qlib 13-feature control | -0.004319 | -0.015309 | 0.05123 | -3.3270 |
| DeepDow flow | -0.005939 | -0.014922 | 0.04676 | -4.6970 |
| DeepDow rotated-flow control | -0.005939 | -0.014459 | 0.04615 | -4.7093 |
| One over N | -0.005947 | -0.014795 | 0.04348 | -4.7190 |

Paired component evidence:

- Qlib full minus control: mean `0.0`, LCB `0.0`; official regularization stopped both at iteration 1 and predictions were constant, so IC/RankIC are undefined rather than zero.
- DeepDow flow minus rotated-flow control: mean `-8.15e-8`, 95% LCB `-2.29e-4`.

Both component migration gates are `HOLD`; no candidate or economic component is promoted.

## Layer attribution and data boundary

- Representation: fixed complete core10 is runnable without filling; exact core12 is not, because BTC March and AVAX April are absent.
- Target/horizon: coexistence of one-day normalized forecast labels and five-day future tensors closes the daily multi-step expressivity gap.
- Model/search: pinned supervised and direct-allocation adapters reject the old model monoculture, but do not establish economic superiority.
- Portfolio: stateful native holdings and direct neural weights now survive into the bridge without rank remapping.
- Evaluator: native and common evaluators are explicitly distinct; the one-month development holdout cannot support promotion.

Narrow data blockers remain for multi-level L2/DeepLOB, 252-day long-history systems, qualified minute targets, and an exact complete core12 direct-allocation tensor. These blockers do not prove that data is the unique bottleneck.

## New release entry

`ingress-preflight` accepts a candidate release only after metadata, file/content hashes, schema, primary-key uniqueness, PIT ordering, coverage, role paths, prohibited performance columns and declared consumer IDs pass. It is a non-performance gate and cannot activate reward, search, memory or promotion.

## Decision

Accept ADR 0003 and retain all four freezes. The next data release can be registered and run through a small development-only adapter experiment without changing the Arena contract. Opening any validation/test/recent/stress/forward role or promoting a candidate still requires the explicit approval gate.

## Evidence-qualification supersession

This package records architecture execution, not the final economic interpretation. `CRYPTO_FRONTIER_EVIDENCE_QUALIFICATION_20260714` supersedes the Qlib `0/0` and DeepDow near-zero economic rows: the original Qlib fit was degenerate and has been repaired once without search; both repaired Qlib and instrumented DeepDow remain below the pre-registered Data Adequacy Gate. No architecture-control registry or generated graph change is part of the repository closure.
