# CRYPTO A7REWARD0 Reward Model Contract 20260610

## Decision

`PASS_A7REWARD0_REWARD_MODEL_CONTRACT_BUILT`

A7REWARD0 replaces numeric-proxy-only candidate ranking with a portfolio reward contract. Historical `score_no_may`, spread, t-stat, and clue counts remain diagnostic inputs, but they are no longer allowed to define the project-level best candidate by themselves.

## External Reference Basis

- FinRL portfolio allocation environments use portfolio value/return as the reward target and separate train/test/trading environments.
- TensorTrade risk-adjusted reward schemes explicitly support Sharpe and Sortino style reward algorithms.
- AlphaGen/AlphaForge style alpha mining optimizes alpha sets by downstream combination performance, not isolated formula prettiness.
- Crypto trading reward practice must include transaction costs, risk, drawdown, turnover, and stress behavior.

## Primary Reward

```text
primary_reward =
  OOS cost-adjusted Sortino
  on dollar-neutral cross-sectional portfolio returns
```

## Required Metrics

Every search shard that wants to claim a leader must output:

```text
sortino
sharpe
ic
rankic
net_mean_return
max_drawdown
turnover
cost_bps
capacity_proxy
control_ratio
shuffle_control_ratio
split_stability
stress_sortino
```

## Reward Construction

```text
signal -> cross-sectional ranked weights
weights -> dollar-neutral gross-1 portfolio
raw forward return -> portfolio PnL
turnover * cost_bps -> transaction cost
net PnL -> Sharpe / Sortino / drawdown
signal vs future return -> IC / RankIC
shuffle/null controls -> anti reward-hacking gate
```

Orientation is chosen only on `train_2024`, then frozen for:

```text
validation_2025H1
test_2025H2
recent_oos_2026JanApr
known_may2026_stress
```

## Hard Rejects

```text
missing reward metrics
recent OOS Sortino <= 0
validation/test/recent net mean not all positive
shuffle/null control dominance
missing cost model
excessive turnover without reward support
future/leakage/timing violations
L7-only evidence without tradable raw PnL support
duplicate cluster without marginal contribution
```

## Composite Reward

```text
overall_reward =
  0.35 * recent_oos_sortino
  0.20 * min(validation_sortino, test_sortino, recent_sortino)
  0.15 * recent_oos_sharpe
  0.15 * recent_oos_rankic * 20
  0.05 * may_stress_sortino
  0.05 * capacity_score
  -0.15 * max_drawdown_penalty
  -0.05 * turnover_penalty
  -0.25 * shuffle_control_penalty
```

## Leaderboard Policy

The project-level best must be reported as:

```text
best_by_sortino
best_by_sharpe
best_by_rankic
best_by_stress_survival
best_by_capacity
best_overall
```

Numeric-proxy leaders may be shown only as:

```text
numeric_proxy_leader
```

They cannot be described as `best alpha`, `实控 best`, or `portfolio best`.

## Implementation

A7REWARD1 implements this contract in:

```text
scripts/crypto_a7reward1_portfolio_reward_model.py
```

It writes:

```text
runtime/a7reward1_portfolio_reward_model_20260610/
  a7reward1_reward_contract.json
  a7reward1_synthetic_smoke_leaderboard.csv
  a7reward1_split_reward_metrics.csv
  a7reward1_candidate_reward_leaderboard.csv
  a7reward1_best_by_sortino.csv
  a7reward1_best_by_sharpe.csv
  a7reward1_best_by_rankic.csv
  a7reward1_best_overall.csv
  a7reward1_manifest.json
```

## Boundary

This contract does not authorize alpha proof, shadow, paper, or live execution. It authorizes reward evaluation and search reward wiring only.
