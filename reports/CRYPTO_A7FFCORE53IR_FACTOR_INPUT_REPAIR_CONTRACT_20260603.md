# CRYPTO A7FF-CORE53IR FACTOR INPUT REPAIR CONTRACT

Generated: 2026-06-03T01:46:49Z

## Decision

`PASS_A7FFCORE53IR_FACTOR_INPUT_REPAIR_CONTRACT_READY_FOR_REPAIRED_QUEUE_BUILDER`

CORE53IR turns CORE53I factor-input redundancy findings into queue construction constraints. It does not execute generation, replay, search, proof, or promotion.

## Current Snapshot

```json
{
  "blockers": [
    "strict_input_type_breadth_low"
  ],
  "diagnostic_input_type_count": 18,
  "strict_input_type_count": 1,
  "top_base_field_share": 0.15625,
  "top_input_field_set_share": 0.028645833333333332,
  "top_input_type_share": 0.4348958333333333
}
```

## Field Type Quota Policy

| field_type         |   max_candidate_share |   min_candidate_share | role                         |
|:-------------------|----------------------:|----------------------:|:-----------------------------|
| price_like         |                  0.3  |                  0.05 | baseline_or_interaction_only |
| funding_like       |                  0.25 |                  0.05 | signal_or_state              |
| positioning_like   |                  0.25 |                  0.08 | signal_or_state              |
| basis_premium_like |                  0.25 |                  0.05 | signal_or_state              |
| liquidity_like     |                  0.25 |                  0.05 | interaction_or_neutralizer   |
| volatility_like    |                  0.2  |                  0.04 | risk_scale_or_interaction    |
| state_or_taxonomy  |                  0.2  |                  0.03 | condition_or_neutralizer     |
| generic_numeric    |                  0.1  |                  0    | restricted_until_retyped     |

## Pair Quota Policy

| pair_rule                           | status         |   max_share | reason                                            |   min_share |
|:------------------------------------|:---------------|------------:|:--------------------------------------------------|------------:|
| single_price_like                   | cap            |        0.12 | price-like standalone often wraps market beta     |      nan    |
| single_funding_like                 | cap            |        0.1  | funding standalone has high control sensitivity   |      nan    |
| positioning_like|funding_like       | require_quota  |      nan    | crowding plus leverage-state interaction          |        0.06 |
| positioning_like|basis_premium_like | require_quota  |      nan    | leverage expansion under dislocation              |        0.05 |
| positioning_like|liquidity_like     | require_quota  |      nan    | crowding under tradability/liquidity state        |        0.05 |
| funding_like|volatility_like        | require_quota  |      nan    | crowding under volatility state                   |        0.04 |
| basis_premium_like|liquidity_like   | require_quota  |      nan    | dislocation with tradability                      |        0.04 |
| state_or_taxonomy interactions      | condition_only |        0.15 | state fields should not dominate standalone alpha |      nan    |

## Repair Actions

| action_id   | action                                                                   | required   |
|:------------|:-------------------------------------------------------------------------|:-----------|
| R0          | retype derived/regime fields from compact frame before formula selection | True       |
| R1          | apply field-type quota before materialization queue selection            | True       |
| R2          | apply input-field-set cap before selector/replay                         | True       |
| R3          | force minimum OI/positioning interaction supply                          | True       |
| R4          | force minimum funding/basis/liquidity/volatility interaction supply      | True       |
| R5          | separate condition/state variables from standalone alpha fields          | True       |
| R6          | rerun CORE53I after repaired queue construction                          | True       |

## Queue Gate

```json
{
  "candidate_queue_requirements": {
    "max_top_base_field_share": 0.25,
    "max_top_input_field_set_share": 0.08,
    "max_top_input_type_share": 0.35,
    "min_candidate_count": 384,
    "min_input_type_count": 7,
    "min_required_interaction_pair_count": 5,
    "min_strict_candidate_input_type_count_after_repaired_targets": 3,
    "no_single_price_or_funding_dominance": true
  },
  "forbidden": [
    "counting multiple formulas with identical input field set as independent breadth",
    "counting L0_raw and L1_xs as independent label evidence",
    "allowing one strict clue from one input type to authorize search",
    "expanding formula search before repaired target replay passes input breadth gate"
  ],
  "strict_promotion_requirements": {
    "median_control_ratio_max": 0.9,
    "min_independent_repaired_target_count": 3,
    "min_input_type_count": 3,
    "min_semantic_pair_count": 3,
    "requires_positive_portfolio_net_spread_proxy": true
  }
}
```

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE54 repaired factor-input queue builder contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
