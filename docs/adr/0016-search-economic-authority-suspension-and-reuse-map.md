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
8. The retained evaluator now implements that design basis as
   `CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2` for future fresh-state use:
   - the duplicated nominal worst-horizon term is removed because
     `CandidateSpec` binds only one horizon;
   - ordered daily returns use deterministic stationary bootstrap under
     `CRYPTO_ORDERED_DAY_STATIONARY_BOOTSTRAP_V1`, not IID resampling and not
     an MCMC or posterior claim;
   - primary and every required matched delta-weight sleeve share the exact
     same bootstrap index path;
   - binary ordering uses the minimum of primary, primary-minus-left-control
     and primary-minus-right-control portfolio components;
   - hierarchical ordering uses the minimum of primary, `AB-A`, `AB-B`, and
     `ABC-AB` portfolio components;
   - legacy V1 reward identities cannot seed adaptive state.
9. This implementation is crypto-only: continuous UTC crypto semantics are
   declared and no A-share T+1, ST, price-limit, stamp-duty, suspension, CN
   evaluator, CN reward or CN market-cost rule is applied.
10. `CRYPTO_SEARCH_ECONOMIC_RECEIPT_V1` is the thin successor binding for a
    future fresh development campaign. It does not copy any evaluator:
    - mechanism and hypothesis resolve to the existing Skeleton registry;
    - every Broad and conditional mechanism family has an explicit mapping
      class and resolves through the existing mechanism-to-mapping authority
      instead of a candidate-global mapping literal;
    - direction resolves to A7Reward's train-frozen orientation and the
      retained pair evaluator has an explicit receipt-bound consumption path;
    - mapping resolves to formal `explicit_portfolio_mapping`; the full-L1
      5 bps cost remains a NON_FORMAL frozen Binance venue assumption;
    - target and execution resolve to the existing Binance USD-M delayed-open
      target contract; the worker wraps the retained carrier with the existing
      `BinanceTargetStore` and the evaluator verifies its target metadata;
    - the evaluator consumes the receipt-bound cost rather than its legacy
      module default, while the 5 bps value remains NON_FORMAL;
    - optimizer reward resolves to
      `CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2`;
    - validation resolves to a distinct pure no-feedback development
      kill-line whose runtime adapter stops the failed arm and atomically
      writes its checkpoint without reading test/recent/stress/holdout, while
      the later holdout remains unreadable.
    Every referenced component is content-hash frozen. Alternate receipt paths
    are rejected and both CLI and direct runner entry points re-resolve the
    committed receipt. This schema requires `run_authorized=false`; source
    qualification cannot activate a market experiment or promote any
    NON_FORMAL role.

## Consequences

- Graph/CURRENT is a control plane and may be corrected when source scope or
  runtime evidence contradicts it.
- The current Graph bindings deliberately leave target, optimizer reward,
  execution price, and cost attached to inactive experimental components.
  The preflight therefore blocks fresh market execution.
- Existing V1.1-V1.4 evidence is unchanged. It remains engineering,
  matched-attribution, and replay evidence under its original contracts.
- The V2 source repair does not activate optimizer authority. Direction,
  portfolio role, tradable venue/instrument/price, an explicitly NON_FORMAL
  frozen venue-cost assumption, a distinct validation kill-line and read-only
  holdout now have one content-hashed successor receipt, but the receipt
  remains run-inactive and has no runtime or market evidence.
- The fresh validation campaign orchestration is now reusable source through
  the dedicated `crypto_search_economic_v1` entry point. It reuses the existing
  rolling Search Engine plus the qualified 115-field OI/mark x aggTrades carrier
  and deliberately does not attach the 2025 receipt partitions to the historical
  2023-2024 legacy run. Behavior descriptor bins and support identity are frozen
  from the receipt train block only; validation and holdout do not contribute.
  Train and validation each purge their final six hours, equal to the two-hour
  execution delay plus maximum four-hour horizon, so target endpoints never
  cross an evidence-role boundary. Receipt component hashes canonicalize text
  line endings to LF before hashing.
  Immediately after
  `checkpoint_000` updates and restores the frozen train policy, and before
  `checkpoint_001` allocation, it selects the top 64 train candidates for each
  required 1h/4h horizon per active arm (128 total), consumes each candidate's persisted train
  orientation and train-frozen limiting matched sleeve, evaluates only the
  receipt validation block, aggregates an equal-weight ensemble with a
  worst-horizon floor, invokes the existing kill-line, writes failed arms to
  the existing `arm_states`, and atomically publishes/restores
  `checkpoint_validation`. The next existing allocation consumes those states,
  so a failed adaptive arm receives zero subsequent budget; a failed typed-random
  control stops continuation. Policy state, archive state, generation attempts,
  and holdout access remain unchanged. Resume ordering selects validation over
  its same-progress train checkpoint, then selects any later numeric checkpoint
  after continuation. This is source and synthetic-test evidence only; no
  validation campaign ran.
- No second AST, compiler, evaluator, Graph layer, scheduler, or experiment
  database is created.
