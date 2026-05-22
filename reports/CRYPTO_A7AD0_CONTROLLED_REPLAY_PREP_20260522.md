# CRYPTO A7AD-0 Controlled Replay Prep

Generated: 2026-05-22T14:24:16Z

## Decision

```text
PASS_A7AD0_CONTROLLED_REPLAY_PREP_READY
```

This stage does not run replay and does not run formula search. It prepares the core48 panel for a small controlled replay smoke only.

## Input Panel

```text
panel: G:\AlphaFactory_CryptoData\gold\panels\crypto_core48_1h_with_metrics_candidate_v1.parquet
sha256: 30197f5b3ac9a3d196ad5e8b577b4881818e693762f943bea6b1517a4ac604f5
rows: 984600
columns: 233
symbols: 48
timestamp range: 2024-01-01 00:00:00+00:00 .. 2026-05-22 00:00:00+00:00
common window: 2024-03-16T12:00:00+00:00 .. 2026-04-30T23:00:00+00:00
common rows: 893376 / 893376
duplicate keys: 0
```

## Authorization

```json
{
  "authorizes_a7ad1_small_controlled_replay_smoke": true,
  "authorizes_a7o_l1_or_a7m_large_continuation": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AD0_CONTROLLED_REPLAY_PREP_READY",
  "may_policy": {
    "core48_common_panel_has_may_stress": false,
    "may_for_generation": false,
    "may_for_ranking": false,
    "may_for_threshold_tuning": false,
    "may_for_weight_selection": false,
    "may_use": "not available for core48 common proof; when available after monthly backfill, stress-only/post-selection only"
  },
  "warnings": [
    "optional_derived_or_spot_fields_sparse_use_required_columns_for_a7ad1",
    "metrics_feature_available_time_metadata_incomplete_use_panel_timestamp_plus_1h_contract",
    "aggtrades_features_not_core48_wide_excluded_from_first_core48_smoke"
  ]
}
```

## Split Manifest

| split                 | start                     | end                       |   rows |   symbols |   expected_rows | complete   | feature_time_rule                           | execution_rule                     | label_rule                                                                  |
|:----------------------|:--------------------------|:--------------------------|-------:|----------:|----------------:|:-----------|:--------------------------------------------|:-----------------------------------|:----------------------------------------------------------------------------|
| train_2024_common     | 2024-03-16T12:00:00+00:00 | 2024-12-31T23:00:00+00:00 | 334656 |        48 |          334656 | True       | feature_available_time = bar timestamp + 1h | execution_time >= next 1h bar open | label_start_time = execution_time; label_end_time depends on tested horizon |
| validation_2025H1     | 2025-01-01T00:00:00+00:00 | 2025-06-30T23:00:00+00:00 | 208512 |        48 |          208512 | True       | feature_available_time = bar timestamp + 1h | execution_time >= next 1h bar open | label_start_time = execution_time; label_end_time depends on tested horizon |
| recent_2025H2_2026Apr | 2025-07-01T00:00:00+00:00 | 2026-04-30T23:00:00+00:00 | 350208 |        48 |          350208 | True       | feature_available_time = bar timestamp + 1h | execution_time >= next 1h bar open | label_start_time = execution_time; label_end_time depends on tested horizon |

## Feature Family Availability

| feature_family              |   columns_expected |   columns_present | missing_columns   | required_columns                                                                                                                                         | required_missing_columns   |   required_common_non_null_rate_min_symbol |   required_common_non_null_rate_median_symbol |   common_non_null_rate_min_symbol |   common_non_null_rate_median_symbol |   symbols_with_family_rate_ge_95pct |   symbols_with_required_rate_ge_95pct |   symbols_total | core48_first_smoke_allowed   | usage_note                                                                 |
|:----------------------------|-------------------:|------------------:|:------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------|-------------------------------------------:|----------------------------------------------:|----------------------------------:|-------------------------------------:|------------------------------------:|--------------------------------------:|----------------:|:-----------------------------|:---------------------------------------------------------------------------|
| market_ohlcv_return         |                 15 |                15 |                   | open;high;low;close;quote_asset_volume;number_of_trades;ret_24;realized_vol_24                                                                           |                            |                                   0.998711 |                                      1        |                          0.998711 |                             1        |                                  48 |                                    48 |              48 | True                         | allowed for A7AD core48 small controlled replay prep                       |
| mark_index_basis_premium    |                  6 |                 6 |                   | mark_close;index_close;mark_index_ratio;mark_minus_index;premium_index                                                                                   |                            |                                   1        |                                      1        |                          0        |                             0        |                                   6 |                                    48 |              48 | True                         | allowed for A7AD core48 small controlled replay prep                       |
| funding_observable          |                  4 |                 4 |                   | latest_known_funding_rate;funding_rate_sign;funding_rate_persistence_3                                                                                   |                            |                                   0.999946 |                                      1        |                          0.578068 |                             0.879083 |                                  11 |                                    48 |              48 | True                         | allowed for A7AD core48 small controlled replay prep                       |
| binance_metrics_positioning |                 15 |                15 |                   | open_interest;open_interest_value;global_long_short_account_ratio;top_long_short_account_ratio;top_long_short_position_ratio;taker_buy_sell_volume_ratio |                            |                                   0.951537 |                                      0.999893 |                          0.951214 |                             0.999624 |                                  48 |                                    48 |              48 | True                         | allowed for A7AD core48 small controlled replay prep                       |
| aggtrades_core_subset_only  |                  9 |                 9 |                   | agg_features_available                                                                                                                                   |                            |                                   1        |                                      1        |                          0        |                             0        |                                   3 |                                    48 |              48 | False                        | not allowed in first core48 replay; aggtrades coverage is core subset only |

## Timing Metadata Audit

| field                          | present   |   non_null_rate |   matches_timestamp_plus_1h_rate | note                                                                              |
|:-------------------------------|:----------|----------------:|---------------------------------:|:----------------------------------------------------------------------------------|
| feature_available_time         | True      |            1    |                             1    | primary timing contract field                                                     |
| metrics_feature_available_time | True      |            0.25 |                             0.25 | supplemental metadata; incomplete on primary additions, do not use as replay gate |

Replay contract uses `feature_available_time = timestamp + 1h` and `execution_time >= next 1h bar`.
`metrics_feature_available_time` is supplemental metadata and is not used as the replay gate because it is incomplete on primary additions.

## Candidate Family Contract

| family_id   | family_name                     | allowed_fields                                                                                                                                             | purpose                                                                                            |   a7ad1_quota_hint |
|:------------|:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------|-------------------:|
| F0          | low_turnover_price_basis        | ret_12;ret_24;realized_vol_24;mark_index_ratio;premium_index                                                                                               | baseline non-funding price/basis family with low-turnover bias                                     |                 80 |
| F1          | funding_residual_controls       | latest_known_funding_rate;funding_rate_z_24;funding_rate_persistence_3                                                                                     | mandatory benchmark/control; cannot promote by itself                                              |                 48 |
| F2          | metrics_crowding_oi_interaction | open_interest;open_interest_change_24h;open_interest_zscore_168h;global_long_short_account_ratio;top_long_short_position_ratio;taker_buy_sell_volume_ratio | new independent historical metrics source interaction smoke                                        |                120 |
| F3          | cross_symbol_relative_strength  | ret_24;quote_asset_volume;open_interest_value;market_cap/liquidity tier proxies                                                                            | cross-sectional core48 relative structure, not single-symbol trend                                 |                 80 |
| F4          | volatility_liquidity_capped     | realized_vol_24;quote_asset_volume;number_of_trades;open_interest_value                                                                                    | allowed only under family cap because previous searches collapsed into liquidity-volatility motifs |                 40 |
| F5          | placebo_null_controls           | row_shuffle;time_shuffle;sign_flip;wrong_lag_stale;random_placebo                                                                                          | negative controls; must be zero promotable                                                         |                 72 |

## Negative Control Contract

| control_mode        | description                                                                 | promotion_allowed   | dominance_rule                                                                                         |
|:--------------------|:----------------------------------------------------------------------------|:--------------------|:-------------------------------------------------------------------------------------------------------|
| sign_flip           | same formula with inverted sign; should not pass as comparable candidate    | False               | candidate robust score must exceed matched controls; any control research-like pass blocks cell/family |
| row_shuffle         | symbol-row shuffled within split; detects cross-sectional artifact          | False               | candidate robust score must exceed matched controls; any control research-like pass blocks cell/family |
| time_shuffle        | time shuffled signal; detects temporal leakage or static exposure           | False               | candidate robust score must exceed matched controls; any control research-like pass blocks cell/family |
| wrong_lag_stale_24h | stale/wrong-lag control; previous A7O blocker, must be explicitly dominated | False               | candidate robust score must exceed matched controls; any control research-like pass blocks cell/family |
| random_placebo      | seeded random signal matched to universe/split                              | False               | candidate robust score must exceed matched controls; any control research-like pass blocks cell/family |

## Cost / Lag Contract

|   cost_bps |   lag_bars | required_in_a7ad1   | usage   | execution_rule                                                                        |
|-----------:|-----------:|:--------------------|:--------|:--------------------------------------------------------------------------------------|
|         10 |          0 | True                | primary | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         10 |          1 | True                | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         10 |          2 | False               | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         20 |          0 | True                | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         20 |          1 | True                | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         20 |          2 | False               | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         30 |          0 | False               | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         30 |          1 | False               | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |
|         30 |          2 | False               | stress  | signal at hour close; position no earlier than next eligible hourly bar plus lag_bars |

## Baseline / Residual Contract

| baseline_id                | formula                                                                      | role                                                                        | required   |
|:---------------------------|:-----------------------------------------------------------------------------|:----------------------------------------------------------------------------|:-----------|
| FundingCore_proxy_core48   | Rank(latest_known_funding_rate) / ZScore(latest_known_funding_rate) variants | mandatory residual baseline and benchmark, not promotable candidate         | True       |
| Core4_research_benchmark   | legacy Core4 motif family where fields exist; benchmark only                 | residual/control benchmark; not alpha proof and not shadow proof            | True       |
| market_beta_price_momentum | ret_12 / ret_24 cross-sectional rank                                         | simple price baseline                                                       | True       |
| metrics_standalone         | open_interest / long-short / taker-ratio single-source standalone baselines  | test whether interactions add information beyond independent metrics source | True       |

## Replay Boundary

- Use only rows where `core48_common_window_eligible = true`.
- May 2026 is not part of the core48 common proof panel. When monthly 2026-05 data is backfilled, May remains stress-only and cannot enter ranking, generation, threshold tuning, weight selection, or authorization.
- `aggtrades_core_subset_only` is excluded from the first core48 small replay because it is not core48-wide.
- FundingCore/Core4 remain benchmarks/residual baselines, not promotable candidates.
- A7AD-1, if run, must remain a small controlled smoke and must include matched negative controls.
