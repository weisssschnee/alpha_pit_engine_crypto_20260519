# CRYPTO A7SEARCH6 June Blind Adapter

Generated: `2026-07-03T01:47:18Z`

## Decision

`PASS_A7SEARCH6_JUNE_BLIND_DIAGNOSTIC_NONEMPTY`

This evaluates accepted A7SEARCH6 formulas on the available June 2026 patch as a diagnostic blind split. It does not authorize alpha proof, search expansion, shadow, paper, or live.

## Counts

- queue_rows: `18`
- metric_rows: `108`
- eval_error_rows: `0`
- june_timestamps: `264`
- diagnostic_pass_rows: `3`

## Original Formula June Summary

| source_blueprint_id        |   horizon_h | june_gate_pass_diagnostic   |   n_obs |    sortino |   nonoverlap_floor_sortino |   june_control_floor_ratio |   rankic_mean | formula                                                                                                                                                                   |
|:---------------------------|------------:|:----------------------------|--------:|-----------:|---------------------------:|---------------------------:|--------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| a7search6_afa93f504b4c29d0 |           4 | True                        |     264 |  14.4965   |                  13.8609   |                  0.79349   |   0.0408168   | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_2e796ac0b2a688c4 |          24 | True                        |     264 |   2.48831  |                   0.471413 |                  0.869706  |   0.00237251  | Mul(open_interest_last,Mean(premium_close_bps,504))                                                                                                                       |
| a7search6_e7ee64f0ef980aca |           4 | True                        |     264 |   1.83127  |                   0.264097 |                -12.5133    |   0.0331355   | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))                                                                              |
| a7search6_afa93f504b4c29d0 |           8 | False                       |     264 |   9.79819  |                   6.80552  |                  1.72605   |   0.0404796   | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))                                                                       |
| a7search6_5a7a41644c28a05a |          24 | False                       |     264 |   3.38215  |                   0.382277 |                130.795     |   0.0106018   | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))                                                                                                 |
| a7search6_229924c832dd5901 |          24 | False                       |     264 |   3.33782  |                   0.254243 |                 34.5793    |   0.010541    | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                                                                                                  |
| a7search6_8d74bccf1d25af11 |           8 | False                       |     264 |   1.60259  |                  -0.130286 |                 -3.9604    |   0.00865266  | SafeDiv(Decay(top_long_short_account_ratio_last,12),Abs(ZScore(Mean(quote_volume_z_168h,504))))                                                                           |
| a7search6_370b9d993902426e |           4 | False                       |     264 |  -1.49516  |                  -2.44882  |                 -0.691086  |   0.0298881   | Sub(CSRank(TSRank(open_interest_value_last,504)),CSRank(Mean(taker_buy_sell_volume_ratio_last,72)))                                                                       |
| a7search6_0159a7544af64b1d |          24 | False                       |     264 |  -0.386321 |                  -2.46826  |                 -1.01274   |   0.000870878 | Sub(CSRank(ZScore(Mean(account_position_divergence,24))),CSRank(Decay(mark_index_basis_bps,336)))                                                                         |
| a7search6_5a326bbdc99cd2b9 |           4 | False                       |     264 |  -1.33981  |                  -3.37701  |                  0.465726  |   0.0215182   | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_06c5d4a2d2ce5d98 |           4 | False                       |     264 |  -4.7396   |                  -4.79381  |                 -0.0873685 |   0.000423605 | SafeDiv(ZScore(Mean(open_interest_value_mean,504)),Abs(global_long_short_account_ratio_last))                                                                             |
| a7search6_4c8a38ddff3fb132 |           4 | False                       |     264 |  -6.23695  |                  -6.94454  |                 -0.661333  |  -0.00428047  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_4c8a38ddff3fb132 |          24 | False                       |     264 |  -3.67056  |                  -7.3712   |                 -0.617747  |  -0.00652892  | SafeDiv(CSRank(Delta(open_interest_value_last,96)),Abs(Decay(account_position_divergence,48)))                                                                            |
| a7search6_5a326bbdc99cd2b9 |           8 | False                       |     264 |  -4.6134   |                  -9.15405  |                 -0.457472  |   0.00961145  | SafeDiv(Sub(CSRank(TSRank(open_interest_value_mean,504)),CSRank(CSRank(global_long_short_account_ratio_last))),Abs(CSRank(CSRank(global_long_short_account_ratio_last)))) |
| a7search6_5be6987af4a13e67 |           4 | False                       |     264 | -14.6548   |                 -16.7638   |                 -0.243937  |  -0.0271693   | SafeDiv(Abs(CSRank(open_interest_value_change_24h)),Abs(Decay(account_position_divergence,8)))                                                                            |
| a7search6_05d9f75e309aa068 |           4 | False                       |     264 | nan        |                 nan        |                nan         | nan           | Mul(ZScore(global_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                     |
| a7search6_215546fe5dfda21c |           4 | False                       |     264 | nan        |                 nan        |                nan         | nan           | Mul(CSRank(Abs(CSRank(global_long_short_account_ratio_last))),Sign(Decay(stress_proxy_state,336)))                                                                        |
| a7search6_9115fe1cea3feca0 |           4 | False                       |     264 | nan        |                 nan        |                nan         | nan           | Mul(ZScore(top_long_short_account_ratio_last),Sign(Decay(stress_proxy_state,336)))                                                                                        |

## Errors

`<empty>`

## Required Next Action

- Keep source-contract HOLD in force. Use this only to prioritize which formulas deserve source timestamp repair first.

