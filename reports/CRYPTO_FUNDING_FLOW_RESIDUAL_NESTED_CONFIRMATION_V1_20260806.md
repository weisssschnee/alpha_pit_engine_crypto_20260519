# Crypto Funding-Flow Residual Nested Confirmation V1

## Research conclusion

**No economic result was observed.** The single authorized diagnostic failed
closed before evaluating any candidate. It neither supports nor rejects the
funding-flow residual mechanism, the R3 anchor, its local parameter basin, or
the swapped-timescale placebo.

This was an operational authority-portability failure, not a negative market
result. Although reuse of the development-validation interval was explicitly
authorized as `ADAPTIVE_DIAGNOSTIC_ONLY`, neither Validation-A nor Validation-B
was read.

## Exact outcome

- Producer: `da9e1943fa57e2062f7a7b71bf22c91469382619`
- PC2 task: `CryptoSearch-PC2-FundingFlowResidualConfirmationV1-20260806`
- Task result: exit `1`
- Frozen grid: 81 main + 81 exact swapped-timescale placebo candidates
- Completed market candidates: `0`
- Validation-A read: `false`
- Validation-B read: `false`
- Holdout/OOS reads: `0 / 0`
- Checkpoints, final decision, run manifest: absent
- Research decision: `NOT_OBSERVED_NO_MARKET_EVALUATION`

The producer reached economic-context construction and rejected the checkout
with `SEARCH_ECONOMIC_RECEIPT_BLOCKED`. The frozen economic receipt contains
byte-level component hashes, while the PC2 sparse Windows checkout had changed
line endings. All listed component hashes consequently failed before worker
submission.

## Preserved evidence

The authoritative partial runtime was copied back without modification:

- `candidate_grid.parquet`: `120A3B1DF07535D80C5FACF63C1E2273600784F12C8AB5EDD749AEAE72804811`
- `paired_grid.parquet`: `F293E5BBD4AAAC1132BD4E9E52D2CB8A2CC2A2D0C51FC3B6EB223CB270416E8D`
- `frozen_contract.json`: `D747C0D649F84950C2C317C5B254DA9C1A1AC9EAD2A6631B48C9AABC4BF9A62D`
- `producer_status.json`: `64C16A427BEF7C2D0E81B0BEEAE77B5DB2FAF71252AC59203886346E97288F1C`
- launcher manifest/stdout/stderr were also hash-matched against PC2.

The seven-file closure bundle SHA256 is
`F7B723E6C8A662E26BE563D2C7E832AD093315076FF436CB06F0C784E6990285`.
The committed `partial_artifact_manifest.json` records all seven PC2 hashes;
the manifest itself is closure metadata and is not included in that bundle.

## Closure and prevention

The run authorization is consumed. No restart, rescue rerun, reseed, tuning,
second task, optimizer feedback, archive write, OOS, holdout, promotion, or new
Arena occurred.

The no-market preflight now resolves the complete economic authority before
launch. A checkout with altered component bytes will therefore fail during
preflight, before a runtime or scheduled market task is created. Any future
attempt requires new explicit authorization and an exact-byte PC2 checkout; it
cannot reuse this consumed receipt.

The existing CURRENT Search capability overlay records this consumed invalid
diagnostic without a new node or authority transition. Its bounded maintenance
attempt returned `BLOCKED / AUDIT_UNAVAILABLE` because the Python audit timed
out; generated CURRENT was therefore left unchanged and is not claimed fresh.

Closure verification: 468 tests passed with the existing NumPy
degrees-of-freedom warning.
