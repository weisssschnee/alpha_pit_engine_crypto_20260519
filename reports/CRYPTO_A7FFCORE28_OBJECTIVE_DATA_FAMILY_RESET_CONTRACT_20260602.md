# CRYPTO A7FF-CORE28 OBJECTIVE/DATA-FAMILY RESET CONTRACT

Generated: 2026-06-01T18:21:28Z

## Decision

`PASS_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_READY_FOR_CORE28E`

CORE28 resets the next search-prep path after CORE27X concluded that current evidence is single-lane S0 only. It does not authorize search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core28e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_READY_FOR_CORE28E",
  "dominant_failure": "single_lane_s0_clue_without_independent_executable_lane",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:21:28Z",
  "next_allowed": "A7FF-CORE28E independent data-family atlas contract/audit",
  "source_decision": "HOLD_A7FFCORE27X_SEARCH_NOT_READY_SINGLE_LANE_SUPPLY",
  "source_stage": "A7FF-CORE27X",
  "stage": "A7FF-CORE28"
}
```

## Reset Policy

| family                             | status                    | allowed                                                                             | blocked                                                         |
|:-----------------------------------|:--------------------------|:------------------------------------------------------------------------------------|:----------------------------------------------------------------|
| F0_positioning_price_basis_s0      | diagnostic_reference_only | use 4 clean S0 candidates as calibration and anti-overfit control                   | standalone search objective, replay contract, large search seed |
| F1_independent_flow_microstructure | primary_reset_candidate   | taker flow, aggTrades flow, liquidity/volume state, low-turnover interactions       | A7V activity/liquidity self-reproduction patterns               |
| F2_independent_basis_funding       | primary_reset_candidate   | basis/funding dislocation with non-S0 neutralization and H8/H24 executable horizons | basis-only or funding-only wrappers                             |
| F3_cross_exchange_forward_context  | diagnostic_forward_only   | forward telemetry / state context only                                              | historical alpha proof or backfilled proof                      |
| F4_new_data_family_contract        | contract_required         | liquidation/orderbook/cross-exchange only after PIT/source contract                 | untraced historical proof                                       |

## Gates

| gate                         | threshold                              |
|:-----------------------------|:---------------------------------------|
| independent_lane_requirement | >= 2 non-S0 lanes before replay/search |
| s0_concentration_cap         | S0 diagnostic reference only           |
| forward_only_source_policy   | cannot enter historical proof          |
| large_search_authorization   | false                                  |

## Execution Plan

| stage             | action                                       | input                                               | authorized   |
|:------------------|:---------------------------------------------|:----------------------------------------------------|:-------------|
| A7FF-CORE28E      | independent data-family atlas contract/audit | CORE27X arbitration + current field/source registry | True         |
| A7FF large search | blocked                                      | requires independent multi-lane executable evidence | False        |
