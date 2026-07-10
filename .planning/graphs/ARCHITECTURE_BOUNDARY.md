# Architecture Boundary

Generated: 2026-07-11

## Purpose

The `.planning/graphs/` directory now has three different views. They are intentionally separate:

| File | Meaning | Use |
|---|---|---|
| `graph.json` | Raw graphify output | Machine-readable navigation index |
| `graph.html` | Raw graphify tree | Human browsing of code/file graph |
| `GRAPH_REPORT.md` | Raw graph statistics | Check graph size/freshness and artifact scope |
| `CURRENT_ARCHITECTURE.md` | Curated current architecture | Explain the active research/search system |
| `EVOLUTION_MAP.md` | Curated evolution map | Explain how A7 phases reached the current state |
| `ARTIFACT_LIFECYCLE.md` | Artifact lifecycle policy | Decide what to keep, archive, supersede, or delete |

## Rule

Raw graphify output is not the architecture.

The raw graph is expected to be large and noisy because it sees code, reports, runtime artifacts, planning files, and historical scripts. It can contain obsolete and superseded paths. It is an index, not a decision document.

Raw graph size is also a cleanup signal. A large raw graph does not imply a large architecture; it often indicates fast-iteration process artifacts that should be classified, archived, summarized, or deleted after source-of-truth extraction.

## 2026-07-11 Build Note

The raw graph was rebuilt from the crypto project root after the A7EFF2 semantic-identity integration:

```text
graph.json:
  19304 nodes
  29160 links
  9 hyperedges

GRAPH_REPORT.md:
  regenerated

graph.html:
  not regenerated in this build because the graph exceeded the default 5000-node HTML visualization limit
```

Therefore, use `graph.json` and `GRAPH_REPORT.md` as the current raw graph artifacts. Treat `graph.html` as an older browsing artifact unless it is explicitly rebuilt with a higher visualization limit or a reduced corpus.

The build includes navigable nodes for `semantic_domains.py`, `signal_identity.py`, and ADR 0001. JSON policy files are still governed through the curated architecture and ADR even when the raw extractor does not emit a dedicated JSON node.

The build emitted cross-chunk node ID collision warnings. This is expected in a repo with many repeated report concepts and historical artifacts, and it reinforces the boundary rule: raw graph reachability is not current architecture or deployment proof.

The current architecture is the smaller manually curated system chain that is still active or explicitly authoritative.

The evolution map is the phase history and supersession story. It explains why the repo contains many old artifacts without treating all of them as live architecture.

## Interpretation Contract

- Use raw graphify files to locate code and relationships.
- Use `CURRENT_ARCHITECTURE.md` to reason about the active system.
- Use `EVOLUTION_MAP.md` to reason about phase history, supersession, and governance.
- Use `ARTIFACT_LIFECYCLE.md` to classify process artifacts and avoid maintaining historical noise as architecture.
- Do not infer deployment readiness from any graph file.
- Do not infer alpha proof, shadow, paper, or live authorization from any graph file.
- If a raw graph node conflicts with A7PM/source-of-truth records, A7PM and current planning state win.

## Current Status

The active system remains a controlled research/search stack. It is not authorized for alpha proof, shadow, paper, live trading, or production portfolio construction.

PC1 asset retirement state is an asset-custody concern, not an alpha-readiness claim. Use `CURRENT_ARCHITECTURE.md` and `Plans.md` for the latest migration evidence.
