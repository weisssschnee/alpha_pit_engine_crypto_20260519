# CRYPTO NEXTGEN SEARCH EPOCH-0 Comparative Decision Report

Execution: `FROZEN_DEVELOPMENT_EPOCH_COMPLETED`
Recommendation: `REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH`

The fixed run completed normally. The 1,801/2,048 full strict evaluations are natural underfill after full-coordinate identity deduplication and the frozen BBO family cap; no identity was repeated and no budget, seed, grammar, reward, or admission rule was changed.

## Fixed-budget execution

- Proposals: 32,768/32,768.
- Stratified strict: 825/1,024 (80.57%).
- Global top-K strict: 976/1,024 (95.31%).
- Total strict: 1801/2,048 (87.94%).
- Hard-gate passes: 1282; development survivors: 0.
- Positive IC LCB / net LCB / benchmark-increment LCB: 116 / 3 / 29.

## Admission comparison

- Main stratified: 652 clusters from 793 strict evaluations (82.22 per 100).
- Main global top-K: 658 clusters from 848 strict evaluations (77.59 per 100).
- Stratified admission improved behaviour-cluster yield per strict evaluation, but neither arm produced a development survivor.
- Scoped BBO stratified admission executed only 32/128 because the frozen family budget cap was 32 while BBO had one legal mechanism family. This is an admission-feasibility defect, not a data-source failure.

## Search algorithms

| panel_id   | lane_id             |   proposals |   legal_rate |   exact_identities |   behaviour_clusters |   n_eff |   top_1_cluster_share |   economic_hypotheses |   strict_evaluations |   development_survivors |   new_behaviour_clusters_per_100_strict |   runtime_seconds |   failure_rate |
|:-----------|:--------------------|------------:|-------------:|-------------------:|---------------------:|--------:|----------------------:|----------------------:|---------------------:|------------------------:|----------------------------------------:|------------------:|---------------:|
| bbo_micro  | bbo_typed_temporal  |        2048 |     0.978027 |               1968 |                   32 | 32      |             0.03125   |                     3 |                   32 |                       0 |                                100      |          40.3442  |      0.0219727 |
| main       | cem                 |        3840 |     0.913281 |               3219 |                   98 | 90.1333 |             0.0288462 |                    28 |                  104 |                       0 |                                 94.2308 |         100.182   |      0.0867187 |
| main       | evolutionary        |        3840 |     0.8875   |               1817 |                  101 | 95.8696 |             0.0285714 |                    25 |                  105 |                       0 |                                 96.1905 |         239.34    |      0.1125    |
| main       | llm_proposal_repair |        3840 |     0.735938 |               2770 |                   85 | 79.3486 |             0.0215054 |                    29 |                   93 |                       0 |                                 91.3978 |          47.2891  |      0.264062  |
| main       | orthogonal_exile    |        3840 |     0.646354 |               2394 |                   75 | 59.6452 |             0.0581395 |                    18 |                   86 |                       0 |                                 87.2093 |         349.924   |      0.353646  |
| main       | surrogate           |        3840 |     0.715104 |               2702 |                   89 | 81.3063 |             0.0315789 |                    29 |                   95 |                       0 |                                 93.6842 |         338.171   |      0.284896  |
| main       | typed_ast           |        3840 |     0.73125  |               2766 |                   95 | 88.7043 |             0.029703  |                    27 |                  101 |                       0 |                                 94.0594 |           1.90047 |      0.26875   |
| main       | typed_random_fresh  |        3840 |     0.73125  |               2766 |                   91 | 84.7658 |             0.0309278 |                    25 |                   97 |                       0 |                                 93.8144 |         121.784   |      0.26875   |
| main       | uct_mcts            |        3840 |     0.982552 |               3411 |                  104 | 89.6    |             0.0446429 |                    20 |                  112 |                       0 |                                 92.8571 |         204.331   |      0.0174479 |

- Evolutionary search had the highest main adaptive cluster yield per 100 strict evaluations; it did not improve survivor production.
- UCT/MCTS reached the highest legal rate but its top proxy decile concentrated 66.58% in one mechanism and 63.93% in one primitive, triggering the reward-basin audit.
- CEM and surrogate did not materially exceed typed AST/random discovery efficiency, and every lane had zero survivors.

## Hypothesis and benchmark diagnosis

- Funding capacity expanded from the B1S reference of 27 exact identities to 120 exact identities in each typed AST/random funding slice. Funding grammar capacity is no longer the primary blocker.
- The best simple main benchmark by net LCB was `volatility` at -0.00012702; it was still negative after costs.
- Only three strict rows had positive net LCB, and no row passed the complete survivor contract. Pareto membership therefore records development trade-offs, not investable evidence.

## Required revision before another development epoch

- Make admission quotas feasible per panel and mechanism count; the BBO family cap must not mechanically force 32/128.
- Move full-identity dedup before final strict quota assignment so sketch collisions do not consume strict slots.
- Recalibrate the lane scalar toward lower-confidence net/cost/stability measures; proxy-driven adaptation currently discovers diverse signals without survivor efficiency.
- Add explicit typed/random matched controls for every adaptive lane and treat zero survivor improvement as an adaptive failure.
- Preserve the expanded mechanism registry; the next revision target is search/admission/reward, not another blind hypothesis-space expansion.

## Boundaries

- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`
- No new evaluation block was read. No rerun was performed or authorized.
