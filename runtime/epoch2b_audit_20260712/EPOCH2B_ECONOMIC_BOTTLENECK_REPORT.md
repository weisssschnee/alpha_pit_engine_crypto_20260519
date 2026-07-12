# CRYPTO EPOCH-2B — Economic Bottleneck and Operator Causal Audit

Status: `ECONOMIC_BOTTLENECK_AUDIT_COMPLETED`
Main recommendation: `PIVOT_TO_NEW_MECHANISM_OR_DATA`

## Main Gross-to-Net Funnel

| epoch   |   all_strict |   positive_gross |   positive_gross_lcb_proxy |   positive_net |   positive_net_lcb |   stable_worst_block |   benchmark_incremental |   survivor |
|:--------|-------------:|-----------------:|---------------------------:|---------------:|-------------------:|---------------------:|------------------------:|-----------:|
| EPOCH0  |         1596 |              897 |                         47 |              3 |                  1 |                    1 |                       1 |          0 |
| EPOCH1R |         1362 |              777 |                         42 |             12 |                  1 |                    1 |                       1 |          0 |
| EPOCH2  |         1448 |              768 |                         41 |             19 |                  0 |                    0 |                       0 |          0 |

- Main median epoch positive gross-LCB proxy fraction: 2.9449%.
- Cost-killed share among the rare positive gross-LCB proxy rows: 98.4615%.
- Main NET_LCB near-misses grew from 55 to 174, while median absolute distance changed from 4.6014363e-05 to 5.2107276e-05 (+13.24%).
- The gross-LCB value is a summary proxy (`net_lcb + mean_cost_drag`), not an exact recomputation.

## Operator Causal Result

- Operators marked no causal control: 24 / 24 adaptive operator-blocker cells.
- Adaptive child target-gate crossing rate: 0.00%; non-target collateral-damage rate: 90.36%.
- Parents classified NO_ECONOMIC_EDGE or UNSTABLE_NEIGHBOURHOOD: 89.29%.
- Mutation labels and LLM explanations were not treated as causal evidence.

## Hybrid Report-only Replay

| panel_id   |   strict_rows |   quality_rows |   diversity_rows |   quality_share |   diversity_share |   exact_identities |   behaviour_clusters |   n_eff |   top_cluster_share |   near_misses |   positive_net_lcb |   survivors |   global_exact_overlap |   stratified_exact_overlap | historical_epoch_rewritten   |   new_performance_queries |
|:-----------|--------------:|---------------:|-----------------:|----------------:|------------------:|-------------------:|---------------------:|--------:|--------------------:|--------------:|-------------------:|------------:|-----------------------:|---------------------------:|:-----------------------------|--------------------------:|
| bbo_micro  |            24 |             14 |               10 |        0.583333 |          0.416667 |                 24 |                   24 |  24     |           0.0416667 |             4 |                  4 |           0 |                     18 |                         12 | False                        |                         0 |
| main       |           744 |            446 |              298 |        0.599462 |          0.400538 |                744 |                  560 | 139.641 |           0.0483871 |           118 |                  0 |           0 |                    515 |                        261 | False                        |                         0 |

This replay used only cached exact identities and strict metrics. It does not rewrite Epoch-2 and is not new performance evidence.

## BBO Scoped Audit

- Positive-net exact identities: 5; behaviour clusters: 5; coverage: 82.22%.
- All five are spread-led, 48/168-window, negative-direction programs; month/symbol/session dependence cannot be identified from aggregated strict summaries.
- Full-2024 physically isolated bookTicker acquisition is a secondary data line; no BBO winner may be selected first.

## Boundary

- `NEW_PERFORMANCE_SEARCH_FROZEN`
- `ANALYSIS_AND_ENGINEERING_ALLOWED`
- `FORWARD_SEALED`
- `NO_CANDIDATE_PROMOTION`
- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`
