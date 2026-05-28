# CRYPTO A7AL-2Q Local OI Price Formula Search

Generated: 2026-05-28T14:17:23Z

## Decision

```text
PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD
```

This is a local OI-price search around the two A7AL-2P1S clean seeds. It executes no training, no large search, no alpha proof, and no shadow/paper/live authorization.

## Scope

```text
generated_total: 4000
selected_for_fast_replay: 128
executed_fast_replay: 128
deep_audit: 16
seed_count: 2
orientation_fit_split: train_2024
May usage: stress/reporting only; not used for generation, ranking, mutation, or selector score
```

## Manifest

```json
{
  "authorizes_a7al2r_local_forensic": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "controls": [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "same_family_random"
  ],
  "controls_deferred_to_deep_forensic": [
    "time_shuffle",
    "symbol_shuffle"
  ],
  "cost_bps": [
    2.0,
    5.0,
    10.0
  ],
  "decision": "PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD",
  "decision_counts": {
    "A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE": 14,
    "HOLD_A7AL2Q_CONTROL_DOMINATED": 114
  },
  "deep_audit": 16,
  "diagnostic_candidate_count": 14,
  "executed_fast_replay": 128,
  "executes_alpha_proof": false,
  "executes_local_search": true,
  "executes_training": false,
  "fields_loaded": [
    "index_close",
    "mark_close",
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_value_mean",
    "trade_close"
  ],
  "generated_at": "2026-05-28T14:17:23Z",
  "generated_total": 4000,
  "input_contract": "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\runtime\\a7al2p2_local_oi_price_search_contract\\a7al2p2_manifest.json",
  "latency_policy": "field-native; no blanket +2h stress; label_t1 and label_t2 are audit labels",
  "latent_coverage": {
    "deferred_to": "A7AL-2R local deep forensic",
    "latent_audit_cap": 16
  },
  "orientation_fit_split": "train_2024",
  "runtime_seconds": 1718.326,
  "seed_candidates": [
    "a7al2k_046e806368e99c76",
    "a7al2k_0a247ec03472983b"
  ],
  "selected_for_fast_replay": 128,
  "selected_skeleton_count": 11,
  "selected_top_skeleton_share": 0.15625,
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
             HOLD_A7AL2Q_CONTROL_DOMINATED    114
A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE     14
```

## Deep Audit Scoreboard

```
           candidate_id                                                                              expression               pattern_id  windows          parent_seed_id                                   decision           reasons                                                                                 warnings  selector_score_no_may  control_ratio_premay_max_by_split  recent_net_mean_spread_10bps  recent_turnover
a7al2q_69d146749c30da3c    Sub(Abs(ZScore(Mean(open_interest_value_mean,8))),Abs(ZScore(Mean(index_close,12))))            abs_level_gap    8\|12                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.937473                           0.638674                      0.002076         0.006876
a7al2q_3abec814a5c6d0df  Mul(Abs(ZScore(Mean(open_interest_value_mean,12))),Abs(ZScore(Delta(mark_close,336)))) oi_abs_x_price_abs_delta  12\|336                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.936418                           0.786453                      0.002223         0.073426
a7al2q_1378ff7d2322adee    Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))            abs_level_gap    24\|8                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.921445                           0.597790                      0.002019         0.004959
a7al2q_a4993fe3273bf0c8   Sub(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Mean(trade_close,72))))            abs_level_gap   12\|72                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.896406                           0.666420                      0.002063         0.005899
a7al2q_0de0d41346741bd1   Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,24))))            abs_level_gap   24\|24                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.884753                           0.604933                      0.001990         0.004812
a7al2q_5da100b2822dc1a6   Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(mark_close,504))))            abs_level_gap  24\|504                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.803724                           0.667808                      0.001972         0.004627
a7al2q_132c2a7c6c4a9142 Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(trade_close,504))))            abs_level_gap 168\|504                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.603911                           0.814765                      0.001919         0.001862
a7al2q_f00f22bbcc48dc2c   Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))            abs_level_gap   48\|96                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.589240                           0.737129                      0.001826         0.003097
a7al2q_d6f7ebc0dbbdda7a   Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))            abs_level_gap   48\|12 a7al2k_046e806368e99c76 A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.534139                           0.813863                      0.001848         0.003263
a7al2q_6671d1fac5e57efe Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336))))            abs_level_gap 168\|336 a7al2k_0a247ec03472983b A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.486534                           0.890176                      0.001877         0.001899
a7al2q_33d51890b0068eb6  Sub(Abs(ZScore(Mean(open_interest_value_mean,168))),Abs(ZScore(Mean(mark_close,336))))            abs_level_gap 168\|336                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.467292                           0.890479                      0.001858         0.001899
a7al2q_100786d679e5b988   Mul(Abs(ZScore(Mean(open_interest_value_last,4))),Abs(ZScore(Delta(index_close,72)))) oi_abs_x_price_abs_delta    4\|72                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                                  timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              13.411662                           0.783719                      0.001695         0.139239
a7al2q_2ec6136e6ff32eb3    Sub(Abs(ZScore(Mean(open_interest_value_mean,96))),Abs(ZScore(Mean(mark_close,12))))            abs_level_gap   96\|12                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.303774                           0.928927                      0.001733         0.002526
a7al2q_ca72f5849cff347a   Mul(Abs(ZScore(Mean(open_interest_value_last,12))),Abs(ZScore(Delta(mark_close,72)))) oi_abs_x_price_abs_delta   12\|72                         A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE                   timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak              13.090712                           0.918655                      0.001509         0.137026
a7al2q_7cf43aae9a3604a4  Mul(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Delta(mark_close,336)))) oi_abs_x_price_abs_delta  48\|336                                      HOLD_A7AL2Q_CONTROL_DOMINATED control_dominated                timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              12.901323                           1.604836                      0.002006         0.071841
a7al2q_4e2ad10685353df3  Mul(Abs(ZScore(Mean(open_interest_value_last,4))),Abs(ZScore(Delta(index_close,720)))) oi_abs_x_price_abs_delta   4\|720                                      HOLD_A7AL2Q_CONTROL_DOMINATED control_dominated                timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak              12.032221                           1.802648                      0.001335         0.095972
```

## Selector Diversity

```text
selected_skeleton_count: 11
selected_top_skeleton_share: 0.156250
```

## Boundary

```text
Allowed:
  local diagnostic candidate follow-up if decision is PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD

Not authorized:
  large search
  alpha proof
  shadow / paper / live
```
