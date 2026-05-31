# CRYPTO A7FF-55R5 REPAIRED ATLAS NUMERIC CONTRACT

Generated: 2026-05-31T12:41:36Z

## Decision

`PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION`

A7FF-55R5 defines the bounded primary-label numeric execution over the repaired 2400-row atlas queue. It does not execute numeric evaluation, replay, or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_numeric_execution": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION",
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "expected_label_response_rows": 28800,
  "generated_at": "2026-05-31T12:41:36Z",
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return"
  ],
  "motif_count": 9,
  "next_allowed": "A7FF-55R5E repaired atlas numeric execution",
  "queue_rows": 2400,
  "semantic_pair_count": 8,
  "source_decision": "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT",
  "source_stage": "A7FF-55R4",
  "stage": "A7FF-55R5",
  "uses_may": false
}
```

## Label Plan

| label_family                       | role              | horizons     | promotion_use                                              |
|:-----------------------------------|:------------------|:-------------|:-----------------------------------------------------------|
| L0_raw_forward_return              | primary           | 1h,4h,8h,24h | raw return sanity; cannot pass alone if control dominated  |
| L1_cross_sectional_relative_return | primary           | 1h,4h,8h,24h | primary cross-sectional economics; required representation |
| L3_liquidity_tier_relative_return  | primary           | 1h,4h,8h,24h | liquidity-tier robustness; required representation         |
| L5_vol_adjusted_return             | blocked_this_wave | none         | blocked to prevent previous L5 absorption                  |
| L7_ranked_future_return            | blocked_this_wave | none         | diagnostic only, not part of repaired primary wave         |

## Queue Summary

| semantic_pair                        | motif               |   queue_rows |
|:-------------------------------------|:--------------------|-------------:|
| liquidity_like\|volatility_like      | liquidity_shock     |          308 |
| open_interest_like\|positioning_like | delta_x_divergence  |          308 |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |          308 |
| open_interest_like\|positioning_like | safe_div_abs        |          292 |
| liquidity_like\|volatility_like      | mean_reversion_gate |          292 |
| open_interest_like\|price_like       | mean_reversion_gate |          174 |
| taker_flow_like\|open_interest_like  | relative_shock      |          169 |
| open_interest_like\|price_like       | delta_x_divergence  |          163 |
| taker_flow_like\|open_interest_like  | gated_sign          |          123 |
| liquidity_like                       | single              |          108 |
| open_interest_like\|price_like       | smooth_mul          |          103 |
| open_interest_like                   | single              |           28 |
| taker_flow_like                      | single              |           16 |
| volatility_like                      | single              |            8 |

## Shard Plan

| company_shard   |   queue_rows |   semantic_pairs |   motifs |
|:----------------|-------------:|-----------------:|---------:|
| shard_00        |          200 |                2 |        2 |
| shard_01        |          200 |                1 |        1 |
| shard_02        |          200 |                1 |        2 |
| shard_03        |          200 |                3 |        3 |
| shard_04        |          200 |                1 |        1 |
| shard_05        |          200 |                1 |        2 |
| shard_06        |          200 |                3 |        3 |
| shard_07        |          200 |                1 |        1 |
| shard_08        |          200 |                1 |        3 |
| shard_09        |          200 |                3 |        3 |
| shard_10        |          200 |                1 |        2 |
| shard_11        |          200 |                1 |        2 |

## Execution Environment

```json
{
  "A7FF8_AUTH_DECISION": "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION",
  "A7FF8_AUTH_MANIFEST": "runtime/a7ff55r5_repaired_atlas_numeric_contract/a7ff55r5_manifest.json",
  "A7FF8_FAST_NUMERIC_CAP": "2400",
  "A7FF8_FILE_PREFIX": "a7ff55r5e",
  "A7FF8_LABELS": "L0_raw_forward_return,L1_cross_sectional_relative_return,L3_liquidity_tier_relative_return",
  "A7FF8_MATERIALIZE_CAP": "2400",
  "A7FF8_PLAN_PATH": "runtime/a7ff55r5_repaired_atlas_numeric_contract/a7ff55r5_numeric_plan.json",
  "A7FF8_PORTFOLIO_CAP": "256",
  "A7FF8_QUEUE_LIMIT": "0",
  "A7FF8_QUEUE_OFFSET": "0",
  "A7FF8_QUEUE_PATH": "runtime/a7ff55r3_repaired_atlas_dry_generation/a7ff55r3_repaired_materialization_queue.csv",
  "A7FF8_REPORT": "reports/CRYPTO_A7FF55R5E_REPAIRED_ATLAS_NUMERIC_EXECUTION_20260531.md",
  "A7FF8_RUNTIME": "runtime/a7ff55r5e_repaired_atlas_numeric_execution",
  "A7FF8_STAGE": "A7FF-55R5E",
  "A7FF8_WRITE_CONTROL_DETAIL": "0"
}
```

## Boundary

```text
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
