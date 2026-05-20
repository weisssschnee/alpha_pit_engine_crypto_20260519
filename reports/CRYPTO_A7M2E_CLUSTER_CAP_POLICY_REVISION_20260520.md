# Crypto A7M-2E Cluster-Cap Policy Revision

- generated_at: `2026-05-20T10:42:49Z`
- decision: `HOLD_A7M2E_CLUSTER_CAP_REVEALS_WEAK_POOL`
- executes_search: `False`
- executes_replay: `False`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- a7m2_decision: `HOLD_A7M2_ENGINE_BAKEOFF_BLOCKED`
- fast_replay_parity_pass: `True`
- fast_replay_parity_max_abs_diff: `0.0`
- blockers: `['post_cap_near_miss_clusters_gte_6', 'post_cap_field_families_gte_4', 'post_cap_engines_gte_4']`

## Fast Replay Parity

- parity_sample_count: `227`
- compared_metric_rows: `19749`
- failed_metric_rows: `0`

All compared metrics passed tolerance `1e-8`.

## Label Refactor

| label                |   count |
|:---------------------|--------:|
| may_vetoed_cluster   |     245 |
| may_vetoed_near_miss |     134 |
| negative_control     |     128 |
| rejected             |       5 |

## Counterfactual Pools

| pool                      |   count |   return_corr_cluster_count |   top_return_corr_cluster_share |   field_family_count |   top_field_family_share |   operator_horizon_count |   top_operator_horizon_share |   engine_count |   formula_family_count |   placebo_or_null_count |
|:--------------------------|--------:|----------------------------:|--------------------------------:|---------------------:|-------------------------:|-------------------------:|-----------------------------:|---------------:|-----------------------:|------------------------:|
| pre_may_near_miss_no_cap  |     379 |                          11 |                        0.646438 |                    3 |                 0.899736 |                        5 |                     0.588391 |              6 |                      6 |                       0 |
| post_may_eligible_no_cap  |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |
| post_may_cluster_cap_0.35 |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |
| post_may_cluster_cap_0.25 |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |
| post_may_cluster_cap_0.20 |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |
| post_may_cluster_cap_0.15 |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |
| post_may_full_caps        |       0 |                           0 |                        0        |                    0 |                 0        |                        0 |                     0        |              0 |                      0 |                       0 |

## Engine Advantage After Full Caps

No post-cap near-miss pool remains.

## Policy Decision

- A7M-2F is authorized only if all gates pass.
- A7M-3 remains unauthorized.
- May remains stress-only; it is not part of ranking, reward, generation, arm allocation, or mutation prior.
