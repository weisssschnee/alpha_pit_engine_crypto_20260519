# CRYPTO A7FF-24R2 REPAIRED COMPANY QUEUE

Generated: 2026-05-30T10:41:18Z

## Decision

`PASS_A7FF24R2_REPAIRED_COMPANY_QUEUE_READY_FOR_DENSE_MATERIALIZER_PREFLIGHT_NO_SEARCH_AUTH`

A7FF-24R2 rebuilds the A7FF-24R company numeric wave queue by preserving healthy shards 00-07 and replacing raw sparse funding_rate tail expressions in shards 08-11 with dense funding-state expressions. It does not run numeric replay or search.

## Experiment Record

```text
experiment_id: 20260530_a7ff24r2_repaired_company_queue
objective: repair no-activity funding tail queue without expanding search
inputs: A7FF-24R queue, A7FF-25R4 tail audit, A7FF-25R6 dense funding-state audit
parameters: preserve 1600 healthy rows; repair 800 tail rows; 12 shards x 200 rows
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_dense_materializer_preflight": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "company_shard_count": 12,
  "decision": "PASS_A7FF24R2_REPAIRED_COMPANY_QUEUE_READY_FOR_DENSE_MATERIALIZER_PREFLIGHT_NO_SEARCH_AUTH",
  "dense_tail_rows": 800,
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T10:41:18Z",
  "healthy_preserved_count": 1600,
  "original_queue_count": 2400,
  "raw_funding_rate_remaining_tail_rows": 0,
  "repaired_queue_count": 2400,
  "stage": "A7FF-24R2",
  "tail_repaired_count": 800,
  "warnings": []
}
```

## Shard Plan

| company_shard   |   row_count |   semantic_pairs |   motifs |   skeletons |   raw_funding_rate_rows |   dense_funding_rows |
|:----------------|------------:|-----------------:|---------:|------------:|------------------------:|---------------------:|
| shard_00        |         200 |                2 |        5 |          20 |                       0 |                    0 |
| shard_01        |         200 |                1 |        3 |          17 |                       0 |                    0 |
| shard_02        |         200 |                2 |        4 |          10 |                       0 |                    0 |
| shard_03        |         200 |                1 |        3 |          12 |                       0 |                    0 |
| shard_04        |         200 |                2 |        4 |          12 |                       0 |                    0 |
| shard_05        |         200 |                1 |        4 |          12 |                       0 |                    0 |
| shard_06        |         200 |                2 |        6 |          14 |                       0 |                    0 |
| shard_07        |         200 |                6 |        7 |          17 |                      13 |                    0 |
| shard_08        |         200 |                1 |        2 |          18 |                       0 |                  200 |
| shard_09        |         200 |                1 |        2 |          24 |                       0 |                  200 |
| shard_10        |         200 |                1 |        2 |          22 |                       0 |                  200 |
| shard_11        |         200 |                2 |        4 |          27 |                       0 |                  200 |

## Repaired Tail Summary

| semantic_pair                   | motif               | repair_rule         |   count |
|:--------------------------------|:--------------------|:--------------------|--------:|
| basis_premium_like|funding_like | gated_sign          | delta_dense_state   |      31 |
| basis_premium_like|funding_like | gated_sign          | generic_dense_state |       2 |
| basis_premium_like|funding_like | gated_sign          | mean_dense_state    |      81 |
| basis_premium_like|funding_like | mean_reversion_gate | delta_dense_state   |      50 |
| basis_premium_like|funding_like | mean_reversion_gate | generic_dense_state |      32 |
| basis_premium_like|funding_like | mean_reversion_gate | mean_dense_state    |     174 |
| basis_premium_like|funding_like | mul                 | generic_dense_state |       2 |
| basis_premium_like|funding_like | mul                 | mean_dense_state    |      60 |
| basis_premium_like|funding_like | relative_shock      | delta_dense_state   |      91 |
| basis_premium_like|funding_like | relative_shock      | mean_dense_state    |     223 |
| basis_premium_like|funding_like | safe_div_abs        | generic_dense_state |       2 |
| basis_premium_like|funding_like | safe_div_abs        | mean_dense_state    |      20 |
| basis_premium_like|funding_like | signed_spread       | mean_dense_state    |      19 |
| funding_like|positioning_like   | gated_sign          | delta_dense_state   |       5 |
| funding_like|positioning_like   | gated_sign          | mean_dense_state    |       8 |

## Dense Field Usage

| field                            |   queue_expression_count | r6_activity_ok   |
|:---------------------------------|-------------------------:|:-----------------|
| funding_rate_state_last_ffill_8h |                      800 | True             |
| funding_rate_update_age_hours    |                        0 | True             |
| funding_rate_abs_state_168h_z    |                        0 | True             |
| funding_rate_delta_state_24h     |                        0 | True             |
| funding_state_x_basis_delta      |                        0 | True             |

## Repair Policy

| gate                        | rule                                                                                              | status   |
|:----------------------------|:--------------------------------------------------------------------------------------------------|:---------|
| no_raw_funding_rate_tail    | tail shard expressions may not contain raw funding_rate as the dense signal source                | pass     |
| dense_materializer_required | numeric runner must materialize funding_rate_state_last_ffill_8h before evaluating repaired queue | required |
| tail_activity_precheck      | A7FF-25R6 dense state finite/nonzero activity passed on 96-symbol audit                           | pass     |
| search_boundary             | queue rebuild does not authorize formula search                                                   | pass     |

## Boundary

```text
A7FF-24R2 only repairs the queue. It does not execute formula search, large search, alpha proof, shadow, paper, or live trading.
The next valid step is dense materializer preflight on the repaired queue.
```
