# CRYPTO A7SHADOW4 Live Capacity Correlation Review

Generated: 2026-07-03T16:17:22Z

## Decision

`HOLD_A7SHADOW4_BLOCKING_HEALTH_OR_EVAL_ISSUE`

A7SHADOW-4 rematerializes the A7SHADOW-3 accepted rows and audits live-field availability, signal overlap, net-return overlap, cost ladder, and capacity proxies. It does not authorize alpha proof, shadow, paper, or live trading.

## Counts

- input_rows: `4`
- unique_candidate_horizon_rows: `4`
- eval_error_rows: `0`
- field_health_min_recent: `1.0`
- field_health_min_stress: `0.003813089295618414`
- max_abs_signal_corr: `1.0`
- mean_abs_signal_corr: `0.2895680978036836`
- max_abs_recent_net_return_corr: `0.9281842719752638`
- recent_20bps_positive_sortino_blueprints: `3`
- recent_30bps_positive_sortino_blueprints: `3`

## Field Health

| field                        | status   |   overall_finite_ratio |   recent_finite_ratio |   stress_finite_ratio |
|:-----------------------------|:---------|-----------------------:|----------------------:|----------------------:|
| funding_rate_delta_state_24h | OK       |               0.944183 |                     1 |            0.00381309 |
| open_interest_last           | OK       |               0.997936 |                     1 |            1          |
| open_interest_mean           | OK       |               0.997936 |                     1 |            1          |
| open_interest_value_last     | OK       |               0.997936 |                     1 |            1          |
| premium_close_bps            | OK       |               0.998707 |                     1 |            0.998336   |

## Signal Correlation

| left               | right              |   signal_corr |
|:-------------------|:-------------------|--------------:|
| a7shadow2_c002|h24 | a7shadow2_c006|h24 |    0.708319   |
| a7shadow2_c002|h24 | a7shadow2_c007|h4  |    0.0087949  |
| a7shadow2_c002|h24 | a7shadow2_c007|h8  |    0.0087949  |
| a7shadow2_c006|h24 | a7shadow2_c007|h4  |    0.00574967 |
| a7shadow2_c006|h24 | a7shadow2_c007|h8  |    0.00574967 |
| a7shadow2_c007|h4  | a7shadow2_c007|h8  |    1          |

## Recent Cost Ladder

| blueprint_id   |   horizon_h | expression                                                                                          |   cost_bps | split                 |   n_obs |    net_mean |   sharpe |   sortino |   max_drawdown |   positive_rate |   avg_turnover |    avg_cost |   capacity_proxy_median_quote_volume |   capacity_proxy_p10_quote_volume |   traded_liquidity_proxy_median |
|:---------------|------------:|:----------------------------------------------------------------------------------------------------|-----------:|:----------------------|--------:|------------:|---------:|----------:|---------------:|----------------:|---------------:|------------:|-------------------------------------:|----------------------------------:|--------------------------------:|
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |          5 | recent_oos_2026JanApr |     720 | 0.000945967 |  2.37311 |   5.59419 |     -0.295414  |        0.494444 |     0.00441653 | 2.20827e-06 |                          1.09718e+07 |                       4.88394e+06 |                         2800.11 |
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |         20 | recent_oos_2026JanApr |     720 | 0.000939342 |  2.35631 |   5.54803 |     -0.295644  |        0.493056 |     0.00441653 | 8.83307e-06 |                          1.09718e+07 |                       4.88394e+06 |                         2800.11 |
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |         30 | recent_oos_2026JanApr |     720 | 0.000934926 |  2.34511 |   5.51729 |     -0.295797  |        0.493056 |     0.00441653 | 1.32496e-05 |                          1.09718e+07 |                       4.88394e+06 |                         2800.11 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |          5 | recent_oos_2026JanApr |     720 | 0.000624096 |  1.31593 |   2.63995 |     -0.537082  |        0.479167 |     0.00266746 | 1.33373e-06 |                          1.1426e+07  |                       5.13699e+06 |                         4129.37 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |         20 | recent_oos_2026JanApr |     720 | 0.000620095 |  1.3075  |   2.62178 |     -0.537305  |        0.479167 |     0.00266746 | 5.33492e-06 |                          1.1426e+07  |                       5.13699e+06 |                         4129.37 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |         30 | recent_oos_2026JanApr |     720 | 0.000617428 |  1.30188 |   2.60968 |     -0.537453  |        0.479167 |     0.00266746 | 8.00239e-06 |                          1.1426e+07  |                       5.13699e+06 |                         4129.37 |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |          5 | recent_oos_2026JanApr |     720 | 0.000555483 |  8.59481 |  13.7681  |     -0.0613551 |        0.586111 |     0.0638847  | 3.19423e-05 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         20 | recent_oos_2026JanApr |     720 | 0.000459656 |  7.09955 |  11.1275  |     -0.0659822 |        0.570833 |     0.0638847  | 0.000127769 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         30 | recent_oos_2026JanApr |     720 | 0.000395771 |  6.10517 |   9.43019 |     -0.0697804 |        0.563889 |     0.0638847  | 0.000191654 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |          5 | recent_oos_2026JanApr |     720 | 0.00117136  |  9.40702 |  18.3432  |     -0.102861  |        0.604167 |     0.0638847  | 3.19423e-05 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         20 | recent_oos_2026JanApr |     720 | 0.00107554  |  8.62448 |  16.481   |     -0.108777  |        0.6      |     0.0638847  | 0.000127769 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         30 | recent_oos_2026JanApr |     720 | 0.00101165  |  8.10375 |  15.2784  |     -0.1127    |        0.593056 |     0.0638847  | 0.000191654 |                          5.81101e+06 |                       2.45315e+06 |                       695053    |

## Stress Cost Ladder

| blueprint_id   |   horizon_h | expression                                                                                          |   cost_bps | split                |   n_obs |    net_mean |   sharpe |   sortino |   max_drawdown |   positive_rate |   avg_turnover |    avg_cost |   capacity_proxy_median_quote_volume |   capacity_proxy_p10_quote_volume |   traded_liquidity_proxy_median |
|:---------------|------------:|:----------------------------------------------------------------------------------------------------|-----------:|:---------------------|--------:|------------:|---------:|----------:|---------------:|----------------:|---------------:|------------:|-------------------------------------:|----------------------------------:|--------------------------------:|
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |          5 | known_may2026_stress |     601 | 0.000680892 |  4.28035 |   6.46029 |     -0.231048  |       0.615641  |     0.00585685 | 2.92842e-06 |                          9.23602e+06 |                       4.39588e+06 |                         1142.04 |
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |         20 | known_may2026_stress |     601 | 0.000672106 |  4.22102 |   6.35872 |     -0.231825  |       0.612313  |     0.00585685 | 1.17137e-05 |                          9.23602e+06 |                       4.39588e+06 |                         1142.04 |
| a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            |         30 | known_may2026_stress |     601 | 0.000666249 |  4.18147 |   6.29119 |     -0.232342  |       0.610649  |     0.00585685 | 1.75705e-05 |                          9.23602e+06 |                       4.39588e+06 |                         1142.04 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |          5 | known_may2026_stress |     601 | 0.00118429  |  6.08764 |   9.91311 |     -0.215315  |       0.657238  |     0.00233913 | 1.16956e-06 |                          9.28381e+06 |                       4.41531e+06 |                         3330.76 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |         20 | known_may2026_stress |     601 | 0.00118078  |  6.0697  |   9.87725 |     -0.215605  |       0.657238  |     0.00233913 | 4.67826e-06 |                          9.28381e+06 |                       4.41531e+06 |                         3330.76 |
| a7shadow2_c006 |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |         30 | known_may2026_stress |     601 | 0.00117845  |  6.05774 |   9.85337 |     -0.215798  |       0.655574  |     0.00233913 | 7.01738e-06 |                          9.28381e+06 |                       4.41531e+06 |                         3330.76 |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |          5 | known_may2026_stress |     601 | 3.31878e-05 |  3.05744 |   5.78477 |     -0.0150988 |       0.0499168 |     0.00780531 | 3.90265e-06 |                          0           |                       0           |                            0    |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         20 | known_may2026_stress |     601 | 2.14799e-05 |  1.96701 |   3.35355 |     -0.0182033 |       0.0449251 |     0.00780531 | 1.56106e-05 |                          0           |                       0           |                            0    |
| a7shadow2_c007 |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         30 | known_may2026_stress |     601 | 1.36745e-05 |  1.23812 |   1.97314 |     -0.0207169 |       0.0432612 |     0.00780531 | 2.34159e-05 |                          0           |                       0           |                            0    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |          5 | known_may2026_stress |     601 | 5.55233e-05 |  2.66224 |   5.94272 |     -0.0217566 |       0.0432612 |     0.00780531 | 3.90265e-06 |                          0           |                       0           |                            0    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         20 | known_may2026_stress |     601 | 4.38153e-05 |  2.1212  |   4.39136 |     -0.0238053 |       0.0415973 |     0.00780531 | 1.56106e-05 |                          0           |                       0           |                            0    |
| a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |         30 | known_may2026_stress |     601 | 3.601e-05   |  1.74734 |   3.44295 |     -0.0259487 |       0.0382696 |     0.00780531 | 2.34159e-05 |                          0           |                       0           |                            0    |

## Interpretation

The surviving candidates remain an engineering-review packet, not a deployable book. This R2 stage is on HOLD because stress-window field coverage is incomplete for funding_rate_delta_state_24h. Recent-window field health and cost ladder are usable, but May-stress claims for the OI/funding candidate are not reliable until that coverage gap is repaired or the candidate is excluded from stress claims. It also does not resolve family concentration: OI, funding, and premium/basis still dominate the accepted set.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_live_adapter_probe": false,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "stress_field_coverage_below_95pct"
  ],
  "decision": "HOLD_A7SHADOW4_BLOCKING_HEALTH_OR_EVAL_ISSUE",
  "eval_error_rows": 0,
  "family_counts": {
    "funding": 2,
    "open_interest": 4,
    "premium_basis": 2
  },
  "field_count": 5,
  "field_health_min_recent": 1.0,
  "field_health_min_stress": 0.003813089295618414,
  "generated_at": "2026-07-03T16:17:22Z",
  "input_rows": 4,
  "max_abs_recent_net_return_corr": 0.9281842719752638,
  "max_abs_signal_corr": 1.0,
  "mean_abs_signal_corr": 0.2895680978036836,
  "next_required": [
    "repair May-stress coverage for funding_rate_delta_state_24h or exclude funding-delta candidates from stress claims",
    "rerun A7SHADOW-4 after stress field coverage repair",
    "family diversification repair before further large search",
    "explicit orderbook/spread slippage model before any shadow book"
  ],
  "recent_20bps_positive_sortino_blueprints": 3,
  "recent_30bps_positive_sortino_blueprints": 3,
  "stage": "A7SHADOW-4",
  "unique_candidate_horizon_rows": 4,
  "warnings": [
    "max_signal_corr_gt_0_85",
    "max_recent_net_return_corr_gt_0_85",
    "open_interest_family_concentrated"
  ]
}
```
