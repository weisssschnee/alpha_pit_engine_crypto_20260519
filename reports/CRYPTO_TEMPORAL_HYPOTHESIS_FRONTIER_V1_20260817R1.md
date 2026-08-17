# Crypto Temporal Hypothesis Frontier V1 — 20260817r1

## Outcome

The sole authorized train-only frontier runtime completed its fixed `30,000 strict` budget and stopped normally. The canonical checker is `PASS` and returns:

`NEXT_DECISION = HYPOTHESIS_FRONTIER_PASS`

This is a structural frontier/breadth pass, not evidence that P5 or P6 is broadly productive. P5 and P6 each converted only `1 / 12,000` strict candidates into matched-positive rows. Their one independent 0.90 cluster apiece is real train-only novelty, but the conversion rate is too thin to imply validation, promotion or deployability.

No follow-up search, validation, OOS, holdout, forward, promotion or sealed read was started.

## Bound lineage and identities

- Runtime: `crypto_temporal_hypothesis_frontier_v1_20260817r1`
- Implementation: `d8e4845d0acb97bc263dab800ac4ca83b6b57f0b`
- Pure authorization: `fe4cf3ed42080f8616f4c2bfd64e6c541f30ad6e`
- Authorization SHA-256: `48E90D3DCAA3616F126CE8ED07BC3D6CEF19C618D21FB691F6DFD170E0A96C4B`
- Offline preauthorization receipt SHA-256: `AE7B2F8EA92A4B8A8BB7FB23427E797FD6869AF8FE263E596886C38DDD1BB9F0`
- Search task: `job_20260817_040337_2aebcb`
- Analysis/checker task: `job_20260817_132535_80da98`
- Final checkpoint: `checkpoint_014`, restore verified
- Run-result SHA-256: `384D1B72621DAE09EFDBCF2F954E416FA9046BAC42DA37F8C406A853EB7894EE`
- Analysis SHA-256: `6A4E49012DE42A898B6640A37D210508CD4E2EC853A4D6659294DF1F9C648BA3`
- Checker SHA-256: `5A49FAA18875C1F04C67973C0CE82E14A27B873E7D09E4BC994CC681A002613E`

Two earlier PC2 tasks, `job_20260817_040046_11ab33` and `job_20260817_040228_bec08d`, failed in launcher engineering before Python runtime creation and before the first strict evaluation. They are not research runs and were not restarted.

## Historical source-gap salvage and frozen catalog

The source-gap reconstruction used the 16,000-row Mechanism V2.3 train ledger:

- bytes: `81,689,188`
- SHA-256: `B19F0E94B9BB50933E8F6BD6A92754E3D8DC8059968C0D5069E3EF87527456E4`
- historical OOS used as adaptive label: `false`
- source-gap SHA-256: `438D6C667996C4A4FD703ED9D61A5B421FD57ED87F74E809A1DE0CC8E12ED250`

The frozen catalog contains all 111 accepted bounded possibilities: P5 `49`, P6 `62`, across three P5 motifs and five P6 motifs. Catalog SHA-256 is `1E6D6648BDEC6BAE3AADF3E82C3D70D5053FC48B82A73E1BF526835BBD10CAE0`.

The catalog explicitly excludes a full Cartesian product, archived P1 position-first overlap, P4 anchor-only semantics and unregistered primitives not required by the source gap. Historical provenance is bound to the OI/funding queue `0692B1DE...C7E266` and regime-mechanism audit `C7C6369C...BC5E7F`.

## Search result

| Family | Strict | Matched-positive | Density | Replicated |
|---|---:|---:|---:|---:|
| P4 health anchor | 6,000 | 1,263 | 21.05% | 2,550 |
| P5 flow/participation conviction | 12,000 | 1 | 0.00833% | 193 |
| P6 derivative crowding/relative pressure | 12,000 | 1 | 0.00833% | 171 |
| **Total** | **30,000** | **1,265** | **4.22%** | **2,914** |

- Raw attempts: `562,122`
- P1/P2/P3 strict: `0 / 0 / 0`
- Fixed raw-attempt ceiling: `2,000,000`, not reached
- Stop: scientific `30,000 strict` cap
- Automatic next run: `false`

## Real economic breadth

These are canonical economic clusters, not behavior-family counts.

| Similarity | Clusters | New clusters |
|---|---:|---:|
| 0.95 | 78 | 17 |
| 0.90 | 56 | 6 |
| 0.85 | 44 | 3 |

- Economic effective rank: `4.2225`
- PCA dimensions for 50% / 80% / 90% variance: `2 / 4 / 6`
- Independent current 0.90 clusters: P4 `60`, P5 `1`, P6 `1`
- Cross-family 0.90 overlap: none
- Economic basin count: `47 -> 56` (`+9`)
- HQ basins deepened: `15`
- New HQ concrete realizations: `73`

Realization-depth increments versus the frozen baseline:

| Dimension | Increment | Current depth >= 2 |
|---|---:|---:|
| asset selection | +4 | 23 |
| mapped weight | +1 | 12 |
| mapped weight >= 3 | +0 | 2 |
| raw field | +2 | 21 |
| turnover | +0 | 1 |

## Family novelty and semantic attribution

At the family-conditioned view, P4 had `54 / 4 new` 0.90 clusters, P5 `48 / 1 new`, and P6 `48 / 1 new`. These overlapping family-conditioned counts must not be summed. The independent current-only view isolates one P5 and one P6 0.90 cluster with zero cross-family overlap.

P5's sole matched-positive row came from `FLOW_INTENSITY_CONVICTION`, using a `Persistence` primitive and `SafeDiv`. That motif received `8,428` strict and produced `162` replicated rows. `FLOW_PRICE_ABSORPTION` produced `0 / 2,793` matched-positive; `LARGE_TRADE_PRICE_RESPONSE` produced `0 / 779`, despite the best motif-level mean reward among the P5 motifs.

P6's sole matched-positive row came from `FUNDING_FLOW_CROWDING`, using a `Transition` primitive and `Residual`. That motif received `6,206` strict and produced `156` replicated rows. `BASIS_OI_CROWDING` had the best P6 motif-level mean reward but `0 / 1,212` matched-positive. `OI_FLOW_CONFIRMATION` was weakest at `0 / 2,987`.

The evidence therefore supports the existence of distinct train-only P5/P6 economic realizations, while simultaneously showing a severe family-level conversion bottleneck.

## Dispatcher efficiency and acceleration

Full dispatcher counters recorded:

- legal generated: `552,895`
- dispatch selections: `38,923`
- strict evaluations: `30,000`
- generated-to-selected: `7.04%`
- selected-to-strict: `77.08%`
- generated-to-strict: `5.43%`
- average / median legal pool: `14.2 / 16`
- pools under eight: `6,148`

Construction routes reaching strict evaluation:

| Route | Strict |
|---|---:|
| frozen frontier catalog sample | 24,000 |
| dimension-aware parameter mutation | 4,851 |
| legacy parameter recombination | 941 |
| representation-successor recombination | 144 |
| semantic-donor mutation | 64 |

During execution, all ten related Python processes were discovered at Windows `BelowNormal` priority. They were raised to `AboveNormal` without changing worker count, code, candidate order, feedback cadence or search state. Throughput improved from about `2,504 strict/hour` to roughly `4,350–4,480 strict/hour`. The acceleration receipt records zero execution-component and zero search-state changes.

## P4 health and boundaries

P4 remained healthy at `6,000 strict / 1,263 matched-positive / 21.05% density`. This rules out a global evaluator, mapping, market-input or Search Core collapse as the explanation for the P5/P6 scarcity.

The canonical checker reports `PASS`, candidate rebuild failures `0`, and exact family allocation `40% / 40% / 20%` for P5/P6/P4. Boundary counters are:

| Boundary | Reads |
|---|---:|
| validation | 0 |
| OOS | 0 |
| holdout | 0 |
| forward | 0 |
| promotion | 0 |
| sealed | 0 |

## Hash-bound closure evidence

The compact closure transfer is `99,432 bytes`, SHA-256 `3A0A35B9E58A51A316D3D88DD75ECF9A06C60E5040FFEDC12B2F9B8611F2BE38`. Fourteen runtime JSON artifacts were pulled and checked against the PC2 manifest with zero mismatches.

The two large Parquet artifacts remain on PC2 but are independently hash-bound in the manifest:

- candidate ledger: `320,347,472 bytes`, SHA-256 `74C7CD4B6D182A681BDC107F879BC257C6D347EF4C02688B9DDC0CAFD688B677`
- behavior archive: `26,092,198 bytes`, SHA-256 `9A46F74982D117A10F79E2D5D2F3816B4785B0D920FB8ED3E3AF07CCA210CC89`

## Final decision

`HYPOTHESIS_FRONTIER_PASS`

The bounded catalog, compiler integration, dispatcher path, checkpointing and canonical economic analysis all completed validly. P5 and P6 each contributed one independent new 0.90 economic cluster, so the hypothesis frontier is not empty. However, two matched-positive rows across 24,000 P5/P6 strict evaluations means the pass is narrow and structural—not broad productivity and not permission for validation, OOS, promotion or another search. P1 remains archived, P4 remains the healthy anchor, and no successor is automatically authorized.
