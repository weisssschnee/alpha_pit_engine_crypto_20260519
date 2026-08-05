# Crypto Replication-Aware Search Gate V1 — Invalid Run Closure

## Decision

`RUN_INVALID_PRODUCER_PARENT_EXITED_BEFORE_ATTEMPTS`

The replication-aware source implementation is retained, but the authorized
PC2 experiment produced no market-search evidence. It cannot answer whether
development-block replication ordering improves Evolution.

## Frozen experiment

- Producer SHA: `ee36ea46a617b8786661b402992ef3fb0fbaaf5a`
- Arms: typed random, current Evolution, replication-aware Evolution
- Budget: `512 strict × 3 arms = 1,536 strict`
- Scope: 4h, binary/two-axis mechanisms, development train only
- Unchanged: 115-field aligned carrier, Binance USD-M target, mapping, 5 bps
  cost, matched controls, mechanism catalog, compiler, AST, evaluator
- Forbidden: validation, OOS, holdout, tuning, reseed, rescue, promotion

## Observed terminal state

The effective task was `job_20260806_044440_a5b83e`. It wrote the frozen
contract, embedded authority preflight, and initial producer status. The
top-level producer then exited before its first generation attempt and left one
`multiprocessing.spawn` child holding inherited pipes.

| Observation | Value |
|---|---:|
| Generation attempts | 0 |
| Strict evaluated | 0 |
| Checkpoints | 0 |
| Validation/OOS/holdout reads | 0 |
| `run_manifest.json` | absent |
| `final_decision.json` | absent |
| Rescue rerun | false |

The orphan was terminated and the scheduled task was unregistered. The
independent checker exited 1 and correctly rejected the incomplete runtime with
13 missing terminal artifacts. Its empty stderr and the bounded Windows event
query provide no proven crash root cause. A concurrent task-owned preflight
PowerShell leak was removed, but causation is not claimed.

Two earlier detached-wrapper attempts failed before Python/runtime creation
because the operational guard compared the receipt's resolved payload SHA with
the checkout file-byte SHA. They consumed zero attempts and are not experiment
runs. The guard was corrected to bind the Git blob identity and resolved
receipt identity separately before the effective task.

## Evidence identity

The pulled ten-file PC2 evidence set is listed in
`invalid_run_artifact_manifest.json`. Its sorted path/size/hash bundle identity
is:

`D0E544EB1396CA5C43E77ED82B4277FAEF05164650846CB7735CB3D4F65EBCFD`

The one-time receipt is consumed as
`RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED` with
`run_authorized=false`.

## Research boundary

No comparison between random, current Evolution, and replication-aware
Evolution exists. There is no candidate, reward, behavior-family, productivity,
Alpha, validation, OOS, or promotion conclusion. The last checker-backed market
evidence remains the prior V1.1 development/validation and family-consensus
closures.

Any identical replacement run requires new explicit authorization and a new
receipt. This closure does not authorize one.

The existing Search capability overlay records this invalid run without a new
node or authority transition. Bounded CURRENT maintenance did not terminate;
its partial generated files were discarded and the prior valid generated view
was restored. The overlay is therefore newer than CURRENT and global freshness
is not claimed.
