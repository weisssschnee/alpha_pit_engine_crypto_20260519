# CRYPTO A7AL-0 Top498 Latent-Neutral Alpha Search Contract

Generated: 2026-05-27T03:48:11Z

## Decision

```text
PASS_A7AL0_TOP498_ALPHA_SEARCH_CONTRACT_READY
```

This stage does not run alpha search or replay. It freezes the split, PIT timing, latent-state, neutralization, exposure, and negative-control rules required before A7AL-1.

## Required Outputs

| file | purpose |
| --- | --- |
| a7al_split_coverage_by_symbol.csv | split composition and coverage by symbol |
| a7al_field_timing_contract.csv | PIT event/availability/execution timing by field |
| a7ak_lv_train_only_state_freeze_audit.csv | latent train-only and no-validation/test-response audit |
| a7al_neutralization_policy.json | neutralization algorithms and fallback rules |
| a7al_beta_liquidity_meme_exposure_baseline.csv | symbol beta/liquidity/meme/multiplier exposure baseline |
| a7al_negative_control_plan.json | shuffle/wrong-lag/sign/random control requirements |

## Split Summary

| split | split_label | start | end | role | expected_hours | symbols_active | strict_full_history_symbols_active | listing_aware_symbols_active | hold_symbols_active | median_rows_per_symbol | min_rows_per_symbol | median_window_coverage_ratio | median_active_span_coverage_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | train_2024 | 2024-01-01T00:00:00 | 2024-12-31T23:00:00 | fit thresholds / latent construction / response merge only | 8784 | 276 | 181 | 92 | 3 | 8784 | 37 | 1.0 | 1.0 |
| validation | validation_2025H1 | 2025-01-01T00:00:00 | 2025-06-30T23:00:00 | field-family validation | 4344 | 374 | 181 | 186 | 7 | 4344 | 108 | 1.0 | 1.0 |
| test | test_2025H2 | 2025-07-01T00:00:00 | 2025-12-31T23:00:00 | held-out historical test | 4416 | 489 | 181 | 297 | 11 | 4416 | 11 | 1.0 | 1.0 |
| recent_oos | recent_oos_2026JanApr | 2026-01-01T00:00:00 | 2026-04-30T23:00:00 | recent OOS; May 2026 unavailable in this panel | 2880 | 498 | 181 | 305 | 12 | 2880 | 2341 | 1.0 | 1.0 |

## Universe Boundary

```text
U0_strict_full_history: 181
U1_listing_aware: 305
U2_hold: 12

Universe498 is current/listing-aware. It is useful for research and cross-sectional diagnostics,
but it is not delisting-complete survivorship-safe proof by itself.
```

## PIT Timing Rule

```text
primary feature availability: timestamp + 1h / next 1h bar open
fixed delay stress: prohibited
same-bar execution: forbidden
promotion rule: field-native latency audit and wrong-lag controls must pass
```

## Latent State Boundary

```json
{
  "lv1_decision": "PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY",
  "lv2_decision": "PASS_A7AK_LV2_RESPONSE_MERGE_AUDIT_READY",
  "state_construction_window": "train_2024 only for thresholds",
  "response_merge_window": "train_2024 only",
  "validation_test_policy": "apply frozen mapping; unseen states held or fallback only",
  "raw_latent_states": 825,
  "train_seen_states": 653,
  "unseen_state_policy_rows": 172,
  "may_used": false
}
```

## Neutralization Boundary

```text
Minimum group symbols: 10
Minimum active symbols per hour: 8
Small-group fallback: parent state / liquidity tier / global
Meme and multiplier groups are exposure strata unless sample size is sufficient.
```

## A7AL-1 Authorization

```text
AUTHORIZED:
  field-family neutralized baseline smoke
  global vs age-neutral vs latent-neutral vs liquidity/meme/multiplier-aware diagnostics
  +1h primary and field-native latency audit
  negative controls before any candidate promotion

NOT AUTHORIZED:
  A7AL-2 formula search
  alpha proof
  shadow / paper / live
```

## Pass Conditions For A7AL-1

```text
At least 2 field families must survive on U0 strict symbols.
Signals must survive neutralization, BTC/ETH beta residual, field-native latency audit, and negative controls.
U1 listing-aware can support lifecycle generalization but not primary proof by itself.
Single symbol / single latent state / meme / multiplier concentration blocks promotion.
```
