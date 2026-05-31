# CRYPTO A7FF-CORE9 BOUNDED REPLAY CONTRACT

Generated: 2026-05-31T23:37:11Z

## Decision

`PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E`

A7FF-CORE9 defines the bounded replay protocol for the CORE8E packet. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core9e": true,
  "authorizes_large_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 114,
  "control_count": 5,
  "cost_tier_count": 4,
  "decision": "PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T23:37:11Z",
  "horizon_count": 4,
  "label_count": 3,
  "motif_bucket_count": 7,
  "next_allowed": "A7FF-CORE9E bounded replay execution",
  "semantic_bucket_count": 9,
  "shard_count": 4,
  "source_decision": "PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT",
  "source_stage": "A7FF-CORE8E",
  "stage": "A7FF-CORE9"
}
```

## Replay Protocol

```json
{
  "candidate_count": 114,
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo"
  ],
  "cost_bps": [
    0,
    2,
    5,
    10
  ],
  "hard_reject": [
    "eval_error_count > 0",
    "label_or_may_token",
    "missing_field_count > 0",
    "control_ratio >= 1.0 in any primary split",
    "wrong_lag_future stronger than original",
    "single_symbol_share > 0.20",
    "single_month_share > 0.35",
    "single_semantic_bucket_share > 0.35",
    "single_motif_bucket_share > 0.35"
  ],
  "horizons": [
    1,
    4,
    8,
    24
  ],
  "input_packet": "runtime\\a7ffcore8e_replay_preflight_packet_audit\\a7ffcore8e_replay_preflight_packet.csv",
  "labels": [
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "orientation": {
    "may_used": false,
    "sign_flip_policy": "diagnostic_only_not_allowed_as_abs_control_dominance",
    "source": "CORE7ER numeric clue sign by label/horizon"
  },
  "pass_gate": [
    "at least 16 replay-clean candidates",
    "at least 4 semantic buckets",
    "at least 4 motif buckets",
    "non-L7 primary label evidence remains positive",
    "controls weaker than original on primary labels",
    "cost 5bps survives for replay-clean queue"
  ],
  "portfolio_proxy": {
    "dollar_neutral": true,
    "long_leg": "top_decile_or_top10_if_active_count_lt_100",
    "max_motif_bucket_weight": 0.35,
    "max_semantic_bucket_weight": 0.3,
    "max_symbol_weight": 0.02,
    "ranking": "cross_sectional_per_timestamp",
    "short_leg": "bottom_decile_or_bottom10_if_active_count_lt_100",
    "weighting": "equal_weight_with_per_symbol_cap"
  },
  "splits": [
    "train",
    "validation",
    "recent"
  ],
  "statistics": [
    "split_spread",
    "non_overlap_offset_spread",
    "hourly_overlap_tstat",
    "block_bootstrap_tstat",
    "control_dominance_margin",
    "turnover_proxy",
    "cost_adjusted_spread",
    "symbol_month_contribution",
    "semantic_motif_concentration"
  ]
}
```

## Shard Plan

| shard_id   |   start_index |   end_index_exclusive |   candidate_count |
|:-----------|--------------:|----------------------:|------------------:|
| S00        |             0 |                    32 |                32 |
| S01        |            32 |                    64 |                32 |
| S02        |            64 |                    96 |                32 |
| S03        |            96 |                   114 |                18 |

## Label Contract

| label_id                           |   horizon | is_primary   |
|:-----------------------------------|----------:|:-------------|
| L1_cross_sectional_relative_return |         1 | True         |
| L1_cross_sectional_relative_return |         4 | True         |
| L1_cross_sectional_relative_return |         8 | True         |
| L1_cross_sectional_relative_return |        24 | True         |
| L3_liquidity_tier_relative_return  |         1 | True         |
| L3_liquidity_tier_relative_return  |         4 | True         |
| L3_liquidity_tier_relative_return  |         8 | True         |
| L3_liquidity_tier_relative_return  |        24 | True         |
| L5_vol_adjusted_return             |         1 | True         |
| L5_vol_adjusted_return             |         4 | True         |
| L5_vol_adjusted_return             |         8 | True         |
| L5_vol_adjusted_return             |        24 | True         |

## Control Contract

| control             | dominance_role                    |
|:--------------------|:----------------------------------|
| wrong_lag_future    | hard_control                      |
| wrong_lag_stale     | hard_control                      |
| time_shuffle        | hard_control                      |
| symbol_shuffle      | hard_control                      |
| same_family_placebo | hard_control                      |
| sign_flip           | diagnostic_only_orientation_check |

## Boundary

```text
bounded replay execution authorized as next stage: true
large replay: false
formula search / large search: false
alpha proof / shadow / paper / live: false
```
