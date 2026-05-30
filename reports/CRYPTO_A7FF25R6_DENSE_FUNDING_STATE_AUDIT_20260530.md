# CRYPTO A7FF-25R6 DENSE FUNDING-STATE AUDIT

Generated: 2026-05-30T09:44:52Z

## Decision

`PASS_A7FF25R6_DENSE_FUNDING_STATE_MATERIALIZATION_READY_FOR_QUEUE_REPAIR_NO_SEARCH_AUTH`

A7FF-25R6 materializes the dense funding-state contract from A7FF-25R5 and checks whether the repaired fields clear basic activity gates. It does not generate formulas, run replay, execute search, or prove alpha.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_queue_repair_contract": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF25R6_DENSE_FUNDING_STATE_MATERIALIZATION_READY_FOR_QUEUE_REPAIR_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "ffill_limit_hours": 8,
  "field_count": 6,
  "generated_at": "2026-05-30T09:44:52Z",
  "min_finite_share": 0.2,
  "min_nonzero_share": 0.01,
  "prior_decision": "PASS_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_BUILT_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-25R5",
  "stage": "A7FF-25R6",
  "symbol_count": 96,
  "timestamp_count": 21025
}
```

## A7FF-25R5 Contract

| field_name                       | source_field                                        | feature_class           | definition                                                                             | pit_rule                                                                              | allowed_role                         | caveat                                                     |
|:---------------------------------|:----------------------------------------------------|:------------------------|:---------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:-------------------------------------|:-----------------------------------------------------------|
| funding_rate_state_last_ffill_8h | funding_rate                                        | dense_funding_state     | last observed funding_rate carried forward up to 8h; stale beyond 8h becomes NaN       | feature available at timestamp after source observation, then usable from next 1h bar | signal_candidate_or_regime           | must record age/staleness; no unlimited forward fill       |
| funding_rate_update_age_hours    | funding_rate                                        | funding_observation_age | hours since latest observed funding_rate for symbol                                    | computed only from past observations                                                  | neutralizer_or_regime                | not standalone alpha                                       |
| funding_rate_abs_state_168h_z    | funding_rate_state_last_ffill_8h                    | funding_crowding_state  | rolling 168h zscore of absolute dense funding state                                    | past rolling window only; min_period >= 48                                            | regime_or_interaction_seed           | direct alpha use requires response evidence                |
| funding_rate_delta_state_24h     | funding_rate_state_last_ffill_8h                    | funding_state_change    | 24h change in dense funding state                                                      | past 24h diff only                                                                    | signal_candidate_or_interaction_seed | must pass activity and control checks before company queue |
| funding_state_x_basis_delta      | funding_rate_delta_state_24h + mark_index_basis_bps | typed_interaction       | interaction between dense funding-state change and basis/premium dislocation transform | inherits max lag of both inputs                                                       | interaction_seed_only                | no funding-only wrapper promotion                          |

## Activity Metrics

| field_name                       |   finite_share |   nonzero_share |    mean_abs |   max_abs | activity_ok   |   train_2024_finite_share |   train_2024_nonzero_share |   validation_2025H1_finite_share |   validation_2025H1_nonzero_share |   test_2025H2_finite_share |   test_2025H2_nonzero_share |   recent_oos_2026JanApr_finite_share |   recent_oos_2026JanApr_nonzero_share |   known_may2026_stress_finite_share |   known_may2026_stress_nonzero_share |
|:---------------------------------|---------------:|----------------:|------------:|----------:|:--------------|--------------------------:|---------------------------:|---------------------------------:|----------------------------------:|---------------------------:|----------------------------:|-------------------------------------:|--------------------------------------:|------------------------------------:|-------------------------------------:|
| raw_funding_rate                 |       0.149801 |        0.149025 | 0.00015024  |    0.03   | False         |                  0.150538 |                   0.149845 |                         0.15209  |                          0.151217 |                   0.156568 |                    0.155738 |                             0.164985 |                              0.164023 |                          0          |                           0          |
| funding_rate_state_last_ffill_8h |       0.970504 |        0.964306 | 0.000146325 |    0.03   | True          |                  0.997558 |                   0.992018 |                         1        |                          0.993051 |                   1        |                    0.993367 |                             1        |                              0.992303 |                          0.00381309 |                           0.00381309 |
| funding_rate_update_age_hours    |       0.970504 |        0.820703 | 3.05039     |    8      | True          |                  0.997558 |                   0.847021 |                         1        |                          0.84791  |                   1        |                    0.843432 |                             1        |                              0.835015 |                          0.00381309 |                           0.00381309 |
| funding_rate_abs_state_168h_z    |       0.928332 |        0.883792 | 0.767745    |   12.9228 | True          |                  0.928953 |                   0.885564 |                         0.977335 |                          0.937977 |                   0.968733 |                    0.899794 |                             0.983529 |                              0.95582  |                          0.0037091  |                           0.00351844 |
| funding_rate_delta_state_24h     |       0.96935  |        0.580967 | 0.000113703 |    0.0301 | True          |                  0.994798 |                   0.542825 |                         1        |                          0.638491 |                   1        |                    0.58347  |                             1        |                              0.727431 |                          0.00381309 |                           0.00240918 |
| funding_state_x_basis_delta      |       0.968601 |        0.579922 | 0.00316707  |   29.7145 | True          |                  0.993887 |                   0.541802 |                         0.998216 |                          0.637038 |                   1        |                    0.582755 |                             1        |                              0.726208 |                          0.00381309 |                           0.00240918 |

## Repair Comparison

| field_name                       |   finite_share |   nonzero_share |    mean_abs |   max_abs | activity_ok   |   train_2024_finite_share |   train_2024_nonzero_share |   validation_2025H1_finite_share |   validation_2025H1_nonzero_share |   test_2025H2_finite_share |   test_2025H2_nonzero_share |   recent_oos_2026JanApr_finite_share |   recent_oos_2026JanApr_nonzero_share |   known_may2026_stress_finite_share |   known_may2026_stress_nonzero_share |   finite_share_gain_vs_raw |
|:---------------------------------|---------------:|----------------:|------------:|----------:|:--------------|--------------------------:|---------------------------:|---------------------------------:|----------------------------------:|---------------------------:|----------------------------:|-------------------------------------:|--------------------------------------:|------------------------------------:|-------------------------------------:|---------------------------:|
| raw_funding_rate                 |       0.149801 |        0.149025 | 0.00015024  |    0.03   | False         |                  0.150538 |                   0.149845 |                         0.15209  |                          0.151217 |                   0.156568 |                    0.155738 |                             0.164985 |                              0.164023 |                          0          |                           0          |                   0        |
| funding_rate_state_last_ffill_8h |       0.970504 |        0.964306 | 0.000146325 |    0.03   | True          |                  0.997558 |                   0.992018 |                         1        |                          0.993051 |                   1        |                    0.993367 |                             1        |                              0.992303 |                          0.00381309 |                           0.00381309 |                   0.820703 |
| funding_rate_delta_state_24h     |       0.96935  |        0.580967 | 0.000113703 |    0.0301 | True          |                  0.994798 |                   0.542825 |                         1        |                          0.638491 |                   1        |                    0.58347  |                             1        |                              0.727431 |                          0.00381309 |                           0.00240918 |                   0.81955  |
| funding_state_x_basis_delta      |       0.968601 |        0.579922 | 0.00316707  |   29.7145 | True          |                  0.993887 |                   0.541802 |                         0.998216 |                          0.637038 |                   1        |                    0.582755 |                             1        |                              0.726208 |                          0.00381309 |                           0.00240918 |                   0.818801 |

## Sample

| symbol        | timestamp                 |   raw_funding_rate |   funding_rate_state_last_ffill_8h |   funding_rate_update_age_hours |   funding_rate_delta_state_24h |   funding_state_x_basis_delta |
|:--------------|:--------------------------|-------------------:|-----------------------------------:|--------------------------------:|-------------------------------:|------------------------------:|
| 1000BONKUSDT  | 2024-01-01T00:00:00+00:00 |         0.00019961 |                         0.00019961 |                               0 |                   nan          |                 nan           |
| 1000BONKUSDT  | 2024-01-01T08:00:00+00:00 |         0.00024704 |                         0.00024704 |                               0 |                   nan          |                 nan           |
| 1000BONKUSDT  | 2024-01-01T16:00:00+00:00 |         0.00036748 |                         0.00036748 |                               0 |                   nan          |                 nan           |
| 1000BONKUSDT  | 2024-01-02T00:00:00+00:00 |         0.00028561 |                         0.00028561 |                               0 |                     8.6e-05    |                  -0.000372365 |
| 1000BONKUSDT  | 2024-01-02T08:00:00+00:00 |         0.00042175 |                         0.00042175 |                               0 |                     0.00017471 |                  -0.000610384 |
| 1000BONKUSDT  | 2024-01-02T16:00:00+00:00 |         0.00036605 |                         0.00036605 |                               0 |                    -1.43e-06   |                   2.94402e-06 |
| 1000BONKUSDT  | 2024-01-03T00:00:00+00:00 |         0.00045586 |                         0.00045586 |                               0 |                     0.00017025 |                   0.000850297 |
| 1000BONKUSDT  | 2024-01-03T08:00:00+00:00 |         9.655e-05  |                         9.655e-05  |                               0 |                    -0.0003252  |                   0.000496262 |
| 1000BONKUSDT  | 2024-01-03T16:00:00+00:00 |         5e-05      |                         5e-05      |                               0 |                    -0.00031605 |                   0.00165807  |
| 1000BONKUSDT  | 2024-01-04T00:00:00+00:00 |         5e-05      |                         5e-05      |                               0 |                    -0.00040586 |                   0.00203706  |
| 1000BONKUSDT  | 2024-01-04T08:00:00+00:00 |         5e-05      |                         5e-05      |                               0 |                    -4.655e-05  |                   5.15245e-05 |
| 1000BONKUSDT  | 2024-01-04T16:00:00+00:00 |         5e-05      |                         5e-05      |                               0 |                     0          |                   0           |
| 1000FLOKIUSDT | 2024-01-01T00:00:00+00:00 |         0.00043392 |                         0.00043392 |                               0 |                   nan          |                 nan           |
| 1000FLOKIUSDT | 2024-01-01T08:00:00+00:00 |         0.0001     |                         0.0001     |                               0 |                   nan          |                 nan           |
| 1000FLOKIUSDT | 2024-01-01T16:00:00+00:00 |         0.00053603 |                         0.00053603 |                               0 |                   nan          |                 nan           |
| 1000FLOKIUSDT | 2024-01-02T00:00:00+00:00 |         0.00070901 |                         0.00070901 |                               0 |                     0.00027509 |                   0.00436589  |
| 1000FLOKIUSDT | 2024-01-02T08:00:00+00:00 |         0.00061031 |                         0.00061031 |                               0 |                     0.00051031 |                  -0.000664141 |
| 1000FLOKIUSDT | 2024-01-02T16:00:00+00:00 |         0.0007636  |                         0.0007636  |                               0 |                     0.00022757 |                  -0.000200893 |
| 1000FLOKIUSDT | 2024-01-03T00:00:00+00:00 |         0.00032534 |                         0.00032534 |                               0 |                    -0.00038367 |                  -0.000181688 |
| 1000FLOKIUSDT | 2024-01-03T08:00:00+00:00 |         0.00055104 |                         0.00055104 |                               0 |                    -5.927e-05  |                  -9.98805e-05 |

## Boundary

```text
Dense funding-state materialization can repair no-activity tail queue inputs.
It does not authorize formula generation, large search, alpha proof, shadow, paper, or live execution.
```
