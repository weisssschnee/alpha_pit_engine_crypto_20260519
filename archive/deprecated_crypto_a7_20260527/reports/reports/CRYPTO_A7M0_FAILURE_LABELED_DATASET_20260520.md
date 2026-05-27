# Crypto A7M-0 Failure-Labeled Search Dataset

- generated_at: `2026-05-20T03:38:17Z`
- decision: `PASS_A7M0_FAILURE_LABELED_DATASET_BUILD`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- executes_search: `False`
- executes_replay: `False`
- trains_surrogate: `False`
- authorizes_a7m1_surrogate_preflight: `True`
- authorizes_large_search: `False`
- row_count: `3417`

## Purpose

A7M-0 converts A7I/A7J/A7K/A7L negative evidence into a structured multi-label dataset for future active search policy work. It does not promote any candidate.

## May Policy

- May 2026 labels are included only as stress/failure attribution labels.
- May labels are explicitly marked `policy_training_allowed = False`.
- A7M-1 may not train ranking, reward, arm allocation, generator tuning, or mutation priors on May labels.

## Source Summary

| source_run | rows | selected | research | near_miss | clue | may_stress_fail |
|---|---:|---:|---:|---:|---:|---:|
| `A7I1B_original_generator` | 1000 | 256 | 1 | 32 | 0 | 230 |
| `A7J2_reranked_original_pool` | 1000 | 256 | 0 | 29 | 140 | 798 |
| `A7K2_new_space` | 1000 | 64 | 0 | 64 | 64 | 758 |
| `A7L1B_dry_preflight` | 417 | 0 | 0 | 0 | 0 | 0 |

## Label Summary

| label | count | rate | policy_training_allowed |
|---|---:|---:|---|
| `coverage_fail` | 0 | 0.0 | `True` |
| `activity_fail` | 52 | 0.015218 | `True` |
| `raw_validation_fail` | 2447 | 0.716125 | `True` |
| `raw_recent_fail` | 2635 | 0.771144 | `True` |
| `residual_funding_validation_fail` | 1333 | 0.390108 | `True` |
| `residual_funding_recent_fail` | 1353 | 0.395961 | `True` |
| `residual_core4_recent_fail` | 1361 | 0.398303 | `True` |
| `cost20_validation_fail` | 1934 | 0.565994 | `True` |
| `cost20_recent_fail` | 2754 | 0.80597 | `True` |
| `lag1_validation_fail` | 1649 | 0.482587 | `True` |
| `lag1_recent_fail` | 2576 | 0.753878 | `True` |
| `funding_beta_fail` | 9 | 0.002634 | `True` |
| `core4_beta_fail` | 40 | 0.011706 | `True` |
| `may_raw_severe_fail_stress_only` | 1760 | 0.515072 | `False` |
| `may_residual_funding_negative_stress_only` | 1459 | 0.426983 | `False` |
| `near_miss_label` | 125 | 0.036582 | `True` |
| `research_candidate_label` | 1 | 0.000293 | `True` |
| `clue_label` | 204 | 0.059701 | `True` |
| `placebo_like` | 822 | 0.240562 | `True` |

## Decision

A7M-0 passes as a dataset build. It authorizes A7M-1 surrogate/policy preflight only. It does not authorize adaptive large search or alpha proof.
