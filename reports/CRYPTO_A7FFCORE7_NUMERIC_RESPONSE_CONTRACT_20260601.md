# CRYPTO A7FF-CORE7 NUMERIC RESPONSE CONTRACT

Generated: 2026-05-31T18:54:49Z

## Decision

`PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E`

A7FF-CORE7 defines the numeric-response contract for the CORE6E materialized gate-native queue. It does not execute numeric response, replay, search, or promotion.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core7e": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_count": 6,
  "decision": "PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E",
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T18:54:49Z",
  "label_family_count": 5,
  "materialized_candidate_count": 2048,
  "next_allowed": "A7FF-CORE7E gate-native numeric-response execution",
  "primary_label_count": 3,
  "queue_candidate_count": 2048,
  "shard_count": 8,
  "source_decision": "PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7",
  "source_stage": "A7FF-CORE6E",
  "stage": "A7FF-CORE7",
  "uses_may": false
}
```

## Label Contract

| label_id                           | field                   | horizons     | primary   |
|:-----------------------------------|:------------------------|:-------------|:----------|
| L0_raw_forward_return              | forward_trade_return_1h | 1h;4h;8h;24h | False     |
| L1_cross_sectional_relative_return | derived_in_runner       | 1h;4h;8h;24h | True      |
| L3_liquidity_tier_relative_return  | derived_in_runner       | 1h;4h;8h;24h | True      |
| L5_vol_adjusted_return             | derived_in_runner       | 1h;4h;8h;24h | True      |
| L7_ranked_future_return            | derived_in_runner       | 1h;4h;8h;24h | False     |

## Control Contract

| control_id          | required   | hard_gate   |
|:--------------------|:-----------|:------------|
| wrong_lag_future    | True       | True        |
| wrong_lag_stale     | True       | True        |
| time_shuffle        | True       | False       |
| symbol_shuffle      | True       | False       |
| sign_flip           | True       | False       |
| same_family_placebo | True       | False       |

## Shard Plan

| shard_id   |   start_index |   end_index_exclusive |   candidate_count |   label_count |   control_count |   expected_rows | expected_output                                                 |
|:-----------|--------------:|----------------------:|------------------:|--------------:|----------------:|----------------:|:----------------------------------------------------------------|
| S00        |             0 |                   256 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S00_response.csv |
| S01        |           256 |                   512 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S01_response.csv |
| S02        |           512 |                   768 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S02_response.csv |
| S03        |           768 |                  1024 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S03_response.csv |
| S04        |          1024 |                  1280 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S04_response.csv |
| S05        |          1280 |                  1536 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S05_response.csv |
| S06        |          1536 |                  1792 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S06_response.csv |
| S07        |          1792 |                  2048 |               256 |             5 |               6 |            5120 | runtime/a7ffcore7e_numeric_response/a7ffcore7e_S07_response.csv |

## Response Gates

| gate_id                     | rule                                                                       | hard_gate   |
|:----------------------------|:---------------------------------------------------------------------------|:------------|
| G00_materialized_only       | only CORE6E status=ok candidates enter numeric response                    | True        |
| G01_primary_non_l7_presence | L1/L3/L5 primary labels must be reported separately from L7                | True        |
| G02_control_dominance       | wrong-lag/stale controls must be weaker than original signal               | True        |
| G03_split_consistency       | train/validation/recent split metrics emitted separately                   | True        |
| G04_nonoverlap_stats        | 24h non-overlap offsets or robust stats required for any future promotion  | True        |
| G05_no_may_selector         | May stress may not enter orientation, selector score, mutation, or ranking | True        |
| G06_no_replay_or_promotion  | CORE7E numeric response is not replay/search/promotion                     | True        |

## Execution Contract

```json
{
  "candidate_count": 2048,
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "sign_flip",
    "same_family_placebo"
  ],
  "forbidden_actions": [
    "replay portfolio construction",
    "search",
    "candidate promotion",
    "alpha proof",
    "shadow/paper/live",
    "May-informed orientation or scoring"
  ],
  "input_materialization": "runtime\\a7ffcore6e_materialization_preflight\\a7ffcore6e_materialization_summary_rows.csv",
  "labels": [
    {
      "field": "forward_trade_return_1h",
      "horizons": "1h;4h;8h;24h",
      "label_id": "L0_raw_forward_return",
      "primary": false
    },
    {
      "field": "derived_in_runner",
      "horizons": "1h;4h;8h;24h",
      "label_id": "L1_cross_sectional_relative_return",
      "primary": true
    },
    {
      "field": "derived_in_runner",
      "horizons": "1h;4h;8h;24h",
      "label_id": "L3_liquidity_tier_relative_return",
      "primary": true
    },
    {
      "field": "derived_in_runner",
      "horizons": "1h;4h;8h;24h",
      "label_id": "L5_vol_adjusted_return",
      "primary": true
    },
    {
      "field": "derived_in_runner",
      "horizons": "1h;4h;8h;24h",
      "label_id": "L7_ranked_future_return",
      "primary": false
    }
  ],
  "pass_conditions_for_next_contract": {
    "missing_label_metric_rate_max": 0.01,
    "primary_non_l7_clue_count_min": 1,
    "single_family_selected_share_max": 0.35,
    "wrong_lag_control_dominated_count": 0
  },
  "shard_count": 8,
  "stage": "A7FF-CORE7E"
}
```

## Boundary

```text
numeric response executed: false
replay executed: false
search executed: false
May used for orientation/scoring: false
alpha proof / shadow / paper / live: false
```
