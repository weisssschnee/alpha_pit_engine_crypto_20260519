# CRYPTO A7FF-CORE19R BOUNDED REPLAY FORENSIC

Generated: 2026-06-01T15:00:10Z

## Decision

`PASS_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_COMPLETE_READY_FOR_CORE19S`

CORE19R freezes the CORE19E bounded replay result. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core19s": true,
  "authorizes_core20": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_COMPLETE_READY_FOR_CORE19S",
  "dominant_failure": "bounded_replay_translation_supply_insufficient",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:00:10Z",
  "next_allowed": "A7FF-CORE19S bounded replay repair contract",
  "replay_clean_candidate_count": 2,
  "replay_clean_seed_lane_count": 2,
  "source_decision": "HOLD_A7FFCORE19E_BOUNDED_REPLAY_INSUFFICIENT",
  "source_stage": "A7FF-CORE19E",
  "stage": "A7FF-CORE19R"
}
```

## Failure Summary

| seed_lane                      | primary_failure                              |   rows |   label_family_count |
|:-------------------------------|:---------------------------------------------|-------:|---------------------:|
| S0_positioning_price_basis     | cost_adjusted_spread_not_positive_all_premay |     31 |                    3 |
| S1_liquidity_basis_positioning | cost_adjusted_spread_not_positive_all_premay |     33 |                    3 |
| S2_taker_flow_liquidity_oi     | cost_adjusted_spread_not_positive_all_premay |      8 |                    3 |
| S2_taker_flow_liquidity_oi     | one_bar_lag_not_positive_all_premay          |      2 |                    1 |
| S2_taker_flow_liquidity_oi     | clean                                        |      1 |                    1 |
| S2_taker_flow_liquidity_oi     | control_ratio_not_clean_all_premay           |      1 |                    1 |
| S3_cross_family_bridge         | cost_adjusted_spread_not_positive_all_premay |     13 |                    3 |
| S3_cross_family_bridge         | one_bar_lag_not_positive_all_premay          |      5 |                    1 |
| S3_cross_family_bridge         | clean                                        |      1 |                    1 |
| S3_cross_family_bridge         | control_ratio_not_clean_all_premay           |      1 |                    1 |

## Clean Clue Summary

| seed_lane                  | label_family                      |   rows |   median_control_ratio |   median_cost_adjusted_spread |
|:---------------------------|:----------------------------------|-------:|-----------------------:|------------------------------:|
| S2_taker_flow_liquidity_oi | L5_vol_adjusted_return            |      1 |               0.94762  |                   0.0660384   |
| S3_cross_family_bridge     | L3_liquidity_tier_relative_return |      1 |               0.705794 |                   0.000494357 |

## Recommended Actions

| action_id                 | action                                                               | reason                                                                                                                                       |
|:--------------------------|:---------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------|
| R0_no_large_search        | do not proceed to CORE20/search-readiness                            | bounded replay clean supply is 2 candidates across 2 lanes, below the 12/3 gate                                                              |
| R1_contract_replay_repair | write CORE19S bounded replay repair contract                         | the failure has moved from seed supply to replay translation; repair should target replay label/cost/lag translation, not formula generation |
| R2_preserve_clean_clues   | freeze the 2 replay-clean candidates as diagnostic replay clues only | they are not enough for search readiness or alpha proof                                                                                      |
