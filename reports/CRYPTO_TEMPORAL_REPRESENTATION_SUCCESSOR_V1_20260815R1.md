# Crypto Temporal Representation Successor V1 — 20k train-only tournament

Status: `FINAL_ANALYSIS_COMPLETE`  
Runtime: `crypto_temporal_representation_successor_v1_20260815r1`  
NEXT_DECISION: `REPRESENTATION_SUCCESSOR_PARTIAL`

## Boundary and authority

- Frozen implementation commit: `ee2afea3f8187c5c0c1c9a39a3fb302887bb4390`
- Pure authorization commit: `d102f1bfa4875f5cbcfc2b61997a7f0f4068abbc`
- Authorization content SHA-256: `19277B534BA95AD9908B64272327E838231CFF277165C4934E16FA68AD437786`
- Frozen parent source: 23 anchored economic basins / 228 parents.
- Both arms used independent paired-derived seeds, independent adaptive state, and independent archives.
- Active families were P1/P4 only. P2 strict = 0; P3 strict = 0.
- Validation/OOS/holdout/forward/promotion/sealed reads were all 0.
- No automatic next run was started.

The canonical independent checker returned `PASS`, SHA-256
`9885F19E74674DFCA67371D60A70823ABF25B274717A9A33BCDABB0881E62E2C`.

## Representation closure

The successor losslessly embedded all 464 TemporalProgramSpec semantic identities;
410/410 constructible programs also preserved exact expression identity. The 54
catalog entries without a constructible sample were pre-existing and were recorded,
not hidden or reclassified.

| Metric | Legacy V2 | Successor | Delta |
|---|---:|---:|---:|
| Same-basin pairs | 552 | 552 | 0 |
| Pairs with legal non-parent child | 507 | 527 | +20 |
| Legal-child existence | 91.85% | 95.47% | +3.62 pp |
| Legal children / pair mean | 8.02 | 10.68 | +2.65 |
| Median | 5 | 7 | +2 |
| P90 | 24.9 | 29.0 | +4.1 |
| Unique children | 3,668 | 4,645 | +977 |
| Completion failure | 8.70% | 7.91% | -0.79 pp |
| Parent-identical rejection | 27.85% | 27.55% | -0.30 pp |
| Duplicate rejection | 61.88% | 62.35% | +0.48 pp |

P1 legal-child existence was 100% in both representations. P4 improved from
91.18% to 95.10%. The implementation therefore closed a real representation gap,
especially in P4, but closure gains did not automatically become superior economic
production.

## Economic tournament

| Metric | Legacy control | Successor | Successor - control |
|---|---:|---:|---:|
| Strict | 10,000 | 10,000 | 0 |
| Attempts | 15,413 | 16,325 | +912 |
| Matched-positive | 1,517 | 1,486 | -31 |
| Matched density | 15.17% | 14.86% | -0.31 pp |
| HQ basins deepened (of 23) | 17 | 17 | 0 |
| New HQ concrete realizations | 103 | 101 | -2 |
| Wide concrete realizations | 263 | 269 | +6 |
| 0.95 real economic clusters / new | 74 / 14 | 74 / 15 | 0 / +1 |
| 0.90 real economic clusters / new | 55 / 4 | 55 / 5 | 0 / +1 |
| 0.85 real economic clusters / new | 43 / 3 | 43 / 3 | 0 / 0 |

These are real economic clusters from the canonical fingerprint clustering, not
behavior-family counts.

Depth deltas were mixed and did not support a full successor pass:

- mapped-weight realizations >=2: control `+1`, successor `-1` (relative delta `-2`);
- mapped-weight realizations >=3: `+2` in both arms;
- turnover realizations >=2: `0` in both arms;
- raw-field realizations >=2: `+2` in both arms;
- asset-selection realizations >=2: control `+5`, successor `+3` (relative delta `-2`).

The successor archive was also slightly smaller: 242 occupied adaptive realization
cells and 583 active descendants, versus 253 and 606 for control. Same-anchor
admissions were 612 versus 637; cross-basin rejects were 68 versus 60. New-basin
diagnostics were retained as diagnostics only and never became anchored-basin parents.

## P1 / P4 decomposition

P1 improved structurally but remained economically narrow:

- proposals: 1,630 control vs 1,522 successor;
- matched-positive: 74 vs 72;
- dual-positive density: 43.93% vs 47.44%;
- 0.90 economic clusters: 3 vs 4;
- concrete realizations: 25 vs 27;
- HQ basins deepened: 1 vs 1.

P4 remained the main economic producer but did not improve under the successor:

- proposals: 8,370 control vs 8,478 successor;
- matched-positive: 1,443 vs 1,414;
- dual-positive density: 46.83% vs 47.26%;
- 0.90 economic clusters: 49 vs 45;
- concrete realizations: 238 vs 242;
- HQ basins deepened: 16 vs 16.

This is not the pattern required for `P1_SEMANTIC_BASIS_BOTTLENECK`, because the
successor was not clearly effective on P4 while failing only on P1.

## Operation attribution

The 0.62/0.03/0.35 values were sampling probabilities, not completion quotas.

| Arm | Requested parameter / mechanism / crossover | Realized parameter / mechanism / crossover | Crossover fallback |
|---|---:|---:|---:|
| Control | 6,526 / 285 / 3,189 | 8,624 / 285 / 1,091 | 2,098 (65.79% of requested crossover) |
| Successor | 6,696 / 245 / 3,059 | 8,654 / 245 / 1,101 | 1,958 (64.01%) |

Successor parameter mutation produced 824 matched-positive, four new 0.90 clusters,
and 101 new HQ realizations. Successor crossover produced 661 matched-positive, one
new 0.90 cluster, and the same 101 HQ realization set. Mechanism mutation produced
one matched-positive and one new 0.90 cluster. Basin/realization contributions overlap
across operations and therefore are not additive.

## Semantic-module attribution

The economically useful successor edits were concentrated rather than general:

- `normalization`: 152 proposals, 104 matched-positive, 20 new HQ realizations;
- `binding`: 102 proposals, 61 matched-positive, 14 new HQ realizations;
- `binding+temporal_parameter`: 55 proposals, 35 matched-positive, 14 new HQ realizations;
- `legacy_parameter_subblock`: 553 proposals, 341 matched-positive, 46 new HQ realizations;
- `temporal_parameter`: 124 proposals, 84 matched-positive, 8 new HQ realizations.

Broad semantic changes were not supported economically in this run:

- `component_change`: 29 proposals, 0 matched-positive;
- `operator_change`: 127 proposals, 1 matched-positive, 0 HQ realizations;
- `role` / `role_change`: 119 proposals, 1 matched-positive total, 0 HQ realizations.

The evidence supports retaining factorized completion and the productive binding,
normalization, and temporal-parameter modules, but not replacing the legacy path
wholesale or declaring the entire donor basis exhausted.

## Engineering recovery

After the first successor 2k computation, Windows legacy path handling failed while
writing a temporary empty pair-diagnostics Parquet file. The failure occurred before
the checkpoint manifest was committed. The preserved state contained the exact 2,000
strict rows, 3,012 attempts, 2,412 attempted IDs, policy state, and archive state.

The checkpoint was completed through an extended-length path, verified with the
canonical checkpoint loader, and atomically promoted. No strict rows were replayed.
Rejected-detail evidence for that prefix was recoverable only as aggregate raw-attempt
overhead (1,012); the exact total attempts and all scientific/adaptive state were
preserved. The next native 4k checkpoint used the standard atomic writer and passed
restore verification, proving the repair path. Recovery receipt SHA-256:
`399BEDD8403CF1212B91B68C9F80003F979D1F5C7209CF7FAAF8934A59939FBB`.

## Decision

`REPRESENTATION_SUCCESSOR_PARTIAL`

The successor materially and losslessly improves legal recombination closure, and a
small subset of semantic modules produces useful economic realizations. It does not,
however, beat the legacy control on matched-positive production, HQ realization yield,
basin deepening, or depth expansion. This rules out `REPRESENTATION_SUCCESSOR_PASS`.
Because useful new economic clusters and productive module-level effects remain, the
evidence also does not justify `CURRENT_TEMPORAL_SEMANTIC_BASIS_EXHAUSTED`.

No validation, OOS, holdout, forward, promotion, sealed read, or subsequent search was
started.
