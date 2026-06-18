# Crypto Pipeline Chain Audit 20260618

## Executive Finding

The current crypto line has usable pieces for data preparation, field enforcement,
proxy evaluation, strict reward, and aggregation. The weak link is not one single
formula. The weak link is that search is still mostly a queue-generation and
sharded-evaluation workflow. A verified integrated optimizer loop such as CEM,
AST-search, or MCTS connected to strict reward is not present in the verified
crypto core.

## Layer Findings

### 1. Data

Status: `PROVISIONAL_PASS`.

Evidence exists for pre-2024 backfill acceptance, recent patch merged panel,
duplicate timestamp checks, age fields, and recent OI/funding/mark/index/premium
coverage. These data are acceptable for controlled research. They should not be
treated as final proof data until source trace/checksum auditing is finished.

Main risk handled: listing gaps and panel continuity.

Main risk not fully handled: production-grade source trace and dynamic PIT proof
across every downstream script.

### 2. Formula / Feature Layer

Status: `PASS` for enforcement/parity, `PROVISIONAL_PASS` for broad generation.

`feature_algebra.py`, `formula_gen_v2_adapter.py`, A7AI-F2, and A7AI-F3 provide
the best current foundation: field roles, fail-closed behavior, and evaluator
parity for approved operators. This is the part that should be preserved.

Main risk handled: label/future/timing-blocked fields should not silently enter
ordinary alpha formula generation.

Main risk not fully handled: new panel schemas and new operators require reruns
of parity and field-contract checks. Generated formulas are not automatically
valid factors.

### 3. Search Space

Status: `PROVISIONAL_PASS`.

The repo has queue builders, typed AST governance, AST parsing, and subgraph
registry. These are useful. They are not the same as a search optimizer.

Main risk handled: formula representation, skeleton/subgraph hygiene, forbidden
field filtering in queue construction.

Main risk not handled: no verified CEM/AST/MCTS optimizer core is currently
connected to strict reward as an automated feedback loop.

### 4. Fast Evaluation

Status: `PROVISIONAL_PASS`.

`crypto_a7v3s9_prereward_oos_control_proxy.py` is usable as a fast filter. It
has recent evidence from A7FAST2: all 32 proxy shards aggregated successfully.
It should remain explicitly labeled proxy/surrogate and should not be treated
as strict acceptance.

Main risk handled: cheap OOS/control filtering before strict reward.

Main risk not fully handled: proxy false positives/false negatives need periodic
calibration against strict reward, especially after new data panels.

### 5. Strict Reward

Status: `PROVISIONAL_PASS`.

`crypto_a7reward1_portfolio_reward_model.py` is the current strict gate. It
uses train orientation, OOS non-overlap floors, stress floor, shuffle/lag/stale
controls, objective vectors, and accepted/rejected queues. A7FAST2 strict reward
produced 30 accepted rows from 764 reward rows.

Main risk handled: raw high Sortino candidates are rejected if train edge,
OOS floors, or controls fail.

Main risk not fully handled: accepted strict reward is still not alpha proof.
The module imports older evaluator/preflight modules and needs a cleaner
parameterized runtime contract.

### 6. Aggregation

Status: `PASS` for proxy aggregate after `355b515`; `PROVISIONAL_PASS` for reward
aggregate.

The proxy aggregate bug was fixed: generic shard discovery now works. Reward
aggregation worked for A7FAST2, but still contains a stage-specific shard regex.

Main risk handled: manifests and result files can be consolidated.

Main risk not fully handled: launch status CSV can falsely mark completed shards
as failed; aggregation should trust manifests and runtime outputs first.

### 7. Regime

Status: `PROVISIONAL_PASS`.

Regime audits exist and should be preserved. The open question is not whether
regime states are computable. They are. The open question is whether they cover
enough crisis mechanisms and event types to support robust train/OOS inference.

Main risk handled: candidate behavior can be attributed by mechanism regime.

Main risk not fully handled: regime/event sufficiency and leave-one-event-out
validation remain required.

## Components Explicitly Not Verified

- CEM search optimizer connected to strict reward.
- AST search optimizer connected to strict reward.
- MCTS search optimizer connected to strict reward.
- Any alpha proof, paper, shadow, or live workflow.

## Next Engineering Target

Create a real search-core contract:

1. Search candidate generator must consume only current `accepted_for_next_search`
   or explicitly approved exploration priors.
2. Search state must record origin: exploitation, exploration, mutation,
   field-pair expansion, AST-subgraph expansion, or raw exploration.
3. Reward feedback must be automatic: proxy can prune; strict reward decides
   promotion.
4. Aggregation must be prefix-agnostic and manifest-first.
5. Every run must write a run manifest, shard plan, input queue hash, data panel
   identity, code commit, and reward version.

