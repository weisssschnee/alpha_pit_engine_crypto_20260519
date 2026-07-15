# ADR 0003: Bounded real-data lazy-search instrument canary

- Status: Accepted
- Date: 2026-07-15
- Scope: development-train-only execution qualification
- Authorization: `BOUNDED_EXISTING_RELEASE_DEVELOPMENT_CANARY`

## Context

The prior capability harness proved that canonical primitives, explicit mappings, strict feasibility feedback, and four search-policy shapes could execute on synthetic planted targets. It did not prove that the same causal chain worked on an existing market-data release, and its fixed nine-proposal family fixtures were not a lazy search instrument.

The accepted frontier closure remains immutable. This canary must neither modify it nor open validation, holdout, challenge, recent, forward, May stress, 2026 data, promotion, new-data integration, historical runners, or cross-sprint adaptive memory.

## Decision

Create `alphafactory_crypto.instrument_canary` as a bounded execution instrument with this fixed causal order:

1. Load only the explicitly enumerated core-10, January-June 2024 development view of the existing native aggTrades release.
2. Generate one structural proposal from a 9,576-candidate typed grammar without materializing the universe.
3. Fail closed through a content-hash-bound authorization receipt before reading the candidate field.
4. Apply one frozen field representation, the canonical primitive authority, and the mechanism-derived canonical portfolio mapping.
5. Evaluate the mapped portfolio with full-L1 5 bps cost, including initial establishment and terminal liquidation.
6. Expose the exact visited candidate's train-only strict-feasibility decision to its policy, then update that policy.

Four generative policies are fixed: canonical typed random, CEM-like, UCT/UCB-like, and evolutionary mutation. Each is single-flight and can observe feedback only through a candidate-bound update. A run-private global cache prevents duplicate first evaluations; the engine is single-use so its hard cap cannot reset.

The feature bucket at `t` is observable at `t+1h`; execution is at `t+2h`. Targets are `log(close[t+2h+h] / close[t+2h])` for `h in {1,4}`. A 4-hour proposal is executed as four equal-capital offset sleeves, each rebalanced every four hours. This avoids pairing overlapping four-hour returns with impossible full-capital hourly rebalancing.

The numerical strict-feasibility thresholds remain frozen, but their old synthetic-only scope is superseded by a content-hash-bound real-data development-canary capsule. This changes scope, not thresholds. The six monthly blocks participate in train feedback and are explicitly not OOS blocks.

Before the formal 1,024-proposal run, a 32-candidate affine-stride cost preflight withholds feedback, disables policy updates, and persists no economic metrics. These evaluations count toward the 2,048 first-evaluation hard cap.

## Assurance

- Authorization receipts bind genome, field/representation, primitive and parameters, family-derived mapping and hash, target/horizon, PIT/lag, cost, real-data feedback capsule, release view and bundle hashes, source commit, and cache identity.
- Materialized arrays are read-only; the evaluator replays the canonical mapping and verifies candidate, signal, weight, feasibility, and sparse support identities.
- The evidence builder independently recomputes every feedback decision and the preregistered top/random/high-cost/high-concentration/low sample, checks pairwise ordering, rejects invalid-field/alias/mapping/lag decoys before reads, and replays policy transcripts without market data.
- Formal evidence generation requires a clean committed source tree and binds every artifact to that source commit.

## Consequences

A qualified result means only that the bounded real-data lazy-search instrument executed according to its frozen contracts. Development survivors are not Alpha, OOS proof, promotion candidates, or authorization to expand the search. Ordinary LCBs are not corrected for serial dependence or multiple testing.

The old release qualification-index mismatch is recorded as superseded provenance; the accepted tag and its original artifacts are not rewritten.

## Evidence entrypoints

- Contract: `config/crypto_real_data_instrument_canary_v1.json`
- CLI: `scripts/crypto_real_data_instrument_canary.py`
- Runtime bundle: `runtime/crypto_real_data_instrument_canary_20260715/`
- Report: `reports/CRYPTO_REAL_DATA_INSTRUMENT_CANARY_REPORT.md`
