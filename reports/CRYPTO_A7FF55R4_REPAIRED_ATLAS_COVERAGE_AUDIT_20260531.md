# CRYPTO A7FF-55R4 REPAIRED ATLAS COVERAGE AUDIT

Generated: 2026-05-31T12:02:36Z

## Decision

`PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT`

A7FF-55R4 audits the repaired 2400-row atlas queue coverage. It does not run numeric evaluation, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric_contract": true,
  "authorizes_numeric_execution": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT",
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "formula_count": 9240,
  "generated_at": "2026-05-31T12:02:36Z",
  "motif_count": 9,
  "next_allowed": "A7FF-55R5 repaired atlas numeric contract",
  "queue_count": 2400,
  "required_pairs_present": [
    "liquidity_like|volatility_like",
    "open_interest_like|positioning_like",
    "taker_flow_like|open_interest_like"
  ],
  "semantic_pair_count": 8,
  "stage": "A7FF-55R4",
  "top_motif_share": 0.19625,
  "top_pair_motif_share": 0.12833333333333333,
  "top_semantic_pair_share": 0.25,
  "uses_may": false
}
```

## Queue By Semantic Pair

| semantic_pair                        |   queue_count |   queue_share |
|:-------------------------------------|--------------:|--------------:|
| liquidity_like\|volatility_like      |           600 |    0.25       |
| open_interest_like\|positioning_like |           600 |    0.25       |
| taker_flow_like\|open_interest_like  |           600 |    0.25       |
| open_interest_like\|price_like       |           440 |    0.183333   |
| liquidity_like                       |           108 |    0.045      |
| open_interest_like                   |            28 |    0.0116667  |
| taker_flow_like                      |            16 |    0.00666667 |
| volatility_like                      |             8 |    0.00333333 |

## Queue By Motif

| motif               |   queue_count |   queue_share |
|:--------------------|--------------:|--------------:|
| delta_x_divergence  |           471 |     0.19625   |
| mean_reversion_gate |           466 |     0.194167  |
| flow_x_leverage     |           308 |     0.128333  |
| liquidity_shock     |           308 |     0.128333  |
| safe_div_abs        |           292 |     0.121667  |
| relative_shock      |           169 |     0.0704167 |
| single              |           160 |     0.0666667 |
| gated_sign          |           123 |     0.05125   |
| smooth_mul          |           103 |     0.0429167 |

## Queue By Pair / Motif

| semantic_pair                        | motif               |   queue_count |   queue_share |
|:-------------------------------------|:--------------------|--------------:|--------------:|
| liquidity_like\|volatility_like      | liquidity_shock     |           308 |    0.128333   |
| open_interest_like\|positioning_like | delta_x_divergence  |           308 |    0.128333   |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |           308 |    0.128333   |
| open_interest_like\|positioning_like | safe_div_abs        |           292 |    0.121667   |
| liquidity_like\|volatility_like      | mean_reversion_gate |           292 |    0.121667   |
| open_interest_like\|price_like       | mean_reversion_gate |           174 |    0.0725     |
| taker_flow_like\|open_interest_like  | relative_shock      |           169 |    0.0704167  |
| open_interest_like\|price_like       | delta_x_divergence  |           163 |    0.0679167  |
| taker_flow_like\|open_interest_like  | gated_sign          |           123 |    0.05125    |
| liquidity_like                       | single              |           108 |    0.045      |
| open_interest_like\|price_like       | smooth_mul          |           103 |    0.0429167  |
| open_interest_like                   | single              |            28 |    0.0116667  |
| taker_flow_like                      | single              |            16 |    0.00666667 |
| volatility_like                      | single              |             8 |    0.00333333 |

## Queue By Shard

| company_shard   |   queue_count |   queue_share |
|:----------------|--------------:|--------------:|
| shard_00        |           200 |     0.0833333 |
| shard_01        |           200 |     0.0833333 |
| shard_02        |           200 |     0.0833333 |
| shard_03        |           200 |     0.0833333 |
| shard_04        |           200 |     0.0833333 |
| shard_05        |           200 |     0.0833333 |
| shard_06        |           200 |     0.0833333 |
| shard_07        |           200 |     0.0833333 |
| shard_08        |           200 |     0.0833333 |
| shard_09        |           200 |     0.0833333 |
| shard_10        |           200 |     0.0833333 |
| shard_11        |           200 |     0.0833333 |

## Boundary

```text
coverage audit executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
