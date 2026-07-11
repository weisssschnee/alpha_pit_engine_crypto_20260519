# B1S CANARY Compact Result

Decision: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`

Execution acceptance: `B1S_CANARY_EXECUTION_ACCEPTED` / `FIXED_BUDGET_CONTRACT_PRESERVED`.

This was not an interruption or failure. Funding-event produced 27 legal exact identities under the frozen proposal budget and one-exact-identity-one-vote contract. The system correctly did not duplicate identities, relax admission, change seeds, add proposals, or extend budget to fill the five unavailable strict evaluations.

Frozen repo SHA: `39dbd40e6ce7bde3fbaba0067da6a5bfbae797f8`
Runtime seconds: `166.46`

Main and BBO micro results are separate comparison domains and were not directly ranked.

## Lane Summary

| panel_id   | lane_id                  |   proposals |   legal_candidates |   legal_candidate_rate |   canonical_identities |   exact_identities |   stratified_admissions |   stratified_strict_evaluations |   runtime_seconds |   failure_rate |
|:-----------|:-------------------------|------------:|-------------------:|-----------------------:|-----------------------:|-------------------:|------------------------:|--------------------------------:|------------------:|---------------:|
| bbo_micro  | bbo_temporal_event_micro |         512 |                490 |               0.957031 |                    256 |                 95 |                      64 |                              32 |           2.3088  |      0.0429688 |
| main       | adaptive_challenger      |         512 |                493 |               0.962891 |                    306 |                184 |                      49 |                              32 |          12.6795  |      0.0371094 |
| main       | basis_oi_state           |         512 |                486 |               0.949219 |                    256 |                120 |                      64 |                              32 |           9.10977 |      0.0507812 |
| main       | competitor_reproduction  |         512 |                382 |               0.746094 |                    256 |                109 |                      64 |                              32 |           8.95834 |      0.253906  |
| main       | cross_asset_state        |         512 |                400 |               0.78125  |                    256 |                 47 |                      47 |                              32 |           7.76044 |      0.21875   |
| main       | funding_event            |         512 |                182 |               0.355469 |                    240 |                 27 |                      27 |                              27 |          23.5356  |      0.644531  |
| main       | orthogonal_exile         |         512 |                484 |               0.945312 |                    256 |                 93 |                      64 |                              32 |          34.9975  |      0.0546875 |
| main       | static_cross_sectional   |         512 |                504 |               0.984375 |                    256 |                151 |                      64 |                              32 |           8.26213 |      0.015625  |
| main       | temporal_program         |         512 |                408 |               0.796875 |                    256 |                 79 |                      64 |                              32 |          11.1137  |      0.203125  |
| main       | volatility_session       |         512 |                306 |               0.597656 |                    256 |                 57 |                      57 |                              32 |           7.39534 |      0.402344  |

## Stratified vs Global Top-K

| panel_id   | arm                  |   strict_evaluations |   canonical_exact_identities |   activation_identities |   behaviour_clusters |   n_eff |   top_1_cluster_share |   top_3_cluster_share |   economic_hypothesis_coverage |   new_behaviour_clusters_per_strict_evaluation |   development_survivor_count |   development_score_median | direct_cross_panel_ranking_performed   |
|:-----------|:---------------------|---------------------:|-----------------------------:|------------------------:|---------------------:|--------:|----------------------:|----------------------:|-------------------------------:|-----------------------------------------------:|-----------------------------:|---------------------------:|:---------------------------------------|
| bbo_micro  | GLOBAL_TOP_K_CONTROL |                   32 |                           32 |                      32 |                   29 | 23.2727 |             0.125     |              0.1875   |                              4 |                                        0.90625 |                            1 |                   -7.69342 | False                                  |
| bbo_micro  | STRATIFIED_ADMISSION |                   32 |                           32 |                      32 |                   30 | 26.9474 |             0.09375   |              0.15625  |                              4 |                                        0.9375  |                            0 |                   -8.72533 | False                                  |
| main       | GLOBAL_TOP_K_CONTROL |                  288 |                          288 |                     109 |                  153 | 49.7863 |             0.0555556 |              0.166667 |                             27 |                                        0.53125 |                            5 |                  -10.1487  | False                                  |
| main       | STRATIFIED_ADMISSION |                  283 |                          210 |                     135 |                  140 | 30.9822 |             0.113074  |              0.254417 |                             27 |                                        0.4947  |                            0 |                  -14.5101  | False                                  |

## Frozen Boundaries

- `FORMAL_SEARCH_FROZEN`
- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- no A7MEM or cross-CANARY adaptive state persistence
- BBO means top-of-book only, not multi-level depth
