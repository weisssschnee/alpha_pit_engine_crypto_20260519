# CRYPTO A7FF-1 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:57Z

## Decision

`PASS_A7FF1_OPERATOR_PROBING_READY_FOR_PAIR_CLUSTERING`

## Manifest

```json
{
  "allowed_operator_rows": 1,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [],
  "decision": "PASS_A7FF1_OPERATOR_PROBING_READY_FOR_PAIR_CLUSTERING",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T16:16:57Z",
  "operator_count": 3,
  "stage": "A7FF-1"
}
```

## Operator Reliability

| operator   |   semantic_type_count |   total_tests |   total_candidates |   total_non_l7_candidates |   best_score |   allow_count | operator_reliability   |
|:-----------|----------------------:|--------------:|-------------------:|--------------------------:|-------------:|--------------:|:-----------------------|
| CSRank     |                     7 |           216 |                  4 |                         0 |      5.24568 |             0 | diagnostic             |
| Identity   |                     7 |           216 |                  4 |                         0 |      5.24568 |             0 | diagnostic             |
| Delta      |                     7 |           216 |                  3 |                         2 |      4.53386 |             1 | allowed_limited        |

## Allowed Operator Rows

| semantic_type      | operator   |   test_count |   candidate_count |   non_l7_candidate_count |   median_control_ratio |   min_control_ratio |   mean_score |   max_score | operator_policy          |
|:-------------------|:-----------|-------------:|------------------:|-------------------------:|-----------------------:|--------------------:|-------------:|------------:|:-------------------------|
| basis_premium_like | Delta      |           45 |                 3 |                        2 |                9.47406 |            0.785786 |      1.88667 |     4.53386 | allow_for_coarse_to_fine |
