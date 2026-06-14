# CRYPTO A7V3S8 Redesigned Reward Smoke Result 20260614

Decision: `HOLD_A7V3S8_REDESIGNED_CONSTRUCTION_ZERO_ACCEPTED`

## Scope

This report records the A7V3S8 redesigned reward smoke result after the remote company-machine run completed.

This is not alpha proof and does not authorize shadow, paper, live, or large continuation search.

## Execution Status

- smoke task: `job_20260614_030340_112cb5`
- auto-guard task: `job_20260614_030641_4308d1`
- smoke shard manifests: `32`
- smoke reward rows: `2048`
- split metric rows: `61440`
- eval error rows: `0`
- accepted rows: `0`
- accepted unique blueprints: `0`

The auto-guard behaved correctly:

```text
guard started
smoke done detected; aggregating
smoke aggregate accepted=0 eval_errors=0 manifests=32
zero accepted or eval errors; no continuation
guard finished
```

## Interpretation

The smoke did run. It did not fail due to missing fields, evaluator exceptions, or remote execution collapse. The failure is substantive: the redesigned candidate construction still produced no candidates that survived the strict reward gate.

The generic aggregate manifest reports:

```text
decision: HOLD_A7V3S0_REWARD_SHARDED_AGGREGATE_INCOMPLETE_OR_DIRTY
expected_shards: 64
manifest_count: 32
```

For A7V3S8 this is expected, because the authorized smoke boundary was 32 shards. The material result is zero accepted candidates with zero evaluation errors.

## Main Rejection Reasons

| reason | count |
| --- | ---: |
| `oos_nonoverlap_floor_not_positive` | 1998 |
| `oos_net_mean_not_all_positive` | 1911 |
| `oos_control_dominated` | 1672 |
| `stress_floor_not_positive` | 1671 |
| `oos_lag_stale_dominated` | 1609 |
| `oos_shuffle_dominated` | 1375 |
| `shuffle_control_dominated_recent` | 1188 |
| `train_orientation_no_positive_edge` | 1114 |
| `recent_sortino_non_positive` | 1062 |
| `non_finite_diagnostic_composite` | 240 |

## Top Diagnostic Failures

The highest recent Sortino rows were rejected, which is the intended behavior of the gate:

```text
open_interest|regime / state_conditioned_rank_mul / 24h
recent_sortino: 34.36
min_oos_floor_sortino: -2.84
stress_floor_sortino: -3.35
reject: OOS floor negative, stress negative, control dominated, lag/stale dominated, shuffle dominated

liquidity|regime / safe_div_abs / 24h
recent_sortino: 31.38
min_oos_floor_sortino: -3.61
min_oos_sortino: -1.59
stress_floor_sortino: -2.13
reject: OOS floor negative, stress negative, control dominated, lag/stale dominated
```

This is a reward-hacking signature: strong recent performance but non-portable OOS/stress behavior and dominance by controls or stale/lag variants.

## Coverage Notes

The 2048 reward rows covered multiple semantic pairs and motifs, including:

- `funding_dense|regime`
- `regime|taker_flow`
- `funding_basis|open_interest`
- `funding_basis|premium`
- `basis|funding_basis`
- `basis|regime`
- `funding_basis|regime`
- `open_interest|regime`
- `positioning|regime`
- `premium|regime`

Main motifs included:

- `state_conditioned_signed`
- `safe_div_abs`
- `state_conditioned_rank_mul`
- `signed_rank_gate`

So the zero-accepted result is not simply from testing one narrow formula family.

## Current Authorization

Allowed:

- preserve aggregate artifacts
- use the rejection surface for construction redesign
- build a pre-reward OOS/control proxy before launching another reward wave
- audit whether candidate construction is overusing regime-denominator or state-conditioned rank motifs

Blocked:

- full continuation of the same A7V3S8 reward queue
- treating recent Sortino leaders as best candidates
- alpha proof
- shadow, paper, or live

## Next Required Change

Do not run more variants of the same motif-level construction as a large search.

The next search must change the construction stage materially:

1. Add a cheap pre-reward OOS/control proxy before reward evaluation.
2. Penalize candidates whose recent edge is mostly reproduced by lag, stale, shuffle, or matched controls.
3. Reduce reliance on regime denominator formulas and state-conditioned rank products unless they show portable pre-reward split behavior.
4. Promote only candidates with positive OOS floor proxy into the expensive reward gate.

Recommended next stage:

```text
A7V3S9 = pre-reward OOS/control proxy construction
```

Target:

```text
large enough search surface, but only candidates with cheap OOS/control survival enter A7REWARD.
```

