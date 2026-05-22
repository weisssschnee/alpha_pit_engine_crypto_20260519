# Crypto A7V-1/A7V-2 Feature Registry and No-Search Smoke

- generated_at: `2026-05-22T01:24:15Z`
- primary_panel: `G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet`
- decision: `PASS_A7V1_FEATURE_REGISTRY_AND_A7V2_NO_SEARCH_SMOKE`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Purpose

A7V accepted the unified panel. This step turns the accepted aggTrades fields into an explicit opt-in generator registry and verifies a small set of self-reproduced derived features on the real panel without running search.

## Registry Summary

- enabled agg base features: `94`
- derived feature specs: `5211`
- config: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\config\crypto_a7v_feature_registry_v1.json`
- integration mode: `opt_in_explicit_load`; old A7M/A7O replay artifacts are not changed by this registry.

## Base Field Families

| field_family         |   enabled_field_count |
|:---------------------|----------------------:|
| activity_liquidity   |                    19 |
| cross_symbol         |                    10 |
| flow                 |                    16 |
| large_trade          |                     6 |
| other                |                     5 |
| price_microstructure |                    12 |
| rolling              |                    26 |

## No-Search Smoke Metrics

| feature_id                                         |   rows |   non_null_rows |   finite_rate_when_non_null |   non_core3_output_rows |   without_agg_mask_output_rows |   may2026_output_rows |   available_non_null_rate |          min |          max | decision   |
|:---------------------------------------------------|-------:|----------------:|----------------------------:|------------------------:|-------------------------------:|----------------------:|--------------------------:|-------------:|-------------:|:-----------|
| TSMean_4h__agg_flow_imbalance_notional             | 250896 |           61263 |                           1 |                       0 |                              0 |                     0 |                  0.999853 | -0.239632    |  0.287482    | PASS       |
| Delta_4h__agg_notional                             | 250896 |           61260 |                           1 |                       0 |                              0 |                     0 |                  0.999804 | -1.33392e+10 |  1.36543e+10 | PASS       |
| TSStd_24h__agg_large_notional_share_100k_plus      | 250896 |           61203 |                           1 |                       0 |                              0 |                     0 |                  0.998874 |  0.0106443   |  0.202081    | PASS       |
| ZScore_by_symbol__agg_price_range_bps              | 250896 |           61272 |                           1 |                       0 |                              0 |                     0 |                  1        | -1.1908      | 34.1077      | PASS       |
| Mul__agg_signed_flow_z_24h__mark_index_ratio       | 250896 |           61239 |                           1 |                       0 |                              0 |                     0 |                  0.999461 | -0.00685623  |  0.0377903   | PASS       |
| CrossSymbolRank_core3__agg_flow_imbalance_notional | 250896 |           61272 |                           1 |                       0 |                              0 |                     0 |                  1        |  0.333333    |  1           | PASS       |
| RelativeToBTC_core3__agg_flow_imbalance_notional   | 250896 |           61272 |                           1 |                       0 |                              0 |                     0 |                  1        | -0.588733    |  0.692855    | PASS       |

## Negative Controls

| control_id                         | control_type                   |   non_core3_output_rows | would_pass_without_contract   | decision                 | notes                                                                                                   |   feature_available_lag_bars | base_fields                                           |
|:-----------------------------------|:-------------------------------|------------------------:|:------------------------------|:-------------------------|:--------------------------------------------------------------------------------------------------------|-----------------------------:|:------------------------------------------------------|
| zero_fill_core12_cross_symbol_rank | forbidden_zero_fill            |                  188172 | True                          | BLOCKED_EXPECTED_CONTROL | Shows why missing agg rows cannot be zero-filled before cross-sectional rank.                           |                          nan | nan                                                   |
| same_hour_execution_lag0           | forbidden_timing               |                     nan | True                          | BLOCKED_EXPECTED_CONTROL | Agg 1h bucket may only be used after hour close; same-hour close execution is forbidden.                |                            0 | nan                                                   |
| funding_unrestricted_interaction   | forbidden_unrestricted_funding |                     nan | True                          | BLOCKED_EXPECTED_CONTROL | Funding may be a baseline/control or residual target; unrestricted discovery packaging remains blocked. |                          nan | agg_flow_imbalance_notional;latest_known_funding_rate |

## Authorization

```json
{
  "authorizes_agg_aware_generator_dry_run": true,
  "authorizes_alpha_proof": false,
  "authorizes_core12_cross_section_rank_with_missing_agg": false,
  "authorizes_full_search": false,
  "authorizes_same_hour_execution": false,
  "authorizes_shadow_paper_live": false,
  "authorizes_zero_fill_for_missing_agg": false,
  "blockers": [],
  "decision": "PASS_A7V1_FEATURE_REGISTRY_AND_A7V2_NO_SEARCH_SMOKE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T01:24:15Z",
  "required_next": [
    "A7V-3 agg-aware candidate dry run using config/crypto_a7v_feature_registry_v1.json",
    "A7V-4 no-mask/wrong-lag/time-shuffle controls before replay",
    "A7U-0R consolidated raw checksum trace before final alpha panel claims"
  ]
}
```

## Required Next

- A7V-3: implement an agg-aware candidate dry-run using this registry, still no alpha proof.
- A7V-4: include row/time/wrong-lag/no-mask controls before any agg-aware search.
- Do not run full A7O/A7M search from this registry until A7V-2 smoke stays clean and raw checksum trace is consolidated.
