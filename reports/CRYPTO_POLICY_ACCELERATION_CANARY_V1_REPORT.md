# Crypto Policy Acceleration Canary V1

Status: `PASS`

## Exact parity

Eight fixed spent-development pairs across ABBA trials: `PASS`. Per-pair full trim used 16 trims; threshold plus lane-boundary used 4.
Median wall time baseline/candidate: 48.980s / 47.490s (1.031x).
Candidate identity, frozen-source complete non-timing evaluation payload, reward, replay hashes, and delta-weight hash are exact.

## Worker scheduling

- 8 workers: two-trial median 0.4651 pairs/s, minimum 0.4314, peak worker RSS 1,218,793,472 B, source parity `PASS`, native trim `True`
- 10 workers: two-trial median 0.5072 pairs/s, minimum 0.4894, peak worker RSS 1,219,280,896 B, source parity `PASS`, native trim `True`
- 12 workers: two-trial median 0.5131 pairs/s, minimum 0.4988, peak worker RSS 1,219,022,848 B, source parity `PASS`, native trim `True`

Selected next development-Arena launch limit: `10` (smallest configuration within 95% of best two-order median throughput).
This is a bounded 20-lane x 4-pair scheduler canary, not a permanent global or 128-pair-lane guarantee.

## Runtime reality

- Python: `D:\HermesWorker\workspace\crypto_line\.venv_b251733\Scripts\python.exe`
- Packages: bottleneck=NOT_INSTALLED, joblib=NOT_INSTALLED, numba=NOT_INSTALLED, numexpr=NOT_INSTALLED, numpy=2.1.3, pandas=2.2.3, polars=NOT_INSTALLED, pyarrow=19.0.1, scikit-learn=NOT_INSTALLED
- Background Python observed: `UNKNOWN, crypto_policy_acceleration_canary.py`; throughput is qualified only for this recorded co-run state.
- Hot path: NumPy/pandas evaluator over the pinned memmap; no Numba, Polars, Joblib, or successive halving is active.
- Applied: RSS-threshold trim at 768 MiB plus mandatory lane-boundary trim; two-order bounded worker selection.
- Not applied: evaluator approximation, JIT rewrite, cache-key relaxation, candidate reuse, or policy feedback.

## Next launch contract

- `use_fast_context`: false / not implemented
- `development_arena_worker_limit`: 10
- `successive_halving`: false
- cache: exact raw bundle, source, compiler, candidate, adaptive block, mapping, delay, and cost identities remain required

This canary changes execution guidance only. It makes no economic, OOS, forward, challenge, candidate, or promotion claim. The producer implementation is temporary and may be evicted after evidence closure.
