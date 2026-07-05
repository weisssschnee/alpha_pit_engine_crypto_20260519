# Artifact Lifecycle

Generated: 2026-07-05

## Purpose

The raw graph is allowed to be large, but raw graph size is also a cleanup signal.

This repository has many fast-iteration artifacts: stage scripts, reports, runtime manifests, forensic outputs, queue shards, search outputs, and superseded experiments. Those files are useful evidence while a phase is active, but they are not all long-term architecture targets.

## Core Rule

Process artifacts are not architecture.

After a project-level milestone, newly created or touched artifacts should be classified into one of these lifecycle buckets:

| Bucket | Meaning | Default action |
|---|---|---|
| `core_source` | Reusable code that belongs to the active system | Keep, test, and map to current architecture |
| `current_contract` | Report/spec/manifest defining an active contract or gate | Keep and reference from planning/source-of-truth files |
| `current_evidence` | Evidence needed for the current milestone or next decision | Keep while current; summarize into source-of-truth |
| `runtime_manifest` | Machine-readable summary/index of a run | Keep selected manifests; avoid storing bulky outputs in git |
| `archive_evidence` | Historical evidence useful for audit or supersession | Archive or keep as historical record; do not map as active architecture |
| `superseded` | Replaced by a newer stage or decision | Mark historical/superseded; remove from active graph reasoning |
| `delete_candidate` | Temp/debug/intermediate file with no durable evidence value | Delete after milestone validation |
| `external_runtime` | Large remote/local compute output | Keep outside git under runtime/data storage; summarize in reports/manifests |

## Milestone Cleanup Checklist

For each medium-or-larger project milestone:

```text
1. Identify new code, reports, manifests, runtime outputs, and generated indexes.
2. Promote only reusable code and active contracts into current architecture docs.
3. Summarize bulky runtime outputs into manifests or reports.
4. Mark superseded reports/scripts as historical when source-of-truth files support it.
5. Delete or archive temp/debug artifacts that no longer support a decision.
6. Update CURRENT_ARCHITECTURE.md only for active components.
7. Update EVOLUTION_MAP.md only for phase history or supersession changes.
8. Treat raw graph growth as a prompt to review artifact lifecycle, not as architecture growth.
```

## File-Level Anchoring Policy

Current architecture docs should link to core files sparingly.

Use this pattern:

```text
architecture component
  -> 1-5 core source files
  -> 1-3 active contract/report files
  -> selected manifest/index files only when they define the current state
```

Do not manually maintain thousands of raw graph nodes. The raw graph keeps file-level traceability; curated architecture keeps system-level meaning.

## Git Policy

- Keep reusable source, current contracts, curated architecture, selected manifests, and high-signal reports in git.
- Keep bulky runtime outputs, queue shards, full logs, and repeated generated surfaces outside git unless explicitly needed.
- Use `.gitignore` for generated graph/build/runtime folders when appropriate.
- If a file is necessary only to reproduce a historical decision, prefer a compact report plus manifest over full raw output.

## Current Interpretation

The current raw graph has many nodes because it indexes both active system code and historical process artifacts. That does not imply the active architecture is large.

The active architecture remains the curated chain in `CURRENT_ARCHITECTURE.md`. The raw graph is a navigation and cleanup aid.
