# CRYPTO A7EFF1 Search And Reward Efficiency Audit

Generated: `2026-07-10`

## Decision

`PASS_A7EFF1_CRYPTO_FLOW_OPTIMIZED_WITH_EQUIVALENT_RESULTS`

The crypto search/reward flow had material computational and statistical-efficiency defects. The corrected flow preserves the reward contract and decisions while reducing the measured focused-flow wall time from about 1,735 seconds to 136.688 seconds.

This audit did not inspect or modify the CN line.

## Confirmed Defects

1. Source-lag results were counted but the full validation queue was still sent to strict reward.
2. Reward shuffle controls depended on shard order because one sequential RNG was shared by each shard.
3. Each reward shard independently decoded and derived the same numeric panel.
4. The reward inner loop reranked the same signal repeatedly and computed IC/RankIC through Python timestamp loops.
5. The DSL admitted deterministic no-information forms such as `Sign(CSRank(x))`, `Abs(TSRank(x))`, and nested `Abs`.
6. A7SOURCE6 tested generic field transforms instead of exact AST source subtrees.
7. The incremental-information approval treated any passing subtree as proof that the complete formula had no incremental information.
8. PC2 panel paths remained an outer-launcher environment contract; the first shared-cache launch failed closed when that contract was omitted.

## Flow Corrections

- Strict reward now consumes a source-lag survivor queue.
- Reward rows per shard are balanced against the configured parallelism.
- Shuffle controls use common random numbers keyed only by horizon and control variant.
- One manifest-backed numeric cache is built from the survivor field union and loaded through read-only NumPy memmaps.
- Cross-sectional ranks and portfolio weights are reused across horizons.
- Lag, stale, time-shuffle, and symbol-shuffle controls transform prepared ranks/weights instead of reranking.
- IC/RankIC uses a stable, two-pass vectorized correlation implementation.
- Exact source subtrees are generated from the parsed AST.
- Incremental approval now distinguishes exact metric equivalence, robust Pareto gain, and unresolved portfolio-marginal trade-offs.

## Measured Efficiency

| Measure | Baseline | Optimized v2 | Result |
|---|---:|---:|---:|
| validation queue rows | 53 | 53 | same input |
| source-lag reward inputs | 33 | 33 | 20 rejected before reward |
| strict reward rows | 132 | 132 | same output surface |
| accepted rows | 16 | 16 | exact set match |
| eval errors | 0 | 0 | exact match |
| total flow seconds | about 1,735 | 136.688 | about 12.7x faster |
| reward stage seconds | about 1,718 | 120.266 | about 14.3x faster |
| numeric-cache build seconds | repeated per worker | 3.763 once | shared |

The broader repaired flow also reduced `107` validation rows to `26` source-lag survivors, avoiding `81 / 107` (`75.7%`) strict-reward evaluations.

## Equivalence Proof

- Leaderboard keys: `132 / 132` matched.
- Gate, hard-reject, reject reasons, source-lag gate, and source-lag policy decisions: exact match.
- Accepted set: `16 / 16` exact match.
- Leaderboard numeric maximum absolute difference: `1.7763568394002505e-15`.
- Split-level IC/RankIC differences: at machine precision after stable centering.
- Split-level capacity proxy maximum absolute difference: `9.313225746154785e-09`, caused by floating-point summation order on large quote-volume values; no decision input changed.
- Duplicate formula+horizon groups: `20` groups / `52` rows, zero metric spread and zero decision mismatches under common controls.

## DSL Waste Audit

The full one-million A7LS15 index contains at least `85,666` deterministic no-information formulas (`8.5666%`):

| Reason | Rows |
|---|---:|
| direct constant `Sign(rank)` | 42,027 |
| smoothed constant `Sign(rank)` | 11,983 |
| redundant `Abs(rank)` | 16,321 |
| redundant nested `Abs` | 15,335 |

The 100k materialization queue contains `8,602` such rows (`8.602%`). Future generation resamples them and preflight fails closed if they remain in a queue.

This is a conservative lower bound because raw-field value domains are not yet propagated through the active generator. For example, a smoothed long/short ratio remains positive even when no explicit rank operator appears.

## Source Information Decisions

| Rank | Source | Decision | Formula |
|---:|---|---|---|
| 1 | `a7ls15_9c0eabfdbed59b50` | `HOLD_NON_UNIQUE_INFORMATION` | `Mul(Sub(CSRank(Decay(mark_trade_basis_bps,240)),CSRank(Decay(global_long_short_account_ratio_last,4))),Sign(Decay(global_long_short_account_ratio_last,4)))` |
| 2 | `a7ls15_068586ffed926481` | `HOLD_CANONICAL_DID_NOT_REPASS` | `Sub(CSRank(Delta(open_interest_value_last,240)),CSRank(Abs(ZScore(Mean(global_long_short_account_ratio_last,168)))))` |
| 3 | `a7ls15_fc7666db25384707` | `PASS_INCREMENTAL_INTERACTION_EVIDENCE` | `Mean(Mul(Delta(open_interest_value_last,120),Abs(ZScore(Mean(account_position_divergence,3)))),4)` |
| 4 | `a7ls15_3e336dcc7a3d7037` | `HOLD_NON_UNIQUE_INFORMATION` | `Mul(Delta(open_interest_value_mean,240),Sign(TSRank(global_long_short_account_ratio_last,48)))` |
| 5 | `a7ls15_897eb3538573d7f3` | `HOLD_NON_UNIQUE_INFORMATION` | `Sub(Delta(open_interest_value_mean,240),ZScore(Mean(top_long_short_account_ratio_last,4)))` |
| 6 | `a7ls15_02151306bb6ff585` | `HOLD_NON_UNIQUE_INFORMATION` | `Sub(Delta(open_interest_value_mean,240),Mean(top_long_short_account_ratio_last,120))` |
| 7 | `a7ls15_18de34f5611f1f80` | `HOLD_NON_UNIQUE_INFORMATION` | `Mul(Delta(open_interest_value_mean,240),Sign(Mean(Decay(top_long_short_position_ratio_last,72),24)))` |
| 8 | `a7ls15_8ea42f29ccc5fa98` | `HOLD_PORTFOLIO_MARGINAL_REVIEW` | `SafeDiv(Delta(open_interest_value_mean,240),Abs(Abs(ZScore(Mean(top_global_account_divergence,240)))))` |

Result: the 16 accepted reward rows do not represent eight independent alpha mechanisms. Five canonical sources are OOS-equivalent to accepted subtrees, one canonical source fails to repass, one interaction has incremental evidence, and one `SafeDiv` expression remains a portfolio-marginal review candidate.

## Remaining Boundary

- Typed State/subgraph governance exists, but reusable State materialization is not active in the main search/reward loop.
- Raw-field value domains still need registry-backed propagation.
- `SafeDiv` needs denominator stability, perturbation, tail contribution, and portfolio-marginal diagnostics. It should not be blanket-rejected because portfolio weights are rank-normalized.
- Signal-vector clustering across non-identical formulas remains a required pre-search gate.
- Alpha proof, shadow, paper, live, and deployment remain unauthorized.

## Evidence

- Local optimized aggregate: `G:\Chengbo\runtime\a7pc2_pc1wide_source_lag_reward_20260710_results\strict_reward_optimized_v2_aggregate`
- Local final source decisions: `G:\Chengbo\runtime\a7pc2_pc1wide_source_lag_reward_20260710_results\a7source6_subtree_incremental_validation`
- Local numeric-cache manifest: `G:\Chengbo\runtime\a7pc2_pc1wide_source_lag_reward_20260710_results\a7reward1_numeric_cache_manifest.json`
- PC2 run root: `D:\HermesWorker\runtime\crypto_line\a7pc2_source6_subtree_incremental_flow_20260710`
