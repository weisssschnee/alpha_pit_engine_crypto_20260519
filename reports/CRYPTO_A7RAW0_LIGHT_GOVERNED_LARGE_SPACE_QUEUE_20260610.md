# CRYPTO A7RAW0 Light Governed Large-Space Queue 20260610

## Decision

`PASS_A7RAW0_LIGHT_GOVERNED_QUEUE_BUILT_NO_SEARCH_AUTH`

A7RAW0 is a lightly governed large-space raw-search queue. It does not hand-code narrow axes; it samples broad pairwise formula grammar from the approved field universe and applies only hard governance caps before field gate.

## Counts

- queue_rows: 16384
- candidate_rows_before_governance: 16500
- field_count: 31
- semantic_count: 8
- shard_count: 32
- rows_per_shard: 512

## Semantic Pair Summary

| semantic_pair                |   queue_rows |
|:-----------------------------|-------------:|
| basis\|positioning           |         1907 |
| open_interest\|positioning   |         1860 |
| positioning\|positioning     |         1416 |
| basis\|open_interest         |         1238 |
| positioning\|regime          |         1116 |
| age\|positioning             |          861 |
| positioning\|taker_flow      |          745 |
| open_interest\|regime        |          712 |
| basis\|regime                |          710 |
| basis\|basis                 |          579 |
| age\|open_interest           |          570 |
| age\|basis                   |          556 |
| open_interest\|open_interest |          537 |
| open_interest\|taker_flow    |          483 |
| basis\|taker_flow            |          418 |
| age\|regime                  |          341 |
| regime\|taker_flow           |          283 |
| age_vol\|positioning         |          252 |
| age\|taker_flow              |          231 |
| coverage\|positioning        |          205 |
| regime\|regime               |          201 |
| basis\|coverage              |          148 |
| coverage\|open_interest      |          135 |
| age_vol\|basis               |          134 |
| age_vol\|open_interest       |          125 |
| age\|age                     |          116 |
| age_vol\|regime              |           98 |
| taker_flow\|taker_flow       |           84 |
| coverage\|regime             |           82 |
| age\|age_vol                 |           68 |
| age\|coverage                |           56 |
| age_vol\|taker_flow          |           53 |
| coverage\|taker_flow         |           42 |
| age_vol\|coverage            |           17 |
| coverage\|coverage           |            4 |
| age_vol\|age_vol             |            1 |

## Motif Summary

| motif                        |   queue_rows |
|:-----------------------------|-------------:|
| raw_signed_mul               |         3533 |
| raw_safe_div_abs             |         3508 |
| raw_spread_rank              |         3466 |
| raw_mul                      |         3461 |
| raw_state_gate               |          700 |
| raw_state_relative           |          695 |
| raw_same_semantic_spread     |          571 |
| raw_basis_oi_scaled_spread   |          267 |
| raw_oi_flow_interaction      |           96 |
| raw_basis_flow_signed_spread |           87 |

## Field Usage Summary

| field                                |   usage_rows |
|:-------------------------------------|-------------:|
| mark_index_basis_bps                 |         1303 |
| account_position_divergence          |         1292 |
| open_interest_value_change_24h       |         1282 |
| premium_close_bps                    |         1275 |
| top_long_short_account_ratio_last    |         1261 |
| premium_abs_168h                     |         1243 |
| open_interest_change_24h             |         1240 |
| taker_buy_sell_volume_ratio_mean     |         1237 |
| mark_trade_basis_bps                 |         1236 |
| open_interest_value_last             |         1236 |
| global_long_short_account_ratio_mean |         1222 |
| open_interest_last                   |         1220 |
| open_interest_mean                   |         1219 |
| basis_abs_168h                       |         1212 |
| top_long_short_account_ratio_mean    |         1212 |
| top_global_account_divergence        |         1212 |
| top_long_short_position_ratio_mean   |         1210 |
| global_long_short_account_ratio_last |         1193 |
| taker_buy_sell_volume_ratio_last     |         1186 |
| top_long_short_position_ratio_last   |         1176 |
| leverage_crowding_state              |          779 |
| liquidity_cycle_state                |          761 |
| age_x_volatility                     |          749 |
| basis_dislocation_state              |          747 |
| sqrt_listing_age_days                |          735 |
| log1p_listing_age_days               |          733 |
| stress_proxy_state                   |          730 |
| listing_age_days                     |          728 |
| market_breadth_state                 |          727 |
| age_percentile_active_universe       |          719 |
| rolling_coverage_168h                |          693 |

## Boundary

```text
This queue is numeric-probe only after field gate PASS.
It does not authorize formula search, alpha proof, shadow, paper, or live.
```
