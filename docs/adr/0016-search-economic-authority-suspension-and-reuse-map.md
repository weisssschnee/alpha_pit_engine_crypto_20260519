# ADR 0016: Search Economic Authority Suspension and Reuse Map

- Status: Accepted
- Date: 2026-07-29
- Supersedes: ADR 0014 as an economic optimizer authority decision
- Amends: ADR 0015 by requiring every bound component to be an active authority

## Context

ADR 0014 correctly removed strict matched-feasibility distance from adaptive
ordering, but it promoted a copied Phase3CM-style formula before the crypto
candidate contract expressed the economic decision that formula was meant to
score.

The retained `CandidateSpec` freezes one horizon and always selects
`CROSS_SECTIONAL_ZERO_NET`. It does not bind a signal direction or orientation
rule, portfolio role, execution venue/instrument, executable price, or
venue-specific cost. The copied reward consequently duplicates its selected
horizon in the nominal worst-horizon term, uses IID daily resampling, and
scores the primary portfolio while matched attribution and behavior identity
describe incremental sleeves.

The wider repository already contains useful pieces, but no single existing
node closes that economic contract:

- `instrument_capability.mapping` is the formal mapping implementation;
- `instrument_canary` provides hashed target/mapping/cost receipts, lazy
  first-visit materialization, and immutable event/receipt ledgers;
- `pair18m` provides A/B/AB/ABC matched controls, incremental delta-weight
  identity, turnover accounting, and dependence-aware monthly diagnostics;
- A7Reward-1 contains train-frozen orientation and portfolio risk primitives,
  but its validation, recent, stress, and OOS roles are outside the current
  search boundary;
- the CN Phase3CM campaign demonstrates explicit direction and conservative
  standalone-plus-incremental ordering, but its market, long-only, cost, and
  tradability contracts are not crypto authority.

CURRENT also bound `adaptive_strict_feasibility_feedback` as a global FORMAL
adaptive feedback authority even though its implementation and evidence are
the instrument-capability canary. Finally, the real-experiment preflight
accepted components whose nodes explicitly said `active_authority: false`.

## Decision

1. `PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1` remains reproducible code and a
   diagnostic prototype. It is suspended as the sole qualified economic
   optimizer authority.
2. The Search Engine node remains the current engineering capability for
   carriers, typed expressions, compiler validation, matched controls,
   deterministic replay, campaign-local archive, adaptive mechanics, and
   checkpoint restoration. No existing policy or campaign state is revived.
3. `adaptive_strict_feasibility_feedback` remains formal only for
   capability/admission feasibility. Its semantic role is narrowed to
   `capability_strict_feedback_authority`; it is not a market optimizer reward.
4. `explicit_portfolio_mapping` remains formal and reusable. A future search
   adapter must select a legal mapping from mechanism semantics instead of
   hardwiring every candidate to cross-sectional zero-net.
5. The canonical `run*` preflight must reject any semantic binding whose
   component is missing, stale, failed, conflicting, or not explicitly active.
   NON_FORMAL is visible but runnable only when the bound component itself is
   active.
6. No market search is authorized. A successor economic authority must, in one
   frozen receipt, bind:
   - mechanism and economic hypothesis;
   - signal direction or train-frozen orientation;
   - portfolio role and canonical mapping;
   - target, execution venue/instrument/price, holding semantics, and cost;
   - train-only standalone portfolio objective;
   - matched incremental objective over identical support and execution;
   - dependence-aware uncertainty;
   - distinct validation kill-line and read-only holdout.
7. The successor ordering must not hide the disagreement between standalone
   quality and mechanism increment. The default design basis is a conservative
   joint rule such as `min(standalone_train_score, matched_increment_score)`,
   subject to an explicit future contract and tests; this ADR does not promote
   that formula.

## Consequences

- Graph/CURRENT is a control plane and may be corrected when source scope or
  runtime evidence contradicts it.
- The current Graph bindings deliberately leave target, optimizer reward,
  execution price, and cost attached to inactive experimental components.
  The preflight therefore blocks fresh market execution.
- Existing V1.1-V1.4 evidence is unchanged. It remains engineering,
  matched-attribution, and replay evidence under its original contracts.
- No second AST, compiler, evaluator, Graph layer, scheduler, or experiment
  database is created.

