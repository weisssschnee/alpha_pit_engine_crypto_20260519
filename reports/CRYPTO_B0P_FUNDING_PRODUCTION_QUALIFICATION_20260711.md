# Crypto B0P Funding Production Qualification

Decision: `PRODUCTION_FUNDING_OBSERVATION_QUALIFIED`

- truth/detected/matched: `30636` / `30636` / `30636`
- recall / precision: `1.0` / `1.0`
- misses / false positives / duplicates: `0` / `0` / `0`
- maximum timestamp error: `0.0 seconds`
- maximum observable-time error: `0.0 seconds`
- symbol coverage: `12/12`
- symbol-month coverage: `336/336`
- funding-rate mismatches: `0`
- cash-flow sign semantics: `True`
- non-8h schedule transitions: `0`

Only event identity, event time, funding rate, and observation time were read. Price returns and Alpha reward were not read or computed.
