# CRYPTO A7FF-CORE16R PRIMITIVE ATLAS SUPPLY REPAIR

Generated: 2026-06-01T08:17:59Z

## Decision

`PASS_A7FFCORE16R_PRIMITIVE_ATLAS_SUPPLY_REPAIR_READY_FOR_CORE16E`

A7FF-CORE16R defines a supply repair for the primitive replay-stability atlas. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16e": true,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16R_PRIMITIVE_ATLAS_SUPPLY_REPAIR_READY_FOR_CORE16E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T08:17:59Z",
  "next_allowed": "A7FF-CORE16E expanded primitive/operator-probe atlas execution",
  "source_decision": "HOLD_A7FFCORE16_PRIMITIVE_ATLAS_INSUFFICIENT",
  "source_stage": "A7FF-CORE16",
  "stage": "A7FF-CORE16R"
}
```

## Repair Actions

| action_id                        | requirement                                                                                                | minimum                                                                                 |
|:---------------------------------|:-----------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------|
| R0_expand_non_l7_primitive_probe | rerun/extend primitive response map with more transforms and less L7 absorption                            | >=64 non-L7 atlas candidates, >=6 field families, >=5 transforms                        |
| R1_operator_probing              | score field_family x operator x label x horizon before factor generation                                   | operator families must pass control_ratio < 1.0 and split consistency before generation |
| R2_field_family_quota            | explicitly quota open_interest, positioning, taker_flow, liquidity, volatility, basis/funding              | no single family >30 percent in atlas                                                   |
| R3_lag_fragility_repair          | separate lag-fragile from control-clean; do not discard all lag-fragile fields without slow-horizon retest | slow-horizon retest contract for 4h/8h/24h primitive transforms                         |
| R4_no_search_until_supply_pass   | formula search remains blocked until primitive atlas supply passes                                         | CORE16R/CORE16E pass before any new generation/replay                                   |

## Next Contract

```json
{
  "action": "expanded primitive/operator-probe atlas execution",
  "forbidden": [
    "formula search",
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
  "inputs": [
    "top498 feature panel",
    "A7AA label contract",
    "field role ledger",
    "CORE16 insufficient atlas"
  ],
  "labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "pass_gate": {
    "atlas_candidate_count": 64,
    "field_family_count": 6,
    "top_family_share_max": 0.3,
    "transform_count": 5
  },
  "stage": "A7FF-CORE16E",
  "transforms": [
    "level",
    "delta_1h",
    "delta_4h",
    "delta_24h",
    "zscore_72h",
    "zscore_168h",
    "tsrank_72h",
    "tsrank_168h",
    "shock_24h",
    "spread_short_long"
  ]
}
```

## Blocked Actions

| item                                | reason                                                     |
|:------------------------------------|:-----------------------------------------------------------|
| CORE17 objective seed policy        | blocked: CORE16 atlas supply insufficient                  |
| formula generation                  | blocked until expanded primitive atlas passes              |
| bounded replay                      | blocked until supply repair yields broader objective atlas |
| large search                        | blocked                                                    |
| alpha proof / shadow / paper / live | not authorized                                             |
