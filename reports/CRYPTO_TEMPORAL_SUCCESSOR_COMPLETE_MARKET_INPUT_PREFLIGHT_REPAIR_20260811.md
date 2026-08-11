# Crypto Temporal Successor complete market-input preflight repair

Status: `SOURCE_REPAIRED_NOT_AUTHORIZED`

The authorized replacement task `job_20260811_220208_ed60dd` did not produce a
successor search result. It restored the valid 30k prefix, wrote the one-time
launch claim, and then failed during worker initialization because the separate
Binance execution-target cache was absent from the clean PC2 checkout.

Observed terminal facts:

- `additional_strict_evaluated = 0`
- `evaluation_batch_count = 0`
- `completed_full_checkpoint_count = 0`
- `cumulative_valid_strict = 30000` (restored source prefix only)
- root exception: `ECONOMIC_RECEIPT_TARGET_CACHE_MISSING`
- missing path: `.cache/crypto_search_engine_v1_4/binance_open_target_v1/metadata.json`
- validation/OOS/holdout/promotion reads: forbidden and absent
- sealed reads: `0`

The launch claim recorded zero market-array reads and zero candidate evaluations
at claim time. After the claim, the source store was opened by the worker
initializer before the target-cache check failed. Therefore this report does not
claim that the whole task was market-free; it claims only the stronger facts
that no initializer reached `INITIALIZER_READY`, no evaluation batch returned,
and no additional strict row was written.

The retained PC2 source workspace contains the exact target bundle:

- target identity: `27F780D458CBA50D6C82393F7DFDA396AC3994724645D112C4F8EF0ACDA865F0`
- source carrier identity: `E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA`
- files: `3`
- bytes: `10,170,182`
- target files: `target_return_1h.npy`, `target_return_4h.npy`

The source repair now verifies both required cache roots before any future launch
claim:

1. the manifest-bound 115-field carrier bundle;
2. the independent Binance open-price target bundle bound by the economic
   receipt.

The target preflight checks target identity, source carrier identity, source
shape, timestamp hash, execution fields, every declared target-file hash/size,
and a complete directory bundle. It hashes files but never calls `numpy.load` or
evaluates a candidate. The authorization materializer records both bundles in
the schema-2 receipt.

Both attempted runtimes are terminal and must not resume. The repository is
returned to `IMPLEMENTED_NOT_AUTHORIZED`. A further PC2 task requires a new,
explicit, exact-SHA authorization; this repair itself does not authorize it.
