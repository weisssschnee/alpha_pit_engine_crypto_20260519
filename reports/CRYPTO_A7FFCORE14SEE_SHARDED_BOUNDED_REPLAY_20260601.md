# CRYPTO A7FF-CORE14SEE SHARDED BOUNDED REPLAY

Generated: 2026-06-01T06:57:05Z

## Decision

`HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE`

A7FF-CORE14SEE executes repaired packet bounded replay as resumable shards. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15_contract": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 128,
  "completed_shard_count": 16,
  "decision": "HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE",
  "eval_error_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T06:57:05Z",
  "next_allowed": "continue A7FF-CORE14SEE shards or run CORE14SER forensic after full shard completion",
  "replay_clean_candidate_count": 1,
  "replay_clean_motif_bucket_count": 1,
  "replay_clean_semantic_bucket_count": 1,
  "replay_row_count": 1536,
  "shard_count": 16,
  "source_decision": "PASS_A7FFCORE14SE_REPAIRED_PACKET_READY_FOR_BOUNDED_REPLAY",
  "source_stage": "A7FF-CORE14SE",
  "stage": "A7FF-CORE14SEE"
}
```

## Clean Candidates

| candidate_id                   | semantic_bucket                     | motif_bucket   |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |   shard_id |
|:-------------------------------|:------------------------------------|:---------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|-----------:|
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like | gated_sign     |            12 |      0.00102972 |                  -3.83035e-05 |     2.85705 |            0.660905 |                                2 | True           |          9 |
