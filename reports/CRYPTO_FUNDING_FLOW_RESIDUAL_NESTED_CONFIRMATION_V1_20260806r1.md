# Crypto Funding-Flow Residual Nested Confirmation V1

- Evidence status: `REUSED_DEVELOPMENT_VALIDATION / ADAPTIVE_DIAGNOSTIC_ONLY`
- Producer source: `3e8d1bbf07303ff983596ea295a3af82fd340b1b`
- Terminal status: `VALIDATION_A_TERMINAL_FAIL_CLOSED`
- Actual research decision: `REUSED_VALIDATION_DIAGNOSTIC_ONLY::FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED`
- Counterfactual preregistered branch: `FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED`
- Validation-B read: `False`
- OOS / holdout reads: `0 / 0`

This run reused a previously read development-validation interval under the
user's explicit one-time override. It can diagnose basin continuity and the
main-versus-swapped-timescale placebo contrast, but it cannot establish unread
migration, OOS qualification, or promotion authority.

## Validation-A family screen

- Gate: `FAIL`
- Main cell median worst-axis net: `-0.00034318043322402545`
- Main cells with both axes positive: `0.07407407407407407`
- Positive funding sources: `0`
- Median main-minus-placebo cell delta: `5.048286306459388e-05`
- Main above placebo cell fraction: `0.6296296296296297`
- Anchor direct-neighbor positive fraction: `0.3333333333333333`

## Validation-B frozen confirmation

- Executed: `False`
- Anchor pass: `None`
- Family pass: `None`
- Source representative median worst-axis net: `None`
- Representative median main-minus-placebo: `None`

No candidate, family, arm, or mechanism is authorized for OOS, promotion,
challenge, forward, or automatic expansion by this diagnostic.
