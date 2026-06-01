# CRYPTO A7FF-CORE15YR SURFACE FAILURE REPAIR

Generated: 2026-06-01T08:05:34Z

## Decision

`PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS`

A7FF-CORE15YR stops replay/packet retries and defines the next atlas rebuild stage. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T08:05:34Z",
  "next_allowed": "A7FF-CORE16 primitive-response replay-stability atlas rebuild",
  "source_decision": "HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT",
  "source_stage": "A7FF-CORE15Y",
  "stage": "A7FF-CORE15YR"
}
```

## Weak Points

| weak_point                     | evidence                                                           | repair                                                                                                         |
|:-------------------------------|:-------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------|
| W0_low_surface_candidate_count | surface_candidate_count=4                                          | do not replay current queue; rebuild candidate objectives from primitive response and non-replay split proxies |
| W1_family_concentration        | top_family_share=0.75                                              | require objective-surface candidate quota by semantic family before any materialization queue                  |
| W2_control_ratio_surface       | family scorecard median control ratios mostly above 1              | make control margin a generation-side objective, not post-replay filter only                                   |
| W3_replay_before_surface       | two bounded replay packets consumed but surface remains too narrow | next stage must be surface reconstruction, not another bounded replay packet                                   |

## Next Contract

```json
{
  "action": "primitive-response replay-stability atlas rebuild",
  "forbidden": [
    "CORE14/CORE14SE packet rerun",
    "new formula search",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "pass_gate": {
    "control_margin_policy": "median_control_ratio < 1.0 by selected family",
    "motif_bucket_count": 5,
    "objective_surface_candidate_count": 64,
    "semantic_bucket_count": 6,
    "top_family_share_max": 0.3
  },
  "required_inputs": [
    "A7AA primitive response maps",
    "A7FF CORE13E numeric clue rows",
    "A7FF CORE14E/14SEE replay rows",
    "field ontology and role enforcement ledgers"
  ],
  "required_outputs": [
    "field_type_by_label_horizon_stability.csv",
    "operator_by_field_type_stability.csv",
    "semantic_family_replay_stability_quota.csv",
    "core16_candidate_objective_atlas.csv",
    "core16_manifest.json"
  ],
  "scope": "no new formula grammar expansion; build candidate objectives from primitive/derived fields with replay-stability quotas",
  "stage": "A7FF-CORE16"
}
```

## Blocked Actions

| item                                | reason                                                          |
|:------------------------------------|:----------------------------------------------------------------|
| CORE15Z seed policy                 | blocked: CORE15Y surface candidate breadth failed               |
| bounded replay rerun                | blocked: replay has already shown objective-surface instability |
| formula search                      | blocked: search would amplify an unstable objective surface     |
| large search                        | blocked until CORE16 atlas passes breadth/control gates         |
| alpha proof / shadow / paper / live | not authorized                                                  |
