# CRYPTO A7LS-13 CONSOLIDATION REPLAY PACKET

Generated: 2026-06-06T03:10:21Z

## Decision

`PASS_A7LS13_CONSOLIDATED_REPLAY_PACKET_READY_NO_SEARCH_AUTH`

## Summary

- input_non_l7_clue_rows: 244
- candidate_level_rows: 31
- priority_multi_label_rows: 11
- multi_label_control_clean_rows: 11
- replay_packet_rows: 25
- packet_source_axis_count: 4
- packet_next_wave_family_count: 7
- packet_label_bundle_count: 5

A7LS-13 consolidates full-timestamp A7LS-12 non-L7 clue rows to candidate-level replay packets. It removes duplicate label/horizon rows from the same formula and applies axis/family/skeleton caps.

## Consolidation Status

| consolidation_status      |   candidate_rows |
|:--------------------------|-----------------:|
| candidate_level_clue      |                9 |
| multi_label_control_clean |               11 |
| priority_multi_label      |               11 |

## Packet By Source Axis

| source_info_axis       |   packet_rows |
|:-----------------------|--------------:|
| listing_x_basis_regime |             2 |
| positioning_x_basis    |             3 |
| raw_multi_axis         |             6 |
| vol_liquidity_x_basis  |            14 |

## Packet By Next Wave Family

| next_wave_family                |   packet_rows |
|:--------------------------------|--------------:|
| basis_context_interaction       |             4 |
| listing_state_interaction       |             2 |
| positioning_context_interaction |             2 |
| positioning_flow_recovery       |             1 |
| raw_multi_axis_probe            |             6 |
| vol_liquidity_deep              |             2 |
| vol_liquidity_interaction       |             8 |

## Packet By Label Bundle

| label_families                                                                                                    |   packet_rows |
|:------------------------------------------------------------------------------------------------------------------|--------------:|
| L0_raw_forward_return;L1_cross_sectional_relative_return                                                          |             9 |
| L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        |            10 |
| L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return |             1 |
| L3_liquidity_tier_relative_return                                                                                 |             3 |
| L5_vol_adjusted_return                                                                                            |             2 |

## Top Replay Packet

|   a7ls13_packet_rank | blueprint_id           | source_info_axis       | next_wave_family                | label_families                                                                                                    | horizons   |   min_control_ratio |   candidate_score |
|---------------------:|:-----------------------|:-----------------------|:--------------------------------|:------------------------------------------------------------------------------------------------------------------|:-----------|--------------------:|------------------:|
|                    1 | a7ls9_13b0747d7cd8a637 | raw_multi_axis         | raw_multi_axis_probe            | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return | 1;4;8;24   |            0.442625 |           636.84  |
|                    2 | a7ls9_db1bf403691c180d | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 1;4;8;24   |            0.631962 |           431.299 |
|                    3 | a7ls9_d7a773685af27a8b | raw_multi_axis         | raw_multi_axis_probe            | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 4;8;24     |            0.491259 |           429.738 |
|                    4 | a7ls9_0c00218805a15710 | vol_liquidity_x_basis  | basis_context_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 4;8;24     |            0.700623 |           420.113 |
|                    5 | a7ls9_a5baef25254e750a | raw_multi_axis         | raw_multi_axis_probe            | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 4;8;24     |            0.708683 |           410.926 |
|                    6 | a7ls9_9060064e491093b0 | raw_multi_axis         | raw_multi_axis_probe            | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 4;8        |            0.562842 |           402.556 |
|                    7 | a7ls9_164ffbbc7312fdc6 | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 4;8;24     |            0.777946 |           400.371 |
|                    8 | a7ls9_f131878ada5f7bdb | vol_liquidity_x_basis  | basis_context_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 24         |            0.482738 |           400.142 |
|                    9 | a7ls9_1d98ff9117e75a6f | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 8;24       |            0.660594 |           394.382 |
|                   10 | a7ls9_a86ac02d201ae3f4 | listing_x_basis_regime | listing_state_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 24         |            0.640914 |           382.413 |
|                   11 | a7ls9_b627111b0d3434a7 | vol_liquidity_x_basis  | basis_context_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return                        | 24         |            0.705567 |           379.923 |
|                   12 | a7ls9_b45bcf9f12dbe4c1 | listing_x_basis_regime | listing_state_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 4;8;24     |            0.703217 |           318.908 |
|                   13 | a7ls9_606d17a2011da024 | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 4;8;24     |            0.686823 |           316.721 |
|                   14 | a7ls9_a2eab9873da00d14 | raw_multi_axis         | raw_multi_axis_probe            | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 4;8;24     |            0.74064  |           298.276 |
|                   15 | a7ls9_516eed52d75aa727 | vol_liquidity_x_basis  | vol_liquidity_deep              | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 4;8;24     |            0.801727 |           296.935 |
|                   16 | a7ls9_37dceefef1275afb | vol_liquidity_x_basis  | vol_liquidity_deep              | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 8;24       |            0.68998  |           293.108 |
|                   17 | a7ls9_027c5a5ab9db998a | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 24         |            0.617802 |           280.036 |
|                   18 | a7ls9_5643d6073296ae92 | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 24         |            0.63422  |           277.799 |
|                   19 | a7ls9_b0eee4793300a610 | positioning_x_basis    | positioning_context_interaction | L5_vol_adjusted_return                                                                                            | 24         |            0.968478 |           268.083 |
|                   20 | a7ls9_f39b206ab8e2b215 | vol_liquidity_x_basis  | basis_context_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 24         |            0.856433 |           251.963 |
|                   21 | a7ls9_af5e4ea972785e6c | vol_liquidity_x_basis  | vol_liquidity_interaction       | L0_raw_forward_return;L1_cross_sectional_relative_return                                                          | 4          |            0.998135 |           225.813 |
|                   22 | a7ls9_877419e7f0b8bf0e | positioning_x_basis    | positioning_flow_recovery       | L3_liquidity_tier_relative_return                                                                                 | 24         |            0.205946 |           212.901 |
|                   23 | a7ls9_ffe3eb90cbdae18a | raw_multi_axis         | raw_multi_axis_probe            | L5_vol_adjusted_return                                                                                            | 1          |            0.556457 |           206.175 |
|                   24 | a7ls9_1920f31cd91f269e | vol_liquidity_x_basis  | vol_liquidity_interaction       | L3_liquidity_tier_relative_return                                                                                 | 24         |            0.61388  |           169.196 |
|                   25 | a7ls9_982bcce5eed1ffc6 | positioning_x_basis    | positioning_context_interaction | L3_liquidity_tier_relative_return                                                                                 | 24         |            0.781603 |           165.665 |

## Authorization

- A7LS-14 replay contract: authorized
- new generation / large search / alpha proof / shadow / paper / live: not authorized
