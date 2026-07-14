# Crypto AlphaFactory Planning State

Last updated: 2026-07-14 Asia/Hong_Kong

## Current status

```text
REPOSITORY_PROVENANCE_CLOSURE_COMPLETED
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
GRAPH_RAW_CURRENT_SEPARATION_ACTIVE
```

Accepted closure identity:

```text
branch: origin/audit/evalreset-collapse-forensics-20260711
commit: 4726795f61052470d56e2d1475e4f6da9d262943
tag:    crypto-frontier-provenance-closure-20260714
```

`REPOSITORY_PROVENANCE_CLOSURE_COMPLETED` is the committed manifest status. `CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED` is the user-accepted interpretation of the annotated closure tag, whose attestation records Reproducer PASS, Gatekeeper PASS, and base bundle SHA256 `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.

The checked-out repository line is `main`, whose pre-maintenance baseline was `dfe2012107955997c200ec5e199e5bdae4344d9c`. The two lines diverge after `ac9fd24`. This Graph closure does not merge them and does not pretend closure-only code is executable from `main`.

## Source-of-truth order

1. Current user boundaries and sealed-block instructions.
2. Committed source, data contracts, manifests, and real run assets on their exact branch/SHA.
3. The accepted closure tag and independent Reproducer/Gatekeeper decisions.
4. `.planning/graphs/CURRENT_ARCHITECTURE.md` for the branch-aware current view.
5. RAW Graphify artifacts for code navigation only.
6. Older planning reports and status text as historical evidence.

No single status code overrides source or execution facts.

## Evidence qualification

- Qlib's historical full/control `0/0` was exact but caused by `MODEL_FIT_DEGENERATE`, followed by identical portfolio mapping. One frozen, non-search repair made model predictions and portfolio weights materially different. The comparison is now `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED`, while its economic status remains `DATA_ADEQUACY_UNDERPOWERED`.
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

The 2026-07-14 feature runtime inventory remains a metadata asset on `main`. Its “current Epoch” label is scoped to its latest verifiable A7 release and is not a complete runtime lineage conclusion. The requested search-instrument/feature forensic has **not** started in this Graph-only task, and no feature classification, compression, objective retuning, primitive change, portfolio remapping, planted economic test, or search was performed.

## Frozen boundaries

```text
NEW_PERFORMANCE_SEARCH_FROZEN
FORWARD_SEALED
CHALLENGE_SEALED
RECENT_SEALED
MAY_STRESS_SEALED
NO_CANDIDATE_PROMOTION
NO_CROSS_SPRINT_ADAPTIVE_MEMORY
```

No existing Graph, report, historical metric, or inventory row can open those boundaries.

## Allowed next action

Graph maintenance may rebuild or query RAW and update CURRENT when committed facts change. It must remain lightweight.

Economic work remains dormant. If a new external data release arrives, use the accepted closure line's existing activation entry: ingress preflight, hash-bound observed release facts, Data Adequacy Gate, at most two best-matched external paradigms plus the internal baseline, then one frozen-budget development-only Arena. If adequacy fails, stop at `DATA_ADEQUACY_UNDERPOWERED` / `NO_LARGE_EXPERIMENT`.

Do not start the deferred feature/search-instrument task until it is explicitly resumed.

## Blocked claims

- Qlib or DeepDow is economically ineffective.
- Current data is the unique remaining bottleneck.
- An external component has a credible development increment.
- Any system has OOS proof.
- Any candidate or component is promotion-eligible.
- The `main` checkout contains closure-line executables that it does not actually contain.
