# CRYPTO A7FF-CORE16FER NON-BASIS ATLAS FORENSIC

Generated: 2026-06-01T09:22:55Z

## Decision

`PASS_A7FFCORE16FER_NON_BASIS_FORENSIC_COMPLETE_READY_FOR_CORE16G`

CORE16FER freezes the CORE16FE result. Non-basis strict supply is too thin for CORE17 or replay expansion, but the 46-row near-miss lane is enough to justify a family-native interaction repair contract. This is not formula generation or search authorization.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16g_contract": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE16FER_NON_BASIS_FORENSIC_COMPLETE_READY_FOR_CORE16G",
  "dominant_failure": "non_basis_single_field_supply_insufficient",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T09:22:55Z",
  "near_miss_non_basis_count": 46,
  "next_allowed": "A7FF-CORE16G family-native interaction repair contract",
  "source_decision": "HOLD_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_INSUFFICIENT",
  "source_stage": "A7FF-CORE16FE",
  "stage": "A7FF-CORE16FER",
  "strict_non_basis_candidate_count": 5,
  "strict_non_basis_field_family_count": 2
}
```

## Family Supply

| field_family   |   rows |   strict_candidate_count |   near_miss_count |   transform_count |   label_family_count |   median_control_ratio |
|:---------------|-------:|-------------------------:|------------------:|------------------:|---------------------:|-----------------------:|
| price_return   |    320 |                        4 |                37 |                10 |                    4 |               13.67    |
| positioning    |    480 |                        1 |                 2 |                10 |                    4 |               11.1439  |
| open_interest  |    480 |                        0 |                 6 |                10 |                    4 |               13.6725  |
| taker_flow     |    320 |                        0 |                 1 |                10 |                    4 |                5.02514 |
| liquidity      |    640 |                        0 |                 0 |                10 |                    4 |                9.97512 |
| volatility     |    320 |                        0 |                 0 |                10 |                    4 |               26.0082  |

## Near-Miss By Family / Transform / Label

| field_family   | transform         | label_family                       |   near_miss_count |   median_control_ratio |   median_positive_splits |
|:---------------|:------------------|:-----------------------------------|------------------:|-----------------------:|-------------------------:|
| price_return   | delta_1h          | L5_vol_adjusted_return             |                 3 |                1.12453 |                        3 |
| open_interest  | level             | L0_raw_forward_return              |                 2 |                1.16911 |                        3 |
| open_interest  | level             | L3_liquidity_tier_relative_return  |                 2 |                1.23897 |                        3 |
| open_interest  | level             | L1_cross_sectional_relative_return |                 2 |                1.16911 |                        3 |
| price_return   | tsrank_168h       | L1_cross_sectional_relative_return |                 2 |                1.33395 |                        3 |
| price_return   | delta_24h         | L3_liquidity_tier_relative_return  |                 2 |                1.32797 |                        3 |
| price_return   | level             | L5_vol_adjusted_return             |                 2 |                1.18707 |                        3 |
| price_return   | tsrank_168h       | L0_raw_forward_return              |                 2 |                1.33395 |                        3 |
| price_return   | tsrank_168h       | L3_liquidity_tier_relative_return  |                 2 |                1.18761 |                        3 |
| positioning    | spread_short_long | L0_raw_forward_return              |                 1 |                1.28778 |                        3 |
| price_return   | delta_1h          | L3_liquidity_tier_relative_return  |                 1 |                1.1667  |                        3 |
| positioning    | spread_short_long | L1_cross_sectional_relative_return |                 1 |                1.28778 |                        3 |
| price_return   | delta_24h         | L1_cross_sectional_relative_return |                 1 |                1.43724 |                        3 |
| price_return   | delta_24h         | L5_vol_adjusted_return             |                 1 |                1.3964  |                        3 |
| price_return   | level             | L1_cross_sectional_relative_return |                 1 |                1.34143 |                        3 |
| price_return   | level             | L0_raw_forward_return              |                 1 |                1.34143 |                        3 |
| price_return   | level             | L3_liquidity_tier_relative_return  |                 1 |                1.14918 |                        3 |
| price_return   | delta_1h          | L1_cross_sectional_relative_return |                 1 |                1.09957 |                        3 |
| price_return   | delta_24h         | L0_raw_forward_return              |                 1 |                1.43724 |                        3 |
| price_return   | delta_1h          | L0_raw_forward_return              |                 1 |                1.09957 |                        3 |
| price_return   | shock_24h         | L3_liquidity_tier_relative_return  |                 1 |                1.4568  |                        3 |
| price_return   | shock_24h         | L1_cross_sectional_relative_return |                 1 |                1.41491 |                        3 |
| price_return   | shock_24h         | L0_raw_forward_return              |                 1 |                1.41491 |                        3 |
| price_return   | shock_24h         | L5_vol_adjusted_return             |                 1 |                1.05022 |                        3 |
| price_return   | tsrank_168h       | L5_vol_adjusted_return             |                 1 |                1.3529  |                        3 |
| price_return   | tsrank_72h        | L0_raw_forward_return              |                 1 |                1.36467 |                        3 |
| price_return   | tsrank_72h        | L1_cross_sectional_relative_return |                 1 |                1.36467 |                        3 |
| price_return   | tsrank_72h        | L3_liquidity_tier_relative_return  |                 1 |                1.0818  |                        3 |
| price_return   | tsrank_72h        | L5_vol_adjusted_return             |                 1 |                1.39299 |                        3 |
| price_return   | zscore_168h       | L0_raw_forward_return              |                 1 |                1.39641 |                        3 |
| price_return   | zscore_168h       | L1_cross_sectional_relative_return |                 1 |                1.39641 |                        3 |
| price_return   | zscore_168h       | L3_liquidity_tier_relative_return  |                 1 |                1.14435 |                        3 |
| price_return   | zscore_72h        | L0_raw_forward_return              |                 1 |                1.13499 |                        3 |
| price_return   | zscore_72h        | L1_cross_sectional_relative_return |                 1 |                1.13499 |                        3 |
| price_return   | zscore_72h        | L5_vol_adjusted_return             |                 1 |                1.12545 |                        3 |
| taker_flow     | level             | L3_liquidity_tier_relative_return  |                 1 |                1.25061 |                        3 |

## Family Repair Actions

| family        | status                 | next_action                                                                                 | hard_limit                                                              |
|:--------------|:-----------------------|:--------------------------------------------------------------------------------------------|:------------------------------------------------------------------------|
| open_interest | near_miss_repairable   | convert OI level/delta near-miss rows into OI x price/funding/basis interaction probes      | no standalone OI alpha promotion without control_ratio < 1.0            |
| positioning   | thin_strict_supply     | use account-vs-position divergence and top-vs-global divergence as typed interaction probes | positioning cannot be a risk-defense wrapper selected as ordinary alpha |
| taker_flow    | zero_strict_supply     | only test taker x OI and taker x liquidity reversal probes; no standalone flow search       | requires non-L7 response and control-clean evidence                     |
| liquidity     | zero_strict_supply     | treat as state/neutralizer unless interaction probe beats controls                          | no liquidity-volatility old-family revival                              |
| volatility    | zero_strict_supply     | use volatility as conditioning state for basis/OI/positioning only                          | no pure volatility beta signal                                          |
| price_return  | thin_but_control_risky | use only as interaction leg and baseline control                                            | no direct price-return objective expansion                              |

## Next Contract

```json
{
  "allowed_interaction_families": [
    "OI_delta_x_price_move",
    "OI_delta_x_funding_abs",
    "OI_delta_x_basis_premium_dislocation",
    "positioning_divergence_x_price_or_basis",
    "taker_flow_x_OI_or_liquidity",
    "liquidity_state_x_basis_or_positioning",
    "volatility_state_x_basis_or_OI"
  ],
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
  "inputs": [
    "CORE16FE strict non-basis atlas candidates",
    "CORE16FE near-miss forensic lane",
    "CORE16F family policy",
    "field role ledger"
  ],
  "name": "family-native interaction repair contract",
  "pass_gate": {
    "control_ratio_required": "< 1.0 for promotion, 1.0-1.5 forensic only",
    "interaction_probe_candidates": 64,
    "non_basis_family_count": 4,
    "top_family_share_max": 0.4
  },
  "stage": "A7FF-CORE16G"
}
```

## Blocked Actions

| item                                | reason                                               |
|:------------------------------------|:-----------------------------------------------------|
| A7FF-CORE17 objective seed policy   | blocked until CORE16G/next interaction repair passes |
| formula generation                  | blocked: non-basis single-field supply insufficient  |
| bounded replay                      | blocked: no broad objective atlas                    |
| large search                        | blocked                                              |
| alpha proof / shadow / paper / live | not authorized                                       |
