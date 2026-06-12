# CRYPTO A7V3S0 Next Large Search Contract 20260613

## Decision

`PASS_A7V3S0_NEXT_LARGE_SEARCH_CONTRACT_READY_NOT_LAUNCHED`

A7V3S0 defines the next large search as a v3-panel-native numeric probe. It does not reuse the old accepted queue as a seed because the v3 reward smoke rejected it. The queue is broad enough for system validation, but it remains gated: materialization first, then reward gate, then only accepted outputs may feed the next stage.

## Counts

- queue_rows: `65536`
- shard_count: `64`
- rows_per_shard: `1024`
- v3_panel_root: `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613`
- guard_decision: `PASS_A7GUARD0_PRESEARCH_GUARD_READY`
- regime_decision: `PASS_A7REGIME2_MECHANISM_REGIME_CANDIDATES_FOUND`
- reward_smoke_decision: `HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED`
- reward_smoke_accepted_rows: `0`

## Lane Summary

| a7v3s0_lane                  |   rows |
|:-----------------------------|-------:|
| funding_basis_recent_robust  |  16384 |
| mechanism_regime_conditioned |  16384 |
| oi_flow_cross_mechanism      |  16384 |
| raw_broad_reserved           |  16384 |

## Semantic Pair Summary

| a7v3s0_lane                  | semantic_pair                 |   rows |
|:-----------------------------|:------------------------------|-------:|
| oi_flow_cross_mechanism      | open_interest|positioning     |   6735 |
| funding_basis_recent_robust  | funding_dense|open_interest   |   6129 |
| oi_flow_cross_mechanism      | open_interest|taker_flow      |   4175 |
| oi_flow_cross_mechanism      | open_interest|premium         |   2756 |
| oi_flow_cross_mechanism      | basis|open_interest           |   2718 |
| funding_basis_recent_robust  | basis|funding_dense           |   2435 |
| funding_basis_recent_robust  | funding_dense|premium         |   2426 |
| mechanism_regime_conditioned | positioning|regime            |   1994 |
| mechanism_regime_conditioned | open_interest|regime          |   1878 |
| mechanism_regime_conditioned | age|open_interest             |   1557 |
| mechanism_regime_conditioned | age|positioning               |   1530 |
| funding_basis_recent_robust  | funding_sparse|open_interest  |   1484 |
| funding_basis_recent_robust  | funding_basis|open_interest   |   1465 |
| raw_broad_reserved           | funding_dense|positioning     |   1289 |
| mechanism_regime_conditioned | funding_dense|regime          |   1234 |
| raw_broad_reserved           | positioning|taker_flow        |   1195 |
| mechanism_regime_conditioned | regime|taker_flow             |   1183 |
| mechanism_regime_conditioned | age|taker_flow                |   1017 |
| mechanism_regime_conditioned | age|funding_dense             |    961 |
| raw_broad_reserved           | positioning|positioning       |    958 |
| raw_broad_reserved           | open_interest|open_interest   |    901 |
| mechanism_regime_conditioned | premium|regime                |    820 |
| raw_broad_reserved           | liquidity|open_interest       |    812 |
| raw_broad_reserved           | basis|positioning             |    784 |
| raw_broad_reserved           | funding_dense|taker_flow      |    776 |
| mechanism_regime_conditioned | basis|regime                  |    743 |
| raw_broad_reserved           | positioning|premium           |    721 |
| raw_broad_reserved           | liquidity|positioning         |    699 |
| mechanism_regime_conditioned | age|basis                     |    662 |
| funding_basis_recent_robust  | funding_basis|premium         |    644 |
| funding_basis_recent_robust  | funding_sparse|premium        |    609 |
| mechanism_regime_conditioned | age|premium                   |    604 |
| funding_basis_recent_robust  | basis|funding_basis           |    601 |
| funding_basis_recent_robust  | basis|funding_sparse          |    591 |
| raw_broad_reserved           | age|regime                    |    547 |
| raw_broad_reserved           | liquidity|taker_flow          |    498 |
| raw_broad_reserved           | funding_dense|liquidity       |    479 |
| raw_broad_reserved           | liquidity|regime              |    462 |
| raw_broad_reserved           | basis|taker_flow              |    440 |
| raw_broad_reserved           | premium|taker_flow            |    435 |
| mechanism_regime_conditioned | positioning|universe_state    |    413 |
| mechanism_regime_conditioned | open_interest|universe_state  |    385 |
| raw_broad_reserved           | funding_dense|funding_dense   |    368 |
| raw_broad_reserved           | age|liquidity                 |    339 |
| raw_broad_reserved           | liquidity|premium             |    323 |
| raw_broad_reserved           | funding_sparse|positioning    |    321 |
| raw_broad_reserved           | taker_flow|taker_flow         |    313 |
| raw_broad_reserved           | basis|premium                 |    305 |
| mechanism_regime_conditioned | funding_basis|regime          |    304 |
| raw_broad_reserved           | funding_basis|positioning     |    304 |
| raw_broad_reserved           | basis|liquidity               |    300 |
| raw_broad_reserved           | regime|regime                 |    282 |
| mechanism_regime_conditioned | taker_flow|universe_state     |    255 |
| mechanism_regime_conditioned | age|funding_basis             |    245 |
| mechanism_regime_conditioned | funding_dense|universe_state  |    245 |
| raw_broad_reserved           | funding_dense|funding_sparse  |    226 |
| raw_broad_reserved           | funding_basis|funding_dense   |    205 |
| raw_broad_reserved           | funding_sparse|regime         |    200 |
| raw_broad_reserved           | funding_sparse|taker_flow     |    193 |
| raw_broad_reserved           | funding_basis|taker_flow      |    187 |
| raw_broad_reserved           | age|age                       |    174 |
| raw_broad_reserved           | age|funding_sparse            |    168 |
| mechanism_regime_conditioned | premium|universe_state        |    155 |
| raw_broad_reserved           | regime|universe_state         |    149 |
| raw_broad_reserved           | funding_basis|liquidity       |    142 |
| raw_broad_reserved           | funding_sparse|liquidity      |    142 |
| mechanism_regime_conditioned | basis|universe_state          |    141 |
| raw_broad_reserved           | premium|premium               |    139 |
| raw_broad_reserved           | liquidity|liquidity           |    136 |
| raw_broad_reserved           | basis|basis                   |    119 |
| raw_broad_reserved           | age|universe_state            |    115 |
| raw_broad_reserved           | liquidity|universe_state      |    102 |
| mechanism_regime_conditioned | funding_basis|universe_state  |     58 |
| raw_broad_reserved           | funding_basis|funding_sparse  |     56 |
| raw_broad_reserved           | funding_sparse|universe_state |     28 |
| raw_broad_reserved           | funding_sparse|funding_sparse |     25 |
| raw_broad_reserved           | funding_basis|funding_basis   |     19 |
| raw_broad_reserved           | universe_state|universe_state |      8 |

## Motif Summary

| a7v3s0_lane                  | motif                      |   rows |
|:-----------------------------|:---------------------------|-------:|
| raw_broad_reserved           | signed_rank_gate           |   4146 |
| raw_broad_reserved           | safe_div_abs               |   4084 |
| raw_broad_reserved           | smooth_mul                 |   4082 |
| funding_basis_recent_robust  | safe_div_abs               |   4080 |
| raw_broad_reserved           | spread_rank                |   4072 |
| funding_basis_recent_robust  | smooth_mul                 |   4056 |
| funding_basis_recent_robust  | spread_rank                |   4056 |
| funding_basis_recent_robust  | signed_rank_gate           |   3976 |
| oi_flow_cross_mechanism      | signed_rank_gate           |   3350 |
| oi_flow_cross_mechanism      | smooth_mul                 |   3294 |
| oi_flow_cross_mechanism      | safe_div_abs               |   3226 |
| oi_flow_cross_mechanism      | oi_flow_scaled_spread      |   3217 |
| oi_flow_cross_mechanism      | spread_rank                |   3177 |
| mechanism_regime_conditioned | state_conditioned_signed   |   2802 |
| mechanism_regime_conditioned | state_conditioned_rank_mul |   2759 |
| mechanism_regime_conditioned | smooth_mul                 |   2747 |
| mechanism_regime_conditioned | spread_rank                |   2740 |
| mechanism_regime_conditioned | safe_div_abs               |   2671 |
| mechanism_regime_conditioned | signed_rank_gate           |   2665 |
| oi_flow_cross_mechanism      | oi_flow_delta_rank         |    120 |
| funding_basis_recent_robust  | funding_basis_delta_sign   |    108 |
| funding_basis_recent_robust  | funding_basis_spread_24h   |    108 |

## Field Usage Summary

| field                                |   usage_rows |
|:-------------------------------------|-------------:|
| open_interest_last                   |         6449 |
| open_interest_value_change_24h       |         6410 |
| open_interest_value_last             |         6388 |
| open_interest_value_mean             |         6358 |
| open_interest_mean                   |         6291 |
| premium_abs_state                    |         5049 |
| premium_close_bps                    |         5027 |
| mark_trade_basis_bps                 |         4991 |
| mark_index_basis_bps                 |         4967 |
| funding_rate_state_last_ffill_8h     |         4327 |
| funding_rate_delta_state_24h         |         4320 |
| funding_rate_update_age_hours        |         4278 |
| funding_state_x_basis_delta          |         4249 |
| funding_rate_abs_state_168h_z        |         4216 |
| funding_rate                         |         4068 |
| taker_buy_sell_volume_ratio_last     |         3681 |
| kline_taker_buy_quote_share          |         3674 |
| top_global_account_divergence        |         3643 |
| taker_buy_sell_volume_ratio_mean     |         3625 |
| global_long_short_account_ratio_last |         3595 |
| account_position_divergence          |         3583 |
| top_long_short_position_ratio_last   |         3552 |
| top_long_short_account_ratio_last    |         3528 |
| trade_quote_volume                   |         2292 |
| quote_volume_z_168h                  |         2278 |
| log1p_listing_age_days               |         2084 |
| active_universe_size                 |         2062 |
| liquidity_cycle_state                |         2060 |
| stress_proxy_state                   |         2022 |
| listing_age_days                     |         2020 |
| market_breadth_state                 |         2016 |
| age_percentile_active_universe       |         2011 |
| leverage_crowding_state              |         2001 |
| basis_dislocation_state              |         1979 |
| sqrt_listing_age_days                |         1978 |

## Operating Rules

- Use v3 panel only: `binance_universe498_replay_1h_v3_patch_age_20260613`.
- Do not consume old accepted queue as seed; it is now a diagnostic negative control.
- Do not claim best/alpha from materialization metrics; reward gate must write accepted/rejected queue.
- Reject any candidate dominated by shuffle/wrong-lag/control or non-overlap floor failures.
- Keep one lane as raw broad search, but keep semantic/skeleton/field caps active.
- Final proof remains blocked until checksum/source trace audit.