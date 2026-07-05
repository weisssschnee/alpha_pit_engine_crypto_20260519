# Architecture Boundary

Generated: 2026-07-05

## Purpose

The `.planning/graphs/` directory now has three different views. They are intentionally separate:

| File | Meaning | Use |
|---|---|---|
| `graph.json` | Raw graphify output | Machine-readable navigation index |
| `graph.html` | Raw graphify tree | Human browsing of code/file graph |
| `GRAPH_REPORT.md` | Raw graph statistics | Check graph size/freshness and artifact scope |
| `CURRENT_ARCHITECTURE.md` | Curated current architecture | Explain the active research/search system |
| `EVOLUTION_MAP.md` | Curated evolution map | Explain how A7 phases reached the current state |

## Rule

Raw graphify output is not the architecture.

The raw graph is expected to be large and noisy because it sees code, reports, runtime artifacts, planning files, and historical scripts. It can contain obsolete and superseded paths. It is an index, not a decision document.

The current architecture is the smaller manually curated system chain that is still active or explicitly authoritative.

The evolution map is the phase history and supersession story. It explains why the repo contains many old artifacts without treating all of them as live architecture.

## Interpretation Contract

- Use raw graphify files to locate code and relationships.
- Use `CURRENT_ARCHITECTURE.md` to reason about the active system.
- Use `EVOLUTION_MAP.md` to reason about phase history, supersession, and governance.
- Do not infer deployment readiness from any graph file.
- Do not infer alpha proof, shadow, paper, or live authorization from any graph file.
- If a raw graph node conflicts with A7PM/source-of-truth records, A7PM and current planning state win.

## Current Status

The active system remains a controlled research/search stack. It is not authorized for alpha proof, shadow, paper, live trading, or production portfolio construction.
