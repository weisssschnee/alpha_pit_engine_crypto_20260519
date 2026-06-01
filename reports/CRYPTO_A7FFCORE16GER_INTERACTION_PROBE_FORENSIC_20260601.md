# CRYPTO A7FF-CORE16GER INTERACTION PROBE FORENSIC

Generated: 2026-06-01T10:00:31Z

## Decision

`PASS_A7FFCORE16GER_INTERACTION_FORENSIC_COMPLETE_READY_FOR_CORE16H`

CORE16GER freezes the CORE16GE result. Typed interactions produced nonzero candidate supply, but only two interaction families contributed candidates. This blocks CORE17 and all search, while authorizing a second-pass interaction breadth repair contract.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16h_contract": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16GER_INTERACTION_FORENSIC_COMPLETE_READY_FOR_CORE16H",
  "dominant_failure": "interaction_candidate_supply_narrow_but_nonzero",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T10:00:31Z",
  "interaction_family_count": 2,
  "interaction_probe_candidate_count": 84,
  "next_allowed": "A7FF-CORE16H second-pass interaction breadth repair contract",
  "source_decision": "HOLD_A7FFCORE16GE_INTERACTION_PROBE_SUPPLY_INSUFFICIENT",
  "source_stage": "A7FF-CORE16GE",
  "stage": "A7FF-CORE16GER",
  "top_interaction_family_share": 0.5952380952380952
}
```

## Source Family Summary

| interaction_family                         |   response_rows |   blueprint_count |   probe_candidate_count |   near_miss_count |   label_family_count |   median_control_ratio |
|:-------------------------------------------|----------------:|------------------:|------------------------:|------------------:|---------------------:|-----------------------:|
| I5_liquidity_state_x_basis_or_positioning  |            3072 |               192 |                      50 |                26 |                    4 |                8.57204 |
| I3_positioning_divergence_x_price_or_basis |            3024 |               189 |                      34 |                47 |                    4 |                8.4569  |
| I4_taker_flow_x_OI_or_liquidity            |            1792 |               112 |                       0 |                10 |                    4 |                6.63881 |
| I2_OI_delta_x_basis_premium_dislocation    |            1920 |               120 |                       0 |                 1 |                    4 |               10.0455  |
| I0_OI_delta_x_price_move                   |             768 |                48 |                       0 |                 0 |                    4 |                8.93879 |
| I1_OI_delta_x_funding_abs                  |             864 |                54 |                       0 |                 0 |                    4 |                3.88144 |
| I6_volatility_state_x_basis_or_OI          |            1536 |                96 |                       0 |                 0 |                    4 |               10.4265  |

## Candidate Breakdown

| interaction_family                         | operator   | label_family                       |   candidate_count |   lag_ok_count |   median_control_ratio |   median_recent_lag |
|:-------------------------------------------|:-----------|:-----------------------------------|------------------:|---------------:|-----------------------:|--------------------:|
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L5_vol_adjusted_return             |                12 |              6 |               0.721556 |         0.0231097   |
| I3_positioning_divergence_x_price_or_basis | Sub        | L5_vol_adjusted_return             |                11 |              9 |               0.788422 |         0.0507313   |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L3_liquidity_tier_relative_return  |                11 |              6 |               0.621477 |         0.000324865 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L1_cross_sectional_relative_return |                 8 |              7 |               0.696232 |         0.000491767 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L0_raw_forward_return              |                 8 |              7 |               0.696232 |         0.000491767 |
| I3_positioning_divergence_x_price_or_basis | Sub        | L0_raw_forward_return              |                 7 |              7 |               0.700692 |         0.000561458 |
| I3_positioning_divergence_x_price_or_basis | Sub        | L3_liquidity_tier_relative_return  |                 7 |              7 |               0.66492  |         0.000538784 |
| I3_positioning_divergence_x_price_or_basis | Sub        | L1_cross_sectional_relative_return |                 7 |              7 |               0.700692 |         0.000561458 |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L3_liquidity_tier_relative_return  |                 4 |              0 |               0.844868 |         0.0001318   |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L5_vol_adjusted_return             |                 3 |              1 |               0.856818 |         0.0202349   |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L1_cross_sectional_relative_return |                 2 |              0 |               0.809627 |         0.000181966 |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L0_raw_forward_return              |                 2 |              0 |               0.809627 |         0.000181966 |
| I3_positioning_divergence_x_price_or_basis | Mul        | L0_raw_forward_return              |                 1 |              1 |               0.984747 |         0.0016073   |
| I3_positioning_divergence_x_price_or_basis | Mul        | L1_cross_sectional_relative_return |                 1 |              1 |               0.984747 |         0.0016073   |

## Near-Miss Breakdown

| interaction_family                         | operator   | label_family                       |   near_miss_count |   median_control_ratio |
|:-------------------------------------------|:-----------|:-----------------------------------|------------------:|-----------------------:|
| I3_positioning_divergence_x_price_or_basis | Sub        | L0_raw_forward_return              |                11 |                1.17869 |
| I3_positioning_divergence_x_price_or_basis | Sub        | L1_cross_sectional_relative_return |                11 |                1.17869 |
| I3_positioning_divergence_x_price_or_basis | Sub        | L3_liquidity_tier_relative_return  |                11 |                1.1701  |
| I3_positioning_divergence_x_price_or_basis | Sub        | L5_vol_adjusted_return             |                10 |                1.16421 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L0_raw_forward_return              |                 6 |                1.13254 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L1_cross_sectional_relative_return |                 6 |                1.13254 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L5_vol_adjusted_return             |                 4 |                1.12091 |
| I5_liquidity_state_x_basis_or_positioning  | Mul        | L3_liquidity_tier_relative_return  |                 4 |                1.17978 |
| I4_taker_flow_x_OI_or_liquidity            | SafeDiv    | L5_vol_adjusted_return             |                 3 |                1.32661 |
| I4_taker_flow_x_OI_or_liquidity            | SafeDiv    | L1_cross_sectional_relative_return |                 2 |                1.28885 |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L5_vol_adjusted_return             |                 2 |                1.23793 |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L0_raw_forward_return              |                 2 |                1.00349 |
| I5_liquidity_state_x_basis_or_positioning  | SafeDiv    | L1_cross_sectional_relative_return |                 2 |                1.00349 |
| I4_taker_flow_x_OI_or_liquidity            | SafeDiv    | L0_raw_forward_return              |                 2 |                1.28885 |
| I3_positioning_divergence_x_price_or_basis | Mul        | L5_vol_adjusted_return             |                 1 |                1.29531 |
| I3_positioning_divergence_x_price_or_basis | Mul        | L3_liquidity_tier_relative_return  |                 1 |                1.09727 |
| I3_positioning_divergence_x_price_or_basis | Mul        | L1_cross_sectional_relative_return |                 1 |                1.41239 |
| I3_positioning_divergence_x_price_or_basis | Mul        | L0_raw_forward_return              |                 1 |                1.41239 |
| I2_OI_delta_x_basis_premium_dislocation    | Mul        | L3_liquidity_tier_relative_return  |                 1 |                1.3119  |
| I4_taker_flow_x_OI_or_liquidity            | Mul        | L1_cross_sectional_relative_return |                 1 |                1.01141 |
| I4_taker_flow_x_OI_or_liquidity            | Mul        | L0_raw_forward_return              |                 1 |                1.01141 |
| I4_taker_flow_x_OI_or_liquidity            | Mul        | L5_vol_adjusted_return             |                 1 |                1.02082 |

## Repair Actions

| action_id                        | target                          | action                                                                                      | reason                                                                                    |
|:---------------------------------|:--------------------------------|:--------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| R0_cap_successful_interactions   | I3/I5                           | cap selected share and require operator/label diversity before any objective seed policy    | CORE16GE found candidates, but only from two interaction families                         |
| R1_expand_near_miss_I4           | I4_taker_flow_x_OI_or_liquidity | repair near-miss rows with asymmetric transforms and tighter control-dominance diagnostics  | I4 produced near misses but no strict candidates; it is the best non-I3/I5 expansion lane |
| R2_block_dead_interactions       | I0/I1/I2/I6                     | keep as diagnostic-only unless a later primitive/field update changes response evidence     | these interaction families produced no strict supply in CORE16GE                          |
| R3_second_pass_interaction_probe | CORE16H                         | run a bounded second-pass probe with asymmetric transforms and family caps; no open grammar | nonzero supply exists, but breadth gates failed                                           |

## Next Contract

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
  "name": "second-pass interaction breadth repair contract",
  "scope": [
    "cap I3/I5 concentration",
    "expand I4 near-miss lane",
    "asymmetric left/right transforms",
    "operator/label diversity gates"
  ],
  "stage": "A7FF-CORE16H",
  "targets": {
    "min_candidate_count": 96,
    "min_interaction_family_count": 3,
    "min_non_L5_label_share": 0.4,
    "min_operator_count": 2,
    "top_interaction_family_share_max": 0.45
  }
}
```

## Blocked Actions

| item                                | reason                                                          |
|:------------------------------------|:----------------------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked: CORE16GE interaction breadth failed                    |
| formula generation                  | blocked: only second-pass typed interaction probe is authorized |
| bounded replay                      | blocked: no broad objective atlas                               |
| large search                        | blocked                                                         |
| alpha proof / shadow / paper / live | not authorized                                                  |
