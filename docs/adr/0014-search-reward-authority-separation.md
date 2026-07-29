# ADR 0014: Search Reward Authority Separation

- Status: Superseded by ADR 0016 as an economic optimizer authority decision
- Date: 2026-07-29

## Context

> Historical note: the implementation and evidence boundary below remain
> reproducible, but ADR 0016 found that the copied formula does not bind enough
> candidate economic semantics to serve as the sole qualified optimizer
> authority. It is retained as a diagnostic prototype.

Search Engine V1 used `pair_reward`, the minimum normalized distance to the
strict matched-sleeve feasibility thresholds, as the sole ordering authority
for CEM elites, Evolution parent and replacement decisions, Behavior Archive
champions, and adaptive arm gates.

`pair_reward` is useful for incremental attribution and execution diagnostics,
but it is not a portfolio return objective. The repository already has a
mature Phase3CM pattern based on train-only cost-adjusted portfolio Sortino,
deterministic day-return resampling, and turnover penalties.

The cost audit also found that the current full-L1 cost is not automatically
double the Phase3CM long-short charge: `full_L1 * one_side_cost` equals
`2 * one_way_turnover * one_side_cost` when one-way turnover is half of the
full-L1 weight change. A7Reward-1 uses a different one-way accounting contract
and therefore does not prove that the Search Engine cost must be halved.

## Decision

1. The sole adaptive ordering authority is
   `PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1`.
2. The existing `pair18m` evaluation path computes the objective from the
   primary mapped portfolio: selected-horizon day Sortino, deterministic
   600-draw bootstrap Sortino p25, and the Phase3CM one-way turnover penalty.
3. `CandidateSpec` freezes one horizon. Therefore the Phase3CM worst-horizon
   term equals the selected-horizon day Sortino and the cross-horizon
   instability penalty is explicitly zero; the implementation does not invent
   a second horizon evaluation.
4. CEM elites, Evolution tournaments and replacement, Behavior Archive
   champions, equal-count quality comparisons, and arm exit gates order only
   by `search_reward`.
5. `pair_reward`, matched-positive status, strict margins, turnover, cost,
   support, and concentration remain persisted matched-attribution and
   execution diagnostics. They do not order adaptive search.
6. Legacy checkpoints or archives without `search_reward` fail closed and
   cannot seed a fresh campaign.
7. Behavior identity excludes both `search_reward` and `pair_reward`.

## Evidence boundary

This is a code-authority repair. It does not recompute or reinterpret the
historical V1.1-V1.4 ledgers because they do not persist the complete daily
primary portfolio return path required to reconstruct the new objective.
Their engineering, replay, and matched-feasibility evidence remains historical;
claims that CEM or Evolution improved Alpha-search reward are suspended.

Search Engine V1 still has no formal validation kill-line. Its historical
report-only block is not promoted to validation. A future adaptive market run
requires a separately frozen train/validation split, validation budget/kill
rules, and a read-only holdout boundary.

## Boundaries

No candidate was generated or reevaluated. No market search, OOS, challenge,
recent, May-stress, forward, promotion, latent training, or cross-sprint
adaptive memory is authorized by this decision.
