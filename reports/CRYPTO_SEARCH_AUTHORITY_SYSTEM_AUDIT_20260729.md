# Crypto Search Authority System Audit

- Scope: repository-wide search, reward, mapping, target, receipt, evaluator,
  archive, checkpoint, and CURRENT authority chains
- Market candidate evaluations: `0`
- New search budget: `0`
- Decision: `ENGINEERING_CHAIN_RETAINED / ECONOMIC_AUTHORITY_SUSPENDED`

## Executive verdict

The system does not need a new search platform. The reusable engineering chain
is substantial and internally coherent. The defect is narrower and more
important: no current component binds candidate economic meaning all the way
from mechanism through direction, mapping, executable target/cost, standalone
portfolio quality, and matched increment.

ADR 0014 fixed the wrong optimizer input but over-promoted the replacement
formula. Its `PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1` implementation is a
deterministic diagnostic prototype, not yet a qualified economic authority.

## Authority findings

| Claim | Source/runtime finding | Verdict |
|---|---|---|
| Search reward is Phase3CM-style economic authority | One candidate horizon makes the nominal worst-horizon term duplicate the same Sortino; daily bootstrap is IID; only the primary portfolio is scored | SUSPEND_AUTHORITY |
| Candidate economics are explicit | `CandidateSpec` has expression, horizon, and mapping id, but no direction/orientation, portfolio role, execution venue/instrument/price, or holding contract | GAP |
| Mapping is mechanism-derived | Search candidate builders hardwire `CROSS_SECTIONAL_ZERO_NET` | GAP |
| Matched attribution is real | `pair18m` evaluates both binary axes and hierarchical A/B/AB/ABC increments on shared support and execution, with delta-weight identities | RETAIN |
| Behavior novelty is incremental | Archive identity uses incremental delta weights and excludes gross, net, cost, and reward | RETAIN |
| Strict feedback is global optimizer authority | `instrument_capability.feedback` is a capability-canary lexicographic feasibility tuple | SCOPE_TO_CAPABILITY |
| CURRENT preflight fails closed | Inactive Search Engine and cost nodes were returned as runnable NON_FORMAL boundaries | REPAIR |

## Reuse map

| Chain | Reuse decision | Required adaptation |
|---|---|---|
| Search carriers, RawPanelStore, FieldContract, typed registry | KEEP_AS_IS | Bind carrier and field receipts into the future economic contract |
| Existing Skeleton, CandidateSpec, compiler, matched controls | KEEP | Extend the existing candidate/receipt contract; do not create a second AST or compiler |
| CEM/Evolution proposal and checkpoint mechanics | KEEP_SUSPENDED | Reactivate only under a fresh, qualified optimizer authority |
| Behavior Archive and incremental delta-weight identity | KEEP | Champion ordering must consume the successor joint economic objective |
| `instrument_capability.mapping` | KEEP_FORMAL | Select mapping from mechanism/portfolio role rather than globally hardwire one mapping |
| `instrument_canary` authorization receipt and lazy engine | REUSE_PATTERN_AND_CODE | Generalize only the thin receipt fields needed by the existing Search Engine |
| `pair18m` turnover, cost path, A/B/AB/ABC, HAC/monthly audit | KEEP | Make standalone and incremental objectives share the same bound execution contract |
| A7 train-frozen orientation and risk primitives | REUSE_PURE_PRIMITIVES_ONLY | Exclude validation, recent, stress, OOS, and leaderboard logic |
| CN Phase3CM explicit direction and conservative joint score | REUSE_DESIGN_PATTERN_ONLY | Do not copy A-share portfolio, tradability, cost, horizons, or uncommitted code |
| Historical V1.1-V1.4 policy/archive/checkpoint state | DO_NOT_REUSE | Preserve only immutable evidence and replay provenance |

## First breakpoints

1. **Economic hypothesis to candidate:** Skeleton prose is not an enforced
   direction, portfolio role, or mapping contract.
2. **Candidate to mapping:** every compositional and conditional candidate is
   assigned `CROSS_SECTIONAL_ZERO_NET` despite three other canonical mapping
   contracts.
3. **Candidate to execution:** Binance target identity exists in the V1.4
   replay contract, not in the general Search Engine candidate/receipt.
4. **Execution to reward:** the primary-only score is not jointly constrained
   by matched mechanism increment.
5. **Uncertainty:** optimizer bootstrap breaks daily dependence while the same
   evaluator already contains dependence-aware monthly diagnostics.
6. **Control plane:** CURRENT had inactive components bound to runnable roles
   and a capability-only feedback node exposed as global adaptive authority.

## Implemented closure repair

- `experiment_authority` now requires `active_authority: true` for every bound
  role; inactive target, reward, execution, or cost blocks before a `run*`
  command reaches candidate generation.
- CURRENT scopes strict-feasibility feedback to capability admission rather
  than economic optimizer authority.
- CURRENT marks the Search Engine as retained engineering capability with
  economic optimizer authority suspended.
- Tests lock both the active/non-formal distinction and the current inactive
  economic bindings.

## Minimal successor implementation

The next authorized code task should modify the existing contracts, not build a
parallel system:

1. add economic direction/orientation, portfolio role/mapping, and executable
   target/cost identity to the existing candidate authorization receipt;
2. derive mapping from mechanism semantics using the formal mapping module;
3. compute train-only standalone portfolio quality and matched incremental
   quality on one execution contract, with dependence-aware uncertainty;
4. define a conservative joint ordering and a distinct validation kill-line;
5. prove receipt/hash/replay/checkpoint restoration with synthetic and
   constructibility tests before any market evaluation.

No new market search, historical candidate replay, OOS, promotion, or larger
budget is justified by this audit.

