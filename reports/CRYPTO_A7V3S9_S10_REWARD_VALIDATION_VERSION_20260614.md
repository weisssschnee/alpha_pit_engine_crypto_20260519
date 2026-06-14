# CRYPTO A7V3S9/S10 Reward Validation Version - 20260614

## Decision

`PASS_A7V3S9_S10_REWARD_VALIDATION_ARCHIVED__HOLD_RESEARCH`

This version package archives the first end-to-end reward validation flow that produced one strict accepted research candidate after proxy filtering, full reward evaluation, and ablation validation.

It does **not** authorize alpha proof, large deployment, shadow, paper, or live trading.

## Scope

Included stages:

- `A7V3S9_PROXY_AGGREGATE`: proxy reward aggregate over 32 shards.
- `A7V3S9_SELECTED_FULL_REWARD`: bounded full reward on proxy-selected candidates.
- `A7V3S10_ACCEPTED_CANDIDATE_VALIDATION_PACK`: single-leg and ablation validation for the accepted formula.

Excluded stages:

- alpha proof
- shadow / paper / live
- unconstrained large search
- production portfolio construction

## Source Of Truth Artifacts

Reports:

- `reports/CRYPTO_A7V3S9_PREREWARD_OOS_CONTROL_PROXY_AGGREGATE_20260614.md`
- `reports/CRYPTO_A7V3S9_SELECTED_FULL_REWARD_AGGREGATE_20260614.md`
- `reports/CRYPTO_A7V3S10_ACCEPTED_CANDIDATE_VALIDATION_PACK_20260614.md`

Runtime archives:

- `runtime/a7v3s9_prereward_oos_control_proxy_aggregate_20260614/`
- `runtime/a7v3s9_selected_full_reward_aggregate_20260614/`
- `runtime/a7v3s10_accepted_candidate_validation_20260614/`

## Stage Results

### A7V3S9 Proxy Aggregate

- Decision: `PASS_A7V3S9_PROXY_AGGREGATE_SELECTED`
- Expected shards: 32
- Completed shard manifests: 32
- Leaderboard rows: 2048
- Eval error rows: 0
- Strict pass rows: 2
- Near miss rows: 4
- Selected rows for bounded full reward: 4
- Selected unique blueprints: 4
- Authorized only bounded full reward.

### A7V3S9 Selected Full Reward

- Decision: `PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`
- Reward rows: 16
- Split metric rows: 480
- Eval error rows: 0
- Accepted rows: 1
- Accepted unique blueprints: 1
- Hard reject rows: 15
- Valid reward rows: 1
- Authorized only the next validation pack.

Main rejection reasons among non-accepted rows:

- `oos_control_dominated`: 15
- `oos_lag_stale_dominated`: 13
- `stress_floor_not_positive`: 11
- `shuffle_control_dominated_recent`: 8
- `oos_shuffle_dominated`: 6
- `oos_nonoverlap_floor_not_positive`: 3
- `train_orientation_no_positive_edge`: 2

### A7V3S10 Accepted Candidate Validation

- Decision: `HOLD_RESEARCH`
- Baseline queue rows: 5
- Baseline reward rows: 20
- Baseline accepted rows: 0
- Full reward accepted rows: 1

Interpretation:

- No tested single-leg or ablation baseline passed full reward.
- The composite therefore has incremental evidence over the tested primitive legs.
- The candidate is still research-only because train Sortino is modest and the accepted set is one candidate from one family.

## Accepted Research Candidate

- Blueprint id: `a7v3s0_37b921db0b74a15a`
- Semantic pair: `basis|premium`
- Motif: `smooth_mul`
- Horizon: `24h`
- Formula:

```text
Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))
```

Full reward metrics:

| Metric | Value |
| --- | ---: |
| train_sortino | 1.2005533133 |
| validation_sortino | 6.3304837497 |
| test_sortino | 5.5108582709 |
| recent_sortino | 1.8147482368 |
| validation_floor_sortino | 4.9710187266 |
| test_floor_sortino | 1.9523059850 |
| recent_floor_sortino | 0.8522200631 |
| stress_sortino | 9.8761720598 |
| stress_floor_sortino | 6.4977159775 |
| stress_n_obs | 601 |
| recent_sharpe | 1.2575733163 |
| recent_ic | 0.0292898441 |
| recent_rankic | 0.0391216650 |
| recent_net_mean | 0.0004762742 |
| recent_max_drawdown | -0.6214403599 |
| recent_avg_turnover | 0.0348717207 |
| recent_control_ratio | 0.9814668328 |
| recent_shuffle_control_ratio | 0.3563163176 |
| oos_control_dominated_count | 0 |
| oos_lag_stale_dominated_count | 0 |
| oos_shuffle_dominated_count | 0 |
| oos_positive_split_count | 3 |

## Research Interpretation

The candidate is not just a naked basis factor. It multiplies:

- `premium_abs_state`: a persistent premium dislocation state.
- `Abs(ZScore(Mean(mark_trade_basis_bps,168)))`: a medium-window absolute mark/trade basis anomaly.

The intuitive financial story is:

```text
When premium dislocation persists and mark/trade basis is unusually far from normal,
the market is in a derivative-pricing stress state.
This candidate tries to capture cross-sectional continuation or correction pressure
from that stress state over a 24h horizon.
```

The ablation result matters: single components did not pass the same strict gate, while the product did. That supports an interaction effect. It does not prove a tradable alpha by itself.

## Known Limits

- Only one accepted candidate survived.
- The accepted family is still `basis|premium`, so field-family breadth is insufficient.
- Train edge is modest compared with OOS and stress results.
- The result can be regime-local and must not be extrapolated into proof.
- Baseline validation covered selected single legs and simple ablations, not every nearby formula.

## Authorization

Allowed:

- Keep this candidate in the research memory / formula registry.
- Use it as positive feedback for broader search-space guidance.
- Use the rejection reasons to tune future generator coverage and proxy selection.
- Run broader controlled search with explicit family caps and new-field lanes.

Blocked:

- alpha proof
- shadow / paper / live
- treating this as production-ready
- concentrating the next search only on `basis|premium`

## Next Work

Recommended next taskflow:

1. Register `a7v3s0_37b921db0b74a15a` as a research-retained candidate.
2. Boost related but not identical motifs around `basis|premium smooth_mul`.
3. Cap `basis|premium` concentration in the next search.
4. Force separate lanes for `OI|positioning`, `OI|taker`, `funding|OI`, CE overlay, listing-age interactions, and regime/event-boundary interactions.
5. Add leave-one-window / regime-out attribution before any stronger claim.

