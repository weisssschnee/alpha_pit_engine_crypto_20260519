# CRYPTO A7FF-55F FULL PRIMARY INPUT REBUILD

Generated: 2026-05-31T11:31:31Z

## Decision

`HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED`

A7FF-55F consolidates the rebuilt primary-label response inputs into one selector-repair dryrun. It does not execute replay or search. The detailed S02-S06 micro-shard artifacts were compacted into `runtime/a7ff55f_full_primary_input_rebuild/a7ff55f_available_primary_response_compact.csv` and intentionally not retained as standalone runtime directories.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_next_contract": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "available_response_sources": 17,
  "blockers": [
    "top_family_share_above_0p30",
    "top_motif_share_above_0p30",
    "top_label_share_above_0p35"
  ],
  "decision": "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED",
  "executes_replay": false,
  "executes_search": false,
  "executes_selector_dryrun": true,
  "generated_at": "2026-05-31T11:31:31Z",
  "next_allowed": "A7FF-55R selector/field-family repair contract",
  "primary_label_candidate_rows": 86,
  "response_rows": 13800,
  "selected_family_count": 6,
  "selected_label_counts": {
    "L0_raw_forward_return": 10,
    "L1_cross_sectional_relative_return": 12,
    "L3_liquidity_tier_relative_return": 8
  },
  "selected_motif_count": 4,
  "selected_rows": 30,
  "stage": "A7FF-55F",
  "top_family_share": 0.4,
  "top_label_share": 0.4,
  "top_motif_share": 0.5333333333333333,
  "uses_may": false
}
```

## Source Audit

| source_shard   | path                                                                                    |   rows |   numeric_clue_rows |   selected_portfolio_rows | available   |
|:---------------|:----------------------------------------------------------------------------------------|-------:|--------------------:|--------------------------:|:------------|
| S00            | runtime\a7ff53e_numeric_response_execution_s00\a7ff53e_s00_label_response_metrics.csv   |   3000 |                  77 |                        24 | True        |
| S01P           | runtime\a7ff55d_selector_repair_inputs_s01p\a7ff55d_s01p_label_response_metrics.csv     |   1800 |                   7 |                         4 | True        |
| S02P00         | runtime\a7ff55f_selector_repair_inputs_s02p00\a7ff55f_s02p00_label_response_metrics.csv |    600 |                   0 |                         0 | True        |
| S02P01         | runtime\a7ff55f_selector_repair_inputs_s02p01\a7ff55f_s02p01_label_response_metrics.csv |    600 |                   0 |                         0 | True        |
| S02P02         | runtime\a7ff55f_selector_repair_inputs_s02p02\a7ff55f_s02p02_label_response_metrics.csv |    600 |                   3 |                         1 | True        |
| S03P00         | runtime\a7ff55f_selector_repair_inputs_s03p00\a7ff55f_s03p00_label_response_metrics.csv |    600 |                   2 |                         1 | True        |
| S03P01         | runtime\a7ff55f_selector_repair_inputs_s03p01\a7ff55f_s03p01_label_response_metrics.csv |    600 |                   1 |                         1 | True        |
| S03P02         | runtime\a7ff55f_selector_repair_inputs_s03p02\a7ff55f_s03p02_label_response_metrics.csv |    600 |                   6 |                         3 | True        |
| S04P00         | runtime\a7ff55f_selector_repair_inputs_s04p00\a7ff55f_s04p00_label_response_metrics.csv |    600 |                  20 |                         6 | True        |
| S04P01         | runtime\a7ff55f_selector_repair_inputs_s04p01\a7ff55f_s04p01_label_response_metrics.csv |    600 |                  19 |                         4 | True        |
| S04P02         | runtime\a7ff55f_selector_repair_inputs_s04p02\a7ff55f_s04p02_label_response_metrics.csv |    600 |                  11 |                         3 | True        |
| S05P00         | runtime\a7ff55f_selector_repair_inputs_s05p00\a7ff55f_s05p00_label_response_metrics.csv |    600 |                   3 |                         1 | True        |
| S05P01         | runtime\a7ff55f_selector_repair_inputs_s05p01\a7ff55f_s05p01_label_response_metrics.csv |    600 |                   3 |                         1 | True        |
| S05P02         | runtime\a7ff55f_selector_repair_inputs_s05p02\a7ff55f_s05p02_label_response_metrics.csv |    600 |                   0 |                         0 | True        |
| S06P00         | runtime\a7ff55f_selector_repair_inputs_s06p00\a7ff55f_s06p00_label_response_metrics.csv |    600 |                   0 |                         0 | True        |
| S06P01         | runtime\a7ff55f_selector_repair_inputs_s06p01\a7ff55f_s06p01_label_response_metrics.csv |    600 |                   0 |                         0 | True        |
| S06P02         | runtime\a7ff55f_selector_repair_inputs_s06p02\a7ff55f_s06p02_label_response_metrics.csv |    600 |                   0 |                         0 | True        |

## Selected Label Summary

| label_family                       |   selected_count |
|:-----------------------------------|-----------------:|
| L0_raw_forward_return              |               10 |
| L1_cross_sectional_relative_return |               12 |
| L3_liquidity_tier_relative_return  |                8 |

## Selected Family Summary

| semantic_pair                         |   selected_count |
|:--------------------------------------|-----------------:|
| basis_premium_like\|price_return_like |               11 |
| liquidity_like\|price_return_like     |                1 |
| open_interest_like\|price_return_like |                1 |
| positioning_like\|price_return_like   |                3 |
| regime_state\|price_return_like       |               12 |
| volatility_like\|basis_premium_like   |                2 |

## Selected Motif Summary

| motif         |   selected_count |
|:--------------|-----------------:|
| safe_div_abs  |                6 |
| signed_spread |                3 |
| spread_rank   |               16 |
| sub           |                5 |

## Candidate Family Summary

| label_family                       | semantic_pair                         |   candidate_rows |
|:-----------------------------------|:--------------------------------------|-----------------:|
| L3_liquidity_tier_relative_return  | regime_state\|price_return_like       |               14 |
| L1_cross_sectional_relative_return | basis_premium_like\|price_return_like |               13 |
| L3_liquidity_tier_relative_return  | basis_premium_like\|price_return_like |               13 |
| L0_raw_forward_return              | basis_premium_like\|price_return_like |               11 |
| L1_cross_sectional_relative_return | regime_state\|price_return_like       |               11 |
| L0_raw_forward_return              | regime_state\|price_return_like       |                9 |
| L1_cross_sectional_relative_return | positioning_like\|price_return_like   |                3 |
| L0_raw_forward_return              | volatility_like\|basis_premium_like   |                2 |
| L1_cross_sectional_relative_return | volatility_like\|basis_premium_like   |                2 |
| L3_liquidity_tier_relative_return  | volatility_like\|basis_premium_like   |                2 |
| L0_raw_forward_return              | open_interest_like\|price_return_like |                1 |
| L0_raw_forward_return              | positioning_like\|price_return_like   |                1 |
| L1_cross_sectional_relative_return | open_interest_like\|price_return_like |                1 |
| L0_raw_forward_return              | liquidity_like\|price_return_like     |                1 |
| L3_liquidity_tier_relative_return  | open_interest_like\|price_return_like |                1 |
| L3_liquidity_tier_relative_return  | liquidity_like\|price_return_like     |                1 |

## Boundary

```text
selector dryrun executed: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
