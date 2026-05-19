# Crypto A7D Decision Record

- decision: `HOLD_A7D_FUNDING_SEMANTICS_UNRESOLVED`
- generated_at: `2026-05-19T13:02:00Z`
- blockers: `['funding_event_detection_exact_match_misses_events']`
- warnings: `['wrong_lag_future_24h_diagnostic_much_stronger_than_observable', 'observable_fundingcore_fresh_may_negative']`

## Conclusion

A7D audits funding time semantics, event detection, payment sign handling, lag ladder behavior, and May 2026 failure attribution.

If blockers are present, FundingCore and Core4 remain data-semantics unresolved and must not enter alpha shadow proof.

## Confirmed

- `latest_known_funding_rate` is joined by backward asof from fundingTime.
- `next_funding_rate` is not present in the current gold panel and remains forbidden.
- A7D does not run new search or tune formulas.

## Not Confirmed

- alpha shadow proof
- paper/live readiness
- production execution
- generator/reward maturity

## Required Next Action

If event detection/payment blockers are present, fix evaluator funding payment semantics and rerun A2.6 onward before using funding results for promotion.
