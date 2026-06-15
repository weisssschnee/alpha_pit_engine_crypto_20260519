# CRYPTO A7FAST0 Backtest Acceleration Audit 20260615

Decision: `PASS_A7FAST0_HOT_PATH_ACCELERATION_CONFIGURED_AND_A7FAST1_STARTED`

## Scope

This audit covers the active crypto reward/proxy hot path:

- `scripts/crypto_a7reward1_portfolio_reward_model.py`
- `scripts/crypto_a7al2x5_evaluator_preflight_smoke.py`
- `scripts/crypto_a7v3s9_prereward_oos_control_proxy.py`

It does not authorize alpha proof, shadow, paper, or live.

## Runtime Reality

Company Python:

`D:\HermesWorker\workspace\.venv\Scripts\python.exe`

Installed acceleration libraries verified on company machine:

| package | status |
|---|---|
| numpy | installed |
| pandas | installed |
| pyarrow | installed |
| numba | installed |
| bottleneck | installed |
| numexpr | installed |
| polars | installed |
| joblib | installed |
| sklearn | installed |

Before this patch, the active hot path did not materially use these acceleration libraries. The heaviest repeated path was pandas cross-sectional ranking via `pd.DataFrame(...).rank(axis=0)`.

## Hot Path

Observed bottlenecks:

- formula/evaluator `Rank`, `CSRank`, and `LatentNeutralRank`
- reward `rank_pct`
- repeated raw label rank calculation per candidate/control
- shard-level parallelism without hot-path acceleration
- no true successive halving in the proxy runner

## Changes Applied

Commit: `1834e76 accelerate crypto reward proxy hot path`

Changes:

- Replaced pandas cross-sectional rank with `bottleneck.nanrankdata` fast path, with pandas fallback.
- Added label-rank precomputation per horizon inside reward evaluation.
- Added `--successive-halving` and `--halving-keep-rows` to the pre-reward proxy runner.
- Verified fast rank parity against pandas rank:
  - local max absolute diff: `0.0`
  - remote max absolute diff: `0.0`
  - NaN mask parity: `true`

## Changes Not Applied

Not applied in this patch:

- no numba rewrite of IC/non-overlap loops
- no cross-process shared numeric panel cache
- no semantic change to split, label, control, cost, or orientation logic
- no approximation replacing the strict reward gate

## A7FAST1 Launch

Started detached company task:

`job_20260615_183406_7e7ea9`

Run root:

`D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7fast1_halving_large_proxy_20260615`

Aggregate root:

`D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7fast1_halving_large_proxy_aggregate_20260615`

Launch contract:

- source queue rows: `65,536`
- sampled rows: `32,768`
- shard count: `32`
- rows per shard: `1,024`
- stage1 halving per shard: `1,024 -> 256`
- full proxy only after halving
- semantic pair count: `78`
- motif count: `10`
- max new A7FAST1 parallel workers: `4`
- memory guard: keep at least `8,000,000 KB` free physical memory

## Current Boundary

A7FAST1 is a large proxy/reward prefilter run. It does not authorize alpha proof, shadow, paper, live, or deployment.
