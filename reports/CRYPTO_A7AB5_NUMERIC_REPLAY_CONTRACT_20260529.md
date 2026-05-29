# CRYPTO A7AB-5 NUMERIC REPLAY CONTRACT

Generated: 2026-05-29T06:09:16Z

## Decision

`PASS_A7AB5_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AB6_SMALL_REPLAY_PREFLIGHT`

A7AB-5 is a contract only. It authorizes a bounded A7AB-6 small numeric replay preflight and does not authorize formula search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ab6_small_numeric_replay_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB5_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AB6_SMALL_REPLAY_PREFLIGHT",
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:09:16Z",
  "input_a7ab4_decision": "PASS_A7AB4_MATERIALIZATION_PREFLIGHT_READY_FOR_A7AB5_NUMERIC_REPLAY_CONTRACT",
  "queue_count": 128,
  "queue_family_count": 4,
  "queue_seed_field_count": 5,
  "queue_skeleton_count": 58,
  "stage": "A7AB-5",
  "uses_may": false
}
```

## Replay Contract Queue Summary

| family_id                    |   queued_count |   seed_field_count |   skeleton_count |
|:-----------------------------|---------------:|-------------------:|-----------------:|
| G0_price_return_reversal     |             32 |                  1 |               24 |
| G1_volatility_state_reversal |             32 |                  2 |               21 |
| G2_basis_premium_dislocation |             38 |                  2 |               22 |
| G3_seed_pair_interaction     |             26 |                  4 |               26 |

## Label Contract

| label_family                       | horizons_h   | primary   |
|:-----------------------------------|:-------------|:----------|
| L7_ranked_future_return            | 1\|4         | True      |
| L1_cross_sectional_relative_return | 1\|4         | False     |
| L0_raw_forward_return              | 1            | False     |

## Control Contract

| control             | required   | failure_if                                         |
|:--------------------|:-----------|:---------------------------------------------------|
| one_bar_lag         | True       | candidate collapses under field-native one-bar lag |
| wrong_lag_future_1h | True       | control ratio >= 1.0                               |
| wrong_lag_stale_24h | True       | control ratio >= 1.0                               |
| time_shuffle        | True       | control ratio >= 1.0                               |
| symbol_shuffle      | True       | control ratio >= 1.0                               |
| same_family_random  | True       | control ratio >= 1.0                               |

## Pass Gates

| gate                    | rule                                                                         |
|:------------------------|:-----------------------------------------------------------------------------|
| pre_may_split_stability | validation/test/recent oriented spread positive                              |
| control_dominance       | matched control ratio < 1.0 in every pre-May split                           |
| nonoverlap_stats        | 24h non-overlap min/median stats reported; naive hourly tstat not sufficient |
| latency                 | field-native one-bar lag must survive; no artificial +2h policy              |
| cost_proxy              | 2bps/5bps/10bps proxy reported                                               |
| diversity               | no single family > 35%, no single skeleton > 15%, no single seed field > 25% |
| no_may                  | May not used in score, selector, threshold, replay ranking, or mutation      |

## Queue Sample

|   replay_contract_rank | candidate_id           | family_id                    | primary_seed_field   | motif                   |   finite_share |   nonzero_share | expression                                                                                                               |
|-----------------------:|:-----------------------|:-----------------------------|:---------------------|:------------------------|---------------:|----------------:|:-------------------------------------------------------------------------------------------------------------------------|
|                      1 | a7ab3_1bbac777d8c7cece | G0_price_return_reversal     | trade_return_1h      | winsor_atom             |       0.999512 |               1 | Winsor(Clip(ZScore(trade_return_1h),-3,3),3)                                                                             |
|                      2 | a7ab3_2f3b0f69f16a25fb | G0_price_return_reversal     | trade_return_1h      | single_atom             |       0.999512 |               1 | Rank(trade_return_1h)                                                                                                    |
|                      3 | a7ab3_3b8e498a22c42cbc | G0_price_return_reversal     | trade_return_1h      | rank_atom               |       0.999512 |               1 | Rank(ZScore(trade_return_1h))                                                                                            |
|                      4 | a7ab3_711cade90871327e | G0_price_return_reversal     | trade_return_1h      | winsor_atom             |       0.999512 |               1 | Winsor(Rank(Clip(ZScore(trade_return_1h),-3,3)),3)                                                                       |
|                      5 | a7ab3_39d7d82ced61179e | G0_price_return_reversal     | trade_return_1h      | rank_atom               |       0.998291 |               1 | Rank(Clip(Delta(trade_return_1h,4),-3,3))                                                                                |
|                      6 | a7ab3_568082728e6a9609 | G0_price_return_reversal     | trade_return_1h      | rank_atom               |       0.998047 |               1 | Rank(Sub(ZScore(Mean(trade_return_1h,4)),ZScore(trade_return_1h)))                                                       |
|                      7 | a7ab3_da906fe9c76e14a5 | G0_price_return_reversal     | trade_return_1h      | single_atom             |       0.998047 |               1 | Sub(ZScore(Delta(trade_return_1h,1)),ZScore(Delta(trade_return_1h,4)))                                                   |
|                      8 | a7ab3_0492fc2dc251a963 | G0_price_return_reversal     | trade_return_1h      | winsor_atom             |       0.997559 |               1 | Winsor(ZScore(Decay(Delta(trade_return_1h,1),4)),3)                                                                      |
|                      9 | a7ab3_ab7fdd25b4c75562 | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.997559 |               1 | ZScore(Mul(ZScore(Winsor(Delta(trade_return_1h,1),3)),ZScore(Decay(Delta(trade_return_1h,1),4))))                        |
|                     10 | a7ab3_dc44afc5259ccc05 | G0_price_return_reversal     | trade_return_1h      | clip_horizon_spread     |       0.997559 |               1 | Clip(Sub(Mul(Decay(trade_return_1h,4),ZScore(Delta(trade_return_1h,4))),ZScore(trade_return_1h)),-3,3)                   |
|                     11 | a7ab3_121126912168eca3 | G0_price_return_reversal     | trade_return_1h      | rank_atom               |       0.994141 |               1 | Rank(Sub(Rank(Decay(trade_return_1h,12)),Rank(Decay(trade_return_1h,4))))                                                |
|                     12 | a7ab3_1586b50c1584aab2 | G0_price_return_reversal     | trade_return_1h      | horizon_spread          |       0.994141 |               1 | Sub(Delta(trade_return_1h,1),ZScore(Sub(Decay(trade_return_1h,4),Decay(trade_return_1h,12))))                            |
|                     13 | a7ab3_53755de12a280dc9 | G0_price_return_reversal     | trade_return_1h      | decay_atom              |       0.994141 |               1 | Decay(Rank(Winsor(ZScore(trade_return_1h),3)),12)                                                                        |
|                     14 | a7ab3_6e1f02f64d66b106 | G0_price_return_reversal     | trade_return_1h      | single_atom             |       0.994141 |               1 | ZScore(Sub(Decay(trade_return_1h,4),Decay(trade_return_1h,12)))                                                          |
|                     15 | a7ab3_742a4e43e745fd41 | G0_price_return_reversal     | trade_return_1h      | horizon_spread          |       0.994141 |               1 | Sub(Delta(trade_return_1h,1),ZScore(Sub(Decay(trade_return_1h,12),Decay(trade_return_1h,4))))                            |
|                     16 | a7ab3_92f58128176f656c | G0_price_return_reversal     | trade_return_1h      | clip_horizon_spread     |       0.994141 |               1 | Clip(Sub(Mul(Decay(trade_return_1h,12),ZScore(Delta(trade_return_1h,4))),ZScore(trade_return_1h)),-3,3)                  |
|                     17 | a7ab3_b32904f3e48a1c9f | G0_price_return_reversal     | trade_return_1h      | decay_atom              |       0.994141 |               1 | Decay(Winsor(ZScore(trade_return_1h),3),12)                                                                              |
|                     18 | a7ab3_4092255ee6888704 | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.993896 |               1 | ZScore(Mul(Mul(TSRank(trade_return_1h,168),ZScore(Mean(trade_return_1h,168))),Rank(Clip(ZScore(trade_return_1h),-3,3)))) |
|                     19 | a7ab3_ced6188c184ada50 | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.993896 |               1 | ZScore(Mul(Mul(TSRank(trade_return_1h,72),ZScore(Mean(trade_return_1h,168))),Rank(Clip(ZScore(trade_return_1h),-3,3))))  |
|                     20 | a7ab3_03c8dd1e0f1406bb | G0_price_return_reversal     | trade_return_1h      | winsor_atom             |       0.993652 |               1 | Winsor(ZScore(Decay(Delta(trade_return_1h,1),12)),3)                                                                     |
|                     21 | a7ab3_b34ecf60d22e6849 | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.993652 |               1 | ZScore(Mul(ZScore(Winsor(Delta(trade_return_1h,1),3)),ZScore(Decay(Delta(trade_return_1h,1),12))))                       |
|                     22 | a7ab3_09c000b24485330c | G0_price_return_reversal     | trade_return_1h      | zscore_atom             |       0.993408 |               1 | ZScore(Mul(Rank(trade_return_1h),ZScore(Delta(trade_return_1h,24))))                                                     |
|                     23 | a7ab3_7fa990b397bb88bd | G0_price_return_reversal     | trade_return_1h      | zscore_atom             |       0.993408 |               1 | ZScore(Winsor(Delta(trade_return_1h,24),3))                                                                              |
|                     24 | a7ab3_ac1d320447cdc0e1 | G0_price_return_reversal     | trade_return_1h      | single_atom             |       0.993164 |               1 | Sub(ZScore(Delta(trade_return_1h,1)),ZScore(Delta(trade_return_1h,24)))                                                  |
|                     25 | a7ab3_1615f89091205d2b | G0_price_return_reversal     | trade_return_1h      | winsor_self_interaction |       0.992676 |               1 | Winsor(Mul(Decay(ZScore(trade_return_1h),4),Mul(Rank(Mean(trade_return_1h,72)),ZScore(Delta(trade_return_1h,24)))),3)    |
|                     26 | a7ab3_1f806f028de41c42 | G0_price_return_reversal     | trade_return_1h      | rank_horizon_spread     |       0.992676 |               1 | Rank(Sub(Rank(Delta(trade_return_1h,24)),Decay(ZScore(trade_return_1h),4)))                                              |
|                     27 | a7ab3_468df1ab66c1556f | G0_price_return_reversal     | trade_return_1h      | clip_horizon_spread     |       0.992676 |               1 | Clip(Sub(TSRank(Delta(trade_return_1h,4),168),Clip(Delta(trade_return_1h,4),-3,3)),-3,3)                                 |
|                     28 | a7ab3_be42b4f4a3005c27 | G0_price_return_reversal     | trade_return_1h      | winsor_self_interaction |       0.992676 |               1 | Winsor(Mul(Sub(ZScore(Mean(trade_return_1h,168)),ZScore(Mean(trade_return_1h,4))),Rank(Delta(trade_return_1h,24))),3)    |
|                     29 | a7ab3_fb7800c317573c85 | G0_price_return_reversal     | trade_return_1h      | clip_horizon_spread     |       0.992676 |               1 | Clip(Sub(TSRank(Delta(trade_return_1h,4),72),Clip(Delta(trade_return_1h,4),-3,3)),-3,3)                                  |
|                     30 | a7ab3_c96b6ce75090d30c | G0_price_return_reversal     | trade_return_1h      | clip_horizon_spread     |       0.992188 |               1 | Clip(Sub(ZScore(Delta(Mean(trade_return_1h,168),4)),Sub(ZScore(Mean(trade_return_1h,4)),ZScore(trade_return_1h))),-3,3)  |
|                     31 | a7ab3_2408450b6a3804c1 | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.991211 |               1 | ZScore(Mul(ZScore(Mean(trade_return_1h,168)),Sub(Decay(trade_return_1h,4),Decay(trade_return_1h,12))))                   |
|                     32 | a7ab3_5c25aa55f36a3ebc | G0_price_return_reversal     | trade_return_1h      | zscore_self_interaction |       0.991211 |               1 | ZScore(Mul(ZScore(Mean(trade_return_1h,168)),Sub(Decay(trade_return_1h,12),Decay(trade_return_1h,4))))                   |
|                     33 | a7ab3_3ce43ff8d3208a0f | G1_volatility_state_reversal | realized_vol_24h     | decay_atom              |       0.855713 |               1 | Decay(Mean(Delta(realized_vol_24h,4),72),12)                                                                             |
|                     34 | a7ab3_2af478d1ff284e21 | G1_volatility_state_reversal | realized_vol_168h    | winsor_atom             |       0.853271 |               1 | Winsor(Rank(Clip(ZScore(realized_vol_168h),-3,3)),3)                                                                     |
|                     35 | a7ab3_3edc6f38cc9be3f3 | G1_volatility_state_reversal | realized_vol_168h    | single_atom             |       0.853271 |               1 | Rank(realized_vol_168h)                                                                                                  |
|                     36 | a7ab3_6e301587da1c1fa3 | G1_volatility_state_reversal | realized_vol_24h     | rank_atom               |       0.853271 |               1 | Rank(ZScore(realized_vol_24h))                                                                                           |
|                     37 | a7ab3_da7270f10c2caee8 | G1_volatility_state_reversal | realized_vol_168h    | winsor_atom             |       0.853271 |               1 | Winsor(Clip(ZScore(realized_vol_168h),-3,3),3)                                                                           |
|                     38 | a7ab3_8c5b70787959de8b | G1_volatility_state_reversal | realized_vol_24h     | rank_atom               |       0.852539 |               1 | Rank(Sub(ZScore(Mean(realized_vol_24h,4)),ZScore(realized_vol_24h)))                                                     |
|                     39 | a7ab3_d4939ee84cb32793 | G1_volatility_state_reversal | realized_vol_24h     | clip_atom               |       0.852539 |               1 | Clip(Decay(realized_vol_24h,4),-3,3)                                                                                     |
|                     40 | a7ab3_165c7d8966b27a17 | G1_volatility_state_reversal | realized_vol_168h    | winsor_atom             |       0.852295 |               1 | Winsor(ZScore(Decay(Delta(realized_vol_168h,1),4)),3)                                                                    |
