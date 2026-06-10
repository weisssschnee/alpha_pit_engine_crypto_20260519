# CRYPTO A7REWARD1 Company Checkpoint Status 20260610

## Decision

`RUNNING_A7REWARD1_COMPANY_CHECKPOINTED_REWARD_BACKFILL`

A7REWARD1 checkpointed portfolio reward backfill is running on the company machine.

## Task

```text
task_id: job_20260610_185249_bc6093
candidate_cap: 80
hours_per_split: 720
cost_bps: 5
checkpoint_every: 4
queue: A7LS30 selected_top240
```

## Current Checkpoint

```text
completed_candidates: 12 / 80
reward_rows: 48
metric_rows: 1440
eval_error_rows: 0
```

## Current Reward Leader

```text
blueprint_id: a7ls30_32f8844234cc65fc
horizon_h: 4
overall_reward: 5.349537928979012
recent_sortino: 8.039814440490163
recent_sharpe: 4.586683667185654
recent_rankic: 0.01547336214192268
recent_shuffle_control_ratio: 0.6043078091368782
hard_reject: false
```

Formula:

```text
SafeDiv(ZScore(Mean(open_interest_value_last,504)),Abs(Mean(account_position_divergence,96)))
```

## Interpretation

This checkpoint already changes the project-best language:

```text
numeric proxy leader:
  not authoritative

current checkpoint reward leader:
  a7ls30_32f8844234cc65fc, 4h horizon
```

The leader is an open-interest-value / positioning-divergence structure, not the earlier basis-premium proxy leader.

## Boundary

This is a running checkpoint, not a final A7REWARD1 acceptance. It does not authorize alpha proof, shadow, paper, or live execution.
