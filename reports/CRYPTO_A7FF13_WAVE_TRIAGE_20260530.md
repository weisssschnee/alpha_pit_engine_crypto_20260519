# CRYPTO A7FF-13 WAVE TRIAGE

Generated: 2026-05-30T04:10:27Z

## Decision

`HOLD_A7FF13_SELECTOR_LABEL_CONCENTRATION_AFTER_NUMERIC_SCALEUP`

A7FF-13 compares the A7FF-12 raw non-L7 clue surface against the selected portfolio queue. It does not run generation, replay, search, alpha proof, shadow, paper, or live execution.

## Manifest

```json
{
  "authorizes_a7ff14_selector_repair_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FF13_SELECTOR_LABEL_CONCENTRATION_AFTER_NUMERIC_SCALEUP",
  "generated_at": "2026-05-30T04:10:27Z",
  "input_blueprints": 720,
  "priority_top_label_share": 1.0,
  "raw_non_l7_label_families": 4,
  "raw_non_l7_numeric_clue_rows": 461,
  "raw_rank_label_diagnostic_clue_rows": 146,
  "selected_priority_clean_count": 39,
  "selected_priority_label_families": 1,
  "selected_queue_count": 83,
  "selected_top_label_share": 0.6265060240963856,
  "source_decision": "PASS_A7FF12_COMPANY_NUMERIC_WAVE_AGGREGATE_BUILT",
  "source_stage": "A7FF-12-COMPANY-NUMERIC-WAVE-AGGREGATE",
  "stage": "A7FF-13-WAVE-TRIAGE",
  "uses_may": false
}
```

## Raw Clue Label Surface

| label_family                       |   label_horizon_h |   clue_count |
|:-----------------------------------|------------------:|-------------:|
| L5_vol_adjusted_return             |                 1 |           83 |
| L3_liquidity_tier_relative_return  |                 1 |           79 |
| L1_cross_sectional_relative_return |                 1 |           75 |
| L0_raw_forward_return              |                 1 |           72 |
| L5_vol_adjusted_return             |                 4 |           39 |
| L5_vol_adjusted_return             |                 8 |           29 |
| L1_cross_sectional_relative_return |                 4 |           25 |
| L3_liquidity_tier_relative_return  |                 4 |           24 |
| L0_raw_forward_return              |                 4 |           22 |
| L0_raw_forward_return              |                 8 |            4 |
| L1_cross_sectional_relative_return |                 8 |            3 |
| L3_liquidity_tier_relative_return  |                 8 |            3 |
| L5_vol_adjusted_return             |                24 |            2 |
| L1_cross_sectional_relative_return |                24 |            1 |

## Selected Label Surface

| label_family                       |   label_horizon_h |   selected_count |   priority_clean_count |   median_control_ratio |   median_cost10 |
|:-----------------------------------|------------------:|-----------------:|-----------------------:|-----------------------:|----------------:|
| L5_vol_adjusted_return             |                 1 |               29 |                     24 |               0.580525 |      0.0826112  |
| L5_vol_adjusted_return             |                 8 |               15 |                     11 |               0.640765 |      0.356854   |
| L5_vol_adjusted_return             |                 4 |                7 |                      4 |               0.746835 |      0.207607   |
| L7_ranked_future_return            |                 4 |                9 |                      0 |               0.70233  |      0.0293897  |
| L7_ranked_future_return            |                 8 |                9 |                      0 |               0.938302 |      0.0274614  |
| L7_ranked_future_return            |                 1 |                7 |                      0 |               0.810981 |      0.0196691  |
| L3_liquidity_tier_relative_return  |                 1 |                3 |                      0 |               0.698038 |     -0.0010009  |
| L1_cross_sectional_relative_return |                 4 |                2 |                      0 |               0.925447 |     -0.00123066 |
| L1_cross_sectional_relative_return |                 1 |                1 |                      0 |               0.729431 |     -0.00145367 |
| L5_vol_adjusted_return             |                24 |                1 |                      0 |               0.990454 |      0.144861   |

## Selected Semantic Surface

| semantic_pair                          |   selected_count |   priority_clean_count |   median_control_ratio |
|:---------------------------------------|-----------------:|-----------------------:|-----------------------:|
| basis_premium_like\|positioning_like   |               27 |                     15 |               0.698038 |
| basis_premium_like\|basis_premium_like |               29 |                     13 |               0.659917 |
| basis_premium_like\|volatility_like    |               19 |                      8 |               0.797678 |
| basis_premium_like\|price_like         |                8 |                      3 |               0.756655 |

## Interpretation

```text
A7FF-12 successfully expanded numeric evidence: L0/L1/L3/L5 raw non-L7 clue families are all present.
The selected queue still concentrates the clean follow-up set in L5_vol_adjusted_return.
The next step is selector repair with label-family balancing, not more unconstrained formula generation.
```

## Boundary

```text
No May is used.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
A7FF-14 may only be a selector repair / dry rerank contract.
```
