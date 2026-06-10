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

The smoke is now adversarial, not just true-signal-vs-noise. It verifies:

```text
synthetic_true_positive:
  gate_pass = True

synthetic_orientation_equivalent:
  gate_pass = True
  verifies train-only orientation handling does not reject an equivalent sign flip

synthetic_train_only_overfit:
  hard_reject = True
  rejects a signal that wins in train but reverses in OOS

synthetic_recent_only_overfit:
  hard_reject = True
  rejects a signal that has isolated recent-window behavior but fails OOS consistency

synthetic_high_turnover_trap:
  hard_reject = True
  rejects a path where a non-overlap metric can look positive while net PnL / controls fail

synthetic_shuffle_noise:
  hard_reject = True
  rejects random signal and shuffle-control dominance
```

This proves the evaluator can detect several expected failure modes. It does not prove market alpha; it proves the reward gate is no longer a trivial scalar that blindly rewards fixed-window response.

## Why The Old Search Produced Invalid Alpha-Like Outputs

The old A7LS/A7RAW numeric search did not lack all scoring. It had a proxy scorer. The problem is that the scorer was not a portfolio reward:

```text
score_no_may =
  non_l7_bonus
  + premay_positive_split_count
  + lag_ok
  + robust_ok
  + (1 - control_ratio)
  + cost5_recent_oriented * 1000
```

That can select formulas with numeric response, but it cannot distinguish enough between:

```text
response surface clue
vs
tradable cost-adjusted portfolio path
vs
control/shuffle artifact
vs
single-window overfit
vs
cluster/family repetition
```

The company checkpoint confirms this failure mode. The completed A7REWARD1 run had:

```text
completed_candidates: 80
reward_rows: 320
metric_rows: 9600
eval_errors: 0
```

The old checkpoint leader by `overall_reward` was:

```text
blueprint_id: a7ls30_fea76deef615bc91
horizon_h: 8
expression: SafeDiv(TSRank(mark_index_basis_bps,72),Abs(Decay(account_position_divergence,48)))
recent_sortino: 13.0146
recent_sharpe: 6.1920
recent_rankic: 0.0322
recent_shuffle_control_ratio: 0.5114
hard_reject: false
```

But the same formula at another horizon appeared as:

```text
horizon_h: 4
recent_sortino: 12.1887
recent_shuffle_control_ratio: 1.0931
hard_reject: true
hard_reject_reasons:
  oos_net_mean_not_all_positive
  shuffle_control_dominated_recent
```

This is exactly why a single scalar or a single horizon cannot be trusted. The old outputs may contain useful clues, but they were not validated as alpha because the active selection layer did not yet require path-level OOS reward, hard controls, and horizon/split stability.

## Current Reward Validity Claim

The valid claim is narrow and concrete:

```text
A7REWARD can now evaluate candidate formulas as portfolio paths.
A7REWARD reports Sortino, Sharpe, IC/RankIC, drawdown, turnover, capacity proxy, controls, and OOS split stability.
A7REWARD uses gate + Pareto ranking as the primary view.
A7REWARD can reject synthetic overfit/control/noise cases.
```

The invalid claim would be:

```text
A7REWARD has proved alpha.
A7REWARD has closed the search feedback loop.
A7REWARD's diagnostic_composite_score is the project best function.
```

Those remain false.

## Immediate Runtime Action

The patched reward evaluator was uploaded to the company machine and the same A7LS30 top240 queue is being rerun with:

```text
task_id: job_20260610_215553_e0e563
candidate_cap: 80
hours_per_split: 720
cost_bps: 5
checkpoint_every: 4
```

This rerun is reward validation only. It does not create new formulas and does not authorize alpha proof.

## Remaining Holds

```text
HOLD_REWARD_NOT_YET_CLOSED_LOOP_IN_SEARCH
HOLD_NO_SET_LEVEL_MARGINAL_CONTRIBUTION_REWARD
HOLD_COMPANY_CHECKPOINT_RESULTS_REQUIRE_REPARSING_WITH_PARETO_COLUMNS
```

No alpha proof, shadow, paper, or live authorization is granted.
