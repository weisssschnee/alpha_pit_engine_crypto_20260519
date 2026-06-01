# CRYPTO A7FF-CORE16F NON-BASIS SUPPLY REPAIR CONTRACT

Generated: 2026-06-01T09:19:48Z

## Decision

`PASS_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_READY_FOR_CORE16FE`

CORE16F is a contract stage. It defines how to repair non-basis primitive/operator supply after CORE16E showed a 96.6% basis/premium concentration. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16fe": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_READY_FOR_CORE16FE",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T09:19:48Z",
  "next_allowed": "A7FF-CORE16FE non-basis expanded primitive/operator atlas execution",
  "source_decision": "PASS_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_COMPLETE_READY_FOR_CORE16F",
  "source_stage": "A7FF-CORE16ER",
  "stage": "A7FF-CORE16F"
}
```

## Target Family Policy

| field_family   |   repair_priority | allowed_transforms                                                              | family_native_labels                                                                        | probe_policy                                                                |   minimum_non_basis_candidates |
|:---------------|------------------:|:--------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------|-------------------------------:|
| open_interest  |                 1 | delta_1h;delta_4h;delta_24h;zscore_72h;zscore_168h;tsrank_72h;spread_short_long | L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return | single-field plus OI-price/OI-funding interaction probe, no open grammar    |                              8 |
| positioning    |                 2 | level;delta_4h;delta_24h;zscore_168h;spread_short_long                          | L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return | divergence and crowding probes only                                         |                              8 |
| taker_flow     |                 3 | delta_1h;delta_4h;zscore_72h;shock_24h;tsrank_72h                               | L0_raw_forward_return;L1_cross_sectional_relative_return;L5_vol_adjusted_return             | flow imbalance and reversal probes; require controls weaker than original   |                              6 |
| liquidity      |                 4 | delta_4h;delta_24h;zscore_168h;tsrank_168h;shock_24h                            | L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return | state/neutralizer first; standalone signal only if non-L7 and control-clean |                              4 |
| volatility     |                 5 | delta_4h;delta_24h;zscore_72h;zscore_168h;spread_short_long                     | L3_liquidity_tier_relative_return;L5_vol_adjusted_return                                    | risk-state and reversal pressure probes; no pure volatility beta wrapper    |                              4 |
| price_return   |                 6 | delta_1h;delta_4h;zscore_72h;tsrank_72h;shock_24h                               | L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return | use only as interaction/control baseline; cap standalone exposure           |                              2 |

## Cap / Floor Policy

| policy_id          | field_family    |   max_share_in_core16fe_queue | reason                                                                                 |   min_candidate_count |   min_field_family_count | gate                                                                                    |
|:-------------------|:----------------|------------------------------:|:---------------------------------------------------------------------------------------|----------------------:|-------------------------:|:----------------------------------------------------------------------------------------|
| basis_premium_cap  | basis_premium   |                          0.35 | CORE16E basis_premium share was 96.6 percent                                           |                   nan |                      nan | nan                                                                                     |
| non_basis_floor    | non_basis_total |                        nan    | CORE17 requires breadth before objective seed policy                                   |                    32 |                        4 | nan                                                                                     |
| family_native_gate | all             |                        nan    | avoid over-conservative latency filtering while still rejecting control-like responses |                   nan |                      nan | premay_all_positive and control_ratio < 1.0; lag_ok is diagnostic flag, not hard reject |
| near_miss_lane     | non_basis       |                        nan    | surface repair evidence without promoting control-like rows                            |                   nan |                      nan | control_ratio between 1.0 and 1.5 may enter forensic-only lane                          |

## Execution Contract

```json
{
  "authorized": true,
  "basis_premium_max_share": 0.35,
  "executes_replay": false,
  "executes_search": false,
  "families": [
    "open_interest",
    "positioning",
    "taker_flow",
    "liquidity",
    "volatility",
    "price_return"
  ],
  "forbidden": [
    "formula generation",
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
  "name": "non-basis expanded primitive/operator atlas execution",
  "non_basis_min_candidate_count": 32,
  "non_basis_min_field_family_count": 4,
  "stage": "A7FF-CORE16FE",
  "top_family_share_max": 0.5
}
```

## Source Family Concentration

| field_family   |   atlas_candidate_count |      share |   transform_count |   label_family_count |   lag_ok_candidate_count |   median_control_ratio | status                    |
|:---------------|------------------------:|-----------:|------------------:|---------------------:|-------------------------:|-----------------------:|:--------------------------|
| basis_premium  |                     144 | 0.966443   |                 9 |                    4 |                       67 |               0.657844 | dominant_saturated_family |
| price_return   |                       4 | 0.0268456  |                 2 |                    3 |                        1 |               0.589453 | thin_positive_supply      |
| positioning    |                       1 | 0.00671141 |                 1 |                    1 |                        1 |               0.983348 | thin_positive_supply      |

## Blocked Actions

| item                                | reason                                                        |
|:------------------------------------|:--------------------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked until CORE16FE non-basis supply passes                |
| formula generation                  | blocked until primitive/operator supply has non-basis breadth |
| bounded replay                      | blocked until objective atlas breadth exists                  |
| large search                        | blocked                                                       |
| alpha proof / shadow / paper / live | not authorized                                                |
