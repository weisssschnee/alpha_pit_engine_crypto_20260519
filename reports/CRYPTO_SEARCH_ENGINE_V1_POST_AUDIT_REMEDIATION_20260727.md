# Crypto Search Engine V1 post-audit remediation

- Decision: `RESEARCH_AND_FUTURE_ARENA_QUALIFICATION_HOLD`
- Remediation source: `369dbb8fadf7a1308fd1820da37e5cd95ffc8450`
- Historical runtime: `runtime/crypto_search_engine_v1_20260721`
- Historical artifact bundle: `2E0EAED26747E1B97F5F4C06482BE61337965DC0CAAA2A5B1C48C06625657288`
- New search or cache build: `NO`
- Sealed reads: `0`

## Audit findings

The joined raw cache inherited partition-local values for
`active_universe_size`, `age_percentile_active_universe`, and
`history_length_hours`. At the 2024 source boundary the active-universe field
collapsed from 176 to 1, age percentile became 1, and history reset instead of
continuing from 744; related history resets also occurred at 2023 month
boundaries. The contaminated fields appeared in 121 of 151 matched-positive
candidates and 51 of 63 matched-positive behavior families. Every behavior
family also used the affected active-universe regime descriptor.

The strict 4h reward LCB used an iid hourly standard error despite overlapping
return sleeves. The ledger retained incremental summary metrics but omitted the
complete primary/control/incremental monthly waterfall. Cost and turnover kill
flags also collapsed to the same threshold diagnostic because fixed cost is a
linear transform of turnover.

These are evaluator and identity defects, not proof that the old data contains
no Alpha. They invalidate the campaign's search-arm qualification and make its
negative or positive reward comparisons unsuitable for economic inference.
The preceding real policy-upgrade canary used the same legacy raw-cache identity
and pair evaluator, so its future-Arena component qualification is suspended as
well; its execution and replay evidence remain historical engineering evidence.

## Remediation

- Cache schema 2 rebuilds the three context fields after the complete
  asset-by-time source join and records the authority in cache identity.
- Missing or legacy context contracts fail closed before a Search Engine run.
- Behavior PIT regimes cannot freeze unless hourly active-universe values equal
  observed cross-sectional support.
- `net_lcb` now uses Newey-West/Bartlett with `horizon - 1` lags while
  preserving missing-hour coordinates.
- Future ledgers persist primary, control, and incremental monthly waterfalls
  and scalar metrics.
- Cost sign-flip, cost-threshold violation, and turnover-threshold violation
  are distinct diagnostics.
- Monthly waterfalls now persist gross, cost, net, and turnover together.
- CPU-hour sums parent proposal/compile/archive/ledger CPU and all worker pair
  evaluation process CPU. Valid exact-unique density uses the exact-unique
  counter, including candidates that fail later matched evaluation.
- Checkpoint state is fully restored and hash-verified in its temporary
  directory; only a manifest already marked restore-verified can be atomically
  renamed to the public checkpoint path.

## Verification

- Targeted search/train tests: `36 passed`.
- Historical checker: engineering integrity `PASS`, strict count `20,000`,
  checkpoints `10`, behavior families `16,712`, errors `[]`.
- Historical component qualification:
  `HOLD_POST_AUDIT_REMEDIATION_REQUIRED`.
- Holds:
  `LEGACY_UNVALIDATED_ACTIVE_UNIVERSE_REGIME`,
  `LEGACY_IID_LCB_ON_OVERLAPPING_HORIZON`,
  `LEGACY_MATCHED_WATERFALL_NOT_PERSISTED`.
- Future-new-data qualified arms from the historical campaign: `[]`.

## Boundary

The historical run, raw cache, checkpoints, and manifests were not modified.
No rescue rerun, new-data Arena, OOS, challenge, recent/May-stress/forward
evaluation, promotion, latent training, relational reopening, or parameter
tuning was performed. Requalification requires separate authorization.
