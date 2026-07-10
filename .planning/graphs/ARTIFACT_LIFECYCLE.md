# Artifact Lifecycle

Generated: 2026-07-10

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

## PC1 Retirement Policy

The old company PC1 may be returned or wiped. Treat this as an asset-custody milestone, not ordinary runtime cleanup.

Before deleting crypto-line assets from PC1, all of the following must be true:

```text
1. PC1 preserve pack exists locally and on PC2.
2. Local and PC2 preserve-pack SHA256 match:
   715F0A23E9AAB23794ED870A14AC5E0B35ED40C45AD15010A8FFE3245A383D07
3. Local full data root exists:
   G:\AlphaFactory_CryptoData
4. PC2 executable subset exists:
   D:\HermesWorker\data\crypto_line\AlphaFactory_CryptoData
5. PC2 runtime/search/reward/preserve roots exist:
   D:\HermesWorker\runtime\crypto_line
6. Final PC1 inventory confirms no unique crypto report/script/runtime output remains outside the preserve pack or local/PC2 custody.
7. Effective mother/contract gap pack exists locally and on PC2 with SHA256:
   `A2ACA1BAED52933226B8A6F27AA02DED1276AAA618917952F2464F8108AA024D`
8. Source-provenance pack exists locally and on PC2 with SHA256:
   `FEDC028A25E59F498FE1EFAC4411CB96F0922FEA987E3262CC1FB226D439C487`
9. Provenance sidecars are expanded on PC2 and include inventory, filelist, manifest, and log for `314300` source-evidence files.
```

Current PC1 residue known from audit:

```text
D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote
D:\HermesWorker\GDrive\AlphaFactory_CryptoData
D:\HermesWorker\runtime crypto/search outputs
possible H:\crypto_migration_20260708 backup material
```

Custody status as of 2026-07-10:

```text
repo/runtime preserve pack: hash-closed locally and on PC2
effective mother/contract gap: hash-closed locally and on PC2
source-provenance evidence: hash-closed locally and on PC2
PC2 provenance sidecars: expanded and directly queryable
physical PC1 residue: still present, pending final wipe checklist
```

Delete only after a final inventory/wipe checklist. Do not infer deletion authorization from raw graph presence or from PC2 executable subset alone; PC2 is not a full 1:1 data mirror, but the effective mother/contract and source-provenance custody gaps are now closed.

## Current Interpretation

The current raw graph has many nodes because it indexes both active system code and historical process artifacts. That does not imply the active architecture is large.

The active architecture remains the curated chain in `CURRENT_ARCHITECTURE.md`. The raw graph is a navigation and cleanup aid.
