# CRYPTO A7AL-2R Local Forensic

Generated: 2026-05-28T14:27:47Z

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
  "candidate_count": 14,
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
    "A7AL2R_LOCAL_FORENSIC_PASS": 10,
    "HOLD_A7AL2R_CONTROL_DOMINATED": 1,
    "HOLD_A7AL2R_LATENT_FRAGILE": 3
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
    "mark_close",
    "open_interest_value_last",
    "open_interest_value_mean",
    "trade_close"
  ],
  "forensic_pass_count": 10,
  "generated_at": "2026-05-28T14:27:47Z",
  "input_q_manifest": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\runtime\\a7al2q_local_oi_price_formula_search\\a7al2q_manifest.json",
  "latent_coverage": {
    "loaded_rows": 3692531,
    "state_non_missing_share": 0.9703079075817397,
    "state_panel_path": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "state_seen_in_train_share": 0.7661959913546751
  },
  "runtime_seconds": 623.811,
  "strict_symbols": 181,
  "timestamps": 21025,
  "uses_may_for_generation": false,
  "uses_may_for_mutation": false,
  "uses_may_for_ranking": false,
  "uses_may_for_selection": false,
  "warnings": [
    "control_dominated_candidates_rejected"
  ]
}
```

## Decision Counts

```
                     decision  count
   A7AL2R_LOCAL_FORENSIC_PASS     10
   HOLD_A7AL2R_LATENT_FRAGILE      3
HOLD_A7AL2R_CONTROL_DOMINATED      1
```

## Candidate Decisions

```
           candidate_id                      decision                    reasons      warnings  label_t1_positive_premay_splits  label_t2_positive_premay_splits  one_bar_lag_positive_premay_splits  latent_positive_premay_splits  net_10bps_positive_premay_splits  control_ratio_premay_max  top_symbol_abs_contribution_share  top_month_abs_contribution_share  top_latent_abs_contribution_share
a7al2q_69d146749c30da3c    A7AL2R_LOCAL_FORENSIC_PASS                                                                         3                                3                                   3                              3                                 3                  0.638674                           0.044962                          0.296990                           0.202941
a7al2q_3abec814a5c6d0df    HOLD_A7AL2R_LATENT_FRAGILE timevarying_latent_fragile control_close                                3                                3                                   3                              2                                 3                  0.820173                           0.043069                          0.313930                           0.201934
a7al2q_1378ff7d2322adee    A7AL2R_LOCAL_FORENSIC_PASS                                                                         3                                3                                   3                              3                                 3                  0.597790                           0.044550                          0.289729                           0.203510
a7al2q_a4993fe3273bf0c8    A7AL2R_LOCAL_FORENSIC_PASS                            control_close                                3                                3                                   3                              3                                 3                  0.955399                           0.044541                          0.296253                           0.202920
a7al2q_0de0d41346741bd1    A7AL2R_LOCAL_FORENSIC_PASS                                                                         3                                3                                   3                              3                                 3                  0.643831                           0.044556                          0.289273                           0.203613
a7al2q_5da100b2822dc1a6    A7AL2R_LOCAL_FORENSIC_PASS                                                                         3                                3                                   3                              3                                 3                  0.782136                           0.044490                          0.286533                           0.202893
a7al2q_132c2a7c6c4a9142    A7AL2R_LOCAL_FORENSIC_PASS                            control_close                                3                                3                                   3                              3                                 3                  0.814765                           0.044703                          0.281888                           0.207234
a7al2q_f00f22bbcc48dc2c    A7AL2R_LOCAL_FORENSIC_PASS                                                                         3                                3                                   3                              3                                 3                  0.737129                           0.045027                          0.285236                           0.204626
a7al2q_d6f7ebc0dbbdda7a    A7AL2R_LOCAL_FORENSIC_PASS                            control_close                                3                                3                                   3                              3                                 3                  0.813863                           0.045059                          0.286532                           0.204604
a7al2q_6671d1fac5e57efe    A7AL2R_LOCAL_FORENSIC_PASS                            control_close                                3                                3                                   3                              3                                 3                  0.890176                           0.044965                          0.278788                           0.206986
a7al2q_33d51890b0068eb6 HOLD_A7AL2R_CONTROL_DOMINATED          control_dominated                                              3                                3                                   3                              3                                 3                  1.637536                           0.044728                          0.279237                           0.207028
a7al2q_100786d679e5b988    HOLD_A7AL2R_LATENT_FRAGILE timevarying_latent_fragile                                              3                                3                                   3                              2                                 3                  0.783719                           0.043586                          0.334784                           0.205836
a7al2q_2ec6136e6ff32eb3    A7AL2R_LOCAL_FORENSIC_PASS                            control_close                                3                                3                                   3                              3                                 3                  0.928927                           0.044637                          0.283611                           0.207139
a7al2q_ca72f5849cff347a    HOLD_A7AL2R_LATENT_FRAGILE timevarying_latent_fragile control_close                                3                                3                                   3                              2                                 3                  0.918655                           0.043155                          0.338262                           0.206045
```

## Control Gate

```
           candidate_id     entry_label                 split  original_abs_spread  max_control_abs_spread  control_ratio                   gate
a7al2q_0de0d41346741bd1 label_t1_to_t25 recent_oos_2026JanApr             0.001994                0.001284       0.643831    ELIGIBLE_DIAGNOSTIC
a7al2q_0de0d41346741bd1 label_t1_to_t25           test_2025H2             0.001868                0.001057       0.565851    ELIGIBLE_DIAGNOSTIC
a7al2q_0de0d41346741bd1 label_t1_to_t25     validation_2025H1             0.001385                0.000806       0.582240    ELIGIBLE_DIAGNOSTIC
a7al2q_100786d679e5b988 label_t1_to_t25 recent_oos_2026JanApr             0.001835                0.001308       0.712745    ELIGIBLE_DIAGNOSTIC
a7al2q_100786d679e5b988 label_t1_to_t25           test_2025H2             0.001384                0.001021       0.737690    ELIGIBLE_DIAGNOSTIC
a7al2q_100786d679e5b988 label_t1_to_t25     validation_2025H1             0.001361                0.001067       0.783719    ELIGIBLE_DIAGNOSTIC
a7al2q_132c2a7c6c4a9142 label_t1_to_t25 recent_oos_2026JanApr             0.001921                0.001316       0.684982    ELIGIBLE_DIAGNOSTIC
a7al2q_132c2a7c6c4a9142 label_t1_to_t25           test_2025H2             0.001600                0.001302       0.813487     WARN_CONTROL_CLOSE
a7al2q_132c2a7c6c4a9142 label_t1_to_t25     validation_2025H1             0.001191                0.000971       0.814765     WARN_CONTROL_CLOSE
a7al2q_1378ff7d2322adee label_t1_to_t25 recent_oos_2026JanApr             0.002024                0.001210       0.597790    ELIGIBLE_DIAGNOSTIC
a7al2q_1378ff7d2322adee label_t1_to_t25           test_2025H2             0.001883                0.001056       0.560846    ELIGIBLE_DIAGNOSTIC
a7al2q_1378ff7d2322adee label_t1_to_t25     validation_2025H1             0.001391                0.000797       0.573336    ELIGIBLE_DIAGNOSTIC
a7al2q_2ec6136e6ff32eb3 label_t1_to_t25 recent_oos_2026JanApr             0.001735                0.001198       0.690289    ELIGIBLE_DIAGNOSTIC
a7al2q_2ec6136e6ff32eb3 label_t1_to_t25           test_2025H2             0.001731                0.001608       0.928927     WARN_CONTROL_CLOSE
a7al2q_2ec6136e6ff32eb3 label_t1_to_t25     validation_2025H1             0.001200                0.000936       0.780274    ELIGIBLE_DIAGNOSTIC
a7al2q_33d51890b0068eb6 label_t1_to_t25 recent_oos_2026JanApr             0.001860                0.001286       0.691452    ELIGIBLE_DIAGNOSTIC
a7al2q_33d51890b0068eb6 label_t1_to_t25           test_2025H2             0.001591                0.002606       1.637536 HOLD_CONTROL_DOMINATED
a7al2q_33d51890b0068eb6 label_t1_to_t25     validation_2025H1             0.001188                0.000970       0.816829     WARN_CONTROL_CLOSE
a7al2q_3abec814a5c6d0df label_t1_to_t25 recent_oos_2026JanApr             0.002296                0.000996       0.433753    ELIGIBLE_DIAGNOSTIC
a7al2q_3abec814a5c6d0df label_t1_to_t25           test_2025H2             0.001647                0.001295       0.786453    ELIGIBLE_DIAGNOSTIC
a7al2q_3abec814a5c6d0df label_t1_to_t25     validation_2025H1             0.001565                0.001283       0.820173     WARN_CONTROL_CLOSE
a7al2q_5da100b2822dc1a6 label_t1_to_t25 recent_oos_2026JanApr             0.001976                0.001320       0.667808    ELIGIBLE_DIAGNOSTIC
a7al2q_5da100b2822dc1a6 label_t1_to_t25           test_2025H2             0.001757                0.000969       0.551223    ELIGIBLE_DIAGNOSTIC
a7al2q_5da100b2822dc1a6 label_t1_to_t25     validation_2025H1             0.001399                0.001094       0.782136    ELIGIBLE_DIAGNOSTIC
a7al2q_6671d1fac5e57efe label_t1_to_t25 recent_oos_2026JanApr             0.001879                0.001249       0.664687    ELIGIBLE_DIAGNOSTIC
a7al2q_6671d1fac5e57efe label_t1_to_t25           test_2025H2             0.001594                0.001419       0.890176     WARN_CONTROL_CLOSE
a7al2q_6671d1fac5e57efe label_t1_to_t25     validation_2025H1             0.001229                0.001022       0.831915     WARN_CONTROL_CLOSE
a7al2q_69d146749c30da3c label_t1_to_t25 recent_oos_2026JanApr             0.002083                0.001330       0.638674    ELIGIBLE_DIAGNOSTIC
a7al2q_69d146749c30da3c label_t1_to_t25           test_2025H2             0.001978                0.001028       0.519785    ELIGIBLE_DIAGNOSTIC
a7al2q_69d146749c30da3c label_t1_to_t25     validation_2025H1             0.001448                0.000821       0.566608    ELIGIBLE_DIAGNOSTIC
a7al2q_a4993fe3273bf0c8 label_t1_to_t25 recent_oos_2026JanApr             0.002069                0.001379       0.666420    ELIGIBLE_DIAGNOSTIC
a7al2q_a4993fe3273bf0c8 label_t1_to_t25           test_2025H2             0.001898                0.001015       0.534976    ELIGIBLE_DIAGNOSTIC
a7al2q_a4993fe3273bf0c8 label_t1_to_t25     validation_2025H1             0.001484                0.001418       0.955399     WARN_CONTROL_CLOSE
a7al2q_ca72f5849cff347a label_t1_to_t25 recent_oos_2026JanApr             0.001646                0.000978       0.593939    ELIGIBLE_DIAGNOSTIC
a7al2q_ca72f5849cff347a label_t1_to_t25           test_2025H2             0.001375                0.001263       0.918655     WARN_CONTROL_CLOSE
a7al2q_ca72f5849cff347a label_t1_to_t25     validation_2025H1             0.001338                0.000906       0.677273    ELIGIBLE_DIAGNOSTIC
a7al2q_d6f7ebc0dbbdda7a label_t1_to_t25 recent_oos_2026JanApr             0.001851                0.000910       0.491294    ELIGIBLE_DIAGNOSTIC
a7al2q_d6f7ebc0dbbdda7a label_t1_to_t25           test_2025H2             0.001914                0.001558       0.813863     WARN_CONTROL_CLOSE
a7al2q_d6f7ebc0dbbdda7a label_t1_to_t25     validation_2025H1             0.001273                0.000763       0.599854    ELIGIBLE_DIAGNOSTIC
a7al2q_f00f22bbcc48dc2c label_t1_to_t25 recent_oos_2026JanApr             0.001829                0.001306       0.713678    ELIGIBLE_DIAGNOSTIC
a7al2q_f00f22bbcc48dc2c label_t1_to_t25           test_2025H2             0.001857                0.001369       0.737129    ELIGIBLE_DIAGNOSTIC
a7al2q_f00f22bbcc48dc2c label_t1_to_t25     validation_2025H1             0.001242                0.000735       0.591895    ELIGIBLE_DIAGNOSTIC
```

## Top Symbol Contribution

```
           candidate_id                 split  rank       symbol  abs_contribution  abs_contribution_share
a7al2q_69d146749c30da3c     validation_2025H1     1      WIFUSDT         14.118084                0.044962
a7al2q_69d146749c30da3c     validation_2025H1     2      WLDUSDT         11.053524                0.035202
a7al2q_69d146749c30da3c     validation_2025H1     3    DODOXUSDT          9.599007                0.030570
a7al2q_69d146749c30da3c     validation_2025H1     4      ILVUSDT          9.367714                0.029833
a7al2q_69d146749c30da3c     validation_2025H1     5     ONDOUSDT          9.246062                0.029446
a7al2q_69d146749c30da3c     validation_2025H1     6      UNIUSDT          9.053023                0.028831
a7al2q_69d146749c30da3c     validation_2025H1     7     NEARUSDT          9.004931                0.028678
a7al2q_69d146749c30da3c     validation_2025H1     8     AVAXUSDT          8.873781                0.028260
a7al2q_69d146749c30da3c     validation_2025H1     9     LINKUSDT          8.653231                0.027558
a7al2q_69d146749c30da3c     validation_2025H1    10     DOGEUSDT          8.574799                0.027308
a7al2q_69d146749c30da3c           test_2025H2     1      ZECUSDT         11.407501                0.040629
a7al2q_69d146749c30da3c           test_2025H2     2      WLDUSDT          8.737656                0.031120
a7al2q_69d146749c30da3c           test_2025H2     3      UNIUSDT          8.252469                0.029392
a7al2q_69d146749c30da3c           test_2025H2     4     NEARUSDT          8.091622                0.028819
a7al2q_69d146749c30da3c           test_2025H2     5      APTUSDT          7.847631                0.027950
a7al2q_69d146749c30da3c           test_2025H2     6      FILUSDT          7.810258                0.027817
a7al2q_69d146749c30da3c           test_2025H2     7      DOTUSDT          7.545759                0.026875
a7al2q_69d146749c30da3c           test_2025H2     8    DODOXUSDT          7.520723                0.026786
a7al2q_69d146749c30da3c           test_2025H2     9     LINKUSDT          7.477891                0.026634
a7al2q_69d146749c30da3c           test_2025H2    10      ILVUSDT          7.237040                0.025776
a7al2q_69d146749c30da3c recent_oos_2026JanApr     1 1000PEPEUSDT          5.597778                0.034353
a7al2q_69d146749c30da3c recent_oos_2026JanApr     2      WLDUSDT          5.153142                0.031624
a7al2q_69d146749c30da3c recent_oos_2026JanApr     3     ETHWUSDT          4.824960                0.029610
a7al2q_69d146749c30da3c recent_oos_2026JanApr     4      SUIUSDT          4.747440                0.029135
a7al2q_69d146749c30da3c recent_oos_2026JanApr     5      APTUSDT          4.696472                0.028822
a7al2q_69d146749c30da3c recent_oos_2026JanApr     6      FILUSDT          4.682585                0.028737
a7al2q_69d146749c30da3c recent_oos_2026JanApr     7     NEARUSDT          4.545985                0.027898
a7al2q_69d146749c30da3c recent_oos_2026JanApr     8      DOTUSDT          4.521757                0.027750
a7al2q_69d146749c30da3c recent_oos_2026JanApr     9      UNIUSDT          4.507745                0.027664
a7al2q_69d146749c30da3c recent_oos_2026JanApr    10    DODOXUSDT          4.365587                0.026791
a7al2q_69d146749c30da3c  known_may2026_stress     1      ZECUSDT          1.676817                0.060445
a7al2q_69d146749c30da3c  known_may2026_stress     2     ONDOUSDT          1.366344                0.049253
a7al2q_69d146749c30da3c  known_may2026_stress     3     NEARUSDT          1.357990                0.048952
a7al2q_69d146749c30da3c  known_may2026_stress     4      SUIUSDT          1.126135                0.040594
a7al2q_69d146749c30da3c  known_may2026_stress     5      WLDUSDT          1.096937                0.039542
a7al2q_69d146749c30da3c  known_may2026_stress     6      FILUSDT          1.062788                0.038311
a7al2q_69d146749c30da3c  known_may2026_stress     7      ARBUSDT          0.911072                0.032842
a7al2q_69d146749c30da3c  known_may2026_stress     8      UNIUSDT          0.861938                0.031070
a7al2q_69d146749c30da3c  known_may2026_stress     9    DODOXUSDT          0.834684                0.030088
a7al2q_69d146749c30da3c  known_may2026_stress    10      ILVUSDT          0.789077                0.028444
```

## Boundary

```text
Allowed if PASS:
  draft A7AL-2S local follow-up contract.

Not authorized:
  alpha proof
  large search
  shadow / paper / live
```
