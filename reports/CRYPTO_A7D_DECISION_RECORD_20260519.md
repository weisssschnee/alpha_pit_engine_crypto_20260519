# Crypto A7D Decision Record

- decision: `PASS_A7D_FUNDING_SEMANTICS_FOR_RESEARCH`
- generated_at: `2026-05-19T13:14:32Z`
- blockers: `[]`
- warnings: `['exact_match_event_detection_misses_ms_offset_events', 'legacy_long_only_funding_model_materially_differs_from_full_signed_model', 'wrong_lag_future_24h_diagnostic_much_stronger_than_observable', 'observable_fundingcore_fresh_may_negative']`

## Conclusion

A7D audits funding time semantics, event detection, payment sign handling, lag ladder behavior, and May 2026 failure attribution.

Funding data semantics pass for further research when blockers are empty. This does not promote FundingCore or Core4 to alpha shadow proof.

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

With evaluator semantics repaired, continue with funding-regime/risk failure audit. Do not run generator bakeoff or shadow promotion while fresh May and drawdown risks remain unresolved.
