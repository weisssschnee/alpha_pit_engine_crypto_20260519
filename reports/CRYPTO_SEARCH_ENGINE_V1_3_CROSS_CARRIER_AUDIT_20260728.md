# Crypto Search Engine V1.3 Cross-Carrier Audit

## Decision

Engineering integrity is `PASS`. Research remains
`HOLD_RESEARCH_FIXED_RETROSPECTIVE_CROSS_CARRIER`. No arm qualifies for a
future new-data Arena, and no Alpha, OOS, challenge, forward, or promotion
claim is authorized.

## Scope and reuse

V1.3 reused the existing `RawPanelStore`, Broad39 registry, full aggTrades44
carrier, `CandidateSpec`, 40 Skeletons, typed compiler, matched evaluator,
Behavior Archive, CEM V2, Evolution V2, and checkpoint implementation. It did
not create another AST, compiler, evaluator, materializer, registry, scheduler,
database, or checkpoint service.

The only legal aligned cross-source surface was the existing 2024H1 physical
carrier containing Broad39 and aggTrades44 over 121 assets. OI/mark begins
after every other verified target cache ends, so it was not falsely joined.
Core3 remained excluded because its verified context contains only three
assets.

## Independently recomputed results

| Arm | Strict | Valid unique / CPU-hour | Families / 1k | Mean reward | Top-decile reward | Duplicate rate |
|---|---:|---:|---:|---:|---:|---:|
| Typed random | 800 | 1076.120083 | 1000.000 | -5.434222 | -3.150546 | 0.000% |
| CEM V2 | 1600 | 1247.791385 | 1000.000 | -5.247853 | -3.321730 | 0.063% |
| Evolution V2 | 1600 | 1092.292558 | 909.375 | -4.541431 | -2.344488 | 9.125% |

Campaign totals:

- 4,000 strict, compile-valid, exact-unique, matched-control-valid,
  full-cost evaluations from 7,165 raw attempts.
- 4,000/4,000 candidates contain at least one Broad and one aggTrades field.
- Broad field exposure: 39/39; aggTrades field exposure: 44/44.
- 3,848 behavior families; 3.8% duplicate rate.
- Zero positive matched discoveries.
- Four atomic checkpoints restored exactly.
- Right-control and right-incremental waterfall, behavior IDs, feedback, and
  delta-weight hashes are separately persisted for all 4,000 rows.
- Manifest artifacts and hashes independently matched; sealed reads are zero.

CEM improved valid-unique density and mean reward versus typed random, but its
top decile was worse. Evolution improved mean and top-decile reward and slightly
improved density, but lost 90.625 behavior families per 1,000 evaluations and
reached a 9.125% duplicate rate. Neither arm passes the complete qualification
gate.

## Bias Audit

- Data source and universe: fixed retrospective Broad39 × delivered aggTrades44
  carrier; not a historical PIT-complete exchange universe.
- Frequency and horizon: hourly, existing 1h/4h candidate horizons.
- OOS sample grade: `NONE`.
- Cost model: existing 5 bps full-L1 matched evaluator cost.
- Turnover: recomputed from each left/right incremental delta-weight sleeve.
- Discovery status: fixed-retrospective development search.
- Look-ahead/PIT: existing lag contracts and matched raw support preserved.
- Survivorship: current delivered cohort limitations remain.
- Replay: fresh policy/archive state; old trajectories were not imported.

### Decision

`HOLD_RESEARCH`

The zero-positive result rejects qualification of these search arms on this
fixed cross-source surface. It does not establish that crypto has no Alpha or
that OI/mark/Core3 cross-carrier mechanisms are economically negative.
