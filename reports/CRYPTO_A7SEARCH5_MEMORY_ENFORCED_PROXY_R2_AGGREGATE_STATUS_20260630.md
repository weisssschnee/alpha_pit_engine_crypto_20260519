# CRYPTO A7SEARCH5 Memory-Enforced Proxy R2 Aggregate Status 20260630

## Decision

`PASS_A7V3S9_PROXY_AGGREGATE_SELECTED`

Boundary: this is a proxy aggregate. It authorizes only bounded full reward on the selected proxy queue. It does not authorize alpha proof, shadow, paper, live, or production portfolio construction.

## Runtime

- source run root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_20260628`
- aggregate root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_aggregate_20260629`
- remote aggregate report: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7SEARCH5_MEMORY_ENFORCED_PROXY_R2_AGGREGATE_20260629.md`
- lock-aware supervisor: `D:\HermesWorker\runtime\a7search5_r2_lockaware_supervisor_20260629.ps1`
- supervisor task id: `job_20260629_120926_3f21c9`

## Completion

- expected shards: `128`
- completed shard reports: `128`
- missing shard reports: `0`
- eval error rows: `0`
- active A7 Python workers after completion: `0`
- supervisor stopped after successful aggregate fix.

## Aggregate Counts

- leaderboard rows: `32768`
- strict pass rows: `42`
- near-miss rows: `323`
- selected rows: `2`
- selected unique blueprints: `2`

## Selected Queue

Selected rows are concentrated in:

- semantic pair: `open_interest|positioning`
- motif: `safe_div_abs`
- horizon: `8h`

Top selected proxy rows:

| blueprint_id | semantic_pair | motif | horizon_h | proxy_score | recent_sortino | min_oos_floor_sortino | stress_floor_sortino | recent_shuffle_control_ratio | expression |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `a7search1_ae732635455df95c` | `open_interest|positioning` | `safe_div_abs` | 8 | 26.5254 | 11.5284 | 4.04352 | 3.2753 | 0.169512 | `SafeDiv(ZScore(open_interest_value_mean),Abs(CSRank(top_long_short_account_ratio_last)))` |
| `a7search1_521ca32c7158db99` | `open_interest|positioning` | `safe_div_abs` | 8 | 26.3896 | 11.5445 | 4.06419 | 3.26946 | 0.113307 | `SafeDiv(ZScore(open_interest_value_last),Abs(CSRank(top_long_short_account_ratio_last)))` |

## Operational Notes

- The original high-parallel supervisor caused repeated `MemoryError` on `s064` and `s067`.
- The run was recovered by a lock-aware supervisor with memory guard, fresh locks, and attempt caps.
- The first aggregate attempt failed due to launch mode: direct `python scripts\crypto_a7v3s9_proxy_aggregate.py` could not import `scripts`.
- Aggregate was fixed by running with `PYTHONPATH=$Repo` and `python -m scripts.crypto_a7v3s9_proxy_aggregate`.

## Next Authorized Work

Allowed:

- bounded full reward on the selected proxy queue;
- strict reward triage;
- duplicate exposure / information-source audit;
- update A7MEM positive and rejection memory after strict reward.

Blocked:

- alpha proof;
- shadow / paper / live;
- treating the two proxy-selected rows as accepted candidates before bounded full reward.

