# CRYPTO A7SEARCH5 Selected Full Reward R3 Aggregate Status 20260630

## Decision

`PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY`

Boundary: this is a bounded full reward aggregate on the two A7SEARCH5 proxy-selected candidates. It authorizes next validation/triage work only. It does not authorize alpha proof, shadow, paper, live, or production portfolio construction.

## Runtime

- selected proxy queue: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_aggregate_20260629\a7v3s9_proxy_selected_for_reward.csv`
- full reward run root: `H:\AlphaFactory_CryptoData_archive\a7search5_selected_full_reward_r3_20260630`
- full reward aggregate root: `H:\AlphaFactory_CryptoData_archive\a7search5_selected_full_reward_r3_aggregate_20260630`
- remote aggregate report: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7SEARCH5_SELECTED_FULL_REWARD_R3_AGGREGATE_20260630.md`

## Execution Notes

- R1 detached task did not produce a reliable status.
- R2 exposed a PowerShell orchestration issue: Python RuntimeWarning output was treated as a fatal native command error under `ErrorActionPreference=Stop`.
- R3 fixed this by using `PYTHONWARNINGS=ignore`, redirecting native output, and allowing the reward model to complete normally.
- R3 completed cleanly: shard queue, reward shard, and aggregate all exited `0`.

## Counts

- input proxy-selected candidates: `2`
- reward rows: `8`
- split metric rows: `240`
- eval error rows: `0`
- accepted rows: `3`
- accepted unique blueprints: `2`
- hard reject rows: `5`
- launcher status conflicts: `0`

## Accepted By Semantic Pair / Motif

- semantic pair: `open_interest|positioning`
- motif: `safe_div_abs`

Accepted horizons:

- `4h`: 2 rows
- `8h`: 1 row

## Top Accepted Rows

| blueprint_id | horizon_h | train_sortino | validation_sortino | test_sortino | recent_sortino | min_oos_floor_sortino | stress_floor_sortino | recent_shuffle_control_ratio | formula |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `a7search1_521ca32c7158db99` | 4 | 1.5634 | 5.7182 | 8.0857 | 10.8199 | 5.3920 | 4.1101 | 0.3886 | `SafeDiv(ZScore(open_interest_value_last),Abs(CSRank(top_long_short_account_ratio_last)))` |
| `a7search1_ae732635455df95c` | 4 | 1.6018 | 5.7837 | 8.1064 | 10.7932 | 5.2818 | 4.1350 | 0.6362 | `SafeDiv(ZScore(open_interest_value_mean),Abs(CSRank(top_long_short_account_ratio_last)))` |
| `a7search1_521ca32c7158db99` | 8 | 1.6081 | 6.1179 | 7.2707 | 11.5445 | 4.0642 | 3.2695 | 0.4484 | `SafeDiv(ZScore(open_interest_value_last),Abs(CSRank(top_long_short_account_ratio_last)))` |

## Rejection Reasons

Rejected horizon rows failed for:

- `oos_control_dominated`: 5
- `oos_lag_stale_dominated`: 4
- `oos_shuffle_dominated`: 4
- `shuffle_control_dominated_recent`: 2

## Interpretation

The two selected proxy candidates survived bounded full reward on 4h/8h views, but the accepted set is still narrow:

- one semantic pair;
- one motif;
- two almost equivalent OI numerator variants;
- same denominator field.

This is positive evidence for an `open_interest_value / top_account_positioning` mechanism, not broad alpha proof.

## Next Authorized Work

Allowed:

- duplicate exposure and information-source audit on these two formulas;
- ablation/single-leg validation;
- A7MEM update with accepted rows and rejection reasons;
- decide whether to allocate a controlled lane around OI/positioning while preserving diversity caps.

Blocked:

- alpha proof;
- shadow / paper / live;
- treating the accepted reward rows as production candidates before ablation and independent exposure review.

