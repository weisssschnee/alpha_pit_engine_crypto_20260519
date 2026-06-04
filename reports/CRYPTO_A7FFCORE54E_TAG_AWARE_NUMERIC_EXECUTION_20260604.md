# CRYPTO A7FF-CORE54E TAG-AWARE NUMERIC EXECUTION

Generated: 2026-06-04T05:50:40Z

## Decision

`PASS_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION_READY_FOR_CORE55`

CORE54E runs the existing numeric probe over the full A7INPUT-2 main queue: ordinary-alpha plus interaction-alpha, excluding rescue lane from the main path. It is numeric execution, not replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core55_numeric_forensic": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION_READY_FOR_CORE55",
  "eval_failure_count": 0,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "external_runtime_dir": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604",
  "failed_shard_count": 0,
  "generated_at": "2026-06-04T05:50:40Z",
  "input_queue_rows": 2451,
  "interaction_rows": 576,
  "label_response_rows": 41420,
  "materialized_activity_ok_count": 2071,
  "non_l7_numeric_clue_rows": 348,
  "ordinary_rows": 1875,
  "portfolio_queue_count": 0,
  "process_exit_code": 0,
  "rank_label_diagnostic_clue_rows": 998,
  "selected_portfolio_queue_count": 149,
  "shard_count": 10,
  "source_decisions": [
    "PASS_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_READY_FOR_CORE54",
    "PASS_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT_READY_FOR_CORE54E"
  ],
  "source_stages": [
    "A7INPUT-2",
    "A7INPUT-3"
  ],
  "stage": "A7FF-CORE54E",
  "started_at": "2026-06-04T05:50:39Z",
  "timed_out": false,
  "timed_out_shard_count": 0,
  "timeout_seconds": 28800,
  "uses_may": false
}
```

## Materialization By Queue

| a7input_queue     |   rows |   eval_success |   activity_ok |   median_finite_share |   median_nonzero_share |
|:------------------|-------:|---------------:|--------------:|----------------------:|-----------------------:|
| interaction_alpha |    576 |            576 |           476 |              0.993105 |               0.99131  |
| ordinary_alpha    |   1875 |           1875 |          1595 |              0.827348 |               0.993277 |

## Shard Summary

| shard   | started_at   | finished_at          |   returncode | timed_out   | runtime_dir                                                                                           |   queue_rows |   ordinary_rows |   interaction_rows | decision                                                     | blockers                |   materialized_activity_ok_count |   label_response_rows |   non_l7_numeric_clue_rows |   rank_label_diagnostic_clue_rows |   selected_portfolio_queue_count | reused_existing   |
|:--------|:-------------|:---------------------|-------------:|:------------|:------------------------------------------------------------------------------------------------------|-------------:|----------------:|-------------------:|:-------------------------------------------------------------|:------------------------|---------------------------------:|----------------------:|---------------------------:|----------------------------------:|---------------------------------:|:------------------|
| s00     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_00 |          256 |             256 |                  0 | PASS_A7FFCORE54ES00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              222 |                  4440 |                         93 |                               117 |                               20 | True              |
| s01     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_01 |          256 |             256 |                  0 | PASS_A7FFCORE54ES01_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              202 |                  4040 |                         46 |                                97 |                               18 | True              |
| s02     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_02 |          256 |             256 |                  0 | PASS_A7FFCORE54ES02_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              200 |                  4000 |                         70 |                               132 |                               19 | True              |
| s03     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_03 |          256 |             256 |                  0 | PASS_A7FFCORE54ES03_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              224 |                  4480 |                         54 |                               207 |                               20 | True              |
| s04     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_04 |          256 |             256 |                  0 | PASS_A7FFCORE54ES04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              221 |                  4420 |                          4 |                               114 |                               11 | True              |
| s05     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_05 |          256 |             256 |                  0 | PASS_A7FFCORE54ES05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              216 |                  4320 |                          1 |                                31 |                                7 | True              |
| s06     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_06 |          256 |             256 |                  0 | PASS_A7FFCORE54ES06_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              228 |                  4560 |                         14 |                                73 |                                9 | True              |
| s07     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_07 |          256 |              83 |                173 | PASS_A7FFCORE54ES07_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              223 |                  4460 |                         49 |                               131 |                               24 | True              |
| s08     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_08 |          256 |               0 |                256 | PASS_A7FFCORE54ES08_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH |                         |                              206 |                  4120 |                         17 |                                84 |                               16 | True              |
| s09     |              | 2026-06-04T05:50:39Z |            0 | False       | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604/shard_09 |          147 |               0 |                147 | HOLD_A7FFCORE54ES09_NO_NON_L7_NUMERIC_CLUES                  | no_non_l7_numeric_clues |                              129 |                  2580 |                          0 |                                12 |                                5 | True              |

## Decision By Queue

| a7input_queue     | decision                                  | label_family                       |   row_count |
|:------------------|:------------------------------------------|:-----------------------------------|------------:|
| ordinary_alpha    | HOLD_A7FFCORE54ES04_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         787 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         747 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         747 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         719 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         719 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         668 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         663 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         657 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         643 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         643 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         642 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         639 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         630 |
| interaction_alpha | HOLD_A7FFCORE54ES08_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         621 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         614 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         610 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         594 |
| interaction_alpha | HOLD_A7FFCORE54ES08_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         593 |
| interaction_alpha | HOLD_A7FFCORE54ES08_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         593 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         591 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         591 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         585 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         585 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         577 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         573 |
| interaction_alpha | HOLD_A7FFCORE54ES08_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         568 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         564 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         564 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_CONTROL_DOMINATED     | L7_ranked_future_return            |         552 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         551 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         533 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_CONTROL_DOMINATED     | L7_ranked_future_return            |         529 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         525 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         525 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_CONTROL_DOMINATED     | L7_ranked_future_return            |         426 |
| interaction_alpha | HOLD_A7FFCORE54ES09_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         422 |
| interaction_alpha | HOLD_A7FFCORE54ES09_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         416 |
| interaction_alpha | HOLD_A7FFCORE54ES09_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         416 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         412 |
| interaction_alpha | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         412 |
| interaction_alpha | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         412 |
| interaction_alpha | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         406 |
| interaction_alpha | HOLD_A7FFCORE54ES08_CONTROL_DOMINATED     | L7_ranked_future_return            |         403 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_CONTROL_DOMINATED     | L7_ranked_future_return            |         399 |
| interaction_alpha | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         393 |
| interaction_alpha | HOLD_A7FFCORE54ES09_PRE_MAY_UNSTABLE      | L3_liquidity_tier_relative_return  |         389 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         381 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_CONTROL_DOMINATED     | L0_raw_forward_return              |         358 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         357 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         348 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         336 |
| ordinary_alpha    | HOLD_A7FFCORE54ES01_CONTROL_DOMINATED     | L7_ranked_future_return            |         333 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         328 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_CONTROL_DOMINATED     | L7_ranked_future_return            |         324 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_CONTROL_DOMINATED     | L7_ranked_future_return            |         318 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_CONTROL_DOMINATED     | L0_raw_forward_return              |         315 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         313 |
| ordinary_alpha    | HOLD_A7FFCORE54ES02_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         308 |
| interaction_alpha | HOLD_A7FFCORE54ES08_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         301 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         292 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         287 |
| ordinary_alpha    | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L5_vol_adjusted_return             |         267 |
| interaction_alpha | HOLD_A7FFCORE54ES09_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         265 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         240 |
| ordinary_alpha    | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L0_raw_forward_return              |         239 |
| ordinary_alpha    | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L1_cross_sectional_relative_return |         239 |
| interaction_alpha | HOLD_A7FFCORE54ES07_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         238 |
| interaction_alpha | HOLD_A7FFCORE54ES08_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         235 |
| ordinary_alpha    | HOLD_A7FFCORE54ES06_CONTROL_DOMINATED     | L5_vol_adjusted_return             |         232 |
| ordinary_alpha    | HOLD_A7FFCORE54ES03_CONTROL_DOMINATED     | L5_vol_adjusted_return             |         223 |
| ordinary_alpha    | HOLD_A7FFCORE54ES04_PRE_MAY_UNSTABLE      | L7_ranked_future_return            |         217 |
| interaction_alpha | HOLD_A7FFCORE54ES09_CONTROL_DOMINATED     | L7_ranked_future_return            |         214 |
| ordinary_alpha    | HOLD_A7FFCORE54ES05_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         211 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_CONTROL_DOMINATED     | L3_liquidity_tier_relative_return  |         211 |
| interaction_alpha | HOLD_A7FFCORE54ES08_CONTROL_DOMINATED     | L0_raw_forward_return              |         211 |
| interaction_alpha | HOLD_A7FFCORE54ES08_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         210 |
| ordinary_alpha    | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |         207 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_CONTROL_DOMINATED     | L1_cross_sectional_relative_return |         204 |
| ordinary_alpha    | HOLD_A7FFCORE54ES00_CONTROL_DOMINATED     | L0_raw_forward_return              |         203 |
| interaction_alpha | HOLD_A7FFCORE54ES07_CONTROL_DOMINATED     | L7_ranked_future_return            |         200 |

## Semantic Response Summary

| a7input_queue     | semantic_pair                         | decision                                  | label_family                       |   row_count |
|:------------------|:--------------------------------------|:------------------------------------------|:-----------------------------------|------------:|
| ordinary_alpha    | volatility_like|volatility_like       | A7FFCORE54ES04_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          71 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES02_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          61 |
| interaction_alpha | price_like|volatility_like            | A7FFCORE54ES08_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          58 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          56 |
| ordinary_alpha    | price_like                            | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          55 |
| interaction_alpha | basis_premium_like|price_like         | A7FFCORE54ES07_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          52 |
| ordinary_alpha    | price_like|volatility_like            | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          51 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          45 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          38 |
| ordinary_alpha    | liquidity_like|volatility_like        | A7FFCORE54ES07_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          37 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES02_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          37 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES06_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          31 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          29 |
| ordinary_alpha    | volatility_like                       | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          28 |
| ordinary_alpha    | price_like|volatility_like            | A7FFCORE54ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          27 |
| ordinary_alpha    | liquidity_like|volatility_like        | A7FFCORE54ES06_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          23 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          23 |
| ordinary_alpha    | volatility_like                       | A7FFCORE54ES04_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          23 |
| ordinary_alpha    | price_like|volatility_like            | A7FFCORE54ES02_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          22 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7FFCORE54ES07_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          19 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          19 |
| ordinary_alpha    | price_like|volatility_like            | A7FFCORE54ES04_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          18 |
| interaction_alpha | basis_premium_like|volatility_like    | A7FFCORE54ES08_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          18 |
| interaction_alpha | basis_premium_like|volatility_like    | A7FFCORE54ES07_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          17 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES05_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          15 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES06_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          14 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          13 |
| ordinary_alpha    | basis_premium_like                    | A7FFCORE54ES00_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |          12 |
| interaction_alpha | basis_premium_like|positioning_like   | A7FFCORE54ES09_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          12 |
| ordinary_alpha    | basis_premium_like                    | A7FFCORE54ES00_NUMERIC_CLUE               | L1_cross_sectional_relative_return |          11 |
| ordinary_alpha    | basis_premium_like                    | A7FFCORE54ES00_NUMERIC_CLUE               | L0_raw_forward_return              |          11 |
| ordinary_alpha    | price_like|volatility_like            | A7FFCORE54ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          11 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES02_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          11 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES02_NUMERIC_CLUE               | L5_vol_adjusted_return             |          11 |
| ordinary_alpha    | basis_premium_like|positioning_like   | A7FFCORE54ES05_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |          10 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES02_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           9 |
| ordinary_alpha    | volatility_like|volatility_like       | A7FFCORE54ES01_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           9 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES00_NUMERIC_CLUE               | L5_vol_adjusted_return             |           8 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES00_NUMERIC_CLUE               | L5_vol_adjusted_return             |           8 |
| interaction_alpha | basis_premium_like|positioning_like   | A7FFCORE54ES08_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           8 |
| ordinary_alpha    | basis_premium_like                    | A7FFCORE54ES00_NUMERIC_CLUE               | L5_vol_adjusted_return             |           8 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES01_NUMERIC_CLUE               | L5_vol_adjusted_return             |           7 |
| ordinary_alpha    | basis_premium_like                    | A7FFCORE54ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           7 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES02_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           7 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES01_NUMERIC_CLUE               | L0_raw_forward_return              |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES02_NUMERIC_CLUE               | L5_vol_adjusted_return             |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES03_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES00_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES00_NUMERIC_CLUE               | L0_raw_forward_return              |           6 |
| interaction_alpha | basis_premium_like|price_like         | A7FFCORE54ES07_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES03_NUMERIC_CLUE               | L5_vol_adjusted_return             |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES02_NUMERIC_CLUE               | L0_raw_forward_return              |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES02_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           6 |
| interaction_alpha | basis_premium_like|price_like         | A7FFCORE54ES07_NUMERIC_CLUE               | L5_vol_adjusted_return             |           6 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES02_NUMERIC_CLUE               | L0_raw_forward_return              |           6 |
| ordinary_alpha    | price_like                            | A7FFCORE54ES03_NUMERIC_CLUE               | L5_vol_adjusted_return             |           6 |
| ordinary_alpha    | volatility_like|volatility_like       | A7FFCORE54ES03_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           6 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES07_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           6 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES01_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           6 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES02_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           6 |
| interaction_alpha | basis_premium_like|price_like         | A7FFCORE54ES07_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           5 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES01_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           5 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES01_NUMERIC_CLUE               | L0_raw_forward_return              |           5 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES01_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           5 |
| interaction_alpha | basis_premium_like|volatility_like    | A7FFCORE54ES07_NUMERIC_CLUE               | L5_vol_adjusted_return             |           5 |
| ordinary_alpha    | basis_premium_like|positioning_like   | A7FFCORE54ES06_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           5 |
| ordinary_alpha    | price_like                            | A7FFCORE54ES03_NUMERIC_CLUE               | L0_raw_forward_return              |           4 |
| ordinary_alpha    | price_like                            | A7FFCORE54ES03_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           4 |
| ordinary_alpha    | price_like                            | A7FFCORE54ES03_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           4 |
| interaction_alpha | basis_premium_like|basis_premium_like | A7FFCORE54ES07_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           4 |
| interaction_alpha | price_like|volatility_like            | A7FFCORE54ES08_NUMERIC_CLUE               | L5_vol_adjusted_return             |           4 |
| interaction_alpha | basis_premium_like|volatility_like    | A7FFCORE54ES07_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           4 |
| interaction_alpha | basis_premium_like|volatility_like    | A7FFCORE54ES07_NUMERIC_CLUE               | L0_raw_forward_return              |           4 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES00_RANK_LABEL_DIAGNOSTIC_CLUE | L7_ranked_future_return            |           4 |
| ordinary_alpha    | basis_premium_like|volatility_like    | A7FFCORE54ES01_NUMERIC_CLUE               | L5_vol_adjusted_return             |           4 |
| ordinary_alpha    | basis_premium_like|price_like         | A7FFCORE54ES00_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           4 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES00_NUMERIC_CLUE               | L0_raw_forward_return              |           4 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES00_NUMERIC_CLUE               | L3_liquidity_tier_relative_return  |           3 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | A7FFCORE54ES00_NUMERIC_CLUE               | L1_cross_sectional_relative_return |           3 |
| ordinary_alpha    | basis_premium_like|positioning_like   | A7FFCORE54ES06_NUMERIC_CLUE               | L5_vol_adjusted_return             |           3 |

## Selected Summary

| a7input_queue     | semantic_pair                         | label_family                      |   row_count |
|:------------------|:--------------------------------------|:----------------------------------|------------:|
| ordinary_alpha    | basis_premium_like|volatility_like    | L7_ranked_future_return           |          21 |
| ordinary_alpha    | basis_premium_like|price_like         | L7_ranked_future_return           |          19 |
| ordinary_alpha    | volatility_like|volatility_like       | L7_ranked_future_return           |          11 |
| ordinary_alpha    | basis_premium_like|price_like         | L5_vol_adjusted_return            |          10 |
| interaction_alpha | basis_premium_like|volatility_like    | L7_ranked_future_return           |          10 |
| interaction_alpha | basis_premium_like|positioning_like   | L7_ranked_future_return           |           9 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | L7_ranked_future_return           |           8 |
| ordinary_alpha    | price_like|volatility_like            | L7_ranked_future_return           |           7 |
| ordinary_alpha    | basis_premium_like|volatility_like    | L5_vol_adjusted_return            |           7 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | L5_vol_adjusted_return            |           6 |
| ordinary_alpha    | liquidity_like|volatility_like        | L7_ranked_future_return           |           6 |
| interaction_alpha | basis_premium_like|basis_premium_like | L7_ranked_future_return           |           4 |
| interaction_alpha | price_like|volatility_like            | L7_ranked_future_return           |           4 |
| interaction_alpha | basis_premium_like|volatility_like    | L5_vol_adjusted_return            |           4 |
| ordinary_alpha    | price_like                            | L7_ranked_future_return           |           3 |
| ordinary_alpha    | basis_premium_like|positioning_like   | L5_vol_adjusted_return            |           3 |
| ordinary_alpha    | basis_premium_like|positioning_like   | L7_ranked_future_return           |           3 |
| interaction_alpha | basis_premium_like|price_like         | L7_ranked_future_return           |           2 |
| interaction_alpha | price_like|volatility_like            | L5_vol_adjusted_return            |           2 |
| ordinary_alpha    | volatility_like                       | L7_ranked_future_return           |           2 |
| ordinary_alpha    | price_like|volatility_like            | L5_vol_adjusted_return            |           2 |
| interaction_alpha | basis_premium_like|basis_premium_like | L5_vol_adjusted_return            |           1 |
| interaction_alpha | basis_premium_like|positioning_like   | L5_vol_adjusted_return            |           1 |
| ordinary_alpha    | basis_premium_like                    | L5_vol_adjusted_return            |           1 |
| interaction_alpha | basis_premium_like|price_like         | L5_vol_adjusted_return            |           1 |
| ordinary_alpha    | basis_premium_like|basis_premium_like | L3_liquidity_tier_relative_return |           1 |
| ordinary_alpha    | price_like                            | L5_vol_adjusted_return            |           1 |

## External Detail Artifacts

```text
G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604
```

## Boundary

```text
numeric probe executed: true
replay executed: false
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
