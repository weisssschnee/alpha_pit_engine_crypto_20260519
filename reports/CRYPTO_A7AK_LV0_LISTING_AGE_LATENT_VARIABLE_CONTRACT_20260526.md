# CRYPTO A7AK-LV0 Listing-Age Latent Variable Contract

Generated: 2026-05-26T15:44:33Z

## Decision

```text
PASS_A7AK_LV0_CONTRACT_READY_FOR_USER_APPROVAL
```

This stage defines the listing-age latent-variable framework and search quota policy. It does not construct states, does not run replay, and does not run search.

## Core Change

```text
Do not hard-bucket or discard short-history symbols by age.
Use age as one observable input into latent market state.
Merge states by train-only response similarity, not by age proximity.
Reserve a fixed age<30d search quota so new listings are studied instead of silently dropped.
```

## Authorization

```json
{
  "age_lt_30d_fixed_quota": "10% minimum of LV smoke generation/selection slots when available; not proof promotion quota",
  "authorizes_a7ak_min_without_lv": false,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": false,
  "authorizes_lv1_after_user_approval": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AK_LV0_CONTRACT_READY_FOR_USER_APPROVAL",
  "executes_replay": false,
  "executes_search": false,
  "executes_state_construction": false,
  "proof_boundary": {
    "hold": "quality audit only",
    "listing_aware": "generalization/lifecycle diagnostic only until frozen state map validates",
    "modeling": "U_all_quality_eligible can participate in train-only latent-state research",
    "primary_proof": "strict_full_history remains primary proof-style universe"
  },
  "requires_user_approval_before_execution": true
}
```

## Input Universe Counts

| search_eligibility            | liquidity_tier   |   symbols |
|:------------------------------|:-----------------|----------:|
| hold_quality_or_short_history | tail             |        10 |
| hold_quality_or_short_history | top20            |         1 |
| hold_quality_or_short_history | top200           |         1 |
| listing_aware                 | tail             |       209 |
| listing_aware                 | top100           |        25 |
| listing_aware                 | top20            |         5 |
| listing_aware                 | top200           |        56 |
| listing_aware                 | top50            |        10 |
| strict_full_history           | tail             |        79 |
| strict_full_history           | top100           |        25 |
| strict_full_history           | top20            |        14 |
| strict_full_history           | top200           |        43 |
| strict_full_history           | top50            |        20 |

## Input Feature Families

| source_class        |   fields |
|:--------------------|---------:|
| derived_replay_base |        3 |
| funding             |        2 |
| key                 |        2 |
| mark_index_premium  |       17 |
| metadata_timing     |        7 |
| metrics_positioning |       13 |
| trade_ohlcv         |       10 |

## Observable State Features

| feature_name                   | feature_group   | definition                                                   | purpose                                                             | timing_rule               |
|:-------------------------------|:----------------|:-------------------------------------------------------------|:--------------------------------------------------------------------|:--------------------------|
| listing_age_hours              | age             | timestamp - first_observed_trade_timestamp                   | row-local observable after listing                                  | past_only                 |
| listing_age_days               | age             | listing_age_hours / 24                                       | row-local observable after listing                                  | past_only                 |
| log1p_listing_age_days         | age_transform   | log1p(listing_age_days)                                      | nonlinear age transform                                             | past_only                 |
| sqrt_listing_age_days          | age_transform   | sqrt(listing_age_days)                                       | nonlinear age transform                                             | past_only                 |
| age_bucket_dynamic             | age_transform   | <30d, 30-90d, 90-180d, 180-365d, >=365d                      | diagnostic bucket only; not final state                             | past_only                 |
| age_percentile_active_universe | age_transform   | cross-sectional percentile among active symbols at timestamp | observable active cross-section; proof caveat from current universe | timestamp_cross_section   |
| history_length_hours           | coverage        | available rows since first observed timestamp                | past coverage proxy                                                 | past_only                 |
| rolling_coverage_168h          | coverage        | source flags complete over trailing 168h                     | data quality state                                                  | past_only                 |
| gap_hours_recent_168h          | coverage        | missing hours over trailing 168h                             | data quality state                                                  | past_only                 |
| median_quote_volume_168h       | liquidity       | rolling median trade_quote_volume                            | liquidity state                                                     | past_only                 |
| log_quote_volume_168h          | liquidity       | log1p(median_quote_volume_168h)                              | liquidity transform                                                 | past_only                 |
| liquidity_rank_active_universe | liquidity       | cross-sectional rank of rolling quote volume                 | active universe liquidity tier                                      | timestamp_cross_section   |
| trade_count_168h               | activity        | rolling mean/sum trade_count                                 | activity state                                                      | past_only                 |
| realized_vol_24h               | volatility      | std of trade_return_1h over trailing 24h                     | volatility state                                                    | past_only                 |
| realized_vol_72h               | volatility      | std of trade_return_1h over trailing 72h                     | volatility state                                                    | past_only                 |
| realized_vol_168h              | volatility      | std of trade_return_1h over trailing 168h                    | volatility state                                                    | past_only                 |
| volume_volatility_ratio_168h   | interaction     | log_quote_volume_168h / realized_vol_168h                    | liquidity-volatility state                                          | past_only                 |
| funding_rate_abs_168h          | funding         | rolling mean abs(funding_rate)                               | crowding/funding state                                              | past_only                 |
| funding_rate_mean_168h         | funding         | rolling mean funding_rate                                    | funding direction state                                             | past_only                 |
| basis_abs_168h                 | basis           | rolling mean abs(mark_index_basis_bps)                       | basis dislocation state                                             | past_only                 |
| premium_abs_168h               | basis           | rolling mean abs(premium_close_bps)                          | premium dislocation state                                           | past_only                 |
| open_interest_change_24h       | positioning     | pct/log change of open_interest_last                         | positioning state                                                   | past_only                 |
| oi_x_price_move_24h            | interaction     | open_interest_change_24h * trade_return_24h                  | crowding/positioning interaction                                    | past_only                 |
| age_x_liquidity                | interaction     | log1p_listing_age_days * liquidity_rank/state                | age-liquidity interaction                                           | past_only                 |
| age_x_volatility               | interaction     | log1p_listing_age_days * realized_vol_168h                   | age-volatility interaction                                          | past_only                 |
| age_x_funding_abs              | interaction     | log1p_listing_age_days * funding_rate_abs_168h               | age-funding interaction                                             | past_only                 |
| is_major                       | symbol_static   | BTC/ETH/BNB/SOL/XRP style major flag                         | static symbol tier                                                  | known_at_symbol_selection |
| is_core12                      | symbol_static   | legacy audited core12 flag                                   | static evidence layer                                               | known_at_symbol_selection |
| contract_format                | symbol_static   | plain vs multiplier contract                                 | contract normalization risk                                         | known_at_symbol_selection |

## State Construction Rules

| stage   | rule_name                 | rule_value                            | rationale                                                                             |
|:--------|:--------------------------|:--------------------------------------|:--------------------------------------------------------------------------------------|
| LV1     | state_construction_period | train only                            | Fit transforms/clusters only on train rows; validation/recent evaluate frozen mapping |
| LV1     | initial_state_model       | interpretable clustering              | First pass uses age/liquidity/vol/funding/basis/coverage features; avoid opaque model |
| LV1     | normalization             | train-only robust zscore or rank      | No validation/test/May distribution in scaler                                         |
| LV1     | age_role                  | input feature only                    | Age bucket is diagnostic, not final state label                                       |
| LV1     | short_history_policy      | include in modeling if quality pass   | Short-history symbols can inform lifecycle states but not primary proof               |
| LV1     | age_lt_30d_policy         | fixed quota                           | Do not discard; reserve explicit search quota and report separately                   |
| LV2     | response_merge_period     | train only                            | State response vector computed only on train                                          |
| LV2     | merge_rule                | response similarity + risk similarity | Merge raw states if response vectors and cost/lag/funding/beta profiles align         |
| LV2     | freeze_rule               | freeze raw-to-merged map              | Apply frozen map to validation/recent; do not refit on outcomes                       |
| LV3     | ranking_views             | global/age-neutral/latent-neutral     | Every candidate reports all three views                                               |
| LV3     | promotion_boundary        | strict proof universe primary         | Listing-aware states can support diagnostics/generalization, not standalone proof     |

## Response Vector For Merge

| response_component            | definition                                             | component_group        | allowed_fit_period   |
|:------------------------------|:-------------------------------------------------------|:-----------------------|:---------------------|
| future_return_mean            | mean next-bar/trade label return within train          | response               | train_only           |
| future_return_vol             | volatility of next-bar/trade label return within train | risk                   | train_only           |
| drawdown_proxy                | state-level cumulative drawdown proxy                  | risk                   | train_only           |
| cost20_survival               | state response after 20bps cost stress                 | execution              | train_only           |
| lag1_survival                 | state response after one-bar lag stress                | execution              | train_only           |
| funding_beta                  | state beta to FundingCore/funding baseline             | exposure               | train_only           |
| btc_beta                      | state beta to BTC return                               | exposure               | train_only           |
| liquidity_beta                | state beta to liquidity factor                         | exposure               | train_only           |
| volatility_beta               | state beta to volatility factor                        | exposure               | train_only           |
| momentum_probe_response       | response to simple momentum probe                      | signal_family_response | train_only           |
| reversal_probe_response       | response to simple reversal probe                      | signal_family_response | train_only           |
| liquidity_probe_response      | response to liquidity/activity probe                   | signal_family_response | train_only           |
| basis_probe_response          | response to basis/premium probe                        | signal_family_response | train_only           |
| funding_probe_response        | response to observable funding probe                   | signal_family_response | train_only           |
| oi_positioning_probe_response | response to OI/positioning probe                       | signal_family_response | train_only           |

## Search Quota Policy

| quota_bucket            | definition                     |   target_share | quota_type    | notes                                                                                                |
|:------------------------|:-------------------------------|---------------:|:--------------|:-----------------------------------------------------------------------------------------------------|
| age_lt_30d              | listing_age_days < 30          |           0.1  | fixed minimum | Minimum 10% of LV smoke generation/selection slots when available; never zeroed due to short history |
| age_30_90d              | 30 <= listing_age_days < 90    |           0.1  | soft minimum  | Lifecycle continuation bucket                                                                        |
| age_90_180d             | 90 <= listing_age_days < 180   |           0.1  | soft minimum  | Post-listing stabilization bucket                                                                    |
| age_180_365d            | 180 <= listing_age_days < 365  |           0.15 | soft minimum  | Maturing alt bucket                                                                                  |
| age_ge_365d             | listing_age_days >= 365        |           0.4  | primary mass  | Primary mature-history mass                                                                          |
| state_diversity_reserve | underrepresented latent states |           0.15 | reserve       | Allocated to latent states with sufficient quality but low representation                            |

## Forbidden Inputs

| forbidden_input              | forbidden_use                                | reason                                            |
|:-----------------------------|:---------------------------------------------|:--------------------------------------------------|
| validation_or_recent_returns | state construction / scaler / cluster fit    | Would leak evaluation outcomes                    |
| May stress labels            | state construction / merge / quota / ranking | Known adversarial stress; stress-only             |
| future delisting or survival | symbol class or latent state                 | Survivorship leakage                              |
| future liquidity percentile  | row-level feature                            | Must use timestamp-active or trailing window only |
| post-period volume median    | state construction                           | Use train-only or trailing windows                |
| control outcome superiority  | candidate promotion                          | Negative controls can block, not optimize         |

## User Approval Checklist

| approval_item                   | approved_default   | description                                                       |
|:--------------------------------|:-------------------|:------------------------------------------------------------------|
| approve_lv1_state_feature_build | False              | Build row-level observable state features with train-only scalers |
| approve_lv1_initial_clustering  | False              | Fit initial interpretable latent states on train rows only        |
| approve_lv2_response_merge      | False              | Compute train-only response vectors and frozen merge map          |
| approve_lv3_neutral_smoke       | False              | Run global vs age-neutral vs latent-neutral field-family smoke    |
| approve_age_lt30_quota          | False              | Reserve fixed age<30d quota in smoke; no direct proof promotion   |

## Execution Boundary

```text
NEXT ONLY AFTER USER APPROVAL:
  A7AK-LV1 train-only latent state feature build and initial clustering

NOT AUTHORIZED:
  replay
  search
  large search
  alpha proof
  shadow / paper / live
```
