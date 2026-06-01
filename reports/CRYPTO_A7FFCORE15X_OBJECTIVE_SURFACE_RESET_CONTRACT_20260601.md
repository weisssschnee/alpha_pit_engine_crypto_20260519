# CRYPTO A7FF-CORE15X OBJECTIVE SURFACE RESET CONTRACT

Generated: 2026-06-01T07:45:26Z

## Decision

`PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y`

A7FF-CORE15X stops replay expansion after CORE14SER and defines a reset contract for replay-stability objective-surface construction. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15y": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y",
  "dominant_failure": "objective_surface_not_replay_stable",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T07:45:26Z",
  "next_allowed": "A7FF-CORE15Y replay-stability objective-surface builder",
  "source_decision": "PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION",
  "source_stage": "A7FF-CORE14SER",
  "stage": "A7FF-CORE15X"
}
```

## Reset Axes

| axis                  | problem                                                                                    | repair_requirement                                                                       |
|:----------------------|:-------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------|
| A0_label_surface      | numeric clue selection does not translate into validation+recent 5bps replay clean breadth | score objectives by split-separate replay stability proxy before packet construction     |
| A1_control_surface    | wrong-lag/shuffle/placebo controls dominate most replay rows                               | make max non-signflip control margin a pre-packet hard gate, not only replay attribution |
| A2_cost_surface       | many high-tstat candidates lose positive spread after 5bps adjustment                      | use 5bps cost floor in objective-surface construction                                    |
| A3_family_surface     | clean evidence collapses to one semantic/motif family                                      | treat single-family clean evidence as non-expandable diagnostic, not search seed         |
| A4_expression_surface | packet repair increased outside-old coverage but did not improve replay stability          | stop queue reshuffling; rebuild objectives from replay-stability features                |

## Allowed Family Policy

| family                                    | status                                 | rule                                                                                                   |
|:------------------------------------------|:---------------------------------------|:-------------------------------------------------------------------------------------------------------|
| split_stable_basis_taker                  | diagnostic_only_until_stability_proven | allowed only if validation and recent both pass before any search expansion                            |
| control_margin_first_liquidity_volatility | conditional                            | allowed only with control_ratio < 0.8 in validation and recent at 5bps                                 |
| oi_positioning_retest                     | weak_prior_retest_only                 | requires non-replay numeric evidence plus split-stable replay proxy; no direct expansion               |
| fresh_objective_surface                   | preferred                              | construct from primitive response fields that survive split/control/cost gates before formula mutation |

## Next Contract

```json
{
  "action": "build replay-stability objective surface from existing response/replay rows; no formula generation",
  "forbidden": [
    "new formula generation",
    "bounded replay rerun",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "inputs": [
    "CORE13E numeric clues",
    "CORE14E replay rows",
    "CORE14SEE repaired replay rows",
    "CORE14R and CORE14SER forensic maps"
  ],
  "must_output": [
    "candidate replay-stability feature matrix",
    "family stability scorecard",
    "control/cost/split bottleneck map",
    "objective-surface allowed seed policy"
  ],
  "pass_minimum": {
    "candidate_count_with_split_stable_proxy": 32,
    "motif_bucket_count": 4,
    "semantic_bucket_count": 5,
    "top_family_share_max": 0.35
  },
  "stage": "A7FF-CORE15Y"
}
```

## Blocked Actions

| item                                | reason                                                         |
|:------------------------------------|:---------------------------------------------------------------|
| CORE14 packet rerun                 | already failed; CORE14R attributed control/cost/split collapse |
| CORE14SE repaired packet rerun      | already failed; CORE14SER found only one clean candidate       |
| CORE15 search-readiness             | blocked; clean pool breadth is insufficient                    |
| large search                        | blocked; replay-stable objective surface is not established    |
| alpha proof / shadow / paper / live | not authorized                                                 |
