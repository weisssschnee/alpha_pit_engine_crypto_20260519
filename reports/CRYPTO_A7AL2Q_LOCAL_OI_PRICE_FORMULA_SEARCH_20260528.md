# CRYPTO A7AL-2Q Local OI Price Formula Search

Generated: 2026-05-28T12:42:54Z

## Decision

```text
PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD
```

This is a local OI-price search around the two A7AL-2P1S clean seeds. It executes no training, no large search, no alpha proof, and no shadow/paper/live authorization.

## Scope

```text
generated_total: 4000
selected_for_fast_replay: 128
executed_fast_replay: 16
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
    "A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE": 4,
    "HOLD_A7AL2Q_CONTROL_DOMINATED": 12
  },
  "deep_audit": 16,
  "diagnostic_candidate_count": 4,
  "executed_fast_replay": 16,
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
  "generated_at": "2026-05-28T12:42:54Z",
  "generated_total": 4000,
  "input_contract": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2p2_local_oi_price_search_contract\\a7al2p2_manifest.json",
  "latency_policy": "field-native; no blanket +2h stress; label_t1 and label_t2 are audit labels",
  "latent_coverage": {
    "deferred_to": "A7AL-2R local deep forensic",
    "latent_audit_cap": 16
  },
  "orientation_fit_split": "train_2024",
  "runtime_seconds": 658.806,
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

| decision                                   |   count |
|:-------------------------------------------|--------:|
| HOLD_A7AL2Q_CONTROL_DOMINATED              |      12 |
| A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE |       4 |

## Deep Audit Scoreboard

| candidate_id            | expression                                                                              | pattern_id                    | windows   | parent_seed_id          | decision                                   | reasons                                                                                                                                               | warnings                                                                                 |   selector_score_no_may |   control_ratio_premay_max_by_split |   recent_net_mean_spread_10bps |   recent_turnover |
|:------------------------|:----------------------------------------------------------------------------------------|:------------------------------|:----------|:------------------------|:-------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------|------------------------:|------------------------------------:|-------------------------------:|------------------:|
| a7al2q_1378ff7d2322adee | Sub(Abs(ZScore(Mean(open_interest_value_last,24))),Abs(ZScore(Mean(trade_close,8))))    | abs_level_gap                 | 24\|8     |                         | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE |                                                                                                                                                       | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               13.9214   |                            0.59779  |                    0.00201923  |       0.00495898  |
| a7al2q_f00f22bbcc48dc2c | Sub(Abs(ZScore(Mean(open_interest_value_mean,48))),Abs(ZScore(Mean(index_close,96))))   | abs_level_gap                 | 48\|96    |                         | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE |                                                                                                                                                       | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               13.5892   |                            0.737129 |                    0.00182637  |       0.00309706  |
| a7al2q_d6f7ebc0dbbdda7a | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | abs_level_gap                 | 48\|12    | a7al2k_046e806368e99c76 | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE |                                                                                                                                                       | timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak |               13.5341   |                            0.813863 |                    0.001848    |       0.00326297  |
| a7al2q_6671d1fac5e57efe | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | abs_level_gap                 | 168\|336  | a7al2k_0a247ec03472983b | A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE |                                                                                                                                                       | timevarying_latent_deferred_to_a7al2r\|control_close\|overlap_adjusted_recent_tstat_weak |               13.4865   |                            0.890176 |                    0.00187671  |       0.00189879  |
| a7al2q_8e279dd3d23e1613 | Sub(Abs(ZScore(Delta(open_interest_last,336))),Abs(ZScore(Delta(trade_close,168))))     | abs_delta_gap                 | 336\|168  |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | control_dominated                                                                                                                                     | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               11.1281   |                            1.87184  |                    0.000499962 |       0.217697    |
| a7al2q_ceda68bb417b5cad | Mul(Abs(ZScore(Mean(open_interest_value_last,336))),Abs(ZScore(Delta(index_close,96)))) | oi_abs_x_price_abs_delta      | 336\|96   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | control_dominated                                                                                                                                     | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |                3.97793  |                            9.94198  |                    0.00141991  |       0.139054    |
| a7al2q_fe342a17a3bf56da | Sub(Abs(ZScore(Mean(open_interest_last,720))),Abs(ZScore(Mean(mark_close,72))))         | abs_level_gap                 | 720\|72   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |                0.354327 |                            1.38217  |                   -0.000263499 |       0.000682091 |
| a7al2q_58ec268c498480a1 | Mul(Abs(ZScore(Delta(open_interest_last,12))),Abs(ZScore(Mean(trade_close,504))))       | oi_abs_delta_x_price_abs      | 12\|504   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               -4.17713  |                            4.34288  |                   -0.00183425  |       0.500359    |
| a7al2q_f962751a6f713294 | Sub(ZScore(Delta(open_interest_last,8)),ZScore(Delta(mark_close,24)))                   | delta_spread                  | 8\|24     |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               -6.01669  |                            8.63132  |                   -0.00238537  |       0.394949    |
| a7al2q_153d45b2cb3aebdd | Mul(ZScore(Delta(open_interest_mean,4)),ZScore(Mean(mark_close,72)))                    | oi_delta_x_price_level        | 4\|72     |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile                        | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               -7.55926  |                           16.3879   |                    0.000328674 |       0.529929    |
| a7al2q_0a44f7b06019cff8 | Mul(Abs(ZScore(Delta(open_interest_value_mean,168))),Abs(ZScore(Mean(trade_close,72)))) | oi_abs_delta_x_price_abs      | 168\|72   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile                        | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |               -8.95767  |                           15.6571   |                    0.00119943  |       0.217808    |
| a7al2q_b463b7c4454b038d | Mul(Abs(ZScore(Delta(open_interest_last,48))),Abs(ZScore(Mean(trade_close,720))))       | oi_abs_delta_x_price_abs      | 48\|720   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |              -12.7822   |                           21.263    |                   -0.00051925  |       0.310738    |
| a7al2q_d7a6680d151b7968 | Mul(Abs(ZScore(Delta(open_interest_value_mean,8))),Abs(ZScore(Mean(trade_close,72))))   | oi_abs_delta_x_price_abs      | 8\|72     |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | control_dominated\|cost_proxy_fragile                                                                                                                 | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |              -15.4538   |                           28.0202   |                    0.00106643  |       0.609107    |
| a7al2q_5b4e7d3dc1984b26 | Add(ZScore(Delta(open_interest_value_last,168)),Neg(ZScore(Mean(trade_close,4))))       | oi_delta_plus_neg_price_level | 168\|4    |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |              -66.5533   |                           66.181    |                   -0.00237224  |       0.1093      |
| a7al2q_bac72457ad9e4104 | Mul(ZScore(Mean(open_interest_last,72)),ZScore(Delta(index_close,8)))                   | oi_level_x_price_delta        | 72\|8     |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile\|recent_10bps_negative | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |             -105.253    |                          109.952    |                   -0.000801025 |       0.530169    |
| a7al2q_69233c377095f5a4 | Sub(ZScore(Delta(open_interest_value_mean,96)),ZScore(Delta(trade_close,720)))          | delta_spread                  | 96\|720   |                         | HOLD_A7AL2Q_CONTROL_DOMINATED              | label_t1_not_all_premay_positive\|label_t2_not_all_premay_positive\|one_bar_lag_fragile\|control_dominated\|cost_proxy_fragile                        | timevarying_latent_deferred_to_a7al2r\|overlap_adjusted_recent_tstat_weak                |             -157.535    |                          166.602    |                    0.000567284 |       0.134114    |

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
