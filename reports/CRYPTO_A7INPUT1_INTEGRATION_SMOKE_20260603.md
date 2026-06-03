# CRYPTO A7INPUT-1 INTEGRATION SMOKE

Generated: 2026-06-03T02:31:16Z

## Decision

`PASS_A7INPUT1_INPUT_ROUTING_INTEGRATION_SMOKE`

A7INPUT-1 verifies that the independent input tag package can gate formula inputs by ordinary-alpha, interaction-alpha, and rescue-lane modes. It does not execute replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core54_queue_builder_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7INPUT1_INPUT_ROUTING_INTEGRATION_SMOKE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-03T02:31:16Z",
  "interaction_alpha_accept_count": 2858,
  "mode_count": 3,
  "ordinary_alpha_accept_count": 2858,
  "rescue_lane_accept_count": 0,
  "sample_formula_count": 5000,
  "source_decision": "PASS_A7INPUT0_INPUT_APPROVAL_PACKAGE_READY",
  "source_stage": "A7INPUT-0",
  "stage": "A7INPUT-1"
}
```

## Mode Acceptance

| mode              |   accepted |   total |   accept_rate |
|:------------------|-----------:|--------:|--------------:|
| interaction_alpha |       2858 |    5000 |        0.5716 |
| ordinary_alpha    |       2858 |    5000 |        0.5716 |
| rescue_lane       |          0 |    5000 |        0      |

## Mode Filter Summary

| mode              | decision   | reason                     |   row_count |   median_input_field_count |
|:------------------|:-----------|:---------------------------|------------:|---------------------------:|
| interaction_alpha | accept     | interaction_allowed        |           0 |                          2 |
| interaction_alpha | reject     | interaction_blocked_tag    |           0 |                          2 |
| ordinary_alpha    | accept     | ordinary_alpha_allowed     |           0 |                          2 |
| ordinary_alpha    | reject     | ordinary_alpha_blocked_tag |           0 |                          2 |
| rescue_lane       | reject     | rescue_lane_non_rescue_tag |           0 |                          2 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE54 input-tag-aware queue builder contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
