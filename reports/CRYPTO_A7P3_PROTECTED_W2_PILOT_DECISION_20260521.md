# Crypto A7P-3 Protected W2 Pilot Decision

- generated_at: `2026-05-21`
- decision: `PASS_A7P3_PROTECTED_W2_PILOT_PIPELINE_HOLD_PRODUCTIVITY`
- source_checkpoint: `A7P3_W2PILOT`
- execution_scope: `64 control-clean W2 registry cells`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- full L1 / L2 / L3: `NOT_AUTHORIZED`

## Purpose

A7P-3 tested whether the A7P control-clean W2 registry can run through the A7O search / strict replay / fold replay / deep audit pipeline without recreating the W1 negative-control and concentration failures.

This is a protected pilot, not a promotion gate.

## Result

| metric | value |
|:--|--:|
| generated | 131072 |
| strict_replay_selected | 1536 |
| deep_audit_selected | 192 |
| eval_failure_count | 0 |
| fold_metric_missing_rate | 0.0 |
| active_cells_with_valid_deep_audit | 64 |
| liquidity_volatility_deep_share | 0.046875 |
| single_return_corr_cluster_share | 0.09375 |
| single_horizon_deep_share | 0.296875 |
| single_hypothesis_family_share | 0.15625 |
| single_feature_operator_horizon_motif_share | 0.015625 |
| strict_negative_control_research_like | 0 |
| negative_control_dominance_failures | 0 |
| placebo_or_null_research_candidates | 0 |
| post_may_eligible_deep_survivors | 13 |

## Decision

`PASS_A7P3_PROTECTED_W2_PILOT_PIPELINE_HOLD_PRODUCTIVITY`

The runner, fold replay, May stress-only policy, negative-control blocker, and diversity caps are functioning on the control-clean W2 registry. The pilot does not reproduce W1's wrong-lag negative-control breach or liquidity-volatility concentration.

However, productivity is low: only `13 / 192` deep-audit rows remain post-May eligible under the v3 activity gate. This is not enough to authorize full L1 continuation or alpha proof.

## Authorization

Authorized:

- A7P-4 productivity and near-miss forensic using A7P-3 outputs.

Not authorized:

- Full A7O-L1 continuation.
- A7O-L2 or A7O-L3.
- Alpha proof.
- Shadow, paper, or live trading.
- Any use of May in ranking, reward, threshold tuning, generation, allocation, mutation, or surrogate training.

## Artifact Hygiene

The original checkpoint report contains an inherited cumulative-checkpoint section from earlier A7O runs. A7P-3 decision-making uses only the dedicated `A7P3_W2PILOT` checkpoint decision, manifest, scoreboard, post-May pool, and this decision record.

The runner has been updated so future `A7O_L1_SKIP_CUMULATIVE_UPDATE=1` reports do not render stale cumulative summaries.

## Next Action

Run `A7P-4 productivity forensic`, no new search:

1. Compare the `13` post-May eligible rows against the `179` May-vetoed / rejected deep rows.
2. Attribute loss by fold, cost20, lag1, residual FundingCore/Core4, field family, hypothesis family, and horizon.
3. Identify whether low productivity is caused by overly strict stress gate, weak W2 cell registry, or broad May fragility.
4. Do not tune May thresholds; May remains stress-only.
