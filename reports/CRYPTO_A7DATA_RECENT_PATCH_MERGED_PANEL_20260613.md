# CRYPTO A7DATA Recent Patch Merged Panel 20260613

## Decision

`PASS_A7DATA_RECENT_PATCH_MERGED_PANEL_READY_FOR_CONTROLLED_EXPERIMENT`

This builds a patch-aware controlled-experiment panel by replacing the overlapping main-panel boundary hour with the richer recent patch row and adding observed first-seen age controls. It does not authorize alpha proof.

## Summary

- output root: `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613`
- symbols: `498`
- rows: `7152282`
- timestamp_min: `2024-01-01 00:00:00`
- timestamp_max: `2026-06-11 23:00:00`
- overlap_rows_dropped: `498`
- duplicate_after_merge: `0`
- inf_cells: `0`
- mean_premium_close_bps_coverage: `0.9989331571508395`
- mean_mark_index_basis_bps_coverage: `0.9965212588837079`
- mean_funding_rate_coverage: `0.24172422614290656`
- mean_open_interest_last_coverage: `0.9986491341353043`

## Merge Rules

- `recent_patch_v1` replaces `main_v2` at identical `(symbol, timestamp)` rows.
- Patch columns are normalized from `open/high/low/close/volume/quote_volume` to `trade_*` names.
- `premium_bps` is normalized to `premium_close_bps`.
- `kline_taker_buy_quote_share` is recomputed from taker buy quote volume divided by quote volume when available.
- Age fields are observed first-seen lower bounds and must not be interpreted as true exchange listing dates.

## Required Downstream Gates

- Block formulas that use `premium_close_bps` without symbol/date coverage checks.
- Block funding-spread assumptions that treat sparse funding events as dense hourly fields.
- Keep field-role enforcement active; legacy `forward_trade_return_1h` is a label-like column and must not enter ordinary alpha features.
- Final proof still requires official Binance Vision CHECKSUM/source trace audit.

## Coverage Sample

| symbol    |   rows |   premium_close_bps_coverage |   mark_index_basis_bps_coverage |   funding_rate_coverage |   open_interest_last_coverage |   recent_patch_rows |   main_rows_kept |
|:----------|-------:|-----------------------------:|--------------------------------:|------------------------:|------------------------------:|--------------------:|-----------------:|
| AIAUSDT   |   3877 |                     0.882383 |                        1        |                0.260769 |                      0.882383 |                 408 |             3469 |
| LITUSDT   |   4615 |                     0.88559  |                        0.766414 |                0.255038 |                      0.88559  |                 408 |             4207 |
| DOGSUSDT  |  15708 |                     0.954163 |                        1        |                0.259868 |                      1        |                 408 |            15300 |
| CVCUSDT   |   9760 |                     0.963012 |                        0.999898 |                0.316906 |                      0.963115 |                 408 |             9352 |
| SLPUSDT   |   8293 |                     0.963825 |                        1        |                0.252864 |                      0.936332 |                 408 |             7885 |
| CVXUSDT   |   8293 |                     0.963825 |                        1        |                0.252864 |                      0.936332 |                 408 |             7885 |
| IMXUSDT   |  21432 |                     0.965286 |                        1        |                0.257279 |                      0.999533 |                 408 |            21024 |
| QTUMUSDT  |  21432 |                     0.965286 |                        1        |                0.138158 |                      0.999533 |                 408 |            21024 |
| SFPUSDT   |  21432 |                     0.968645 |                        1        |                0.138158 |                      0.999533 |                 408 |            21024 |
| SPACEUSDT |   3349 |                     0.985667 |                        1        |                0.296506 |                      1        |                 408 |             2941 |
| SKRUSDT   |   3374 |                     0.985774 |                        1        |                0.326615 |                      1        |                 408 |             2966 |
| ELSAUSDT  |   3377 |                     0.985786 |                        1        |                0.31448  |                      1        |                 408 |             2969 |
| JUPUSDT   |  20694 |                     0.999565 |                        1        |                0.257418 |                      0.999517 |                 408 |            20286 |
| CTKUSDT   |  10478 |                     0.999905 |                        0.999905 |                0.256538 |                      0.933575 |                 408 |            10070 |
| ZORAUSDT  |   7717 |                     1        |                        1        |                0.270183 |                      1        |                 408 |             7309 |
| ZKUSDT    |  17389 |                     1        |                        1        |                0.261545 |                      1        |                 408 |            16981 |
| ZKPUSDT   |   4142 |                     1        |                        1        |                0.379768 |                      1        |                 408 |             3734 |
| ZKCUSDT   |   6466 |                     1        |                        1        |                0.274049 |                      1        |                 408 |             6058 |
| ZILUSDT   |  21432 |                     1        |                        1        |                0.158221 |                      0.999533 |                 408 |            21024 |
| ZETAUSDT  |  20656 |                     1        |                        1        |                0.257552 |                      0.999516 |                 408 |            20248 |