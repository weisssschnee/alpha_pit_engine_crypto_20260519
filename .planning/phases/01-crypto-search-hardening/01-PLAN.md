---
phase: 1
name: crypto-search-hardening
type: system-hardening-and-search-continuation
status: active
wave: 1
autonomous: true
last_updated: 2026-07-04 02:40 Asia/Hong_Kong
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

### Current A7SHADOW / A7LIVE Engineering State

- A7SHADOW-6 repaired May 2026 funding coverage with Binance Vision funding history.
- A7SHADOW-5 repaired stress coverage now passes with funding delta stress finite share `1.0`.
- A7SHADOW-4 R3 built an engineering review packet with no blockers, but still showed high overlap and open-interest concentration.
- A7SHADOW-7 deduped the review packet from `4` candidate-horizon rows to `2` selected rows and rejected `2` overlap variants.
- A7LIVE-0 forward adapter probe passed on the recent patch with `0` eval errors, no missing fields, and minimum formula active ratio `0.884446`.
- A7LIVE-1 source-lag/checksum audit passed for controlled research continuation with no controlled blockers.
- A7LIVE-1 still blocks final proof on official checksum and REST funding source evidence.
- A7SEARCH7 family-diversified queue passed coverage gates and launched on the company machine.
- Current boundary: adapter/materialization evidence only. The packet is too small and too open-interest concentrated for book/deployment language.

## Success Criteria

- A7SEARCH5_R2 reaches `128 / 128` shard reports or stops with a documented abort reason.
- Aggregate report is produced in the remote repo and copied/synced into the main repo if valid.
- Strict accepted candidates are separated from proxy selected and near-miss rows.
- Candidate output is clustered/deduped before any next expensive replay.
- Reward output includes train, validation, test, recent, stress, control, shuffle, lag, and non-overlap floors.
- No claim stronger than research/proxy candidate is made.

## Tasks

### 1. Maintain Current Source Of Truth

Type: operations

Actions:

- Keep `.planning/STATE.md` aligned after each major run.
- Keep git remote synchronized after source/report/runtime-index updates.
- Record every transition with a report path, runtime path, decision, blockers, and authorization boundary.

Verification:

- `HEAD == origin/main` after each committed taskflow update unless GitHub network is unavailable.
- State file must not point to stale active searches.

Acceptance criteria:

- A fresh agent can continue from `.planning/STATE.md` without relying on chat history.

### 2. A7LIVE-1 Source-Lag / Checksum Audit

Type: data-integrity

Actions:

- Audit the forward recent patch used by A7LIVE-0.
- Check source trace, field timestamp lag, funding event alignment, mark/index/premium aliases, active universe coverage, and same-bar/future leakage risk.
- Confirm whether Binance Vision checksum/source evidence exists for every field family used by the selected packet.
- Block stronger claims if source-lag or checksum evidence is incomplete.

Verification:

- Machine-readable manifest includes pass/blocker status by field family.
- Any field with uncertain timestamp semantics is marked blocker or diagnostic-only.

Acceptance criteria:

- Forward adapter can be treated as source-lag audited engineering evidence, not merely materialization smoke.

### 3. A7SEARCH7 Family-Diversified Queue

Type: search-preparation

Actions:

- Consume A7SHADOW-7 selected packet and overlap rejection map.
- Use the two selected OI/funding/premium candidates as positive priors, not as the entire search space.
- Force non-OI families into the queue: liquidity, taker flow, volatility, CE overlay, regime/event state.
- Apply caps by expression, skeleton, semantic pair, motif, base field, and economic exposure.
- Make rejected overlap variants negative memory for near-duplicate structures.

Verification:

- Queue report includes semantic-family coverage and cap enforcement.
- Open-interest/funding/premium does not dominate the queue.
- Every row has role/source/field contract trace.

Acceptance criteria:

- Queue is large, checkpointable, and family-diversified enough to test whether current bests are a true mechanism or only a narrow data-access artifact.

### 4. A7SEARCH7 Proxy Run And Aggregate

Type: execution-control

Actions:

- Run on company machine with shard manifests and restartable checkpoints.
- Use memory-enforced generator defaults.
- Monitor CPU/memory and avoid duplicate shard execution.
- Aggregate only after all expected shard manifests exist or a documented abort reason is written.

Verification:

- Completed shard count equals expected shard count.
- Eval error rows are counted explicitly.
- Aggregate selected rows are separated from strict accepted rows.

Acceptance criteria:

- Proxy aggregate is available as a source-of-truth artifact and can authorize bounded strict reward only if blockers are absent.

### 5. Strict Reward And Candidate Triage

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

### 6. Dedupe And Information-Source Audit

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

### 7. Reward/Leakage/Regime Gate Review

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

Monitor A7SEARCH7 proxy run until all shard manifests exist or a concrete shard failure is documented. Then aggregate selected proxy rows and only proceed to strict reward if the aggregate has no missing/suspect shards.
