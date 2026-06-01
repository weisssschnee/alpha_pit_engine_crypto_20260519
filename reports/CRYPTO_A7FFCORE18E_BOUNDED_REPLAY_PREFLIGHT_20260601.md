# CRYPTO A7FF-CORE18E BOUNDED REPLAY PREFLIGHT

Generated: 2026-06-01T14:43:02Z

## Decision

`PASS_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_READY_FOR_CORE19_CONTRACT`

CORE18E verifies bounded replay preflight readiness for the locked packet. It does not execute bounded replay, formula generation, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_bounded_replay_execution": false,
  "authorizes_core19_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_READY_FOR_CORE19_CONTRACT",
  "duplicate_keys": 0,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T14:43:02Z",
  "missing_field_count": 0,
  "next_allowed": "A7FF-CORE19 bounded replay contract",
  "non_l5_share": 0.8958333333333334,
  "packet_size": 96,
  "seed_lane_count": 4,
  "source_decision": "PASS_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE18E",
  "source_stage": "A7FF-CORE18",
  "stage": "A7FF-CORE18E",
  "top_lane_share": 0.34375,
  "unsupported_operator_count": 0
}
```

## Gate Audit

| gate                  |     value | threshold   | pass   |
|:----------------------|----------:|:------------|:-------|
| packet_size           | 96        | 96          | True   |
| missing_fields        |  0        | 0           | True   |
| unsupported_operators |  0        | 0           | True   |
| duplicate_keys        |  0        | 0           | True   |
| direct_replay_flags   |  0        | 0           | True   |
| search_flags          |  0        | 0           | True   |
| alpha_flags           |  0        | 0           | True   |
| top_lane_share        |  0.34375  | <=0.35      | True   |
| non_l5_share          |  0.895833 | >=0.40      | True   |

## Lane Summary

| seed_lane                      |   rows |   label_family_count |   horizon_count |   operator_count |   left_field_count |   right_field_count |   median_control_ratio |
|:-------------------------------|-------:|---------------------:|----------------:|-----------------:|-------------------:|--------------------:|-----------------------:|
| S1_liquidity_basis_positioning |     33 |                    3 |               2 |                2 |                  4 |                   2 |               0.71876  |
| S0_positioning_price_basis     |     31 |                    3 |               1 |                2 |                  3 |                   4 |               0.555319 |
| S3_cross_family_bridge         |     20 |                    4 |               4 |                2 |                  6 |                   3 |               0.830484 |
| S2_taker_flow_liquidity_oi     |     12 |                    4 |               3 |                2 |                  2 |                   6 |               0.741474 |
