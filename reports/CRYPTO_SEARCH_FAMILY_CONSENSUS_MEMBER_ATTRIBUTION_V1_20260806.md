# Crypto Search Family Consensus Member Attribution V1

## Decision

`HOLD_RESEARCH`

The 23-member 4h two-axis flow-intensity/stateful family did not fail because its members cancelled one another. Across each member's full stored objective path, 20/23 retain positive gross on both matched axes, but only 7/23 retain positive net on both axes and none has positive net-LCB on both axes. Under the frozen branch order this is `EXECUTION_DRAG` at member level.

The consensus terminal failure is narrower and more important: exact common support falls from a median 330 individual objective hours to 66 hours (20%). On those 66 hours, both consensus incremental gross means are already negative. Cost worsens the result but does not create the sign failure.

## Read-only method

- Input cohort: all frozen 23 `main` members; no member was added, removed, or reoriented.
- Sources: committed candidate ledger, `checkpoint_000` hourly sleeves and sparse asset positions, consensus metrics, concentration table, and the consumed receipt.
- Recalculation: member gross/net means were independently recomputed from stored hourly paths; behavior alignment was independently recomputed from stored incremental weights on the exact consensus common mask.
- No market payload, target, validation/OOS/holdout, candidate generator, evaluator, optimizer, Archive, or reward was read or run.
- Frozen diagnostic thresholds and branch order are in `runtime/crypto_search_family_consensus_member_attribution_v1_20260806/frozen_contract.json`.

## Member economics

| Measure | Result |
|---|---:|
| Members | 23 |
| Gross positive on both matched axes | 20 |
| Net positive on both matched axes | 7 |
| Net-LCB positive on both matched axes | 0 |
| Gross-both positive but net-both not positive | 13 |
| Current validation reward positive | 6 |
| Matched positive | 0 |
| Train-to-current-validation reward Spearman | -0.605 |

The gross mechanism is therefore not extinct on the members' full paths. It is thin relative to execution drag for most members, and train reward does not provide stable current-window ordering. The six current positive rewards are descriptive only; selecting them now would be post-selection leakage.

## Consensus support and economics

| Axis | Gross mean | Cost mean | Net mean |
|---|---:|---:|---:|
| `AB - left control` | -0.548 bps | 1.017 bps | -1.565 bps |
| `AB - right control` | -1.415 bps | 1.623 bps | -3.037 bps |

The exact consensus mask is the intersection of primary, left-control, and right-control evaluation masks across all 23 members. It contains 66 hours versus a median 330 hours per member. The 20% retention is below the frozen 25% material-bottleneck threshold.

This explains why positive member-level gross and negative consensus gross can coexist: the consensus is evaluated on a much narrower shared slice, and that slice reverses the gross sign. Reducing the 5 bps cost would not make a negative-gross consensus economically valid.

## Member alignment

| Incremental sleeve | Weight retention | Median pairwise cosine | Negative pairs |
|---|---:|---:|---:|
| `AB - left control` | 93.33% | 0.461 | 4/253 |
| `AB - right control` | 96.82% | 0.460 | 11/253 |

Both retention ratios are far above the frozen 50% family-incoherence threshold. The family is behaviorally aligned; averaging does not materially cancel its weights. The failure is not an ensemble-sign conflict.

## Failure attribution

1. `GROSS_MECHANISM_DECAY` on full member paths: **not supported** (20/23 gross-both positive).
2. `EXECUTION_DRAG` on full member paths: **supported** (only 7/23 net-both positive).
3. `FAMILY_INCOHERENCE`: **not supported** (93.3%/96.8% incremental-weight retention).
4. Material common-support bottleneck: **supported** (66/330 = 20%).
5. Consensus terminal observation: **gross sign reversal on the exact common-support slice**, followed by additional cost drag.

## Bias Audit

- Discovery and attribution are separated: this readout did not generate or select candidates.
- The family and thresholds were frozen before the aggregate readout.
- The current interval is already development-fresh evidence and is now spent for selection.
- The 66-hour shared slice is too small for promotion and all dual-axis net-LCB results remain non-positive.
- No OOS, challenge, forward, or promotion authority is created.

Bias Audit decision: `HOLD_RESEARCH`.

## Required action

Close the current equal-weight family-consensus construction. Do not rescue it by lowering cost, selecting the six current positive members, or rerunning the interval. Preserve the 4h flow-intensity pocket only as descriptive mechanism evidence.

Any separately authorized future mechanism experiment must establish uniform, pre-frozen member support before aggregation and should spend budget on genuinely different mechanism forms rather than another parameterized consensus of this family. This report does not itself authorize that experiment.
