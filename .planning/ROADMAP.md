# Crypto AlphaFactory Roadmap

**Last updated:** 2026-08-17 Asia/Hong_Kong

## Maintenance Override — Current Authority

The project is in `SYSTEM_MAINTENANCE_CONTROL_PLANE_RECOVERY` under accepted ADR `docs/adr/0024-system-maintenance-suspension-and-control-plane-recovery.md`.

This section supersedes the stale phase statuses below for current execution decisions. The historical roadmap is retained because its older phase definitions and evidence remain useful provenance.

Current rules:

- Phase 5 system rectification is the owning active phase.
- Phase 5 Wave 1 (state freeze, verified-core inventory, core interface contracts, architecture blueprint) was already executed on 2026-06-30 and is not repeated.
- Phase 5 Wave 2/3 are resumed against the current August code/evidence: data/field/PIT authority audit and repair; reward/search/memory control-chain audit; verified-core/current-repo decision and final maintenance audit.
- New economic/market search, strict candidate budgets, validation/OOS/forward/promotion and automatic successor runs are suspended.
- Phase 6 Controlled Expansion is blocked by maintenance exit, not by completion of an obsolete A7SEARCH5 checklist.
- Maintenance exit requires the carrier-admission, field continuity, SearchEvidenceMemory, search-core continuity, project-state/Graph enforcement and runtime-safety criteria in ADR 0024.

## Already Passed Prerequisites

The roadmap below does not restart the project from zero. It assumes the following prior phases are complete and remain part of the current source of truth:

- A7PM-0/1/2/3: governance registry, asset taxonomy, lifecycle state machine, and experiment board.
- A7AI-F0/F1/F2/F3/F4: field contract enforcement, engine wiring, end-to-end enforcement, materialization/evaluator parity, and response-backed field promotion.
- A7AA-0/1/2/3/4: label/response contract, primitive response map, role classification, selector rewrite contract, and handoff.
- A7MEM-0/1: search memory registry and memory-enforced generator.
- A7SEARCH4: completed proxy search aggregate with strict candidates.

These prerequisites support controlled research/search continuation only.

## Phase 1 - Crypto Search Hardening

Status: active

Goal:

Finish the current A7SEARCH5_R2 memory-enforced proxy search, aggregate results, and convert them into strict reward, dedupe, information-source, and memory-update decisions.

Primary artifact:

- `.planning/phases/01-crypto-search-hardening/01-PLAN.md`

Exit criteria:

- A7SEARCH5_R2 reaches `128 / 128` reports or has a documented abort reason.
- Aggregate manifest and report exist.
- Strict reward results are separated from proxy selected rows.
- Duplicate economic exposure is capped before updating next-search memory.
- Leakage, PIT, control, lag, shuffle, and regime gates have no unresolved blocker.

## Phase 2 - Data, Regime, And Label Integrity Audit

Status: planned

Goal:

Quantify whether available data, including the incremental 2023-07 to 2023-12 pre-2024 backfill and the 2026 recent patch, has enough regime/event coverage for the current train, validation, test, recent, and stress design.

Scope:

- Coverage by symbol, listing age, and active universe.
- Event/regime counts for crash, high vol/low liquidity, funding boundary, basis dislocation, OI expansion/contraction, CE spread, and session/event boundaries.
- Explicit answer to whether additional data is needed and where it should be added without destroying time-contiguous splits.
- Decision on whether 1h remains the primary search horizon or whether 15m/1m requires a separate adapter/reward stack.

Exit criteria:

- Regime coverage table exists.
- Inadequate regimes have quantified gap counts.
- Reward/stress windows are revised if coverage is insufficient.

## Phase 3 - Reward And Validation Unification

Status: planned

Goal:

Make reward reporting and validation automatic enough that a search output cannot be interpreted without train, validation, test, recent, stress, control, shuffle, lag, and non-overlap floors.

Scope:

- Train Sortino and train orientation as first-class metrics.
- Validation/test/recent/stress floors.
- Control and shuffle dominance.
- Lag/stale dominance.
- Non-overlap floors.
- Candidate rejection reasons.
- Accepted-for-next-search output.

Exit criteria:

- Reward report cannot omit train/OOS/stress/control fields.
- Any accepted row has machine-readable gate evidence.
- Reward output feeds A7MEM update directly.

## Phase 4 - Search Policy Bakeoff And Memory Update

Status: planned

Goal:

Compare search policies under the same memory, feature, reward, and dedupe rules, then update A7MEM with strict positive and rejection priors.

Scope:

- CEM-style policy.
- UCT/UCB-style policy.
- Typed AST mutation.
- Raw broad exploration lane.
- Diversity/MAP-Elites style lane.
- Memory-guided exploitation lane.

Exit criteria:

- Policies are compared on strict pass rate, non-duplicate strict clusters, independent information-source count, and reward gate survival.
- Next-search memory update is produced.
- The next search queue has explicit family, motif, skeleton, and source caps.

## Phase 5 - Verified Core Extraction Or New Repo Decision

Status: **ACTIVE MAINTENANCE** — Wave 1 completed 2026-06-30; Wave 2/3 resumed 2026-08-17 under ADR 0024

Goal:

Separate verified reusable core components from historical research scripts and decide whether to continue in the existing repo or create a clean successor repo.

Primary artifact:

- `.planning/phases/05-verified-core-extraction-or-new-repo-decision/05-PLAN.md`

Scope:

- Data contract core.
- Feature/materialization core.
- Formula AST/search core.
- Reward/validation core.
- Memory registry core.
- Runtime orchestration.
- Report/version package format.
- Automatic transition rules between proxy aggregate, strict reward, validation pack, memory triage, and next queue.

Exit criteria:

- Verified core inventory exists.
- Components are classified as keep, rewrite, archive, or legacy reference.
- Core interface contracts exist for data, field, formula queue, proxy result, reward result, validation pack, memory update, and run manifest.
- Search core, search policy, reward, validation, memory, and orchestration are separated in the architecture plan.
- New repo decision is made with migration plan if needed.

## Phase 6 - Controlled Expansion

Status: **BLOCKED BY SYSTEM MAINTENANCE** — requires an explicit ADR 0024 maintenance-exit decision after Phase 5 Wave 2/3 and the final system-level audit pass

Goal:

Run larger controlled search only after data, reward, memory, and dedupe gates are working.

Blocked by:

- incomplete current A7SEARCH5_R2 aggregate;
- incomplete regime coverage audit;
- incomplete reward-memory feedback loop;
- unresolved duplicate exposure risk.

Explicitly not authorized:

- alpha proof;
- shadow/paper/live;
- production portfolio construction.
