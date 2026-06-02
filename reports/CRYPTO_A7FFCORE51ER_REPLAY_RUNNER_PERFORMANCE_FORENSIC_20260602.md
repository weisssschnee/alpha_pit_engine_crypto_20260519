# CRYPTO A7FF-CORE51ER REPLAY RUNNER PERFORMANCE FORENSIC

Generated: 2026-06-02T01:55:14Z

## Decision

`HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER`

CORE51E candidate logic is not rejected. The current runner implementation is rejected because the 16-candidate smoke timed out after 1200 seconds. The blocker is repeated full-frame groupby/rank replay, not field/data/source readiness.

## Incident

| incident_id              | attempted_command                                                                                |   timeout_seconds |   candidate_count |   frame_rows |   frame_symbols | result                      |
|:-------------------------|:-------------------------------------------------------------------------------------------------|------------------:|------------------:|-------------:|----------------:|:----------------------------|
| I0_core51e_smoke_timeout | $env:A7FFCORE51E_MAX_CANDIDATES='16'; py scripts/crypto_a7ffcore51e_filtered_replay_execution.py |              1200 |                16 |      6949596 |             498 | timeout_no_replay_artifacts |

## Bottleneck Matrix

| bottleneck_id               | description                                                                                           | severity   | fix                                                                                     |
|:----------------------------|:------------------------------------------------------------------------------------------------------|:-----------|:----------------------------------------------------------------------------------------|
| B0_repeated_full_frame_rank | runner recomputes timestamp rank/top-bottom spread for every seed, control, label family, and horizon | critical   | precompute timestamp group codes and use vectorized top/bottom masks per signal         |
| B1_repeated_control_replay  | stale/sign/time/symbol controls trigger four additional full-frame spread passes per label            | critical   | compute original/control spreads in one vectorized block and cache label arrays         |
| B2_full_frame_reload        | runner rebuilds full 498-symbol frame and latent overlay inside execution                             | medium     | persist compact replay frame or memory-map only symbol/timestamp/labels/required fields |
| B3_no_shard_resume          | timeout leaves no shard-level partial metrics because replay writes only at the end                   | high       | write per-shard/per-candidate metrics incrementally with resume manifest                |

## Repair Plan

| stage          | action                                              | requirements                                                    | executes_replay   |
|:---------------|:----------------------------------------------------|:----------------------------------------------------------------|:------------------|
| A7FF-CORE51P   | optimized replay runner contract and implementation | sharded, resumable, vectorized label arrays, incremental writes | False             |
| A7FF-CORE51PE  | optimized 16-candidate smoke                        | complete within 180 seconds and produce metrics                 | True              |
| A7FF-CORE51E-R | rerun bounded filtered replay with optimized runner | 384 candidates max, shard outputs, no search/proof/promotion    | True              |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE51P optimized replay runner contract / implementation": true
  },
  "not_authorized": {
    "CORE51E_current_runner_rerun": true,
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core51p_runner_optimization": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER",
  "dominant_failure": "replay_runner_repeated_full_frame_groupby_rank_timeout",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T01:55:14Z",
  "next_allowed": "A7FF-CORE51P optimized replay runner contract / implementation",
  "source_decision": "PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E",
  "source_stage": "A7FF-CORE51",
  "stage": "A7FF-CORE51ER"
}
```
