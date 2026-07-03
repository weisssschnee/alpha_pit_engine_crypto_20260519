# CRYPTO A7SHADOW6 May Funding Repair

Generated: 2026-07-03T17:50:21Z

## Decision

`PASS_A7SHADOW6_MAY_FUNDING_REPAIR_PANEL_BUILT`

This stage builds a separate evaluator base panel with repaired Binance funding-rate events for the May 2026 stress window. It does not run search or authorize any trading stage.

## Counts

- symbol_count: `96`
- ok_symbol_count: `96`
- fetch_error_count: `0`
- dense_delta_stress_finite_share: `1.0`
- output_panel_root: `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704`

## Dense Stress Audit

| field                                 | split                |   hour_count |   finite_share |   nonzero_share |   symbol_with_any_finite |
|:--------------------------------------|:---------------------|-------------:|---------------:|----------------:|-------------------------:|
| raw_funding_rate                      | known_may2026_stress |          601 |       0.166753 |        0.166303 |                       96 |
| funding_rate_state_last_ffill_8h      | known_may2026_stress |          601 |       1        |        0.996395 |                       96 |
| funding_rate_delta_state_24h_ffill_8h | known_may2026_stress |          601 |       1        |        0.674761 |                       96 |
| premium_close_bps                     | known_may2026_stress |          601 |       0.998336 |        0.623509 |                       96 |
| open_interest_mean                    | known_may2026_stress |          601 |       1        |        1        |                       96 |

## Symbol Repair Manifest

| symbol        | status   | fetch_source                       | fetch_error   |   event_rows |   filled_rows |   repair_window_missing_before |   repair_window_missing_after |   stress_raw_funding_finite_share | output_path                                                                                                                                |
|:--------------|:---------|:-----------------------------------|:--------------|-------------:|--------------:|-------------------------------:|------------------------------:|----------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------|
| 1000BONKUSDT  | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000BONKUSDT\part.parquet  |
| 1000FLOKIUSDT | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000FLOKIUSDT\part.parquet |
| 1000LUNCUSDT  | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000LUNCUSDT\part.parquet  |
| 1000PEPEUSDT  | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000PEPEUSDT\part.parquet  |
| 1000RATSUSDT  | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000RATSUSDT\part.parquet  |
| 1000SATSUSDT  | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000SATSUSDT\part.parquet  |
| 1000SHIBUSDT  | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000SHIBUSDT\part.parquet  |
| 1000XECUSDT   | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1000XECUSDT\part.parquet   |
| 1INCHUSDT     | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=1INCHUSDT\part.parquet     |
| AAVEUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=AAVEUSDT\part.parquet      |
| ACEUSDT       | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ACEUSDT\part.parquet       |
| ACHUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ACHUSDT\part.parquet       |
| ADAUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ADAUSDT\part.parquet       |
| AGLDUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=AGLDUSDT\part.parquet      |
| ALGOUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ALGOUSDT\part.parquet      |
| ALICEUSDT     | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ALICEUSDT\part.parquet     |
| ALTUSDT       | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ALTUSDT\part.parquet       |
| ANKRUSDT      | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ANKRUSDT\part.parquet      |
| APEUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=APEUSDT\part.parquet       |
| API3USDT      | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=API3USDT\part.parquet      |
| APTUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=APTUSDT\part.parquet       |
| ARBUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ARBUSDT\part.parquet       |
| ARKMUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ARKMUSDT\part.parquet      |
| ARKUSDT       | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ARKUSDT\part.parquet       |
| ARPAUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ARPAUSDT\part.parquet      |
| ARUSDT        | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ARUSDT\part.parquet        |
| ASTRUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ASTRUSDT\part.parquet      |
| ATOMUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=ATOMUSDT\part.parquet      |
| AUCTIONUSDT   | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=AUCTIONUSDT\part.parquet   |
| AVAXUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=AVAXUSDT\part.parquet      |
| AXSUSDT       | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=AXSUSDT\part.parquet       |
| BANDUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BANDUSDT\part.parquet      |
| BATUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BATUSDT\part.parquet       |
| BCHUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BCHUSDT\part.parquet       |
| BEAMXUSDT     | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BEAMXUSDT\part.parquet     |
| BELUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BELUSDT\part.parquet       |
| BICOUSDT      | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BICOUSDT\part.parquet      |
| BIGTIMEUSDT   | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BIGTIMEUSDT\part.parquet   |
| BLURUSDT      | ok       | binance_vision_monthly_fundingRate |               |          157 |           151 |                            619 |                           468 |                          0.251248 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BLURUSDT\part.parquet      |
| BNBUSDT       | ok       | binance_vision_monthly_fundingRate |               |           79 |            76 |                            622 |                           546 |                          0.126456 | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704\symbol=BNBUSDT\part.parquet       |

## Manifest

```json
{
  "authorizes_a7shadow4_rerun": true,
  "authorizes_a7shadow5_rerun": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "base_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "data_manifest": "G:\\AlphaFactory_CryptoData\\manifests\\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704_manifest.csv",
  "decision": "PASS_A7SHADOW6_MAY_FUNDING_REPAIR_PANEL_BUILT",
  "dense_delta_stress_finite_share": 1.0,
  "fetch_error_count": 0,
  "generated_at": "2026-07-03T17:50:21Z",
  "ok_symbol_count": 96,
  "output_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704",
  "raw_cache_root": "G:\\AlphaFactory_CryptoData\\raw\\binance_api\\funding_rate_may2026_repair_v1_20260704",
  "repair_end": "2026-05-26T00:00:00Z",
  "repair_start": "2026-04-30T00:00:00Z",
  "runtime": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow6_may_funding_repair_20260704",
  "stage": "A7SHADOW-6",
  "symbol_count": 96,
  "vision_cache_root": "G:\\AlphaFactory_CryptoData\\raw\\binance_vision\\fundingRate_may2026_repair_v1_20260704"
}
```
