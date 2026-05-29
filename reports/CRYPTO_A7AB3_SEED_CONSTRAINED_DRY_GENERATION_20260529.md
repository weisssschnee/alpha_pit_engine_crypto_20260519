# CRYPTO A7AB-3 SEED-CONSTRAINED DRY GENERATION

Generated: 2026-05-29T05:47:13Z

## Decision

`PASS_A7AB3_SEED_CONSTRAINED_DRY_GENERATION_READY_FOR_A7AB4_MATERIALIZATION_PREFLIGHT`

A7AB-3 generates a static formula pool from A7AB-1 primitive-response seeds. It does not run replay, search execution, training, or alpha proof.

## Manifest

```json
{
  "authorizes_a7ab4_materialization_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_fast_replay": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB3_SEED_CONSTRAINED_DRY_GENERATION_READY_FOR_A7AB4_MATERIALIZATION_PREFLIGHT",
  "executes_formula_generation": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_static_dry_generation_only": true,
  "executes_training": false,
  "generated_at": "2026-05-29T05:47:13Z",
  "generation_contract": {
    "future_deep_audit_cap_if_later_authorized": 16,
    "future_fast_replay_cap_if_later_authorized": 128,
    "generated_total_cap": 4096,
    "max_depth": 4,
    "max_interaction_nodes": 1,
    "max_per_family_share": 0.35,
    "max_per_seed_field_share": 0.25,
    "max_same_skeleton_share": 0.15,
    "min_family_count_static_queue": 3,
    "min_seed_field_count_static_queue": 5,
    "static_selected_cap": 512
  },
  "quota_summary": {
    "family_count": 4,
    "generated_total": 1855,
    "primary_seed_field_count": 5,
    "skeleton_count": 96,
    "static_selected_count": 512,
    "static_selected_family_count": 4,
    "static_selected_seed_field_count": 5,
    "static_selected_skeleton_count": 74,
    "static_top_family_share": 0.349609375,
    "static_top_seed_field_share": 0.25,
    "static_top_skeleton_share": 0.087890625,
    "unique_expression_ratio": 1.0
  },
  "stage": "A7AB-3",
  "static_validity": {
    "generated_obvious_self_spread_count": 0,
    "generated_uses_may_count": 0,
    "selected_obvious_self_spread_count": 0,
    "selected_uses_may_count": 0
  },
  "uses_may": false
}
```

## Generation Family Summary

| family_id                    |   generated_count |   seed_field_count |   skeleton_count |
|:-----------------------------|------------------:|-------------------:|-----------------:|
| G0_price_return_reversal     |               277 |                  1 |               48 |
| G1_volatility_state_reversal |               277 |                  2 |               48 |
| G2_basis_premium_dislocation |               277 |                  2 |               48 |
| G3_seed_pair_interaction     |              1024 |                  5 |               48 |

## Static Selected Family Summary

| family_id                    |   selected_count |   seed_field_count |   skeleton_count |
|:-----------------------------|-----------------:|-------------------:|-----------------:|
| G0_price_return_reversal     |              128 |                  1 |               48 |
| G1_volatility_state_reversal |              179 |                  2 |               48 |
| G2_basis_premium_dislocation |              179 |                  2 |               48 |
| G3_seed_pair_interaction     |               26 |                  4 |               26 |

## Static Validity Audit

```json
{
  "generated_obvious_self_spread_count": 0,
  "generated_uses_may_count": 0,
  "selected_obvious_self_spread_count": 0,
  "selected_uses_may_count": 0
}
```

## Static Selected Queue Sample

|   static_selector_rank | candidate_id           | family_id                | primary_seed_field   | source_fields   | skeleton_key              | production_key        | motif                   | expression                                                                                                                                               |
|-----------------------:|:-----------------------|:-------------------------|:---------------------|:----------------|:--------------------------|:----------------------|:------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
|                      1 | a7ab3_3b8e498a22c42cbc | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_0f915c45eabbea19 | prod_6f9573d1224714f3 | rank_atom               | Rank(ZScore(trade_return_1h))                                                                                                                            |
|                      2 | a7ab3_617d5fd64be60100 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_8196f9d0a18000c7 | prod_bf6a0736d8853070 | zscore_atom             | ZScore(TSRank(trade_return_1h,24))                                                                                                                       |
|                      3 | a7ab3_385c707663bf3d94 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_92a027c8f2dc1bf3 | prod_d9e852b96887a3ae | horizon_spread          | Sub(Delta(trade_return_1h,1),ZScore(Sub(Decay(trade_return_1h,12),Decay(trade_return_1h,24))))                                                           |
|                      4 | a7ab3_e9d3ac5ca8c61f32 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_f45bdb251a88eaea | prod_6199adfa8867969c | self_interaction        | Mul(Mean(trade_return_1h,24),Sub(TSRank(Delta(trade_return_1h,4),168),Rank(Delta(trade_return_1h,24))))                                                  |
|                      5 | a7ab3_1b877fb7b527e1ae | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_5190274b100e392b | prod_7d438a3bbcba55b6 | clip_atom               | Clip(Decay(trade_return_1h,4),-3,3)                                                                                                                      |
|                      6 | a7ab3_1bbac777d8c7cece | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_d4e122deedc31056 | prod_6f6c6bd3b682d7ab | winsor_atom             | Winsor(Clip(ZScore(trade_return_1h),-3,3),3)                                                                                                             |
|                      7 | a7ab3_b32904f3e48a1c9f | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_6914c509e2ef8a2e | prod_ab0044062d7eed99 | decay_atom              | Decay(Winsor(ZScore(trade_return_1h),3),12)                                                                                                              |
|                      8 | a7ab3_1f806f028de41c42 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_f2a1f4fc989ed2f7 | prod_d2adf3bf20dbeb32 | rank_horizon_spread     | Rank(Sub(Rank(Delta(trade_return_1h,24)),Decay(ZScore(trade_return_1h),4)))                                                                              |
|                      9 | a7ab3_2408450b6a3804c1 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_b4719759c75cc639 | prod_0b0687502f84bf2e | zscore_self_interaction | ZScore(Mul(ZScore(Mean(trade_return_1h,168)),Sub(Decay(trade_return_1h,4),Decay(trade_return_1h,12))))                                                   |
|                     10 | a7ab3_038bfab0a7a0ecb3 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_9e297cdfa8071e81 | prod_51fe2182fc723b6d | clip_horizon_spread     | Clip(Sub(TSRank(Delta(trade_return_1h,4),24),Clip(Delta(trade_return_1h,4),-3,3)),-3,3)                                                                  |
|                     11 | a7ab3_1615f89091205d2b | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_dbcc3589a0dbe876 | prod_dc30f8d952ea4686 | winsor_self_interaction | Winsor(Mul(Decay(ZScore(trade_return_1h),4),Mul(Rank(Mean(trade_return_1h,72)),ZScore(Delta(trade_return_1h,24)))),3)                                    |
|                     12 | a7ab3_90e5cc8b69d8e4f8 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_b1cbe6cc6bad4f18 | prod_830f4ae6a9b61971 | single_atom             | Sub(TSRank(trade_return_1h,72),Rank(trade_return_1h))                                                                                                    |
|                     13 | a7ab3_568082728e6a9609 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_6574be5f6db7bce2 | prod_63e18a82ceed5db7 | rank_atom               | Rank(Sub(ZScore(Mean(trade_return_1h,4)),ZScore(trade_return_1h)))                                                                                       |
|                     14 | a7ab3_09c000b24485330c | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_cc27571b1f17020e | prod_123566b01069d672 | zscore_atom             | ZScore(Mul(Rank(trade_return_1h),ZScore(Delta(trade_return_1h,24))))                                                                                     |
|                     15 | a7ab3_8a63f47f08ef2ff2 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_d28a4a1d3d3ef772 | prod_5e2ddc6848a8647b | horizon_spread          | Sub(Sub(Mean(trade_return_1h,24),Decay(trade_return_1h,4)),Sub(TSRank(trade_return_1h,24),Rank(trade_return_1h)))                                        |
|                     16 | a7ab3_54087a42f7c10ba9 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_9d763470c3811caf | prod_b98c981c78f86d30 | self_interaction        | Mul(Sub(Mean(trade_return_1h,24),Mean(trade_return_1h,168)),Mean(Delta(trade_return_1h,4),72))                                                           |
|                     17 | a7ab3_e3e5d9d8a8429553 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_2c7cbbca5fb2e3ff | prod_a8fe6605cb56c896 | clip_atom               | Clip(Sub(TSRank(trade_return_1h,72),TSRank(trade_return_1h,168)),-3,3)                                                                                   |
|                     18 | a7ab3_29a63a6062424850 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_1bfeeed2faa0c752 | prod_8e644e9ec4718486 | winsor_atom             | Winsor(Sub(Decay(trade_return_1h,12),Decay(trade_return_1h,24)),3)                                                                                       |
|                     19 | a7ab3_972af57f374b5dfa | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_791a3cbc00bffd5b | prod_3884afec03689cbd | decay_atom              | Decay(Mean(Delta(trade_return_1h,4),72),12)                                                                                                              |
|                     20 | a7ab3_98b89c29ed9d981a | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_55190e4dae05846e | prod_de6f7d73aed56a96 | rank_horizon_spread     | Rank(Sub(Decay(Delta(trade_return_1h,24),12),Mul(Rank(Delta(trade_return_1h,24)),TSRank(Mean(trade_return_1h,168),72))))                                 |
|                     21 | a7ab3_86e5ec09c46a292b | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_98d9fdb977d26ca6 | prod_9935966b8924989e | zscore_self_interaction | ZScore(Mul(TSRank(Mean(trade_return_1h,168),72),Clip(ZScore(trade_return_1h),-3,3)))                                                                     |
|                     22 | a7ab3_c96b6ce75090d30c | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_b76f814c406fe774 | prod_43ffa06fc73cf307 | clip_horizon_spread     | Clip(Sub(ZScore(Delta(Mean(trade_return_1h,168),4)),Sub(ZScore(Mean(trade_return_1h,4)),ZScore(trade_return_1h))),-3,3)                                  |
|                     23 | a7ab3_19c5ae8eb5cebf96 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_ccfa2357b3384254 | prod_730aac3ca69a9422 | winsor_self_interaction | Winsor(Mul(Rank(Sub(Mean(trade_return_1h,168),Mean(trade_return_1h,4))),Decay(Delta(trade_return_1h,24),4)),3)                                           |
|                     24 | a7ab3_eaae2209184ca101 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_80be2e39216c5bd2 | prod_d8e79de02a0cbdcc | single_atom             | ZScore(Sub(Decay(trade_return_1h,12),Decay(trade_return_1h,24)))                                                                                         |
|                     25 | a7ab3_39d7d82ced61179e | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_3f55f7b241c017b0 | prod_ba82ada35e673e0a | rank_atom               | Rank(Clip(Delta(trade_return_1h,4),-3,3))                                                                                                                |
|                     26 | a7ab3_7fa990b397bb88bd | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_7d48c4b2a2648ef2 | prod_db361ebd7f495722 | zscore_atom             | ZScore(Winsor(Delta(trade_return_1h,24),3))                                                                                                              |
|                     27 | a7ab3_dfba4b96be94d2d4 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_db44ca1a799bf920 | prod_187e9026e98edec4 | horizon_spread          | Sub(Clip(Mean(trade_return_1h,24),-3,3),Rank(trade_return_1h))                                                                                           |
|                     28 | a7ab3_b979e5779612d9dd | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_e25be550185307eb | prod_c77af23699f5ad5f | self_interaction        | Mul(Winsor(Mean(trade_return_1h,24),3),Winsor(ZScore(trade_return_1h),3))                                                                                |
|                     29 | a7ab3_6a5ba7fe2527a46c | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_929d58856d54a847 | prod_e449fddf523ca4ba | clip_atom               | Clip(Rank(Mean(Delta(trade_return_1h,24),24)),-3,3)                                                                                                      |
|                     30 | a7ab3_03c8dd1e0f1406bb | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_631f433b0ee241f4 | prod_3d36a8835cdf28f4 | winsor_atom             | Winsor(ZScore(Decay(Delta(trade_return_1h,1),12)),3)                                                                                                     |
|                     31 | a7ab3_1d0854ac5ec2163d | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_7575df9b531b63a5 | prod_16ca27c1c6a0bce8 | decay_atom              | Decay(Sub(TSRank(Delta(trade_return_1h,4),168),Rank(Delta(trade_return_1h,24))),12)                                                                      |
|                     32 | a7ab3_8a1c4ec5e39f7a5a | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_4cc6aa92a92e6b32 | prod_e8c554ee2a3a8724 | rank_horizon_spread     | Rank(Sub(Mul(Rank(Mean(trade_return_1h,72)),ZScore(Delta(trade_return_1h,24))),Sub(ZScore(Mean(trade_return_1h,168)),ZScore(Mean(trade_return_1h,24))))) |
|                     33 | a7ab3_5244861cb5bca9f2 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_e52f279333afdc9d | prod_8bb33185279cfaf6 | zscore_self_interaction | ZScore(Mul(Mul(TSRank(trade_return_1h,24),ZScore(Mean(trade_return_1h,168))),Rank(Clip(ZScore(trade_return_1h),-3,3))))                                  |
|                     34 | a7ab3_a0aabd2a13785c73 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_007ceb90e9646fcf | prod_a95f791bfd5358fe | clip_horizon_spread     | Clip(Sub(Mul(Decay(trade_return_1h,24),ZScore(Delta(trade_return_1h,4))),ZScore(trade_return_1h)),-3,3)                                                  |
|                     35 | a7ab3_8680c0acdd0b3423 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_2c7cd176105b2194 | prod_3ea07d65a9e9f256 | winsor_self_interaction | Winsor(Mul(Sub(ZScore(Mean(trade_return_1h,168)),ZScore(Mean(trade_return_1h,72))),Rank(Delta(trade_return_1h,24))),3)                                   |
|                     36 | a7ab3_ac1d320447cdc0e1 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_85fc7254db9ccb56 | prod_8b3a0e02509b8a7e | single_atom             | Sub(ZScore(Delta(trade_return_1h,1)),ZScore(Delta(trade_return_1h,24)))                                                                                  |
|                     37 | a7ab3_679945dd31d9c8a9 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_0d0b63c5ed3bddab | prod_603d364565462afc | rank_atom               | Rank(Sub(Rank(Decay(trade_return_1h,24)),Rank(Decay(trade_return_1h,4))))                                                                                |
|                     38 | a7ab3_fe15894bfdfc1a5c | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_4bc196574b0d7a0a | prod_1debfd1164de9f7a | zscore_atom             | ZScore(TSRank(Sub(Mean(trade_return_1h,4),Mean(trade_return_1h,72)),24))                                                                                 |
|                     39 | a7ab3_43a43b7a0cdeb066 | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_1889f2effaf94e35 | prod_a1a05a4ec1de64ab | horizon_spread          | Sub(Decay(Sub(Mean(trade_return_1h,24),Mean(trade_return_1h,72)),24),Sub(ZScore(Delta(trade_return_1h,1)),ZScore(Delta(trade_return_1h,24))))            |
|                     40 | a7ab3_5261a71eb76ffc5c | G0_price_return_reversal | trade_return_1h      | trade_return_1h | skeleton_aee8e5fc677d3eb9 | prod_379dbc439456e4cf | self_interaction        | Mul(Clip(Sub(Mean(trade_return_1h,24),Decay(trade_return_1h,24)),-3,3),Rank(Winsor(ZScore(trade_return_1h),3)))                                          |
