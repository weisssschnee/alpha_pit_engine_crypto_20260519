# CRYPTO A7AK-LV3 Neutral Field-Family Smoke

Generated: 2026-05-26T19:15:14Z

## Decision

```text
PASS_A7AK_LV3_NEUTRAL_FIELD_FAMILY_DIAGNOSTIC_READY
```

LV3 compares fixed field-family signals under global, age-neutral, coarse-latent-neutral, and raw-latent-neutral ranking. It does not generate formulas and does not authorize promotion.

## Summary

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_broad_search": false,
  "authorizes_lv4_small_fixed_family_replay_design": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AK_LV3_NEUTRAL_FIELD_FAMILY_DIAGNOSTIC_READY",
  "diagnostic_survivors_age_and_coarse_latent": 12,
  "executes_fixed_field_family_diagnostic": true,
  "executes_formula_generation": false,
  "executes_search": false,
  "executes_tradable_replay": false,
  "generated_at": "2026-05-26T19:15:14Z",
  "input_base_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v1_20260525",
  "input_lv1_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
  "likely_age_or_latent_bias_signals": 1,
  "neutralization_modes": [
    "global",
    "age_neutral",
    "coarse_latent_neutral",
    "raw_latent_neutral"
  ],
  "sampled_rows": 342120,
  "signals_tested": 13,
  "timestamp_sample_caps": {
    "recent_2025H2_2026Apr": 384,
    "train_2024": 384,
    "validation_2025H1": 256
  },
  "warnings": [
    "LV3 uses IC/spread diagnostics, not executable book PnL",
    "Raw latent neutralization has lower coverage because groups are sparse",
    "May rows are unavailable and not used",
    "Signals that survive neutralization are diagnostic candidates only"
  ]
}
```

## Signal Decisions

| signal_name      | field_family    |   global_validation_mean_ic |   global_recent_mean_ic |   age_neutral_validation_mean_ic |   age_neutral_recent_mean_ic |   coarse_latent_validation_mean_ic |   coarse_latent_recent_mean_ic |   raw_latent_recent_valid_row_share | diagnostic_decision                               |
|:-----------------|:----------------|----------------------------:|------------------------:|---------------------------------:|-----------------------------:|-----------------------------------:|-------------------------------:|------------------------------------:|:--------------------------------------------------|
| age_x_liquidity  | age_interaction |                 -0.0122065  |             -0.0275416  |                      -0.0251475  |                  -0.0365612  |                        -0.010193   |                   -0.0130439   |                            0.635865 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| age_x_volatility | age_interaction |                 -0.0527491  |             -0.0765256  |                      -0.0594385  |                  -0.0727143  |                        -0.023022   |                   -0.0201036   |                            0.634915 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| basis_abs        | basis           |                 -0.016947   |             -0.0280265  |                      -0.00542832 |                  -0.0163199  |                         0.00321086 |                   -0.000723211 |                            0.635865 | LIKELY_LATENT_STATE_BIAS                          |
| premium_abs      | basis           |                 -0.0305917  |             -0.0352716  |                      -0.0171135  |                  -0.0294207  |                        -0.00316189 |                   -0.00582976  |                            0.635578 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| funding_abs      | funding         |                 -0.0415981  |             -0.0441063  |                      -0.0218316  |                  -0.0318594  |                        -0.0047461  |                   -0.00807845  |                            0.300409 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| liquidity_rank   | liquidity       |                 -0.0406432  |             -0.0405129  |                      -0.0286932  |                  -0.0383466  |                        -0.0134729  |                   -0.0150336   |                            0.635865 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| low_liquidity    | liquidity       |                  0.0406432  |              0.0405129  |                       0.0286932  |                   0.0383466  |                         0.0134729  |                    0.0150336   |                            0.635865 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| oi_change_24h    | positioning     |                 -0.00721668 |             -0.00730089 |                      -0.0057646  |                  -0.00745969 |                        -0.0106419  |                   -0.015621    |                            0.634678 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| oi_x_price_move  | positioning     |                 -0.0108942  |             -0.0221871  |                      -0.00839006 |                  -0.0229037  |                        -0.00538061 |                   -0.0120905   |                            0.634678 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| momentum_24h     | price           |                 -0.0349916  |             -0.0453524  |                      -0.042781   |                  -0.048766   |                        -0.03832    |                   -0.0511828   |                            0.635394 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| reversal_24h     | price           |                  0.0349916  |              0.0453524  |                       0.042781   |                   0.048766   |                         0.03832    |                    0.0511828   |                            0.635394 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| low_realized_vol | volatility      |                  0.0923791  |              0.0878333  |                       0.0605314  |                   0.0740298  |                         0.0235738  |                    0.0211155   |                            0.634915 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |
| realized_vol     | volatility      |                 -0.0923791  |             -0.0878333  |                      -0.0605314  |                  -0.0740298  |                        -0.0235738  |                   -0.0211155   |                            0.634915 | SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC |

## Timestamp Sample Audit

| split                 |   available_timestamps |   sampled_timestamps |   sample_cap |
|:----------------------|-----------------------:|---------------------:|-------------:|
| train_2024            |                   8784 |                  384 |          384 |
| validation_2025H1     |                   4344 |                  256 |          256 |
| recent_2025H2_2026Apr |                   7296 |                  384 |          384 |

## Validation / Recent Metrics

| signal_name      | field_family    | neutralization_mode   | split                 |   n_dates |   avg_n_obs |   valid_row_share |   valid_rows |      mean_ic |   ic_tstat |   positive_ic_rate |   mean_decile_spread |   decile_spread_tstat |   positive_spread_rate |
|:-----------------|:----------------|:----------------------|:----------------------|----------:|------------:|------------------:|-------------:|-------------:|-----------:|-------------------:|---------------------:|----------------------:|-----------------------:|
| low_realized_vol | volatility      | global                | recent_2025H2_2026Apr |       382 |    459.312  |          0.989419 |       338500 |  0.0878333   |  11.7412   |           0.725131 |          0.00838     |             4.98036   |               0.617801 |
| low_realized_vol | volatility      | age_neutral           | recent_2025H2_2026Apr |       382 |    459.154  |          0.988615 |       338225 |  0.0740298   |   9.89005  |           0.696335 |          0.00716479  |             4.8949    |               0.609948 |
| reversal_24h     | price           | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635394 |       217381 |  0.0581877   |   9.77687  |           0.719895 |          0.00516223  |             4.75767   |               0.617801 |
| reversal_24h     | price           | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.906816 |       310240 |  0.0511828   |   9.06761  |           0.696335 |          0.00381431  |             3.2875    |               0.609948 |
| reversal_24h     | price           | age_neutral           | recent_2025H2_2026Apr |       382 |    459.547  |          0.990284 |       338796 |  0.048766    |   7.66787  |           0.651832 |          0.00527112  |             3.83786   |               0.586387 |
| reversal_24h     | price           | global                | recent_2025H2_2026Apr |       382 |    459.704  |          0.991085 |       339070 |  0.0453524   |   6.57321  |           0.649215 |          0.00590257  |             3.85397   |               0.591623 |
| low_liquidity    | liquidity       | global                | recent_2025H2_2026Apr |       382 |    459.728  |          0.991658 |       339266 |  0.0405129   |   6.72606  |           0.612565 |          0.00576478  |             5.52622   |               0.60733  |
| low_liquidity    | liquidity       | age_neutral           | recent_2025H2_2026Apr |       382 |    459.571  |          0.990857 |       338992 |  0.0383466   |   6.39164  |           0.596859 |          0.0057063   |             5.85683   |               0.615183 |
| low_realized_vol | volatility      | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.634915 |       217217 |  0.0218685   |   3.08853  |           0.573298 |          0.001963    |             1.74988   |               0.518325 |
| low_realized_vol | volatility      | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.906287 |       310059 |  0.0211155   |   4.26266  |           0.60733  |          0.00286558  |             2.86311   |               0.573298 |
| low_liquidity    | liquidity       | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.907331 |       310416 |  0.0150336   |   3.46949  |           0.562827 |          0.00113851  |             1.50214   |               0.544503 |
| low_liquidity    | liquidity       | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635865 |       217542 |  0.0149739   |   3.09336  |           0.549738 |          0.000135601 |             0.180328  |               0.502618 |
| basis_abs        | basis           | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635865 |       217542 |  0.00531784  |   1.52018  |           0.549738 |          0.00101402  |             1.30503   |               0.554974 |
| basis_abs        | basis           | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    427.199  |          0.905799 |       309892 | -0.000723211 |  -0.186678 |           0.505236 |         -0.000219984 |            -0.268919  |               0.505236 |
| funding_abs      | funding         | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    205.335  |          0.300409 |       102776 | -0.00284955  |  -0.670892 |           0.471204 |          0.000201284 |             0.187861  |               0.502618 |
| premium_abs      | basis           | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    310.759  |          0.635578 |       217444 | -0.00333198  |  -0.881575 |           0.465969 |         -0.000663868 |            -0.906806  |               0.497382 |
| premium_abs      | basis           | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    427.696  |          0.906881 |       310262 | -0.00582976  |  -1.71104  |           0.481675 |         -0.000836532 |            -1.10812   |               0.47644  |
| oi_change_24h    | positioning     | global                | recent_2025H2_2026Apr |       382 |    459.387  |          0.989165 |       338413 | -0.00730089  |  -1.98359  |           0.434555 |         -0.00125043  |            -1.09743   |               0.486911 |
| oi_change_24h    | positioning     | age_neutral           | recent_2025H2_2026Apr |       382 |    459.23   |          0.98837  |       338141 | -0.00745969  |  -2.18334  |           0.421466 |         -0.000657419 |            -0.627462  |               0.463351 |
| funding_abs      | funding         | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    295.963  |          0.500962 |       171389 | -0.00807845  |  -1.85167  |           0.463351 |         -0.00196482  |            -1.78682   |               0.455497 |
| oi_x_price_move  | positioning     | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    427.924  |          0.905443 |       309770 | -0.0120905   |  -4.09038  |           0.410995 |         -0.00174888  |            -2.00863   |               0.460733 |
| age_x_liquidity  | age_interaction | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.907331 |       310416 | -0.0130439   |  -3.02716  |           0.465969 |         -0.0010229   |            -1.40739   |               0.468586 |
| age_x_liquidity  | age_interaction | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635865 |       217542 | -0.0142007   |  -2.92473  |           0.442408 |          0.000502864 |             0.643516  |               0.510471 |
| liquidity_rank   | liquidity       | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635865 |       217542 | -0.0149739   |  -3.09336  |           0.450262 |         -0.000135601 |            -0.180328  |               0.497382 |
| liquidity_rank   | liquidity       | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.907331 |       310416 | -0.0150336   |  -3.46949  |           0.437173 |         -0.00113851  |            -1.50214   |               0.455497 |
| oi_change_24h    | positioning     | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    427.924  |          0.905443 |       309770 | -0.015621    |  -5.20343  |           0.348168 |         -0.00281039  |            -3.36112   |               0.41623  |
| basis_abs        | basis           | age_neutral           | recent_2025H2_2026Apr |       382 |    458.5    |          0.989147 |       338407 | -0.0163199   |  -3.37029  |           0.431937 |         -0.00226404  |            -2.25772   |               0.484293 |
| oi_x_price_move  | positioning     | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.003  |          0.634678 |       217136 | -0.0173459   |  -5.24815  |           0.371728 |         -0.00350171  |            -3.99882   |               0.426702 |
| oi_change_24h    | positioning     | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.003  |          0.634678 |       217136 | -0.0181793   |  -5.45315  |           0.374346 |         -0.00341762  |            -4.13446   |               0.397906 |
| age_x_volatility | age_interaction | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.906287 |       310059 | -0.0201036   |  -3.94954  |           0.418848 |         -0.00230756  |            -2.27999   |               0.41623  |
| age_x_volatility | age_interaction | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.634915 |       217217 | -0.0210487   |  -2.94793  |           0.429319 |         -0.00168194  |            -1.52217   |               0.479058 |
| realized_vol     | volatility      | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.906287 |       310059 | -0.0211155   |  -4.26266  |           0.39267  |         -0.00286558  |            -2.86311   |               0.426702 |
| realized_vol     | volatility      | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.634915 |       217217 | -0.0218685   |  -3.08853  |           0.426702 |         -0.001963    |            -1.74988   |               0.481675 |
| oi_x_price_move  | positioning     | global                | recent_2025H2_2026Apr |       382 |    459.387  |          0.989165 |       338413 | -0.0221871   |  -6.5312   |           0.371728 |         -0.000983882 |            -0.836784  |               0.494764 |
| oi_x_price_move  | positioning     | age_neutral           | recent_2025H2_2026Apr |       382 |    459.23   |          0.98837  |       338141 | -0.0229037   |  -6.55037  |           0.361257 |         -0.00100564  |            -0.949577  |               0.507853 |
| age_x_liquidity  | age_interaction | global                | recent_2025H2_2026Apr |       382 |    459.728  |          0.991658 |       339266 | -0.0275416   |  -4.28699  |           0.447644 |         -0.00286459  |            -3.59829   |               0.434555 |
| basis_abs        | basis           | global                | recent_2025H2_2026Apr |       382 |    458.657  |          0.989948 |       338681 | -0.0280265   |  -4.60327  |           0.431937 |         -0.00214209  |            -1.69636   |               0.458115 |
| premium_abs      | basis           | age_neutral           | recent_2025H2_2026Apr |       382 |    459.058  |          0.99022  |       338774 | -0.0294207   |  -7.59473  |           0.350785 |         -0.00472265  |            -4.32423   |               0.426702 |
| funding_abs      | funding         | age_neutral           | recent_2025H2_2026Apr |       382 |    330.12   |          0.588776 |       201432 | -0.0318594   |  -7.10198  |           0.356021 |         -0.00551746  |            -4.2866    |               0.424084 |
| premium_abs      | basis           | global                | recent_2025H2_2026Apr |       382 |    459.215  |          0.991021 |       339048 | -0.0352716   |  -8.93892  |           0.324607 |         -0.00574455  |            -4.63366   |               0.426702 |
| age_x_liquidity  | age_interaction | age_neutral           | recent_2025H2_2026Apr |       382 |    459.571  |          0.990857 |       338992 | -0.0365612   |  -6.06903  |           0.395288 |         -0.00463785  |            -4.89563   |               0.397906 |
| liquidity_rank   | liquidity       | age_neutral           | recent_2025H2_2026Apr |       382 |    459.571  |          0.990857 |       338992 | -0.0383466   |  -6.39164  |           0.403141 |         -0.0057063   |            -5.85683   |               0.384817 |
| liquidity_rank   | liquidity       | global                | recent_2025H2_2026Apr |       382 |    459.728  |          0.991658 |       339266 | -0.0405129   |  -6.72606  |           0.387435 |         -0.00576478  |            -5.52622   |               0.39267  |
| funding_abs      | funding         | global                | recent_2025H2_2026Apr |       382 |    330.33   |          0.589659 |       201734 | -0.0441063   |  -8.27151  |           0.348168 |         -0.00538451  |            -3.72373   |               0.434555 |
| momentum_24h     | price           | global                | recent_2025H2_2026Apr |       382 |    459.704  |          0.991085 |       339070 | -0.0453524   |  -6.57321  |           0.350785 |         -0.00590257  |            -3.85397   |               0.408377 |
| momentum_24h     | price           | age_neutral           | recent_2025H2_2026Apr |       382 |    459.547  |          0.990284 |       338796 | -0.048766    |  -7.66787  |           0.348168 |         -0.00527112  |            -3.83786   |               0.413613 |
| momentum_24h     | price           | coarse_latent_neutral | recent_2025H2_2026Apr |       382 |    428.073  |          0.906816 |       310240 | -0.0511828   |  -9.06761  |           0.303665 |         -0.00381431  |            -3.2875    |               0.390052 |
| momentum_24h     | price           | raw_latent_neutral    | recent_2025H2_2026Apr |       382 |    311.016  |          0.635394 |       217381 | -0.0581877   |  -9.77687  |           0.280105 |         -0.00516223  |            -4.75767   |               0.382199 |
| age_x_volatility | age_interaction | age_neutral           | recent_2025H2_2026Apr |       382 |    459.154  |          0.988615 |       338225 | -0.0727143   |  -9.65122  |           0.301047 |         -0.00756051  |            -5.18744   |               0.382199 |
| realized_vol     | volatility      | age_neutral           | recent_2025H2_2026Apr |       382 |    459.154  |          0.988615 |       338225 | -0.0740298   |  -9.89005  |           0.303665 |         -0.00716479  |            -4.8949    |               0.390052 |
| age_x_volatility | age_interaction | global                | recent_2025H2_2026Apr |       382 |    459.312  |          0.989419 |       338500 | -0.0765256   |  -9.96047  |           0.295812 |         -0.00754079  |            -4.73226   |               0.387435 |
| realized_vol     | volatility      | global                | recent_2025H2_2026Apr |       382 |    459.312  |          0.989419 |       338500 | -0.0878333   | -11.7412   |           0.274869 |         -0.00838     |            -4.98036   |               0.382199 |
| low_realized_vol | volatility      | global                | validation_2025H1     |       254 |    323.283  |          0.989419 |       338500 |  0.0923791   |   5.82895  |           0.645669 |          0.00858626  |             3.12722   |               0.602362 |
| low_realized_vol | volatility      | age_neutral           | validation_2025H1     |       254 |    323.283  |          0.988615 |       338225 |  0.0605314   |   4.15545  |           0.602362 |          0.00494236  |             2.22516   |               0.562992 |
| reversal_24h     | price           | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635394 |       217381 |  0.0481397   |   5.65547  |           0.669291 |          0.000559793 |             0.49531   |               0.562992 |
| reversal_24h     | price           | age_neutral           | validation_2025H1     |       254 |    323.839  |          0.990284 |       338796 |  0.042781    |   4.1275   |           0.61811  |          0.00178075  |             1.11575   |               0.543307 |
| low_liquidity    | liquidity       | global                | validation_2025H1     |       254 |    323.862  |          0.991658 |       339266 |  0.0406432   |   4.61621  |           0.586614 |          0.00436046  |             3.36266   |               0.566929 |
| reversal_24h     | price           | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.906816 |       310240 |  0.03832     |   4.79478  |           0.653543 |          0.00218212  |             1.64816   |               0.582677 |
| reversal_24h     | price           | global                | validation_2025H1     |       254 |    323.839  |          0.991085 |       339070 |  0.0349916   |   3.15469  |           0.594488 |          0.000834908 |             0.429878  |               0.559055 |
| low_liquidity    | liquidity       | age_neutral           | validation_2025H1     |       254 |    323.862  |          0.990857 |       338992 |  0.0286932   |   3.33732  |           0.570866 |          0.000916097 |             0.844323  |               0.527559 |
| low_realized_vol | volatility      | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.634915 |       217217 |  0.0265639   |   2.49144  |           0.547244 |          0.00210743  |             1.57365   |               0.551181 |
| low_realized_vol | volatility      | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.906287 |       310059 |  0.0235738   |   3.06593  |           0.574803 |          0.0021899   |             1.47425   |               0.535433 |
| funding_abs      | funding         | raw_latent_neutral    | validation_2025H1     |       245 |     52.4898 |          0.300409 |       102776 |  0.022257    |   2.40845  |           0.555102 |          0.00195158  |             1.13426   |               0.579592 |
| low_liquidity    | liquidity       | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635865 |       217542 |  0.0184981   |   3.09313  |           0.559055 |          0.00138498  |             2.03236   |               0.562992 |
| low_liquidity    | liquidity       | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.907331 |       310416 |  0.0134729   |   2.91648  |           0.566929 |          0.000805038 |             1.07249   |               0.543307 |
| basis_abs        | basis           | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635865 |       217542 |  0.00822566  |   1.67683  |           0.543307 |          0.000639524 |             0.929206  |               0.488189 |
| basis_abs        | basis           | coarse_latent_neutral | validation_2025H1     |       254 |    287.197  |          0.905799 |       309892 |  0.00321086  |   0.633894 |           0.523622 |          0.000654312 |             0.795985  |               0.511811 |
| premium_abs      | basis           | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635578 |       217444 | -0.00158221  |  -0.291842 |           0.496063 |          0.000815234 |             1.18101   |               0.53937  |
| premium_abs      | basis           | coarse_latent_neutral | validation_2025H1     |       254 |    287.484  |          0.906881 |       310262 | -0.00316189  |  -0.75147  |           0.503937 |         -0.000259388 |            -0.291253  |               0.507874 |
| funding_abs      | funding         | coarse_latent_neutral | validation_2025H1     |       254 |    148.335  |          0.500962 |       171389 | -0.0047461   |  -0.680977 |           0.480315 |          0.000332535 |             0.220617  |               0.503937 |
| oi_x_price_move  | positioning     | coarse_latent_neutral | validation_2025H1     |       254 |    287.449  |          0.905443 |       309770 | -0.00538061  |  -1.11448  |           0.484252 |         -0.000726632 |            -0.723496  |               0.464567 |
| basis_abs        | basis           | age_neutral           | validation_2025H1     |       254 |    323.575  |          0.989147 |       338407 | -0.00542832  |  -0.837621 |           0.480315 |         -0.00158272  |            -1.41596   |               0.468504 |
| oi_change_24h    | positioning     | age_neutral           | validation_2025H1     |       254 |    323.343  |          0.98837  |       338141 | -0.0057646   |  -1.28779  |           0.437008 |         -0.00199757  |            -1.89844   |               0.429134 |
| oi_change_24h    | positioning     | global                | validation_2025H1     |       254 |    323.343  |          0.989165 |       338413 | -0.00721668  |  -1.54095  |           0.468504 |         -0.00200974  |            -1.72637   |               0.417323 |
| oi_x_price_move  | positioning     | age_neutral           | validation_2025H1     |       254 |    323.343  |          0.98837  |       338141 | -0.00839006  |  -1.69569  |           0.444882 |         -0.00102462  |            -0.861204  |               0.468504 |
| oi_change_24h    | positioning     | raw_latent_neutral    | validation_2025H1     |       254 |    165.748  |          0.634678 |       217136 | -0.00926077  |  -1.7286   |           0.42126  |         -9.61845e-05 |            -0.117258  |               0.480315 |
| age_x_liquidity  | age_interaction | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.907331 |       310416 | -0.010193    |  -2.13882  |           0.429134 |         -0.00094393  |            -1.26047   |               0.468504 |
| oi_change_24h    | positioning     | coarse_latent_neutral | validation_2025H1     |       254 |    287.449  |          0.905443 |       309770 | -0.0106419   |  -2.41671  |           0.417323 |         -0.0023143   |            -2.44968   |               0.433071 |
| oi_x_price_move  | positioning     | global                | validation_2025H1     |       254 |    323.343  |          0.989165 |       338413 | -0.0108942   |  -2.06868  |           0.448819 |         -0.00218942  |            -1.55203   |               0.444882 |
| age_x_liquidity  | age_interaction | global                | validation_2025H1     |       254 |    323.862  |          0.991658 |       339266 | -0.0122065   |  -1.43424  |           0.46063  |          7.5658e-05  |             0.0825856 |               0.464567 |
| oi_x_price_move  | positioning     | raw_latent_neutral    | validation_2025H1     |       254 |    165.748  |          0.634678 |       217136 | -0.0124387   |  -2.32886  |           0.433071 |         -0.000914261 |            -1.10542   |               0.448819 |
| liquidity_rank   | liquidity       | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.907331 |       310416 | -0.0134729   |  -2.91648  |           0.433071 |         -0.000805038 |            -1.07249   |               0.456693 |
| basis_abs        | basis           | global                | validation_2025H1     |       254 |    323.575  |          0.989948 |       338681 | -0.016947    |  -2.49802  |           0.429134 |         -0.00362037  |            -2.90359   |               0.437008 |
| premium_abs      | basis           | age_neutral           | validation_2025H1     |       254 |    323.776  |          0.99022  |       338774 | -0.0171135   |  -3.53753  |           0.389764 |         -0.00227101  |            -2.08598   |               0.448819 |
| liquidity_rank   | liquidity       | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635865 |       217542 | -0.0184981   |  -3.09313  |           0.440945 |         -0.00138498  |            -2.03236   |               0.437008 |
| age_x_liquidity  | age_interaction | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635865 |       217542 | -0.0193361   |  -3.18993  |           0.437008 |         -0.00163025  |            -2.29968   |               0.429134 |
| funding_abs      | funding         | age_neutral           | validation_2025H1     |       254 |    185.732  |          0.588776 |       201432 | -0.0218316   |  -3.39343  |           0.405512 |         -0.00150049  |            -0.926317  |               0.425197 |
| age_x_volatility | age_interaction | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.906287 |       310059 | -0.023022    |  -3.00564  |           0.433071 |         -0.00233993  |            -1.54108   |               0.448819 |
| realized_vol     | volatility      | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.906287 |       310059 | -0.0235738   |  -3.06593  |           0.425197 |         -0.0021899   |            -1.47425   |               0.464567 |
| age_x_liquidity  | age_interaction | age_neutral           | validation_2025H1     |       254 |    323.862  |          0.990857 |       338992 | -0.0251475   |  -2.92247  |           0.433071 |         -0.000707674 |            -0.66935   |               0.464567 |
| age_x_volatility | age_interaction | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.634915 |       217217 | -0.0264753   |  -2.48209  |           0.472441 |         -0.00181009  |            -1.37456   |               0.468504 |
| realized_vol     | volatility      | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.634915 |       217217 | -0.0265639   |  -2.49144  |           0.452756 |         -0.00210743  |            -1.57365   |               0.448819 |
| liquidity_rank   | liquidity       | age_neutral           | validation_2025H1     |       254 |    323.862  |          0.990857 |       338992 | -0.0286932   |  -3.33732  |           0.429134 |         -0.000916097 |            -0.844323  |               0.472441 |
| premium_abs      | basis           | global                | validation_2025H1     |       254 |    323.776  |          0.991021 |       339048 | -0.0305917   |  -5.70671  |           0.338583 |         -0.00569304  |            -3.84099   |               0.370079 |
| momentum_24h     | price           | global                | validation_2025H1     |       254 |    323.839  |          0.991085 |       339070 | -0.0349916   |  -3.15469  |           0.405512 |         -0.000834908 |            -0.429878  |               0.440945 |
| momentum_24h     | price           | coarse_latent_neutral | validation_2025H1     |       254 |    287.524  |          0.906816 |       310240 | -0.03832     |  -4.79478  |           0.346457 |         -0.00218212  |            -1.64816   |               0.417323 |
| liquidity_rank   | liquidity       | global                | validation_2025H1     |       254 |    323.862  |          0.991658 |       339266 | -0.0406432   |  -4.61621  |           0.413386 |         -0.00436046  |            -3.36266   |               0.433071 |
| funding_abs      | funding         | global                | validation_2025H1     |       254 |    185.732  |          0.589659 |       201734 | -0.0415981   |  -5.65414  |           0.366142 |         -0.00555237  |            -3.0093    |               0.413386 |
| momentum_24h     | price           | age_neutral           | validation_2025H1     |       254 |    323.839  |          0.990284 |       338796 | -0.042781    |  -4.1275   |           0.38189  |         -0.00178075  |            -1.11575   |               0.456693 |
| momentum_24h     | price           | raw_latent_neutral    | validation_2025H1     |       254 |    165.78   |          0.635394 |       217381 | -0.0481397   |  -5.65547  |           0.330709 |         -0.000559793 |            -0.49531   |               0.437008 |
| age_x_volatility | age_interaction | global                | validation_2025H1     |       254 |    323.283  |          0.989419 |       338500 | -0.0527491   |  -3.52191  |           0.413386 |         -0.00400416  |            -1.756     |               0.444882 |
| age_x_volatility | age_interaction | age_neutral           | validation_2025H1     |       254 |    323.283  |          0.988615 |       338225 | -0.0594385   |  -4.07806  |           0.405512 |         -0.00463972  |            -2.14284   |               0.429134 |
| realized_vol     | volatility      | age_neutral           | validation_2025H1     |       254 |    323.283  |          0.988615 |       338225 | -0.0605314   |  -4.15545  |           0.397638 |         -0.00494236  |            -2.22516   |               0.437008 |
| realized_vol     | volatility      | global                | validation_2025H1     |       254 |    323.283  |          0.989419 |       338500 | -0.0923791   |  -5.82895  |           0.354331 |         -0.00858626  |            -3.12722   |               0.397638 |

## Neutralization Coverage

| signal_name      | field_family    | neutralization_mode   |   valid_row_share |   valid_rows |   min_group_size |
|:-----------------|:----------------|:----------------------|------------------:|-------------:|-----------------:|
| momentum_24h     | price           | global                |          0.991085 |       339070 |                1 |
| momentum_24h     | price           | age_neutral           |          0.990284 |       338796 |                5 |
| momentum_24h     | price           | coarse_latent_neutral |          0.906816 |       310240 |                5 |
| momentum_24h     | price           | raw_latent_neutral    |          0.635394 |       217381 |                5 |
| reversal_24h     | price           | global                |          0.991085 |       339070 |                1 |
| reversal_24h     | price           | age_neutral           |          0.990284 |       338796 |                5 |
| reversal_24h     | price           | coarse_latent_neutral |          0.906816 |       310240 |                5 |
| reversal_24h     | price           | raw_latent_neutral    |          0.635394 |       217381 |                5 |
| liquidity_rank   | liquidity       | global                |          0.991658 |       339266 |                1 |
| liquidity_rank   | liquidity       | age_neutral           |          0.990857 |       338992 |                5 |
| liquidity_rank   | liquidity       | coarse_latent_neutral |          0.907331 |       310416 |                5 |
| liquidity_rank   | liquidity       | raw_latent_neutral    |          0.635865 |       217542 |                5 |
| low_liquidity    | liquidity       | global                |          0.991658 |       339266 |                1 |
| low_liquidity    | liquidity       | age_neutral           |          0.990857 |       338992 |                5 |
| low_liquidity    | liquidity       | coarse_latent_neutral |          0.907331 |       310416 |                5 |
| low_liquidity    | liquidity       | raw_latent_neutral    |          0.635865 |       217542 |                5 |
| realized_vol     | volatility      | global                |          0.989419 |       338500 |                1 |
| realized_vol     | volatility      | age_neutral           |          0.988615 |       338225 |                5 |
| realized_vol     | volatility      | coarse_latent_neutral |          0.906287 |       310059 |                5 |
| realized_vol     | volatility      | raw_latent_neutral    |          0.634915 |       217217 |                5 |
| low_realized_vol | volatility      | global                |          0.989419 |       338500 |                1 |
| low_realized_vol | volatility      | age_neutral           |          0.988615 |       338225 |                5 |
| low_realized_vol | volatility      | coarse_latent_neutral |          0.906287 |       310059 |                5 |
| low_realized_vol | volatility      | raw_latent_neutral    |          0.634915 |       217217 |                5 |
| funding_abs      | funding         | global                |          0.589659 |       201734 |                1 |
| funding_abs      | funding         | age_neutral           |          0.588776 |       201432 |                5 |
| funding_abs      | funding         | coarse_latent_neutral |          0.500962 |       171389 |                5 |
| funding_abs      | funding         | raw_latent_neutral    |          0.300409 |       102776 |                5 |
| basis_abs        | basis           | global                |          0.989948 |       338681 |                1 |
| basis_abs        | basis           | age_neutral           |          0.989147 |       338407 |                5 |
| basis_abs        | basis           | coarse_latent_neutral |          0.905799 |       309892 |                5 |
| basis_abs        | basis           | raw_latent_neutral    |          0.635865 |       217542 |                5 |
| premium_abs      | basis           | global                |          0.991021 |       339048 |                1 |
| premium_abs      | basis           | age_neutral           |          0.99022  |       338774 |                5 |
| premium_abs      | basis           | coarse_latent_neutral |          0.906881 |       310262 |                5 |
| premium_abs      | basis           | raw_latent_neutral    |          0.635578 |       217444 |                5 |
| oi_change_24h    | positioning     | global                |          0.989165 |       338413 |                1 |
| oi_change_24h    | positioning     | age_neutral           |          0.98837  |       338141 |                5 |
| oi_change_24h    | positioning     | coarse_latent_neutral |          0.905443 |       309770 |                5 |
| oi_change_24h    | positioning     | raw_latent_neutral    |          0.634678 |       217136 |                5 |
| oi_x_price_move  | positioning     | global                |          0.989165 |       338413 |                1 |
| oi_x_price_move  | positioning     | age_neutral           |          0.98837  |       338141 |                5 |
| oi_x_price_move  | positioning     | coarse_latent_neutral |          0.905443 |       309770 |                5 |
| oi_x_price_move  | positioning     | raw_latent_neutral    |          0.634678 |       217136 |                5 |
| age_x_liquidity  | age_interaction | global                |          0.991658 |       339266 |                1 |
| age_x_liquidity  | age_interaction | age_neutral           |          0.990857 |       338992 |                5 |
| age_x_liquidity  | age_interaction | coarse_latent_neutral |          0.907331 |       310416 |                5 |
| age_x_liquidity  | age_interaction | raw_latent_neutral    |          0.635865 |       217542 |                5 |
| age_x_volatility | age_interaction | global                |          0.989419 |       338500 |                1 |
| age_x_volatility | age_interaction | age_neutral           |          0.988615 |       338225 |                5 |
| age_x_volatility | age_interaction | coarse_latent_neutral |          0.906287 |       310059 |                5 |
| age_x_volatility | age_interaction | raw_latent_neutral    |          0.634915 |       217217 |                5 |

## Bias Boundary Audit

| check                | status   | detail                                                                                 |
|:---------------------|:---------|:---------------------------------------------------------------------------------------|
| candidate_set        | PASS     | fixed field-family list only; no generated formulas                                    |
| neutralization_modes | PASS     | global, age-neutral, coarse-latent-neutral, raw-latent-neutral are reported separately |
| may_usage            | PASS     | May rows are unavailable and not used                                                  |
| promotion_boundary   | PASS     | LV3 is diagnostic IC/spread smoke, not tradable replay or alpha proof                  |
| cost_boundary        | WARN     | no executable turnover/cost book is run in LV3                                         |

## Boundary

```text
AUTHORIZED NEXT:
  A7AK-LV4 small fixed-family neutral replay design, only for signals that survive age/coarse-latent diagnostics

NOT AUTHORIZED:
  broad formula search
  alpha proof
  shadow / paper / live

INTERPRETATION:
  Global-only signal = likely age/state exposure.
  Age-neutral survival but coarse-latent failure = likely latent state bias.
  Survival under age and coarse latent = diagnostic candidate only, not alpha proof.
```
