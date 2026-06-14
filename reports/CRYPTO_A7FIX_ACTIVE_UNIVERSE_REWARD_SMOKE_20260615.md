# CRYPTO A7FIX Active Universe Reward Smoke 20260615

Purpose: verify that `active_universe_size` is now accepted by the reward numeric loader as a computed universe-state field.

Result: `eval_error_rows = 0`. The sampled formulas were not selected, but the field no longer fails with `missing numeric fields for reward model`.

Underlying proxy report follows.

# CRYPTO A7V3S9 Pre-Reward OOS/Control Proxy 20260614

Decision: `HOLD_A7V3S9_PREREWARD_PROXY_NO_SELECTABLE`

A7V3S9 is a cheap pre-reward gate. It reuses the reward numeric loader, evaluator, label alignment, split logic, and metrics, but only evaluates horizons 8h/24h and control variants one_bar_lag/stale_168h/time_shuffle.

It is not alpha proof and does not authorize shadow, paper, live, or full reward continuation.

## Counts

- queue_rows: `2`
- candidate_cap: `2`
- metric_rows: `80`
- reward_rows: `4`
- eval_error_rows: `0`
- strict_pass_rows: `0`
- near_miss_rows: `0`
- selected_rows: `0`
- selected_semantic_pair_count: `0`
- selected_motif_count: `0`

## Bucket Summary

| proxy_bucket   |   count |
|:---------------|--------:|
| proxy_reject   |       4 |

## Selected Pair Summary

`<empty>`

## Selected Motif Summary

`<empty>`

## Rejection Reasons

| hard_reject_reason                 |   count |
|:-----------------------------------|--------:|
| oos_nonoverlap_floor_not_positive  |       4 |
| oos_net_mean_not_all_positive      |       4 |
| stress_floor_not_positive          |       3 |
| recent_sortino_non_positive        |       3 |
| oos_control_dominated              |       2 |
| oos_lag_stale_dominated            |       2 |
| non_finite_diagnostic_composite    |       2 |
| train_orientation_no_positive_edge |       2 |
| shuffle_control_dominated_recent   |       1 |

## Top Selected

`<empty>`

## Boundary

Only `proxy_pass` and bounded `proxy_near_miss` rows may enter the expensive reward gate. Full continuation of unfiltered A7V3S8-style queues remains blocked.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_bounded_reward_smoke": false,
  "authorizes_full_reward_wave": false,
  "authorizes_shadow_paper_live": false,
  "candidate_cap": 2,
  "decision": "HOLD_A7V3S9_PREREWARD_PROXY_NO_SELECTABLE",
  "eval_error_rows": 0,
  "generated_at": "2026-06-14T16:20:28Z",
  "hours_per_split": 720,
  "metric_rows": 80,
  "near_miss_rows": 0,
  "output_selected_queue": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7fix_active_universe_reward_smoke_20260615\\a7v3s9_proxy_selected_for_reward.csv",
  "proxy_control_variants": [
    "one_bar_lag",
    "stale_168h",
    "time_shuffle"
  ],
  "proxy_horizons": [
    8,
    24
  ],
  "queue": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7fix_active_universe_reward_smoke_20260615\\active_universe_smoke_queue.csv",
  "queue_rows": 2,
  "reward_rows": 4,
  "runtime": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\research_runtime\\a7fix_active_universe_reward_smoke_20260615",
  "selected_motif_count": 0,
  "selected_rows": 0,
  "selected_semantic_pair_count": 0,
  "selected_unique_blueprints": 0,
  "stage": "A7V3S9_PREREWARD_OOS_CONTROL_PROXY",
  "strict_pass_rows": 0
}
```
