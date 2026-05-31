# CRYPTO A7FF-CORE9E BOUNDED REPLAY EXECUTION

Generated: 2026-05-31T23:55:53Z

## Decision

`PASS_A7FFCORE9E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE10`

A7FF-CORE9E executes a bounded replay proxy for the CORE9 packet. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core10_contract": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 114,
  "decision": "PASS_A7FFCORE9E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE10",
  "eval_error_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-05-31T23:55:53Z",
  "next_allowed": "A7FF-CORE10 replay-clean consolidation / search-readiness contract",
  "replay_clean_candidate_count": 27,
  "replay_clean_motif_bucket_count": 6,
  "replay_clean_semantic_bucket_count": 8,
  "replay_rows": 1368,
  "sample_rows": 383696,
  "sample_timestamp_count": 1152,
  "source_decision": "PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E",
  "source_stage": "A7FF-CORE9",
  "stage": "A7FF-CORE9E"
}
```

## Family Summary

| semantic_bucket                      | motif_bucket        |   candidate_count |   clean_candidate_count |   median_cost_adjusted_spread |   median_control_ratio |
|:-------------------------------------|:--------------------|------------------:|------------------------:|------------------------------:|-----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock     |                12 |                       9 |                  -0.000209708 |               1.17451  |
| taker_flow_like\|open_interest_like  | flow_x_leverage     |                24 |                       4 |                  -0.000698123 |               2.28533  |
| taker_flow_like                      | single              |                15 |                       3 |                  -0.000959032 |               3.30606  |
| open_interest_like                   | single              |                 5 |                       3 |                   0.000458633 |               0.424597 |
| liquidity_like                       | single              |                 6 |                       2 |                  -0.000940031 |               1.19759  |
| open_interest_like\|positioning_like | delta_x_divergence  |                 2 |                       2 |                   0.0232658   |               6.521    |
| volatility_like                      | single              |                 2 |                       2 |                   0.000959793 |               0.925087 |
| liquidity_like\|volatility_like      | safe_div_abs        |                12 |                       1 |                  -0.000988543 |               2.08824  |
| taker_flow_like\|basis_premium_like  | gated_sign          |                 7 |                       1 |                  -0.000916588 |               1.93896  |
| open_interest_like\|price_like       | mean_reversion_gate |                24 |                       0 |                  -0.00062326  |               3.55578  |
| open_interest_like                   | delta_x_divergence  |                 3 |                       0 |                   0.00252727  |               4.49251  |
| liquidity_like                       | liquidity_shock     |                 2 |                       0 |                  -0.00169483  |               3.88075  |

## Candidate Summary

| candidate_id                 | semantic_bucket                      | motif_bucket        |   replay_rows |   positive_validation_recent_cost5 |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |
|:-----------------------------|:-------------------------------------|:--------------------|--------------:|-----------------------------------:|----------------:|------------------------------:|------------:|--------------------:|
| a7ffcore5_9e4293913b29d39f8d | liquidity_like                       | single              |            12 |                                  1 |    -7.75828e-05 |                  -0.000777583 |    3.03917  |          0.0935175  |
| a7ffcore5_89d456568ed9db84c6 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.00108754  |                   0.000126979 |    2.87115  |          0.463453   |
| a7ffcore5_d495bcdff277541a9d | open_interest_like                   | single              |            12 |                                  1 |    -0.000168621 |                  -0.000522229 |    2.73639  |          0.375304   |
| a7ffcore5_f8f5a7d388d98ddbee | liquidity_like                       | single              |            12 |                                  1 |     0.000243087 |                  -0.000766885 |    2.6959   |          0.430438   |
| a7ffcore5_e49456a170f19eb240 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000672356 |                  -0.000192275 |    2.64209  |          0.395994   |
| a7ffcore5_056264aa1859f3ac7b | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000902823 |                  -5.58321e-05 |    2.61125  |          0.481281   |
| a7ffcore5_f12228440913b31bb1 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000928672 |                   8.1032e-05  |    2.5691   |          0.337463   |
| a7ffcore5_11903004dcea88bab8 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.0006366   |                  -0.000241338 |    2.55517  |          0.406357   |
| a7ffcore5_20349c393fc8912b86 | taker_flow_like                      | single              |            12 |                                  1 |     0.000149236 |                  -0.000879444 |    2.40812  |          0.275308   |
| a7ffcore5_b9beb4fd43cf7914e2 | taker_flow_like\|basis_premium_like  | gated_sign          |            12 |                                  1 |     0.000109995 |                  -0.000388594 |    2.38193  |          0.752219   |
| a7ffcore5_b594b57d1ee90136c4 | volatility_like                      | single              |            12 |                                  1 |     0.00149178  |                   0.000760421 |    2.33048  |          0.430835   |
| a7ffcore5_1f8c481e4c787863b8 | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  1 |     0.000599414 |                  -2.5231e-05  |    2.30678  |          0.1645     |
| a7ffcore5_155172eb90a4ffee4e | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000724418 |                  -0.000318438 |    2.24876  |          0.0815097  |
| a7ffcore5_55d479db927df299ef | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000637922 |                  -8.20563e-05 |    2.18659  |          0.191493   |
| a7ffcore5_0460706c8101b16f2f | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000547767 |                  -0.000440432 |    2.16686  |          0.222972   |
| a7ffcore5_89d2049d11221f570d | volatility_like                      | single              |            12 |                                  1 |     0.00201492  |                   0.000959793 |    2.10062  |          0.445537   |
| a7ffcore5_4a1f7c7ea34e49f970 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  1 |     0.000638752 |                  -4.11492e-05 |    1.96614  |          0.0615944  |
| a7ffcore5_be5c080d95c8a13e44 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  1 |     0.000144825 |                  -0.000555175 |    1.94236  |          0.158157   |
| a7ffcore5_ff02da2fd4f0d8e0e9 | open_interest_like                   | single              |            12 |                                  1 |     0.0765483   |                   0.0758483   |    1.70762  |          0.0893407  |
| a7ffcore5_636578f5c6f8790d3d | open_interest_like                   | single              |            12 |                                  1 |     0.0811696   |                   0.0804696   |    1.39492  |          0.184241   |
| a7ffcore5_e87b3041b2d66982dc | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  1 |     0.000730168 |                  -0.000433062 |    1.24609  |          0.179302   |
| a7ffcore5_24de13cbccf306e9bd | open_interest_like\|positioning_like | delta_x_divergence  |            12 |                                  1 |     0.0410904   |                   0.0403904   |    1.24115  |          0.655423   |
| a7ffcore5_6527a26f6a35191da1 | open_interest_like\|positioning_like | delta_x_divergence  |            12 |                                  1 |     0.0074413   |                   0.0067413   |    1.20975  |          0.0916841  |
| a7ffcore5_74463938d5563b479a | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  1 |     4.61075e-05 |                  -0.000510776 |    1.20875  |          0.597168   |
| a7ffcore5_fe463430faa60b809b | taker_flow_like                      | single              |            12 |                                  1 |     0.0272224   |                   0.0265224   |    1.13539  |          0.86938    |
| a7ffcore5_b4246145a5fe0becc1 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  1 |    -0.00419408  |                  -0.00489408  |    0.909577 |          0.709413   |
| a7ffcore5_e47c061c959d628ecb | taker_flow_like                      | single              |            12 |                                  1 |     0.0602835   |                   0.0595835   |    0.887775 |          0.220917   |
| a7ffcore5_1f43d8b7466f67685b | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000149127 |                  -0.000692389 |    2.44966  |          0.312187   |
| a7ffcore5_b39e253ad9a5084d9a | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000144596 |                  -0.000736483 |    2.35379  |          1.2614     |
| a7ffcore5_2545209b43e8b162b7 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     6.11497e-05 |                  -0.000796672 |    2.30199  |          0.193649   |
| a7ffcore5_1c5baae90be2044d1c | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     3.38795e-05 |                  -0.000559656 |    2.15143  |          0.785322   |
| a7ffcore5_b8522de8b6805b1c4c | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.00024038  |                  -0.000455013 |    1.89872  |          1.82607    |
| a7ffcore5_fe6ab6fb0843878019 | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |     0.000395763 |                  -0.000292122 |    1.87627  |          1.32512    |
| a7ffcore5_7f1edcbee2c722cdf1 | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |     0.000562325 |                  -0.000224339 |    1.86676  |          0.00462475 |
| a7ffcore5_cd7c08a204b1d4b10e | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000112895 |                  -0.000347812 |    1.8525   |          2.03335    |
| a7ffcore5_6591c5e3e78f0eb755 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |    -0.000194527 |                  -0.00065918  |    1.83586  |          0.0231458  |
| a7ffcore5_347cfd7114f3a1ae41 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  0 |     0.000885941 |                  -0.000145366 |    1.78254  |          0.257663   |
| a7ffcore5_b064580d00c38b06a9 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     1.74303e-05 |                  -0.000628127 |    1.77461  |          0.852219   |
| a7ffcore5_2904ff05e6bb681dbc | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |    -0.000156846 |                  -0.000856846 |    1.76524  |          0.527187   |
| a7ffcore5_0d36019628d9445207 | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |     0.000243966 |                  -0.000336593 |    1.73985  |          2.43063    |
| a7ffcore5_63939f40a439f34abb | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |    -0.000355073 |                  -0.000835727 |    1.72038  |          0.290536   |
| a7ffcore5_abd21a5a171736e21e | liquidity_like                       | single              |            12 |                                  0 |    -2.17522e-06 |                  -0.000571039 |    1.69579  |          0.648804   |
| a7ffcore5_736118f153d95df58b | liquidity_like                       | single              |            12 |                                  0 |     8.04788e-05 |                  -0.000393765 |    1.57419  |          0.936397   |
| a7ffcore5_25b2704821ce1d532b | taker_flow_like\|basis_premium_like  | gated_sign          |            12 |                                  0 |     8.66807e-05 |                  -0.000332943 |    1.48341  |          0.968895   |
| a7ffcore5_3f91329ef2964f3fc7 | taker_flow_like\|basis_premium_like  | gated_sign          |            12 |                                  0 |    -0.00451336  |                  -0.00521336  |    1.43432  |          1.79001    |
| a7ffcore5_f478e18da8849c8f7e | taker_flow_like\|basis_premium_like  | gated_sign          |            12 |                                  0 |    -0.00227428  |                  -0.00297428  |    1.4341   |          1.52596    |
| a7ffcore5_93ba861b3b4f99be53 | liquidity_like                       | single              |            12 |                                  0 |    -0.000922052 |                  -0.0013268   |    1.39301  |          0.336008   |
| a7ffcore5_6bc9223f8acc9c7e0b | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000647189 |                  -0.00046838  |    1.38809  |          0.66955    |
| a7ffcore5_22f94c55c49a93d48b | taker_flow_like                      | single              |            12 |                                  0 |     3.3933e-05  |                  -0.000565276 |    1.38596  |          1.23422    |
| a7ffcore5_c5ecfea1d2af189266 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |    -0.000419874 |                  -0.000917495 |    1.35977  |          0.231667   |
| a7ffcore5_2ba317cc57140f6f9f | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000153161 |                  -0.000615823 |    1.31769  |          2.02126    |
| a7ffcore5_f414f2621b03d718f6 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |    -0.000397088 |                  -0.000863033 |    1.27096  |          0.193169   |
| a7ffcore5_5868db3efa1fa51de5 | liquidity_like                       | single              |            12 |                                  0 |    -0.141497    |                  -0.142197    |    1.26076  |          0.0285155  |
| a7ffcore5_c50f6e97fe917f4167 | taker_flow_like                      | single              |            12 |                                  0 |    -0.000470081 |                  -0.000921699 |    1.18362  |          1.66058    |
| a7ffcore5_cc640529861c49f97b | taker_flow_like                      | single              |            12 |                                  0 |     0.00926695  |                   0.00856695  |    1.17216  |          0.260165   |
| a7ffcore5_3bebbf951fb4027ab4 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.000374614 |                  -0.000640284 |    1.13949  |          0.0425999  |
| a7ffcore5_c105fe668fa7685fa6 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.000374614 |                  -0.000640284 |    1.13949  |          0.0425999  |
| a7ffcore5_0c0b5ec3c3ea91900d | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000164144 |                  -0.000617104 |    1.13803  |          1.93799    |
| a7ffcore5_c84732657e9ffe68d5 | liquidity_like                       | liquidity_shock     |            12 |                                  0 |    -0.104652    |                  -0.105352    |    1.06327  |          0.414987   |
| a7ffcore5_7851200536e69a684f | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |    -0.000488516 |                  -0.000939765 |    1.04841  |          1.74155    |
| a7ffcore5_3d1036bce80ff6e4e8 | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     0.000451462 |                  -0.000248538 |    1.04792  |          0.591424   |
| a7ffcore5_b14219288b18bf0b0c | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |    -9.89324e-05 |                  -0.00105722  |    1.04477  |          0.685438   |
| a7ffcore5_ead6f57d703b25a5ae | taker_flow_like\|open_interest_like  | flow_x_leverage     |            12 |                                  0 |     2.38367e-05 |                  -0.000616748 |    1.04193  |          3.70004    |
| a7ffcore5_390ea2e8b9236b3198 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.000514311 |                  -0.000554474 |    1.01037  |          0.260094   |
| a7ffcore5_f687ee1e9ed95c3b67 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.000514311 |                  -0.000554474 |    1.01037  |          0.260094   |
| a7ffcore5_6695074813549a8bc9 | taker_flow_like                      | single              |            12 |                                  0 |     0.027168    |                   0.026468    |    1.00681  |          1.80341    |
| a7ffcore5_e5244edd9837f40696 | open_interest_like                   | single              |            12 |                                  0 |    -0.00044937  |                  -0.00112475  |    0.988748 |          0.381344   |
| a7ffcore5_134c181d2d0d0a7a0d | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  0 |     5.8023e-05  |                  -0.000570138 |    0.953691 |          2.5563     |
| a7ffcore5_c3db204b4025d59ad1 | taker_flow_like\|basis_premium_like  | gated_sign          |            12 |                                  0 |     0.000258772 |                  -0.000445794 |    0.927894 |          3.18509    |
| a7ffcore5_1366945af1d14e8e7b | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |    -0.000241186 |                  -0.000651563 |    0.861941 |          0.317199   |
| a7ffcore5_1caefe1090deb89fed | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |    -0.000241186 |                  -0.000651563 |    0.861941 |          0.317199   |
| a7ffcore5_94147d9c33bfe08943 | taker_flow_like                      | single              |            12 |                                  0 |    -0.000676054 |                  -0.00108455  |    0.859992 |          4.70762    |
| a7ffcore5_e7f5d8fab7b8470b71 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     1.51002e-05 |                  -0.000550236 |    0.858314 |          4.75695    |
| a7ffcore5_6f285061a4d5fa2922 | liquidity_like\|volatility_like      | liquidity_shock     |            12 |                                  0 |    -1.44236e-05 |                  -0.000616047 |    0.837653 |          3.08513    |
| a7ffcore5_08bebdf81544e01497 | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.00465814  |                   0.00396045  |    0.805559 |          6.33407    |
| a7ffcore5_5a0eb1293d5ed37629 | taker_flow_like                      | single              |            12 |                                  0 |    -0.0205116   |                  -0.0212116   |    0.802448 |          0.265801   |
| a7ffcore5_65b597049ca5e0b759 | open_interest_like                   | single              |            12 |                                  0 |     0.000544491 |                  -0.000109019 |    0.800893 |          0.161015   |
| a7ffcore5_e8b09c1c628442bb96 | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |    -0.0374435   |                  -0.0381435   |    0.787786 |          1.39026    |
| a7ffcore5_6681094b87ee50474f | open_interest_like\|price_like       | mean_reversion_gate |            12 |                                  0 |     0.000181081 |                  -0.000782727 |    0.759484 |          6.64907    |
| a7ffcore5_74192e756c0281059e | liquidity_like\|volatility_like      | safe_div_abs        |            12 |                                  0 |    -0.000805481 |                  -0.00157717  |    0.749841 |          0.245202   |

## Boundary

```text
bounded replay proxy: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
