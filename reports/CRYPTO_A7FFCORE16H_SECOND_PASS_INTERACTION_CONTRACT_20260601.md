# CRYPTO A7FF-CORE16H SECOND-PASS INTERACTION CONTRACT

Generated: 2026-06-01T10:01:36Z

## Decision

`PASS_A7FFCORE16H_SECOND_PASS_INTERACTION_CONTRACT_READY_FOR_CORE16HE`

CORE16H defines the second-pass interaction breadth repair. It is still not formula generation, replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16he": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16H_SECOND_PASS_INTERACTION_CONTRACT_READY_FOR_CORE16HE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T10:01:36Z",
  "next_allowed": "A7FF-CORE16HE second-pass interaction breadth execution",
  "source_decision": "PASS_A7FFCORE16GER_INTERACTION_FORENSIC_COMPLETE_READY_FOR_CORE16H",
  "source_stage": "A7FF-CORE16GER",
  "stage": "A7FF-CORE16H"
}
```

## Second-Pass Families

| family                 | source_interaction                         | action                                                                                                                               | target                                                                |
|:-----------------------|:-------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|
| H0_I3_deconcentration  | I3_positioning_divergence_x_price_or_basis | cap Sub/L5 concentration; add asymmetric transforms positioning:spread_short_long\|zscore_168h with price/basis:delta_24h\|shock_24h | keep I3 useful while preventing single operator/label dominance       |
| H1_I5_deconcentration  | I5_liquidity_state_x_basis_or_positioning  | cap Mul/L5; add SafeDiv and Sub only where semantic scale permits; require non-L5 share                                              | convert liquidity-state interaction into diversified candidate supply |
| H2_I4_near_miss_repair | I4_taker_flow_x_OI_or_liquidity            | expand asymmetric transforms around near-miss rows; evaluate flow reversal under OI/liquidity context                                | turn best non-I3/I5 near-miss lane into strict candidates             |
| H3_cross_family_bridge | I3/I5/I4                                   | build low-count bridge probes that combine positioning/liquidity/taker context without basis dominance                               | raise interaction family count to at least 3 without open grammar     |

## Cap Policy

| policy_id           | value                            | reason                                      |
|:--------------------|:---------------------------------|:--------------------------------------------|
| i3_i5_top_share_cap | each <= 45%                      | CORE16GE top family share was 59.5%         |
| non_l5_label_floor  | >= 40%                           | avoid ranked/vol-only label concentration   |
| operator_floor      | >= 2 operators                   | avoid single Sub/Mul morphology             |
| i4_floor            | >= 12 strict or near-strict rows | force non-I3/I5 expansion lane to be tested |
| control_gate        | strict < 1.0; forensic 1.0-1.5   | do not promote control-like interactions    |

## Execution Contract

```json
{
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "families": [
    "H0_I3_deconcentration",
    "H1_I5_deconcentration",
    "H2_I4_near_miss_repair",
    "H3_cross_family_bridge"
  ],
  "forbidden": [
    "open grammar FormulaGen",
    "bounded replay",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "max_blueprints": 4096,
  "name": "second-pass interaction breadth execution",
  "pass_gate": {
    "candidate_count": 96,
    "i4_floor": 12,
    "interaction_family_count": 3,
    "non_l5_label_share_min": 0.4,
    "operator_count_min": 2,
    "top_family_share_max": 0.45
  },
  "stage": "A7FF-CORE16HE"
}
```

## Source Candidate Breakdown

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

## Blocked Actions

| item                                | reason                                                              |
|:------------------------------------|:--------------------------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked until CORE16HE breadth execution passes                     |
| formula generation                  | blocked: only second-pass typed interaction execution is authorized |
| bounded replay                      | blocked: no broad objective atlas                                   |
| large search                        | blocked                                                             |
| alpha proof / shadow / paper / live | not authorized                                                      |
