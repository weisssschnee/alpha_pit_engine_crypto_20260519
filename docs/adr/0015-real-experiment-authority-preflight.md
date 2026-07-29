# ADR 0015: Real Experiment Authority Preflight

- Status: Accepted
- Date: 2026-07-29

## Context

Engineering correctness does not prove that an experiment used the intended
target, optimizer reward, execution price, portfolio mapping, cost, validation,
or promotion boundary. The Search Engine now has a repaired train-only reward,
but several experiment semantics remain non-formal and the validation kill-line
is not qualified.

## Decision

Before a Search Engine `run*` command starts, it resolves these seven semantic
roles from CURRENT and emits their authority references:

`target`, `optimizer_reward`, `execution_price`, `portfolio_mapping`, `cost`,
`validation_role`, and `promotion_gate`.

Vacant, conflicting, stale, inactive, or missing components block the run. A
non-formal binding may support a bounded development experiment only when its
bound node explicitly declares `active_authority: true`; it remains displayed
as unqualified and cannot authorize formal claims, OOS, promotion, or
authority replacement.

Each run must also state:

- the new evidence it is expected to add;
- the project decision that evidence can change.

If either statement is absent, the run is not information-bearing enough to
start through the canonical CLI.

## Boundaries

This preflight reads CURRENT; it creates no authority database, persisted
capsule, broad CI gate, or Obsidian status system. Synthetic tests, ordinary
coding, build/check commands, and diagnostics that cannot change a project
conclusion remain outside this gate.

This decision authorizes no market experiment. The existing research HOLD,
validation gap, sealed roles, spent state, and promotion restrictions remain.
ADR 0016 records the current inactive economic bindings and the resulting
fresh-run block.
