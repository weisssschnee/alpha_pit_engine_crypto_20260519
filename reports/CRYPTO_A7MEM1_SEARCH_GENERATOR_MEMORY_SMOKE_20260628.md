# CRYPTO A7SEARCH1 CEM UCT Typed-AST Policy Bakeoff 20260618

## Decision

`PASS_A7SEARCH1_CEM_UCT_AST_QUEUE_READY_FOR_PROXY`

This stage tests search policy over a shared typed-AST formula space. AST is the expression/state representation; CEM and UCT are the search policies. The output authorizes proxy evaluation only.

## Counts

- queue_rows: `256`
- shard_count: `4`
- rows_per_shard: `64`
- max_parallel: `1`
- prior_rows: `6`
- semantic_pair_count: `36`
- motif_count: `8`
- skeleton_count: `183`
- memory_enforcement_enabled: `True`
- memory_trace_rows: `411`

## Policy Summary

| search_policy        |   rows |
|:---------------------|-------:|
| cem_ast_prior        |     87 |
| map_elites_diversity |     30 |
| raw_ast_explore      |     52 |
| uct_ast_tree         |     87 |

## Pair Summary

| search_policy        | semantic_pair                 |   rows |
|:---------------------|:------------------------------|-------:|
| uct_ast_tree         | premium|taker_flow            |      6 |
| uct_ast_tree         | regime|taker_flow             |      6 |
| uct_ast_tree         | age|positioning               |      6 |
| uct_ast_tree         | funding_sparse|funding_sparse |      5 |
| cem_ast_prior        | open_interest|regime          |      5 |
| uct_ast_tree         | liquidity|open_interest       |      5 |
| uct_ast_tree         | positioning|regime            |      5 |
| cem_ast_prior        | premium|premium               |      4 |
| cem_ast_prior        | taker_flow|taker_flow         |      4 |
| cem_ast_prior        | liquidity|positioning         |      4 |
| cem_ast_prior        | liquidity|liquidity           |      4 |
| uct_ast_tree         | taker_flow|taker_flow         |      4 |
| uct_ast_tree         | basis|basis                   |      4 |
| uct_ast_tree         | funding_basis|funding_basis   |      4 |
| raw_ast_explore      | liquidity|taker_flow          |      4 |
| cem_ast_prior        | funding_dense|funding_dense   |      4 |
| cem_ast_prior        | age|taker_flow                |      4 |
| cem_ast_prior        | basis|regime                  |      4 |
| cem_ast_prior        | funding_dense|positioning     |      3 |
| cem_ast_prior        | basis|liquidity               |      3 |
| cem_ast_prior        | basis|positioning             |      3 |
| raw_ast_explore      | funding_basis|funding_basis   |      3 |
| uct_ast_tree         | open_interest|regime          |      3 |
| uct_ast_tree         | funding_dense|liquidity       |      3 |
| raw_ast_explore      | taker_flow|taker_flow         |      3 |
| raw_ast_explore      | basis|basis                   |      3 |
| raw_ast_explore      | positioning|premium           |      3 |
| cem_ast_prior        | age|positioning               |      3 |
| cem_ast_prior        | basis|basis                   |      3 |
| cem_ast_prior        | positioning|premium           |      3 |
| cem_ast_prior        | basis|open_interest           |      3 |
| uct_ast_tree         | open_interest|taker_flow      |      3 |
| uct_ast_tree         | liquidity|taker_flow          |      3 |
| uct_ast_tree         | age|open_interest             |      3 |
| uct_ast_tree         | basis|funding_sparse          |      3 |
| uct_ast_tree         | basis|positioning             |      3 |
| raw_ast_explore      | regime|taker_flow             |      3 |
| cem_ast_prior        | open_interest|taker_flow      |      3 |
| cem_ast_prior        | positioning|positioning       |      3 |
| map_elites_diversity | funding_sparse|funding_sparse |      2 |
| map_elites_diversity | open_interest|taker_flow      |      2 |
| map_elites_diversity | age|taker_flow                |      2 |
| cem_ast_prior        | funding_dense|liquidity       |      2 |
| cem_ast_prior        | open_interest|open_interest   |      2 |
| cem_ast_prior        | open_interest|premium         |      2 |
| cem_ast_prior        | regime|taker_flow             |      2 |
| map_elites_diversity | age|positioning               |      2 |
| cem_ast_prior        | premium|taker_flow            |      2 |
| cem_ast_prior        | positioning|taker_flow        |      2 |
| cem_ast_prior        | basis|funding_sparse          |      2 |
| cem_ast_prior        | funding_basis|funding_basis   |      2 |
| cem_ast_prior        | funding_dense|open_interest   |      2 |
| cem_ast_prior        | basis|funding_dense           |      2 |
| uct_ast_tree         | premium|premium               |      2 |
| uct_ast_tree         | funding_dense|positioning     |      2 |
| uct_ast_tree         | basis|taker_flow              |      2 |
| uct_ast_tree         | positioning|positioning       |      2 |
| uct_ast_tree         | positioning|premium           |      2 |
| uct_ast_tree         | open_interest|premium         |      2 |
| raw_ast_explore      | basis|regime                  |      2 |

## Motif Summary

| search_policy        | motif                    |   rows |
|:---------------------|:-------------------------|-------:|
| uct_ast_tree         | safe_div_abs             |     34 |
| cem_ast_prior        | safe_div_abs             |     27 |
| map_elites_diversity | safe_div_abs             |     26 |
| cem_ast_prior        | safe_div_abs_gated       |     23 |
| uct_ast_tree         | safe_div_abs_gated       |     23 |
| raw_ast_explore      | smooth_mul               |     16 |
| raw_ast_explore      | additive_composite       |     14 |
| cem_ast_prior        | spread                   |     12 |
| raw_ast_explore      | safe_div_abs             |     12 |
| raw_ast_explore      | spread                   |     10 |
| uct_ast_tree         | spread                   |     10 |
| uct_ast_tree         | additive_composite       |      8 |
| cem_ast_prior        | additive_composite       |      8 |
| cem_ast_prior        | smooth_mul               |      7 |
| cem_ast_prior        | additive_composite_gated |      5 |
| uct_ast_tree         | smooth_mul               |      5 |
| uct_ast_tree         | spread_gated             |      4 |
| cem_ast_prior        | smooth_mul_gated         |      3 |
| map_elites_diversity | spread                   |      3 |
| uct_ast_tree         | smooth_mul_gated         |      2 |
| cem_ast_prior        | spread_gated             |      2 |
| map_elites_diversity | smooth_mul               |      1 |
| uct_ast_tree         | additive_composite_gated |      1 |

## Guardrails

- Search policies generate candidates only.
- Proxy evaluation is not promotion.
- Strict reward remains the only accepted-for-next-search gate.
- Every candidate records search_policy, AST path, semantic pair, motif, fields, windows, and origin.
- A7MEM prior is fail-closed by default; use --no-memory-enforcement only for legacy reproduction.