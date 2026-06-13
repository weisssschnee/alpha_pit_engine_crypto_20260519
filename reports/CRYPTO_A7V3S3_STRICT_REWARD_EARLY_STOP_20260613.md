# CRYPTO A7V3S3 Strict Reward Early Stop - 20260613

## Decision

`STOP_A7V3S3_STRICT_REWARD_ZERO_ACCEPTED_SYSTEMIC_CONTROL_STALE_REJECTION`

A7V3S3 strict reward sharded run was intentionally stopped after early shard evidence showed zero accepted candidates and systemic rejection under the tightened reward gate.

This is not an alpha result and does not authorize alpha proof, shadow, paper, or live execution.

## Run Scope

- Remote run root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s3_strict_reward_sharded_720h_20260613`
- Local evidence root: `runtime/a7v3s3_strict_reward_early_stop_20260613`
- Planned queue: 4096 candidates across 256 shards
- Completed evidence at stop: 18 shard manifests
- Rejection rows inspected: 1152
- Accepted rows: 0

## Stop Rationale

The early completed shards produced no accepted queue rows. Dominant rejection reasons were not isolated evaluation errors; they were the exact failure modes the strict reward gate was designed to catch:

| rejection reason | count |
| --- | ---: |
| `oos_nonoverlap_floor_not_positive` | 1103 |
| `oos_net_mean_not_all_positive` | 1049 |
| `oos_control_dominated` | 1035 |
| `oos_lag_stale_dominated` | 999 |
| `oos_shuffle_dominated` | 836 |
| `stress_floor_not_positive` | 823 |
| `shuffle_control_dominated_recent` | 789 |
| `recent_sortino_non_positive` | 647 |
| `train_orientation_no_positive_edge` | 596 |
| `non_finite_diagnostic_composite` | 8 |

Continuing the same queue would mostly spend compute on candidates already failing OOS floor, control dominance, lag/stale dominance, and stress floor checks.

## Operational Notes

The detached launcher status files marked some child jobs as failed because the launcher used child PowerShell process state, while reward manifests and rejection files were still written. This is a launcher-status accounting issue, not evidence of accepted candidates.

A residual parent launcher continued starting new shards after the first stop attempt. A second targeted stop killed both A7V3S3 parent launchers and all child Python/PowerShell processes matching the A7V3S3 run root. A follow-up process check showed no A7V3S3 crypto reward process remaining.

## Interpretation

The tightened reward gate is functioning: it rejects recent-window winners that do not survive OOS, stress, matched controls, shuffle controls, and lag/stale controls.

The failure is upstream of reward execution:

- The current candidate queue still overproduces recent-period artifacts.
- Many high recent Sortino candidates are control or stale dominated.
- The current queue should not be continued as-is.

## Next Allowed Work

Allowed:

- `A7V3S4_NEAR_MISS_MECHANISM_AUDIT`
- `SEARCH_SPACE_CONTROL_PREFILTER_REDESIGN`
- Build a pre-reward candidate approval/filter layer that removes control/stale-dominated structures before expensive reward evaluation.

Not authorized:

- Continue the same A7V3S3 queue
- Alpha proof
- Shadow / paper / live

