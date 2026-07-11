# Crypto B0 Future Wrong-Lag Negative Control

Decision: `PASS_B0_FUTURE_WRONG_LAG_CONTROL_HARNESS`

`future_wrong_lag_24h` applies the signal from t+24h at t, leaving the final 24 hours unavailable. It is deliberately impossible under PIT semantics.

- clean fixture: `PASS_FUTURE_WRONG_LAG_WEAKER`
- leakage fixture: `FAIL_FUTURE_WRONG_LAG_DOMINATES`
- strict reward integration: implemented
- production execution: not run during HOLD_RESEARCH
- candidate feedback authorization: false
