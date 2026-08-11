# Crypto Temporal Successor Pre-Market Deployment Repair — 2026-08-11

## Result

The authorized PC2 task `job_20260811_212229_f6d45d` is closed as
`PRE_MARKET_DEPLOYMENT_INVALID`. It is not a market or economic result.

## Observed evidence

- Task exit: `FAILED`, exit code `1`.
- Launch claim SHA256:
  `09D63C46C65037823776F91DD2E467BD0CE882C007715E98DE105AA143A0550A`.
- Market arrays read: `0`.
- Candidate evaluations: `0`.
- Sealed reads: `0`.
- Failed runtime files: exactly one, `successor_launch_claim.json`.
- Active successor processes after failure: `0`.
- Exception: `FileNotFoundError` for
  `.cache/crypto_search_engine_v1_4/oi_mark_x_aggtrades_115/metadata.json`.

The deployed checkout contained the tracked aligned-carrier manifest but not
the Git-excluded carrier cache it references. A retained PC2 workspace contains
the cache. The tracked manifest freezes its required content as 122 files,
598,775,942 bytes and bundle SHA256
`340C01BEB680E776F9B2C6024FDD09AB3CDF09B608A4372C3E355AECF7F0CD97`.

## Source repair

The successor preflight now verifies, before creating a launch claim:

1. the tracked aligned-carrier manifest;
2. the manifest SHA256;
3. cache identity SHA256;
4. every required root/field file and its content hash;
5. exact file count, byte count and directory-bundle SHA256.

The check hashes files but does not load market arrays, evaluate candidates or
read a sealed role. Missing or changed cache content fails closed as
`FAIL_CLOSED_BEFORE_MARKET_READ`.

## Unchanged research contract

This repair does not change the valid 30k prefix, suffix exclusion, fresh
Random control, reconstructed CEM/Evolution state, 20/20/60 allocation, 5k
decision cadence, cumulative 50k hard stop, target, mapping, 5 bps cost,
reward, evaluator, validation/OOS/holdout/promotion prohibition, or any formal
authority.

The failed claim is retained and cannot be resumed. A true market run requires
one explicit source-only replacement authorization bound to the failed claim,
repaired implementation, distinct runtime and exact verified cache.
