# CRYPTO A7FF-19 EXTERNAL SELECTOR CONFIRMATION CONTRACT

Generated: 2026-05-30T05:02:53Z

## Decision

`PASS_A7FF19_EXTERNAL_SELECTOR_CONFIRMATION_CONTRACT_READY_FOR_COMPANY_EXECUTION`

A7FF-19 converts the A7FF-18 external label-balanced selected queue into a unique-blueprint execution queue for company-machine numeric confirmation. It does not execute replay in this stage; it only authorizes a bounded company run through the existing A7FF-8 numeric runner.

## Manifest

```json
{
  "a7ff18_selected_rows": 80,
  "authorizes_alpha_proof": false,
  "authorizes_company_numeric_execution": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "cost5_or_better_execution_blueprints": 56,
  "decision": "PASS_A7FF19_EXTERNAL_SELECTOR_CONFIRMATION_CONTRACT_READY_FOR_COMPANY_EXECUTION",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "execution_blueprints": 56,
  "generated_at": "2026-05-30T05:02:53Z",
  "source_a7ff18_decision": "PASS_A7FF18_EXTERNAL_LABEL_BALANCED_SELECTOR_READY_FOR_A7FF19",
  "stage": "A7FF-19-EXTERNAL-SELECTOR-CONFIRMATION-CONTRACT",
  "strict_cost10_execution_blueprints": 35,
  "top_motif_share": 0.30357142857142855,
  "top_semantic_share": 0.35714285714285715,
  "uses_may": false
}
```

## Runner Config

```json
{
  "fast_numeric_cap_per_shard": 28,
  "file_prefix": "a7ff19s",
  "materialize_cap_per_shard": 28,
  "portfolio_cap_per_shard": 128,
  "queue_local_path": "runtime\\a7ff19_external_selector_confirmation_contract\\a7ff19_execution_queue.csv",
  "queue_remote_path": "runtime\\a7ff19_external_selector_confirmation_contract\\a7ff19_execution_queue.csv",
  "recommended_max_parallel": 2,
  "recommended_shard_count": 2,
  "recommended_shard_size": 28,
  "remote_base_panel": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "remote_data_root": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData",
  "remote_python": "D:\\HermesWorker\\venvs\\phase3z33\\Scripts\\python.exe",
  "remote_repo": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote",
  "runner_script": "scripts\\crypto_a7ff8_expanded_numeric_probe.py",
  "stage_prefix": "A7FF-19S"
}
```

## Label Target Summary

| label_family                       | cost_tier      |   rows |   unique_blueprints |
|:-----------------------------------|:---------------|-------:|--------------------:|
| L0_raw_forward_return              | cost5_followup |      9 |                   9 |
| L0_raw_forward_return              | strict_cost10  |     11 |                  11 |
| L1_cross_sectional_relative_return | cost5_followup |     10 |                  10 |
| L1_cross_sectional_relative_return | strict_cost10  |     10 |                  10 |
| L3_liquidity_tier_relative_return  | cost5_followup |     20 |                  20 |
| L5_vol_adjusted_return             | strict_cost10  |     20 |                  20 |

## Execution Semantic Summary

| semantic_pair                          |   execution_blueprints |
|:---------------------------------------|-----------------------:|
| basis_premium_like\|positioning_like   |                     20 |
| basis_premium_like\|basis_premium_like |                     17 |
| basis_premium_like\|volatility_like    |                     15 |
| basis_premium_like\|price_like         |                      4 |

## Execution Motif Summary

| motif              |   execution_blueprints |
|:-------------------|-----------------------:|
| safe_div_abs       |                     17 |
| sub                |                     16 |
| spread_rank        |                      8 |
| mul                |                      8 |
| gated_sign         |                      6 |
| smooth_interaction |                      1 |

## Execution Queue Preview

| blueprint_id            | expression                                                                                                        | semantic_pair                          | motif              | skeleton_key          |   a7ff18_selected_rows | a7ff18_label_targets                                                 | a7ff18_horizon_targets   |   a7ff18_best_tier_rank |   a7ff18_best_selector_score | a7ff18_any_strict_cost10   | a7ff18_any_cost5_or_better   |
|:------------------------|:------------------------------------------------------------------------------------------------------------------|:---------------------------------------|:-------------------|:----------------------|-----------------------:|:---------------------------------------------------------------------|:-------------------------|------------------------:|-----------------------------:|:---------------------------|:-----------------------------|
| a7ff7e_2c50d60ccb24722c | Sub(Delta(mark_index_basis_bps,12),Delta(realized_vol_168h,24))                                                   | basis_premium_like\|volatility_like    | sub                | skel_8727d93aac220fc6 |                      2 | L3_liquidity_tier_relative_return;L5_vol_adjusted_return             | 1;8                      |                       3 |                     698.931  | True                       | True                         |
| a7ff7e_3f3c420268049cb3 | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(CSRank(mark_trade_basis_bps)))                                  | basis_premium_like\|basis_premium_like | spread_rank        | skel_9505754fb4b5368b |                      1 | L5_vol_adjusted_return                                               | 8                        |                       3 |                     614.899  | True                       | True                         |
| a7ff7e_b38081e93d4f200f | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(mark_trade_basis_bps))                                          | basis_premium_like\|basis_premium_like | spread_rank        | skel_51c2bb588b20fa9e |                      1 | L5_vol_adjusted_return                                               | 8                        |                       3 |                     614.899  | True                       | True                         |
| a7ff7e_77104f0e768df207 | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Clip(ZScore(mark_trade_basis_bps),-3,3)))                       | basis_premium_like\|basis_premium_like | spread_rank        | skel_00fa107e5b1b71eb |                      1 | L5_vol_adjusted_return                                               | 8                        |                       3 |                     613.813  | True                       | True                         |
| a7ff7e_e76bd3133ec25361 | Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))                           | basis_premium_like\|positioning_like   | sub                | skel_fb9325ceddb1ac6f |                      2 | L3_liquidity_tier_relative_return;L5_vol_adjusted_return             | 1;4                      |                       3 |                     495.345  | True                       | True                         |
| a7ff7e_f93323f3cf580b67 | Mul(Delta(mark_index_basis_bps,12),taker_buy_sell_volume_ratio_last)                                              | basis_premium_like\|positioning_like   | mul                | skel_0994b3a36a4d53ba |                      1 | L5_vol_adjusted_return                                               | 4                        |                       3 |                     435.126  | True                       | True                         |
| a7ff7e_6318fc22f34b1456 | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Delta(premium_close_bps,12)))                                   | basis_premium_like\|basis_premium_like | spread_rank        | skel_bcb165b7818f5d85 |                      1 | L5_vol_adjusted_return                                               | 8                        |                       3 |                     339.74   | True                       | True                         |
| a7ff7e_49154ed0f73733d8 | Mul(Delta(mark_index_basis_bps,1),realized_vol_24h)                                                               | basis_premium_like\|volatility_like    | mul                | skel_0994b3a36a4d53ba |                      2 | L3_liquidity_tier_relative_return;L5_vol_adjusted_return             | 4;8                      |                       3 |                     294.766  | True                       | True                         |
| a7ff7e_e0cb06581d22fb61 | Sub(mark_index_basis_bps,Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3))                                     | basis_premium_like\|positioning_like   | sub                | skel_593666ed3f85046b |                      2 | L3_liquidity_tier_relative_return;L5_vol_adjusted_return             | 1                        |                       3 |                     245.28   | True                       | True                         |
| a7ff7e_2959fcddf1a8a931 | SafeDiv(mark_index_basis_bps,Abs(Abs(ZScore(realized_vol_24h))))                                                  | basis_premium_like\|volatility_like    | safe_div_abs       | skel_6a4becaf6b891485 |                      2 | L3_liquidity_tier_relative_return;L5_vol_adjusted_return             | 1                        |                       3 |                     240.647  | True                       | True                         |
| a7ff7e_a5d58d0a148c1372 | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(taker_buy_sell_volume_ratio_last),-3,3)))                  | basis_premium_like\|positioning_like   | safe_div_abs       | skel_6a3533b4d89c4d45 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     203.76   | True                       | True                         |
| a7ff7e_5b5909ab9ba6fc5e | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Sign(Delta(top_long_short_account_ratio_last,24))))             | basis_premium_like\|positioning_like   | spread_rank        | skel_af8c1327eb17d836 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     199.755  | True                       | True                         |
| a7ff7e_4fed0431f792f0c8 | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Sign(Delta(top_long_short_position_ratio_last,24))))            | basis_premium_like\|positioning_like   | spread_rank        | skel_af8c1327eb17d836 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     196.213  | True                       | True                         |
| a7ff7e_c0ec1785df986116 | Mul(Abs(ZScore(mark_index_basis_bps)),Delta(premium_close_bps,12))                                                | basis_premium_like\|basis_premium_like | mul                | skel_7c564c472f890218 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     183.583  | True                       | True                         |
| a7ff7e_620758ad5441a864 | Mul(Clip(ZScore(mark_index_basis_bps),-3,3),CSRank(mark_trade_basis_bps))                                         | basis_premium_like\|basis_premium_like | mul                | skel_3363cfb4025bd87d |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     176.851  | True                       | True                         |
| a7ff7e_0ebc522cfac9064b | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(premium_close_bps),-3,3)))                                 | basis_premium_like\|basis_premium_like | safe_div_abs       | skel_6a3533b4d89c4d45 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     175.712  | True                       | True                         |
| a7ff7e_a3368f0b979e0c23 | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Delta(taker_buy_sell_volume_ratio_last,12)))                           | basis_premium_like\|positioning_like   | safe_div_abs       | skel_3afee12eb6a9078f |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     167.129  | True                       | True                         |
| a7ff7e_10e4997b8ce12a81 | Mean(Mul(Delta(mark_index_basis_bps,12),CSRank(mark_trade_basis_bps)),4)                                          | basis_premium_like\|basis_premium_like | smooth_interaction | skel_1128a9bc5ebfee1a |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     161.574  | True                       | True                         |
| a7ff7e_6dd372cacc5ae787 | Sub(CSRank(mark_index_basis_bps),Delta(premium_close_bps,12))                                                     | basis_premium_like\|basis_premium_like | sub                | skel_e47b3d7310e98dd5 |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     155.769  | True                       | True                         |
| a7ff7e_600569f7d9453450 | Sub(Clip(ZScore(mark_index_basis_bps),-3,3),Delta(premium_close_bps,12))                                          | basis_premium_like\|basis_premium_like | sub                | skel_b04640f9c6171dfc |                      1 | L5_vol_adjusted_return                                               | 1                        |                       3 |                     148.287  | True                       | True                         |
| a7ff7e_0f6554ac44a17024 | Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(mark_trade_basis_bps),-3,3))                                       | basis_premium_like\|basis_premium_like | sub                | skel_fb9325ceddb1ac6f |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1;4                      |                       3 |                      22.4219 | True                       | True                         |
| a7ff7e_c879e0a27e94f6b7 | Sub(Delta(mark_index_basis_bps,12),CSRank(realized_vol_24h))                                                      | basis_premium_like\|volatility_like    | sub                | skel_136259b72205469f |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1;4                      |                       3 |                      21.9758 | True                       | True                         |
| a7ff7e_03e03bed8d34ba2e | Sub(Delta(mark_index_basis_bps,12),CSRank(mark_trade_basis_bps))                                                  | basis_premium_like\|basis_premium_like | sub                | skel_136259b72205469f |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.9086 | True                       | True                         |
| a7ff7e_89ed25c2f6fd341b | Sub(Delta(mark_index_basis_bps,12),Delta(mark_trade_basis_bps,12))                                                | basis_premium_like\|basis_premium_like | sub                | skel_8727d93aac220fc6 |                      2 | L0_raw_forward_return                                                | 1;4                      |                       3 |                      21.7503 | True                       | True                         |
| a7ff7e_31a152b5a6d123af | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(global_long_short_account_ratio_last,24))))                 | basis_premium_like\|positioning_like   | safe_div_abs       | skel_156d0fafafecde17 |                      2 | L1_cross_sectional_relative_return                                   | 1;4                      |                       3 |                      21.7132 | True                       | True                         |
| a7ff7e_81476805533d6b2f | Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(realized_vol_24h))))                                           | basis_premium_like\|volatility_like    | gated_sign         | skel_3d008dc9486239b2 |                      1 | L1_cross_sectional_relative_return                                   | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_af0cebc89db56866 | Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(mark_trade_basis_bps))))                                       | basis_premium_like\|basis_premium_like | gated_sign         | skel_3d008dc9486239b2 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_b0946aa9e40dd3c9 | Mul(Delta(mark_index_basis_bps,12),Sign(Abs(ZScore(premium_close_bps))))                                          | basis_premium_like\|basis_premium_like | gated_sign         | skel_3d008dc9486239b2 |                      1 | L1_cross_sectional_relative_return                                   | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_b5ca9f3f6b8f16d6 | Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(premium_close_bps)))                                               | basis_premium_like\|basis_premium_like | gated_sign         | skel_069f2015163fa7ef |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_f484f2e1a7036ff4 | Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(mark_trade_basis_bps)))                                            | basis_premium_like\|basis_premium_like | gated_sign         | skel_069f2015163fa7ef |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_f8a8d6cf8b654e64 | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))                     | basis_premium_like\|positioning_like   | safe_div_abs       | skel_156d0fafafecde17 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.7031 | True                       | True                         |
| a7ff7e_3a7e3ddbe5462bea | Sub(Delta(mark_index_basis_bps,12),Delta(trade_return_24h,1))                                                     | basis_premium_like\|price_like         | sub                | skel_8727d93aac220fc6 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 4                        |                       3 |                      21.6814 | True                       | True                         |
| a7ff7e_0c55e3731792d3b1 | Mul(Delta(mark_index_basis_bps,12),Sign(CSRank(trade_return_24h)))                                                | basis_premium_like\|price_like         | gated_sign         | skel_069f2015163fa7ef |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1;4                      |                       3 |                      21.6507 | True                       | True                         |
| a7ff7e_f7464aff233896c8 | Sub(Delta(mark_index_basis_bps,12),CSRank(trade_return_1h))                                                       | basis_premium_like\|price_like         | sub                | skel_136259b72205469f |                      1 | L0_raw_forward_return                                                | 4                        |                       3 |                      21.3476 | True                       | True                         |
| a7ff7e_6445196984a5b167 | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Clip(ZScore(realized_vol_168h),-3,3)))                                 | basis_premium_like\|volatility_like    | safe_div_abs       | skel_6a3533b4d89c4d45 |                      2 | L0_raw_forward_return                                                | 1;8                      |                       3 |                      20.4728 | True                       | True                         |
| a7ff7e_42b9aa89029367d2 | SafeDiv(mark_index_basis_bps,Abs(Delta(realized_vol_168h,24)))                                                    | basis_premium_like\|volatility_like    | safe_div_abs       | skel_a2f58ee62d9e7ad2 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      20.3544 | False                      | True                         |
| a7ff7e_5201f3314c5dae1a | SafeDiv(mark_index_basis_bps,Abs(Clip(ZScore(realized_vol_24h),-3,3)))                                            | basis_premium_like\|volatility_like    | safe_div_abs       | skel_1c4b9d5957f9af9c |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      20.0638 | False                      | True                         |
| a7ff7e_bddf5c5d29f96eb6 | SafeDiv(Delta(mark_index_basis_bps,12),Abs(Abs(ZScore(realized_vol_168h))))                                       | basis_premium_like\|volatility_like    | safe_div_abs       | skel_3d008dc9486239b2 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      19.5794 | False                      | True                         |
| a7ff7e_77ca3b839d710afd | Sub(CSRank(Clip(ZScore(mark_index_basis_bps),-3,3)),CSRank(Clip(ZScore(top_long_short_account_ratio_last),-3,3))) | basis_premium_like\|positioning_like   | spread_rank        | skel_3d2988e4547fbd95 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      19.1489 | False                      | True                         |
| a7ff7e_66fc9f6699584033 | SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Abs(ZScore(realized_vol_168h))))                              | basis_premium_like\|volatility_like    | safe_div_abs       | skel_79b46e3bec19bc64 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      18.8997 | False                      | True                         |
| a7ff7e_058a55fa679948ae | SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(Clip(ZScore(realized_vol_168h),-3,3)))                        | basis_premium_like\|volatility_like    | safe_div_abs       | skel_f5a350b26e95f33f |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      18.7473 | False                      | True                         |
| a7ff7e_42cf23f63bb0ad8d | Mul(CSRank(mark_index_basis_bps),CSRank(trade_return_1h))                                                         | basis_premium_like\|price_like         | mul                | skel_293cae94cfd91548 |                      2 | L0_raw_forward_return;L1_cross_sectional_relative_return             | 1                        |                       2 |                      18.0953 | False                      | True                         |
| a7ff7e_ca3c03329ffd2edb | Mul(CSRank(mark_index_basis_bps),realized_vol_24h)                                                                | basis_premium_like\|volatility_like    | mul                | skel_37ba6246678096b3 |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      18.0429 | False                      | True                         |
| a7ff7e_306cf26692372a73 | Sub(Delta(mark_index_basis_bps,12),Clip(ZScore(realized_vol_24h),-3,3))                                           | basis_premium_like\|volatility_like    | sub                | skel_fb9325ceddb1ac6f |                      2 | L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return | 1                        |                       2 |                      18.0259 | False                      | True                         |
| a7ff7e_175e58eb9e5404d5 | Sub(Delta(mark_index_basis_bps,12),taker_buy_sell_volume_ratio_last)                                              | basis_premium_like\|positioning_like   | sub                | skel_0994b3a36a4d53ba |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      17.8814 | False                      | True                         |
| a7ff7e_f05cfb85e23e4866 | Sub(Delta(mark_index_basis_bps,12),CSRank(taker_buy_sell_volume_ratio_last))                                      | basis_premium_like\|positioning_like   | sub                | skel_136259b72205469f |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      17.8643 | False                      | True                         |
| a7ff7e_72d1bbd3a38254c0 | SafeDiv(CSRank(mark_index_basis_bps),Abs(Delta(taker_buy_sell_volume_ratio_last,12)))                             | basis_premium_like\|positioning_like   | safe_div_abs       | skel_1a1b3fb29dff7328 |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      17.5291 | False                      | True                         |
| a7ff7e_e6d01e672425fc7c | SafeDiv(Clip(ZScore(mark_index_basis_bps),-3,3),Abs(CSRank(taker_buy_sell_volume_ratio_last)))                    | basis_premium_like\|positioning_like   | safe_div_abs       | skel_99250fb0b3bee329 |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      17.0724 | False                      | True                         |
| a7ff7e_ffdab637dbab0125 | SafeDiv(mark_index_basis_bps,Abs(CSRank(taker_buy_sell_volume_ratio_last)))                                       | basis_premium_like\|positioning_like   | safe_div_abs       | skel_06aed53e0aa5366a |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      16.9374 | False                      | True                         |
| a7ff7e_4e141259215570d3 | SafeDiv(Delta(mark_index_basis_bps,24),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))                     | basis_premium_like\|positioning_like   | safe_div_abs       | skel_156d0fafafecde17 |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      16.8071 | False                      | True                         |
| a7ff7e_ae49260ddd504924 | Mul(Delta(mark_index_basis_bps,12),realized_vol_24h)                                                              | basis_premium_like\|volatility_like    | mul                | skel_0994b3a36a4d53ba |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      16.6193 | False                      | True                         |
| a7ff7e_0c7cd03187d0a1be | Sub(mark_index_basis_bps,CSRank(taker_buy_sell_volume_ratio_last))                                                | basis_premium_like\|positioning_like   | sub                | skel_d9d4f69744bac825 |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      16.3194 | False                      | True                         |
| a7ff7e_3746e01233c26dfb | Mul(Delta(mark_index_basis_bps,24),realized_vol_24h)                                                              | basis_premium_like\|volatility_like    | mul                | skel_0994b3a36a4d53ba |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      16.1183 | False                      | True                         |
| a7ff7e_ddea9f3dc39ed8de | Sub(mark_index_basis_bps,taker_buy_sell_volume_ratio_last)                                                        | basis_premium_like\|positioning_like   | sub                | skel_337820bc5afcf6cc |                      1 | L3_liquidity_tier_relative_return                                    | 1                        |                       2 |                      15.4923 | False                      | True                         |
| a7ff7e_01654e884fbd77b8 | Sub(CSRank(Delta(mark_index_basis_bps,12)),CSRank(Delta(taker_buy_sell_volume_ratio_last,1)))                     | basis_premium_like\|positioning_like   | spread_rank        | skel_bcb165b7818f5d85 |                      1 | L3_liquidity_tier_relative_return                                    | 4                        |                       2 |                      14.6433 | False                      | True                         |
| a7ff7e_cf79e50562e65c3a | SafeDiv(Delta(mark_index_basis_bps,1),Abs(Sign(Delta(taker_buy_sell_volume_ratio_last,24))))                      | basis_premium_like\|positioning_like   | safe_div_abs       | skel_156d0fafafecde17 |                      1 | L3_liquidity_tier_relative_return                                    | 8                        |                       2 |                      14.0673 | False                      | True                         |

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay in this stage: `false`
- Executes search: `false`
- Authorizes company numeric confirmation only if decision PASS: `True`
- Authorizes alpha proof / shadow / paper / live: `false`
