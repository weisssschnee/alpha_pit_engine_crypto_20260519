# CRYPTO A7SOURCE-2 Source-Lag Retest

Generated: `2026-07-03T02:31:55Z`

## Decision

`PASS_A7SOURCE2_SOURCE_LAG_SURVIVORS_FOUND`

This retests June-diagnostic survivors after delaying the whole signal by 1h, 2h, and 4h. It is diagnostic only and does not override A7SOURCE-1 source-contract holds.

## Counts

- queue_rows: `3`
- metric_rows: `15`
- eval_error_rows: `0`
- source_lag_pass_count: `2`

## Source-Lag Summary

| source_blueprint_id        | blueprint_id                                      |   horizon_h | formula                                                                                             |   nonoverlap_floor_sortino_control_one_bar_lag |   nonoverlap_floor_sortino_original |   nonoverlap_floor_sortino_source_lag_1h |   nonoverlap_floor_sortino_source_lag_2h |   nonoverlap_floor_sortino_source_lag_4h |   rankic_mean_control_one_bar_lag |   rankic_mean_original |   rankic_mean_source_lag_1h |   rankic_mean_source_lag_2h |   rankic_mean_source_lag_4h |   sortino_control_one_bar_lag |   sortino_original |   sortino_source_lag_1h |   sortino_source_lag_2h |   sortino_source_lag_4h | source_lag_gate                  | formula_decision           | field_proof_decisions                                                     |
|:---------------------------|:--------------------------------------------------|------------:|:----------------------------------------------------------------------------------------------------|-----------------------------------------------:|------------------------------------:|-----------------------------------------:|-----------------------------------------:|-----------------------------------------:|----------------------------------:|-----------------------:|----------------------------:|----------------------------:|----------------------------:|------------------------------:|-------------------:|------------------------:|------------------------:|------------------------:|:---------------------------------|:---------------------------|:--------------------------------------------------------------------------|
| a7search6_e7ee64f0ef980aca | a7search6_vp_a7search6_e7ee64f0ef980aca_canonical |           4 | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |                                      -3.41     |                            0.264097 |                                -3.41     |                                -3.3916   |                                -7.1559   |                        0.0247479  |             0.0331355  |                  0.0247479  |                  0.0204243  |                  0.0114508  |                     -0.657252 |            1.83127 |               -0.657252 |                -1.77431 |                -5.1778  | HOLD_SOURCE_LAG_FRAGILE          | HOLD_SOURCE_PROOF_REQUIRED | HOLD_PUBLICATION_LAG_PROOF_REQUIRED                                       |
| a7search6_afa93f504b4c29d0 | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           4 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |                                       8.18257  |                           13.8609   |                                 8.18257  |                                 6.22251  |                                 2.70251  |                        0.0328488  |             0.0408168  |                  0.0328488  |                  0.0277093  |                  0.0196705  |                     11.0258   |           14.4965  |               11.0258   |                 8.82097 |                 4.5242  | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC | HOLD_SOURCE_PROOF_REQUIRED | HOLD_EVENT_PUBLICATION_PROOF_REQUIRED|HOLD_PUBLICATION_LAG_PROOF_REQUIRED |
| a7search6_2e796ac0b2a688c4 | a7search6_vp_a7search6_2e796ac0b2a688c4_canonical |          24 | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |                                       0.409991 |                            0.471413 |                                 0.409991 |                                 0.425837 |                                 0.440479 |                        0.00239585 |             0.00237251 |                  0.00239585 |                  0.00245661 |                  0.00257813 |                      2.47332  |            2.48831 |                2.47332  |                 2.47238 |                 2.45804 | PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC | HOLD_SOURCE_PROOF_REQUIRED | HOLD_PUBLICATION_LAG_PROOF_REQUIRED|PASS_CONTROLLED_EXPERIMENT            |

## Errors

`<empty>`

