# Crypto P1 G2 Operational Continuation V1 — 20260816r3

## Outcome

The checkpoint-preserving operational successor completed the originally authorized `20,000 strict` train-only question. It preserved the restore-verified r2 prefix at `12,000 strict / 479,114 attempts`, imported the exact adaptive/economic state, and continued only rows `12,001..20,000`. The old r2 runtime remains immutable and is not reinterpreted as a completed 20k result.

`NEXT_DECISION = P1_HYPOTHESIS_FAMILY_WEAK`

The conclusion is family-local, not a global Search Core regression. P1 G2 received 14,000 strict evaluations and produced 1,782 dual-positive plus 162 replicated rows, but zero matched-positive rows, zero 0.90 economic clusters and zero new HQ realizations. The unchanged P4 lane remained healthy with 856 matched-positive rows from 3,000 strict evaluations.

No follow-up search, validation, OOS, holdout, forward, promotion or sealed read was started.

## Bound lineage and identities

- Source durable runtime: `crypto_temporal_p1_semantic_supply_expansion_v1_block_robust_v2_20260816r2`
- Source durable boundary: `12,000 strict / 479,114 attempts`
- Continuation runtime: `p1g2_opcont_v1_20260816r3`
- Continuation implementation: `55df1cda91a1d232904b09df9e447f79c9cee11b`
- Pure authorization: `043da5dc478e0b81ba7cca168cf10562c84a057e`
- Authorization SHA-256: `A795C6A2398F1184EEC355001A4A732A5A289DCD5DA5C9CA62533F142826B960`
- Migration receipt SHA-256: `4555BEBBF14D3400FE8FC61B2D167ED07E5BFDC26FA8063B2B63E7FBE547BF53`
- Imported manifest SHA-256: `B8D2B51B575A77CA0345FC1DEC6E8B1188D0F43843D4C2222F8329E75C0FD81D`
- Final checkpoint state SHA-256: `713CEE709C71BAE83234419D325988916B11487B3B782C904FCCA503BD60C747`
- Candidate ledger: `20,000 rows / 236,034,747 bytes / 2FC6B541EAE9AE04915034B33068BF32E1BC48BD1851F64B51D6CCED919447D9`
- Run result SHA-256: `B03DAC2D0C0D850C2262275B949BEBABEA43798310449370AA1A29B8AB33CDC7`
- Final analysis SHA-256: `4E78E555FFDBB6BC41CB59B9DA216287980D90F07689C6C53EC45369674DFA0B`

The migration receipt proves exact equality for ledger contents/order, candidate IDs, Block Robust V2 payloads, Behavior Archive, policy populations and RNG, dispatcher memory, realization/QD state, attempted IDs, generation attempts, arm/lane counters, seed and catalog identities, and market/economic identities. Only successor metadata, authorization, resource-ceiling and migration-receipt metadata changed.

## Search result

| Measure | Result |
|---|---:|
| strict | 20,000 |
| raw attempts | 756,099 |
| matched-positive | 956 |
| replicated candidates | 3,127 |
| P1 G2 strict / matched / replicated | 14,000 / 0 / 162 |
| P1 G1 strict / matched | 3,000 / 100 |
| P4 strict / matched / replicated | 3,000 / 856 / 1,376 |
| P2 strict | 0 |
| P3 strict | 0 |

The 500,000 raw-attempt terminal from r2 is classified as `OPERATIONAL_RAW_ATTEMPT_BUDGET_EXHAUSTED`, not research invalidity. The successor's fixed 1,250,000 operational ceiling was not reached; the scientific 20,000 strict cap stopped the run normally.

All four native continuation checkpoints were restore-verified:

| Checkpoint | Strict | Attempts |
|---|---:|---:|
| checkpoint_006 | 14,000 | 553,927 |
| checkpoint_007 | 16,000 | 623,836 |
| checkpoint_008 | 18,000 | 692,823 |
| checkpoint_009 | 20,000 | 756,099 |

## P1 G2 attribution

Condition role:

| Role | Strict | Dual-positive | Replicated | Matched |
|---|---:|---:|---:|---:|
| FUNDING | 5,828 | 297 | 21 | 0 |
| OI_LEVEL | 8,172 | 1,485 | 141 | 0 |

Condition primitive:

| Primitive | Strict | Dual-positive | Replicated | Matched |
|---|---:|---:|---:|---:|
| MultiScaleRelation | 3,760 | 702 | 41 | 0 |
| Persistence | 7,684 | 918 | 110 | 0 |
| Transition | 2,556 | 162 | 11 | 0 |

Condition operator:

| Operator | Strict | Dual-positive | Replicated | Matched |
|---|---:|---:|---:|---:|
| ConditionGate | 9,385 | 1,416 | 97 | 0 |
| StateModulation | 4,615 | 366 | 65 | 0 |

All eight observed P1 G2 semantic program IDs had zero matched-positive rows. This rules out a single missing condition role, primitive or operator as the explanation for the failure.

## Economic clusters and realization depth

Real economic clusters, not behavior-family counts:

| Similarity | Clusters | New clusters |
|---|---:|---:|
| 0.95 | 72 | 12 |
| 0.90 | 50 | 3 |
| 0.85 | 45 | 2 |

Overall P1/P4 search depth:

- HQ basins deepened: `19`
- new unique HQ concrete realizations: `81`
- 0.90 P1 G2 economic clusters / new clusters: `0 / 0`
- P1 G2 new HQ concrete realizations: `0`
- existing HQ basins deepened by P1 semantic breadth: `1`

Depth increments versus the frozen baseline:

| Dimension | Increment |
|---|---:|
| asset-selection realizations >= 2 | +7 |
| mapped-weight realizations >= 2 | +4 |
| mapped-weight realizations >= 3 | +0 |
| raw-field realizations >= 2 | +6 |
| turnover realizations >= 2 | +0 |

## P4 health and operation attribution

P4 remained frozen and healthy: `3,000 strict / 856 matched-positive / 28.53% matched density`, with 39 real 0.90 clusters and 18 HQ basins deepened in the full lineage diagnostic.

Full-run operation attribution:

| Operation | Proposals | Dual-positive | Matched | 0.90 clusters | New 0.90 clusters | HQ basins deepened | New HQ realizations |
|---|---:|---:|---:|---:|---:|---:|---:|
| parameter mutation | 4,135 | 1,961 | 239 | 42 | 2 | 19 | 81 |
| mechanism mutation | 14,080 | 1,797 | 1 | 1 | 0 | 1 | 9 |
| crossover | 1,785 | 1,753 | 716 | 26 | 1 | 19 | 81 |

These rows are overlapping basin-level contribution views; HQ counts must not be summed across operations.

## Dispatcher efficiency

- legal proposals generated/scored: `695,306 / 695,306`
- dispatcher selections: `60,793`
- strict evaluations: `20,000`
- exploitation / exploration selections: `51,556 / 9,237`
- average / median legal pool: `11.437 / 12`
- pools under eight: `4,920`
- proposal CPU time: `7,864.328125 seconds`
- known low-value generation: role `7,254`, operator `0`, component `0`

The dispatch machinery remained productive and reached 20k under the fixed operational ceiling. The terminal economic weakness is therefore attributed to P1 G2 conversion under the frozen semantic family, not to proposal-supply exhaustion or a global Search Core failure.

## Block Robust V2 and canonical checker

- Ordering authority: `DEVELOPMENT_THREE_BLOCK_ROBUST_ORDERING_V2`
- Matched-control schema: `HIERARCHICAL_A_B_AB_ABC`
- partition: train only
- 171 P1 G2 catalog identity unchanged
- 180 P1 G1 identity set unchanged
- canonical checker: `PASS`
- checker SHA-256: `3D6F3D6BB7EF3B10B626C6D226F868399D04861AC1371064E6DE8CF060E4A6CB`
- validation/OOS/holdout/forward/promotion/sealed reads: `0 / 0 / 0 / 0 / 0 / 0`
- P2/P3 strict: `0 / 0`
- automatic next run: `false`

The pre-strict Windows path-length failure created no new strict row, forbidden read or economic-state advancement. Its failed runtime remains preserved as engineering evidence, and the same frozen identities passed launch preflight before the productive continuation.

## Final decision

`P1_HYPOTHESIS_FAMILY_WEAK`

The experiment completed validly and does not support P1 G2 semantic expansion under the frozen family: broad dual-positive and some replication did not convert into a single matched-positive or economic basin. P4 and the dispatcher stayed healthy, so `GLOBAL_SEARCH_CORE_REGRESSION` is not supported. The run is not research-invalid, and no next validation, OOS, promotion or search is authorized by this closure.
