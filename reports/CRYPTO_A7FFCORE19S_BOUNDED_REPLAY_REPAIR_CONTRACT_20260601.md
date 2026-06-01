# CRYPTO A7FF-CORE19S BOUNDED REPLAY REPAIR CONTRACT

Generated: 2026-06-01T15:01:49Z

## Decision

`PASS_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_READY_FOR_CORE19SE`

CORE19S defines replay repair only. It does not execute formula generation, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core19se": true,
  "authorizes_core20": false,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE19S_BOUNDED_REPLAY_REPAIR_CONTRACT_READY_FOR_CORE19SE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:01:49Z",
  "next_allowed": "A7FF-CORE19SE bounded replay repair execution",
  "source_decision": "PASS_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_COMPLETE_READY_FOR_CORE19S",
  "source_replay_clean_candidate_count": 2,
  "source_replay_clean_seed_lane_count": 2,
  "source_stage": "A7FF-CORE19R",
  "stage": "A7FF-CORE19S"
}
```

## Repair Policy

| repair_lane                    | action                                                                                              | allowed   | forbidden                                                          |
|:-------------------------------|:----------------------------------------------------------------------------------------------------|:----------|:-------------------------------------------------------------------|
| L0_cost_tier_attribution       | re-evaluate clean supply at 2bps/5bps/10bps/20bps without changing candidate orientation            | True      | using cost tier to claim alpha proof                               |
| L1_lag_attribution             | separate same-bar, one-bar-lag, and stale-lag failure counts                                        | True      | promoting same-bar-only candidates                                 |
| L2_label_translation           | audit L0/L1/L3/L5 and horizon-24 translation by lane                                                | True      | L5-only pass as search-ready evidence                              |
| L3_lane_specific_replay_packet | construct a diagnostic repair packet preserving S2/S3 clean clues and testing S0/S1 failure reasons | True      | adding new formula generation or changing the locked packet source |

## Execution Plan

| stage         | action                                                 | input                                       | output                                                       | authorized   |
|:--------------|:-------------------------------------------------------|:--------------------------------------------|:-------------------------------------------------------------|:-------------|
| A7FF-CORE19SE | bounded replay repair execution                        | CORE19E replay rows + CORE17E locked packet | cost/lag/label/lane attribution and repaired replay decision | True         |
| A7FF-CORE20   | replay-clean consolidation / search-readiness contract | CORE19SE pass only                          | contract only                                                | False        |

## Source Failure Summary

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
