# ADR 0008: Search Engine V1 post-audit remediation and qualification suspension

- Status: Accepted
- Date: 2026-07-27
- Remediation source: `dadb10059629b8d68da546c5b92a163aa67d8065`
- Supersedes: Real policy-upgrade canary and Search Engine V1 future-new-data
  component qualification only

## Context

The completed Broad 39 Search Engine V1 campaign remains an intact engineering
run: 20,000 strict candidates, 10 atomic checkpoints, verified receipts, and
zero sealed reads still reconcile. A later source-and-artifact audit found that
its research qualification was not reliable:

1. `active_universe_size`, `age_percentile_active_universe`, and
   `history_length_hours` were generated inside source partitions instead of
   after the joined asset-by-time panel was complete.
2. The 4h overlapping-return `net_lcb` used an iid hourly standard error.
3. The candidate ledger did not persist the full primary, control, and
   incremental monthly economic waterfall.
4. Cost sign-flip and turnover/cost threshold diagnostics were not separately
   identifiable.

The first two defects affect behavior identity and primary reward authority.
The old campaign therefore cannot qualify search arms for a future Arena even
though its files, deterministic replay, checkpoint restoration, and counting
contracts remain valid engineering evidence.

The preceding real policy-upgrade canary used the same legacy raw-cache identity
and pair evaluator. Its engineering execution evidence remains intact, but its
future-Arena qualification is suspended by the same defects.

## Decision

1. Preserve `runtime/crypto_search_engine_v1_20260721` and its cache as immutable
   historical evidence. Do not rewrite, relabel, or rescue-rerun it.
2. Suspend the future-new-data qualification from both the real policy-upgrade
   canary and Search Engine V1, including canonical typed random, real/lite CEM,
   typed evolution, Hierarchical Typed CEM V2, Typed Evolution V2, and the
   per-run Behavior Archive. The old Search Engine checker must report
   engineering `PASS` and component qualification `HOLD` as independent
   dimensions.
3. Raw-panel cache schema 2 must rebuild all three context fields only after all
   source segments and assets are joined. Missing context fields or an
   unvalidated legacy cache fail closed.
4. Behavior-contract freezing must verify that each hourly
   `active_universe_size` is cross-sectionally constant and equals the finite
   observed asset support before PIT regime thresholds are frozen.
5. The strict pair evaluator must use a horizon-aware Newey-West/Bartlett
   standard error with `horizon - 1` dependency lags. Monthly-block LCB remains
   diagnostic and cannot replace the strict reward authority.
6. Future ledgers must retain primary, control, and incremental scalar metrics
   and monthly waterfalls. Gross-positive-to-net-nonpositive cost sign-flip,
   cost-threshold violation, and turnover-threshold violation are distinct
   diagnostics.
7. Requalification requires a separately authorized, fresh-state run over a
   newly built schema-2 cache. This ADR does not authorize a cache build,
   current-data rerun, new-data Arena, OOS, challenge, promotion, latent model,
   or larger budget.

## Consequences

- The old 20k artifact bundle remains reproducible engineering evidence, not
  research admission or economic evidence.
- Previously reported arm productivity and behavior-family conclusions are
  historical diagnostics only and cannot allocate future budget.
- The repaired code is fail-closed but unqualified until a new campaign
  exercises it under an authorized data contract.
- CURRENT keeps the existing Search Engine V1 capability node and records the
  qualification suspension; no new Graph layer or replacement authority is
  created.
