# Crypto Latest Evidence and Search-Instrument Independent Audit

Final status: `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED`

Financial decision: `HOLD_RESEARCH`
OOS evidence grade: `NONE`
Audit baseline: `main@09ac397c61b0b462497e9a8c0ea84981cc6a93f9`
Accepted economic-evidence line: `crypto-frontier-provenance-closure-20260714@4726795f61052470d56e2d1475e4f6da9d262943`

## Executive decision

The currently accepted Crypto economic result is the Frontier provenance closure plus its qualified development evidence:

```text
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
```

Qlib's original `0/0` comparison was `MODEL_FIT_DEGENERATE`. Its identical predictions mechanically produced identical weights; that observation cannot independently diagnose `PORTFOLIO_MAPPING_COLLAPSE`. One frozen, non-search repair made full/control predictions and weights different, so the comparison degeneracy was fixed; its economic comparison is still underpowered. DeepDow is not exactly fit-, comparison-, or mapping-degenerate, but it has only five independent five-day development blocks and is also underpowered. Neither is an informative economic negative.

The new independent finding is separate: the internal search instrument has material, source-proven mismatches. B1S and Epoch-0 adapt on a zero-cost gross proxy. B1S strict evaluation adds cost, turnover and IC; Epoch-0's downstream surface additionally adds benchmark increment, stability, uncertainty, concentration and controls. Epoch-1 materially improves the feedback, but does not fully align it; Epoch-1R changes admission rather than that feedback. Epoch-2 is a blocker-local repair experiment, not unrestricted mechanism discovery. Primitive semantics drift or collapse across implementations, and the common rank mapping removes signal information while potentially creating reranking turnover.

This supports `INTERNAL_SEARCH_INSTRUMENT_NOT_FULLY_QUALIFIED` and `CURRENT_IMPLEMENTED_GRAMMAR_LOW_YIELD`. It does not support “the market has no alpha”, “the mechanism space is exhausted”, or “new data is the unique remedy”. No repair, economic search, new-data integration, sealed-block access, or promotion was started.

## Evidence authority and branch roles

| Evidence line | Exact identity | Role now | Authority boundary |
|---|---|---|---|
| Immutable main audit input | `main@09ac397c61b0b462497e9a8c0ea84981cc6a93f9` | Navigation, static feature inventory, and this audit's starting tree | Does not contain or execute closure-only Frontier code |
| Accepted closure | `crypto-frontier-provenance-closure-20260714@4726795f61052470d56e2d1475e4f6da9d262943` | Accepted Frontier economic evidence and implementation source | Development-only; no OOS proof or promotion |
| Historical A7/B1S/Epoch tags and commits | Exact refs recorded in the timeline and stage-lineage CSVs | Immutable lineage and implementation/run evidence | Not one combined “current Epoch”; old action recommendations may be superseded |
| RAW Graph | `.planning/graphs/graph.json` generated from main | Code navigation only | Not runtime proof, result authority, or an architecture control plane |

The row-level evidence ledger is [CRYPTO_ACCEPTED_RESULT_TIMELINE.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_ACCEPTED_RESULT_TIMELINE.csv), the stage contract is [CRYPTO_RUNTIME_STAGE_LINEAGE.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_RUNTIME_STAGE_LINEAGE.csv), and the branch interpretation is [CRYPTO_BRANCH_EVIDENCE_MAP.md](CRYPTO_BRANCH_EVIDENCE_MAP.md). The feature, algorithm and primitive ledgers carry the same seven provenance/authority fields. Each conclusion is tied to a repo ref, commit, run identity, data release, evidence role, supersession state, and current authority.

## External paradigm qualification

### Qlib 0.9.7

The full input was not the control input: 158 versus 13 raw/processed features, 145 full-only features, different matrix hashes, positive variance in all full-only raw features, and a minimum full-only non-null rate of 0.6703. Labels were variable and supported. Artifact identity was not reused.

The original pinned fit nevertheless produced one constant prediction per cross section for both variants: 240/240 rows exactly equal and prediction variance approximately `1.34e-46`. The resulting 23 daily weight vectors were exactly equal. This is `MODEL_FIT_DEGENERATE`; because the mapper received identical predictions, equal weights are a mechanical downstream result and do not independently establish `PORTFOLIO_MAPPING_COLLAPSE`. It is not evidence that “Alpha158 has no increment”.

The single predeclared repair removed only the CSI300 regularization terms (`lambda_l1=lambda_l2=0`) while retaining feature sets, label, splits, seeds, fit count, boosting budget, early stopping, TopK mapping and costs. It was one trial, not tuning. After repair:

- full/control each produced one retained tree, with 25/17 split nodes and 22/10 nonzero-gain features; training losses changed materially;
- full/control prediction value correlation: `0.06017`;
- prediction rank correlation: `0.17787`;
- exact-equal rows: `0/240`;
- mean daily L1 weight difference: `1.38245`;
- exact-equal dates: `0/23`.

Therefore the comparison is `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED`, while economic status remains `DATA_ADEQUACY_UNDERPOWERED`.

### DeepDow 0.2.3

DeepDow has 156 overlapping windows, not 156 independent evaluation observations. Training, validation and development contain at most 17, 5 and 5 non-overlapping five-day target blocks respectively; the estimated label-autocorrelation effective sample size is about 29.7 over the complete window set. Train and evaluation target intervals do not cross split boundaries.

Inputs and labels have positive variance; gradients, loss and parameters move; challenger/control and cross-seed model/portfolio identities differ. The development ensemble challenger/control weights have mean daily L1 difference `0.09617`, with no exactly equal date. Long-only output is close to equal weight, but not collapsed: challenger mean daily L1 distance from one-over-N is `0.07136`. The result is not fit-, comparison-, or mapping-degenerate. Its economic status is still `DATA_ADEQUACY_UNDERPOWERED`, not `INFORMATIVE_NEGATIVE`.

### Data Adequacy Gate

| Paradigm | Key actual information | Predeclared minimums failed | Qualification |
|---|---|---|---|
| Qlib cross-sectional daily | 23 dev dates; 840 training rows; 10 assets; 182 history days; 4 independent blocks; 23 turnover observations | dates, samples, assets, non-null rate, history, turnover, independent blocks | `DATA_ADEQUACY_UNDERPOWERED` |
| DeepDow direct 5-day | 23 dev dates; 84 training windows; 10 assets; 182 history days; 5 independent blocks; 23 turnover observations | dates, samples, history, turnover, independent blocks | `DATA_ADEQUACY_UNDERPOWERED` |
| Internal long-only daily bridge | 23 dev dates; 10 assets; 182 history days; 1 independent 20-day block; 23 turnover observations | dates, turnover, independent blocks | `DATA_ADEQUACY_UNDERPOWERED` |

The gate is paradigm-specific and predeclared. Its result is bounded to this fixed core10 release and these target/evaluator contracts. It does not prove that every use of the current data is underpowered or that more data alone repairs the internal instrument.

## Feature information-axis audit

All 94 base rows and all 5,211 derived registry rows were audited without reading feature values, returns, selector outputs, or performance artifacts. The deterministic reproducer is [crypto_latest_feature_space_audit.py](../scripts/crypto_latest_feature_space_audit.py).

The complete 5,388-row runtime map was also checked: all IDs are unique, exactly ten fields are marked runtime-loaded in `A7EFF2_SOURCE_LAG_REWARD`, and the other 5,378 rows remain static-only in that map. Those ten loaded fields are persisted in the summary JSON and must not be confused with the 94-row aggTrades registry.

Base classification:

| Class | Rows |
|---|---:|
| `RAW_OBSERVATION` | 19 |
| `NORMALIZED_REPRESENTATION` | 14 |
| `ROLLING_DERIVED` | 24 |
| `CROSS_SYMBOL_DERIVED` | 9 |
| `INTEGRITY_METADATA` | 4 |
| `FORMULA_PROVENANCE_UNRESOLVED` | 24 |

The 5,211 rows split exactly into 4,606 rolling, 395 core3 cross-symbol, and 210 interaction specs. Reconstructing the declared formatter yields 5,181 expression identities; 35 `HorizonSpread` interaction rows discard their declared market dependency and reduce to five expressions, creating 30 exact duplicates.

The number of independent information axes is **`NOT_IDENTIFIABLE_STATICALLY`**. Under the explicitly defined taxonomy, the registry maps to **26 formula-resolved, non-metadata canonical dependency buckets**, with **29 unresolved dependency-axis sets** reported separately. The bucket count excludes transform and window variants, representation-only ranks, exact expression duplicates, metadata, and unresolved formulas. It must not be read as empirical dimension, correlation rank, statistical independence, full materialization, or economic usefulness.

Material compression and risk facts include:

- 1,274 rolling-on-rolling specs;
- 1,228 specs exposed to the three-asset cross-section's low degrees of freedom;
- 658 rolling `ZScore` specs whose historical formatter applies a different scope from a conventional rolling z-score interpretation;
- 196 specs that admit ID/timestamp integrity metadata as generator input;
- 395 cross-symbol transforms with conditional order-preserving/rank-equivalence risk;
- 588 buy/sell mirror or formula-unresolved side-label candidate specs; unresolved pairs are flagged as candidates, not asserted equivalent;
- 70 `Add`/`Sub` interactions mixing z-score and percentile-rank coordinates; physical-unit Add/Sub mismatch is not present because both operands are normalized;
- 35 `SafeDiv` expressions with an explicit `0.05..4.0` absolute-z denominator guard; the floor permits up to 20x structural amplification and can make ranks sensitive near the clip boundary, while empirical instability remains unproven;
- 1,333 specs with unresolved formula or canonical-axis provenance.

The row-level ledgers are [CRYPTO_FEATURE_INFORMATION_AXIS_AUDIT.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_FEATURE_INFORMATION_AXIS_AUDIT.csv), [CRYPTO_DERIVED_SPEC_EQUIVALENCE_AUDIT.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_DERIVED_SPEC_EQUIVALENCE_AUDIT.csv), and [CRYPTO_FEATURE_SPACE_COMPRESSION_SUMMARY.json](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_FEATURE_SPACE_COMPRESSION_SUMMARY.json).

## Algorithm and objective lineage

The complete 32-row matrix is [CRYPTO_ALGORITHM_OBJECTIVE_LINEAGE.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_ALGORITHM_OBJECTIVE_LINEAGE.csv). Its main distinctions are:

| Stage | Adaptive feedback actually used | What can be learned | What remains fixed or absent | Qualification |
|---|---|---|---|---|
| B1S | zero-cost gross `proxy_score` on subsampled development coordinates | one shared preferred operator | no distinct CEM/UCT/evolutionary policy, field identity, horizon or mapping | algorithm-label degeneracy plus confirmed proxy/strict mismatch |
| Epoch-0 | zero-cost gross rank-weight proxy | grammar-slot probabilities; learned mechanism family can indirectly change the eligible field pool; evolutionary parent inheritance | no direct single-field learner; target horizon and mapping fixed; strict cost, benchmark, uncertainty, stability and controls omitted | confirmed gross-proxy/strict-multiobjective mismatch |
| Epoch-1/Epoch-1R | net LCB, benchmark increment LCB, worst/positive blocks, stability, turnover and concentration in `limited_scalar` | sampling probabilities and parent choice inside the same grammar | mapping fixed; IC, placebo and the full Pareto surface are strict-only; wrong-lag is diagnostic-only | material repair with residual mismatch; Epoch-1R is admission repair |
| Epoch-2 | blocker-local near-miss plus blocker-specific net or benchmark LCB for a tiny UCB action set | preference among at most four legal repair actions | no global grammar, field, horizon or mapping learning; CEM/surrogate diagnostic-only | blocker-local proxy versus global strict objective |

The mismatch finding is not based merely on different objective names. `proxy_score` is computed at zero cost from a scalar gross mean/standard-deviation ratio. Strict net independently depends on mapped turnover times 5 bps, and the strict decision also depends on IC, benchmark-relative, block-stability and control coordinates that cannot be recovered from that scalar. Two candidates can therefore share or reverse gross-proxy ordering while differing on strict eligibility; the feedback is not a sufficient statistic for the final decision surface. Historical Epoch-2B cached evidence corroborates the mechanism: 98.4615% of the rare positive gross-LCB-proxy rows were cost-killed. That gross-LCB quantity is explicitly only `net_lcb + mean_cost_drag`, not an exact gross-series recomputation, so it is corroboration rather than a new performance conclusion.

CEM, UCT/MCTS and surrogate do not create new economic hypotheses; they alter probabilities over encoded grammar slots. Learning a mechanism family can indirectly change the eligible observable-field pool, but no policy learns an individual field identity or target horizon directly. Evolutionary search can inherit a selected field through its parent, while field mutation remains random. `typed_random_fresh` and `typed_ast` call the same canonical sampler in the audited Epoch implementation and are not an independent algorithm comparison. The recorded LLM paths are legal/deterministic typed repairs; Epoch-2 makes no model call. No named RX-UCB implementation was recovered in the accepted closure scope, so its correct status is `NOT_RECOVERED`.

The detailed objective evidence and strict-surface comparison are in [CRYPTO_PROXY_TO_FINAL_OBJECTIVE_AUDIT.md](CRYPTO_PROXY_TO_FINAL_OBJECTIVE_AUDIT.md).

## Primitive semantics

The deterministic non-market audit covers all 13 requested primitives across `temporal_program.py` versus `nextgen_epoch.py` and `b1s_canary.py`. The 26 rows contain four exact equivalences, three shared-coordinate/warm-up-qualified equivalences, 16 semantic mismatches, and three B1S primitives not implemented. Three of the mismatches explicitly compare B1S's cross-name `event_age` operator with `StateAge`, `TimeSince`, and `LastHit`.

Confirmed examples:

- `Slope`: rolling OLS slope in `temporal_program`, endpoint delta/window in nextgen/B1S;
- `StateAge`, `TimeSince`, `LastHit`: distinct temporal meanings collapse into nextgen's event-age implementation;
- `Transition` and `FirstHit`: code aliases within both temporal and nextgen, while the underlying state definition differs;
- `PathShape`: first-third versus last-third path comparison in temporal, but aliases nextgen `MultiScaleRelation`;
- `EventWindow`: active-state count in temporal versus transition count in nextgen; B1S has another event-transition implementation;
- `Persistence`: raw-threshold state in temporal/B1S versus rolling-z state in nextgen.

The row-level raw, rank, weight, activation and behavior comparisons are in [CRYPTO_PRIMITIVE_EQUIVALENCE_MATRIX.csv](../runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_PRIMITIVE_EQUIVALENCE_MATRIX.csv). Conditional equivalence is never upgraded to global equivalence.

## Portfolio mapping and cost attribution

The common internal mapping ranks each cross section, subtracts its mean, normalizes L1 gross, clips, and renormalizes. Source and deterministic synthetic diagnostics prove that it:

- deletes common-mode direction and positive-scale/absolute-confidence information;
- forces approximately zero net and unit gross when dispersion exists;
- maps a singleton finite sparse event to zero;
- has no stateful hold rule and reranks every coordinate;
- can suppress large raw changes with stable ranks or create mapped turnover from a small rank crossing;
- can violate the nominal `0.20` cap after post-clip renormalization (`0.272727` in the five-asset synthetic case).

The executable cost path is:

```text
gross[t] = sum_i(weight[i,t] * target_return[i,t])
mapped_turnover[t] = sum_i(abs(weight[i,t] - weight[i,t-1]))
fixed_cost[t] = mapped_turnover[t] * 5 / 10000
net[t] = gross[t] - fixed_cost[t]
```

The previous-weight matrix is initialized to zero at the first coordinate, so initial portfolio establishment is included in L1 turnover and charged the same fixed cost.

Attribution must remain four-way: raw-signal dynamics, turnover created or suppressed by mapping, the fixed 5 bps rate, and unmodeled spread/slippage/impact/fills/capacity. Historical assets do not persist a raw-signal-to-mapped-weight counterfactual, so whether rank mapping created the **majority** of observed turnover is `NOT_IDENTIFIED`. Full evidence is in [CRYPTO_PORTFOLIO_MAPPING_AND_COST_ATTRIBUTION.md](CRYPTO_PORTFOLIO_MAPPING_AND_COST_ATTRIBUTION.md).

## Layer-by-layer attribution

| Layer | Supported finding | Unsupported extension |
|---|---|---|
| Data observability | external and internal Arena comparisons fail paradigm-specific adequacy gates | data is the unique bottleneck |
| Field representation | 94 rows compress into repeated/derived buckets; 5,211 specs were not all materialized | 26 static canonical buckets are statistically independent signals |
| Generator reachability | the implemented grammar repeatedly produced no strict survivor | all economically meaningful mechanisms are reachable or exhausted |
| Search objective | B1S/Epoch-0 mismatch is confirmed; Epoch-1R partial; Epoch-2 blocker-local | adaptive algorithm families are intrinsically ineffective |
| Primitive semantics | drift and pseudo-diversity are source- and synthetic-test-proven | every primitive implementation is wrong |
| Portfolio mapping | deterministic information loss and turnover amplification mechanisms exist | mapping caused most historical turnover |
| Evaluator power | 23 dates and 4/5 independent external blocks are inadequate | a reliable negative or positive external-paradigm comparison |
| Trading economics | fixed-cost evaluator shows cost sensitivity within its model | real spread, slippage, impact, fills or capacity are represented |

## Proposition decisions

| Proposition | Decision | Scope |
|---|---|---|
| Qlib comparison is currently underpowered | `SUPPORTED` | after the one-shot degeneracy fix; core10 development-only |
| DeepDow comparison is currently underpowered | `SUPPORTED` | five independent development blocks; core10 development-only |
| `CURRENT_DATA_UNDERPOWERED` | `SUPPORTED_WITH_SCOPE` | for the predeclared Qlib, DeepDow and internal Arena gates—not all possible analyses |
| Current implemented grammar is low yield | `SUPPORTED_WITH_SCOPE` | audited frozen development runs produced no strict survivor |
| Internal search-instrument capability is proven | `REJECTED` | objective mismatch, comparison degeneracy and fixed representation/mapping prevent that claim |
| Current mechanism space is exhausted | `REJECTED` | reachability and semantic coverage are not established |
| New data is the unique next step | `REJECTED` | data adequacy and instrument qualification are separate blockers |

## Direct answers to the ten requested questions

1. **Accepted result:** the accepted economic evidence is the Frontier provenance closure, `CURRENT_DATA_UNDERPOWERED`, and `FINANCIAL_GATE_HOLD_RESEARCH`; the new static result is the bounded instrument-mismatch finding, not an alpha result.
2. **Main versus closure tag:** immutable `main@09ac397` is the navigation/static-inventory audit input; `closure-tag@4726795` is authoritative for Frontier execution and qualified economic evidence. The audit commit adds evidence only and does not merge closure executables into main.
3. **Superseded conclusions:** A7EFF2 as project-wide “current Epoch”, Epoch-0's challenge recommendation, unqualified Qlib `0/0`, DeepDow informative-negative wording, Epoch-2B as unique-data proof, and all old instructions that reopen sealed evaluation or search.
4. **Actually loaded fields:** A7V1 loaded metadata/mask plus seven smoke inputs; A7V3 loaded schema/spec metadata only; A7EFF2 loaded the ten persisted release fields; B1S and Epoch-0 loaded the enumerated main/BBO raw columns; Epoch-1/1R/2 used that same loader; Epoch-2B loaded cached evidence only; Frontier, Qlib and DeepDow used their separately enumerated native fields. The exact per-stage lists are in `CRYPTO_RUNTIME_STAGE_LINEAGE.csv`—no registry count is substituted for runtime loading.
5. **5,211 specs versus information axes:** independent-axis count is `NOT_IDENTIFIABLE_STATICALLY`; the deterministic taxonomy yields 26 resolved non-metadata canonical dependency buckets and 29 unresolved sets, not 5,211 independent signals.
6. **Objective mismatch:** B1S and Epoch-0 are confirmed mismatches because the gross zero-cost feedback is not a sufficient statistic for their strict surfaces; Epoch-1/1R is partially aligned; Epoch-2 remains blocker-local. Typed-random/typed-AST and B1S adaptive-label comparisons also contain comparison degeneracy.
7. **Primitive drift/pseudo-diversity:** confirmed in `Slope`, state/event-age families, `Transition`/`FirstHit`, `PathShape`/`MultiScaleRelation`, `EventWindow`, and `Persistence`, with exact, conditional, cross-name, and not-implemented cases separated in the matrix.
8. **Did rank mapping create the main turnover?** It can create turnover and destroys material signal information, but whether it created the historical majority is `NOT_IDENTIFIED` because no raw-to-mapped counterfactual was persisted.
9. **Failure attribution:** external evidence is underpowered at the data/evaluator layer; internal evidence is additionally confounded by representation compression, reachability limits, objective mismatch, primitive drift and fixed rank mapping; trading economics model only fixed L1 cost and omits real frictions.
10. **Priority now:** maintain `HOLD_RESEARCH`. Do not auto-start repair or new-data integration. If separately authorized later, qualify the instrument before interpreting another internal negative; route any genuinely new release through the existing adequacy gate.

## Bias gate and next decision

Following the backtest-bias audit gate, every result here remains development/reproduction evidence. Historical discovery and replay are separated from evaluation roles in the timeline; forward, challenge, recent and May-stress blocks remain sealed. The accepted development holdout is not OOS proof, temporal overlap is disclosed, costs are incomplete, and no promotion inference is permitted. Decision: `HOLD_RESEARCH`; OOS grade: `NONE`.

The immediate priority is therefore **HOLD**, not an automatic repair or a new-data experiment. If a future task authorizes work, the internal instrument should first receive a small, predeclared capability qualification that aligns adaptive feedback, primitive semantics and portfolio representation before another internal negative is interpreted economically. Independent data acquisition may continue outside this task; any later integration must use the existing ingress and Data Adequacy Gate. New data and instrument repair are complementary possibilities, not a proven ordering or unique remedy.

## Reproduction and boundaries

```powershell
G:\PythonProject\.venv\Scripts\python.exe scripts/crypto_latest_feature_space_audit.py check
G:\PythonProject\.venv\Scripts\python.exe scripts/crypto_latest_instrument_semantics_audit.py check
```

The feature check reconstructs its outputs from committed inventory inputs plus hash-pinned historical/current source and fails on byte drift. The instrument check reconstructs exact closure-tagged source, verifies the peeled closure SHA, runs deterministic non-market diagnostics, and fails on byte drift. This audit preserved:

```text
NEW_PERFORMANCE_SEARCH_FROZEN
FORWARD_SEALED
CHALLENGE_SEALED
RECENT_SEALED
MAY_STRESS_SEALED
NO_CANDIDATE_PROMOTION
NO_CROSS_SPRINT_ADAPTIVE_MEMORY
NO_NEW_DATA_INTEGRATION
```
