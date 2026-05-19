# Crypto A7I-1a Runner Implementation Preflight

- generated_at: `2026-05-19T16:00:37Z`
- decision: `PASS_A7I1A_RUNNER_PREFLIGHT`
- executes_search: `False`
- authorizes_a7i1b: `True`
- authorizes_alpha_proof: `False`
- blockers: `[]`

## Scope

A7I-1a tests runner mechanics on fixed known objects and placebo variants. It does not run matched-budget search.

## May Usage Audit

| check | pass | detail |
|---|---:|---|
| `rank_score_components_have_no_may_columns` | `True` |  |
| `candidate_selection_trace_has_no_may_threshold_or_weight` | `True` | may_derived_threshold_used=False; may_derived_weight_used=False |
| `rank_order_unchanged_after_may_shuffle` | `True` | May stress label shuffled in audit-only column |
| `rank_order_unchanged_after_may_delete` | `True` | May columns deleted from ranking frame |
| `selected_for_replay_unchanged_after_may_shuffle_delete` | `True` | selection driven by validation/recent rank score only |
| `may_affects_only_final_stress_label` | `True` | May stress label is written in classification audit only |

## Baseline Classification

| candidate | expected | runner | match |
|---|---|---|---:|
| `a7i1a_fundingcore_baseline` | `MANDATORY_BASELINE_NOT_CANDIDATE` | `MANDATORY_BASELINE_NOT_CANDIDATE` | `True` |
| `a7i1a_core4_benchmark` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` | `True` |
| `a7i1a_taker_imbalance_original` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` | `True` |
| `a7i1a_avg_trade_size_original` | `REJECTED_TAIL_RISK` | `REJECTED_TAIL_RISK` | `True` |
| `a7i1a_taker_imbalance_sign_flip` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` |
| `a7i1a_taker_imbalance_row_shuffle` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` |
| `a7i1a_taker_imbalance_time_shuffle` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` |
| `a7i1a_taker_imbalance_wrong_lag` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` |
| `a7i1a_random_noise_placebo` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` |

## Selection Trace

| selected candidate | rank score | reason |
|---|---:|---|

## Decision Boundary

- PASS authorizes A7I-1b small matched-budget smoke implementation/run.
- PASS does not authorize alpha proof, shadow, paper, or live.
- May 2026 remains known adversarial stress and is not used for ranking or selection.
