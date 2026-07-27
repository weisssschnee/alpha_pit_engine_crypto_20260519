# Crypto Search Engine V1 code-authority audit

- Target: `6fe4f96417476693b57ea9ff543e1f5da3952ed0`
- Original baseline: `bbb0e696bc5f560f733dd4e9bfe263f11e4bb840`
- Scope: source contracts and future-run behavior only
- Historical 20k artifacts modified: `NO`
- New search/cache/Arena: `NO`
- Sealed reads: `0`

## Decision

The external audit correctly identified authority misalignment in behavior
identity, turnover, adaptive arm state, CEM updates, and final qualification.
Those defects were repaired without replacing the existing AST, compiler,
matched-control constructor, strict evaluator, or checkpoint system.

| Audit item | Finding | Disposition |
|---|---|---|
| Dual single-axis controls | Real attribution limitation | `VERSIONED_CONTRACT_REQUIRED`; not silently added because `CandidateSpec`, strict-count semantics, and the frozen evaluator currently own one matched ablation |
| Incremental Behavior Archive | Confirmed | Fixed: family identity uses delta signal/weight; primary/control IDs are annotations |
| Turnover identity | Confirmed | Fixed: evaluator and Archive share one horizon-phased full-L1 authority |
| Arm-local adaptive state | Confirmed | Fixed: policy-local family counts own Evolution novelty; CEM tie-break reads arm×seed-local completion counts |
| CEM historical double weighting | Confirmed | Fixed: current-checkpoint elite distribution is smoothed once into prior probabilities; cumulative counts are observation diagnostics only |
| Replace strict pair reward | Contract conflict | Rejected for V1: the original contract keeps strict `pair_reward` as the only ordering authority; fixed-cost/turnover redundancy remains an explicit versioned reward-contract issue |
| Final arm qualification | Confirmed | Fixed: engineering execution and strategy qualification are separate; reward non-inferiority, clear productivity gain, duplicate ceiling, four-seed agreement, two-checkpoint consistency, and frozen tolerance are required |
| Representation whitelist | Confirmed | Fixed conservatively for field-family normalizers and typed-role windows |
| `market_context == local` | Claim not established | No change: `CrossAssetRelative` explicitly converts the right asset-local source into a contemporaneous cross-sectional reference; replacing it with a cross-sectionally constant market aggregate would make the current operator degenerate |
| Ineffective genes | Confirmed for V2 | Fixed: CEM V2 and Evolution V2 sample/cross only effective genes; V1 controls retain their policy identity and share compiler legality gates |
| Evolution population collapse | Partial | Added bounded mechanism cells plus effective-parent, lineage-entropy, top-root-share, and mechanism-occupancy diagnostics |

An additional Standards-axis defect was fixed: behavior-contract freezing had
validated `active_universe_size` against its own finite mask. It now requires
an independent observed-support mask with exact coordinate equality.

## Deferred blockers

Dual left/right controls and reward-authority replacement are not ordinary bug
fixes. They would change the frozen evaluator and candidate/ledger identities.
They require a separately authorized versioned contract before any fresh run;
no placeholder interface or second evaluator was added.

## Verification

- New authority/penetration tests: `11`
- Full suite: `242 passed, 1 warning`
- Historical checker: engineering `PASS`, errors `[]`
- Historical strict count/checkpoints: `20,000` / `10`
- Historical component qualification: `HOLD_POST_AUDIT_REMEDIATION_REQUIRED`
- Future qualified arms from historical evidence: `[]`

The historical 20k campaign remains engineering replay evidence only. These
source repairs do not establish Alpha, new economic evidence, OOS, promotion,
challenge, recent/May-stress/forward evidence, or permission for another Arena.
