# CRYPTO A7MEM-0 Search Memory Registry 20260628

## Decision

`PASS_A7MEM0_SEARCH_MEMORY_REGISTRY_BUILT`

Boundary: search memory and next-search prior only. This does not authorize alpha proof, shadow, paper, or live.

## Why This Exists

Crypto search memory existed as a low-level expression/skeleton smoke, but large-search stages used ad-hoc priors and local skeleton caps instead of a single mandatory memory registry.
A7MEM-0 makes the search memory explicit and machine-readable before the next large search.

## Counts

- source_files_seen: `5`
- source_files_missing: `0`
- source_record_rows: `355`
- candidate_memory_rows: `313`
- strict_rows: `42`
- accepted_prior_rows: `47`
- rejected_rows: `224`
- formula_clusters: `224`
- pair_motif_priors: `86`

## Mandatory Next-Search Gate

Next large search must load `runtime/a7mem0_search_memory_registry_20260628/a7mem0_next_search_prior.json`.
If the prior file is absent or stale relative to the latest aggregate, the search is not authorized.

## Top Pair/Motif Priors

| semantic_pair | motif | strict_count | rejected_count | prior_action | search_weight |
| --- | --- | --- | --- | --- | --- |
| open_interest\|taker_flow | additive_composite | 5 | 10 | promote_with_cluster_cap | 2.5 |
| liquidity\|open_interest | spread | 4 | 6 | promote_with_cluster_cap | 2.5 |
| liquidity\|open_interest | additive_composite | 3 | 9 | promote_with_cluster_cap | 2.5 |
| basis\|open_interest | additive_composite | 2 | 5 | promote_with_cluster_cap | 2.5 |
| basis\|open_interest | spread | 2 | 6 | promote_with_cluster_cap | 2.5 |
| liquidity\|positioning | additive_composite | 2 | 7 | promote_with_cluster_cap | 2.5 |
| open_interest\|positioning | safe_div_abs_gated | 2 | 9 | promote_with_cluster_cap | 2.5 |
| open_interest\|premium | additive_composite_gated | 2 | 3 | promote_with_cluster_cap | 2.5 |
| open_interest\|taker_flow | spread_gated | 2 | 0 | promote_with_cluster_cap | 2.5 |
| basis\|open_interest | additive_composite_gated | 1 | 1 | exploit_lightly_with_diversity_cap | 1.5 |
| basis\|positioning | safe_div_abs_gated | 1 | 1 | exploit_lightly_with_diversity_cap | 1.5 |
| funding_dense\|positioning | safe_div_abs_gated | 1 | 0 | exploit_lightly_with_diversity_cap | 1.5 |
| liquidity\|positioning | safe_div_abs | 1 | 2 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|open_interest | safe_div_abs_gated | 1 | 2 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|positioning | smooth_mul_gated | 1 | 4 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|premium | additive_composite | 1 | 5 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|premium | smooth_mul | 1 | 5 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|premium | spread | 1 | 6 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|premium | spread_gated | 1 | 2 | exploit_lightly_with_diversity_cap | 1.5 |
| open_interest\|taker_flow | safe_div_abs | 1 | 6 | exploit_lightly_with_diversity_cap | 1.5 |

## Top Formula Clusters

| semantic_pair | motif | record_count | strict_count | duplicate_pressure | next_action |
| --- | --- | --- | --- | --- | --- |
| open_interest\|taker_flow | additive_composite | 5 | 3 | 4 | keep_but_cluster_cap |
| open_interest\|positioning | safe_div_abs_gated | 4 | 2 | 3 | keep_but_cluster_cap |
| liquidity\|open_interest | spread | 2 | 2 | 1 | keep_but_cluster_cap |
| open_interest\|premium | smooth_mul | 5 | 1 | 4 | keep_but_cluster_cap |
| liquidity\|open_interest | spread | 4 | 1 | 3 | keep_but_cluster_cap |
| basis\|open_interest | spread | 3 | 1 | 2 | keep_but_cluster_cap |
| liquidity\|positioning | additive_composite | 3 | 1 | 2 | keep_but_cluster_cap |
| open_interest\|taker_flow | additive_composite | 3 | 1 | 2 | keep_but_cluster_cap |
| basis\|positioning | safe_div_abs_gated | 2 | 1 | 1 | keep_but_cluster_cap |
| liquidity\|open_interest | additive_composite | 2 | 1 | 1 | keep_but_cluster_cap |
| liquidity\|open_interest | spread | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|positioning | smooth_mul_gated | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|premium | additive_composite_gated | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|premium | spread | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|premium | spread_gated | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|taker_flow | safe_div_abs | 2 | 1 | 1 | keep_but_cluster_cap |
| open_interest\|taker_flow | spread | 2 | 1 | 1 | keep_but_cluster_cap |
| positioning\|premium | smooth_mul | 2 | 1 | 1 | keep_but_cluster_cap |
| positioning\|taker_flow | smooth_mul | 2 | 1 | 1 | keep_but_cluster_cap |
| basis\|open_interest | additive_composite | 1 | 1 | 0 | keep_but_cluster_cap |

## Outputs

- `a7mem0_search_run_registry.csv`
- `a7mem0_candidate_memory.csv`
- `a7mem0_formula_cluster_memory.csv`
- `a7mem0_rejection_memory.csv`
- `a7mem0_pair_motif_prior.csv`
- `a7mem0_archive_pointer_map.csv`
- `a7mem0_next_search_prior.json`
- `a7mem0_manifest.json`
