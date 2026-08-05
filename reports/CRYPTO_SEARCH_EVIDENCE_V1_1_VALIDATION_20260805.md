# Crypto Search Evidence V1.1 Champion Validation

- Status: `ENGINE_RUNTIME_WRAPPER_FAILED_NO_CHECKPOINT`
- Producer source: `5fd83536cc84121636a28a6f09b3de3b8e5c8636`
- PC2 job: `job_20260805_105900_5fd835`
- Frozen cohort: 49 final positive V1.1 behavior-family champions; selection SHA256 `C3BD1C0D0940BEE2FAE41B51BD94D11B3684CD93B4E9AD84D125AEC0D5A746DE`.
- Contract: Binance USD-M delayed-open target, frozen train direction, existing mapping/evaluator/reward, 5 bps cost, development validation `2025-11-01` through `2026-01-01`.

## Terminal fact

Remote selection and all 49 static typed reconstructions passed before the validation read. The PC2 wrapper then promoted a NumPy `RuntimeWarning` written to stderr into a terminating PowerShell `NativeCommandError` because the wrapper used `ErrorActionPreference=Stop`. The Python parent was killed after starting one worker. That orphan worker was stopped only to release its inherited pipe and memory.

No `checkpoint_000`, candidate ledger, final decision, or run manifest was produced. Therefore the auditable completed candidate count is zero. PC2 and local independent checkers both fail exactly on the missing candidate ledger. This is a runtime-wrapper failure, not a candidate, evaluator, economic, validation, or Alpha result.

Closure verification passes 435 repository tests. The suite emits the same pre-existing NumPy degrees-of-freedom warning that exposed the wrapper defect; the warning is diagnostic and the test suite itself passes.

## Boundaries

- No restart, backfill, reseed, tuning, or rescue rerun was started.
- No optimizer feedback, policy memory, or archive write occurred.
- Holdout/OOS read count is zero; no promotion, challenge, recent, May-stress, forward, or automatic expansion occurred.
- The one-time validation authorization is consumed. Another attempt requires a new explicit authorization; the present run cannot be cited as migration evidence.
