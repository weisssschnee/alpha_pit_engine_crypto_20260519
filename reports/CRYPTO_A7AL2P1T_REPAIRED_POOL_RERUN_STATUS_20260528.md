# CRYPTO A7AL-2P1T Repaired Pool Rerun Status

Generated: 2026-05-28T07:28:44Z

## Decision

```text
PASS_A7AL2P1T_REPAIRED_POOL_READY_FOR_PROVENANCE_AUDIT
```

This status record freezes the repaired current A7AL-2K/L/P1/P1R rerun. It supersedes the stale two-candidate P1/P1R selector pool for downstream authorization.

## Manifest

```json
{
  "a7al2k_generated_at": "2026-05-28T01:45:32Z",
  "a7al2k_generated_candidates": 8000,
  "a7al2k_selected_for_replay": 768,
  "a7al2l_clue_count": 2,
  "a7al2l_generated_at": "2026-05-28T07:12:23Z",
  "a7al2l_replay_cap": 2,
  "a7al2p1_candidate_count": 2,
  "a7al2p1_decision_counts": {
    "A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE": 2
  },
  "a7al2p1_generated_at": "2026-05-28T07:19:02Z",
  "a7al2p1_selector_eligible_count": 2,
  "a7al2p1r_decision": "PASS_A7AL2P1R_SELECTOR_REWEIGHTED_POOL_READY_FOR_P0R_RETRY",
  "a7al2p1r_diagnostic_pass_count": 2,
  "a7al2p1r_generated_at": "2026-05-28T07:23:21Z",
  "authorizes_a7al2p2": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AL2P1T_REPAIRED_POOL_READY_FOR_PROVENANCE_AUDIT",
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T07:28:44Z",
  "required_next": "run or rely on A7AL-2P1S provenance audit before drafting A7AL-2P2"
}
```

## Stage Summary

| stage                                                 | decision                                                        | generated_at         |   generated_candidates |   selected_or_replayed_candidates |   candidate_count |   clue_count |   selector_eligible_count |   diagnostic_pass_count | blockers   | warnings   | authorizes_formula_search_execution   | authorizes_alpha_proof   |
|:------------------------------------------------------|:----------------------------------------------------------------|:---------------------|-----------------------:|----------------------------------:|------------------:|-------------:|--------------------------:|------------------------:|:-----------|:-----------|:--------------------------------------|:-------------------------|
| A7AL-2K repaired current generated pool               | PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L            | 2026-05-28T01:45:32Z |                   8000 |                               768 |                   |              |                           |                         |            |            | False                                 | False                    |
| A7AL-2L repaired current 64-cap replay preflight      | PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD | 2026-05-28T07:12:23Z |                        |                                 2 |                   |            2 |                           |                         |            |            | False                                 | False                    |
| A7AL-2P1 selector feature generation on repaired pool | PASS_A7AL2P1_SELECTOR_FEATURES_READY_FOR_P0R_RETRY              | 2026-05-28T07:19:02Z |                        |                                   |                 2 |              |                         2 |                         |            |            | False                                 | False                    |
| A7AL-2P1R selector-reweighted retry                   | PASS_A7AL2P1R_SELECTOR_REWEIGHTED_POOL_READY_FOR_P0R_RETRY      | 2026-05-28T07:23:21Z |                        |                                   |                 2 |              |                           |                       2 |            |            | False                                 | False                    |

## Repaired A7AL-2L Clue Pool

| candidate_id            | decision                             | cell                | family                 | field_families       | fields                                |   control_dominance_ratio_premay_max |   one_bar_lag_recent_spread |
|:------------------------|:-------------------------------------|:--------------------|:-----------------------|:---------------------|:--------------------------------------|-------------------------------------:|----------------------------:|
| a7al2k_046e806368e99c76 | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE | J0_oi_derived_state | derived_oi_price_state | open_interest\|price | index_close\|open_interest_value_last |                              0.79335 |                  0.0018384  |
| a7al2k_0a247ec03472983b | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE | J0_oi_derived_state | derived_oi_price_state | open_interest\|price | index_close\|open_interest_value_last |                              0.88085 |                  0.00186493 |

## P1 Selector Decisions

| candidate_id            | selector_decision                    | latent_gate   | matched_control_gate   |   control_ratio_premay_max_by_split |   latent_positive_premay_splits | field_families       | expression                                                                              |
|:------------------------|:-------------------------------------|:--------------|:-----------------------|------------------------------------:|--------------------------------:|:---------------------|:----------------------------------------------------------------------------------------|
| a7al2k_046e806368e99c76 | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE | PASS          | PASS                   |                             0.79335 |                               3 | open_interest\|price | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   |
| a7al2k_0a247ec03472983b | A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE | PASS          | PASS                   |                             0.88085 |                               3 | open_interest\|price | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) |

## Boundary

```text
Authorized:
  none

Not authorized:
  A7AL-2P2 local search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
