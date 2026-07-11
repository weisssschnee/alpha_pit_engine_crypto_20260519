# Crypto B0A Frozen Signal Behaviour Qualification

Decision: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`

## Frozen Inputs

- accepted candidate pack SHA256: `65CB07431725FA1CAFF91990BA67305AADAD82616ABA58B2D9010217A5D3946D`
- 33-row alias mapping SHA256: `5667B246E250AF50123B316305E5DA1DE96A846097C888FEA8C10CE1BDCF7EAA`
- observation data release SHA256: `EC4C9F84641C6EBCB218B89AA7F4F248DEA418DC0DF6387A5F2B7BA29B5F9928`
- physical panel container SHA256: `AD75C90E2D3D5AA7FA30D1EDF16502FCB8D6A42E706EBF20B8C56B105E7A46D7`
- field registry SHA256: `C201B87CEBDF17AF3231B7DD8CB8A06B561572E58DAA670D5D82F71F95A7628D`
- materializer code SHA256: `8D714B10AE616B63D717C5C70D58EEE0C56C10BAE70DC91DD714138C6BA5F0B8`
- interval: `2024-01-01T00:00:00+00:00` through `2026-04-30T23:00:00+00:00`
- coordinates: `96 symbols x 20424 hourly timestamps`
- source coordinate coverage: `0.999322692`; missing coordinates are reindexed and preserved in the missingness mask

## Identity Compression

- frozen source-lag survivor mapping: `33 rows -> 18 exact identities`
- accepted behaviour scope: `16 restored aliases -> 6 canonical/exact signals -> 5 activation identities -> 4 behaviour clusters -> 5 economic hypotheses`
- N_eff: `3.000000`
- top-cluster share: `0.500000`
- cross-time slice stability median/min: `1.000000` / `1.000000`

The 33 survivor rows must not be misstated as six exact signals: only the 16 accepted restored rows map to the six accepted exact identities. The remaining 17 survivor rows are frozen provenance but are outside accepted behaviour qualification.

## Reproducibility

- first artifact SHA256: `CD40C5C521DDBC6A2704D5A45A798CF3DAB5A5A7B6D2CD476D28F6BFB30C7D6B`
- repeated reversed-order artifact SHA256: `CD40C5C521DDBC6A2704D5A45A798CF3DAB5A5A7B6D2CD476D28F6BFB30C7D6B`
- reproducible: `True`
- alias reconstruction: `True`

## Boundaries

No return label, reward, new forward/OOS performance, search, candidate modification, candidate selection, scheduler feedback, or memory update was used. PnL/regime remains `SPENT_HISTORICAL_DIAGNOSTIC_ONLY / NO_SELECTION / NO_MEMORY / NO_SCHEDULER_FEEDBACK`.
Phase B1 remains frozen.
