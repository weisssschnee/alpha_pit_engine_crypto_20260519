# ADR 0003: Multi-paradigm frontier Arena and artifact contracts

Status: Accepted for development-only architecture; economic migration and candidate promotion remain on hold.

## Context

The previous frontier-assimilation closure treated a manual Alpha158-like model and a scoped momentum LSTM as two end-to-end external reproductions. Source and runtime review showed that neither preserved the upstream feature/processor/model/portfolio/evaluator chain. The earlier data-only closure also exceeded its evidence: it did not isolate target, horizon, model, portfolio mapping, and evaluator expressivity from data availability.

Historical raw assets remain unchanged. `runtime/crypto_frontier_research_v2_20260713/supersession_decision.json` records the narrower claims that survive and the claims that are superseded.

## Decision

Replace the assumption of one formula-score-rank pipeline with adapter-neutral artifacts:

- `ForecastArtifact` for timestamped instrument forecasts;
- `PortfolioArtifact` for native stateful or direct portfolio weights;
- a native evaluator retained by each adapter;
- an explicit common one-day, delayed, 5 bps turnover-cost bridge for cross-paradigm comparison;
- a hash- and PIT-gated external release entry before any new data can be consumed.

Qlib v0.9.7 and DeepDow v0.2.3 are the first pinned native adapters. Qlib preserves official Alpha158, processors, LGBModel, TopKDropout and risk analysis. DeepDow preserves its multi-step tensor, KeynesNet direct allocation, Run and native buy-and-hold losses. Both are adapted to a fixed complete crypto core10 and are not representations of their original market benchmarks.

## Consequences

Architecture result B is complete: a direct multi-step portfolio-allocation paradigm that was previously not expressible can now run and enter a six-system Arena without being converted into a rank score.

No economic component is promoted. The fixed development holdout contains 23 common bridge dates. Qlib full and its 13-feature control are identical; DeepDow flow and its asset-rotated control have approximately zero paired mean increment and a negative 95% lower bound. The bias gate is `HOLD_RESEARCH`.

The following boundaries remain normative:

- `NEW_PERFORMANCE_SEARCH_FROZEN`
- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- `NO_CROSS_SPRINT_ADAPTIVE_MEMORY`

This decision does not imply that Qlib or DeepDow is ineffective, that data is the unique bottleneck, or that development evidence is OOS proof.
