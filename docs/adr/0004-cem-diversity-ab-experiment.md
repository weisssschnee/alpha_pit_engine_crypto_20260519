# ADR 0004: Matched CEM diversity A/B experiment

- Status: Accepted for one bounded development-only experiment
- Date: 2026-07-15
- Scope: non-formal search-instrument A/B
- Authorization: `BOUNDED_EXISTING_RELEASE_DEVELOPMENT_CEM_DIVERSITY_AB`

## Context

The qualified real-data canary showed that the existing `cem_like` lanes repeat
many proposals.  The proposed experiment asks whether a separate
diversity-preserving CEM can improve proposal coverage while remaining directed
by visited strict feedback.  It does not authorize performance search, Alpha
claims, OOS access, promotion, new data, or cross-sprint memory.

The historical baseline's 38 and 58 evaluator calls were observed inside one
eight-lane engine cache.  They are not pure lane-local novelty: the two CEM
transcripts contain 39 and 66 unique candidates.  Comparing those global-cache
misses with an isolated challenger would therefore mix policy diversity with
lane scheduling.

## Decision

Add an independent `cem_diversity_v2` policy without changing `cem_like`.
Each proposal draws its 80/20 exploit/explore branch exactly once.  Duplicate
resampling stays inside that branch, sees only candidate IDs previously emitted
by the same policy instance, and stops after 16 deterministic retries.

Run one fresh, single-lane cache for each frozen seed.  This makes strict calls
equal policy-local first visits and prevents either seed or any historical lane
from donating cache entries.  Preserve the historical 38/58 counts as
provenance, but use the baseline's 39/66 policy-local unique counts as the
primary matched coverage denominator.  A `QUALIFIED` decision must pass both
the user's original thresholds and this stricter matched accounting.

Feedback sensitivity replays use the same seed, step count, RNG semantics, and
update cadence.  The real-feedback replay must reproduce the formal transcript.
The neutral replay supplies the same fixed neutral decision from its first
update.  Because CEM does not condition on elites until eight observations
exist, the first eight proposals still arise from the same pre-warm-up model.
Sampling sensitivity is proven only by a post-warm-up proposal transcript
divergence; final state divergence is recorded but is not sufficient by itself.
The replay never calls the evaluator or changes the formal ledger.

Raw artifact byte hashes live in the artifact manifest.  JSON and CSV artifacts
carry producer/source/data-role/lifecycle/status identity, but do not attempt a
self-referential byte hash inside their own bytes.

The accepted baseline was produced and hashed from a Windows CRLF checkout,
while the closure commit stores normalized LF blobs.  Baseline binding records
and verifies both byte identities; the Git-blob hashes own closure provenance
and the CRLF hashes reproduce the accepted run manifest.

The offline checker is a reproducer, not only a file-hash gate.  It reruns no
market evaluation, but it replays both policies and derives lane metrics,
cache/strict/numeric integrity, distributions, top-16 quality, and the final
four-state decision from the committed event log before accepting the bundle.

## Consequences

The experiment can identify a coverage-and-feedback-direction increment for
this frozen CEM instrument only.  It cannot identify which of duplicate
resampling or the fixed exploration mixture caused the increment, and it cannot
support economic, OOS, cross-algorithm, scaling, or promotion claims.

The accepted closure tag and the qualified canary evidence remain immutable.
