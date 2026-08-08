# Crypto Temporal Program Systemic Failure Gap Report — 2026-08-08

## Verdict

The zero-strict temporal-program run was invalid before candidate economics could
be interpreted.  The defect is systemic, not a single role-name typo: an
authority mismatch was detected only after expensive evaluation, swallowed as a
candidate-local rejection, repeatedly scheduled through one Stage-0 lane, and
allowed to consume the wall budget without a zero-progress liveness stop.

## Observed failure chain

| Layer | Source gap | Observed consequence | Required repair |
|---|---|---|---|
| Evaluator authority | Paired diagnostic role admission occurs near the end of `evaluate_pair`; the runner supplied an incompatible role. | Full materialization/mapping/reward work preceded a deterministic authority rejection. | Validate receipt-bound partition and paired role before any store or market-array access. |
| Failure classification | The temporal-program worker converts all `ValueError`/`FloatingPointError` exceptions into `PAIR_REJECTED`. | A run-global contract error appeared as ordinary candidate attrition. | Introduce an explicit evaluation-contract exception and fail the run immediately on it. |
| Stage-0 scheduling | Each batch starts at the first ordered lane and fills from it; completion, not attempts, advances its quota. | All 117,457 persisted rejects came from one family/seed lane; P2/P3/P4 had no exposure. | Rotate deterministically across eligible lanes at proposal-attempt granularity. |
| Liveness | Throughput is checked only after a full 2,000-strict checkpoint. | A zero-strict run can never reach the first throughput gate and therefore runs to the wall limit. | Add a frozen zero-strict liveness ceiling plus immediate fatal-system-error stop. |
| Process evidence | The program runner passes no process-evidence root and emits no batch lifecycle. | Submitted/returned work and the 65-attempt terminal gap cannot be independently reconciled. | Reuse existing worker and proposal-batch process receipts; require closed evidence. |
| Checkpoint semantics | Budget checkpoint is written only when strict rows exceed the last full checkpoint. | The invalid zero-strict run had no exact terminal checkpoint. | Write atomic terminal checkpoints even with an empty strict ledger. |
| Terminal authority | Only budget exhaustion is modeled; systemic invalidity falls through to budget exhaustion. | The terminal label obscured the actual invalid-run cause. | Add `ENGINE_RUN_INVALID` with a distinct terminal checkpoint and no research conclusion. |
| Independent checker | The checker validates artifact hashes/counts but does not reject nonzero-attempt, zero-strict invalid runs. | Artifact integrity could be reported without research-run validity. | Report artifact integrity and run validity separately; require fatal/liveness and process-evidence consistency. |
| Source smoke | Smoke compiles/replays representatives but performs no exact evaluator-admission check. | The source bundle passed while its runner/evaluator authority pair was incompatible. | Add a no-market exact-path admission preflight and a sentinel test proving no store access precedes it. |
| Receipt enforcement | `expected_branch` and `authorized_implementation_sha` were recorded but not enforced by the program receipt validator. | A correctly hashed component bundle could run from an unintended branch or without proving the authorized implementation is an ancestor. | Enforce exact branch plus Git ancestry, and bind receipt budget, market authority, and prohibited boundaries. |
| Checkout portability | Component identity used raw worktree bytes even though Git permits semantically identical LF/CRLF checkouts. | A clean exact-SHA PC2 checkout failed before candidate evaluation on one unchanged Python file. | Bind component identity to committed Git blobs and separately require a clean component worktree. |

## Scope of the repair

Reuse the existing `CandidateSpec`, temporal program catalog, compiler, pair
evaluator, mapping, reward, worker initializer, checkpoint format, and process
evidence helpers.  Do not change seeds, market data, target, mapping, cost,
reward, program catalog, optimizer parameters, release gates, or research
budget.  Do not start validation, OOS, promotion, or a rescue search.

## Replacement-run admission

A replacement development run is not safe until all of the following pass:

1. exact paired authority admission succeeds before store access;
2. a synthetic run-global contract failure terminates as `ENGINE_RUN_INVALID`;
3. Stage-0 rejected proposals rotate across every frozen family/seed lane;
4. zero strict progress produces an atomic, restorable terminal checkpoint;
5. worker and producer batch evidence closes with zero unexplained attempts;
6. the checker distinguishes artifact integrity from run validity; and
7. the full repository test suite passes under the new committed source SHA.

Only after those gates pass may a new one-time receipt be frozen for the same
development contract.  The prior invalid runtime must never be resumed or used
as policy, archive, reward, or distribution state.
