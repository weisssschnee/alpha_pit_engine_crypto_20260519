# CRYPTO A7FF-CORE16ER EXPANDED ATLAS FORENSIC

Generated: 2026-06-01T09:17:15Z

## Decision

`PASS_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_COMPLETE_READY_FOR_CORE16F`

CORE16ER freezes the CORE16E result. CORE16E deliberately relaxed the lag gate and still produced a basis/premium-dominated atlas, so the blocker is field-family supply concentration, not an over-conservative latency rule.

This stage does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "atlas_candidate_count": 149,
  "authorizes_alpha_proof": false,
  "authorizes_core16f_contract": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_COMPLETE_READY_FOR_CORE16F",
  "dominant_failure": "basis_premium_supply_concentration",
  "executes_replay": false,
  "executes_search": false,
  "field_family_count": 3,
  "generated_at": "2026-06-01T09:17:15Z",
  "next_allowed": "A7FF-CORE16F non-basis field-family supply repair contract",
  "source_decision": "HOLD_A7FFCORE16E_EXPANDED_PRIMITIVE_ATLAS_INSUFFICIENT",
  "source_stage": "A7FF-CORE16E",
  "stage": "A7FF-CORE16ER",
  "top_family_share": 0.9664429530201343
}
```

## Family Concentration

| field_family   |   atlas_candidate_count |      share |   transform_count |   label_family_count |   lag_ok_candidate_count |   median_control_ratio | status                    |
|:---------------|------------------------:|-----------:|------------------:|---------------------:|-------------------------:|-----------------------:|:--------------------------|
| basis_premium  |                     144 | 0.966443   |                 9 |                    4 |                       67 |               0.657844 | dominant_saturated_family |
| price_return   |                       4 | 0.0268456  |                 2 |                    3 |                        1 |               0.589453 | thin_positive_supply      |
| positioning    |                       1 | 0.00671141 |                 1 |                    1 |                        1 |               0.983348 | thin_positive_supply      |

## Family Supply Forensic

| field_family              |   scored_rows |   atlas_candidate_count |   lag_ok_candidate_count |   near_miss_count |   median_control_ratio |   transform_count |   label_family_count | supply_class          |
|:--------------------------|--------------:|------------------------:|-------------------------:|------------------:|-----------------------:|------------------:|---------------------:|:----------------------|
| basis_premium             |           800 |                     144 |                       67 |                33 |                3.88014 |                10 |                    4 | positive_concentrated |
| price_return              |           320 |                       4 |                        1 |                18 |               13.8974  |                10 |                    4 | near_miss_repairable  |
| positioning               |           480 |                       1 |                        1 |                 0 |               11.2452  |                10 |                    4 | zero_or_control_like  |
| open_interest             |           480 |                       0 |                        0 |                 5 |               11.4071  |                10 |                    4 | near_miss_repairable  |
| listing_age               |           320 |                       0 |                        0 |                 1 |                4.88101 |                10 |                    4 | near_miss_repairable  |
| coverage                  |           320 |                       0 |                        0 |                 0 |              nan       |                10 |                    4 | zero_or_control_like  |
| funding                   |           480 |                       0 |                        0 |                 0 |                3.93035 |                10 |                    4 | zero_or_control_like  |
| liquidity                 |           640 |                       0 |                        0 |                 0 |               11.4725  |                10 |                    4 | zero_or_control_like  |
| liquidity_volatility      |           160 |                       0 |                        0 |                 0 |               12.4723  |                10 |                    4 | zero_or_control_like  |
| listing_age_interaction   |           320 |                       0 |                        0 |                 0 |               12.3357  |                10 |                    4 | zero_or_control_like  |
| open_interest_interaction |           160 |                       0 |                        0 |                 0 |               17.6108  |                10 |                    4 | zero_or_control_like  |
| taker_flow                |           320 |                       0 |                        0 |                 0 |                4.49078 |                10 |                    4 | zero_or_control_like  |
| volatility                |           320 |                       0 |                        0 |                 0 |               27.6406  |                10 |                    4 | zero_or_control_like  |

## Repair Actions

| action_id                           | target                                                | action                                                                                                                      | reason                                                                                                     |
|:------------------------------------|:------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
| R0_cap_basis_premium_atlas          | basis_premium                                         | treat as saturated diagnostic supply; cap in any future atlas/queue until non-basis families show supply                    | CORE16E top_family_share is above 96 percent even after lag gate relaxation                                |
| R1_non_basis_near_miss_repair       | open_interest, price_return, positioning, listing_age | mine near-miss rows with control_ratio between 1.0 and 1.5 and require split-specific failure attribution before generation | non-basis families have sparse or zero atlas supply but some near-miss evidence exists                     |
| R2_family_native_label_policy       | all non-basis families                                | allow family-native label/transform pair contracts rather than one global pass gate                                         | global primitive atlas pass gate rewards basis/premium and suppresses sparse event-like families           |
| R3_interaction_probe_before_formula | OI, positioning, taker_flow, liquidity, volatility    | run typed interaction probes only after single-family near-miss repair; no open grammar                                     | single-field response is insufficient, but direct formula generation would amplify control-like structures |
| R4_stop_core17_until_breadth        | CORE17/search                                         | block objective seed policy, replay expansion, and formula search until non-basis breadth gate passes                       | 149 candidates are not useful if 144 come from one family                                                  |

## Next Contract

```json
{
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "forbidden": [
    "CORE17 objective seed policy",
    "formula generation",
    "replay expansion",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "minimum_success_criteria": {
    "basis_premium_share_max": 0.5,
    "non_basis_candidate_count": 32,
    "non_basis_field_family_count": 4,
    "top_family_share_max": 0.5
  },
  "name": "non-basis field-family supply repair contract",
  "scope": [
    "basis/premium cap policy",
    "non-basis near-miss mining",
    "family-native label/transform pass gates",
    "typed interaction probe contract"
  ],
  "stage": "A7FF-CORE16F"
}
```

## Blocked Actions

| item                                | reason                                                |
|:------------------------------------|:------------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked: CORE16E atlas breadth failed                 |
| A7FF formula generation             | blocked: primitive/operator supply is basis-dominated |
| A7FF bounded replay expansion       | blocked: no broad objective atlas to replay           |
| A7FF large search                   | blocked                                               |
| alpha proof / shadow / paper / live | not authorized                                        |
