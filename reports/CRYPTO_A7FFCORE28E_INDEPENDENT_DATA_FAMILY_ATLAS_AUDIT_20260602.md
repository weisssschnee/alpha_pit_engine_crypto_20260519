# CRYPTO A7FF-CORE28E INDEPENDENT DATA-FAMILY ATLAS AUDIT

Generated: 2026-06-01T18:30:26Z

## Decision

`PASS_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_READY_FOR_CORE29_CONTRACT`

CORE28E is an atlas/contract audit. It does not run formula generation, numeric replay, alpha search, large search, alpha proof, shadow, paper, or live.

## Summary

- family_count: `8`
- ready_for_core29_family_count: `3`
- independent_ready_family_count: `3`
- A7AI-F4 promoted ordinary-alpha family count: `1`

## Ready Families

| family_id                         | data_family                   | universe_scope                                      | pit_status                                                                  | independence_from_s0   | recommended_role                                          | notes                                                                                                  |
|:----------------------------------|:------------------------------|:----------------------------------------------------|:----------------------------------------------------------------------------|:-----------------------|:----------------------------------------------------------|:-------------------------------------------------------------------------------------------------------|
| F1a_aggtrades_flow_microstructure | aggTrades_flow_microstructure | core12/core3 richer microstructure, not full top498 | hourly_bucket_available_after_hour_end                                      | high                   | bounded_core12_candidate_and_state_interaction            | Use flow/large-trade/imbalance as independent state; block A7V activity/liquidity self-reproduction.   |
| F1b_taker_flow_market_panel       | taker_flow_market_panel       | top498 listing-aware                                | 1h panel feature; use after bar close                                       | high                   | ordinary_alpha_candidate_if_interaction_and_control_clean | Top498 coverage makes this the main independent flow candidate, but not standalone activity/liquidity. |
| F2a_basis_funding_independent     | basis_funding_dislocation     | top498 listing-aware                                | usable_existing_panel; funding/metrics use conservative availability policy | medium                 | bounded_independent_interaction_candidate                 | Must be non-S0-neutralized and interaction/state-conditioned; prior promoted seed is basis_delta only. |

## Blocked Or Diagnostic Families

| family_id                             | data_family                        | recommended_role                   | blocked_pattern_risk                | notes                                                                                                    |
|:--------------------------------------|:-----------------------------------|:-----------------------------------|:------------------------------------|:---------------------------------------------------------------------------------------------------------|
| F0_positioning_price_basis_s0         | positioning_price_basis_s0         | diagnostic_reference_only          | high                                | 4 S0 clean candidates are calibration/anti-overfit reference only; standalone rerun blocked.             |
| F2b_positioning_ratios_diagnostic     | positioning_ratios                 | risk_exposure_or_interaction_input | high_as_standalone_signal           | A7AI-F3/F4 treat most positioning as risk/control-like; require interaction-only contract before search. |
| F3_liquidity_volume_state             | liquidity_volume_state             | regime_state_or_interaction_input  | high_A7V_activity_liquidity_caution | Useful as state/neutralizer; standalone activity/liquidity alpha family remains blocked.                 |
| F4_cross_exchange_forward_context     | cross_exchange_basis_funding_depth | forward_context_diagnostic_only    | high_if_backfilled_as_history       | Can design telemetry; cannot enter historical alpha proof or backfilled replay.                          |
| F5_new_liquidation_orderbook_contract | liquidation_orderbook_depth        | new_data_contract_only             | high_without_PIT_contract           | High-value candidate family, but must not be used as historical proof without source/PIT contract.       |

## Independence Scorecard

| family_id                             |   independence_score | ready_for_core29   | core29_recommendation          |
|:--------------------------------------|---------------------:|:-------------------|:-------------------------------|
| F1b_taker_flow_market_panel           |                  7.5 | True               | candidate_for_bounded_contract |
| F1a_aggtrades_flow_microstructure     |                  6.5 | True               | candidate_for_bounded_contract |
| F2a_basis_funding_independent         |                  6.5 | True               | candidate_for_bounded_contract |
| F3_liquidity_volume_state             |                  7   | False              | blocked_or_diagnostic_only     |
| F2b_positioning_ratios_diagnostic     |                  6   | False              | blocked_or_diagnostic_only     |
| F0_positioning_price_basis_s0         |                  3   | False              | blocked_or_diagnostic_only     |
| F4_cross_exchange_forward_context     |                  1   | False              | blocked_or_diagnostic_only     |
| F5_new_liquidation_orderbook_contract |                  1   | False              | blocked_or_diagnostic_only     |

## Source Artifact Inventory

| artifact_id                   | path                                                                                                                                             | exists   | artifact_type   |
|:------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|:---------|:----------------|
| top498_replay_v2              | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                                                               | True     | directory       |
| core12_aggtrades_all_features | G:\AlphaFactory_CryptoData\gold\features\binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet                      | True     | file            |
| cross_exchange_30d_v2         | G:\AlphaFactory_CryptoData\gold\features\okx_binance_cross_exchange_unified_1h_30d_v2_20260527                                                   | True     | directory       |
| A7U0R_source_trace            | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7u0r_source_trace_audit\a7u0r_manifest.json                                     | True     | manifest        |
| A7S1_metrics_acceptance       | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7s1_metrics_acceptance_audit\a7s1_acceptance_manifest.json                      | True     | manifest        |
| A7AP1_cross_exchange          | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ap1_cross_exchange_field_smoke\a7ap1_manifest.json                             | True     | manifest        |
| A7AI-F3_fields                | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7aif3_materialization_evaluator_parity\a7aif3_field_materialization_matrix.csv  | True     | csv             |
| A7AI-F4_promoted_fields       | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7aif4_response_backed_field_promotion\a7aif4_promoted_ordinary_alpha_fields.csv | True     | csv             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE29 independent family bounded generation/probe contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_generation_execution": true,
    "large_search": true,
    "search": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "a7aif4_promoted_family_count": 1,
  "authorizes_alpha_proof": false,
  "authorizes_core29_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_family_ids": [
    "F0_positioning_price_basis_s0",
    "F2b_positioning_ratios_diagnostic",
    "F3_liquidity_volume_state",
    "F4_cross_exchange_forward_context",
    "F5_new_liquidation_orderbook_contract"
  ],
  "candidate_family_ids": [
    "F1a_aggtrades_flow_microstructure",
    "F1b_taker_flow_market_panel",
    "F2a_basis_funding_independent"
  ],
  "decision": "PASS_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_READY_FOR_CORE29_CONTRACT",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 8,
  "generated_at": "2026-06-01T18:30:26Z",
  "independent_ready_family_count": 3,
  "next_allowed": "A7FF-CORE29 independent family bounded generation/probe contract",
  "ready_for_core29_family_count": 3,
  "source_decision": "PASS_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_READY_FOR_CORE28E",
  "source_stage": "A7FF-CORE28",
  "stage": "A7FF-CORE28E"
}
```
