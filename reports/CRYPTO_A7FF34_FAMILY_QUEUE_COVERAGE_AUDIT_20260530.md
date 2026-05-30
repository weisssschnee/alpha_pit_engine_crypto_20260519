# CRYPTO A7FF-34 FAMILY QUEUE COVERAGE AUDIT

Generated: 2026-05-30T11:14:01Z

## Decision

`PASS_A7FF34_FAMILY_QUEUE_COVERAGE_ACCEPTABLE_READY_FOR_A7FF35_NUMERIC_PREFLIGHT_NO_SEARCH_AUTH`

A7FF-34 audits A7FF-33 queue coverage only. It does not run numeric probe, replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ff35_numeric_prefight": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "blueprint_count": 24000,
  "company_basis_root_share": 0.14333333333333334,
  "company_family_count": 7,
  "company_motif_count": 10,
  "company_non_basis_share": 0.8566666666666667,
  "company_shard_count": 18,
  "company_top_root_family_share": 0.14333333333333334,
  "company_wave_queue_count": 3600,
  "decision": "PASS_A7FF34_FAMILY_QUEUE_COVERAGE_ACCEPTABLE_READY_FOR_A7FF35_NUMERIC_PREFLIGHT_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:14:01Z",
  "materialization_queue_count": 6000,
  "source_a7ff33_decision": "PASS_A7FF33_FAMILY_DIVERSIFIED_DRY_GENERATION_BUILT_NO_NUMERIC_NO_SEARCH_AUTH",
  "stage": "A7FF-34",
  "uses_may": false,
  "warnings": []
}
```

## Company Family Coverage

| family_id                     | root_family                           |   company_wave_count |   company_wave_share |   motif_count |   skeleton_count |   primary_field_count |   secondary_field_count |
|:------------------------------|:--------------------------------------|---------------------:|---------------------:|--------------:|-----------------:|----------------------:|------------------------:|
| D0_basis_premium_reference    | basis_premium_like|basis_premium_like |                  516 |             0.143333 |            10 |               45 |                     1 |                       2 |
| D1_open_interest_positioning  | open_interest_like|positioning_like   |                  514 |             0.142778 |            10 |               45 |                     1 |                       2 |
| D2_taker_flow_leverage        | taker_flow_like|open_interest_like    |                  514 |             0.142778 |            10 |               45 |                     1 |                       2 |
| D3_liquidity_volatility_state | liquidity_like|volatility_like        |                  514 |             0.142778 |            10 |               45 |                     1 |                       2 |
| D4_regime_relative_value      | regime_state|price_return_like        |                  514 |             0.142778 |            10 |               38 |                     1 |                       2 |
| D5_funding_dense_state        | funding_like|basis_premium_like       |                  514 |             0.142778 |            10 |               45 |                     1 |                       2 |
| D6_listing_latent_lifecycle   | listing_age_like|latent_state         |                  514 |             0.142778 |            10 |               38 |                     1 |                       2 |

## Company Shard Coverage

| company_shard   |   row_count |   family_count |   root_family_count |   motif_count |   skeleton_count |
|:----------------|------------:|---------------:|--------------------:|--------------:|-----------------:|
| shard_00        |         200 |              7 |                   7 |            10 |               31 |
| shard_01        |         200 |              7 |                   7 |            10 |               32 |
| shard_02        |         200 |              7 |                   7 |            10 |               30 |
| shard_03        |         200 |              7 |                   7 |            10 |               32 |
| shard_04        |         200 |              7 |                   7 |            10 |               29 |
| shard_05        |         200 |              7 |                   7 |            10 |               30 |
| shard_06        |         200 |              7 |                   7 |            10 |               30 |
| shard_07        |         200 |              7 |                   7 |            10 |               31 |
| shard_08        |         200 |              7 |                   7 |            10 |               29 |
| shard_09        |         200 |              7 |                   7 |            10 |               31 |
| shard_10        |         200 |              7 |                   7 |            10 |               31 |
| shard_11        |         200 |              7 |                   7 |            10 |               31 |
| shard_12        |         200 |              7 |                   7 |            10 |               31 |
| shard_13        |         200 |              7 |                   7 |            10 |               33 |
| shard_14        |         200 |              7 |                   7 |            10 |               30 |
| shard_15        |         200 |              7 |                   7 |            10 |               33 |
| shard_16        |         200 |              7 |                   7 |            10 |               32 |
| shard_17        |         200 |              7 |                   7 |            10 |               32 |

## Company Field Usage

| queue        | field                                |   formula_count |
|:-------------|:-------------------------------------|----------------:|
| company_wave | mark_index_basis_bps                 |            1394 |
| company_wave | open_interest_last                   |             953 |
| company_wave | taker_buy_sell_volume_ratio_last     |             514 |
| company_wave | trade_quote_volume                   |             514 |
| company_wave | rolling_coverage_168h                |             514 |
| company_wave | funding_rate_state_last_ffill_8h     |             514 |
| company_wave | sqrt_listing_age_days                |             514 |
| company_wave | global_long_short_account_ratio_last |             439 |
| company_wave | realized_vol_24h                     |             439 |
| company_wave | trade_return_1h                      |             351 |
| company_wave | raw_latent_state_id                  |             351 |
| company_wave | premium_close_bps                    |             255 |
| company_wave | trade_return_24h                     |             214 |
| company_wave | liquidity_rank_active_universe       |             214 |
| company_wave | global_long_short_account_ratio_mean |             126 |
| company_wave | open_interest_value_last             |             126 |
| company_wave | realized_vol_72h                     |             126 |

## Boundary

```text
numeric probe executed: false
replay executed: false
search executed: false
May used: false
next if PASS: A7FF-35 numeric preflight on diversified queue
```
