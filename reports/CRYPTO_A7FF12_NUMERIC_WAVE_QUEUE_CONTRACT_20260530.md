# CRYPTO A7FF-12 NUMERIC WAVE QUEUE CONTRACT

Generated: 2026-05-30T03:28:36Z

## Decision

`PASS_A7FF12_NUMERIC_WAVE_QUEUE_READY_FOR_COMPANY_EXECUTION`

A7FF-12 builds a broader numeric-probe queue from the full A7FF-7E blueprint pool. It excludes the already-covered 384 queue and does not run generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_company_numeric_probe": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_pool_rows": 8887,
  "decision": "PASS_A7FF12_NUMERIC_WAVE_QUEUE_READY_FOR_COMPANY_EXECUTION",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_search": false,
  "full_pool_rows": 9271,
  "generated_at": "2026-05-30T03:28:36Z",
  "max_per_motif": 128,
  "max_per_semantic": {
    "basis_premium_like": 0,
    "basis_premium_like|basis_premium_like": 192,
    "basis_premium_like|positioning_like": 240,
    "basis_premium_like|price_like": 144,
    "basis_premium_like|volatility_like": 192
  },
  "max_per_skeleton": 8,
  "motif_count": 7,
  "old_queue_rows": 384,
  "selected_queue_size": 720,
  "semantic_pair_count": 4,
  "skeleton_count": 102,
  "source_a7ff11_decision": "PASS_A7FF11_TRIAGE_READY_FOR_A7FF12_NUMERIC_WAVE_WITH_LABEL_DIVERSITY_WARNING",
  "source_a7ff11r_decision": "PASS_A7FF11R_COMPANY_RUNNER_CONTRACT_READY_WITH_MANIFEST_POLLING_REQUIRED",
  "stage": "A7FF-12-NUMERIC-WAVE-QUEUE-CONTRACT",
  "target_queue_size": 720,
  "uses_may": false
}
```

## Candidate Coverage

| bucket                    |   count |
|:--------------------------|--------:|
| full_pool                 |    9271 |
| old_a7ff7e_selected_queue |     384 |
| unselected_candidate_pool |    8887 |
| a7ff12_selected_queue     |     720 |

## Semantic Quotas

| semantic_pair                          |   count |
|:---------------------------------------|--------:|
| basis_premium_like\|positioning_like   |     215 |
| basis_premium_like\|basis_premium_like |     192 |
| basis_premium_like\|volatility_like    |     192 |
| basis_premium_like\|price_like         |     121 |

## Motif Quotas

| motif              |   count |
|:-------------------|--------:|
| relative_shock     |     128 |
| spread_rank        |     128 |
| smooth_interaction |     128 |
| gated_sign         |      97 |
| mul                |      80 |
| sub                |      80 |
| safe_div_abs       |      79 |

## Transform Summary

| primary_transform   | secondary_transform   |   count |
|:--------------------|:----------------------|--------:|
| winsor_zscore       | winsor_zscore         |      40 |
| winsor_zscore       | csrank                |      35 |
| delta_12h           | csrank                |      34 |
| csrank              | csrank                |      33 |
| csrank              | winsor_zscore         |      31 |
| abs_zscore          | winsor_zscore         |      28 |
| delta_12h           | winsor_zscore         |      28 |
| abs_zscore          | csrank                |      27 |
| delta_12h           | abs_zscore            |      18 |
| delta_12h           | level                 |      18 |
| level               | csrank                |      17 |
| csrank              | level                 |      17 |
| winsor_zscore       | delta_12h             |      16 |
| level               | winsor_zscore         |      16 |
| csrank              | delta_12h             |      15 |
| winsor_zscore       | level                 |      15 |
| csrank              | abs_zscore            |      14 |
| csrank              | delta_24h             |      14 |
| winsor_zscore       | abs_zscore            |      13 |
| winsor_zscore       | delta_1h              |      13 |
| delta_12h           | delta_12h             |      13 |
| delta_12h           | delta_1h              |      12 |
| abs_zscore          | delta_24h             |      12 |
| csrank              | sign_delta_24h        |      11 |
| delta_12h           | delta_24h             |      11 |
| csrank              | delta_1h              |      11 |
| delta_1h            | abs_zscore            |      10 |
| abs_zscore          | abs_zscore            |      10 |
| delta_12h           | sign_delta_24h        |      10 |
| winsor_zscore       | sign_delta_24h        |      10 |
| abs_zscore          | delta_12h             |      10 |
| winsor_zscore       | delta_24h             |      10 |
| delta_1h            | winsor_zscore         |       9 |
| abs_zscore          | level                 |       8 |
| level               | level                 |       8 |
| level               | sign_delta_24h        |       8 |
| abs_zscore          | delta_1h              |       7 |
| level               | delta_24h             |       7 |
| abs_zscore          | sign_delta_24h        |       7 |
| level               | abs_zscore            |       7 |
| level               | delta_1h              |       7 |
| delta_1h            | level                 |       7 |
| csrank              | zscore                |       7 |
| zscore              | winsor_zscore         |       6 |
| abs_zscore          | zscore                |       5 |
| winsor_zscore       | zscore                |       5 |
| delta_24h           | level                 |       5 |
| delta_12h           | zscore                |       4 |
| delta_24h           | sign_delta_24h        |       4 |
| delta_1h            | sign_delta_24h        |       4 |
| delta_4h            | sign_delta_24h        |       3 |
| delta_24h           | winsor_zscore         |       3 |
| level               | delta_12h             |       3 |
| abs_zscore          | delta_4h              |       2 |
| delta_1h            | csrank                |       2 |
| delta_12h           | delta_4h              |       2 |
| delta_4h            | level                 |       2 |
| level               | delta_4h              |       2 |
| zscore              | abs_zscore            |       2 |
| delta_24h           | delta_24h             |       1 |
| delta_24h           | abs_zscore            |       1 |
| delta_1h            | delta_12h             |       1 |
| abs_zscore          | tsrank_24h            |       1 |
| level               | tsrank_24h            |       1 |
| level               | mean_24h              |       1 |
| delta_4h            | abs_zscore            |       1 |
| level               | decay_8h              |       1 |
| winsor_zscore       | delta_4h              |       1 |
| level               | zscore                |       1 |
| zscore              | level                 |       1 |
| zscore              | sign_delta_24h        |       1 |

## Boundary

```text
This is a queue contract only.
No May is used.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-12 numeric execution must use company-machine preflight and manifest polling from A7FF-11R.
```
