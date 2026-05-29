# CRYPTO A7AL-2Z4F BROADER NON-OI PREFLIGHT FORENSIC

Generated: 2026-05-29T03:48:31Z

## Decision

`HOLD_A7AL2Z4F_PRE_MAY_SIGNAL_CONTROL_OR_LAG_FRAGILE`

Z4F explains the Z4 numeric preflight hold. It does not run new replay, generation, training, or proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_same_pool_expansion": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 128,
  "control_dominated_count": 9,
  "decision": "HOLD_A7AL2Z4F_PRE_MAY_SIGNAL_CONTROL_OR_LAG_FRAGILE",
  "executes_forensic_only": true,
  "executes_generation": false,
  "executes_replay": false,
  "executes_training": false,
  "generated_at": "2026-05-29T03:48:31Z",
  "lag_fragile_count": 3,
  "may_veto_count": 0,
  "pre_may_positive_count": 12,
  "pre_may_unstable_count": 116,
  "stage": "A7AL-2Z4F",
  "stress_clean_count": 0,
  "uses_may_in_selector": false
}
```

## Family Failure Profile

| objective_family                         |   candidate_count |   pre_may_positive_count |   lag_ok_count |   may_stress_clean_count |   median_control_ratio |
|:-----------------------------------------|------------------:|-------------------------:|---------------:|-------------------------:|-----------------------:|
| Z0_funding_basis_premium_dislocation     |                16 |                        1 |              5 |                        4 |                4.45389 |
| Z1_price_range_volatility_structure      |                16 |                        2 |              8 |                        8 |                5.38596 |
| Z2_liquidity_taker_microstructure_lite   |                16 |                        2 |              8 |                        7 |               21.3299  |
| Z3_basis_price_trend_reversal            |                16 |                        0 |              6 |                        5 |               29.6796  |
| Z4_upper_regime_relative_value           |                16 |                        0 |              3 |                        0 |                2.91204 |
| Z5_latent_listing_meme_neutral_structure |                16 |                        4 |              7 |                       11 |               28.4792  |
| Z6_cross_sectional_relative_flow_value   |                16 |                        0 |              9 |                        9 |                5.32705 |
| Z7_market_regime_price_breadth           |                16 |                        3 |              8 |                        0 |               16.6116  |

## Family Decision Breakdown

| objective_family                         | decision                         |   count |
|:-----------------------------------------|:---------------------------------|--------:|
| Z0_funding_basis_premium_dislocation     | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      15 |
| Z0_funding_basis_premium_dislocation     | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |       1 |
| Z1_price_range_volatility_structure      | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      14 |
| Z1_price_range_volatility_structure      | HOLD_A7AL2Z4_CONTROL_DOMINATED   |       2 |
| Z2_liquidity_taker_microstructure_lite   | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      14 |
| Z2_liquidity_taker_microstructure_lite   | HOLD_A7AL2Z4_CONTROL_DOMINATED   |       2 |
| Z3_basis_price_trend_reversal            | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      16 |
| Z4_upper_regime_relative_value           | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      16 |
| Z5_latent_listing_meme_neutral_structure | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      12 |
| Z5_latent_listing_meme_neutral_structure | HOLD_A7AL2Z4_CONTROL_DOMINATED   |       3 |
| Z5_latent_listing_meme_neutral_structure | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |       1 |
| Z6_cross_sectional_relative_flow_value   | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      16 |
| Z7_market_regime_price_breadth           | HOLD_A7AL2Z4_PRE_MAY_UNSTABLE    |      13 |
| Z7_market_regime_price_breadth           | HOLD_A7AL2Z4_CONTROL_DOMINATED   |       2 |
| Z7_market_regime_price_breadth           | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |       1 |

## Control Summary

| objective_family                         | control_variant      |   median_control_ratio |   max_control_ratio |   dominated_count |
|:-----------------------------------------|:---------------------|-----------------------:|--------------------:|------------------:|
| Z0_funding_basis_premium_dislocation     | wrong_lag_future_24h |               1.59483  |           550.971   |                26 |
| Z0_funding_basis_premium_dislocation     | wrong_lag_stale_168h |               0.831417 |            60.6085  |                19 |
| Z0_funding_basis_premium_dislocation     | symbol_shuffle       |               0.598744 |            10.8823  |                17 |
| Z0_funding_basis_premium_dislocation     | time_shuffle         |               0.521797 |            39.3455  |                14 |
| Z0_funding_basis_premium_dislocation     | same_family_random   |               0.372257 |            29.6453  |                 7 |
| Z1_price_range_volatility_structure      | wrong_lag_future_24h |               2.49042  |           193.738   |                37 |
| Z1_price_range_volatility_structure      | wrong_lag_stale_168h |               1.01899  |            31.6636  |                25 |
| Z1_price_range_volatility_structure      | symbol_shuffle       |               0.77162  |            10.2813  |                20 |
| Z1_price_range_volatility_structure      | time_shuffle         |               0.453222 |            10.2178  |                14 |
| Z1_price_range_volatility_structure      | same_family_random   |               0.253634 |             2.28686 |                 5 |
| Z2_liquidity_taker_microstructure_lite   | wrong_lag_future_24h |               3.29736  |          1071.3     |                42 |
| Z2_liquidity_taker_microstructure_lite   | time_shuffle         |               0.739584 |           357.248   |                21 |
| Z2_liquidity_taker_microstructure_lite   | wrong_lag_stale_168h |               0.793049 |           521.19    |                21 |
| Z2_liquidity_taker_microstructure_lite   | same_family_random   |               0.412484 |           147.639   |                15 |
| Z2_liquidity_taker_microstructure_lite   | symbol_shuffle       |               0.582374 |           180.537   |                15 |
| Z3_basis_price_trend_reversal            | wrong_lag_future_24h |               8.96126  |           464.247   |                44 |
| Z3_basis_price_trend_reversal            | wrong_lag_stale_168h |               1.28027  |            24.8818  |                30 |
| Z3_basis_price_trend_reversal            | symbol_shuffle       |               0.701204 |            20.0791  |                20 |
| Z3_basis_price_trend_reversal            | time_shuffle         |               0.544763 |            24.5885  |                15 |
| Z3_basis_price_trend_reversal            | same_family_random   |               0.333394 |            14.9732  |                11 |
| Z4_upper_regime_relative_value           | wrong_lag_future_24h |               2.16129  |           464.247   |                30 |
| Z4_upper_regime_relative_value           | symbol_shuffle       |               0.566819 |            22.4312  |                14 |
| Z4_upper_regime_relative_value           | wrong_lag_stale_168h |               0.594803 |            24.8818  |                14 |
| Z4_upper_regime_relative_value           | time_shuffle         |               0.47114  |            13.9411  |                 9 |
| Z4_upper_regime_relative_value           | same_family_random   |               0.112877 |             6.68935 |                 2 |
| Z5_latent_listing_meme_neutral_structure | wrong_lag_future_24h |              12.3937   |           329.915   |                37 |
| Z5_latent_listing_meme_neutral_structure | symbol_shuffle       |               0.635876 |            85.3975  |                14 |
| Z5_latent_listing_meme_neutral_structure | wrong_lag_stale_168h |               0.628338 |            25.541   |                14 |
| Z5_latent_listing_meme_neutral_structure | time_shuffle         |               0.382526 |            27.8245  |                10 |
| Z5_latent_listing_meme_neutral_structure | same_family_random   |               0.210296 |            21.1711  |                 7 |
| Z6_cross_sectional_relative_flow_value   | wrong_lag_future_24h |               2.63849  |            31.1213  |                33 |
| Z6_cross_sectional_relative_flow_value   | wrong_lag_stale_168h |               0.529324 |            16.4544  |                16 |
| Z6_cross_sectional_relative_flow_value   | time_shuffle         |               0.510152 |            17.5143  |                14 |
| Z6_cross_sectional_relative_flow_value   | symbol_shuffle       |               0.505851 |            21.4422  |                12 |
| Z6_cross_sectional_relative_flow_value   | same_family_random   |               0.238109 |            27.5132  |                 9 |
| Z7_market_regime_price_breadth           | wrong_lag_future_24h |              10.3565   |           622.65    |                46 |
| Z7_market_regime_price_breadth           | wrong_lag_stale_168h |               0.910172 |            37.6068  |                21 |
| Z7_market_regime_price_breadth           | symbol_shuffle       |               0.561666 |            46.0384  |                13 |
| Z7_market_regime_price_breadth           | time_shuffle         |               0.417246 |            11.2572  |                12 |
| Z7_market_regime_price_breadth           | same_family_random   |               0.308843 |             1.685   |                 7 |

## Premay Near Misses

| candidate_id             | objective_family                         |   orientation_from_train |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread |   oriented_may_stress_spread |   may_stress_n_dates |   one_bar_lag_recent_oriented |   cost10_recent_proxy |   control_dominance_ratio_premay_max | pre_may_positive   | lag_ok   | may_stress_clean   | decision                         |
|:-------------------------|:-----------------------------------------|-------------------------:|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|---------------------:|------------------------------:|----------------------:|-------------------------------------:|:-------------------|:---------|:-------------------|:---------------------------------|
| a7al2z1_2785f094943ec26b | Z0_funding_basis_premium_dislocation     |                        1 |                  0.000364118 |            0.0026833   |              0.000537974 |                nan           |                    0 |                  -0.000687947 |          -0.00146203  |                              4.01028 | True               | False    | False              | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |
| a7al2z1_0f6949bf2fb808d8 | Z7_market_regime_price_breadth           |                       -1 |                  0.000884036 |            0.00129857  |              0.00110064  |                nan           |                    0 |                   0.000330947 |          -0.000899356 |                             13.3959  | True               | True     | False              | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_156476a0c1baf8a6 | Z7_market_regime_price_breadth           |                       -1 |                  0.000884036 |            0.00129857  |              0.00110064  |                nan           |                    0 |                   0.000330947 |          -0.000899356 |                             13.3959  | True               | True     | False              | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_06179c2b2c6fa22c | Z2_liquidity_taker_microstructure_lite   |                        1 |                  0.000385402 |            0.000242961 |              0.000111306 |                  0.000400182 |                  576 |                   0.000593247 |          -0.00188869  |                             21.3299  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_0a75fb1c32beed6e | Z2_liquidity_taker_microstructure_lite   |                        1 |                  0.000385402 |            0.000242961 |              0.000111306 |                nan           |                    0 |                   0.000593247 |          -0.00188869  |                             21.3299  | True               | True     | False              | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_004c9dd933b4db99 | Z5_latent_listing_meme_neutral_structure |                       -1 |                  0.00279483  |            0.0042652   |              0.00480494  |                  0.002767    |                  552 |                   0.0048621   |           0.00280494  |                             27.1227  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_23b1d0ac27d832c5 | Z5_latent_listing_meme_neutral_structure |                       -1 |                  0.002841    |            0.00308519  |              0.0045996   |                  0.00245154  |                  552 |                   0.00456499  |           0.0025996   |                             28.4792  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_1b2c2d5174c6f84b | Z5_latent_listing_meme_neutral_structure |                       -1 |                  0.00370857  |            0.00356552  |              0.00456453  |                  0.00225845  |                  552 |                   0.00472186  |           0.00256453  |                             29.8584  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_0137caa89f7a1268 | Z1_price_range_volatility_structure      |                       -1 |                  0.00015467  |            0.00368361  |              0.00743149  |                  0.00582935  |                  576 |                   0.0072796   |           0.00543149  |                             39.8954  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_0d64b81aeb0a9836 | Z7_market_regime_price_breadth           |                       -1 |                  0.000545496 |            0.000271928 |              0.000424451 |                nan           |                    0 |                  -0.000428519 |          -0.00157555  |                             42.7588  | True               | False    | False              | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |
| a7al2z1_2d6e3bd57d32e9b1 | Z1_price_range_volatility_structure      |                       -1 |                  0.000947606 |            0.00173451  |              0.00081687  |                  0.00104265  |                  576 |                   0.000327494 |          -0.00118313  |                             49.4747  | True               | True     | True               | HOLD_A7AL2Z4_CONTROL_DOMINATED   |
| a7al2z1_005d486584e1be09 | Z5_latent_listing_meme_neutral_structure |                       -1 |                  0.000410343 |            0.000551469 |              4.75356e-05 |                  0.00143208  |                  574 |                  -0.00101272  |          -0.00195246  |                            329.915   | True               | False    | True               | HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE |

## Boundary

```text
Same-pool expansion is not authorized.
The useful evidence is failure attribution: most candidates are pre-May unstable; the few pre-May positives are rejected by control or lag gates.
```
