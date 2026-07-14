# Crypto AlphaFactory Planning State

Last updated: 2026-07-14 Asia/Hong_Kong

## Current status

```text
REPOSITORY_PROVENANCE_CLOSURE_COMPLETED
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED
GRAPH_RAW_CURRENT_SEPARATION_ACTIVE
```

Accepted closure identity:

```text
branch: origin/audit/evalreset-collapse-forensics-20260711
commit: 4726795f61052470d56e2d1475e4f6da9d262943
tag:    crypto-frontier-provenance-closure-20260714
```

`REPOSITORY_PROVENANCE_CLOSURE_COMPLETED` is the committed manifest status. `CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED` is the user-accepted interpretation of the annotated closure tag, whose attestation records Reproducer PASS, Gatekeeper PASS, and base bundle SHA256 `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.

The checked-out repository line is `main`; this independent audit is rooted at baseline `09ac397c61b0b462497e9a8c0ea84981cc6a93f9`. The main and accepted closure lines diverge after `ac9fd24`. This audit does not merge them and does not pretend closure-only code is executable from `main`.

## Source-of-truth order

1. Current user boundaries and sealed-block instructions.
2. Committed source, data contracts, manifests, and real run assets on their exact branch/SHA.
3. The accepted closure tag and independent Reproducer/Gatekeeper decisions.
4. `.planning/graphs/CURRENT_ARCHITECTURE.md` for the branch-aware current view.
5. RAW Graphify artifacts for code navigation only.
6. Older planning reports and status text as historical evidence.

No single status code overrides source or execution facts.

## Evidence qualification

- Qlib's historical full/control `0/0` was exact and classified `MODEL_FIT_DEGENERATE`. Identical predictions mechanically yielded identical weights, so mapping collapse is not independently identified. One frozen, non-search repair made model predictions and portfolio weights materially different. The comparison is now `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED`, while its economic status remains `DATA_ADEQUACY_UNDERPOWERED`.
- DeepDow learned non-identical parameters and produced non-identical challenger/control weights. It is not an exact comparison, fit, or mapping collapse. Its economic status is `DATA_ADEQUACY_UNDERPOWERED`, not `INFORMATIVE_NEGATIVE`.
- The corrected Arena still has only 23 development dates. Qlib and DeepDow fail multiple predeclared adequacy conditions. No external component increment, OOS robustness, or promotion eligibility was established.
- The accepted financial gate is `HOLD_RESEARCH`.

## Graph state

- RAW: `.planning/graphs/graph.json`, `GRAPH_REPORT.md`, and optional `graph.html`; generated from the current checkout for navigation/query.
- CURRENT: `.planning/graphs/CURRENT_ARCHITECTURE.md`; concise manual fact view with explicit branch and lifecycle labels.
- Maintenance: `scripts/maintain_crypto_navigation_graph.ps1 build|check|query`.
- Ignore contract: `.graphifyignore` prevents RAW products from being re-ingested as source.
- `main` has no `crypto_architecture_control_registry_v1.json`; none is fabricated for this Graph task.
- No `architecture_overlay.json`, `current.json`, execution trace, second registry, full runtime trace, edge-level fail-closed gate, hook, or heavyweight CI layer is added.

The old RAW graph built from `fb27d14c` is superseded by the refreshed navigation graph. Historical Graph artifacts remain recoverable through Git.

## Planning supersession

The old A7EFF2 planning state and its immediate A7INPUT0 -> A7MEM/CEM/UCB -> broader reward-search taskflow are superseded. They must not be resumed as current instructions.

The 2026-07-14 feature runtime inventory remains a metadata asset on `main`. Its “current Epoch” label is scoped to its latest verifiable A7 release and is not a complete runtime lineage conclusion.

The requested feature and search-instrument forensic is now complete as a static, development-evidence audit. It classified all 94 base rows, audited all 5,211 registered derived specs, recovered algorithm objectives, compared primitive semantics, and ran deterministic non-market mapping diagnostics. It did not retune an objective, modify a primitive or mapping, read a sealed block, integrate data, run a return search, or promote a candidate.

The bounded result is `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED`: B1S/Epoch-0 feedback is materially misaligned with strict evaluation; Epoch-1/Epoch-1R only partially align it; Epoch-2 is blocker-local repair; primitive aliasing/semantic drift and rank-mapping information loss are real. This result coexists with `CURRENT_DATA_UNDERPOWERED`. Neither one proves that data is the unique bottleneck or that the implemented mechanism space is exhausted.

## Frozen boundaries

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

No existing Graph, report, historical metric, or inventory row can open those boundaries.

## Decision after the independent audit

Graph maintenance may rebuild or query RAW and update CURRENT when committed facts change. It must remain lightweight.

Economic work remains `HOLD_RESEARCH`. A future decision may qualify or repair the research instrument, or evaluate a genuinely new release, but neither route starts automatically. If new-data integration is later authorized, use the accepted closure line's existing activation entry: ingress preflight, hash-bound observed release facts, Data Adequacy Gate, at most two best-matched external paradigms plus the internal baseline, then one frozen-budget development-only Arena. If adequacy fails, stop at `DATA_ADEQUACY_UNDERPOWERED` / `NO_LARGE_EXPERIMENT`.

## Blocked claims

- Qlib or DeepDow is economically ineffective.
- Current data is the unique remaining bottleneck.
- The current internal search instrument has been fully capability-qualified.
- The implemented mechanism space has been exhausted.
- New data is the unique next step.
- An external component has a credible development increment.
- Any system has OOS proof.
- Any candidate or component is promotion-eligible.
- The `main` checkout contains closure-line executables that it does not actually contain.
