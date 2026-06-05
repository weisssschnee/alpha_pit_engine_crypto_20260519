# CRYPTO A7FF-CORE64 RETEST AND FUNDING STATE PACKAGE

Generated: 2026-06-05T01:14:26Z

## Decision

`HOLD_CORE64_PACKAGE_READY_WITH_FUNDING_REPAIR_REQUIRED`

CORE64 packages the CORE63 dice output into a bounded retest queue and defines the funding sparse-event state repair. It does not execute formula search, replay promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_company_retest": true,
  "authorizes_funding_state_patch": true,
  "authorizes_search": false,
  "blockers": [
    "funding_pair_requires_state_field_retest"
  ],
  "core64a_retest_queue_rows": 24,
  "core64a_semantic_pair_count": 4,
  "core64a_shard_count": 4,
  "core64b_panel_rows": 6949596,
  "core64b_panel_symbols": 498,
  "core64b_raw_event_coverage_median": 0.2335107203962832,
  "core64b_state8_over_raw_lift_median": 4.002318034306907,
  "core64b_state_8h_coverage_median": 0.9542358613300681,
  "decision": "HOLD_CORE64_PACKAGE_READY_WITH_FUNDING_REPAIR_REQUIRED",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-05T01:14:26Z",
  "stage": "A7FF-CORE64"
}
```

## CORE64A Retest Shard Plan

| core64_shard   |   rows |   semantic_pair_count |   motif_count |   min_repair_score |   max_repair_score |
|:---------------|-------:|----------------------:|--------------:|-------------------:|-------------------:|
| core64a_s00    |      6 |                     4 |             4 |           0.740374 |           0.83501  |
| core64a_s01    |      6 |                     4 |             5 |           0.736203 |           0.838921 |
| core64a_s02    |      6 |                     3 |             3 |           0.734656 |           0.87647  |
| core64a_s03    |      6 |                     3 |             3 |           0.734302 |           0.839696 |

## CORE64A Retest Queue Preview

| blueprint_id             | core64_shard   | semantic_pair                         | motif        | primary_label_family   |   primary_label_horizon_h |   repair_score |   control_ratio |    cost10 | expression                                                            |
|:-------------------------|:---------------|:--------------------------------------|:-------------|:-----------------------|--------------------------:|---------------:|----------------:|----------:|:----------------------------------------------------------------------|
| a7ff24r_fad5886189793630 | core64a_s00    | basis_premium_like                    | single       | L5_vol_adjusted_return |                         1 |       0.83501  |        0.331902 | 0.134581  | Delta(mark_index_basis_bps,8)                                         |
| a7ff24r_09b35fe95cd05cef | core64a_s01    | basis_premium_like                    | single       | L5_vol_adjusted_return |                         1 |       0.742468 |        0.626238 | 0.13034   | mark_index_basis_bps                                                  |
| a7ff24r_2809983f46ab7d37 | core64a_s02    | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                         1 |       0.87647  |        0.164387 | 0.125786  | Sub(mark_index_basis_bps,Mean(premium_close_bps,4))                   |
| a7ff24r_16a015591ba6cab1 | core64a_s03    | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return |                         1 |       0.813083 |        0.233555 | 0.0831497 | Sub(CSRank(mark_index_basis_bps),CSRank(Mean(premium_close_bps,8)))   |
| a7ff24r_1de5ef954b835313 | core64a_s00    | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.809419 |        0.286131 | 0.0952585 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(premium_close_bps,2))))  |
| a7ff24r_3fab392f9c9b9117 | core64a_s01    | basis_premium_like|basis_premium_like | spread_rank  | L5_vol_adjusted_return |                         1 |       0.804514 |        0.212299 | 0.0682034 | Sub(CSRank(mark_index_basis_bps),CSRank(Delta(premium_close_bps,12))) |
| a7ff24r_4df75107da3300e3 | core64a_s02    | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.803294 |        0.284052 | 0.0885092 | SafeDiv(mark_index_basis_bps,Abs(Mean(premium_close_bps,4)))          |
| a7ff24r_857b34a691777ebd | core64a_s03    | basis_premium_like|basis_premium_like | sub          | L5_vol_adjusted_return |                         1 |       0.774166 |        0.540646 | 0.13636   | Sub(mark_index_basis_bps,ZScore(Mean(premium_close_bps,8)))           |
| a7ff24r_0976d19eda31e7f3 | core64a_s00    | basis_premium_like|basis_premium_like | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.773425 |        0.388999 | 0.0901245 | SafeDiv(Delta(mark_index_basis_bps,2),Abs(premium_close_bps))         |
| a7ff24r_0bb7454738389fdf | core64a_s01    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.838921 |        0.215974 | 0.103713  | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,8)))            |
| a7ff24r_52a6ae8f1116e35c | core64a_s02    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.833318 |        0.188606 | 0.0898997 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,8))))    |
| a7ff24r_41899ad2dd939b91 | core64a_s03    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.820195 |        0.296589 | 0.109172  | SafeDiv(mark_index_basis_bps,Abs(Mean(trade_return_1h,12)))           |
| a7ff24r_16c27a7264d3bf28 | core64a_s00    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.79378  |        0.359498 | 0.10163   | SafeDiv(mark_index_basis_bps,Abs(Delta(trade_return_1h,1)))           |
| a7ff24r_7b68fb1f6c2a4885 | core64a_s01    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.787884 |        0.321436 | 0.0843147 | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(trade_return_1h,4))))    |
| a7ff24r_14eb7b2a6dbac47a | core64a_s02    | basis_premium_like|price_like         | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.787275 |        0.291724 | 0.0747923 | SafeDiv(Delta(mark_index_basis_bps,2),Abs(trade_return_1h))           |
| a7ff24r_3150667d0a336319 | core64a_s03    | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                         1 |       0.749577 |        0.602653 | 0.130373  | Sub(mark_index_basis_bps,Mean(trade_return_1h,8))                     |
| a7ff24r_158a51cba747edb0 | core64a_s00    | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                         1 |       0.740374 |        0.62375  | 0.127499  | Sub(mark_index_basis_bps,Delta(trade_return_1h,4))                    |
| a7ff24r_82f9cbcbe2bc7d31 | core64a_s01    | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                         1 |       0.736203 |        0.629034 | 0.124914  | Sub(mark_index_basis_bps,Mean(trade_return_1h,2))                     |
| a7ff24r_28ad710f94ed7607 | core64a_s02    | basis_premium_like|price_like         | sub          | L5_vol_adjusted_return |                         1 |       0.734656 |        0.645141 | 0.128198  | Sub(mark_index_basis_bps,Mean(trade_return_1h,12))                    |
| a7ff24r_55f0d29bc064638b | core64a_s03    | basis_premium_like|volatility_like    | safe_div_abs | L5_vol_adjusted_return |                         1 |       0.839696 |        0.211248 | 0.10307   | SafeDiv(mark_index_basis_bps,Abs(ZScore(Mean(realized_vol_168h,2))))  |
| a7ff24r_0b842e7d57714bb0 | core64a_s00    | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                         1 |       0.83501  |        0.331902 | 0.134581  | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_24h))             |
| a7ff24r_5e93346f70a68d33 | core64a_s01    | basis_premium_like|volatility_like    | gated_sign   | L5_vol_adjusted_return |                         1 |       0.83501  |        0.331902 | 0.134581  | Mul(Delta(mark_index_basis_bps,8),Sign(realized_vol_168h))            |
| a7ff24r_58cd9af618657156 | core64a_s02    | basis_premium_like|volatility_like    | mul          | L5_vol_adjusted_return |                         1 |       0.828595 |        0.220251 | 0.0946703 | Mul(Delta(mark_index_basis_bps,2),realized_vol_24h)                   |
| a7ff24r_258f236cd1332bb2 | core64a_s03    | basis_premium_like|volatility_like    | sub          | L5_vol_adjusted_return |                         1 |       0.734302 |        0.658145 | 0.131746  | Sub(mark_index_basis_bps,realized_vol_168h)                           |

## CORE64B Funding State Coverage Summary

```json
{
  "panel_rows": 6949596,
  "panel_symbols": 498,
  "raw_event_coverage_median": 0.2335107203962832,
  "state24_over_raw_lift_median": 4.009735744089013,
  "state8_over_raw_lift_median": 4.002318034306907,
  "state_24h_coverage_median": 0.9554603198897987,
  "state_8h_coverage_median": 0.9542358613300681
}
```

## CORE64B Funding State Field Contract

| field_name              | feature_class                | allowed_for_alpha   | allowed_for_diagnostic   | pit_rule                                                                                                       | materialization_status   |
|:------------------------|:-----------------------------|:--------------------|:-------------------------|:---------------------------------------------------------------------------------------------------------------|:-------------------------|
| funding_rate            | raw_event                    | False               | True                     | event timestamp only; sparse raw source; do not use rolling operators directly for ordinary alpha              | sparse_event_field       |
| funding_rate_state_8h   | derived_pit_last_known_state | True                | True                     | per-symbol last known funding_rate carried forward for <=8h after event; no backfill before first event        | proposed_core64b_repair  |
| funding_rate_state_24h  | derived_pit_last_known_state | False               | True                     | diagnostic carry up to 24h; alpha use requires separate approval because stale carry may wash out event timing | diagnostic_only          |
| funding_event_age_hours | derived_state_age            | True                | True                     | hours since last observed funding event, computed forward-only per symbol                                      | proposed_core64b_repair  |
| funding_event_flag      | event_indicator              | False               | True                     | event-hour indicator only; do not use as standalone alpha                                                      | diagnostic_only          |

## CORE64B Symbol Coverage Preview

| symbol       |   rows |   raw_event_coverage |   state_8h_coverage |   state_24h_coverage | first_timestamp     | last_timestamp      |   state8_over_raw_lift |   state24_over_raw_lift |
|:-------------|-------:|---------------------:|--------------------:|---------------------:|:--------------------|:--------------------|-----------------------:|------------------------:|
| AIAUSDT      |   3470 |             0.173775 |            0.696542 |             0.701153 | 2026-01-01 00:00:00 | 2026-05-26 00:00:00 |                4.00829 |                 4.03483 |
| LITUSDT      |   4208 |             0.182747 |            0.732177 |             0.735979 | 2025-12-01 00:00:00 | 2026-05-26 00:00:00 |                4.0065  |                 4.02731 |
| SPACEUSDT    |   2942 |             0.198844 |            0.797077 |             0.802515 | 2026-01-23 11:00:00 | 2026-05-26 00:00:00 |                4.00855 |                 4.0359  |
| SKRUSDT      |   2967 |             0.233906 |            0.79845  |             0.803842 | 2026-01-22 10:00:00 | 2026-05-26 00:00:00 |                3.41354 |                 3.4366  |
| ELSAUSDT     |   2970 |             0.220202 |            0.79899  |             0.804377 | 2026-01-22 07:00:00 | 2026-05-26 00:00:00 |                3.62844 |                 3.65291 |
| ACUUSDT      |   2989 |             0.199398 |            0.799264 |             0.804617 | 2026-01-21 12:00:00 | 2026-05-26 00:00:00 |                4.00839 |                 4.03523 |
| SPORTFUNUSDT |   3108 |             0.201416 |            0.807272 |             0.81242  | 2026-01-16 13:00:00 | 2026-05-26 00:00:00 |                4.00799 |                 4.03355 |
| FRAXUSDT     |   3137 |             0.202104 |            0.81001  |             0.81511  | 2026-01-15 08:00:00 | 2026-05-26 00:00:00 |                4.00789 |                 4.03312 |
| FOGOUSDT     |   3251 |             0.20363  |            0.816057 |             0.820978 | 2026-01-10 14:00:00 | 2026-05-26 00:00:00 |                4.00755 |                 4.03172 |
| ZAMAUSDT     |   3280 |             0.203963 |            0.817378 |             0.822256 | 2026-01-09 09:00:00 | 2026-05-26 00:00:00 |                4.00747 |                 4.03139 |
| MAGMAUSDT    |   3492 |             0.206758 |            0.828465 |             0.833047 | 2025-12-31 13:00:00 | 2026-05-26 00:00:00 |                4.00693 |                 4.02909 |
| COLLECTUSDT  |   3492 |             0.206758 |            0.828465 |             0.833047 | 2025-12-31 13:00:00 | 2026-05-26 00:00:00 |                4.00693 |                 4.02909 |
| BREVUSDT     |   3519 |             0.207161 |            0.830065 |             0.834612 | 2025-12-30 10:00:00 | 2026-05-26 00:00:00 |                4.00686 |                 4.02881 |
| GUAUSDT      |   3735 |             0.209639 |            0.839893 |             0.844177 | 2025-12-21 10:00:00 | 2026-05-26 00:00:00 |                4.00639 |                 4.02682 |
| ZKPUSDT      |   3735 |             0.311914 |            0.839893 |             0.844177 | 2025-12-21 10:00:00 | 2026-05-26 00:00:00 |                2.6927  |                 2.70644 |
| RAVEUSDT     |   3898 |             0.265264 |            0.846845 |             0.850949 | 2025-12-14 15:00:00 | 2026-05-26 00:00:00 |                3.19246 |                 3.20793 |
| USUSDT       |   3951 |             0.211845 |            0.848646 |             0.852696 | 2025-12-12 10:00:00 | 2026-05-26 00:00:00 |                4.00597 |                 4.02509 |
| CYSUSDT      |   3950 |             0.211899 |            0.848861 |             0.852911 | 2025-12-12 11:00:00 | 2026-05-26 00:00:00 |                4.00597 |                 4.02509 |
| NIGHTUSDT    |   3998 |             0.212356 |            0.850675 |             0.854677 | 2025-12-10 11:00:00 | 2026-05-26 00:00:00 |                4.00589 |                 4.02473 |
| WETUSDT      |   4002 |             0.293353 |            0.850825 |             0.854823 | 2025-12-10 07:00:00 | 2026-05-26 00:00:00 |                2.90034 |                 2.91397 |
| POWERUSDT    |   4096 |             0.258301 |            0.85376  |             0.857666 | 2025-12-06 09:00:00 | 2026-05-26 00:00:00 |                3.30529 |                 3.32042 |
| CVXUSDT      |   7886 |             0.214177 |            0.857342 |             0.859371 | 2025-07-01 00:00:00 | 2026-05-26 00:00:00 |                4.00296 |                 4.01243 |
| SLPUSDT      |   7886 |             0.214177 |            0.857342 |             0.859371 | 2025-07-01 00:00:00 | 2026-05-26 00:00:00 |                4.00296 |                 4.01243 |
| IRYSUSDT     |   4329 |             0.215292 |            0.862324 |             0.86602  | 2025-11-26 16:00:00 | 2026-05-26 00:00:00 |                4.00536 |                 4.02253 |
| SENTUSDT     |   4621 |             0.320926 |            0.870158 |             0.87362  | 2025-11-14 12:00:00 | 2026-05-26 00:00:00 |                2.7114  |                 2.72218 |
| PIEVERSEUSDT |   4622 |             0.217438 |            0.870835 |             0.874297 | 2025-11-14 11:00:00 | 2026-05-26 00:00:00 |                4.00498 |                 4.0209  |
| BEATUSDT     |   4669 |             0.289784 |            0.87235  |             0.875776 | 2025-11-12 12:00:00 | 2026-05-26 00:00:00 |                3.01035 |                 3.02217 |
| CLANKERUSDT  |   4669 |             0.21782  |            0.87235  |             0.875776 | 2025-11-12 12:00:00 | 2026-05-26 00:00:00 |                4.00492 |                 4.02065 |
| ALLOUSDT     |   4691 |             0.217864 |            0.872522 |             0.875933 | 2025-11-11 14:00:00 | 2026-05-26 00:00:00 |                4.00489 |                 4.02055 |
| JCTUSDT      |   4719 |             0.218055 |            0.873278 |             0.876669 | 2025-11-10 10:00:00 | 2026-05-26 00:00:00 |                4.00486 |                 4.02041 |
