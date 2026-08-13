# Crypto Temporal Targeted P1/P4 Basin Deepening V1 — r1 closure

Date: 2026-08-13 Asia/Hong_Kong

Decision: `SYSTEM_INVALID`

The sole authorized PC2 run was stopped after an independent audit of the exact
10,000-row checkpoint found 201 out-of-scope strict rows: 77 P2 and 124 P3.
P2/P3 were explicitly paused for this campaign. The run is therefore not valid
targeted P1/P4 evidence and no automatic replacement run was started.

## TARGETED_DEEPENING_VALIDITY

| Item | Result |
|---|---:|
| Runtime | `crypto_temporal_targeted_p1_p4_basin_deepening_v1_20260813r1` |
| PC2 task | `job_20260813_122829_4a039f` |
| Producer source | `d8ec967c69678dfef600bed5dd68a6bbfe8810a4` |
| Last producer heartbeat | 13,691 strict / 23,671 attempts |
| Independently audited prefix | 10,000 strict, contiguous ordinals |
| Frozen arm counts at 10k | Random 2,000 / CEM 2,000 / Evolution 6,000 |
| Validation / OOS / sealed reads | 0 / 0 / 0 |
| Hard stop | `TARGETED_PROGRAM_FAMILY_SCOPE_VIOLATION` |
| Task terminal | `FAILED`, exit 1, 2026-08-13 15:36:54 HKT |
| Checker | `INDEPENDENT_SCOPE_AUDIT_FAIL` |
| Runtime integrity | `INVALID_PARTIAL_NO_FINAL_MANIFEST` |

The audited ledger SHA-256 is
`E9E8795E1A5A87C6B8E47AFE1B0587ECF5DF5B1DA1340AD602DD2092E1C40837`.
It matches the restore-verified checkpoint-004 manifest. Program-family counts
are P1 3,464, P4 6,335, P2 77 and P3 124. All 201 out-of-scope rows came from
`temporal_program_random` with operation
`EXTENSIBLE_MECHANISM_TYPED_RANDOM`.

The detached process tree was terminated after the violation was proven. A
post-stop process audit found zero processes associated with the target
workspace. Because termination occurred between checkpoints, there is no
normal `final_decision.json`, final run manifest, or normal PASS checker. The
10k checkpoint is recoverable evidence; the whole run is not valid.

The one-time authorization is consumed with `run_authorized=false`, outcome
`SYSTEM_INVALID`, and `automatic_next_run_started=false`.

## REAL_ECONOMIC_CLUSTER_RESULT

These are diagnostic values from the contaminated 10k checkpoint, computed
from the persisted 53-field economic fingerprint without market reevaluation.
They combine the frozen 302-row baseline with 32 matched-positive rows from this
run. The P2/P3 rows themselves produced no matched-positive rows, but their
budget use makes the campaign invalid, so the table is retained only as
non-authoritative diagnostic evidence.

| Similarity | Cumulative economic clusters | New vs baseline | Largest share | Top-3 share |
|---:|---:|---:|---:|---:|
| 0.95 | 73 | 16 | 5.69% | 15.27% |
| 0.90 | 50 | 9 | 6.29% | 18.26% |
| 0.85 | 41 | 7 | 11.08% | 23.35% |

Economic effective rank is `3.9689909193`; PCA dimensions for 50% / 80% / 90%
variance are `2 / 4 / 6`. Full PnL and full weight vectors were not persisted
and remain `NOT_AVAILABLE`.

## BASIN_REALIZATION_DEPTH

At similarity 0.90, the cumulative baseline-plus-10k diagnostic contains:

| Depth measure | Count | Change vs baseline |
|---|---:|---:|
| Basins with >=2 mapped-weight realizations | 16 | +5 |
| Basins with >=3 mapped-weight realizations | 10 | +8 |
| Basins with >=2 turnover realizations | 7 | +6 |
| Basins with >=2 raw-field realizations | 23 | +4 |
| Basins with >=2 asset-selection realizations | 24 | +5 |
| Singleton basins | 9 | +2 |
| High-quality basins genuinely deepened | 0 | 0 |
| New high-quality concrete realizations | 0 | 0 |

Realization descriptors became broader, but the campaign added no qualifying
high-quality basin deepening. Because the search scope was violated, these
increments cannot justify continuation or sufficiency.

## P1_VS_P4

The counts below exclude the 201 P2/P3 rows and therefore sum to 9,799, not
10,000.

| Family | Proposals | Dual-positive density | Replication density | Matched-positive | New 0.90 economic clusters | Concrete realizations | Depth signal |
|---|---:|---:|---:|---:|---:|---:|---|
| P1 | 3,464 | 9.99% | 1.76% | 0 | 0 | 0 | no observed depth |
| P4 | 6,335 | 65.43% | 40.87% | 32 | 9 | 32 | 6 basins with >=2 mapped-weight and 6 with >=2 turnover realizations |

This checkpoint is P4-dominated, but family concentration is not the stop
reason. The stop reason is the hard P1/P4 scope violation.

## EVOLUTION_OPERATION_RESULT

| Operation | Proposals | Dual-positive | Matched-positive | New 0.90 clusters | High-quality basins deepened | Diagnostic role |
|---|---:|---:|---:|---:|---:|---|
| Parameter mutation | 3,659 | 2,652 | 13 | 6 | 0 | productive basin discovery, no proven high-quality deepening |
| Crossover | 1,565 | 1,316 | 19 | 8 | 0 | strongest matched-positive exploitation/discovery signal |
| Mechanism mutation | 520 | 52 | 0 | 0 | 0 | low-value exploration in this checkpoint |

This attribution is diagnostic only. It does not change the frozen algorithm,
arm allocation, Evolution semantics, target, evaluator, reward, execution,
mapping, cost, grammar, AST, or compiler.

## Root cause and source closure

The targeted runner inherited a broad-search rule that replaced every tenth
Random proposal with `temporal_program_random_diagnostic` whenever the catalog
contained inactive families. That route was appropriate for broad diagnostics
but contradicted the frozen P1/P4-only contract.

Source now disables that substitution in targeted mode while preserving the
existing broad-search behavior. A focused regression proves targeted Random
keeps its P1/P4 lane key even when the catalog contains paused families. The
audit script independently checks exact ledger ordinals, hashes, family counts,
out-of-scope arms and read boundaries. Temporal regression tests pass 89/89;
focused closure tests pass 5/5.

No replacement search, validation, OOS, holdout, forward read, promotion,
Alpha qualification, pocket gate, or new algorithm was started.

## NEXT_DECISION

`SYSTEM_INVALID`
