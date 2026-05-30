# CRYPTO A7FF-12 COMPANY NUMERIC WAVE AGGREGATE

Generated: 2026-05-30T04:04:57Z

## Decision

`PASS_A7FF12_COMPANY_NUMERIC_WAVE_AGGREGATE_BUILT`

A7FF-12 aggregates company-machine numeric-wave shards over the broader A7FF-12 queue. It is not generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF12_COMPANY_NUMERIC_WAVE_AGGREGATE_BUILT",
  "generated_at": "2026-05-30T04:04:57Z",
  "missing_manifests": [],
  "shard_count_complete": 8,
  "shard_count_expected": 8,
  "stage": "A7FF-12-COMPANY-NUMERIC-WAVE-AGGREGATE",
  "start_shard": 0,
  "total_input_blueprints": 720,
  "total_label_response_rows": 14400,
  "total_materialized_activity_ok": 720,
  "total_non_l7_numeric_clue_rows": 461,
  "total_portfolio_queue_count": 162,
  "total_rank_label_diagnostic_clue_rows": 146,
  "total_selected_portfolio_queue_count": 83,
  "uses_may": false
}
```

## Shards

```text
shard      stage                                                decision  input_blueprint_count                                                                                                                                                  queue_path  queue_offset  queue_limit  materialized_activity_ok_count  label_response_rows  non_l7_numeric_clue_rows  rank_label_diagnostic_clue_rows  portfolio_queue_count  selected_portfolio_queue_count  uses_may  authorizes_search
   00 A7FF-12S00 PASS_A7FF12S00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv             0           90                              90                 1800                        38                               17                     17                               9     False              False
   01 A7FF-12S01 PASS_A7FF12S01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv            90           90                              90                 1800                       160                               41                     33                              12     False              False
   02 A7FF-12S02 PASS_A7FF12S02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           180           90                              90                 1800                        40                               15                     21                              11     False              False
   03 A7FF-12S03 PASS_A7FF12S03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           270           90                              90                 1800                        59                               15                     16                              10     False              False
   04 A7FF-12S04 PASS_A7FF12S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           360           90                              90                 1800                        78                               24                     24                              10     False              False
   05 A7FF-12S05 PASS_A7FF12S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           450           90                              90                 1800                        40                               12                     18                              13     False              False
   06 A7FF-12S06 PASS_A7FF12S06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           540           90                              90                 1800                        20                               11                     17                              11     False              False
   07 A7FF-12S07 PASS_A7FF12S07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH                     90 D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv           630           90                              90                 1800                        26                               11                     16                               7     False              False
```

## Non-L7 Clue Summary

```text
                         semantic_pair                       label_family  label_horizon_h  count
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return                1     31
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                1     30
  basis_premium_like\|positioning_like              L0_raw_forward_return                1     30
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                1     28
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                1     25
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                1     23
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                1     23
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                1     21
   basis_premium_like\|volatility_like              L0_raw_forward_return                1     20
basis_premium_like\|basis_premium_like  L3_liquidity_tier_relative_return                1     17
basis_premium_like\|basis_premium_like              L0_raw_forward_return                1     15
basis_premium_like\|basis_premium_like L1_cross_sectional_relative_return                1     15
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                4     12
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                4     11
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                4     10
basis_premium_like\|basis_premium_like             L5_vol_adjusted_return                8      9
   basis_premium_like\|volatility_like             L5_vol_adjusted_return                8      9
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                4      9
  basis_premium_like\|positioning_like              L0_raw_forward_return                4      9
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                4      9
        basis_premium_like\|price_like             L5_vol_adjusted_return                1      9
        basis_premium_like\|price_like L1_cross_sectional_relative_return                1      8
  basis_premium_like\|positioning_like             L5_vol_adjusted_return                8      8
   basis_premium_like\|volatility_like              L0_raw_forward_return                4      7
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                4      7
        basis_premium_like\|price_like  L3_liquidity_tier_relative_return                1      7
        basis_premium_like\|price_like              L0_raw_forward_return                1      7
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return                4      6
        basis_premium_like\|price_like             L5_vol_adjusted_return                4      6
basis_premium_like\|basis_premium_like  L3_liquidity_tier_relative_return                4      6
basis_premium_like\|basis_premium_like L1_cross_sectional_relative_return                4      5
        basis_premium_like\|price_like L1_cross_sectional_relative_return                4      5
basis_premium_like\|basis_premium_like              L0_raw_forward_return                4      3
        basis_premium_like\|price_like              L0_raw_forward_return                4      3
        basis_premium_like\|price_like             L5_vol_adjusted_return                8      3
   basis_premium_like\|volatility_like L1_cross_sectional_relative_return                8      3
        basis_premium_like\|price_like  L3_liquidity_tier_relative_return                4      2
  basis_premium_like\|positioning_like             L5_vol_adjusted_return               24      2
  basis_premium_like\|positioning_like              L0_raw_forward_return                8      2
   basis_premium_like\|volatility_like              L0_raw_forward_return                8      2
   basis_premium_like\|volatility_like  L3_liquidity_tier_relative_return                8      2
  basis_premium_like\|positioning_like L1_cross_sectional_relative_return               24      1
  basis_premium_like\|positioning_like  L3_liquidity_tier_relative_return                8      1
```

## Boundary

```text
No May/post-selection stress is used in scoring or authorization.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
