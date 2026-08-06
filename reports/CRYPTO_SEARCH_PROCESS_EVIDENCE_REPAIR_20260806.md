# Crypto Search Process Evidence Repair — 2026-08-06

## Outcome

The Replication-Aware Search Gate source/process failure is repaired at production source commit `175ce33f31ba56ab336d187e2b7ca0c9e2e29e98`. The repair adds campaign-local, atomic, fail-closed process receipts before worker submission and at worker initializer/task boundaries. It does not change candidate economics, reward, mapping, optimizer policy, Archive behavior, or research authority.

The original consumed run remains invalid and is not replayed. Its persisted producer status recorded zero generation attempts, but the exact proposal count is **unknown**, not proven zero: no pre-submit attempt receipt existed, while an orphan multiprocessing spawn child proves the submission path began. Strict evaluated count and checkpoint count remain exactly zero.

## Repairs

- `G:/Chengbo/tools/company-remote/company-remote.ps1` no longer combines a future Scheduled Task trigger with an immediate start. It registers triggerless, starts once, uses `MultipleInstances IgnoreNew`, and holds a persistent atomic start lock.
- The remote launcher persists launcher PID, child PID, separate stdout/stderr paths, and the real child exit code using `System.Diagnostics.Process`.
- `search_engine_v1.py` writes an atomic proposal-batch receipt after construction and before submission, binding generation attempts and exact candidate/spec identities.
- Worker processes write atomic initializer and task-stage receipts, including explicit failure receipts.
- Process evidence is scoped to the replication-aware campaign and is fail-closed process authority only.

## Verification

- Intentional PC2 nonzero launcher smoke `job_20260806_111245_5b7afd`: exactly one invocation; child exit `7`; Scheduled Task result `7`; launcher PID `26992`; child PID `24228`.
- PC2 no-market engine smoke `job_20260806_114350_12ba4d`: exit `0`; 115-field store/registry initialized; five materialized workers emitted five `INITIALIZER_READY` receipts; configured worker limit remained 10.
- Market evaluation: `false`.
- Receipt consumption: `false`.
- Validation/OOS/holdout reads: none.
- Focused tests: `29 passed`.
- Full suite: `454 passed`, with one pre-existing NumPy warning.
- Independent Standards and Spec reviews: no remaining actionable findings.

The existing Search capability overlay is updated without a new node or authority transition. Bounded CURRENT maintenance did not terminate, so its partial generated files were discarded and the prior committed CURRENT was restored. Generated CURRENT remains stale; this closure does not claim global Graph freshness.

The remote launcher is a global operational tool outside this Git repository. Its exact path and SHA256 are bound in the runtime manifest: `G:/Chengbo/tools/company-remote/company-remote.ps1`, `75036FFAC3A80A3E0A12637DD93F37B6A0582C9F6313E4F6BCBFC85F4BE726AA`.

## Research boundary

This is source and process-runtime evidence only. It creates no market result, random/Evolution comparison, replication-ordering result, Alpha claim, validation, OOS, promotion, or replacement-run authority. The consumed Replication-Aware Search Gate receipt remains unauthorized. Any market replacement requires a new explicit authorization and receipt.

Authoritative artifact index: `runtime/crypto_search_process_evidence_repair_20260806/run_manifest.json`.
