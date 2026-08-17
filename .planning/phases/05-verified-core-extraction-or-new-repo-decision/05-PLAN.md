---
phase: 5
name: verified-core-extraction-or-new-repo-decision
type: system-rectification-and-core-extraction
status: active_maintenance
wave: 2
autonomous: true
last_updated: 2026-08-17 Asia/Hong_Kong
depends_on:
  - Phase 1 A7SEARCH6 proxy aggregate status
  - Phase 2 data/regime coverage audit
  - Phase 3 reward/validation unification
requirements:
  - do not interrupt active A7SEARCH6 workers
  - preserve all source-of-truth reports and runtime manifests
  - separate verified core from historical research scripts
  - require automatic validation before search outputs feed memory
  - keep alpha proof, shadow, paper, and live blocked
---

# Phase 5: Verified Core Extraction Or New Repo Decision

## 2026-08-17 Maintenance Resumption

This phase is now the owning project phase under accepted ADR `docs/adr/0024-system-maintenance-suspension-and-control-plane-recovery.md`.

Wave 1 was materially executed on 2026-06-30. The following existing artifacts are accepted as completed prerequisites and must not be regenerated merely to create new paperwork:

- `runtime/system_rectification_20260630/system_state_manifest.json`
- `runtime/system_rectification_20260630/core_inventory.csv`
- `runtime/system_rectification_20260630/core_status_summary.csv`
- `runtime/system_rectification_20260630/core_interface_contracts.json`
- `runtime/system_rectification_20260630/architecture_nodes.csv`
- `runtime/system_rectification_20260630/architecture_edges.csv`
- `reports/CRYPTO_SYSTEM_CORE_INVENTORY_20260630.md`
- `reports/CRYPTO_SYSTEM_CORE_INTERFACE_CONTRACTS_20260630.md`
- `reports/CRYPTO_SYSTEM_ARCHITECTURE_BLUEPRINT_20260630.md`

The current work starts at Wave 2 and audits the live August implementation rather than the June snapshot. The newly confirmed blocking failures are:

1. a research-admission HOLD was not propagated through `_load_v14_inputs()` / later Temporal preflights;
2. Unified Field Management (298 base / 235 carrier-bound) and the Temporal executable registry (115) are disconnected;
3. A7MEM candidate/cluster/rejection memory was not carried into the Temporal generation and current BehaviorArchive state is campaign-local;
4. new P5/P6 frontier families used a bounded sampler rather than the mature archive/parent/deepening path;
5. CURRENT preserved the data HOLD but market runs lacked task-relevant runtime traces/strict Graph gating; `workflow_guard` was disabled;
6. PROJECT/ROADMAP/STATE stopped agreeing about which phase was actually active.

Until this phase closes under ADR 0024, no market/economic search or strict candidate budget is authorized. Maintenance uses source-only tests and immutable evidence. The old `do not interrupt A7SEARCH6` rule is historical and no longer describes a live process.

## Objective

Rectify the crypto AlphaFactory system by separating verified reusable components from historical research scripts, enforcing automatic validation between every major stage, and producing a concrete decision on whether to continue in the existing repo or create a clean successor repo.

This phase is a system-hardening phase. It does not run alpha proof, deployment, shadow, paper, or live trading.

## Current Situation

The project now has enough evidence to stop treating the repo as a loose research notebook:

- Governance, field enforcement, materialization parity, primitive response, reward gating, and search memory have passed prior gates.
- A7SEARCH5 found an OI/positioning mechanism, but validation showed it is not a unique formula discovery.
- A7SEARCH6 is running a broader memory-seeded mechanism surface on the company machine.
- The repo still contains many stage scripts where generation, evaluation, reward, aggregation, and reporting are operationally separated.
- GitHub push is currently unreliable from the local machine; local commits must be treated as durable only after a successful remote push.

The system risk is not lack of search throughput. The risk is that partially verified scripts and runtime artifacts can still be confused with source-of-truth components.

## Phase Boundary

In scope:

- Core inventory and classification.
- Source-of-truth artifact registry refresh.
- Data/field/materialization/reward/search/memory/report chain audit.
- Automatic gate specification and smoke tests.
- Verified-core staging layout.
- New-repo decision record.

Out of scope:

- New alpha search execution beyond already running A7SEARCH6.
- Formula large search expansion.
- Alpha proof.
- Shadow, paper, or live trading.
- Refactoring every historical script.

## System Rectification Thesis

The clean system should look like this:

```text
data registry / PIT contract
-> field contract and materialization
-> formula / AST generation
-> proxy evaluator
-> strict reward gate
-> validation / ablation / dedupe
-> search memory update
-> next queue authorization
```

Every arrow needs a machine-readable manifest, gate decision, and rejection path. Any script that bypasses one of these arrows becomes legacy/reference-only.

## Success Criteria

- A verified-core inventory exists and classifies each important component as `keep`, `wrap`, `rewrite`, `archive`, or `legacy_reference`.
- Each core interface has an input contract, output contract, manifest, and failure mode.
- Architecture blueprints exist as Mermaid diagrams plus machine-readable node/edge tables.
- Search output cannot feed reward or memory unless automatic validation artifacts exist.
- Runtime/report artifacts are mapped to source-of-truth status.
- The active A7SEARCH6 run is preserved and not interrupted.
- A repo decision record exists:
  - continue in current repo with staged package boundaries; or
  - create a clean successor repo with a migration list.
- No deployment-stage authorization is introduced.

## Tasks

### 1. Freeze Current System State

Type: governance

Actions:

- Record latest local and remote git hashes.
- Record unpushed commits and push failures.
- Snapshot active company-machine tasks and run roots.
- Snapshot current reports and runtime manifests for A7SEARCH5/A7SEARCH6.

Files:

- `.planning/STATE.md`
- `reports/CRYPTO_SYSTEM_RECTIFICATION_STATE_FREEZE_20260630.md`
- `runtime/system_rectification_20260630/system_state_manifest.json`

Verification:

- State freeze includes local `HEAD`, `origin/main`, active run roots, active task ids, and current authorization boundaries.
- No running company-machine search is stopped by this phase.

Acceptance criteria:

- Future agents can resume from the freeze without guessing which artifact is current.

### 2. Build Verified-Core Inventory

Type: audit

Actions:

- Inventory code under:
  - `alphafactory_crypto/`
  - `scripts/crypto_a7*.py`
  - `reports/`
  - `runtime/`
- Classify components by subsystem:
  - data contracts
  - field contracts
  - feature/materialization
  - formula AST/generation
  - proxy evaluation
  - strict reward
  - ablation/validation
  - search memory
  - aggregation/reporting
  - company-machine orchestration
- Assign status:
  - `keep_core`
  - `wrap_with_contract`
  - `rewrite_needed`
  - `archive_only`
  - `legacy_reference`

Files:

- `reports/CRYPTO_SYSTEM_CORE_INVENTORY_20260630.md`
- `runtime/system_rectification_20260630/core_inventory.csv`
- `runtime/system_rectification_20260630/core_status_summary.csv`

Verification:

- Each kept/wrapped component has an owner subsystem and at least one evidence artifact.
- Historical scripts are not silently promoted to core because they happen to work once.

Acceptance criteria:

- There is a concise list of reusable modules and a separate list of scripts that must not be reused without wrapping.

### 3. Define Core Interface Contracts

Type: architecture

Actions:

- Define stable interfaces for:
  - `DataPanelContract`
  - `FieldContractRegistry`
  - `FormulaCandidateQueue`
  - `ProxyEvaluationResult`
  - `RewardGateResult`
  - `ValidationPackResult`
  - `SearchMemoryUpdate`
  - `RunManifest`
- For each interface, specify required columns/fields, failure behavior, and authorization outputs.

Files:

- `reports/CRYPTO_SYSTEM_CORE_INTERFACE_CONTRACTS_20260630.md`
- `runtime/system_rectification_20260630/core_interface_contracts.json`

Verification:

- Each interface has both human-readable and machine-readable definitions.
- Any missing field or stale artifact causes fail-closed behavior.

Acceptance criteria:

- New search or reward scripts can be checked against a stable contract instead of inferred CSV shape.

### 4. Audit Data, Field, And Leakage Controls

Type: safety-audit

Actions:

- Verify that current primary 1h search stack is explicit about:
  - source panel path
  - point-in-time semantics
  - label horizon
  - entry alignment
  - field availability
  - listing-age and active-universe behavior
- Check that 1m/15m data is marked as available data, not silently part of current search/reward unless an adapter exists.
- List every known future/same-bar/leakage control and where it is enforced.

Files:

- `reports/CRYPTO_SYSTEM_DATA_FIELD_LEAKAGE_AUDIT_20260630.md`
- `runtime/system_rectification_20260630/data_field_leakage_matrix.csv`

Verification:

- No current core path can use a field without contract status.
- 1m/15m are not conflated with 1h reward stack.

Acceptance criteria:

- Field/input layer is either verified or explicitly blocked before core extraction.

### 5. Audit Reward And Validation Automation

Type: validation

Actions:

- Confirm reward emits train, validation, test, recent, stress, control, lag, shuffle, and non-overlap floors.
- Confirm accepted queue cannot omit rejection reasons or gate evidence.
- Confirm validation packs can run ablation/single-leg/operator-baseline checks.
- Define automatic transition rules:
  - proxy aggregate pass -> bounded full reward
  - full reward pass -> validation pack
  - validation pack pass/hold -> memory triage
  - memory triage pass -> next search queue

Files:

- `reports/CRYPTO_SYSTEM_REWARD_VALIDATION_AUTOMATION_AUDIT_20260630.md`
- `runtime/system_rectification_20260630/reward_validation_gate_matrix.csv`
- `runtime/system_rectification_20260630/automatic_transition_rules.json`

Verification:

- A candidate cannot be called accepted without train/OOS/stress/control evidence.
- A validation `HOLD` cannot be fed as a positive memory seed without a documented triage rule.

Acceptance criteria:

- Reward and validation are no longer manually interpreted stages.

### 6. Audit Search Core And Policy Separation

Type: search-audit

Actions:

- Separate:
  - search core implementation
  - policy/lane configuration
  - memory enforcement
  - proxy evaluation
  - supervisor/runtime orchestration
- Compare CEM-like, UCT/UCB-like, AST mutation, raw exploration, diversity, and mechanism-seeded lanes by output artifacts, not by theoretical label.
- Identify where A7SEARCH1/A7SEARCH6 reuse core logic and where they still carry one-off logic.

Files:

- `reports/CRYPTO_SYSTEM_SEARCH_CORE_AUDIT_20260630.md`
- `runtime/system_rectification_20260630/search_policy_component_matrix.csv`
- `runtime/system_rectification_20260630/search_runtime_supervisor_audit.csv`

Verification:

- Search policy is not confused with search core.
- A queue generator cannot bypass memory enforcement unless explicitly marked legacy reproduction.

Acceptance criteria:

- The next search can be configured as a policy experiment without rewriting the evaluator/reward path.

### 7. Stage Verified Core Layout

Type: refactor-plan

Actions:

- Create a staged target layout proposal, without moving code immediately:

```text
alphafactory_crypto_core/
  data/
  fields/
  formula/
  proxy/
  reward/
  validation/
  memory/
  orchestration/
  reporting/
```

- Map current files to target modules.
- Mark minimal extraction sequence.

Files:

- `reports/CRYPTO_SYSTEM_VERIFIED_CORE_TARGET_LAYOUT_20260630.md`
- `reports/CRYPTO_SYSTEM_ARCHITECTURE_BLUEPRINT_20260630.md`
- `runtime/system_rectification_20260630/verified_core_target_layout.json`
- `runtime/system_rectification_20260630/file_migration_plan.csv`
- `runtime/system_rectification_20260630/architecture_nodes.csv`
- `runtime/system_rectification_20260630/architecture_edges.csv`

Verification:

- No broad code move happens before interface contracts and tests exist.
- Target layout keeps company-machine orchestration separate from research logic.
- Architecture report includes current system flow, target verified-core flow, runtime/report source-of-truth flow, and company-machine orchestration flow.

Acceptance criteria:

- The project has a migration plan that can be executed incrementally.
- Future agents can inspect one architecture blueprint instead of reconstructing the system from scattered reports.

### 8. New Repo Decision Record

Type: decision

Actions:

- Evaluate two options:
  - continue current repo with `alphafactory_crypto_core/` staged boundaries;
  - create a clean successor repo and migrate only verified components.
- Decision factors:
  - amount of legacy script noise
  - reproducibility burden
  - risk of breaking active research
  - cost of migrating runtime/report history
  - need for clean agent handoff

Files:

- `reports/CRYPTO_SYSTEM_NEW_REPO_DECISION_20260630.md`
- `runtime/system_rectification_20260630/new_repo_decision.json`

Verification:

- Decision includes explicit migration list and hold list.
- If new repo is chosen, the old repo remains immutable evidence/history, not deleted.

Acceptance criteria:

- Future agents know whether to build inside this repo or start a successor repo.

## Gates

### Pre-flight Gate

- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` exist.
- Active A7SEARCH6 run root is recorded.
- Local git unpushed state is recorded.
- No system-rectification task may kill or reset active company-machine Python workers.

### Revision Gate

Revise the plan if:

- any core subsystem lacks a contract;
- any verification output is only human-readable;
- reward/search/memory handoff remains manual;
- any task would move code before inventory and interface contracts exist.

### Escalation Gate

Escalate to the user if:

- a verified component depends on unavailable data or remote-only state;
- git push remains unavailable after local commits are created;
- A7SEARCH6 finishes with eval errors or memory failures that change system assumptions;
- new repo vs current repo decision is not clear from evidence.

### Abort Gate

Abort execution if:

- a leakage or PIT violation is confirmed in a kept core path;
- source-of-truth runtime artifacts are missing;
- a migration would overwrite active runtime outputs;
- a script attempts to bypass reward or memory gates.

## Verification Loop

Each task must produce:

1. human report under `reports/`;
2. machine-readable artifact under `runtime/system_rectification_20260630/`;
3. manifest or decision JSON;
4. `.planning/STATE.md` update;
5. git commit attempt.

The phase is complete only when the new repo/current repo decision is written and every kept component has an interface contract plus evidence.

## Execution Order

Wave 1:

1. Freeze current state.
2. Build verified-core inventory.
3. Define interface contracts.

Wave 2:

4. Audit data/field/leakage controls.
5. Audit reward/validation automation.
6. Audit search core/policy separation.

Wave 3:

7. Stage verified core layout.
8. Write new repo decision record.

## Current Next Action

Do not interrupt A7SEARCH6. While it runs, execute Wave 1 as a documentation and inventory pass. When A7SEARCH6 aggregate exists, feed its final artifacts into Wave 2 reward/search/memory audit.
