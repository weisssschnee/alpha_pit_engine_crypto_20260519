# CRYPTO A7AC-2 Preflight Current Coverage Gap Scan

Generated: 2026-05-22T10:51:04Z

## Decision

`HOLD_A7AC2_PREFLIGHT_EXPANDED_PANEL_NOT_PRESENT`

A7AC-2 preflight checks what already exists locally and converts the A7AC-1 contract into concrete P0 backfill batches. It does not download data, build panels, run replay, or authorize search.

## Current Gold Inventory

| path                                                                                               | exists   |   rows |   columns |   symbols | symbol_list                                                                                        | timestamp_min             | timestamp_max             | read_error   | dataset                                             |
|:---------------------------------------------------------------------------------------------------|:---------|-------:|----------:|----------:|:---------------------------------------------------------------------------------------------------|:--------------------------|:--------------------------|:-------------|:----------------------------------------------------|
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_v1.parquet                                 | True     | 251148 |        -1 |        12 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |              | crypto_core12_1h_v1                                 |
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet         | True     | 251148 |        -1 |        12 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |              | crypto_core12_1h_with_aggtrades_features_v1         |
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet | True     | 251148 |        -1 |        12 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |              | crypto_core12_1h_with_aggtrades_metrics_features_v1 |
| G:\AlphaFactory_CryptoData\gold\features\binance_metrics_1h_features_v1.parquet                    | True     | 251028 |        -1 |        12 | ADAUSDT,AVAXUSDT,BCHUSDT,BNBUSDT,BTCUSDT,DOGEUSDT,ETHUSDT,LINKUSDT,LTCUSDT,SOLUSDT,SUIUSDT,XRPUSDT | 2024-01-01 00:00:00+00:00 | 2026-05-22 00:00:00+00:00 |              | binance_metrics_1h_features_v1                      |
| G:\AlphaFactory_CryptoData\gold\panels\crypto_expanded_1h_v1.parquet                               | False    |      0 |         0 |         0 |                                                                                                    |                           |                           |              | crypto_expanded_1h_v1                               |
| G:\AlphaFactory_CryptoData\gold\panels\crypto_core48_1h_v1.parquet                                 | False    |      0 |         0 |         0 |                                                                                                    |                           |                           |              | crypto_core48_1h_v1                                 |
| G:\AlphaFactory_CryptoData\gold\panels\crypto_liquid80_1h_v1.parquet                               | False    |      0 |         0 |         0 |                                                                                                    |                           |                           |              | crypto_liquid80_1h_v1                               |

## Symbol Gap Summary

| track                            | a7ac2_status              |   symbols |   p0_backfill_needed |
|:---------------------------------|:--------------------------|----------:|---------------------:|
| baseline_core12_existing         | READY_EXISTING_CORE12     |        12 |                    0 |
| primary_core48_top36_addition    | MISSING_P0_EXPANDED_PANEL |        36 |                   36 |
| secondary_liquid80_eligible_pool | MISSING_P0_EXPANDED_PANEL |        47 |                   47 |

## Missing Primary Additions

| symbol        | tier             | priority              | a7ac2_status              |
|:--------------|:-----------------|:----------------------|:--------------------------|
| ALGOUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| CELOUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ACHUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| APEUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ARUSDT        | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ATOMUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| CHZUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| DASHUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| GMXUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| LRCUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| MAGICUSDT     | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| MASKUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| NEARUSDT      | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| SEIUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| UNIUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| YFIUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ZECUSDT       | core48_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| BLURUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| BOMEUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ETCUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| HBARUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| KNCUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| MANAUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| PENDLEUSDT    | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| WLDUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| 1000BONKUSDT  | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| 1000FLOKIUSDT | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| 1INCHUSDT     | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| AAVEUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ACEUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| API3USDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| APTUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| ARBUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| AXSUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| BANDUSDT      | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| BATUSDT       | midcap_candidate | P0_backfill_contract  | MISSING_P0_EXPANDED_PANEL |
| BIGTIMEUSDT   | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| CFXUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| COMPUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| CRVUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| DOTUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| DYDXUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| EGLDUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ENJUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ETHFIUSDT     | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| FILUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| FLOWUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| GALAUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| GMTUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ICPUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| IMXUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| INJUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| IOTAUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| JTOUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| JUPUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| KSMUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| LDOUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| LPTUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| LQTYUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| MEMEUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| MINAUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| NOTUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ONDOUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| OPUSDT        | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ORDIUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| PYTHUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| QTUMUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| RSRUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| SANDUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| SNXUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| SSVUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| STRKUSDT      | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| STXUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| SUSHIUSDT     | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| TIAUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| TRBUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| TRXUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| XLMUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| XTZUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |
| ZILUSDT       | midcap_candidate | P1_secondary_contract | MISSING_P0_EXPANDED_PANEL |

## P0 Backfill Batch Plan

| batch_id   | source_family           |   jobs | symbols                                                                                                                                                                                                                                                                                                                       |
|:-----------|:------------------------|-------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| P0B01      | futures_trade_klines_1m |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |
| P0B02      | mark_price_klines_1m    |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |
| P0B03      | index_price_klines_1m   |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |
| P0B04      | premium_index_klines_1m |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |
| P0B05      | funding_rate            |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |
| P0B06      | binance_metrics_daily   |     36 | 1000BONKUSDT,1000FLOKIUSDT,1INCHUSDT,AAVEUSDT,ACEUSDT,ACHUSDT,ALGOUSDT,APEUSDT,API3USDT,APTUSDT,ARBUSDT,ARUSDT,ATOMUSDT,AXSUSDT,BANDUSDT,BATUSDT,BLURUSDT,BOMEUSDT,CELOUSDT,CHZUSDT,DASHUSDT,ETCUSDT,GMXUSDT,HBARUSDT,KNCUSDT,LRCUSDT,MAGICUSDT,MANAUSDT,MASKUSDT,NEARUSDT,PENDLEUSDT,SEIUSDT,UNIUSDT,WLDUSDT,YFIUSDT,ZECUSDT |

## Authorization

| decision                                        | generated_at         | executes_download   | executes_panel_build   | executes_search   | executes_replay   |   core12_existing_symbols |   primary_addition_symbols |   secondary_pool_symbols | expanded_gold_panel_exists   |   primary_additions_missing_p0_panel |   p0_batch_jobs | authorizes_data_line_execution   | authorizes_search   | authorizes_large_search   | authorizes_alpha_proof   | authorizes_shadow_paper_live   | required_next                                                                                                                                                                                                                                                                        |
|:------------------------------------------------|:---------------------|:--------------------|:-----------------------|:------------------|:------------------|--------------------------:|---------------------------:|-------------------------:|:-----------------------------|-------------------------------------:|----------------:|:---------------------------------|:--------------------|:--------------------------|:-------------------------|:-------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| HOLD_A7AC2_PREFLIGHT_EXPANDED_PANEL_NOT_PRESENT | 2026-05-22T10:51:04Z | False               | False                  | False             | False             |                        12 |                         36 |                       47 | False                        |                                   36 |             216 | True                             | False               | False                     | False                    | False                          | ['Execute P0B01-P0B06 backfill batches for primary_core48 additions', 'Build crypto_expanded_1h_v1 or crypto_core48_1h_v1 gold panel', 'Run A7AC-2 full source trace/panel integrity audit after expanded panel exists', 'Run A7AC-3 listing/survivorship policy before any replay'] |

## Required Next Action

1. Data line runs P0B01-P0B06 for the 36 primary additions.
2. Build an expanded 1h gold panel only after raw/source traces are closed.
3. Re-run this A7AC-2 script; decision should move from HOLD to panel-integrity audit if expanded panel exists.
4. Do not run formula search until A7AC-2 panel audit and A7AC-3 listing/survivorship policy pass.
