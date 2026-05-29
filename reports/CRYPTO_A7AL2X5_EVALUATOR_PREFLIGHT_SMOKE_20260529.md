# CRYPTO A7AL-2X5 EVALUATOR PREFLIGHT SMOKE

## Decision

`PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT`

This stage evaluates A7AL-2X3 selected expressions on a bounded strict-universe sample. It does not compute returns, replay, candidate promotion, search, or proof.

## Summary

- selected candidates evaluated: 176
- eval failures: 0
- activity failures: 0
- symbols loaded: 96
- timestamps: 21025

## Candidate Evaluation Summary

| candidate_id             | objective_family                   | expression                                                                                | operator_signature                   | eval_success   |   finite_share |   nonzero_share | activity_ok   |     min_value |   max_value | error   |
|:-------------------------|:-----------------------------------|:------------------------------------------------------------------------------------------|:-------------------------------------|:---------------|---------------:|----------------:|:--------------|--------------:|------------:|:--------|
| a7al2x3_c6d040e141ee4a7a | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,12))),Winsor(ZScore(Delta(index_close,12))))   | Delta\|Mul\|Winsor\|ZScore           | True           |       0.997035 |        1        | True          |  -1.51932     |    1.72223  |         |
| a7al2x3_a685d04007266d3e | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,12)),Rank(Delta(index_close,12)))                       | Delta\|Mul\|Rank\|Sign               | True           |       0.997035 |        0.999997 | True          |  -1           |    1        |         |
| a7al2x3_7ea2d37cbc880c31 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,12)),ZScore(Delta(index_close,12)))                   | Delta\|Sub\|ZScore                   | True           |       0.997035 |        1        | True          |  -9.92559     |    9.99137  |         |
| a7al2x3_e2d80967eacd522d | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),12)),Rank(Mean(Delta(index_close,12),12)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.995883 |        0.992365 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_66e1442493b16731 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,168))),Winsor(ZScore(Delta(index_close,12))))  | Delta\|Mul\|Winsor\|ZScore           | True           |       0.989616 |        1        | True          |  -1.51932     |    1.72223  |         |
| a7al2x3_1c279a7fbcfa6e13 | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,12)),Rank(Delta(index_close,168)))                      | Delta\|Mul\|Rank\|Sign               | True           |       0.989461 |        0.999997 | True          |  -1           |    1        |         |
| a7al2x3_3e4ba1b6fdb0397c | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,168)),ZScore(Delta(index_close,12)))                  | Delta\|Sub\|ZScore                   | True           |       0.989616 |        1        | True          |  -9.96992     |    9.95545  |         |
| a7al2x3_20ce9622602f2b99 | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),168)),Rank(Mean(Delta(index_close,168),168)))  | Delta\|Mean\|Rank\|Sub               | True           |       0.989486 |        0.992968 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_93c3678f22a08669 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,24))),Winsor(ZScore(Delta(index_close,12))))   | Delta\|Mul\|Winsor\|ZScore           | True           |       0.996465 |        1        | True          |  -1.51932     |    1.72223  |         |
| a7al2x3_3059961b27c76009 | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,24)),Rank(Delta(index_close,12)))                       | Delta\|Mul\|Rank\|Sign               | True           |       0.996465 |        0.999999 | True          |  -1           |    1        |         |
| a7al2x3_938c8de15beb9e29 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,12)),ZScore(Delta(index_close,24)))                   | Delta\|Sub\|ZScore                   | True           |       0.996453 |        1        | True          |  -9.95376     |    9.9723   |         |
| a7al2x3_663a5ea1a6e2a66d | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),24)),Rank(Mean(Delta(index_close,24),24)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.994147 |        0.992391 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_4cd7689ef5bcda11 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,12))),Winsor(ZScore(Delta(index_close,336))))  | Delta\|Mul\|Winsor\|ZScore           | True           |       0.981304 |        1        | True          |  -1.25226     |    1.39172  |         |
| a7al2x3_0e80d16577ac1dd9 | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,12)),Rank(Delta(index_close,336)))                      | Delta\|Mul\|Rank\|Sign               | True           |       0.981304 |        0.999997 | True          |  -1           |    1        |         |
| a7al2x3_61dfe18f6d7e10a9 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,12)),ZScore(Delta(index_close,336)))                  | Delta\|Sub\|ZScore                   | True           |       0.981304 |        1        | True          |  -9.94593     |    9.91975  |         |
| a7al2x3_95dfb2b3cb785ab9 | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,336),336)),Rank(Mean(Delta(index_close,12),336)))  | Delta\|Mean\|Rank\|Sub               | True           |       0.981816 |        0.992247 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_035db391f91d7640 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,12))),Winsor(ZScore(Delta(index_close,48))))   | Delta\|Mul\|Winsor\|ZScore           | True           |       0.995287 |        1        | True          |  -1.43059     |    1.35477  |         |
| a7al2x3_3b50258a91cad453 | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,48)),Rank(Delta(index_close,12)))                       | Delta\|Mul\|Rank\|Sign               | True           |       0.995323 |        1        | True          |  -1           |    1        |         |
| a7al2x3_57e41e23954d044e | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,12)),ZScore(Delta(index_close,48)))                   | Delta\|Sub\|ZScore                   | True           |       0.995287 |        1        | True          |  -9.93377     |    9.97326  |         |
| a7al2x3_2c9cee28de17d79c | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),48)),Rank(Mean(Delta(index_close,48),48)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.995193 |        0.992923 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_5d5099aa43ee4989 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,12))),Winsor(ZScore(Delta(index_close,72))))   | Delta\|Mul\|Winsor\|ZScore           | True           |       0.994122 |        1        | True          |  -1.60542     |    1.60465  |         |
| a7al2x3_00fd86b46e479f6c | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,12)),Rank(Delta(index_close,72)))                       | Delta\|Mul\|Rank\|Sign               | True           |       0.994122 |        0.999997 | True          |  -1           |    1        |         |
| a7al2x3_08289a92830cd2f7 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,12)),ZScore(Delta(index_close,72)))                   | Delta\|Sub\|ZScore                   | True           |       0.994122 |        1        | True          |  -9.93901     |    9.96918  |         |
| a7al2x3_9f0dfda50390118b | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),72)),Rank(Mean(Delta(index_close,72),72)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.994052 |        0.993067 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_53e5c25552b81640 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,96))),Winsor(ZScore(Delta(index_close,12))))   | Delta\|Mul\|Winsor\|ZScore           | True           |       0.99304  |        1        | True          |  -1.60217     |    1.72223  |         |
| a7al2x3_61087f9eadca1cca | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,12)),Rank(Delta(index_close,96)))                       | Delta\|Mul\|Rank\|Sign               | True           |       0.992957 |        0.999997 | True          |  -1           |    1        |         |
| a7al2x3_2b7755a6d78e1583 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,96)),ZScore(Delta(index_close,12)))                   | Delta\|Sub\|ZScore                   | True           |       0.99304  |        1        | True          |  -9.92002     |   10.0011   |         |
| a7al2x3_1e0e44f981df087d | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,12),96)),Rank(Mean(Delta(index_close,96),96)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.99291  |        0.993259 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_1f183b54f4a341a6 | F0_OI_delta_price_interaction      | Mul(Winsor(ZScore(Delta(open_interest_last,168))),Winsor(ZScore(Delta(index_close,168)))) | Delta\|Mul\|Winsor\|ZScore           | True           |       0.989461 |        1        | True          |  -1.43041     |    1.39451  |         |
| a7al2x3_eade69f82268bb4c | F0_OI_delta_price_interaction      | Mul(Sign(Delta(open_interest_last,168)),Rank(Delta(index_close,168)))                     | Delta\|Mul\|Rank\|Sign               | True           |       0.989461 |        1        | True          |  -1           |    1        |         |
| a7al2x3_d990c6f9da5bc6c6 | F0_OI_delta_price_interaction      | Sub(ZScore(Delta(open_interest_last,168)),ZScore(Delta(index_close,168)))                 | Delta\|Sub\|ZScore                   | True           |       0.989461 |        1        | True          |  -9.9697      |    9.91843  |         |
| a7al2x3_1189ab9f925585e3 | F0_OI_delta_price_interaction      | Sub(Rank(Mean(Delta(open_interest_last,168),168)),Rank(Mean(Delta(index_close,168),168))) | Delta\|Mean\|Rank\|Sub               | True           |       0.989486 |        0.993134 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_8943bb8dd3c5f640 | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,168)),Neg(Rank(Mean(mark_index_basis_bps,168))))      | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.989795 |        1        | True          | -10.6834      |    9.61552  |         |
| a7al2x3_8133b78c17250336 | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,168))),Sign(Delta(open_interest_last,168)))     | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.989795 |        1        | True          |  -5           |    5        |         |
| a7al2x3_23f49936bc301294 | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,168)),ZScore(Mean(mark_index_basis_bps,168)))         | Delta\|Mean\|Sub\|ZScore             | True           |       0.989795 |        1        | True          | -11.5682      |   15.0155   |         |
| a7al2x3_4529f2a727b6c66c | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,168),168)),Rank(Mean(mark_index_basis_bps,168)))   | Delta\|Mean\|Rank\|Sub               | True           |       0.989652 |        0.990484 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_35d4fbc6ca2699b6 | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,168)),Neg(Rank(Mean(mark_index_basis_bps,336))))      | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.989961 |        1        | True          | -10.6777      |    9.61803  |         |
| a7al2x3_8bb8d4f5ef96c3aa | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,336))),Sign(Delta(open_interest_last,168)))     | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.989961 |        1        | True          |  -5           |    5        |         |
| a7al2x3_420f726f0f42a5ed | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,336)),ZScore(Mean(mark_index_basis_bps,168)))         | Delta\|Mean\|Sub\|ZScore             | True           |       0.981804 |        1        | True          | -11.9933      |   10.9539   |         |
| a7al2x3_cb0ca6d51a48f340 | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,336),168)),Rank(Mean(mark_index_basis_bps,168)))   | Delta\|Mean\|Rank\|Sub               | True           |       0.981662 |        0.990423 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_c4069bf78415ab2e | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,24)),Neg(Rank(Mean(mark_index_basis_bps,24))))        | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.996454 |        1        | True          | -10.6958      |    9.68545  |         |
| a7al2x3_0ae1469fb51e2b6d | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,24))),Sign(Delta(open_interest_last,24)))       | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.996454 |        0.999999 | True          |  -5           |    5        |         |
| a7al2x3_dd59069dfbb1ff68 | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,24)),ZScore(Mean(mark_index_basis_bps,24)))           | Delta\|Mean\|Sub\|ZScore             | True           |       0.996454 |        1        | True          | -13.2412      |   17.182    |         |
| a7al2x3_c0ae56385ca47ae5 | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,24),24)),Rank(Mean(mark_index_basis_bps,24)))      | Delta\|Mean\|Rank\|Sub               | True           |       0.9936   |        0.990378 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_4059c8d99e2021eb | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,168)),Neg(Rank(Mean(mark_index_basis_bps,24))))       | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.989605 |        1        | True          | -10.693       |    9.68534  |         |
| a7al2x3_db1512a14ebdd5d6 | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,168))),Sign(Delta(open_interest_last,24)))      | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.996644 |        0.999999 | True          |  -5           |    5        |         |
| a7al2x3_1cf0c31b9193f7b8 | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,24)),ZScore(Mean(mark_index_basis_bps,168)))          | Delta\|Mean\|Sub\|ZScore             | True           |       0.996644 |        1        | True          | -11.8977      |   11.4141   |         |
| a7al2x3_638792b42e418b1b | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,168),24)),Rank(Mean(mark_index_basis_bps,24)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.986323 |        0.990504 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_9733cada7099c087 | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,24)),Neg(Rank(Mean(mark_index_basis_bps,336))))       | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.99681  |        1        | True          | -10.675       |    9.61936  |         |
| a7al2x3_5a68f70e0e0cc8ee | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,336))),Sign(Delta(open_interest_last,24)))      | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.99681  |        0.999999 | True          |  -5           |    5        |         |
| a7al2x3_0eb97f169c988424 | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,336)),ZScore(Mean(mark_index_basis_bps,24)))          | Delta\|Mean\|Sub\|ZScore             | True           |       0.981619 |        1        | True          | -12.5542      |   15.5659   |         |
| a7al2x3_c0fd69123ab04b9a | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,336),24)),Rank(Mean(mark_index_basis_bps,24)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.978349 |        0.99068  | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_1de82f0ee352cb24 | F1_OI_basis_premium_interaction    | Add(ZScore(Delta(open_interest_last,48)),Neg(Rank(Mean(mark_index_basis_bps,24))))        | Add\|Delta\|Mean\|Neg\|Rank\|ZScore  | True           |       0.995312 |        1        | True          | -10.6913      |    9.68536  |         |
| a7al2x3_6a082122284b288f | F1_OI_basis_premium_interaction    | Mul(Clip(ZScore(Mean(mark_index_basis_bps,48))),Sign(Delta(open_interest_last,24)))       | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.996525 |        0.999999 | True          |  -5           |    5        |         |
| a7al2x3_8b831c7ca0a033b3 | F1_OI_basis_premium_interaction    | Sub(ZScore(Delta(open_interest_last,48)),ZScore(Mean(mark_index_basis_bps,24)))           | Delta\|Mean\|Sub\|ZScore             | True           |       0.995312 |        1        | True          | -12.9632      |   16.9031   |         |
| a7al2x3_394293e249f89817 | F1_OI_basis_premium_interaction    | Sub(Rank(Mean(Delta(open_interest_last,24),48)),Rank(Mean(mark_index_basis_bps,48)))      | Delta\|Mean\|Rank\|Sub               | True           |       0.996382 |        0.990287 | True          |  -0.989583    |    0.989583 |         |
| a7al2x3_dcf6359c32accfb4 | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,168))),Sign(Delta(open_interest_last,168)))    | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.217143 |        1        | True          |  -4.71001     |    4.68835  |         |
| a7al2x3_0bd3d497403b3991 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,168)),Neg(ZScore(Mean(funding_rate_abs_168h,168))))   | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.217143 |        1        | True          | -12.1833      |   10.6972   |         |
| a7al2x3_49318bc4563b3038 | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,168),168)),Rank(Mean(funding_rate_abs_168h,168)))  | Delta\|Mean\|Rank\|Sub               | True           |       0.217113 |        0.998245 | True          |  -0.989583    |    0.952381 |         |
| a7al2x3_2a3e04a7ef01524d | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,168)),Abs(ZScore(Mean(funding_rate_abs_168h,168))))     | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.217143 |        1        | True          |   1.1612e-06  |    4.46212  |         |
| a7al2x3_03902ab9f8781dff | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,168))),Sign(Delta(open_interest_last,336)))    | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.215478 |        1        | True          |  -4.39978     |    4.71001  |         |
| a7al2x3_70df65bfaee58429 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,336)),Neg(ZScore(Mean(funding_rate_abs_168h,168))))   | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.215478 |        1        | True          | -12.3694      |   10.7739   |         |
| a7al2x3_5d85b65deb198a29 | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,168),336)),Rank(Mean(funding_rate_abs_168h,336)))  | Delta\|Mean\|Rank\|Sub               | True           |       0.219693 |        0.998877 | True          |  -0.989583    |    0.967742 |         |
| a7al2x3_3da0bf5fd3bb9e5b | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,168)),Abs(ZScore(Mean(funding_rate_abs_168h,336))))     | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.219723 |        1        | True          |   1.61008e-07 |    4.26334  |         |
| a7al2x3_9794f9f4dde82087 | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,24))),Sign(Delta(open_interest_last,24)))      | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.21545  |        0.999998 | True          |  -4.79012     |    4.73382  |         |
| a7al2x3_c16bffb0672ac602 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,24)),Neg(ZScore(Mean(funding_rate_abs_168h,24))))     | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.21545  |        1        | True          | -12.7768      |   10.6622   |         |
| a7al2x3_775798753039c461 | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,24),24)),Rank(Mean(funding_rate_abs_168h,24)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.215084 |        0.998549 | True          |  -0.989583    |    0.967742 |         |
| a7al2x3_ad5d2776f048ebf4 | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,24)),Abs(ZScore(Mean(funding_rate_abs_168h,24))))       | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.21545  |        1        | True          |   1.54062e-07 |    4.60995  |         |
| a7al2x3_4ffc6837ac0783ef | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,24))),Sign(Delta(open_interest_last,168)))     | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.214931 |        1        | True          |  -4.79012     |    4.73742  |         |
| a7al2x3_34150540b7e6ab92 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,168)),Neg(ZScore(Mean(funding_rate_abs_168h,24))))    | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.214931 |        1        | True          | -12.8287      |   10.654    |         |
| a7al2x3_12d1702bc61eeacd | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,168),24)),Rank(Mean(funding_rate_abs_168h,24)))    | Delta\|Mean\|Rank\|Sub               | True           |       0.214247 |        0.998145 | True          |  -0.989583    |    0.952381 |         |
| a7al2x3_bb6e7c46cc25aa5a | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,24)),Abs(ZScore(Mean(funding_rate_abs_168h,168))))      | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.217662 |        1        | True          |   1.55728e-06 |    4.41067  |         |
| a7al2x3_3453ef7a612e7a2f | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,336))),Sign(Delta(open_interest_last,24)))     | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.220242 |        0.999998 | True          |  -4.7057      |    4.71001  |         |
| a7al2x3_0daaf09509efe600 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,24)),Neg(ZScore(Mean(funding_rate_abs_168h,336))))    | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.220242 |        1        | True          | -11.2597      |   10.5073   |         |
| a7al2x3_0731335cff9513ae | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,24),336)),Rank(Mean(funding_rate_abs_168h,336)))   | Delta\|Mean\|Rank\|Sub               | True           |       0.22044  |        0.998577 | True          |  -0.989583    |    0.967742 |         |
| a7al2x3_26ae0767ea7c70ac | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,24)),Abs(ZScore(Mean(funding_rate_abs_168h,336))))      | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.220242 |        1        | True          |   6.52162e-07 |    4.2908   |         |
| a7al2x3_40310d163311a69f | F2_OI_funding_crowding_interaction | Mul(Clip(ZScore(Mean(funding_rate_abs_168h,48))),Sign(Delta(open_interest_last,24)))      | Clip\|Delta\|Mean\|Mul\|Sign\|ZScore | True           |       0.215819 |        0.999998 | True          |  -4.73255     |    4.73276  |         |
| a7al2x3_ae18dc6b4e2103a5 | F2_OI_funding_crowding_interaction | Add(ZScore(Delta(open_interest_last,24)),Neg(ZScore(Mean(funding_rate_abs_168h,48))))     | Add\|Delta\|Mean\|Neg\|ZScore        | True           |       0.215819 |        1        | True          | -12.7909      |   10.6633   |         |
| a7al2x3_9bc2b62be2f535b9 | F2_OI_funding_crowding_interaction | Sub(Rank(Mean(Delta(open_interest_last,24),48)),Rank(Mean(funding_rate_abs_168h,48)))     | Delta\|Mean\|Rank\|Sub               | True           |       0.216017 |        0.998805 | True          |  -0.989583    |    0.967742 |         |
| a7al2x3_42dd14f0ee864118 | F2_OI_funding_crowding_interaction | Mul(Rank(Delta(open_interest_last,48)),Abs(ZScore(Mean(funding_rate_abs_168h,24))))       | Abs\|Delta\|Mean\|Mul\|Rank\|ZScore  | True           |       0.21545  |        1        | True          |   1.54062e-07 |    4.67382  |         |

## Operator Coverage

| operator        |   selected_candidate_count |
|:----------------|---------------------------:|
| Abs             |                          6 |
| Add             |                         18 |
| Clip            |                         18 |
| Delta           |                        164 |
| GroupNeutralize |                         30 |
| Mean            |                         80 |
| Mul             |                         70 |
| Neg             |                         18 |
| Rank            |                        112 |
| Sign            |                         44 |
| StateMask       |                         18 |
| Sub             |                         64 |
| Winsor          |                          8 |
| ZScore          |                         76 |

## Group Field Coverage

| group_field                        |   unique_values | values                                    |
|:-----------------------------------|----------------:|:------------------------------------------|
| R2_market_breadth_state            |               3 | breadth_mid\|breadth_strong\|breadth_weak |
| R3_liquidity_cycle_state           |               3 | liq_contracting\|liq_expanding\|liq_mid   |
| R4_leverage_crowding_state         |               3 | lev_high\|lev_low\|lev_mid                |
| R5_basis_premium_dislocation_state |               3 | basis_high\|basis_low\|basis_mid          |
| is_major                           |               2 | False\|True                               |
| liquidity_tier                     |               5 | tail\|top100\|top20\|top200\|top50        |

## Blockers

No blockers.

## Authorization

- numeric replay: not authorized
- formula generation/search: not authorized
- alpha proof / shadow / paper / live: not authorized
