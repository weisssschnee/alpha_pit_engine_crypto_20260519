# Crypto Search Carrier Activation & Fresh-State Matched Gate V1

## Result

The existing Search Engine, carrier loaders, compiler, evaluator, archive, and
checkpoint implementation completed three independent fresh-state gates. No
carrier, cache, compiler, AST, evaluator, or registry was duplicated.

| Carrier | Fields used | Strict | Attempts | Families | Positive matched |
|---|---:|---:|---:|---:|---:|
| full aggTrades | 44/44 | 256 | 256 | 256 | 0 |
| Core3 | 81/81 | 256 | 274 | 255 | 0 |
| OI/mark available | 69/71 sampled | 256 | 260 | 255 | 0 |

Every completed carrier has two atomic checkpoints with exact restore,
64 typed-random controls, 96 Hierarchical Typed CEM V2 candidates, and
96 Typed Evolution V2 candidates. Liquidation, the 25 zero-support OI/mark
fields, and Top50 raw OI/mark remained HOLD.

## Search authority repair

- The primary is evaluated independently against left-only and right-only
  support-matched controls. Pair reward is the worse strict-feasibility
  distance across the two incremental sleeves.
- Behavior identity is derived from incremental delta weights, not the primary
  portfolio.
- Transition collision memory is owned by the arm-and-seed policy. The global
  archive is reporting/champion state only.
- CEM uses current-checkpoint elite sufficient statistics plus one probability
  EMA. Historical counts remain diagnostic and are not consumed twice.
- Partial carrier grammars use the existing `field_role_surface` and compatible
  Skeleton subset.
- The Core3 carrier's mislabeled microsecond timestamp array is normalized by
  the existing `RawPanelStore` time authority; no cache was rebuilt.

## Equal-count matched diagnostics

All reward comparisons use the first 64 completed candidates per arm.

| Carrier | Arm | valid/hour | families/1k | mean reward | top-decile |
|---|---|---:|---:|---:|---:|
| aggTrades | random | 1013.16 | 1000 | -5.6013 | -3.5843 |
| aggTrades | CEM V2 | 972.92 | 1000 | -5.9883 | -3.1091 |
| aggTrades | Evolution V2 | 992.79 | 1000 | -5.8975 | -3.7823 |
| Core3 | random | 8232.96 | 1000 | -3.6194 | -1.2108 |
| Core3 | CEM V2 | 9166.64 | 1000 | -3.6217 | -1.6732 |
| Core3 | Evolution V2 | 8257.20 | 1000 | -3.4780 | -1.8060 |
| OI/mark | random | 341.57 | 1000 | -4.0708 | -1.7120 |
| OI/mark | CEM V2 | 345.53 | 1000 | -4.1670 | -1.9726 |
| OI/mark | Evolution V2 | 336.11 | 1000 | -4.0483 | -1.7145 |

No arm dominates random on density, discovery, mean reward, and top-decile
reward within any carrier. This small gate grants no larger-Arena
qualification.

## Bias audit

Decision: `HOLD_RESEARCH`.

The runs are fixed-retrospective development carriers with OOS grade `NONE`.
Costs, turnover, candidate-local support, PIT lag, overlapping-horizon HAC,
fresh state, and sealed boundaries are enforced. OI/mark remains a fixed
cohort without historical PIT-universe qualification. No result is Alpha,
OOS, promotion, or evidence that the wider crypto Alpha space is empty.

The ledger persists the authoritative pair reward and left incremental
waterfall, while the right-axis waterfall is bound through the producer source
and frozen evaluator contract but is not separately persisted row-by-row.
That traceability gap must be closed before any larger Arena; these 768
candidates must not be rerun merely to backfill it.

## Pre-evaluation failures retained

Two zero-strict failures are preserved: an undersized attempt-reservation
contract and a partial-grammar/behavior-contract activation failure. Neither
read a successful reward or contributes to the 768 completed-candidate budget.
