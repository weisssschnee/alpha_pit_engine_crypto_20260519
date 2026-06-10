# CRYPTO A7REWARD2 Algorithm Chain And Reward Objective Audit 20260610

## Decision

`HOLD_A7REWARD_FIXED_SCALAR_OBJECTIVE_NOT_ACCEPTABLE`

The user's objection is correct. A fixed weighted `overall_reward` must not be the locked search objective. It can be kept only as a diagnostic composite or tie-breaker. Primary candidate acceptance must be multi-objective: gate pass, Pareto rank, OOS stability, control survival, turnover/cost, and stress behavior.

## Current Chain Finding

```text
formula / derived feature generation
-> numeric probe
-> selected queue by score_no_may
-> A7REWARD1 portfolio evaluator
-> leaderboard / diagnostics
```

The breaking point is that the active queue-building path is still upstream of the real portfolio reward. In `crypto_a7ff8_expanded_numeric_probe.py`, `portfolio_proxy()` builds `score_no_may` from:

```text
non_l7_bonus
premay_positive_split_count
lag_ok
robust_ok
1 - control_ratio
cost5_recent_oriented * 1000
```

This is a useful cheap filter, but it is not a final reward model. It does not fully represent portfolio drawdown, turnover path, leverage/capacity, multi-horizon consistency, stress survival, or marginal contribution.

## Fixed Composite Problem

The original A7REWARD1 implementation created:

```text
overall_reward =
  0.35 * recent_sortino
  0.20 * min(validation_sortino, test_sortino, recent_sortino)
  0.15 * recent_sharpe
  0.15 * recent_rankic * 20
  0.05 * stress_sortino
  0.05 * capacity_score
  - penalties
```

This is unsafe as a locked optimization target because search can learn the measurement quirks:

```text
maximize recent window
hide risk in non-weighted dimensions
prefer formulas that exploit score scaling
optimize RankIC while PnL path is weak
trade off control/stress/cost in arbitrary fixed ratios
```

The bug is not that these metrics are wrong. The bug is treating one fixed linear blend as the winner function.

## Patch Applied

`scripts/crypto_a7reward1_portfolio_reward_model.py` was changed so that:

```text
diagnostic_composite_score:
  retained only for compatibility and tie-break diagnostics

primary ranking:
  gate_pass
  pareto_rank
  objective_pass_count
  recent_sortino
  min_oos_sortino
  recent_shuffle_control_ratio
```

Added objective columns:

```text
obj_recent_sortino
obj_min_oos_sortino
obj_recent_sharpe
obj_recent_rankic
obj_stress_sortino
obj_neg_recent_drawdown
obj_neg_recent_turnover
obj_neg_shuffle_control_ratio
```

Added outputs:

```text
a7reward1_pareto_leaderboard.csv
a7reward1_diagnostic_composite_leaderboard.csv
```

Renamed checkpoint/manifest language away from `best_overall_reward` toward:

```text
top_pareto_blueprint_id
top_pareto_rank
top_pareto_objective_pass_count
top_diagnostic_composite_score
ranking_policy = multi_objective_gate_and_pareto
```

## Correct Interpretation

Current A7REWARD1 is not alpha proof and not final search reward. It is now a portfolio evaluation layer with multi-objective leaderboard views. Search should not directly optimize the diagnostic composite.

The corrected architecture should be:

```text
cheap numeric proxy:
  broad prefilter only

portfolio reward evaluator:
  computes path metrics, control metrics, costs, stress, turnover, capacity

multi-objective selector:
  gates + Pareto frontier + diversity / marginal contribution

search feedback:
  learns from which field families/operators survive Pareto gates,
  not from a single fixed scalar score
```

## Verification

Synthetic smoke was rerun after the patch:

```text
PASS_A7REWARD1_SYNTHETIC_SMOKE
```

This verifies that the reward evaluator still ranks the true synthetic signal above shuffled noise and hard-rejects the shuffle noise case.

## Remaining Holds

```text
HOLD_REWARD_NOT_YET_CLOSED_LOOP_IN_SEARCH
HOLD_NO_SET_LEVEL_MARGINAL_CONTRIBUTION_REWARD
HOLD_COMPANY_CHECKPOINT_RESULTS_REQUIRE_REPARSING_WITH_PARETO_COLUMNS
```

No alpha proof, shadow, paper, or live authorization is granted.
