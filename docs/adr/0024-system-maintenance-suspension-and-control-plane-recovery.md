# ADR 0024: System Maintenance Suspension and Control-Plane Recovery

- Status: Accepted
- Date: 2026-08-17
- Authority: explicit user instruction in the active project session to enter maintenance, inspect Codex project management / Graph, stop drift, and repair the system before further search
- Amends: ADR 0011, ADR 0012, ADR 0015, ADR 0016, ADR 0023 for all future execution while this maintenance state is active

## Context

The project accumulated strong local components but the end-to-end control chain drifted apart.

The canonical project contract already states that field loadability is not PIT qualification, development evidence is not OOS proof, unqualified data releases may not be bypassed, and CURRENT/ADR/STATE own current authority. ADR 0011 separately states that delivered Search Surface Integration is an engineering reachability layer and that historical instrument-identity / PIT-universe holds remain research blockers. ADR 0012 states that Unified Field Management is a compiled view, not research admission.

Despite those decisions, the August Temporal line reused the V1.4 aligned cache with identity `E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA`. The cache metadata itself declares `fixed_retrospective_cohort=true` and `research_admission=DEVELOPMENT_DIAGNOSTIC_ONLY`. Its upstream integration decision retains `research_admission=HOLD` and the historical PIT/universe blockers. `_load_v14_inputs()` verifies cache identity, field order and window but does not consume those admission states. As a result, hash-bound reproducibility was stronger than scientific admission enforcement.

The field system also fragmented by layer. Unified Field Management currently describes 298 base fields, 5,509 canonical views and 235 carrier-bound base fields, while the Temporal V1.4 loader exposes only the 71 OI/mark plus 44 aggTrades fields. Broad39 and nearly all Core3 fields do not reach the active Temporal registry even though many are already materialized, typed, compiler-valid and matched-control-constructible.

Search memory suffered a separate generational disconnect. A7MEM-0 already built candidate, cluster, rejection and pair/motif memory and declared it mandatory for the next large search. Later Temporal campaigns instead use campaign-local BehaviorArchive state plus a statistical historical proposal prior. Candidate-level prior observations, route closures, rejection memory and explicit `already searched` semantics are therefore not mandatory inputs to new campaigns. This is distinct from the intentional prohibition on carrying adaptive population/RNG/reward state between campaigns.

The P5/P6 Frontier exposed a third disconnect. Its source-gap plan is a bounded hard-coded motif plan; two historical artifacts are recorded as provenance hashes but not consumed as decision evidence. P5/P6 proposals sample bounded semantic programs and random realization bindings and enter the dispatcher with no survivor parent lineage. This is not the same archive-driven mechanism deepening path used by P4. The 111-entry frontier contains temporal-only and condition-only variants but no temporal+condition compositions.

Project management did not stop the drift. Phase 5 `Verified Core Extraction Or New Repo Decision` was designed on 2026-06-30 specifically to enforce `data/PIT -> fields -> formula/search -> reward/validation -> memory -> next queue`, and Wave 1 artifacts were created, but ROADMAP kept the phase as planned and STATE became an append-heavy history rather than a reliable current-state pointer. CURRENT preserved the new-data research HOLD, but runtime campaigns were not supplied with matching Graph execution traces; generated CURRENT therefore remained advisory. The Codex `PROJECT_CONTROL_REVIEW` route is also explicitly advisory: the installed Review Skill states that it is not a controller, scheduler, or execution interceptor. The installed GSD runtime recognizes `hooks.context_warnings` but does not implement a `hooks.workflow_guard` execution gate even though one settings document mentions the key. Freshness of RAW/CURRENT files and prompt-level review were consequently mistaken for proof that task-relevant authority had been enforced.

On 2026-08-17 the subsequently authorized Frontier Pocket r2/r3 processes were manually stopped before any durable candidate ledger/checkpoint because their authorizations still bound the retrospective diagnostic carrier. Their runtime/launch evidence is retained; it must not be deleted or rewritten as if the launches never happened.

## Decision

The project enters `SYSTEM_MAINTENANCE_CONTROL_PLANE_RECOVERY` immediately.

### 1. Suspend real market/search execution

Until an explicit maintenance-exit decision is accepted:

- no new economic/market search authorization may be created;
- no PC2 candidate-generation/evaluation run may start or resume;
- no validation, OOS, holdout, forward, promotion or sealed role may be opened;
- no P5/P6 pocket, P7/P8 frontier, P1 rescue, P4 expansion, optimizer bakeoff or new large search may consume strict budget;
- existing diagnostic or consumed runtimes remain immutable evidence.

Allowed maintenance work is source inspection, contract repair, deterministic/source-only tests, artifact classification, data-authority reconstruction, field-registry integration, evidence-memory migration, project-management/Graph repair and non-market replay planning. A market replay is not authorized merely because the repair compiles.

### 2. Reclassify the E8BFD15A lineage without destroying it

All evidence produced on carrier `E8BFD15A...` remains useful for search-engine engineering, relative policy comparison under a common surface, mechanism clues, proposal conversion diagnostics and exact reproducibility.

It is not clean historical-PIT Alpha qualification. Economic cluster / family claims from that lineage are therefore `DEVELOPMENT_DIAGNOSTIC` until explicitly transferred to a research-admitted PIT carrier. Historical artifacts and reports are not rewritten; CURRENT/STATE must carry the qualification downgrade.

### 3. Make carrier research admission a mandatory run dependency

Future market loaders must not infer research admission from cache identity, field contracts, compiler reachability, finite support or successful evaluation.

The canonical search preflight must resolve an explicit data/carrier admission role in addition to the existing target/reward/execution/mapping/cost/validation/promotion roles. The run must fail before market-array access when the selected carrier is retrospective, diagnostic-only, HOLD, missing historical-universe authority, or inconsistent with the requested evidence role.

No run-specific authorization may override a data-admission HOLD by merely pinning the held carrier hash.

### 4. Reconnect the field system instead of adding another field registry

Reuse Unified Field Management, existing `FieldContract`, carrier bindings and typed-role resolution. Do not create a second ontology, feature store or field approval database.

Maintenance must produce one executable research-carrier view that makes these distinctions machine-readable for every exposed field:

`source -> materialized -> PIT timing -> historical-universe authority -> research admission -> typed role -> compiler/control reachability`.

The already-existing Broad39, Core3 81, aggTrades44 and OI/mark71 assets must be classified/reused before acquiring new feature families. Data backfill is limited to the missing symbol/date/source support required by a chosen PIT carrier; do not rebuild the data lake by default.

### 5. Restore SearchEvidenceMemory; keep adaptive-state isolation

`NO_CROSS_SPRINT_ADAPTIVE_MEMORY` remains in force for optimizer populations, CEM tables, Evolution populations, RNG state and individual learned reward state unless a later explicit decision changes it.

Separately, future search must consume a persistent non-sealed `SearchEvidenceMemory` compiled from development evidence. It must include at least candidate/semantic identity, exact field binding, carrier/data authority, evidence role, economic fingerprint/cluster where available, strict/rejection outcome, route/family closure or hold decisions, search budget already spent, parent/descendant lineage, realization depth and canonical source links.

A7MEM-0 candidate/cluster/rejection memory, Mechanism aggregate knowledge, Temporal dispatcher prior and later ledgers are inputs to this compiler. They must no longer form isolated memory islands.

Before proposing a previously explored mechanism, a future run must state the new degree of freedom or transfer question it is testing. Exact/semantic duplication without a declared delta is rejected before strict evaluation.

### 6. Unify frontier and deepening semantics

A new mechanism family may begin with bounded semantic seeds, but once strict evidence exists it must enter the same archive/parent/lineage/deepening framework used by productive families, or be explicitly labelled a diagnostic sampler.

Future mechanism-space work must measure actual exposure by family, semantic complexity, field surface, proposal count, strict count and CPU. The system must distinguish binary, temporal, conditional and composed temporal+condition structures; catalog presence is not evidence that a complexity stratum was searched.

### 7. Restore project-management truth

Phase 5 system rectification becomes the active maintenance phase. Its 2026-06-30 Wave 1 inventory/interface/architecture artifacts are retained as completed prerequisites; Wave 2/3 are resumed against current code and evidence rather than restarted from zero.

`.planning/STATE.md` must again contain one explicit current phase, current blockers, allowed work and next action at the top. Historical phase detail may remain below but cannot override the top current state.

`.planning/ROADMAP.md` must show maintenance as active and Controlled Expansion blocked by maintenance exit.

Do not rely on a `hooks.workflow_guard` setting: the installed GSD runtime does not implement that key. Prompt-level `PROJECT_CONTROL_REVIEW` remains advisory. Real execution control must therefore be enforced by repository authority/authorization preflights and explicit lifecycle state, while CURRENT provides task-scoped authority context and audit evidence.

### 8. Make CURRENT a pre-execution gate, not a post-hoc diagram

For any future medium-or-larger market/search change, the task must inspect task-scoped CURRENT before implementation/authorization.

Formal market start/resume/closure must have an explicitly selected execution trace and strict profile audit. CURRENT freshness alone is not sufficient evidence. The development-research profile must include the data-admission, field-information, search capability, formal-search boundary and sealed-boundary components relevant to current execution.

Graphify/CURRENT remains the existing two-layer architecture view; do not add a third project-control graph.

## Maintenance exit criteria

Maintenance may exit only when all of the following are satisfied and an explicit decision records the exit:

1. A market/search carrier has explicit research admission for the intended development role, with historical PIT-universe/source coverage and field timing bound and enforced by loader/preflight.
2. The executable field surface is generated from existing field/carrier authorities; the 298/235/115-layer discrepancy is accounted for and no field is silently dropped or promoted.
3. One SearchEvidenceMemory compiler/index incorporates A7MEM plus later mechanism/Temporal ledgers and route closures; proposal preflight can query it without importing adaptive optimizer state.
4. New frontier families cannot silently bypass archive/parent/deepening; semantic complexity/exposure accounting is explicit.
5. PROJECT/STATE/ROADMAP/Phase 5 agree on current phase and boundaries.
6. Task-relevant CURRENT includes restored dependencies, profiles are current, and a strict audit with an explicit execution trace can prove a no-market maintenance smoke or future authorized run path.
7. All pocket r2/r3 authorizations are disabled/consumed, no relevant PC2 runner survives, and no automatic successor task is active.
8. An independent system review checks `PROJECT -> ADR/STATE -> data admission -> fields -> SearchEvidenceMemory -> search core -> runtime authorization -> evidence/Graph`, not only local tests/hash/checkpoints.

## Consequences

- Previous evaluator/search/checkpoint work is retained but its claim scope is corrected.
- New fields, mechanisms and optimizer work are lower priority than reconnecting already-built assets.
- A checker PASS for one runtime is no longer sufficient to establish project-level correctness when upstream carrier, memory or authority continuity is unresolved.
