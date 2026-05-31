# CRYPTO A7FF-CORE8E REPLAY-PREFLIGHT PACKET AUDIT

Generated: 2026-05-31T23:34:41Z

## Decision

`PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT`

A7FF-CORE8E audits the CORE8 packet as input for a future replay contract. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core9_contract": true,
  "authorizes_replay_execution": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T23:34:41Z",
  "horizon_count": 4,
  "label_family_count": 3,
  "motif_bucket_count": 7,
  "next_allowed": "A7FF-CORE9 bounded replay contract",
  "packet_candidate_count": 114,
  "packet_ready_count": 114,
  "risk_flags": [],
  "semantic_bucket_count": 9,
  "shard_count": 4,
  "source_decision": "PASS_A7FFCORE8_NUMERIC_CLUE_CONSOLIDATION_READY_FOR_CORE8E",
  "source_stage": "A7FF-CORE8",
  "stage": "A7FF-CORE8E",
  "top_motif_bucket_share": 0.24561403508771928,
  "top_semantic_bucket_share": 0.21052631578947367
}
```

## Label-Horizon Coverage

| label_id                           |   horizon |   candidate_count |   clue_rows |   median_control_ratio |
|:-----------------------------------|----------:|------------------:|------------:|-----------------------:|
| L1_cross_sectional_relative_return |         4 |                51 |          51 |               0.490987 |
| L1_cross_sectional_relative_return |         8 |                47 |          47 |               0.556763 |
| L3_liquidity_tier_relative_return  |         4 |                47 |          47 |               0.462307 |
| L3_liquidity_tier_relative_return  |         8 |                47 |          47 |               0.572461 |
| L1_cross_sectional_relative_return |        24 |                31 |          31 |               0.665061 |
| L1_cross_sectional_relative_return |         1 |                29 |          29 |               0.658418 |
| L3_liquidity_tier_relative_return  |         1 |                29 |          29 |               0.618879 |
| L5_vol_adjusted_return             |        24 |                24 |          24 |               0.683444 |
| L5_vol_adjusted_return             |         8 |                23 |          23 |               0.639357 |
| L3_liquidity_tier_relative_return  |        24 |                18 |          18 |               0.595154 |
| L5_vol_adjusted_return             |         4 |                18 |          18 |               0.651467 |
| L5_vol_adjusted_return             |         1 |                12 |          12 |               0.637329 |

## Semantic Bucket Audit

| semantic_bucket                      |   candidate_count |   ready_count |   median_min_control_ratio |
|:-------------------------------------|------------------:|--------------:|---------------------------:|
| liquidity_like\|volatility_like      |                24 |            24 |                   0.350897 |
| taker_flow_like\|open_interest_like  |                24 |            24 |                   0.364714 |
| open_interest_like\|price_like       |                24 |            24 |                   0.534425 |
| taker_flow_like                      |                15 |            15 |                   0.589722 |
| liquidity_like                       |                 8 |             8 |                   0.648357 |
| open_interest_like                   |                 8 |             8 |                   0.678945 |
| taker_flow_like\|basis_premium_like  |                 7 |             7 |                   0.566731 |
| open_interest_like\|positioning_like |                 2 |             2 |                   0.609825 |
| volatility_like                      |                 2 |             2 |                   0.626293 |

## Motif Bucket Audit

| motif_bucket        |   candidate_count |   ready_count |   median_min_control_ratio |
|:--------------------|------------------:|--------------:|---------------------------:|
| single              |                28 |            28 |                   0.611764 |
| mean_reversion_gate |                24 |            24 |                   0.534425 |
| flow_x_leverage     |                24 |            24 |                   0.364714 |
| liquidity_shock     |                14 |            14 |                   0.406516 |
| safe_div_abs        |                12 |            12 |                   0.291669 |
| gated_sign          |                 7 |             7 |                   0.566731 |
| delta_x_divergence  |                 5 |             5 |                   0.693701 |

## Role/Gate Audit

| candidate_roles                             | formula_gen_gate               | gate_mode         |   candidate_count |   ready_count |
|:--------------------------------------------|:-------------------------------|:------------------|------------------:|--------------:|
| role_mixed_allowed                          | diagnostic_or_repair_root_only | diagnostic_repair |                81 |            81 |
| exploratory_signal_probe                    | diagnostic_or_repair_root_only | diagnostic_repair |                28 |            28 |
| exploratory_signal_probe;role_mixed_allowed | diagnostic_or_repair_root_only | diagnostic_repair |                 5 |             5 |

## Shard Plan

| shard_id   |   start_index |   end_index_exclusive |   candidate_count |
|:-----------|--------------:|----------------------:|------------------:|
| S00        |             0 |                    32 |                32 |
| S01        |            32 |                    64 |                32 |
| S02        |            64 |                    96 |                32 |
| S03        |            96 |                   114 |                18 |

## Boundary

```text
portfolio replay execution: false
formula search: false
promotion: false
alpha proof / shadow / paper / live: false
```
