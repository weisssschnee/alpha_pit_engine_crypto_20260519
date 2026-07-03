# CRYPTO A7DEDUP1 Canonical Reward Queue Dedup

Generated: 2026-07-03T13:39:47.020164+00:00

## Decision

`PASS_A7DEDUP1_CANONICAL_QUEUE_BUILT`

A7DEDUP-1 canonicalizes strict-reward accepted formulas and applies exact-expression, skeleton, semantic-pair, and base-family caps before the next mechanism expansion. This is a queue hygiene gate, not alpha proof.

## Counts

- input_rows: `8`
- selected_rows: `3`
- rejected_rows: `5`
- exact_duplicate_groups: `3`
- max_per_expression: `1`
- max_per_skeleton: `1`
- max_per_semantic_pair: `2`
- max_per_base_family: `2`

## Selected Queue

| rank | blueprint_id | horizon_h | train_sortino | validation_sortino | test_sortino | recent_sortino | expression |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | a7mech1_0026_oi_only_tsrank | 24 | 3.4985599741227675 | 2.551076502062724 | 3.891615500928222 | 4.392425060799842 | `TSRank(open_interest_mean,504)` |
| 2 | a7mech1_0002_base_safe_div_oi_funding | 8 | 2.4473052293036317 | 3.249800166301023 | 0.9630842884017243 | 7.559932085877106 | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` |
| 3 | a7mech1_0061_oi_only_cs_tsrank | 24 | 3.4985599741227675 | 2.551076502062724 | 3.891615500928222 | 4.392425060799842 | `CSRank(TSRank(open_interest_mean,504))` |

## Interpretation

The accepted A7REWARD-3 queue contains repeated OI-only expressions under different blueprint IDs. Dedup keeps the strongest canonical representatives and prevents the next search from mistaking duplicate OI structures for independent breadth.

## Outputs

- selected_queue: `runtime\a7dedup1_canonical_reward_queue_20260703\a7dedup1_canonical_selected_queue.csv`
- rejected_rows: `runtime\a7dedup1_canonical_reward_queue_20260703\a7dedup1_dedup_rejections.csv`
- group_summary: `runtime\a7dedup1_canonical_reward_queue_20260703\a7dedup1_group_summary.csv`
- manifest: `runtime\a7dedup1_canonical_reward_queue_20260703\a7dedup1_manifest.json`
