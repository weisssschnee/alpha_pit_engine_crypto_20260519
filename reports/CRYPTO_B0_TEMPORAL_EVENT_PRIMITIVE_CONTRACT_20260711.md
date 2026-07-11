# Crypto B0 Temporal/Event Primitive Contract

Decision: `PASS_B0_TEMPORAL_EVENT_PRIMITIVE_CONTRACT`

- event time: underlying phenomenon time
- observable time: first system-known time
- maturity time: value/window/cashflow completion time
- usable time: `max(observable_time, maturity_time)`
- PIT: only usable records at or before decision time
- event/state to reward in B0: `false`

Canonicalization normalizes durations and parameters. Equivalence additionally requires identical source, event identity, observability, maturity, and tolerance contracts.
