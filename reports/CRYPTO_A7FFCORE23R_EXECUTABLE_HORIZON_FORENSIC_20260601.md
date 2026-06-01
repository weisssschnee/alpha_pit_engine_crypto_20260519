# CRYPTO A7FF-CORE23R EXECUTABLE-HORIZON FORENSIC

Generated: 2026-06-01T15:35:57Z

## Decision

`PASS_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_COMPLETE_READY_FOR_CORE24`

CORE23R freezes the CORE23E hold and identifies the next bottleneck. It does not authorize formula generation, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core24_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "best_executable_h4_plus_clean_candidate_count": 4,
  "best_executable_h4_plus_clean_lane_count": 2,
  "best_same_bar_h4_plus_candidate_count": 7,
  "best_same_bar_h4_plus_lane_count": 3,
  "decision": "PASS_A7FFCORE23R_EXECUTABLE_HORIZON_FORENSIC_COMPLETE_READY_FOR_CORE24",
  "dominant_failure": "executable_lane_supply_too_narrow",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:35:57Z",
  "missing_executable_lanes": [
    "S0_positioning_price_basis",
    "S1_basis_premium_funding"
  ],
  "next_allowed": "A7FF-CORE24 lower-turnover executable lane repair contract",
  "source_decision": "HOLD_A7FFCORE23E_EXECUTABLE_HORIZON_SUPPLY_INSUFFICIENT",
  "source_stage": "A7FF-CORE23E",
  "stage": "A7FF-CORE23R"
}
```

## Diagnosis

| finding                  | value                                               | interpretation                                                                |
|:-------------------------|:----------------------------------------------------|:------------------------------------------------------------------------------|
| executable_supply_exists | 4                                                   | there is H4+ one-bar executable evidence, but not enough breadth              |
| lane_breadth_deficit     | 2                                                   | only two seed lanes survive; missing lanes must be repaired before any search |
| same_bar_excess_supply   | 3                                                   | same-bar H4+ diagnostics still exceed executable one-bar evidence             |
| missing_executable_lanes | S0_positioning_price_basis,S1_basis_premium_funding | lane repair target set                                                        |
| dominant_failure         | executable_lane_supply_too_narrow                   | the bottleneck is not label translation anymore; it is executable breadth     |

## Lane Presence

| seed_lane                  |   clean_candidate_count |   label_family_count |
|:---------------------------|------------------------:|---------------------:|
| S2_taker_flow_liquidity_oi |                       1 |                    1 |
| S3_cross_family_bridge     |                       3 |                    3 |

## Label Presence

| label_family                       |   clean_candidate_count |   lane_count |
|:-----------------------------------|------------------------:|-------------:|
| L0_raw_forward_return              |                       1 |            1 |
| L1_cross_sectional_relative_return |                       1 |            1 |
| L3_liquidity_tier_relative_return  |                       1 |            1 |
| L5_vol_adjusted_return             |                       1 |            1 |

## Field Usage

| field                              |   usage_count |
|:-----------------------------------|--------------:|
| open_interest_value_last           |             3 |
| top_long_short_position_ratio_last |             3 |
| open_interest_last                 |             1 |
| taker_buy_sell_volume_ratio_last   |             1 |

## Recommended Actions

| next_stage                 | action                                         | rationale                                                                                      | authorized   |
|:---------------------------|:-----------------------------------------------|:-----------------------------------------------------------------------------------------------|:-------------|
| A7FF-CORE24                | lower-turnover executable lane repair contract | repair missing S0/S1 executable lanes and H4/H8 one-bar conversion without open formula search | True         |
| A7FF search / large search | blocked                                        | current executable clean supply is 4 candidates / 2 lanes only                                 | False        |
