# CRYPTO A7FF-CORE23 EXECUTABLE-HORIZON REDESIGN CONTRACT

Generated: 2026-06-01T15:27:52Z

## Decision

`PASS_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_READY_FOR_CORE23E`

CORE23 redirects the current packet from same-bar-dominated replay toward executable-horizon diagnostics. It does not execute formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core23e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_READY_FOR_CORE23E",
  "dominant_failure": "same_bar_diagnostic_dominates_one_bar_executable",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:27:52Z",
  "next_allowed": "A7FF-CORE23E executable-horizon diagnostic audit",
  "source_decision": "PASS_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_COMPLETE_READY_FOR_CORE23",
  "source_stage": "A7FF-CORE22R",
  "stage": "A7FF-CORE23"
}
```

## Horizon Policy

| axis              | allowed                                                               | forbidden                                                     |
|:------------------|:----------------------------------------------------------------------|:--------------------------------------------------------------|
| execution_horizon | 4h/8h/24h holding and lower-turnover replay diagnostics               | same-bar promotion or one-hour high-turnover search expansion |
| signal_source     | reuse locked seed packet and replay-clean diagnostic clues as anchors | open grammar FormulaGen or large search                       |
| cost_model        | cost tier must be tied to turnover bucket and horizon                 | choosing lowest cost tier as proof                            |
| lane_repair       | S0/S1/S2/S3 lane-specific lower-turnover diagnostics                  | single-lane promotion                                         |

## Execution Plan

| stage        | action                                 | input                                                 | authorized   |
|:-------------|:---------------------------------------|:------------------------------------------------------|:-------------|
| A7FF-CORE23E | executable-horizon diagnostic audit    | CORE17E locked packet + CORE19E rows where applicable | True         |
| A7FF-CORE24  | lower-turnover bounded replay contract | CORE23E pass only                                     | False        |

## Blocked

| blocked_task                        | reason                                                                 |
|:------------------------------------|:-----------------------------------------------------------------------|
| large search                        | blocked: one-bar executable supply insufficient and same-bar dominates |
| formula generation/search           | blocked: CORE23 authorizes horizon redesign diagnostics only           |
| alpha proof / shadow / paper / live | not authorized                                                         |
