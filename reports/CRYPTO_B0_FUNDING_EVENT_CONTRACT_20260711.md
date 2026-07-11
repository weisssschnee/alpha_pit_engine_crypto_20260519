# Crypto B0 Funding Event Contract

Decision: `PASS_B0_FUNDING_EVENT_CONTRACT_AND_AUDIT_HARNESS`

Native venue settlement time defines event identity. Repeated last-known rates are state, not events. Missing native event time fails closed.

Positive funding rate means long pays and short receives; long and short cashflow rates must sum to zero.

## Synthetic Audit Harness

- expected events: `4`
- detected events: `3`
- matched events: `3`
- missed events: `1`
- recall: `0.75`
- precision: `1.0`
- tolerance seconds: `1800.0`
- max absolute timing error seconds: `1200.0`
- cashflow semantics pass: `True`

Production recall remains unmeasured because B0 does not authorize new forward reads or an unsealed truth set.

This contract authorizes audit and Feature/State Fabric input design only. It does not authorize generator, reward, memory, or search use.
