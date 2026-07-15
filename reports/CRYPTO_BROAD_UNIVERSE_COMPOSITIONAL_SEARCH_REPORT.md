# Crypto Broad-Universe Compositional Search Epoch 1

## Decision

`CRYPTO_BROAD_SEARCH_DATA_UNIVERSE_BLOCKED`

The requested large Alpha search did not start.  Existing data qualifies neither
the broad cross-sectional mode nor the explicit core time-series fallback.

## Data gate

- Broad archive: 176 observed assets, 6 continuous months; required 40 assets and 18 months.
- Core native aggTrades: 10 assets, 6 continuous months; required 24 months for the fallback.
- Failure classes: TIME_HISTORY_TOO_SHORT, SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED, ORDER_FIELD_COVERAGE_FRAGMENTED, EXPLICIT_CORE_TIME_HISTORY_TOO_SHORT.
- Universe provenance: the historical seed came from a 2026 current exchangeInfo/metrics probe, so delisted historical contracts may be omitted.
- Sealed reads: 0.

## Current grammar

- Frozen support: 9576 exact candidates.
- Structure: one field, one representation, one primitive, zero cross-field interactions.
- Deterministic sample: 2000 candidates; 951 numeric, 931 rank, 1242 mapped-weight, and 1214 behavior identities.
- Grammar decision: `CRYPTO_COMPOSITIONAL_GRAMMAR_BOTTLENECK_CONFIRMED`.

## Experimental replacement

The closure includes a small typed DAG and matched-ablation contract, but it is
not connected to the formal evaluator and was not economically evaluated.  Its
lifecycle remains `EXPERIMENTAL_CURRENT_NON_FORMAL`.

## Search budget

Proposal attempts: 0. Strict primary/control pairs: 0. The 64-pair cost
preflight and the 500,000-attempt search are gated behind qualified data and
were intentionally not run.
