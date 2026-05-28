# CRYPTO A7AL-2R Local Forensic

Generated: 2026-05-28T13:17:54Z

## Decision

```text
PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT
```

This stage deep-audits A7AL-2Q local OI-price diagnostic candidates. It does not generate formulas, does not train, does not authorize large search, and does not authorize alpha proof or shadow/paper/live.

## Manifest

```json
{
  "authorizes_a7al2s_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 4,
  "controls": [
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "same_family_random",
    "time_shuffle",
    "symbol_shuffle"
  ],
  "cost_bps": [
    2.0,
    5.0,
    10.0
  ],
  "decision": "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT",
  "decision_counts": {
    "A7AL2R_LOCAL_FORENSIC_PASS": 4
  },
  "entry_labels": [
    "label_t1_to_t25",
    "label_t2_to_t26"
  ],
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "fields_loaded": [
    "index_close",
    "open_interest_value_last",
    "open_interest_value_mean",
    "trade_close"
  ],
  "forensic_pass_count": 4,
  "generated_at": "2026-05-28T13:17:54Z",
  "input_q_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2q_local_oi_price_formula_search\\a7al2q_manifest.json",
  "latent_coverage": {
    "loaded_rows": 3692531,
    "state_non_missing_share": 0.9703079075817397,
    "state_panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "state_seen_in_train_share": 0.7661959913546751
  },
  "runtime_seconds": 630.561,
  "strict_symbols": 181,
  "timestamps": 21025,
  "uses_may_for_generation": false,
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false,
  "warnings": []
}
```

## Decision Counts

| decision                   |   count |
|:---------------------------|--------:|
| A7AL2R_LOCAL_FORENSIC_PASS |       4 |

## Candidate Decisions

| candidate_id            | decision                   | reasons   | warnings      |   label_t1_positive_premay_splits |   label_t2_positive_premay_splits |   one_bar_lag_positive_premay_splits |   latent_positive_premay_splits |   net_10bps_positive_premay_splits |   control_ratio_premay_max |   top_symbol_abs_contribution_share |   top_month_abs_contribution_share |   top_latent_abs_contribution_share |
|:------------------------|:---------------------------|:----------|:--------------|----------------------------------:|----------------------------------:|-------------------------------------:|--------------------------------:|-----------------------------------:|---------------------------:|------------------------------------:|-----------------------------------:|------------------------------------:|
| a7al2q_1378ff7d2322adee | A7AL2R_LOCAL_FORENSIC_PASS |           |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.59779  |                           0.0445498 |                           0.289729 |                            0.20351  |
| a7al2q_f00f22bbcc48dc2c | A7AL2R_LOCAL_FORENSIC_PASS |           |               |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.737129 |                           0.0450271 |                           0.285236 |                            0.204626 |
| a7al2q_d6f7ebc0dbbdda7a | A7AL2R_LOCAL_FORENSIC_PASS |           | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.813863 |                           0.0450585 |                           0.286532 |                            0.204604 |
| a7al2q_6671d1fac5e57efe | A7AL2R_LOCAL_FORENSIC_PASS |           | control_close |                                 3 |                                 3 |                                    3 |                               3 |                                  3 |                   0.890176 |                           0.0449655 |                           0.278788 |                            0.206986 |

## Control Gate

| candidate_id            | entry_label     | split                 |   original_abs_spread |   max_control_abs_spread |   control_ratio | gate                |
|:------------------------|:----------------|:----------------------|----------------------:|-------------------------:|----------------:|:--------------------|
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | recent_oos_2026JanApr |            0.00202419 |              0.00121004  |        0.59779  | ELIGIBLE_DIAGNOSTIC |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | test_2025H2           |            0.00188264 |              0.00105587  |        0.560846 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_1378ff7d2322adee | label_t1_to_t25 | validation_2025H1     |            0.00139064 |              0.000797305 |        0.573336 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | recent_oos_2026JanApr |            0.00187861 |              0.00124869  |        0.664687 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | test_2025H2           |            0.0015938  |              0.00141876  |        0.890176 | WARN_CONTROL_CLOSE  |
| a7al2q_6671d1fac5e57efe | label_t1_to_t25 | validation_2025H1     |            0.00122872 |              0.000931355 |        0.757989 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | recent_oos_2026JanApr |            0.00185126 |              0.000909515 |        0.491294 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | test_2025H2           |            0.00191435 |              0.00155802  |        0.813863 | WARN_CONTROL_CLOSE  |
| a7al2q_d6f7ebc0dbbdda7a | label_t1_to_t25 | validation_2025H1     |            0.0012727  |              0.000763433 |        0.599854 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | recent_oos_2026JanApr |            0.00182947 |              0.000966453 |        0.528271 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | test_2025H2           |            0.0018574  |              0.00136914  |        0.737129 | ELIGIBLE_DIAGNOSTIC |
| a7al2q_f00f22bbcc48dc2c | label_t1_to_t25 | validation_2025H1     |            0.00124169 |              0.000734951 |        0.591895 | ELIGIBLE_DIAGNOSTIC |

## Top Symbol Contribution

| candidate_id            | split                 |   rank | symbol       |   abs_contribution |   abs_contribution_share |
|:------------------------|:----------------------|-------:|:-------------|-------------------:|-------------------------:|
| a7al2q_1378ff7d2322adee | validation_2025H1     |      1 | WIFUSDT      |          13.9662   |                0.0445498 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      2 | WLDUSDT      |          10.9513   |                0.0349327 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      3 | DODOXUSDT    |           9.55776  |                0.0304877 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      4 | ILVUSDT      |           9.28965  |                0.0296325 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      5 | ONDOUSDT     |           9.25693  |                0.0295281 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      6 | NEARUSDT     |           9.10307  |                0.0290373 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      7 | UNIUSDT      |           8.97717  |                0.0286357 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      8 | AVAXUSDT     |           8.80142  |                0.0280751 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |      9 | LINKUSDT     |           8.61215  |                0.0274714 |
| a7al2q_1378ff7d2322adee | validation_2025H1     |     10 | DOGEUSDT     |           8.50149  |                0.0271184 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      1 | ZECUSDT      |          11.3789   |                0.0405946 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      2 | WLDUSDT      |           8.68966  |                0.0310006 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      3 | UNIUSDT      |           8.2709   |                0.0295067 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      4 | NEARUSDT     |           8.16599  |                0.0291324 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      5 | APTUSDT      |           7.84763  |                0.0279967 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      6 | FILUSDT      |           7.73561  |                0.027597  |
| a7al2q_1378ff7d2322adee | test_2025H2           |      7 | DOTUSDT      |           7.54576  |                0.0269197 |
| a7al2q_1378ff7d2322adee | test_2025H2           |      8 | DODOXUSDT    |           7.54359  |                0.026912  |
| a7al2q_1378ff7d2322adee | test_2025H2           |      9 | LINKUSDT     |           7.47323  |                0.026661  |
| a7al2q_1378ff7d2322adee | test_2025H2           |     10 | ILVUSDT      |           7.25632  |                0.0258871 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      1 | 1000PEPEUSDT |           5.60806  |                0.0344034 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      2 | WLDUSDT      |           5.1595   |                0.0316516 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      3 | ETHWUSDT     |           4.8359   |                0.0296665 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      4 | SUIUSDT      |           4.74744  |                0.0291238 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      5 | APTUSDT      |           4.69969  |                0.0288309 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      6 | FILUSDT      |           4.68259  |                0.0287259 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      7 | NEARUSDT     |           4.54599  |                0.027888  |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      8 | DOTUSDT      |           4.52176  |                0.0277393 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |      9 | UNIUSDT      |           4.50775  |                0.0276534 |
| a7al2q_1378ff7d2322adee | recent_oos_2026JanApr |     10 | DODOXUSDT    |           4.40687  |                0.0270345 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      1 | ZECUSDT      |           1.67682  |                0.0604797 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      2 | NEARUSDT     |           1.38101  |                0.0498106 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      3 | ONDOUSDT     |           1.32977  |                0.0479624 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      4 | SUIUSDT      |           1.12613  |                0.0406176 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      5 | WLDUSDT      |           1.09694  |                0.0395645 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      6 | FILUSDT      |           1.06279  |                0.0383328 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      7 | ARBUSDT      |           0.917609 |                0.0330965 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      8 | UNIUSDT      |           0.861938 |                0.0310885 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |      9 | DODOXUSDT    |           0.835462 |                0.0301336 |
| a7al2q_1378ff7d2322adee | known_may2026_stress  |     10 | ILVUSDT      |           0.789077 |                0.0284605 |

## Boundary

```text
Allowed if PASS:
  draft A7AL-2S local follow-up contract.

Not authorized:
  alpha proof
  large search
  shadow / paper / live
```
