# B1S CANARY Deep Attribution

Execution status: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL` / `B1S_CANARY_EXECUTION_ACCEPTED` / `FIXED_BUDGET_CONTRACT_PRESERVED`.

This was not an interruption or failure. Funding-event produced 27 legal exact identities under the frozen budget; the system correctly did not duplicate identities, relax admission, change seeds, add proposals, or extend budget.

## Per-lane evidence

| panel_id   | lane_id                  |   proposals |   legal_rate |   canonical_identities |   exact_identities |   canonical_to_exact_rate |   activation_identities |   behaviour_clusters |    n_eff |   top_cluster_share |   economic_hypothesis_coverage |   strict_survivors |   strict_survivor_efficiency |   new_behaviour_clusters_per_strict_evaluation |
|:-----------|:-------------------------|------------:|-------------:|-----------------------:|-------------------:|--------------------------:|------------------------:|---------------------:|---------:|--------------------:|-------------------------------:|-------------------:|-----------------------------:|-----------------------------------------------:|
| bbo_micro  | bbo_temporal_event_micro |         512 |     0.957031 |                    256 |                 95 |                  0.371094 |                      32 |                   30 | 26.9474  |            0.09375  |                              4 |                  0 |                            0 |                                        0.9375  |
| main       | adaptive_challenger      |         512 |     0.962891 |                    306 |                184 |                  0.601307 |                      18 |                   22 | 16.5161  |            0.125    |                              3 |                  0 |                            0 |                                        0.6875  |
| main       | basis_oi_state           |         512 |     0.949219 |                    256 |                120 |                  0.46875  |                      25 |                   23 | 17.6552  |            0.125    |                              3 |                  0 |                            0 |                                        0.71875 |
| main       | competitor_reproduction  |         512 |     0.746094 |                    256 |                109 |                  0.425781 |                      25 |                   15 |  8.39344 |            0.21875  |                              4 |                  0 |                            0 |                                        0.46875 |
| main       | cross_asset_state        |         512 |     0.78125  |                    256 |                 47 |                  0.183594 |                      27 |                   28 | 24.381   |            0.09375  |                              3 |                  0 |                            0 |                                        0.875   |
| main       | funding_event            |         512 |     0.355469 |                    240 |                 27 |                  0.1125   |                      27 |                   27 | 27       |            0.037037 |                              2 |                  0 |                            0 |                                        1       |
| main       | orthogonal_exile         |         512 |     0.945312 |                    256 |                 93 |                  0.363281 |                      23 |                   20 | 11.1304  |            0.21875  |                              3 |                  0 |                            0 |                                        0.625   |
| main       | static_cross_sectional   |         512 |     0.984375 |                    256 |                151 |                  0.589844 |                      16 |                   30 | 28.4444  |            0.0625   |                              4 |                  0 |                            0 |                                        0.9375  |
| main       | temporal_program         |         512 |     0.796875 |                    256 |                 79 |                  0.308594 |                      29 |                   20 | 11.907   |            0.15625  |                              3 |                  0 |                            0 |                                        0.625   |
| main       | volatility_session       |         512 |     0.597656 |                    256 |                 57 |                  0.222656 |                      20 |                   17 |  8.12698 |            0.25     |                              3 |                  0 |                            0 |                                        0.53125 |

## Diagnosis

- Funding identity capacity saturated after the first 128 proposals; both seeds produced the same 27-identity set.
- `event_window` and `transition` produced zero legal exact identities; `event_age` collapsed 108 proposals to one identity.
- The adaptive post-pilot segment concentrated all 448 proposals on `blend`; proxy median improved, but no development survivor emerged and operator diversity collapsed.
- Global top-K found more main-panel behaviour clusters and all five survivors; stratified admission increased activation diversity but not behaviour-cluster count under the B1S quota design.
- Historical four-cluster IDs and B1S cluster IDs are not directly comparable, so no claim about returning to the historical four is valid from raw ID overlap.

## Executable changes

- replace single-operator adaptive collapse with separate CEM, multi-step UCT/MCTS, evolutionary and surrogate lanes
- expand funding into level/change/surprise/event-age/state-transition programs and remove 128-proposal alias cycle
- use semantic-volume round-robin and exact-identity voting before performance selection
- replace single development score with hard gates, full multi-objective vectors and Pareto archive
- run simple benchmarks under the same development/cost contract and report incremental contribution
- emit compatible within-Epoch behaviour clusters and static historical-reference comparability diagnostics

No new evaluation block was read and no CANARY rerun is required.
