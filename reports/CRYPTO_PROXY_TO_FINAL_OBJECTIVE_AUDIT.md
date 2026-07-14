# Crypto Proxy-to-Final Objective Audit

Status: `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED` (bounded to the implementations below)

## Scope and provenance

- Current navigation baseline: `main@09ac397c61b0b462497e9a8c0ea84981cc6a93f9`.
- Accepted economic-evidence line and recovered source: `crypto-frontier-provenance-closure-20260714@4726795f61052470d56e2d1475e4f6da9d262943`.
- This audit executed no market-return evaluation, opened no sealed block, integrated no data, changed no reward, and made no candidate promotion.
- All algorithm details are recorded row-by-row in `runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_ALGORITHM_OBJECTIVE_LINEAGE.csv` with source blob identities and historical run IDs.

## Findings

### B1S

The adaptive challenger is not three independently implemented algorithms. `generate_proposals` rotates the labels `cem`, `uct_mcts`, and `evolutionary`; the runner aggregates all 64 pilot results by operator and applies one shared preferred operator to the remaining proposals. Its feedback is `proxy_score`: a gross, zero-cost risk ratio on subsampled development coordinates. Strict evaluation instead applies 5 bps to mapped L1 turnover and requires positive net mean and IC. Therefore the B1S adaptive comparison is both **algorithm-label degenerate** and **proxy-to-strict mismatched**. This says nothing about properly implemented CEM, UCT, or evolutionary search.

### Why the mismatch is not merely a reward-label difference

For B1S and Epoch-0, the adaptive scalar is

```text
P = mean(gross_return) / std(gross_return) * sqrt(observations)
```

and `gross_return` is produced with `cost_bps=0`. For `P` to be a sufficient statistic for strict selection, candidates with the same `P` would need to have the same strict decision/ranking, or at least an order preserved by `P`. The implementation does not have that property:

- **Cost and turnover:** the scalar does not retain the weight path. Different weight paths can produce the same aggregate gross-return scalar while having different `sum(abs(w[t]-w[t-1]))`; strict net then differs by `turnover * 5 / 10000` and can reverse order.
- **Cross-sectional IC:** aggregate portfolio return does not uniquely determine the cross-sectional rank correlation of weights and targets. IC and IC LCB can therefore differ at the same gross scalar.
- **Benchmark and stability:** a mean/std scalar is many-to-one over return paths. Paths with the same scalar can have different monthly/quarterly block order, worst block, positive-block fraction, and benchmark-increment LCB.
- **Controls:** placebo qualification, wrong-lag diagnostics, and adaptive-versus-matched-control deltas depend on coordinates or comparison arms absent from `P`; they can vary without changing the gross scalar.

Consequently equal—or higher—gross proxy does not uniquely imply equal—or higher—strict quality. The feedback cannot uniquely direct search toward the final strict surface; this is a functional-information mismatch, not a renamed reward.

The existing Epoch-2B cache provides limited corroboration without a new return run: among its rare positive gross-LCB-proxy rows, `98.4615%` were classified cost-killed. That figure is **not** an exact recomputed gross LCB. Epoch-2B defines the summary approximation as `gross_lcb_proxy = net_lcb + mean_cost_drag` because gross-series variance was not retained. It supports only the bounded claim that the cached cost axis frequently changes the sign/qualification after a positive gross summary; it does not estimate an exact gross LCB, prove causality for every candidate, or replace the sufficiency argument above. Evidence: `crypto-frontier-provenance-closure-20260714:runtime/epoch2b_audit_20260712/EPOCH2B_ECONOMIC_BOTTLENECK_REPORT.md#cost-killed/gross-LCB caveat;git_blob=4dd3b0d9fb1dbd52a57d4c599935d0cb3c795ce1;sha256=962E734A13D91AA26C8F17B66558D3E60E17ACFCD899067815A73AC270138DBA` and `crypto-frontier-provenance-closure-20260714:runtime/epoch2b_audit_20260712/economic_bottleneck_decision.json#cost_killed_share_of_positive_gross_lcb_proxy;git_blob=02839704ead72e2ed31b91db11d1dc14f6369233;sha256=6A20F64D6C4E0AE31134445A4073C63E05243ADE256D7B5930093B5690A03447`.

### Epoch-0

CEM, UCT, evolutionary, and surrogate policies are real sampling policies, but all learn from `SignalRecord.proxy_score`, a costless gross rank-weight portfolio ratio. The strict vector adds cost, turnover, benchmark incremental LCB, time-block stability, IC LCB, concentration, a placebo hard gate and Pareto axes; wrong-lag is retained as a diagnostic, not a gate. The mismatch is substantive, not a naming issue. CEM/UCT/surrogate learn mechanism family and other encoded grammar slots, so they can indirectly change the field distribution, but none learns the exact field slot. Evolutionary selection can inherit exact fields through selected parents, while field mutation remains random. Portfolio mapping is fixed for every lane.

`typed_random_fresh` and `typed_ast` call the same `make_program` sampler. Lane/algorithm labels are excluded from `_choice` and canonical program identity, so equal seed/ordinal/family scope yields the same canonical program. This pair is not an independent algorithm comparison.

### Epoch-1 and Epoch-1R

Epoch-1 **did materially repair** the Epoch-0 feedback: `development_feedback` includes fixed-cost net LCB, benchmark increment LCB, monthly worst/positive blocks, stability, turnover and concentration. Epoch-1R explicitly preserves that search/reward implementation and changes admission only. It is incorrect to describe Epoch-1R as merely renaming the gross scalar, but it is also incorrect to claim full alignment: final strict evaluation still adds IC LCB, a placebo hard gate and a different multiobjective/Pareto surface. Wrong-lag is computed and retained only as a diagnostic. Naive LCB calculations do not correct temporal dependence.

### Epoch-2

Epoch-2 is blocker-local repair, not an unrestricted economic-hypothesis learner. Evolutionary repair applies a deterministic blocker action after a random mutation and has a matched random control. Local MCTS is a UCB selector over at most four blocker action indices; it does not search the full ProgramSpec, field identity, or portfolio mapping. Its reward is near-miss score plus a blocker-specific net/benchmark LCB term. CEM and surrogate are explicitly diagnostic-only and cannot affect proposal, admission, or selection. `llm_typed_repair` records a prompt but performs deterministic local code repair with no model call.

No named `RX-UCB` implementation was recovered in the accepted closure's `alphafactory_crypto/`, `scripts/`, `config/`, or `reports/`. That status is `NOT_RECOVERED`, not `NOT_IMPLEMENTED` and not evidence about code outside the audited ref.

## Exact mismatch boundary

| Stage | Feedback actually used | Final/strict surface omitted by feedback | Qualification |
|---|---|---|---|
| B1S | costless gross proxy on subsampled coordinates | cost, turnover, IC and strict survivor rule | `CONFIRMED_PROXY_TO_STRICT_OBJECTIVE_MISMATCH`; adaptive labels degenerate |
| Epoch-0 | costless gross proxy for every adaptive policy | cost, benchmark increment, stability, IC, placebo, concentration, Pareto vector | `CONFIRMED_GROSS_PROXY_TO_STRICT_MULTI_OBJECTIVE_MISMATCH` |
| Epoch-1R | net/benchmark/stability/turnover/concentration limited scalar and near-miss | IC, placebo hard gate and the complete strict Pareto surface; wrong-lag remains diagnostic-only | `PARTIAL_ALIGNMENT_WITH_RESIDUAL_STRICT_ONLY_AXES` |
| Epoch-2 | frozen blocker-local rule; UCB uses near-miss plus one target LCB | global strict vector and unsearched grammar/mapping slots | `BLOCKER_LOCAL_PROXY_TO_GLOBAL_STRICT_OBJECTIVE_MISMATCH` |

## Supported and unsupported conclusions

Supported: the current internal search instrument is **not fully qualified**. B1S and Epoch-0 have confirmed objective mismatch; Epoch-1 materially narrows it; Epoch-1R does not change it; Epoch-2 tests only a small repair action surface. Typed-random/typed-AST and B1S adaptive-label comparisons are degenerate at the generator/policy level.

Not supported: that the implemented grammar has no alpha, that the mechanism space is exhausted, that new data is the only possible next step, or that CEM/UCT/evolutionary/surrogate/LLM paradigms are economically ineffective. Existing negative economic evidence remains separate from this capability audit.
