# CRYPTO A7REWARD2 Acceptance Bias Audit 20260610

## Decision

`HOLD_A7REWARD1_OLD_TOP_REJECTED_BY_STRICT_GATE`

`PASS_A7REWARD2_STRICT_RERANK_BUILT`

This audit does not authorize alpha proof, shadow, paper, or live execution.

## Why The 13 Sortino Was Suspicious

The old A7REWARD1 top row was:

```text
blueprint_id: a7ls30_fea76deef615bc91
horizon_h: 8
expression:
  SafeDiv(TSRank(mark_index_basis_bps,72),Abs(Decay(account_position_divergence,48)))

recent_sortino: 13.0146
recent_sharpe: 6.1920
recent_rankic: 0.0322
recent_shuffle_control_ratio: 0.5114
```

The number is not fake, but it was too easy to overread:

```text
1. It is annualized.
   horizon 8h uses sqrt(1095) ~= 33.09 annualization.
   recent non-overlap median Sortino 13.0146 is about 0.393 unannualized.

2. It is not stable across all evidence windows.
   train_sortino: -1.8966
   validation_sortino: 1.1387
   validation_nonoverlap_floor_sortino: -0.8155
   test_sortino: 10.6589
   recent_sortino: 13.0146
   stress_sortino: 6.1981

3. Orientation was weak in train.
   train net mean after orientation was still negative.

4. The result was concentrated in a specific post-2025 regime.
   The signal is strong in test/recent but not in train and only weak in validation.
```

So the correct interpretation is:

```text
interesting clue,
not accepted portfolio candidate,
not alpha proof.
```

## Gate Patch

The reward model was tightened in `scripts/crypto_a7reward1_portfolio_reward_model.py`.

New hard rejects:

```text
train_orientation_no_positive_edge
oos_nonoverlap_floor_not_positive
```

New objective/gate field:

```text
min_oos_floor_sortino
```

Primary gate now requires:

```text
not hard_reject
min_oos_sortino > 0
min_oos_floor_sortino > 0
recent_shuffle_control_ratio < 1
```

This catches candidates whose median non-overlap reward looks good but at least one OOS offset is negative.

## Strict Rerank Result

Input:

```text
runtime/a7reward1_portfolio_reward_model_20260610/a7reward1_split_reward_metrics.csv
metric_rows: 9430
old_reward_rows: 315
```

Output:

```text
runtime/a7reward2_acceptance_bias_audit_20260610/
  a7reward2_strict_candidate_reward_leaderboard.csv
  a7reward2_strict_gate_pass_candidates.csv
  a7reward2_manifest.json
```

Strict result:

```text
strict_reward_rows: 315
strict_gate_pass_rows: 6
strict_gate_pass_unique_blueprints: 3
old_top_rejected: true
old_top_reject_reasons:
  train_orientation_no_positive_edge
  oos_nonoverlap_floor_not_positive
```

## New Strict Top

```text
blueprint_id: a7ls30_c94e306c3e19bd08
horizon_h: 8
semantic_pair: open_interest_like|positioning_like
motif: safe_div_abs
expression:
  SafeDiv(ZScore(Mean(open_interest_value_last,240)),Abs(Mean(account_position_divergence,72)))

train_sortino: 2.5480
validation_sortino: 8.5912
validation_floor_sortino: 7.7553
test_sortino: 20.7804
test_floor_sortino: 18.0730
recent_sortino: 8.0485
recent_floor_sortino: 7.0495
stress_sortino: 2.9829
stress_floor_sortino: 2.7454
recent_sharpe: 4.3618
recent_rankic: 0.0210
recent_net_mean: 0.0005396
recent_max_drawdown: -0.2123
recent_avg_turnover: 0.00637
recent_shuffle_control_ratio: 0.5807
```

This is materially cleaner than the old 13 Sortino row, but it is still only a research candidate because the surviving set is narrow.

## Remaining Risk

The strict survivors are concentrated:

```text
strict_gate_pass_rows: 6
unique_blueprints: 3
semantic_family: open_interest_like|positioning_like only
motif: safe_div_abs only
```

That concentration means the current search has not yet produced broad independent alpha supply. It found one plausible information route:

```text
open-interest magnitude / positioning divergence
```

The project should treat this as a validated research branch, not as a finished alpha book.

## Memory Errors

Two rows failed in the reward evaluator:

```text
a7ls30_4ccf03d3ec71426c
Clip(CSRank(Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(global_long_short_account_ratio_last,72)))),-3,3)

a7ls30_649adbc6c6bad5f6
Clip(ZScore(Sub(Delta(mark_index_basis_bps,2),ZScore(Mean(global_long_short_account_ratio_mean,36)))),-3,3)
```

Both failed with:

```text
MemoryError((96, 3481), dtype('float64'))
```

This is an evaluator implementation issue for dense operator paths, not evidence that those formulas are bad. It should be fixed with chunked evaluation before using full-scale reward as a hard production gate.

## Next Required Action

```text
1. Upload the stricter reward gate to the company machine.
2. Re-run A7REWARD on the broader queue with the strict gate.
3. Add chunked evaluator support for dense CSRank/ZScore/Clip paths.
4. Only after strict reward survives, wire gate/Pareto reward into A7RAW/A7LS search feedback.
```

No formula search, alpha proof, shadow, paper, or live execution is authorized by this audit.
