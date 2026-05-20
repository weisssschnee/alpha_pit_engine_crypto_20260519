# Crypto A7D Funding Semantics Reconfirmation

- date: `2026-05-20`
- decision: `A7D_RECONFIRMED_PASS_FOR_RESEARCH_ONLY`
- source_audit: `CRYPTO_A7D_FUNDING_TIME_SEMANTICS_AUDIT_20260519.md`
- source_decision: `PASS_A7D_FUNDING_SEMANTICS_FOR_RESEARCH`
- executes_search: `False`
- executes_replay: `False`
- authorizes_alpha_proof: `False`
- authorizes_shadow_paper_live: `False`

## Reconfirmation

A7D already executed the required funding time-semantics audit. It covered the funding field contract, timestamp alignment, funding lag ladder, funding payment/sign handling, Core4 residual by funding version, and May 2026 failure attribution.

The 2026-05-19 A7D result remains valid as a research-only semantics pass:

- `latest_known_funding_rate` is joined by backward asof from `fundingTime_ms`.
- `next_funding_rate` is not present in the current gold panel and remains forbidden as a signal.
- `feature_time < execution_time <= label_start_time` has zero observed violations.
- `funding_field_time <= feature_time` has zero observed violations.
- observable funding-change event detection rate is `1.0`.
- time-shuffled and symbol-shuffled funding variants are weak/negative, so ordinary shuffle placebo does not explain FundingCore.
- the signed funding payment model is now explicit: positive funding means longs pay shorts.

## Retained Warnings

The following warnings remain active and must not be hidden:

- `exact_match_event_detection_misses_ms_offset_events`
- `legacy_long_only_funding_model_materially_differs_from_full_signed_model`
- `wrong_lag_future_24h_diagnostic_much_stronger_than_observable`
- `observable_fundingcore_fresh_may_negative`

These warnings do not invalidate funding field semantics for research, but they block promotion of FundingCore/Core4 into alpha shadow proof.

## Current Interpretation

Funding semantics are not the current hard blocker for continuing research. The clean interpretation is:

- `FundingCore` is a mandatory benchmark / research baseline.
- `Core4` is a research object, not independent alpha proof.
- A6 dry-shadow remains engineering telemetry only.
- A7.3 generator/reward bakeoff remains blocked unless a later design explicitly residualizes against FundingCore and preserves all A7D constraints.
- paper/live/shadow promotion remains blocked.

A7D does not authorize ignoring later negative evidence. In particular, the later A7M-2E result still holds:

- fast replay parity passed;
- A7M-2 survivor labels collapse after May stress and cap refactor;
- A7M-2F and A7M-3 remain unauthorized under the current objective.

## Next Valid Use

A7D can be used as a field-semantics foundation for later crypto work, but any future search must be FundingCore-aware:

- report raw performance and residual vs FundingCore/Core4;
- keep May as stress-only, not ranking/reward/generation input;
- keep funding payment/sign accounting explicit;
- treat wrong-lag future strength as a warning, not as usable signal.

