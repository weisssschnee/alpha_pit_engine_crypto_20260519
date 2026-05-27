# Crypto A7E Funding Evaluator Repair Record

- decision: `PASS_EVALUATOR_REPAIR_FOR_RESEARCH`
- generated_at: `2026-05-19`
- scope: evaluator semantics only; no formula search, no cluster selection, no shadow promotion

## Repairs

1. Funding event detection now uses observable `fundingTime_ms` changes in the backward-asof 1h panel.
   - Old behavior: exact `open_time_ms == fundingTime_ms` matching.
   - Problem: Binance funding events can carry millisecond offsets, so exact matching missed valid events.
   - New behavior: first row where `fundingTime_ms` changes is treated as the observable funding event; first row per symbol is excluded.

2. Book-level funding cashflow now uses signed long/short semantics.
   - Positive funding means longs pay and shorts receive.
   - `funding_drag = sum(position * funding_cost)`; drag can be negative when the book receives funding.

## Rerun Evidence

### A7D Funding Semantics

- decision: `PASS_A7D_FUNDING_SEMANTICS_FOR_RESEARCH`
- blockers: `[]`
- observable change event detection rate: `1.0`
- within 1h event visibility rate: `1.0`
- exact match event detection rate: `0.6602760736196319`
- evaluator funding payment model: `full_signed_long_pays_short_receives`

Warnings remain:

- `exact_match_event_detection_misses_ms_offset_events`
- `legacy_long_only_funding_model_materially_differs_from_full_signed_model`
- `wrong_lag_future_24h_diagnostic_much_stronger_than_observable`
- `observable_fundingcore_fresh_may_negative`

### A7B Funding Baseline

- decision: `HOLD_A7B_FUNDING_BASELINE_DOMINANCE_RISK`
- Core4 recent OOS 10bp annualized: `0.7165`
- Funding-only recent OOS 10bp annualized: `0.9279`
- Core4 fresh May 10bp annualized: `-2.6313`
- Funding-only fresh May 10bp annualized: `-2.7061`
- Core4 residual vs funding recent OOS 10bp annualized: `0.3550`
- Core4 residual vs funding fresh May 10bp annualized: `-0.7373`

Interpretation: funding-only remains the dominant simple explanation. Core4 has residual signal in recent OOS, but not enough to overcome fresh May failure.

### A7C FundingCore

- decision: `HOLD_FUNDINGCORE_ALPHA_SHADOW_PROOF`
- validation 10bp annualized: `2.1062`
- recent OOS 10bp annualized: `0.9279`
- fresh May 10bp annualized: `-2.7061`
- recent OOS compounded max DD: `-0.6068`
- blocker: `fresh_may_10bp_negative`

Interpretation: FundingCore is retained as a mandatory benchmark and research baseline. It is not promoted to alpha shadow proof.

## Current State

The crypto funding line is no longer blocked by the specific event-detection bug. It remains blocked by strategy evidence:

- fresh-forward May is negative;
- drawdown is still large;
- FundingCore explains most of Core4;
- future/wrong-lag diagnostics remain unusually strong and must stay as warnings.

## Next Action

Do not run generator bakeoff or expand search yet. Next valid step is a funding-regime/risk failure audit:

- identify whether May 2026 is a funding-regime family failure;
- split losses by funding sign, funding magnitude, volatility, basis, and symbol;
- test whether a predeclared funding-regime gate can reduce the fresh-forward failure without using future labels.

