# Crypto External Frontier Assimilation Sprint

Status: `CRYPTO_FRONTIER_ASSIMILATION_COMPLETED`
Main recommendation: `WAIT_FOR_EXTERNAL_DATA_WITH_ARENA_READY`
Outcome: `B_DATA_BOTTLENECK_WITH_ARENA_READY`

## Result

- Reproduced end to end: Qlib Alpha158/LightGBM/TopKDropout and scoped Deep Momentum LSTM/direct-Sharpe.
- Arena: `6` systems, `12` common bridge results and `8` native portfolio results.
- Weakest layer: `APPROVED_DATA_REPRESENTATION_AND_HISTORY_DEPTH`.
- Behaviour: N_eff `4.3189`, clusters `5`, top share `0.3333`.
- Migrated components: `none`.

## Common challenge comparison

| system_id                         |     net_mean |     net_lcb |   annualized_sharpe |   positive_month_fraction |   turnover_mean |   behaviour_overlap |
|:----------------------------------|-------------:|------------:|--------------------:|--------------------------:|----------------:|--------------------:|
| INTERNAL_FORMULA_20D_CS_MOMENTUM  |  1.71514e-05 | -0.00165781 |           0.0272723 |                      0.5  |        0.375461 |           1         |
| SIMPLE_ECONOMIC_20D_TSMOM         | -0.00455343  | -0.00663626 |          -3.36549   |                      0    |        0.245882 |           0.183829  |
| QLIB_ALPHA158_LIGHTGBM            |  0.000562614 | -0.00167941 |           0.966952  |                      0.75 |        0.986798 |          -0.139612  |
| QLIB_PRICE_KBAR_CONTROL           |  0.000375804 | -0.00174744 |           0.571     |                      0.5  |        1.30734  |          -0.0414891 |
| DEEP_MOMENTUM_LSTM                |  0.00109732  | -0.00411857 |           0.875445  |                      0.5  |        0.696428 |          -0.139434  |
| DEEP_MOMENTUM_NO_TURNOVER_CONTROL |  0.00116488  | -0.00408391 |           0.934253  |                      0.5  |        0.701432 |          -0.143898  |

## Native forecast evaluation

| system_id               | data_role   |        ic |      icir |     rank_ic |   rank_icir |   ic_days |
|:------------------------|:------------|----------:|----------:|------------:|------------:|----------:|
| QLIB_ALPHA158_LIGHTGBM  | DEVELOPMENT | 0.86189   | 9.49946   | 0.785605    |  5.30417    |       180 |
| QLIB_ALPHA158_LIGHTGBM  | CHALLENGE   | 0.0176777 | 0.0533643 | 0.000641507 |  0.00214781 |       121 |
| QLIB_PRICE_KBAR_CONTROL | DEVELOPMENT | 0.641856  | 3.36831   | 0.53803     |  2.63979    |       180 |
| QLIB_PRICE_KBAR_CONTROL | CHALLENGE   | 0.0239817 | 0.0649528 | 0.0629939   |  0.206359   |       121 |

## Matched component decisions

| component                                | challenger             | matched_control                   |   development_net_mean_increment |   challenge_net_mean_increment |   challenge_net_lcb |   challenge_positive_month_fraction |   behaviour_correlation_to_internal | migration_gate_passed   | decision                             |
|:-----------------------------------------|:-----------------------|:----------------------------------|---------------------------------:|-------------------------------:|--------------------:|------------------------------------:|------------------------------------:|:------------------------|:-------------------------------------|
| ALPHA158_REPRESENTATION_AND_CS_TARGET    | QLIB_ALPHA158_LIGHTGBM | QLIB_PRICE_KBAR_CONTROL           |                      0.00582697  |                    0.00018681  |         -0.00167941 |                                0.75 |                           -0.139612 | False                   | HOLD_NO_STABLE_DEVELOPMENT_INCREMENT |
| TURNOVER_AWARE_PORTFOLIO_FIRST_OBJECTIVE | DEEP_MOMENTUM_LSTM     | DEEP_MOMENTUM_NO_TURNOVER_CONTROL |                     -3.98982e-05 |                   -6.75609e-05 |         -0.00411857 |                                0.5  |                           -0.139434 | False                   | HOLD_NO_STABLE_DEVELOPMENT_INCREMENT |

## Layer attribution

- Data representation: `NO_STABLE_INCREMENT`.
- Target/horizon: `INSUFFICIENT_EVIDENCE_TO_REDEFINE`.
- Model expression: `NO_STABLE_INCREMENT`.
- Search/training: `EXTERNAL_FIXED_TRAINING_DID_NOT_REMOVE_DATA_BOTTLENECK`.
- Portfolio mapping: `PORTFOLIO_MAPPING_NOT_ALLOWED_TO_HIDE_FORECAST_FAILURE`.
- Regime/state: `NATIVE_LONG_REGIME_HISTORY_UNAVAILABLE`.
- Evaluator: `MULTI_PARADIGM_BRIDGE_IMPLEMENTED`.

The system cannot honestly infer that DeepLOB, full Momentum Transformer, native G-Research minute forecasting, or DeePM is ineffective. Those paradigms are data-incompatible with the currently qualified release. The result supports an Arena-first architecture and a direct external-data entry contract, while keeping formula search frozen.

## Scope and non-claims

- No validation, test, recent, May stress, sealed forward, promotion, or cross-sprint memory was accessed.
- The Jul-Oct role is the already-opened pre-forward challenge block from the qualified native aggTrades release; it is not untouched OOS.
- Bias audit: `HOLD_RESEARCH` because OOS grade is `NONE`.
- These are reproductions and architecture evidence, not alpha-ready or deployable candidates.

## External references

- Qlib Alpha158/LightGBM workflow: https://github.com/microsoft/qlib/blob/main/examples/benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
- Deep Momentum Networks: https://arxiv.org/abs/1904.04912v3
- Momentum Transformer companion code: https://github.com/kieranjwood/trading-momentum-transformer
- G-Research Crypto Forecasting: https://www.gresearch.com/news/wrapping-up-the-g-research-crypto-forecasting-competition/
- DeepLOB: https://github.com/zcakhaa/DeepLOB-Deep-Convolutional-Neural-Networks-for-Limit-Order-Books
- Digital-asset order-book model: https://arxiv.org/abs/2010.01241
- DeepDow: https://deepdow.readthedocs.io/
- FinRL: https://github.com/AI4Finance-Foundation/FinRL
- AlphaGen: https://github.com/ICT-FinD-Lab/alphagen
