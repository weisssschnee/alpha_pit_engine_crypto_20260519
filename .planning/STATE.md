# Crypto AlphaFactory Planning State

Last updated: 2026-07-15 Asia/Hong_Kong

## Current status

```text
REPOSITORY_PROVENANCE_CLOSURE_COMPLETED
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED
CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED
INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_PATH_EXPERIMENTAL
GRAPH_RAW_CURRENT_SEPARATION_ACTIVE
CURRENT_CONTRACT_CAPSULE_ACTIVE
```

Accepted closure identity:

```text
branch: origin/audit/evalreset-collapse-forensics-20260711
commit: 4726795f61052470d56e2d1475e4f6da9d262943
tag:    crypto-frontier-provenance-closure-20260714
```

`REPOSITORY_PROVENANCE_CLOSURE_COMPLETED` is the committed manifest status. `CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED` is the user-accepted interpretation of the annotated closure tag, whose attestation records Reproducer PASS, Gatekeeper PASS, and base bundle SHA256 `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.

The checked-out repository line is `repair/crypto-instrument-capability-20260715`, rooted at `origin/main` commit `9b8d9b105c92fa7427b450290ee2efc0d3f2488b`. Capability source is bound to `46280c5ad2acf6783d0ede0eb27fd93e3713d6f0`; its 14-artifact evidence bundle was committed at `6055bc9ce9794113178a40c8f6f403e1ccd3781e`. The main and accepted closure lines remain distinct. Fixed parity reads exact closure-tag source without merging it or pretending closure-only runners are executable on this branch.

## Source-of-truth order

1. Current user boundaries and sealed-block instructions.
2. Committed source, data contracts, manifests, and real run assets on their exact branch/SHA.
3. The accepted closure tag and independent Reproducer/Gatekeeper decisions.
4. `config/architecture_overlay.json` for approved lifecycle/contracts and generated `.planning/graphs/current.json` for the checked assurance view.
5. RAW Graphify artifacts for code navigation only.
6. Older planning reports and status text as historical evidence.

No single status code overrides source or execution facts.

## Evidence qualification

- Qlib's historical full/control `0/0` was exact and classified `MODEL_FIT_DEGENERATE`. Identical predictions mechanically yielded identical weights, so mapping collapse is not independently identified. One frozen, non-search repair made model predictions and portfolio weights materially different. The comparison is now `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED`, while its economic status remains `DATA_ADEQUACY_UNDERPOWERED`.
- DeepDow learned non-identical parameters and produced non-identical challenger/control weights. It is not an exact comparison, fit, or mapping collapse. Its economic status is `DATA_ADEQUACY_UNDERPOWERED`, not `INFORMATIVE_NEGATIVE`.
- The corrected Arena still has only 23 development dates. Qlib and DeepDow fail multiple predeclared adequacy conditions. No external component increment, OOS robustness, or promotion eligibility was established.
- The accepted financial gate is `HOLD_RESEARCH`.
- The repaired capability-only path has one canonical authority for 13 temporal primitives, three explicit portfolio mappings, full-L1 turnover at a fixed 5 bps, frozen strict-feasibility feedback, and a nine-rule finite proposal grammar. Its evolutionary path uses label-blind structural parent/child mutation receipts, and qualification fails closed below two distinct fixed seeds. All 35 deterministic tests and all 10 qualification criteria pass across seven planted families and two fixed seeds.
- `CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED` is scoped to fixed finite-grammar synthetic expression, reachability, mapping, costing, feedback, and survivor retention. It is not a market, economic, OOS, open-generator recall, or historical-runner repair conclusion.

## Graph state

- RAW: `.planning/graphs/graph.json`, `GRAPH_REPORT.md`, and optional `graph.html`; generated from the current checkout for navigation/query.
- CURRENT input: `config/architecture_overlay.json`; it contains twelve critical nodes and eight critical edges, using only Authority, Boundary, Admission, and Evidence capsules.
- CURRENT outputs: `.planning/graphs/current.json` and `current.html`; both are generated and must not be edited by hand.
- Assurance is independent from lifecycle color. `checked_at` is generated; exact evidence SHA/path/hash may be refreshed automatically, but lifecycle transitions still require an explicit accepted decision.
- Profiles remain limited to the same two explicitly referenced files under `profiles/`; this repair adds no profile, registry, control plane, or automatic lifecycle inference.
- Maintenance: RAW uses `scripts/maintain_crypto_navigation_graph.ps1 build|check|query`; CURRENT uses `node "$env:CODEX_HOME\get-shit-done\bin\gsd-tools.cjs" graphify maintain` and strict audit only with an explicit trace/profile.
- Ignore contract: `.graphifyignore` prevents RAW and CURRENT products, the overlay, and profiles from being re-ingested as source.
- `main` still does not import the historical `crypto_architecture_control_registry_v1.json`; that 65-node closure-line registry remains historical evidence rather than the new CURRENT input.
- The former hand-maintained `CURRENT_ARCHITECTURE.md` is superseded and removed from the live tree; Git history preserves it.
- No second registry, automatic runtime inference, large contract file, hook, or heavyweight CI layer is added.

The old RAW graph built from `fb27d14c` is superseded by the refreshed navigation graph. Historical Graph artifacts remain recoverable through Git.

## Planning supersession

The old A7EFF2 planning state and its immediate A7INPUT0 -> A7MEM/CEM/UCB -> broader reward-search taskflow are superseded. They must not be resumed as current instructions.

The 2026-07-14 feature runtime inventory remains a metadata asset on `main`. Its “current Epoch” label is scoped to its latest verifiable A7 release and is not a complete runtime lineage conclusion.

The requested feature and search-instrument forensic is now complete as a static, development-evidence audit. It classified all 94 base rows, audited all 5,211 registered derived specs, recovered algorithm objectives, compared primitive semantics, and ran deterministic non-market mapping diagnostics. It did not retune an objective, modify a primitive or mapping, read a sealed block, integrate data, run a return search, or promote a candidate.

The bounded result is `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED`: B1S/Epoch-0 feedback is materially misaligned with strict evaluation; Epoch-1/Epoch-1R only partially align it; Epoch-2 is blocker-local repair; primitive aliasing/semantic drift and rank-mapping information loss are real. This result coexists with `CURRENT_DATA_UNDERPOWERED`. Neither one proves that data is the unique bottleneck or that the implemented mechanism space is exhausted.

The repaired path supersedes the prior `NOT_FULLY_QUALIFIED` capability finding only for the frozen nine-rule proposal grammar and deterministic synthetic harness. It does not supersede the historical diagnosis of legacy runners, establish open-generator recall, or change any economic boundary.

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

Graph maintenance may rebuild or query RAW and regenerate CURRENT when committed facts change. It must remain lightweight. A passing validation refresh cannot by itself activate an experimental component, open a sealed boundary, start a search, integrate data, or promote a candidate.

Economic work remains `HOLD_RESEARCH`. The repaired instrument is capability-qualified only inside its frozen finite grammar; this decision does not authorize a real development canary, repair historical runners, or open any sealed block. If new-data integration is later authorized, use the accepted closure line's existing activation entry: ingress preflight, hash-bound observed release facts, Data Adequacy Gate, at most two best-matched external paradigms plus the internal baseline, then one frozen-budget development-only Arena. If adequacy fails, stop at `DATA_ADEQUACY_UNDERPOWERED` / `NO_LARGE_EXPERIMENT`.

## Blocked claims

- Qlib or DeepDow is economically ineffective.
- Current data is the unique remaining bottleneck.
- Finite-grammar synthetic capability qualification proves market alpha, economic increment, OOS robustness, or open-generator/full-grammar recall.
- Capability qualification repairs or validates the historical search runners.
- Capability qualification authorizes a real development canary or any frozen-boundary change.
- The implemented mechanism space has been exhausted.
- New data is the unique next step.
- An external component has a credible development increment.
- Any system has OOS proof.
- Any candidate or component is promotion-eligible.
- The `main` checkout contains closure-line executables that it does not actually contain.
