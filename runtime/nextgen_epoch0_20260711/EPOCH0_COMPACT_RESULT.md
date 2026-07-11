# CRYPTO NEXTGEN SEARCH EPOCH-0

Status: `FROZEN_DEVELOPMENT_EPOCH_COMPLETED`
Recommendation: `PREPARE_ROTATING_CHALLENGE_EPOCH`

Frozen design hash: `CD839D4F095E330DE17EB50E69FC55F8AFDEEA16CADB0C62FF3CE3DE9E6E7E62`
Runtime seconds: `2120.44`

## Arm comparison

| panel_id   | arm                  |   strict_evaluations |   exact_identities |   activation_identities |   behaviour_clusters |   economic_hypotheses |   n_eff |   top_1_cluster_share |   top_3_cluster_share |   development_survivors |   pareto_candidates |   new_behaviour_clusters_per_100_strict | direct_cross_panel_ranking   |
|:-----------|:---------------------|---------------------:|-------------------:|------------------------:|---------------------:|----------------------:|--------:|----------------------:|----------------------:|------------------------:|--------------------:|----------------------------------------:|:-----------------------------|
| bbo_micro  | GLOBAL_TOP_K_CONTROL |                  128 |                128 |                     128 |                  126 |                     3 | 124.121 |             0.015625  |             0.0390625 |                       0 |                  31 |                                 98.4375 | False                        |
| bbo_micro  | STRATIFIED_ADMISSION |                   32 |                 32 |                      32 |                   32 |                     3 |  32     |             0.03125   |             0.09375   |                       0 |                  10 |                                100      | False                        |
| main       | GLOBAL_TOP_K_CONTROL |                  848 |                848 |                     648 |                  658 |                    30 | 350.782 |             0.0153302 |             0.0412736 |                       0 |                 210 |                                 77.5943 | False                        |
| main       | STRATIFIED_ADMISSION |                  793 |                793 |                     666 |                  652 |                    30 | 297.61  |             0.0226986 |             0.0617907 |                       0 |                 181 |                                 82.2194 | False                        |

## Lane efficiency

| panel_id   | lane_id             |   proposals |   legal_rate |   canonical_identities |   exact_identities |   activation_identities |   behaviour_clusters |   economic_hypotheses |   n_eff |   top_1_cluster_share |   top_3_cluster_share |   strict_evaluations |   development_survivors |   new_behaviour_clusters_per_100_strict |   runtime_seconds |   failure_rate |
|:-----------|:--------------------|------------:|-------------:|-----------------------:|-------------------:|------------------------:|---------------------:|----------------------:|--------:|----------------------:|----------------------:|---------------------:|------------------------:|----------------------------------------:|------------------:|---------------:|
| bbo_micro  | bbo_typed_temporal  |        2048 |     0.978027 |                   2048 |               1968 |                      32 |                   32 |                     3 | 32      |             0.03125   |             0.09375   |                   32 |                       0 |                                100      |          40.3442  |      0.0219727 |
| main       | cem                 |        3840 |     0.913281 |                   3839 |               3219 |                      98 |                   98 |                    28 | 90.1333 |             0.0288462 |             0.0769231 |                  104 |                       0 |                                 94.2308 |         100.182   |      0.0867187 |
| main       | evolutionary        |        3840 |     0.8875   |                   2912 |               1817 |                      98 |                  101 |                    25 | 95.8696 |             0.0285714 |             0.0666667 |                  105 |                       0 |                                 96.1905 |         239.34    |      0.1125    |
| main       | llm_proposal_repair |        3840 |     0.735938 |                   3840 |               2770 |                      86 |                   85 |                    29 | 79.3486 |             0.0215054 |             0.0645161 |                   93 |                       0 |                                 91.3978 |          47.2891  |      0.264062  |
| main       | orthogonal_exile    |        3840 |     0.646354 |                   3836 |               2394 |                      83 |                   75 |                    18 | 59.6452 |             0.0581395 |             0.127907  |                   86 |                       0 |                                 87.2093 |         349.924   |      0.353646  |
| main       | surrogate           |        3840 |     0.715104 |                   3839 |               2702 |                      93 |                   89 |                    29 | 81.3063 |             0.0315789 |             0.0842105 |                   95 |                       0 |                                 93.6842 |         338.171   |      0.284896  |
| main       | typed_ast           |        3840 |     0.73125  |                   3840 |               2766 |                      97 |                   95 |                    27 | 88.7043 |             0.029703  |             0.0693069 |                  101 |                       0 |                                 94.0594 |           1.90047 |      0.26875   |
| main       | typed_random_fresh  |        3840 |     0.73125  |                   3840 |               2766 |                      93 |                   91 |                    25 | 84.7658 |             0.0309278 |             0.0721649 |                   97 |                       0 |                                 93.8144 |         121.784   |      0.26875   |
| main       | uct_mcts            |        3840 |     0.982552 |                   3815 |               3411 |                     103 |                  104 |                    20 | 89.6    |             0.0446429 |             0.0803571 |                  112 |                       0 |                                 92.8571 |         204.331   |      0.0174479 |

## Boundaries

- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`
- Main and scoped BBO micro panels were not directly ranked.
- No validation, test, recent, May stress, or forward block was read.
- Frozen candidate pack is development-only evidence, not alpha-ready or OOS-proven.
