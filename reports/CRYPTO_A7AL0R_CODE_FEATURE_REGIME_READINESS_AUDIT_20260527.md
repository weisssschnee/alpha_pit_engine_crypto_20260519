# CRYPTO A7AL-0R Code Feature Regime Readiness Audit

Generated: 2026-05-27T03:49:06Z

## Decision

```text
PASS_A7AL0R_READY_FOR_FEATURE_REGIME_REBUILD
```

This audit makes derived features first-class search inputs only when lineage, PIT lag, label isolation, and field-native latency audit are explicit. Fixed delay stress is prohibited.

## Summary

```json
{
  "generated_at": "2026-05-27T03:49:06Z",
  "decision": "PASS_A7AL0R_READY_FOR_FEATURE_REGIME_REBUILD",
  "executes_search": false,
  "executes_replay": false,
  "feature_lineage_rows": 81,
  "derived_feature_rows": 30,
  "label_fields": 1,
  "pit_rows": 80,
  "input_decisions": {
    "lv1": "PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY",
    "lv2": "PASS_A7AK_LV2_RESPONSE_MERGE_AUDIT_READY",
    "lv3": "PASS_A7AK_LV3_NEUTRAL_FIELD_FAMILY_DIAGNOSTIC_READY",
    "a7al0": "PASS_A7AL0_TOP498_ALPHA_SEARCH_CONTRACT_READY"
  },
  "blockers": [],
  "warnings": [
    "Derived fields are allowed as first-class state/search inputs when lineage, PIT lag, and field-native latency audit are explicit",
    "Forward labels remain label-only",
    "A7AL-0R does not authorize formula search"
  ]
}
```

## Script Inventory

| script_name | exists | lines | declares_search | reads_may | risk_note |
| --- | --- | --- | --- | --- | --- |
| crypto_a7al_universe498_replay_acceptance.py | True | 557 | True | True | reviewed for dataflow inventory; not edited by A7AL-0R |
| crypto_a7ak_lv1_latent_state_feature_build.py | True | 575 | True | True | reviewed for dataflow inventory; not edited by A7AL-0R |
| crypto_a7ak_lv2_response_merge_audit.py | True | 648 | True | True | reviewed for dataflow inventory; not edited by A7AL-0R |
| crypto_a7ak_lv3_neutral_field_family_smoke.py | True | 505 | True | True | reviewed for dataflow inventory; not edited by A7AL-0R |
| crypto_a7al0_top498_alpha_search_contract.py | True | 798 | True | True | reviewed for dataflow inventory; not edited by A7AL-0R |

## Label Audit

| field_name | feature_class | allowed_for_label | allowed_for_rank | allowed_for_search | allowed_for_regime | status |
| --- | --- | --- | --- | --- | --- | --- |
| forward_trade_return_1h | derived_label | True | False | False | False | PASS_LABEL_ISOLATED |

## Derived Feature Sample

| field_name | source_field_names | source_family | feature_class | formula | lookback_hours | fit_window | train_only_fit | uses_future | uses_label | pit_lag_required | latency_audit_required | fixed_delay_stress_required | allowed_for_rank | allowed_for_regime | allowed_for_search | allowed_for_label | allowed_for_neutralization | caveat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trade_return_1h | derived from accepted source fields | derived_replay_base | derived_rolling | pipeline metadata or accepted derived field | 1 | none | False | False | False | +1h primary | True | False | True | True | True | False | False | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| forward_trade_return_1h | derived from accepted source fields | derived_replay_base | derived_label | pipeline metadata or accepted derived field | 1 | none | False | True | True | +1h primary | True | False | False | False | False | True | False | label only; never enter feature/search |
| premium_close_bps | derived from accepted source fields | derived_replay_base | derived_rolling | pipeline metadata or accepted derived field | 1 | none | False | False | False | +1h primary | True | False | True | True | True | False | False | timestamp + 1h / next 1h bar open; field-native latency audit required; fixed delay stress prohibited |
| listing_age_hours | symbol,timestamp,first_observed_timestamp | metadata_listing | derived_latent_state | (timestamp - first_observed_timestamp) / 1h | 0 | train thresholds only | True | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| listing_age_days | listing_age_hours | metadata_listing | derived_latent_state | listing_age_hours / 24 | 0 | train thresholds only | True | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| log1p_listing_age_days | listing_age_days | metadata_listing | derived_latent_state | log1p(listing_age_days) | 0 | train thresholds only | True | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| sqrt_listing_age_days | listing_age_days | metadata_listing | derived_latent_state | sqrt(listing_age_days) | 0 | train thresholds only | True | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| age_percentile_active_universe | listing_age_days | metadata_listing | derived_cross_section | rank_pct(listing_age_days) within timestamp | 0 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| history_length_hours | symbol,timestamp | metadata_listing | derived_latent_state | row_number_since_first_observed + 1 | 0 | train thresholds only | True | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| rolling_coverage_168h | source_trade_klines,source_metrics,source_market_funding | metadata_timing | derived_rolling | rolling_mean(all_sources_available, 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | False | True | False | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| gap_hours_recent_168h | timestamp | metadata_timing | derived_rolling | rolling_sum(max(timestamp_diff_hours - 1, 0), 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | False | True | False | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| median_quote_volume_168h | trade_quote_volume | trade_ohlcv | derived_rolling | rolling_median(trade_quote_volume, 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| log_quote_volume_168h | median_quote_volume_168h | trade_ohlcv | derived_rolling | log1p(median_quote_volume_168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| liquidity_rank_active_universe | median_quote_volume_168h | trade_ohlcv | derived_cross_section | rank_pct(median_quote_volume_168h) within timestamp | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| trade_count_168h | trade_count | trade_ohlcv | derived_rolling | rolling_mean(trade_count, 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| realized_vol_24h | trade_return_1h | trade_ohlcv | derived_rolling | rolling_std(trade_return_1h, 24h) | 24 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| realized_vol_72h | trade_return_1h | trade_ohlcv | derived_rolling | rolling_std(trade_return_1h, 72h) | 72 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| realized_vol_168h | trade_return_1h | trade_ohlcv | derived_rolling | rolling_std(trade_return_1h, 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| volume_volatility_ratio_168h | log_quote_volume_168h,realized_vol_168h | trade_ohlcv | derived_interaction | log_quote_volume_168h / realized_vol_168h | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| funding_rate_abs_168h | funding_rate | funding | derived_rolling | rolling_mean(abs(funding_rate), 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| funding_rate_mean_168h | funding_rate | funding | derived_rolling | rolling_mean(funding_rate, 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| basis_abs_168h | mark_index_basis_bps | mark_index_premium | derived_rolling | rolling_mean(abs(mark_index_basis_bps), 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| premium_abs_168h | premium_close_bps | mark_index_premium | derived_rolling | rolling_mean(abs(premium_close_bps), 168h) | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| open_interest_change_24h | open_interest_last | metrics_positioning | derived_rolling | log(open_interest_last).diff(24h) | 24 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| trade_return_24h | trade_close | trade_ohlcv | derived_rolling | log(trade_close).diff(24h) | 24 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| oi_x_price_move_24h | open_interest_change_24h,trade_return_24h | metrics_positioning,trade_ohlcv | derived_interaction | open_interest_change_24h * trade_return_24h | 24 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | False | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| age_x_liquidity | log1p_listing_age_days,liquidity_rank_active_universe | metadata_listing,trade_ohlcv | derived_interaction | log1p_listing_age_days * liquidity_rank_active_universe | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| age_x_volatility | log1p_listing_age_days,realized_vol_168h | metadata_listing,trade_ohlcv | derived_interaction | log1p_listing_age_days * realized_vol_168h | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| age_x_funding_abs | log1p_listing_age_days,funding_rate_abs_168h | metadata_listing,funding | derived_interaction | log1p_listing_age_days * funding_rate_abs_168h | 168 | rolling past only | False | False | False | +1h primary | True | False | True | True | True | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |
| raw_latent_state_id | age/liquidity/volatility/funding/basis/coverage/major buckets | latent_state | derived_latent_state | train-threshold bucket tuple hashed to state id | 168 | train thresholds only | True | False | False | +1h primary | True | False | False | True | False | False | True | derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited |

## Boundary

```text
AUTHORIZED NEXT:
  A7AL-0F derived feature engineering contract
  A7AL-0G upper-regime state builder

NOT AUTHORIZED:
  A7AL-1 replay
  A7AL-2 formula search
  alpha proof / shadow / paper / live
```
