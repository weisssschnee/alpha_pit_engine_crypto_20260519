# ADR 0021: V2.3 Frozen-Cohort OOS Replay

Status: Accepted for one read-only OOS replay on 2026-08-03.

## Decision

Open the previously frozen `2026-01-01` through `2026-07-01` holdout exactly
once and replay all 1,024 successful V2.3 validation-cohort identities.  The
cohort is bound to the committed V2.3 validation ledger and contains 256
candidates each from random stratified, random train-top, Evolution stratified,
and Evolution train-top.  Candidate identity, train-frozen orientation,
train-frozen limiting matched sleeve, horizon, target, mapping, and 5 bps cost
remain unchanged.

The primary OOS estimand is the equal-weight daily total-policy effect across
both preregistered seeds and both 1h/4h horizons:

```text
Evolution train-top - random train-top
```

Proposal-distribution and train-ranker effects are also reported.  Individual
seed/horizon cells are heterogeneity evidence, not an all-cell kill gate.  The
report persists point estimates, seven-day block-bootstrap distributions and
quantiles; it does not retrofit a binary promotion gate.

## Integrity rules

- replay all four frozen cohorts, with no validation-performance filtering;
- persist OOS-local constructibility failures and do not backfill them;
- generate no candidate and import no optimizer, population, archive or policy
  state;
- write no optimizer, archive, policy, scheduler or cross-sprint memory;
- perform no tuning, reseeding, rescue rerun or second OOS read;
- use the existing carrier, compiler, matched evaluator, Binance target,
  mapping and cost implementation;
- checkpoint every 64 candidate identities and restore exactly;
- run heavy evaluation only on company PC2.

## Boundaries

This decision authorizes OOS policy-attribution evidence only.  It does not
authorize challenge, recent, May-stress, forward, promotion, a new search,
candidate selection after seeing OOS, or an Alpha claim.  Results remain
conditional on the existing non-formal Binance execution and fixed 5 bps cost
contracts.  The receipt is consumed after the one replay regardless of result.

## Consequence

V2.3's development all-cell gate no longer substitutes for the direct transfer
question.  The OOS result can show whether the frozen total search policy has a
positive, mixed or negative aggregate effect while retaining seed/horizon
heterogeneity and uncertainty in the evidence rather than hiding them behind a
single conjunction.
