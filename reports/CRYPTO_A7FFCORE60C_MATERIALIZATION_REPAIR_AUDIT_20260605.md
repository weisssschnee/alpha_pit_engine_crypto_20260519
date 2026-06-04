# CRYPTO A7FF-CORE60C MATERIALIZATION REPAIR AUDIT

Generated: 2026-06-04T16:08:55Z

## Decision

`HOLD_CORE60C_MATERIALIZATION_REPAIR_REQUIRED`

CORE60C audits materialization attrition from CORE59. It does not search, replay, or promote candidates.

## Decision Record

```json
{
  "activity_ok_rate": 0.5391666666666667,
  "activity_ok_rows": 647,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "blockers": [
    "activity_ok_rate_lt_0_6",
    "semantic_pairs_with_zero_activity_ok"
  ],
  "decision": "HOLD_CORE60C_MATERIALIZATION_REPAIR_REQUIRED",
  "eval_fail_rows": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-04T16:08:55Z",
  "inactive_or_sparse_rows": 553,
  "queue_rows": 1200,
  "stage": "A7FF-CORE60C",
  "zero_activity_semantic_pair_count": 2
}
```

## Materialization By Semantic Pair

| semantic_pair                         |   queue_rows |   activity_ok_rows |   inactive_rows |   eval_fail_rows |   median_finite_share |   median_nonzero_share |   median_std_value |   activity_ok_rate |
|:--------------------------------------|-------------:|-------------------:|----------------:|-----------------:|----------------------:|-----------------------:|-------------------:|-------------------:|
| basis_premium_like|funding_like       |          360 |                  0 |             360 |                0 |           0.000670305 |               0.958106 |        0.000145443 |           0        |
| funding_like|positioning_like         |           13 |                  0 |              13 |                0 |           0.00326475  |               0.900716 |        0.00100181  |           0        |
| basis_premium_like|basis_premium_like |          200 |                132 |              68 |                0 |           0.996265    |               0.94419  |       16.1199      |           0.66     |
| basis_premium_like|volatility_like    |          213 |                167 |              46 |                0 |           0.825338    |               0.988895 |        0.41324     |           0.784038 |
| basis_premium_like|price_like         |          282 |                230 |              52 |                0 |           0.995691    |               0.987939 |        1.46311     |           0.815603 |
| price_like|volatility_like            |           51 |                 43 |               8 |                0 |           0.825338    |               0.987948 |        0.0264015   |           0.843137 |
| volatility_like|volatility_like       |           26 |                 22 |               4 |                0 |           0.825625    |               0.978125 |        0.0285546   |           0.846154 |
| basis_premium_like                    |           38 |                 36 |               2 |                0 |           0.993393    |               1        |        0.994778    |           0.947368 |
| volatility_like                       |           14 |                 14 |               0 |                0 |           0.827348    |               1        |        0.77494     |           1        |
| price_like                            |            3 |                  3 |               0 |                0 |           0.999425    |               1        |        0.28863     |           1        |

## Materialization By Semantic Pair / Motif

| semantic_pair                         | motif               |   queue_rows |   activity_ok_rows |   inactive_rows |   eval_fail_rows |   median_finite_share |   median_nonzero_share |   median_std_value |   activity_ok_rate |
|:--------------------------------------|:--------------------|-------------:|-------------------:|----------------:|-----------------:|----------------------:|-----------------------:|-------------------:|-------------------:|
| basis_premium_like|funding_like       | relative_shock      |          216 |                  0 |             216 |                0 |           0.00314505  |               0.621793 |        8.64868e-05 |           0        |
| basis_premium_like|funding_like       | mean_reversion_gate |          144 |                  0 |             144 |                0 |           0.000670305 |               1        |        0.707107    |           0        |
| funding_like|positioning_like         | gated_sign          |           13 |                  0 |              13 |                0 |           0.00326475  |               0.900716 |        0.00100181  |           0        |
| basis_premium_like|basis_premium_like | sub                 |           23 |                 10 |              13 |                0 |           0           |               0        |       13.7352      |           0.434783 |
| basis_premium_like|basis_premium_like | mul                 |           29 |                 17 |              12 |                0 |           0.996553    |               0.664012 |     2261.28        |           0.586207 |
| basis_premium_like|volatility_like    | safe_div_abs        |            5 |                  3 |               2 |                0 |           0.825338    |               0.672366 |     5593.9         |           0.6      |
| basis_premium_like|basis_premium_like | spread_rank         |           45 |                 29 |              16 |                0 |           0.996553    |               0.968268 |        0.310646    |           0.644444 |
| basis_premium_like|basis_premium_like | safe_div_abs        |           15 |                 10 |               5 |                0 |           0.662579    |               0.993336 |      176.898       |           0.666667 |
| basis_premium_like|basis_premium_like | gated_sign          |           22 |                 15 |               7 |                0 |           0.997558    |               0.664105 |       14.0942      |           0.681818 |
| price_like|volatility_like            | mul                 |            7 |                  5 |               2 |                0 |           0.825338    |               0.964073 |        0.0223628   |           0.714286 |
| basis_premium_like|price_like         | smooth_mul          |           95 |                 71 |              24 |                0 |           0.99368     |               0.999892 |        2.33093     |           0.747368 |
| basis_premium_like|volatility_like    | smooth_mul          |           29 |                 22 |               7 |                0 |           0.824476    |               1        |        0.0301132   |           0.758621 |
| basis_premium_like|volatility_like    | mul                 |           46 |                 35 |              11 |                0 |           0.825768    |               0.832274 |        0.273631    |           0.76087  |
| basis_premium_like|basis_premium_like | smooth_mul          |           66 |                 51 |              15 |                0 |           0.995691    |               0.993289 |       62.8252      |           0.772727 |
| basis_premium_like|volatility_like    | spread_rank         |           74 |                 58 |              16 |                0 |           0.825338    |               0.98915  |        0.411602    |           0.783784 |
| price_like|volatility_like            | spread_rank         |           24 |                 19 |               5 |                0 |           0.825912    |               0.987655 |        0.413235    |           0.791667 |
| basis_premium_like|price_like         | safe_div_abs        |           26 |                 21 |               5 |                0 |           0.963034    |               0.987432 |    12775.8         |           0.807692 |
| basis_premium_like|volatility_like    | gated_sign          |           44 |                 36 |               8 |                0 |           0.825338    |               0.9871   |       10.152       |           0.818182 |
| volatility_like|volatility_like       | smooth_mul          |           11 |                  9 |               2 |                0 |           0.824476    |               1        |        0.02413     |           0.818182 |
| volatility_like|volatility_like       | spread_rank         |           11 |                  9 |               2 |                0 |           0.825338    |               0.954408 |        0.213124    |           0.818182 |
| basis_premium_like|price_like         | spread_rank         |           62 |                 51 |              11 |                0 |           0.997271    |               0.988081 |        0.406349    |           0.822581 |
| basis_premium_like|price_like         | mul                 |           34 |                 29 |               5 |                0 |           0.997558    |               0.95511  |        1.26871     |           0.852941 |
| basis_premium_like|volatility_like    | sub                 |           15 |                 13 |               2 |                0 |           0.826487    |               1        |        0.995997    |           0.866667 |
| basis_premium_like|price_like         | gated_sign          |           38 |                 33 |               5 |                0 |           0.996984    |               0.963292 |       13.4905      |           0.868421 |
| basis_premium_like|price_like         | sub                 |           27 |                 25 |               2 |                0 |           0.997989    |               0.99955  |       12.9684      |           0.925926 |
| price_like|volatility_like            | smooth_mul          |           15 |                 14 |               1 |                0 |           0.824476    |               0.999312 |        0.013791    |           0.933333 |
| basis_premium_like                    | single              |           38 |                 36 |               2 |                0 |           0.993393    |               1        |        0.994778    |           0.947368 |
| volatility_like                       | single              |           14 |                 14 |               0 |                0 |           0.827348    |               1        |        0.77494     |           1        |
| price_like|volatility_like            | gated_sign          |            4 |                  4 |               0 |                0 |           0.825338    |               1        |        0.0116505   |           1        |
| price_like                            | single              |            3 |                  3 |               0 |                0 |           0.999425    |               1        |        0.28863     |           1        |
| price_like|volatility_like            | sub                 |            1 |                  1 |               0 |                0 |           0.827348    |               1        |        0.0129138   |           1        |
| volatility_like|volatility_like       | gated_sign          |            1 |                  1 |               0 |                0 |           0.827348    |               1        |        0.00541432  |           1        |
| volatility_like|volatility_like       | mul                 |            1 |                  1 |               0 |                0 |           0.827348    |               1        |        0.00023495  |           1        |
| volatility_like|volatility_like       | safe_div_abs        |            1 |                  1 |               0 |                0 |           0.827348    |               1        |        0.49622     |           1        |
| volatility_like|volatility_like       | sub                 |            1 |                  1 |               0 |                0 |           0.827348    |               1        |        0.00508844  |           1        |

## Materialization By Field

| field                                |   usages |   activity_ok_rows |   inactive_rows |   eval_fail_rows |   median_finite_share |   median_nonzero_share |   activity_ok_rate |
|:-------------------------------------|---------:|-------------------:|----------------:|-----------------:|----------------------:|-----------------------:|-------------------:|
| funding_rate                         |      373 |                  0 |             373 |                0 |           0.000670305 |               0.958106 |           0        |
| index_close                          |      218 |                  0 |             218 |                0 |           0.000670305 |               0.958106 |           0        |
| mark_close                           |      142 |                  0 |             142 |                0 |           0.00067629  |               0.67481  |           0        |
| global_long_short_account_ratio_last |        9 |                  0 |               9 |                0 |           0.0033246   |               0.999083 |           0        |
| global_long_short_account_ratio_mean |        4 |                  0 |               4 |                0 |           0           |               0        |           0        |
| premium_close_bps                    |      411 |                301 |             110 |                0 |           0.993105    |               0.959232 |           0.73236  |
| mark_index_basis_bps                 |      522 |                396 |             126 |                0 |           0.993105    |               0.987463 |           0.758621 |
| realized_vol_168h                    |      179 |                145 |              34 |                0 |           0.825338    |               0.988895 |           0.810056 |
| realized_vol_24h                     |      151 |                123 |              28 |                0 |           0.825338    |               0.989031 |           0.81457  |
| trade_return_1h                      |      336 |                276 |              60 |                0 |           0.994111    |               0.987944 |           0.821429 |

## Inactive / Failed Examples

| blueprint_id             | semantic_pair                         | motif        | primary_field        | secondary_field   | status             |   finite_share |   nonzero_share | expression                                                                           |
|:-------------------------|:--------------------------------------|:-------------|:---------------------|:------------------|:-------------------|---------------:|----------------:|:-------------------------------------------------------------------------------------|
| a7ff24r_49641183569fa632 | basis_premium_like                    | single       | mark_index_basis_bps | nan               | inactive_or_sparse |              0 |               0 | ZScore(Mean(mark_index_basis_bps,1))                                                 |
| a7ff24r_5e3756c09dd9800d | basis_premium_like                    | single       | mark_index_basis_bps | nan               | inactive_or_sparse |              0 |               0 | Mean(mark_index_basis_bps,1)                                                         |
| a7ff24r_2ab082367c1b62e6 | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Sign(premium_close_bps))                    |
| a7ff24r_8df15a328689de4d | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Sign(ZScore(Mean(premium_close_bps,4))))    |
| a7ff24r_b4fdfbf0e95cd293 | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Sign(ZScore(Mean(premium_close_bps,1))))    |
| a7ff24r_be3665cc85e43910 | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Sign(ZScore(Mean(premium_close_bps,2))))    |
| a7ff24r_09c2ead438b1c084 | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(mark_index_basis_bps,Sign(ZScore(Mean(premium_close_bps,1))))                    |
| a7ff24r_12c28f14b2e253f4 | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(Mean(mark_index_basis_bps,1),Sign(premium_close_bps))                            |
| a7ff24r_6c90b9509851a83f | basis_premium_like|basis_premium_like | gated_sign   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(mark_index_basis_bps,Sign(Mean(premium_close_bps,1)))                            |
| a7ff24r_153150ce9f2b7614 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,2))                  |
| a7ff24r_32f3ba668bc38d03 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,8))                  |
| a7ff24r_45d7b4c784664282 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,8))                 |
| a7ff24r_565844b4b03d0c4e | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,1))                  |
| a7ff24r_5a5b2d36ce1bfa55 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,12))                |
| a7ff24r_66c8dc3dfd71fb92 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,4))                 |
| a7ff24r_b49a82ab946f4f0c | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,12))                 |
| a7ff24r_c07a5893014d3870 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Mean(premium_close_bps,4))                  |
| a7ff24r_c52d5fddec1c7cad | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,2))                 |
| a7ff24r_cf7da82540f43dfe | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(ZScore(Mean(mark_index_basis_bps,1)),Delta(premium_close_bps,1))                 |
| a7ff24r_20a079fcfdf25411 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(mark_index_basis_bps,ZScore(Mean(premium_close_bps,1)))                          |
| a7ff24r_6b29e664c1bd0c20 | basis_premium_like|basis_premium_like | mul          | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mul(Mean(mark_index_basis_bps,1),premium_close_bps)                                  |
| a7ff24r_52be692a8fb8d5ea | basis_premium_like|basis_premium_like | safe_div_abs | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | SafeDiv(ZScore(Mean(mark_index_basis_bps,1)),Abs(premium_close_bps))                 |
| a7ff24r_aecbde8439b14b81 | basis_premium_like|basis_premium_like | safe_div_abs | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | SafeDiv(ZScore(Mean(mark_index_basis_bps,1)),Abs(ZScore(Mean(premium_close_bps,2)))) |
| a7ff24r_ecdb104e2087e0e0 | basis_premium_like|basis_premium_like | safe_div_abs | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | SafeDiv(ZScore(Mean(mark_index_basis_bps,1)),Abs(ZScore(Mean(premium_close_bps,1)))) |
| a7ff24r_076aa62d106129ed | basis_premium_like|basis_premium_like | safe_div_abs | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | SafeDiv(mark_index_basis_bps,Abs(Mean(premium_close_bps,1)))                         |
| a7ff24r_298895bc6f870b0f | basis_premium_like|basis_premium_like | safe_div_abs | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | SafeDiv(Mean(mark_index_basis_bps,1),Abs(premium_close_bps))                         |
| a7ff24r_145b8196cae8d3f4 | basis_premium_like|basis_premium_like | smooth_mul   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mean(Mul(Mean(mark_index_basis_bps,1),ZScore(Mean(premium_close_bps,12))),4)         |
| a7ff24r_2623db2eecd780ec | basis_premium_like|basis_premium_like | smooth_mul   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mean(Mul(ZScore(Mean(mark_index_basis_bps,2)),Mean(premium_close_bps,1)),4)          |
| a7ff24r_2c52281e0f36e2ec | basis_premium_like|basis_premium_like | smooth_mul   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mean(Mul(Mean(mark_index_basis_bps,1),ZScore(Mean(premium_close_bps,8))),4)          |
| a7ff24r_2e4dbd744f3f6fec | basis_premium_like|basis_premium_like | smooth_mul   | mark_index_basis_bps | premium_close_bps | inactive_or_sparse |              0 |               0 | Mean(Mul(Mean(mark_index_basis_bps,1),ZScore(Mean(premium_close_bps,4))),4)          |
