# Crypto Temporal Proposal Dispatch Successor V1 — 20260815r1

## Outcome

`SEARCH_CORE_PROPOSAL_DISPATCH_SUCCESSOR_V1` 已完成唯一一次正常 train-only targeted P1/P4 run，并在 `20,000 strict` hard cap 停止。未启动后续 search、validation、OOS、forward 或 promotion。

`NEXT_DECISION = P1_SEMANTIC_SUPPLY_BOTTLENECK`

这不是全局 semantic supply 耗尽，也不是 search-policy collapse。dispatcher 对 P4 仍有明确经济转换，而 P1 在充足 legal-pool 供给下只产生 `106 / 2,923 = 3.63%` matched-positive、只 deepened 1 个 HQ basin；P4 为 `2,270 / 17,077 = 13.29%`，deepened 15 个 HQ basins。

## Bound identities

- Implementation commit: `7936825b061a3fef69de55bf6e42486b7664b3bf`
- Pure authorization commit: `c927c0f658a93ef005ce76bd365380ef4e3715a3`
- Runtime: `crypto_temporal_proposal_dispatch_successor_v1_20260815r1`
- Authorization SHA-256: `88FC399D0A7BC5639B26F954A5361B96CCAC0FF6CA044EF4D6C0DFD1BB82FB48`
- Historical prior SHA-256: `719B1DB5764701897D3CC2764E595ABD4F582BF64F6C91B0E658D864F4F39AEA`
- Frozen contract SHA-256: `303A32A685F30D628A81D893F32C991FB2DCE0D49D82372738F64A17CB718948`
- Run result SHA-256: `C40B22116BA2C13CEF792AD01CB385CDBA55A0BF990A5191BED65F9AADFFF483`
- Final analysis SHA-256: `6DFEC85ADA418723A6250EDD7A8DE4681A6784A59514D222F2A9236826E4CBA6`

Checker-only engineering repairs `2ca41db8` and `e9f8522f` corrected two post-run false negatives: dispatch selections were reconciled with pre-strict paired-control rejections, and completed-runtime authorization was verified from its immutable snapshot/launch Git objects rather than the current control-plane HEAD. Neither repair changed an authorization-bound execution component or any runtime economic row.

## A. Search result

| Measure | Result |
|---|---:|
| strict | 20,000 |
| raw attempts | 255,334 |
| matched-positive | 2,376 |
| matched density | 11.88% |
| P1 strict / matched | 2,923 / 106 |
| P4 strict / matched | 17,077 / 2,270 |
| P2 strict | 0 |
| P3 strict | 0 |
| HQ basins deepened | 16 / 23 |
| new unique HQ concrete realizations | 121 |
| wide concrete realizations, P1 + P4 | 309 |

Real economic clusters（不是 behavior-family 数量）：

| Similarity | Clusters | New clusters |
|---|---:|---:|
| 0.95 | 84 | 23 |
| 0.90 | 58 | 9 |
| 0.85 | 44 | 6 |

Realization depth increments：

| Dimension | Increment |
|---|---:|
| asset-selection realizations >= 2 | +7 |
| mapped-weight realizations >= 2 | +2 |
| mapped-weight realizations >= 3 | +3 |
| raw-field realizations >= 2 | +5 |
| turnover realizations >= 2 | +0 |

## B. Dispatch closure

Across all dispatcher selections, including proposals later rejected by the paired-control contract:

- legal generated/scored: `230,205 / 230,205`
- dispatcher selections: `25,106`
- strict selected: `20,000`
- paired-control pre-strict rejects: `5,106`
  - `CONTROL_BEHAVIOR_EQUALS_PRIMARY`: 3,998
  - `MATCHED_CONTROL_SUPPORT_DIFFERS_PRIMARY`: 1,108
- average / median pool: `9.169 / 9`
- exploitation / exploration: `21,293 / 3,813` = `84.81% / 15.19%`
- selected rank #1 / #2 / #3: `13,086 / 6,168 / 2,605`
- pools under eight: `6,804`

The exact closure identity is:

`25,106 dispatch selections = 20,000 strict + 5,106 paired-control pre-strict rejects`.

At the 10k diagnostic boundary, the run had 12,585 dispatch selections, 133,980 legal proposals, median pool 10 and no research-invalid condition. Per preregistration it continued to the 20k hard cap.

## C. Construction-route attribution

`selected` is pre-strict dispatcher selection; `strict` excludes paired-control rejects. `new HQ` below is a per-dispatch QD admission event and must not be summed as the final unique-HQ count of 121.

| Route | Generated | Selected | Strict | Matched | Basin retained | New realization | New HQ event |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dimension-aware parameter mutation | 115,972 | 20,776 | 16,617 | 1,193 | 189 | 134 | 85 |
| Legacy parameter recombination | 7,026 | 1,502 | 1,437 | 736 | 487 | 341 | 161 |
| Representation Successor recombination | 9,208 | 1,506 | 1,194 | 439 | 322 | 239 | 110 |
| Semantic donor mutation | 97,999 | 1,322 | 752 | 8 | 0 | 0 | 0 |

Both Legacy and Representation Successor recombination remained active. The successor did not expand the frozen 464 TemporalProgram semantic basis.

## D. Semantic-edit attribution

| Edit | Generated | Selected | Strict | Matched | Basin retained | New realization | New HQ event |
|---|---:|---:|---:|---:|---:|---:|---:|
| binding | 425 | 158 | 128 | 36 | 39 | 30 | 13 |
| normalization | 547 | 314 | 230 | 99 | 81 | 62 | 37 |
| temporal_parameter | 733 | 190 | 139 | 49 | 33 | 21 | 17 |
| binding + temporal_parameter | 375 | 176 | 122 | 35 | 35 | 31 | 15 |
| binding + normalization | 551 | 73 | 51 | 11 | 9 | 6 | 0 |
| normalization + temporal_parameter | 528 | 59 | 43 | 13 | 13 | 10 | 5 |
| binding + normalization + temporal_parameter | 197 | 15 | 6 | 0 | 0 | 0 | 0 |
| legacy_parameter | 7,026 | 1,502 | 1,437 | 736 | 487 | 341 | 161 |
| legacy_parameter_subblock | 5,145 | 517 | 474 | 196 | 112 | 79 | 23 |
| role | 98,706 | 1,326 | 753 | 8 | 0 | 0 | 0 |
| component | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| operator | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Strong historical edit priors remained economically informative; role-only semantic donors retained an exploration floor but converted poorly.

## E. Mutation-target attribution

| Target | Generated attempts | Selected | Strict / descriptor-change | Basin retained | Matched | New realization | New HQ event |
|---|---:|---:|---:|---:|---:|---:|---:|
| mapped-weight | 27,398 | 6,346 | 5,307 | 24 | 249 | 17 | 6 |
| turnover | 8,425 | 1,808 | 1,458 | 16 | 58 | 10 | 7 |
| raw-field | 4,911 | 1,421 | 1,134 | 2 | 29 | 2 | 2 |
| asset-selection | 6,819 | 1,851 | 1,490 | 7 | 113 | 6 | 6 |
| generic | 182,652 | 13,680 | 10,611 / 0 | 949 | 1,927 | 679 | 335 |

Turnover remained operator-reachable, but final turnover depth increment stayed zero. The supported finding remains `TURNOVER_LOW_ECONOMIC_CONVERSION`, not `TURNOVER_NOT_REACHABLE`.

## F. Train-only proposal-prior quality

| Selected-score band | Strict | Mean score | Matched density | Basin retention | New realization | New HQ event |
|---|---:|---:|---:|---:|---:|---:|
| top decile | 2,000 | 0.4107 | 38.50% | 30.55% | 23.50% | 11.20% |
| middle (deciles 5–6) | 4,000 | 0.2606 | 6.48% | 0.98% | 0.70% | 0.40% |
| bottom decile | 2,000 | 0.1800 | 11.00% | 1.70% | 0.75% | 0.65% |

The top region clearly ranked productive proposals, but the middle-to-bottom ordering was not monotonic. This supports a useful but partial train-only prior, not validation/OOS proof.

## G. Descriptive efficiency

All comparisons reuse development data and are descriptive only.

| Campaign | Matched / 1k | New HQ / 1k | New realization / 1k |
|---|---:|---:|---:|
| Proposal Dispatch V1 | 118.8 | 6.05 | 35.7 |
| r3 | 81.37 | 15.53 | 750.3 |
| Realization V2 | 111.7 | 6.70 | 839.3 |
| Representation Legacy | 151.7 | 6.10 | 730.9 |
| Representation Successor | 148.6 | 5.90 | 712.1 |

Current new-realization admission semantics are stricter than the mapped historical lineage metric, so that column is not an apples-to-apples promotion claim. Proposal Dispatch improved matched density over r3 and Realization V2, but did not exceed either Representation tournament arm. That prevents a global `PROPOSAL_DISPATCH_SUCCESSOR_PASS` conclusion.

## Canonical checker and boundaries

- Checker: `PASS`
- Checker SHA-256: `5135B8C9B506A307A4D85FB22826BAD83BC932AA13D6E50F0548764253B79029`
- checkpoint count: 10
- evaluation partition: train only
- validation/OOS/holdout/forward/promotion/sealed reads: `0 / 0 / 0 / 0 / 0 / 0`
- automatic next run started: false

The one operational worker-memory interruption was replayed from checkpoint 0 under the same launch claim and frozen seeds after removing two stuck status-helper processes. No frozen identity changed and no second research run was authorized.

## Final decision

`P1_SEMANTIC_SUPPLY_BOTTLENECK`

The integrated dispatcher works and did not collapse: it produced abundant bounded legal pools, preserved exploration, ranked a highly productive top region, and deepened 16/23 target HQ basins. The residual failure is family-local. P1 retained an exploration floor but remained economically narrow under the frozen 464 semantic basis, while P4 supplied almost all matched-positive and basin deepening. No follow-up experiment, semantic-basis expansion, validation, OOS, or promotion is authorized by this report.
