# CRYPTO A7FF-CORE21 REPLAY TRANSLATION RESET CONTRACT

Generated: 2026-06-01T15:07:18Z

## Decision

`PASS_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_READY_FOR_CORE21E`

CORE21 resets replay translation objectives after bounded replay supply failure. It does not execute formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core20": false,
  "authorizes_core21e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_READY_FOR_CORE21E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:07:18Z",
  "next_allowed": "A7FF-CORE21E replay translation matrix audit",
  "source_best_clean_candidate_count": 4,
  "source_best_clean_seed_lane_count": 2,
  "source_decision": "PASS_A7FFCORE19SER_REPLAY_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE21",
  "source_stage": "A7FF-CORE19SER",
  "stage": "A7FF-CORE21"
}
```

## Reset Policy

| axis              | allowed                                                                                               | forbidden                                                      |
|:------------------|:------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
| label_translation | evaluate raw, cross-sectional, liquidity-tier, vol-adjusted, and ranked labels as separate objectives | using ranked/L5-only evidence as search-ready proof            |
| cost_model        | report 2/5/10/20bps tiers separately and define low-turnover lane gates                               | selecting by the easiest cost tier without diagnostic labeling |
| lag_model         | separate same-bar, one-bar, stale-lag, and label horizon effects                                      | promoting same-bar-only behavior                               |
| lane_breadth      | treat S2/S3 clean clues as diagnostic anchors and require S0/S1 translation repair                    | single-lane replay-clean promotion                             |
| candidate_source  | reuse locked packet and CORE19E rows for attribution; no new formula generation                       | open grammar expansion or large search                         |

## Execution Plan

| stage        | action                                       | input                                       | authorized   |
|:-------------|:---------------------------------------------|:--------------------------------------------|:-------------|
| A7FF-CORE21E | label/cost/lag/lane translation matrix audit | CORE19E replay rows + CORE17E locked packet | True         |
| A7FF-CORE22  | bounded replay objective repair contract     | CORE21E pass only                           | False        |

## Blocked

| blocked_task                        | reason                                                                           |
|:------------------------------------|:---------------------------------------------------------------------------------|
| CORE20                              | superseded by CORE19SER hold; replay-clean supply insufficient                   |
| large search                        | blocked until replay translation reset produces robust multi-lane clean evidence |
| formula generation/search           | blocked: CORE21 is translation reset only                                        |
| alpha proof / shadow / paper / live | not authorized                                                                   |
