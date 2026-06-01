# CRYPTO A7FF-CORE17E OBJECTIVE SEED PACKET CONSTRUCTION

Generated: 2026-06-01T14:39:17Z

## Decision

`PASS_A7FFCORE17E_OBJECTIVE_SEED_PACKET_READY_FOR_CORE18_CONTRACT`

CORE17E builds and audits the objective seed packet for preflight contract drafting only. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core18_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE17E_OBJECTIVE_SEED_PACKET_READY_FOR_CORE18_CONTRACT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:39:17Z",
  "label_family_count": 4,
  "next_allowed": "A7FF-CORE18 bounded replay preflight contract",
  "non_l5_share": 0.8958333333333334,
  "operator_count": 3,
  "packet_size": 96,
  "seed_lane_count": 4,
  "source_decision": "PASS_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_READY_FOR_CORE17E",
  "source_stage": "A7FF-CORE17",
  "stage": "A7FF-CORE17E",
  "top_seed_lane_share": 0.34375
}
```

## Gate Audit

| gate                |     value | threshold   | pass   |
|:--------------------|----------:|:------------|:-------|
| packet_size         | 96        | >=96        | True   |
| seed_lane_count     |  4        | >=4         | True   |
| top_seed_lane_share |  0.34375  | <=0.35      | True   |
| duplicate_keys      |  0        | 0           | True   |
| non_l5_share        |  0.895833 | >=0.40      | True   |
| operator_count      |  3        | >=3         | True   |
| label_family_count  |  4        | >=3         | True   |

## Seed Lane Summary

| seed_lane                      | second_pass_family     |   rows |   label_family_count |   horizon_count |   operator_count |   left_field_count |   right_field_count |   lag_ok_count |   median_control_ratio |
|:-------------------------------|:-----------------------|-------:|---------------------:|----------------:|-----------------:|-------------------:|--------------------:|---------------:|-----------------------:|
| S1_liquidity_basis_positioning | H1_I5_deconcentration  |     33 |                    3 |               2 |                2 |                  4 |                   2 |             33 |               0.71876  |
| S0_positioning_price_basis     | H0_I3_deconcentration  |     31 |                    3 |               1 |                2 |                  3 |                   4 |             31 |               0.555319 |
| S3_cross_family_bridge         | H3_cross_family_bridge |     20 |                    4 |               4 |                2 |                  6 |                   3 |             15 |               0.830484 |
| S2_taker_flow_liquidity_oi     | H2_I4_near_miss_repair |     12 |                    4 |               3 |                2 |                  2 |                   6 |              5 |               0.741474 |

## Label/Horizon Summary

| label_family                       |   label_horizon_h |   rows |   seed_lane_count |
|:-----------------------------------|------------------:|-------:|------------------:|
| L0_raw_forward_return              |                 1 |     26 |                 4 |
| L1_cross_sectional_relative_return |                 1 |     26 |                 4 |
| L3_liquidity_tier_relative_return  |                 1 |     19 |                 4 |
| L5_vol_adjusted_return             |                 1 |      7 |                 2 |
| L0_raw_forward_return              |                 4 |      3 |                 3 |
| L1_cross_sectional_relative_return |                 4 |      3 |                 3 |
| L3_liquidity_tier_relative_return  |                24 |      2 |                 2 |
| L5_vol_adjusted_return             |                 4 |      2 |                 1 |
| L3_liquidity_tier_relative_return  |                 4 |      2 |                 2 |
| L0_raw_forward_return              |                 8 |      1 |                 1 |
| L0_raw_forward_return              |                24 |      1 |                 1 |
| L1_cross_sectional_relative_return |                 8 |      1 |                 1 |
| L1_cross_sectional_relative_return |                24 |      1 |                 1 |
| L3_liquidity_tier_relative_return  |                 8 |      1 |                 1 |
| L5_vol_adjusted_return             |                24 |      1 |                 1 |
