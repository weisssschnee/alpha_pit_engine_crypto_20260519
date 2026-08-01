# Crypto Search Mechanism V2.1 Acceleration Audit

Status: `SOURCE_REPAIRED_BENCHMARK_PASS_PENDING_PRODUCTION_CHECKPOINT`

## Throughput contract

- Official Python: `G:\PythonProject\.venv\Scripts\python.exe`
- Strict target: 10,000 `PAIR_EVALUATED`
- Wall limit: 18 hours
- Required throughput: 555.556 pairs/hour
- Raw-attempt ceiling: 100,000
- Workers: request 10; memory fail-closed limit 8; 12 forbidden
- Cache: existing candidate-local DAG cache and memmapped carrier only
- Optimizer feedback: adaptive policy lanes remain one-in-flight

## Defect and repair

The first producer `f60f145a` wrote only the frozen contract and four-candidate
memory preflight. It produced no ledger or checkpoint and is not running. Its
single-arm checkpoints exposed only four seed lanes, so an eight-worker pool
could receive at most four evaluations.

The repaired schedule preserves all totals, seeds, reward, evaluator, carrier,
cost and matched controls:

- checkpoint 000: 2,000 old-grammar random;
- checkpoints 001-004: 1,000 expanded random plus 1,000 fresh Evolution each;
- expanded random total: 4,000;
- Evolution total: 4,000.

This produces eight independent arm/seed lanes after checkpoint 000. Stateless
random lanes may issue deterministic lookahead proposals to fill free slots.
Evolution remains strictly reward-before-next-proposal within each seed lane.
The producer now writes an atomic heartbeat with actual pairs/hour, ETA, slot
fill and effective evaluator cores, plus a traceback-bearing failure artifact
for an unhandled engine exception.

## Same-input A/B

Eight exact candidate payloads were evaluated by the unchanged official
evaluator after persistent-executor warm-up.

| Workers | Pairs | Wall seconds | Pairs/hour | Peak worker RSS |
|---:|---:|---:|---:|---:|
| 4 | 8 | 23.129 | 1,245.216 | 231,948,288 bytes |
| 8 | 8 | 18.657 | 1,543.677 | 225,316,864 bytes |

- Full economic evaluation parity excluding timing fields: PASS.
- Measured steady-batch speedup, 8 over 4: 1.240x.
- Both settings exceed the 555.556 pairs/hour campaign minimum in this bounded
  batch; only checkpoint 000 can confirm end-to-end production throughput.
- Cold executor startup was separately observed to make 8 workers 6% slower
  than 4. Production uses a persistent executor, so cold-start throughput is
  not used as the acceleration claim.

## Hot path and environment

The active path is existing expression materialization, portfolio mapping,
turnover/cost, matched sleeves and bootstrap Sortino evaluation. The carrier is
memory-mapped and each candidate shares one DAG cache across primary and
controls. There is no active Numba, Polars, joblib, `use_fast_context`, global
semaphore or successive-halving path.

Installed versions: NumPy 2.1.3, pandas 2.2.3, PyArrow 19.0.1, Numba 0.64.0,
Bottleneck 1.6.0, NumExpr 2.14.1, Polars 1.41.0 and joblib 1.4.2. Scikit-learn
is absent. No package was installed and installed-but-unused libraries are not
claimed as acceleration.

The CPU path did not demonstrate host saturation. The same-input concurrency
counterfactual nevertheless improved end-to-end throughput by 23.97%, so the
launch contract treats the bottleneck as overlap of evaluator wait/memory-I/O
rather than imposing an artificial CPU-occupancy target. Production telemetry
must report this explicitly at checkpoint 000.

## Funnel evidence

The failed preflight had 12/12 proposal lanes constructible and 4/4 submitted
candidates strict-evaluated, but zero retained campaign rows and no checkpoint.
The A/B batch had 8/8 evaluator completions and identical result hashes. Exact,
behavior and archive funnel rates remain pending the first immutable production
checkpoint and are not inferred from the benchmark.

## Deliberately unchanged

- no second AST, compiler, evaluator, scheduler service or database;
- no reward, mapping, target, cost, PIT/lag or matched-control change;
- no cross-campaign candidate, reward, population, archive or RNG import;
- no adaptive lookahead, reseed, HPO, 12-worker launch, JIT rewrite or new
  cross-candidate cache;
- no OOS, holdout, challenge, recent, forward or promotion read.

## Next launch gate

Use a persistent detached process with stdout and stderr files. After
checkpoint 000, require an exact 2,000-row checkpoint, restore verification,
actual throughput at or above 555.556 pairs/hour, and explicit slot-fill and
effective-core telemetry. Preserve and stop on the existing 100,000-attempt or
18-hour limits; do not tune, reseed or rescue within the campaign.
