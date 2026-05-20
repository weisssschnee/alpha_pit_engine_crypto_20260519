# Crypto A7L-0 Search-Space Coverage Audit

- generated_at: `2026-05-20T00:04:37Z`
- decision: `HOLD_A7L0_BUDGET_LADDER_NOT_AUTHORIZED`
- evidence_level: `coverage_audit_not_alpha_proof`
- executes_search: `False`
- executes_replay: `False`
- authorizes_budget_ladder_level1: `False`
- authorizes_alpha_proof: `False`
- blockers: `['a7k_preselection_pass_rate_below_10pct', 'a7k_zero_research_candidates', 'a7k_selected_candidates_may_failure_too_homogeneous']`

## Coverage Summary

| source | generated | unique expr ratio | field combos | op combos | horizons | preselect pass | research |
|---|---:|---:|---:|---:|---:|---:|---:|
| `A7I1B_original_generator` | 1000 | 0.723 | 14 | 15 | 2 | NA | 1 |
| `A7J2_reranked_original_pool` | 1000 | 0.723 | 14 | 15 | 2 | 0.011 | 0 |
| `A7K2_new_space` | 1000 | 1.000 | 15 | 8 | 2 | 0.064 | 0 |

## Gate Attrition

| source | stage | count | rate vs generated |
|---|---|---:|---:|
| `A7I1B_original_generator` | `generated` | 1000 | 1.0000 |
| `A7I1B_original_generator` | `non_may_preselection_pass` | NA | NA |
| `A7I1B_original_generator` | `selected` | 256 | 0.2560 |
| `A7I1B_original_generator` | `research_candidate` | 1 | 0.0010 |
| `A7I1B_original_generator` | `placebo_research_candidate` | 0 | 0.0000 |
| `A7I1B_original_generator` | `non_flow_research_candidate` | 0 | 0.0000 |
| `A7J2_reranked_original_pool` | `generated` | 1000 | 1.0000 |
| `A7J2_reranked_original_pool` | `non_may_preselection_pass` | 11 | 0.0110 |
| `A7J2_reranked_original_pool` | `selected` | 256 | 0.2560 |
| `A7J2_reranked_original_pool` | `research_candidate` | 0 | 0.0000 |
| `A7J2_reranked_original_pool` | `placebo_research_candidate` | 0 | 0.0000 |
| `A7J2_reranked_original_pool` | `non_flow_research_candidate` | 0 | 0.0000 |
| `A7K2_new_space` | `generated` | 1000 | 1.0000 |
| `A7K2_new_space` | `non_may_preselection_pass` | 64 | 0.0640 |
| `A7K2_new_space` | `selected` | 64 | 0.0640 |
| `A7K2_new_space` | `research_candidate` | 0 | 0.0000 |
| `A7K2_new_space` | `placebo_research_candidate` | 0 | 0.0000 |
| `A7K2_new_space` | `non_flow_research_candidate` | 0 | 0.0000 |

## Interpretation

- A7K is a narrow negative result, not a falsification of broader crypto formula search.
- A7L-0 checks whether the observed search distributions justify a budget ladder.
- If budget ladder is not authorized, the next valid work is search-space redesign or data/feature-layer rethink, not blind larger search.
