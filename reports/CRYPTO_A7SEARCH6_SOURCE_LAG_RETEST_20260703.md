# CRYPTO A7SEARCH6 Source Lag Retest

Generated: `2026-07-03T02:06:26Z`

## Decision

`PASS_A7SEARCH6_SOURCE_LAG_SURVIVORS_FOUND`

This retests only June diagnostic survivors under delayed source-field variants. It is a leakage-sensitivity diagnostic, not alpha proof.

## Counts

- queue_rows: `3`
- metric_rows: `102`
- error_rows: `0`
- all_risk_lag1_pass_rows: `1`
- all_risk_lag2_pass_rows: `1`

## Sensitivity Summary

| source_blueprint_id        |   horizon_h | variant             | lagged_fields                                              | lag_gate_pass   |   sortino |   nonoverlap_floor_sortino |   floor_retention_ratio |   control_floor_ratio | formula                                                                                             |
|:---------------------------|------------:|:--------------------|:-----------------------------------------------------------|:----------------|----------:|---------------------------:|------------------------:|----------------------:|:----------------------------------------------------------------------------------------------------|
| a7search6_2e796ac0b2a688c4 |          24 | all_risk_lag1h      | open_interest_last                                         | True            |  2.47408  |                   0.390858 |                0.82912  |              0.992903 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_2e796ac0b2a688c4 |          24 | all_risk_lag2h      | open_interest_last                                         | True            |  2.46093  |                   0.429006 |                0.910044 |              0.726772 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_2e796ac0b2a688c4 |          24 | all_risk_lag8h      | open_interest_last                                         | False           |  2.5016   |                   0.529959 |                1.12419  |              7.18126  | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_2e796ac0b2a688c4 |          24 | open_interest_lag1h | open_interest_last                                         | True            |  2.47408  |                   0.390858 |                0.82912  |              0.992903 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_2e796ac0b2a688c4 |          24 | original            |                                                            | True            |  2.48831  |                   0.471413 |                1        |              0.869706 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_afa93f504b4c29d0 |           4 | all_risk_lag1h      | funding_rate_delta_state_24h|open_interest_value_last      | False           | 11.0258   |                   8.18257  |                0.590334 |              1.47743  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_afa93f504b4c29d0 |           4 | all_risk_lag2h      | funding_rate_delta_state_24h|open_interest_value_last      | False           |  8.82097  |                   6.22251  |                0.448925 |              1.36726  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_afa93f504b4c29d0 |           4 | all_risk_lag8h      | funding_rate_delta_state_24h|open_interest_value_last      | False           |  3.58967  |                   1.115    |                0.080442 |              4.74681  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_afa93f504b4c29d0 |           4 | funding_state_lag1h | funding_rate_delta_state_24h                               | True            | 13.7476   |                  13.3693   |                0.964534 |              0.979852 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_afa93f504b4c29d0 |           4 | open_interest_lag1h | open_interest_value_last                                   | False           | 11.5596   |                   8.338    |                0.601548 |              1.22042  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_afa93f504b4c29d0 |           4 | original            |                                                            | True            | 14.4965   |                  13.8609   |                1        |              0.79349  | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_e7ee64f0ef980aca |           4 | all_risk_lag1h      | open_interest_value_last|top_long_short_account_ratio_last | False           | -0.657252 |                  -3.41     |              -12.9119   |              0.615309 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |
| a7search6_e7ee64f0ef980aca |           4 | all_risk_lag2h      | open_interest_value_last|top_long_short_account_ratio_last | False           | -1.77431  |                  -3.3916   |              -12.8423   |              2.28948  | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |
| a7search6_e7ee64f0ef980aca |           4 | all_risk_lag8h      | open_interest_value_last|top_long_short_account_ratio_last | False           | -8.63906  |                  -9.64125  |              -36.5066   |              0.664743 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |
| a7search6_e7ee64f0ef980aca |           4 | open_interest_lag1h | open_interest_value_last                                   | False           | -0.683315 |                  -3.43516  |              -13.0072   |              0.610896 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |
| a7search6_e7ee64f0ef980aca |           4 | original            |                                                            | False           |  1.83127  |                   0.264097 |                1        |             50.7045   | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |
| a7search6_e7ee64f0ef980aca |           4 | positioning_lag1h   | top_long_short_account_ratio_last                          | False           |  1.74738  |                   0.182029 |                0.689252 |             12.0679   | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |

## Errors

`<empty>`

## Decision Boundary

- Passing this retest does not prove source timing. It only means delayed-source versions remain worth source timestamp repair.
- Broad search remains blocked until source contracts for OI, positioning, funding-state, and regime-state are wired into the loader.

