# CRYPTO A7V3S8 Redesigned Reward Smoke Launch - 20260614

## Decision

`PASS_A7V3S8_REDESIGNED_REWARD_SMOKE_LAUNCHED`

A7V3S8 launches a bounded strict-reward smoke on the A7V3S7 redesigned candidate queue.

This is a smoke execution only. It does not authorize full reward wave, alpha proof, shadow, paper, or live.

## Launch

- Task id: `job_20260614_030340_112cb5`
- Auto-guard task id: `job_20260614_030641_4308d1`
- Remote run root: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s8_redesigned_reward_smoke_720h_20260614`
- Input queue: `a7v3s7_redesigned_reward_prequeue.csv`
- Candidate rows authorized for smoke: `512`
- Shards authorized: `32`
- Rows per shard: `16`
- Concurrency: `8`
- Reward parameters:
  - `hours_per_split = 720`
  - `cost_bps = 5.0`
  - `checkpoint_every = 4`

## Launch Verification

Initial verification showed eight A7V3S8 reward workers active on shards `s000` through `s007`, each running `crypto_a7reward1_portfolio_reward_model.py` under the A7V3S8 run root.

An auto-guard was also launched. It waits for the 32-shard smoke to finish, aggregates the result, and only starts continuation shards `s032` through `s063` if the smoke has accepted rows greater than zero and zero eval errors. If the smoke remains zero accepted, it writes `A7V3S8_NO_CONTINUATION.txt` and stops.

## Stop Rule

Do not expand beyond the 32-shard smoke unless aggregate results show a material improvement over A7V3S6:

- accepted rows must be greater than zero, and
- accepted candidates must not be control/stale dominated, and
- eval errors must remain zero.

If accepted rows remain zero, stop and redesign construction again rather than continuing the queue.
