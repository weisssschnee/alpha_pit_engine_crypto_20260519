# Crypto P4 Mechanism Pocket Fresh-Development Gate V1

## Decision

`PRE_CANDIDATE_ENGINE_RUN_INVALID`

The one-time authorization is consumed. No economic candidate evaluation ran,
so this attempt produces no Alpha, mechanism, optimizer, validation, OOS, or
promotion conclusion.

## What completed

- Frozen cohort remained exactly 80 candidates: 40 Evolution matched-positive
  discovery rows, 20 Evolution near-miss controls, and 20 Random near-miss
  controls.
- Producer source remained
  `5179bd2875d4bad56c02919bf774ddc7483ee984`.
- OI/mark acquisition completed `27/27` venue-days across Bybit, OKX futures,
  and Hyperliquid futures with zero failures.
- The frozen symbol map matched exactly.

## Failure

The PC2 wrapper used the `Start-Process` object's native `ExitCode` as the next
phase authority. After the OI child had written a successful terminal status,
the wrapper observed a null/empty exit-code value and treated it as non-zero.
It stopped before aggTrades acquisition, carrier preparation, or candidate
evaluation.

Both PC2 and local independent checkers correctly fail because no
`run_manifest.json` exists. This is checker-confirmed absence of a market run,
not a failed economic gate.

## Boundaries

- Strict evaluated candidates: `0`
- Candidate generation: `false`
- Optimizer feedback: `false`
- Archive writes: `false`
- OOS reads: `0`
- Promotion or automatic expansion: `false`
- Rescue or second run: not started and not authorized

The completed OI payload is retained on PC2 to avoid unnecessary network use.
It may be reused only after independent hash binding and a separately authorized
source-repaired replacement run.
