---
phase: 1
name: crypto-search-hardening
type: system-hardening-and-search-continuation
status: active
wave: 1
autonomous: true
last_updated: 2026-06-29 10:45 Asia/Hong_Kong
requirements:
  - preserve active A7SEARCH5_R2 run
  - maintain memory-enforced search
  - verify reward and leakage gates before stronger claims
  - keep planning artifacts compact and continuously updated
---

# Phase 1: Crypto Search Hardening And Continuation

## Objective

Stabilize the crypto alpha search chain while the current large memory-enforced search runs, then convert the completed outputs into a strict, reproducible next-search decision. This phase is not an alpha proof phase.

## Current Situation

The project has moved from ad-hoc formula expansion toward a controlled search system:

- A7MEM-0 built the search memory registry.
- A7MEM-1 made memory enforcement mandatory in queue generation.
- A7SEARCH4 completed a prior 65k proxy search and found strict candidates, but also showed duplicate economic exposure pressure.
- A7SEARCH5_R2 is currently running a larger memory-enforced proxy search on the company machine.
- Reward gating has been tightened so high headline Sortino is not accepted unless train, OOS, stress/control, and shuffle/lag checks survive.

The immediate risk is not that no search is running. The immediate risk is losing reproducibility, letting duplicated exposures dominate, or over-interpreting proxy-stage candidates.

## Known Evidence

### A7MEM-0 Search Memory Registry

- Decision: `PASS_A7MEM0_SEARCH_MEMORY_REGISTRY_BUILT`
- Candidate memory rows: `313`
- Strict rows: `42`
- Accepted prior rows: `47`
- Rejected rows: `224`
- Pair/motif priors: `86`
- Required prior file: `runtime/a7mem0_search_memory_registry_20260628/a7mem0_next_search_prior.json`

### A7MEM-1 Memory Enforcement

- Generator loads A7MEM prior by default.
- `--no-memory-enforcement` is allowed only for legacy reproduction.
- Per-shard cap bug was fixed in `1b13a43`.
- Smoke validated duplicate expression rejection and skeleton cap enforcement.

### A7SEARCH4 Final Aggregate

- Completed shards: `128 / 128`
- Leaderboard rows: `32768`
- Strict pass rows: `42`
- Selected rows: `266`
- Eval errors: `0`
- Best strict candidate was still proxy-stage only:

```text
Mul(
  SafeDiv(Decay(mark_index_basis_bps,240),Abs(Decay(account_position_divergence,120))),
  Sign(Decay(trade_quote_volume,336))
)
```

### A7SEARCH5_R2 Active Run

- Run root: `H:\AlphaFactory_CryptoData_archive\a7search5_memory_enforced_proxy_65k_r2_20260628`
- Queue: `65536` rows, `128` shards, `512` rows/shard
- Current completion: `40 / 128` reports at last check
- Current active parallelism: `18` shards
- Supervisor: takeover script running
- Aggregate: pending

## Success Criteria

- A7SEARCH5_R2 reaches `128 / 128` shard reports or stops with a documented abort reason.
- Aggregate report is produced in the remote repo and copied/synced into the main repo if valid.
- Strict accepted candidates are separated from proxy selected and near-miss rows.
- Candidate output is clustered/deduped before any next expensive replay.
- Reward output includes train, validation, test, recent, stress, control, shuffle, lag, and non-overlap floors.
- No claim stronger than research/proxy candidate is made.

## Tasks

### 1. Monitor Active Search

Type: operations

Actions:

- Check company-machine process health.
- Confirm active shard count and CPU delta.
- Confirm no duplicate active shard IDs.
- Confirm reports count increases over time.
- Inspect latest `.out.log` and `.err.log` tails.

Verification:

- 18 active child Python workers are expected under current takeover policy.
- Any 60-90 minute stall at the same report count triggers shard-level diagnosis.

Acceptance criteria:

- Search is either progressing or a concrete stuck shard/failure reason is recorded.

### 2. Complete And Aggregate A7SEARCH5_R2

Type: execution-control

Actions:

- Let takeover supervisor continue until reports reach `128 / 128`.
- Run aggregate only after all reports exist.
- Produce aggregate manifest and report.
- Record exact run root, task/supervisor script, commit, queue size, shard count, and result counts.

Verification:

- Aggregate manifest exists.
- Aggregate report exists.
- Completed shard count equals expected shard count.
- Eval error rows are counted explicitly.

Acceptance criteria:

- A7SEARCH5_R2 aggregate is available as a source-of-truth artifact.

Automation rule:

- When a proxy aggregate completes with `authorizes_bounded_full_reward=true`, automatically launch bounded full reward on the selected queue. Do not pause for user approval unless the aggregate has eval errors, missing shards, or an authorization conflict.

### 3. Strict Reward And Candidate Triage

Type: validation

Actions:

- Run strict reward gate only on aggregate-selected candidates.
- Separate strict pass, near-miss, hard reject, control dominated, lag stale dominated, shuffle dominated, and invalid numeric rows.
- Compare strict pass distribution by semantic pair, motif, skeleton, horizon, and source policy.

Verification:

- No candidate is accepted on headline Sortino alone.
- Train Sortino consistency is reported alongside validation/test/recent/stress.
- Control and shuffle ratios are included.

Acceptance criteria:

- A next-search memory update can distinguish positive priors from rejection priors.

### 4. Dedupe And Information-Source Audit

Type: governance

Actions:

- Cluster strict and near-miss rows by expression, skeleton, semantic pair, motif, and metric similarity.
- Detect duplicate economic exposure.
- Keep independent information-source candidates; cap repeated variants.
- Explicitly protect potentially useful independent derived fields from being killed solely by family-level caps.

Verification:

- Each retained cluster has a reason: strict winner, independent exposure, diagnostic value, or rejection memory.
- Repeated formula-equivalent candidates do not dominate the next queue.

Acceptance criteria:

- Memory registry can be updated without collapsing search into one family.

### 5. Reward/Leakage/Regime Gate Review

Type: system-audit

Actions:

- Re-check label alignment, PIT timing, no future fields, no same-bar leakage, listing-age handling, and active-universe handling.
- Review whether regime/stress windows have enough event coverage after the 2023-07 to 2023-12 backfill and 2026 recent patch.
- Define whether 1h remains the current search horizon and what separate work would be needed for 1m/15m.

Verification:

- Any data/regime insufficiency is listed as a concrete missing coverage count or unavailable source, not a vague concern.
- Reward gate must not rely on fixed post-hoc stress cherry-picking.

Acceptance criteria:

- Search results can be interpreted as controlled research outputs.

## Gates

### Pre-flight Gate

- Active run root exists.
- Memory prior exists.
- Search generator remains memory-enforced by default.
- Remote runtime writes to H: archive root, not low-space D:/G: roots.

### Revision Gate

- If aggregate contains too many duplicated strict rows, revise memory caps before next search.
- If reward accepts candidates with weak train edge or OOS floor failure, revise reward gate before next search.
- If regime coverage is insufficient, revise split/stress design before stronger validation.

### Escalation Gate

Escalate to the user if:

- Reports count does not increase for more than one inspection cycle and CPU delta is zero.
- Any shard repeatedly fails with a traceback.
- Aggregate contradicts current memory assumptions.
- Strict candidates are all one exposure family.

### Abort Gate

Abort or pause search if:

- D:/G: free space falls into unsafe range again.
- H: output root becomes unavailable.
- Memory enforcement is bypassed unintentionally.
- Any future leakage or label alignment failure is confirmed.

## Verification Loop

After every major update:

1. Update `.planning/STATE.md`.
2. Update this `01-PLAN.md` status if scope or gates change.
3. If a run completes, add the final counts and report paths.
4. If a blocker appears, record the blocker and the restart/checkpoint path.
5. Commit planning changes together with source/report changes when the update is material.

## Current Next Action

Continue monitoring A7SEARCH5_R2 until either:

- reports reach `128 / 128`, then aggregate and triage; or
- reports remain stuck across the next inspection window, then diagnose shard-level logs and CPU progress.
