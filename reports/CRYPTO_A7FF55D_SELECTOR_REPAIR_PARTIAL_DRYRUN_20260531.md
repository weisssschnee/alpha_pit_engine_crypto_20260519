# CRYPTO A7FF-55D SELECTOR REPAIR PARTIAL DRYRUN

Generated: 2026-05-31T09:35:05Z

## Decision

`HOLD_A7FF55D_PARTIAL_SELECTOR_DRYRUN_REQUIRES_FULL_INPUT_REBUILD`

A7FF-55D tests the repaired selector target on currently available primary-label response rows. It is partial by design because full S01-S06 primary-label compact inputs were not retained. It does not authorize replay or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_full_input_rebuild": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "available_response_sources": 2,
  "blockers": [
    "top_family_share_above_0p30",
    "top_motif_share_above_0p30",
    "partial_scope_not_replay_authorizing"
  ],
  "decision": "HOLD_A7FF55D_PARTIAL_SELECTOR_DRYRUN_REQUIRES_FULL_INPUT_REBUILD",
  "executes_replay": false,
  "executes_search": false,
  "executes_selector_dryrun": true,
  "generated_at": "2026-05-31T09:35:05Z",
  "primary_label_candidate_rows": 39,
  "response_rows": 4800,
  "selected_family_count": 2,
  "selected_label_counts": {
    "L0_raw_forward_return": 4,
    "L1_cross_sectional_relative_return": 4,
    "L3_liquidity_tier_relative_return": 4
  },
  "selected_motif_count": 4,
  "selected_rows": 12,
  "stage": "A7FF-55D",
  "top_family_share": 0.9166666666666666,
  "top_motif_share": 0.5,
  "uses_may": false
}
```

## Source Audit

| source_shard   | path                                                                                  |   rows | available   |
|:---------------|:--------------------------------------------------------------------------------------|-------:|:------------|
| S00            | runtime\a7ff53e_numeric_response_execution_s00\a7ff53e_s00_label_response_metrics.csv |   3000 | True        |
| S01P           | runtime\a7ff55d_selector_repair_inputs_s01p\a7ff55d_s01p_label_response_metrics.csv   |   1800 | True        |

## Selected Label Summary

| label_family                       |   selected_count |
|:-----------------------------------|-----------------:|
| L0_raw_forward_return              |                4 |
| L1_cross_sectional_relative_return |                4 |
| L3_liquidity_tier_relative_return  |                4 |

## Selected Family Summary

| semantic_pair                        |   selected_count |
|:-------------------------------------|-----------------:|
| basis_premium_like|price_return_like |               11 |
| liquidity_like|price_return_like     |                1 |

## Selected Motif Summary

| motif         |   selected_count |
|:--------------|-----------------:|
| safe_div_abs  |                3 |
| signed_spread |                1 |
| spread_rank   |                6 |
| sub           |                2 |

## Boundary

```text
selector dryrun executed: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
