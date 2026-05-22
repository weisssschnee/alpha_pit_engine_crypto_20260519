# Crypto A7W-0 Post Source-Trace Status

- generated_at: `2026-05-22T06:29:19Z`
- decision: `PASS_A7W0_SOURCE_TRACE_RESOLVED_SIGNAL_LINE_STILL_HOLD`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Purpose

A7W-0 separates the data-line result from the alpha-line result after A7U-0R was repaired.

Data status: the enhanced aggTrades panel source trace is complete. The previous `source_trace_incomplete` caveat is removed.

Signal status: A7V smoke positives still fail May stress and control dominance checks. A7U-0R PASS does not revive A7V candidates.

## Stage Status

| stage   | decision                                           | blockers                                                                                                                | executes_search   | executes_replay                       | authorizes_alpha_proof   | authorizes_full_search   | authorizes_expanded_replay   | authorizes_shadow_paper_live   |
|:--------|:---------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:------------------|:--------------------------------------|:-------------------------|:-------------------------|:-----------------------------|:-------------------------------|
| A7U-0R  | PASS_A7U0R_SOURCE_TRACE_COMPLETE                   |                                                                                                                         | False             | False                                 | False                    | False                    | False                        | False                          |
| A7V-5   | PASS_A7V5_SMALL_REPLAY_SMOKE_METHOD_ONLY           |                                                                                                                         | False             | small_smoke_only                      | False                    | False                    | False                        | False                          |
| A7V-6   | HOLD_A7V6_NO_POST_MAY_DOMINANT_CANDIDATE           | no_a7v5_positive_survives_may_stress;matched_controls_positive_for_a7v5_positives;pre_may_clues_family_concentrated     | False             | False                                 | False                    | False                    | False                        | False                          |
| A7V-7   | HOLD_A7V7_ACTIVITY_LIQUIDITY_CLUES_FAIL_MAY_STRESS | all_pre_may_clues_fail_may_stress;activity_liquidity_family_concentration;matched_control_contamination_present_in_a7v6 | False             | forensic_recompute_on_a7v6_clues_only | False                    | False                    | False                        | False                          |

## Current Boundary

- The unified panel can be used for controlled experiments without the prior source-trace caveat.
- A7V-5 remains method-only smoke.
- A7V-6 and A7V-7 block expanded replay from the current activity/liquidity clue family.
- No alpha proof, shadow, paper, live, or production claim is authorized.

## Authorization

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_controlled_experiments_without_source_trace_caveat": true,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "a7v_signal_family_blocked"
  ],
  "current_a7v_activity_liquidity_family_promotable": false,
  "decision": "PASS_A7W0_SOURCE_TRACE_RESOLVED_SIGNAL_LINE_STILL_HOLD",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T06:29:19Z",
  "required_next": [
    "Do not expand current A7V activity/liquidity clue family",
    "Use A7U-0R PASS only as data provenance closure, not alpha evidence",
    "If continuing, define a new aggTrades objective/horizon/family redesign stage"
  ],
  "source_trace_incomplete_caveat_removed": true
}
```

## Required Next

- Do not expand the current A7V activity/liquidity clue family.
- If continuing aggTrades research, start from objective/horizon/family redesign, not from A7V-5 positive labels.
- Any new panel refresh must rerun A7U-0R before source-trace claims.
