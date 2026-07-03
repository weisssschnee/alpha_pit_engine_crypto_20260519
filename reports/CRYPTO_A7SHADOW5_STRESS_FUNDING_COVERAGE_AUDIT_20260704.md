# CRYPTO A7SHADOW5 Stress Funding Coverage Audit

Generated: 2026-07-03T17:04:32Z

## Decision

`HOLD_A7SHADOW5_STRESS_FUNDING_COVERAGE_GAP_CONFIRMED`

This stage diagnoses why A7SHADOW-4 held on May-stress field coverage. It does not run search or promote any candidate.

## Key Findings

- base_delta_ffill8_stress_finite_share: `0.003813089295618414`
- best_delta_stress_finite_share_across_ffill_limits: `0.11030227398779811`
- base_premium_stress_finite_share: `0.9983361064891847`
- base_open_interest_stress_finite_share: `1.0`
- stress_hours: `601`
- recent_patch_stress_overlap_hours: `1`
- estimated_stress_hours_not_covered_by_recent_patch: `600`

## Split Hours

| split                 | timestamp_start           | timestamp_end             |   hour_count |
|:----------------------|:--------------------------|:--------------------------|-------------:|
| train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |
| validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |
| test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |
| recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |
| known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |

## Base Dense Funding Coverage

| source     | field                                  | split                 | timestamp_start           | timestamp_end             |   hour_count |   cell_count |   finite_cell_count |   finite_share |   nonzero_share |   symbol_with_any_finite |
|:-----------|:---------------------------------------|:----------------------|:--------------------------|:--------------------------|-------------:|-------------:|--------------------:|---------------:|----------------:|-------------------------:|
| base_panel | raw_funding_rate                       | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              126943 |     0.150538   |      0.149845   |                       96 |
| base_panel | raw_funding_rate                       | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               10530 |     0.152344   |      0.151331   |                       96 |
| base_panel | raw_funding_rate                       | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               11256 |     0.162847   |      0.161965   |                       96 |
| base_panel | raw_funding_rate                       | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               11648 |     0.168519   |      0.16781    |                       96 |
| base_panel | raw_funding_rate                       | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                   0 |     0          |      0          |                        0 |
| base_panel | funding_rate_state_last_ffill_8h       | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              841205 |     0.997558   |      0.992018   |                       96 |
| base_panel | funding_rate_state_last_ffill_8h       | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.991956   |                       96 |
| base_panel | funding_rate_state_last_ffill_8h       | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.99294    |                       96 |
| base_panel | funding_rate_state_last_ffill_8h       | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.994329   |                       96 |
| base_panel | funding_rate_state_last_ffill_8h       | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                 220 |     0.00381309 |      0.00381309 |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_8h  | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              838877 |     0.994798   |      0.542825   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_8h  | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.73397    |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_8h  | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.789193   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_8h  | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.680556   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_8h  | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                 220 |     0.00381309 |      0.00240918 |                       96 |
| base_panel | funding_rate_state_last_ffill_24h      | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              841221 |     0.997577   |      0.992037   |                       96 |
| base_panel | funding_rate_state_last_ffill_24h      | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.991956   |                       96 |
| base_panel | funding_rate_state_last_ffill_24h      | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.99294    |                       96 |
| base_panel | funding_rate_state_last_ffill_24h      | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.994329   |                       96 |
| base_panel | funding_rate_state_last_ffill_24h      | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                1756 |     0.0304354  |      0.0304354  |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_24h | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              838893 |     0.994817   |      0.542843   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_24h | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.73397    |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_24h | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.789193   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_24h | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.680556   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_24h | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                1756 |     0.0304354  |      0.0215613  |                       96 |
| base_panel | funding_rate_state_last_ffill_72h      | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              841269 |     0.997634   |      0.992094   |                       96 |
| base_panel | funding_rate_state_last_ffill_72h      | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.991956   |                       96 |
| base_panel | funding_rate_state_last_ffill_72h      | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.99294    |                       96 |
| base_panel | funding_rate_state_last_ffill_72h      | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.994329   |                       96 |
| base_panel | funding_rate_state_last_ffill_72h      | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                6364 |     0.110302   |      0.110302   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_72h | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              838941 |     0.994873   |      0.542843   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_72h | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.73397    |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_72h | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.789193   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_72h | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.680556   |                       96 |
| base_panel | funding_rate_delta_state_24h_ffill_72h | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |                6364 |     0.110302   |      0.0215613  |                       96 |
| base_panel | premium_close_bps                      | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              841927 |     0.998414   |      0.719464   |                       96 |
| base_panel | premium_close_bps                      | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.698293   |                       96 |
| base_panel | premium_close_bps                      | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.673872   |                       96 |
| base_panel | premium_close_bps                      | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      0.606264   |                       96 |
| base_panel | premium_close_bps                      | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |               57600 |     0.998336   |      0.623509   |                       96 |
| base_panel | open_interest_mean                     | train_2024            | 2024-01-01T00:00:00+00:00 | 2024-12-31T23:00:00+00:00 |         8784 |       843264 |              840976 |     0.997287   |      0.997268   |                       96 |
| base_panel | open_interest_mean                     | validation_2025H1     | 2025-06-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      1          |                       96 |
| base_panel | open_interest_mean                     | test_2025H2           | 2025-12-02T00:00:00+00:00 | 2025-12-31T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      1          |                       96 |
| base_panel | open_interest_mean                     | recent_oos_2026JanApr | 2026-04-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 |          720 |        69120 |               69120 |     1          |      1          |                       96 |
| base_panel | open_interest_mean                     | known_may2026_stress  | 2026-05-01T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |          601 |        57696 |               57696 |     1          |      1          |                       96 |

## Recent Patch Coverage

| source       | field              | observed_field     | status   | root                                                                                     |   symbols_with_field | timestamp_start           | timestamp_end             |   cell_count |   finite_cell_count |   finite_share |   overlaps_may_stress_hours | stress_overlap_start      | stress_overlap_end        |
|:-------------|:-------------------|:-------------------|:---------|:-----------------------------------------------------------------------------------------|---------------------:|:--------------------------|:--------------------------|-------------:|--------------------:|---------------:|----------------------------:|:--------------------------|:--------------------------|
| recent_patch | funding_rate       | funding_rate       | OK       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612 |                   96 | 2026-05-26T00:00:00+00:00 | 2026-06-11T23:00:00+00:00 |        39168 |               39168 |       1        |                           1 | 2026-05-26T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |
| recent_patch | funding_mark_price | funding_mark_price | OK       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612 |                   96 | 2026-05-26T00:00:00+00:00 | 2026-06-11T23:00:00+00:00 |        39168 |               39168 |       1        |                           1 | 2026-05-26T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |
| recent_patch | open_interest_mean | open_interest_mean | OK       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612 |                   96 | 2026-05-26T00:00:00+00:00 | 2026-06-11T23:00:00+00:00 |        39168 |               39154 |       0.999643 |                           1 | 2026-05-26T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |
| recent_patch | premium_close_bps  | premium_bps        | OK       | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612 |                   96 | 2026-05-26T00:00:00+00:00 | 2026-06-11T23:00:00+00:00 |        39168 |               39168 |       1        |                           1 | 2026-05-26T00:00:00+00:00 | 2026-05-26T00:00:00+00:00 |

## Required Repair

- Backfill `2026-05-01 00:00` through `2026-05-26 00:00 UTC` for funding-rate fields, plus at least 24h lookback before May 1 for `funding_rate_delta_state_24h`.
- Then build a merged evaluator base panel and rerun A7SHADOW-4.
- Base OI and premium coverage are not the May-stress blocker in this audit; still re-check OI/premium/mark-index source trace if a merged panel is rebuilt.
- Without that repair, the OI/funding candidate can be reviewed for recent OOS only, not for May-stress proof.

## Manifest

```json
{
  "authorizes_a7shadow4_rerun": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "base_delta_ffill8_stress_finite_share": 0.003813089295618414,
  "base_open_interest_stress_finite_share": 1.0,
  "base_panel_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "base_premium_stress_finite_share": 0.9983361064891847,
  "best_delta_stress_finite_share_across_ffill_limits": 0.11030227398779811,
  "blockers": [
    "base_panel_funding_delta_stress_coverage_below_95pct",
    "recent_patch_does_not_cover_full_may_stress_window"
  ],
  "decision": "HOLD_A7SHADOW5_STRESS_FUNDING_COVERAGE_GAP_CONFIRMED",
  "estimated_stress_hours_not_covered_by_recent_patch": 600,
  "generated_at": "2026-07-03T17:04:32Z",
  "hours_per_split": 720,
  "recent_patch_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_recent_patch_1h_v1_20260612",
  "recent_patch_stress_overlap_hours": 1,
  "required_repair": [
    "Backfill Binance funding-rate data for 2026-05-01 00:00 through 2026-05-26 00:00 UTC for the strict universe, plus at least 24h lookback before May 1 for funding_delta.",
    "Merge the repair into the evaluator base panel or set A7AL_BASE_PANEL_ROOT to a merged panel before rerunning A7SHADOW-4.",
    "Base OI and premium coverage are not the May-stress blocker in this audit, but any rebuilt merged panel should still re-check OI/premium/mark-index source trace.",
    "If full funding backfill is unavailable, exclude funding_delta candidates from May-stress claims and rerun A7SHADOW-4 on OI/premium candidates only."
  ],
  "stage": "A7SHADOW-5",
  "stress_hours": 601,
  "symbol_count": 96,
  "train_hours_per_split": 0
}
```
