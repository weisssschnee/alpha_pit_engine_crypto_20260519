# CRYPTO A7FF-CORE16G FAMILY-NATIVE INTERACTION CONTRACT

Generated: 2026-06-01T09:24:48Z

## Decision

`PASS_A7FFCORE16G_FAMILY_NATIVE_INTERACTION_CONTRACT_READY_FOR_CORE16GE`

CORE16G defines a typed, family-native interaction probe contract after CORE16FE showed non-basis single-field supply is insufficient. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16ge": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16G_FAMILY_NATIVE_INTERACTION_CONTRACT_READY_FOR_CORE16GE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T09:24:48Z",
  "interaction_family_count": 7,
  "near_miss_non_basis_count": 46,
  "next_allowed": "A7FF-CORE16GE family-native interaction probe execution",
  "source_decision": "PASS_A7FFCORE16FER_NON_BASIS_FORENSIC_COMPLETE_READY_FOR_CORE16G",
  "source_stage": "A7FF-CORE16FER",
  "stage": "A7FF-CORE16G"
}
```

## Source Near-Miss Summary

| field_family   |   near_miss_count |   transform_count |   label_family_count |   median_control_ratio |
|:---------------|------------------:|------------------:|---------------------:|-----------------------:|
| price_return   |                37 |                 8 |                    4 |                1.27518 |
| open_interest  |                 6 |                 1 |                    3 |                1.16911 |
| positioning    |                 2 |                 1 |                    2 |                1.28778 |
| taker_flow     |                 1 |                 1 |                    1 |                1.25061 |

## Interaction Families

| interaction_family                         | left_family   | right_family                | allowed_transforms                               | role                                | rationale                                                                                                |
|:-------------------------------------------|:--------------|:----------------------------|:-------------------------------------------------|:------------------------------------|:---------------------------------------------------------------------------------------------------------|
| I0_OI_delta_x_price_move                   | open_interest | price_return                | delta_4h;delta_24h;zscore_168h;spread_short_long | ordinary_alpha_probe                | OI single-field rows have near misses but need price-move context to avoid slow leverage-state ambiguity |
| I1_OI_delta_x_funding_abs                  | open_interest | funding                     | delta_4h;delta_24h;zscore_168h                   | ordinary_alpha_probe                | leverage expansion should be interpreted under crowding/funding state                                    |
| I2_OI_delta_x_basis_premium_dislocation    | open_interest | basis_premium               | delta_4h;zscore_72h;zscore_168h;shock_24h        | ordinary_alpha_probe_with_basis_cap | use basis/premium as context leg, not dominant standalone source                                         |
| I3_positioning_divergence_x_price_or_basis | positioning   | price_return;basis_premium  | spread_short_long;delta_24h;zscore_168h          | ordinary_alpha_probe                | positioning strict supply is thin but divergence may only matter under price/basis context               |
| I4_taker_flow_x_OI_or_liquidity            | taker_flow    | open_interest;liquidity     | delta_1h;delta_4h;shock_24h;tsrank_72h           | diagnostic_to_alpha_probe           | flow alone has zero strict supply; test only with leverage or liquidity state                            |
| I5_liquidity_state_x_basis_or_positioning  | liquidity     | basis_premium;positioning   | zscore_168h;tsrank_168h;shock_24h                | state_conditioned_probe             | liquidity is likely a state/neutralizer unless interaction beats controls                                |
| I6_volatility_state_x_basis_or_OI          | volatility    | basis_premium;open_interest | zscore_72h;zscore_168h;spread_short_long         | state_conditioned_probe             | volatility should condition dislocation/leverage signals, not become pure volatility beta                |

## Operator Policy

| operator    | allowed   | constraint                                                          |
|:------------|:----------|:--------------------------------------------------------------------|
| Mul         | True      | only typed left/right families in interaction_families              |
| SafeDiv     | True      | denominator must be positive-stable; winsorize extreme denominators |
| Sub         | True      | only for divergence/spread semantics                                |
| Add         | True      | only after same semantic scale normalization                        |
| ZScore      | True      | lookback 72h/168h only                                              |
| TSRank      | True      | lookback 72h/168h only                                              |
| Clip        | True      | predefined quantile clip; no tuned thresholds                       |
| IfElse      | False     | blocked: no deep conditionals or threshold masks                    |
| SignedPower | False     | blocked: unbounded nonlinear transform                              |

## Execution Contract

```json
{
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "forbidden": [
    "open grammar FormulaGen",
    "bounded replay",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "horizons": [
    1,
    4,
    8,
    24
  ],
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "max_blueprints": 2048,
  "name": "family-native interaction probe execution",
  "promotion_gate": {
    "control_ratio_for_promotion": "< 1.0",
    "interaction_probe_candidates": 64,
    "near_miss_lane": "1.0 <= control_ratio < 1.5 forensic-only",
    "non_basis_family_count": 4,
    "top_family_share_max": 0.4
  },
  "stage": "A7FF-CORE16GE",
  "target_interaction_families": [
    "I0_OI_delta_x_price_move",
    "I1_OI_delta_x_funding_abs",
    "I2_OI_delta_x_basis_premium_dislocation",
    "I3_positioning_divergence_x_price_or_basis",
    "I4_taker_flow_x_OI_or_liquidity",
    "I5_liquidity_state_x_basis_or_positioning",
    "I6_volatility_state_x_basis_or_OI"
  ]
}
```

## Blocked Actions

| item                                | reason                                                    |
|:------------------------------------|:----------------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked until CORE16GE interaction probe passes           |
| formula generation                  | blocked: CORE16G authorizes typed interaction probes only |
| bounded replay                      | blocked: no broad objective atlas                         |
| large search                        | blocked                                                   |
| alpha proof / shadow / paper / live | not authorized                                            |
