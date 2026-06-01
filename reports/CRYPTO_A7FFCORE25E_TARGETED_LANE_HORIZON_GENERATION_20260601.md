# CRYPTO A7FF-CORE25E TARGETED LANE/HORIZON GENERATION

Generated: 2026-06-01T15:46:24Z

## Decision

`PASS_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_PACKET_READY_FOR_CORE26_CONTRACT`

CORE25E generates a bounded targeted blueprint/preflight packet for missing executable lanes. It does not execute numeric replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_open_formula_generation": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_PACKET_READY_FOR_CORE26_CONTRACT",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:46:24Z",
  "generated_blueprint_count": 4800,
  "next_allowed": "A7FF-CORE26 targeted numeric probe contract",
  "preflight_horizon_count": 3,
  "preflight_label_family_count": 4,
  "preflight_lane_count": 4,
  "preflight_packet_count": 960,
  "source_decision": "PASS_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_READY_FOR_CORE25E",
  "source_stage": "A7FF-CORE25",
  "stage": "A7FF-CORE25E"
}
```

## Lane Distribution

| seed_lane                      |   generated_count |   label_family_count |   horizon_count |
|:-------------------------------|------------------:|---------------------:|----------------:|
| S0_positioning_price_basis     |              1800 |                    3 |               3 |
| S1_liquidity_basis_positioning |              1800 |                    3 |               3 |
| S2_taker_flow_liquidity_oi     |               600 |                    4 |               1 |
| S3_cross_family_bridge         |               600 |                    4 |               2 |

## Preflight Distribution

| seed_lane                      |   preflight_count |   label_family_count |   horizon_count |
|:-------------------------------|------------------:|---------------------:|----------------:|
| S0_positioning_price_basis     |               360 |                    3 |               3 |
| S1_liquidity_basis_positioning |               360 |                    3 |               3 |
| S2_taker_flow_liquidity_oi     |               120 |                    4 |               1 |
| S3_cross_family_bridge         |               120 |                    4 |               2 |

## Top Field Usage

| field                              |   usage_count |
|:-----------------------------------|--------------:|
| top_long_short_position_ratio_last |          2742 |
| median_quote_volume_168h           |          1940 |
| mark_trade_basis_bps               |           862 |
| mark_index_basis_bps               |           822 |
| premium_close_bps                  |           702 |
| taker_buy_sell_volume_ratio_last   |           600 |
| top_long_short_account_ratio_last  |           324 |
| open_interest_value_last           |           320 |
| trade_return_24h                   |           288 |
| index_close                        |           270 |
| mark_close                         |           270 |
| basis_abs_168h                     |           160 |
| open_interest_last                 |           160 |
| open_interest_change_24h           |           140 |
