# Crypto A7S-4 Crowding Robustness Audit

- generated_at: `2026-05-22T09:11:11Z`
- decision: `HOLD_A7S4_CROWDING_MOTIF_NOT_ROBUST`
- executes_search: `False`
- executes_replay: `robustness_from_a7s3_artifacts`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7S-4 tests whether the A7S-3 global-long-short crowding motif survives basic robustness gates. It uses A7S-3 artifacts and does not generate new formulas.

## Robustness Summary

|   horizon |   validation_net10 |   validation_net20 |   recent_net10 |   recent_net20 |   may_net10 |   lag1_recent_net10 |   lag2_recent_net10 |   lag3_recent_net10 |   recent_symbol_loo_positive_rate |   may_symbol_loo_positive_rate |   recent_month_loo_positive_rate |   recent_min_symbol_loo_net10 |   recent_min_month_loo_net10 |   recent_control_positive_count |   may_control_positive_count | passes_validation_recent_10bps   | passes_validation_recent_20bps   | passes_lag_ladder_recent   | passes_symbol_loo   | passes_month_loo   | passes_controls_recent   | passes_may_stress   |
|----------:|-------------------:|-------------------:|---------------:|---------------:|------------:|--------------------:|--------------------:|--------------------:|----------------------------------:|-------------------------------:|---------------------------------:|------------------------------:|-----------------------------:|--------------------------------:|-----------------------------:|:---------------------------------|:---------------------------------|:---------------------------|:--------------------|:-------------------|:-------------------------|:--------------------|
|        24 |           0.503662 |          -0.152838 |       0.948899 |       0.122899 |    0.588787 |             1.056   |             1.12174 |             1.23089 |                          0.833333 |                       0.916667 |                              0.9 |                      -1.87753 |                    -1.1271   |                               0 |                            1 | True                             | False                            | True                       | False               | False              | True                     | True                |
|        48 |           1.11734  |           0.460841 |       1.38927  |       0.563268 |    0.730215 |             1.37804 |             1.31922 |             1.26529 |                          0.666667 |                       0.916667 |                              0.9 |                      -2.97437 |                    -0.762102 |                               0 |                            1 | True                             | True                             | True                       | False               | False              | True                     | True                |

## Recent Symbol Leave-One-Out

|   horizon | split                     | left_out_symbol   |   full_net10 |   symbol_net10 |   loo_net10 | loo_positive   |
|----------:|:--------------------------|:------------------|-------------:|---------------:|------------:|:---------------|
|        24 | recent_oos_2025H2_2026Apr | SOLUSDT           |     0.948899 |      2.82643   |   -1.87753  | False          |
|        24 | recent_oos_2025H2_2026Apr | BCHUSDT           |     0.948899 |      1.47031   |   -0.521408 | False          |
|        24 | recent_oos_2025H2_2026Apr | LTCUSDT           |     0.948899 |      0.706689  |    0.242211 | True           |
|        24 | recent_oos_2025H2_2026Apr | BTCUSDT           |     0.948899 |      0.393831  |    0.555069 | True           |
|        24 | recent_oos_2025H2_2026Apr | ADAUSDT           |     0.948899 |      0.377104  |    0.571796 | True           |
|        24 | recent_oos_2025H2_2026Apr | ETHUSDT           |     0.948899 |      0.238463  |    0.710437 | True           |
|        24 | recent_oos_2025H2_2026Apr | LINKUSDT          |     0.948899 |      0.152533  |    0.796366 | True           |
|        24 | recent_oos_2025H2_2026Apr | BNBUSDT           |     0.948899 |     -0.170153  |    1.11905  | True           |
|        24 | recent_oos_2025H2_2026Apr | DOGEUSDT          |     0.948899 |     -0.661162  |    1.61006  | True           |
|        24 | recent_oos_2025H2_2026Apr | SUIUSDT           |     0.948899 |     -0.830982  |    1.77988  | True           |
|        24 | recent_oos_2025H2_2026Apr | XRPUSDT           |     0.948899 |     -0.855608  |    1.80451  | True           |
|        24 | recent_oos_2025H2_2026Apr | AVAXUSDT          |     0.948899 |     -2.69856   |    3.64746  | True           |
|        48 | recent_oos_2025H2_2026Apr | SOLUSDT           |     1.38927  |      4.36364   |   -2.97437  | False          |
|        48 | recent_oos_2025H2_2026Apr | ETHUSDT           |     1.38927  |      1.9426    |   -0.553333 | False          |
|        48 | recent_oos_2025H2_2026Apr | BCHUSDT           |     1.38927  |      1.86659   |   -0.477322 | False          |
|        48 | recent_oos_2025H2_2026Apr | LTCUSDT           |     1.38927  |      1.59439   |   -0.205126 | False          |
|        48 | recent_oos_2025H2_2026Apr | BTCUSDT           |     1.38927  |      0.960002  |    0.429266 | True           |
|        48 | recent_oos_2025H2_2026Apr | BNBUSDT           |     1.38927  |      0.196061  |    1.19321  | True           |
|        48 | recent_oos_2025H2_2026Apr | SUIUSDT           |     1.38927  |      0.0653073 |    1.32396  | True           |
|        48 | recent_oos_2025H2_2026Apr | ADAUSDT           |     1.38927  |     -0.175766  |    1.56503  | True           |
|        48 | recent_oos_2025H2_2026Apr | LINKUSDT          |     1.38927  |     -0.767686  |    2.15695  | True           |
|        48 | recent_oos_2025H2_2026Apr | DOGEUSDT          |     1.38927  |     -2.33669   |    3.72596  | True           |
|        48 | recent_oos_2025H2_2026Apr | XRPUSDT           |     1.38927  |     -2.84595   |    4.23522  | True           |
|        48 | recent_oos_2025H2_2026Apr | AVAXUSDT          |     1.38927  |     -3.47323   |    4.8625   | True           |

## Recent Month Leave-One-Out

|   horizon | split                     | left_out_month   |   full_net10 |   month_net10 |   loo_net10 | loo_positive   |
|----------:|:--------------------------|:-----------------|-------------:|--------------:|------------:|:---------------|
|        24 | recent_oos_2025H2_2026Apr | 2025-10          |     0.948899 |    2.076      |   -1.1271   | False          |
|        24 | recent_oos_2025H2_2026Apr | 2026-03          |     0.948899 |    0.708276   |    0.240623 | True           |
|        24 | recent_oos_2025H2_2026Apr | 2026-04          |     0.948899 |    0.528443   |    0.420456 | True           |
|        24 | recent_oos_2025H2_2026Apr | 2025-11          |     0.948899 |    0.448929   |    0.499971 | True           |
|        24 | recent_oos_2025H2_2026Apr | 2026-02          |     0.948899 |   -0.0875485  |    1.03645  | True           |
|        24 | recent_oos_2025H2_2026Apr | 2026-01          |     0.948899 |   -0.19172    |    1.14062  | True           |
|        24 | recent_oos_2025H2_2026Apr | 2025-08          |     0.948899 |   -0.28493    |    1.23383  | True           |
|        24 | recent_oos_2025H2_2026Apr | 2025-12          |     0.948899 |   -0.295474   |    1.24437  | True           |
|        24 | recent_oos_2025H2_2026Apr | 2025-09          |     0.948899 |   -0.496822   |    1.44572  | True           |
|        24 | recent_oos_2025H2_2026Apr | 2025-07          |     0.948899 |   -1.45626    |    2.40516  | True           |
|        48 | recent_oos_2025H2_2026Apr | 2025-10          |     1.38927  |    2.15137    |   -0.762102 | False          |
|        48 | recent_oos_2025H2_2026Apr | 2025-12          |     1.38927  |    1.11582    |    0.273447 | True           |
|        48 | recent_oos_2025H2_2026Apr | 2026-04          |     1.38927  |    0.529876   |    0.859393 | True           |
|        48 | recent_oos_2025H2_2026Apr | 2025-11          |     1.38927  |    0.488524   |    0.900744 | True           |
|        48 | recent_oos_2025H2_2026Apr | 2026-03          |     1.38927  |    0.426454   |    0.962814 | True           |
|        48 | recent_oos_2025H2_2026Apr | 2026-01          |     1.38927  |    0.191476   |    1.19779  | True           |
|        48 | recent_oos_2025H2_2026Apr | 2025-09          |     1.38927  |   -0.00545135 |    1.39472  | True           |
|        48 | recent_oos_2025H2_2026Apr | 2026-02          |     1.38927  |   -0.673593   |    2.06286  | True           |
|        48 | recent_oos_2025H2_2026Apr | 2025-08          |     1.38927  |   -0.797054   |    2.18632  | True           |
|        48 | recent_oos_2025H2_2026Apr | 2025-07          |     1.38927  |   -2.03815    |    3.42742  | True           |

## Authorization

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_crowding_motif_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_shadow_paper_live": false,
  "authorizes_state_feature_use": true,
  "blockers": [
    "validation_recent_20bps_fail",
    "symbol_loo_fail",
    "month_loo_fail"
  ],
  "decision": "HOLD_A7S4_CROWDING_MOTIF_NOT_ROBUST",
  "executes_replay": "robustness_from_a7s3_artifacts",
  "executes_search": false,
  "generated_at": "2026-05-22T09:11:11Z",
  "required_next": [
    "Do not promote standalone global-long-short crowding motif",
    "Use metrics as state/exposure/interactions in later reset only",
    "No expanded replay from A7S-4"
  ],
  "warnings": [
    "single_formula_single_family",
    "may_control_positive_stress_only"
  ]
}
```

## Required Next

- Do not expand this crowding motif as an alpha candidate.
- Keep global_long_short_account_ratio_zscore_168h as a candidate state/exposure feature.
- If continuing metrics work, redesign around interaction/state use, not standalone crowding promotion.
