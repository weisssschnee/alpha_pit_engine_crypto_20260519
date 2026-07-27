# Crypto Search Surface Integration V1

- Status: `PASS_ACTIVE_SEARCH_CARRIERS_WITH_DECLARED_FIELD_HOLDS`
- Declared engineering fields: `260`; runtime-active: `235`; explicitly held: `25`.
- Runtime materialized/compiler/matched fields: `235` / `235` / `235`.
- Broad39 and Core3 81 remain independent; no joint 120-channel panel was created.
- Candidate support is PIT base eligibility intersected with finite values for exactly the candidate raw fields.
- aggTrades Top200 is runtime-active at `44/44` delivered fields.
- OI/mark retains `25` source-unavailable zero-support fields; they were not filled or synthesized.
- No market search, pair evaluation, reward read, sealed read, Alpha claim, or promotion occurred.

## Data planes

| Plane | Fields | Materialized | Compiler reachable | Blocked |
|---|---:|---:|---:|---:|
| AGGTRADES_TOP200_DELIVERED | 44 | 44 | 44 | 0 |
| BROAD_PANEL_BASELINE | 39 | 39 | 39 | 0 |
| CORE3_MICROSTRUCTURE_PILOT | 81 | 81 | 81 | 0 |
| LIQUIDATION_DELIVERED_QUARANTINED | 7 | 0 | 0 | 7 |
| OI_MARK_RANKS51_200_DELIVERED | 96 | 71 | 71 | 25 |
| OI_MARK_TOP50_RAW | 96 | 0 | 0 | 96 |

## Boundary

This is engineering reachability, not research admission. Existing instrument-identity, PIT-universe, source-coverage, liquidation, and Top50 raw-consumer holds remain in force.
