# CRYPTO A7AL-2G Matched-Control Gate

Generated: 2026-05-27T09:42:16Z

## Decision

```text
PASS_A7AL2G_MATCHED_CONTROL_GATE_PREFLIGHT_EXECUTION_HOLD
```

This is a pre-replay gate preflight. It does not execute formula search, formula replay, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7al2_execution": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers_to_execution": [
    "selected_pool_contains_not_authorized_field_families",
    "matched_control_gate_not_yet_connected_to_replay_runner"
  ],
  "decision": "PASS_A7AL2G_MATCHED_CONTROL_GATE_PREFLIGHT_EXECUTION_HOLD",
  "executes_formula_generation": false,
  "executes_formula_search": false,
  "executes_replay": false,
  "generated_at": "2026-05-27T09:42:16Z",
  "input_a7al2_decision": "PASS_A7AL2_CONTROL_DOMINANCE_CONTRACT_DRAFTED_EXECUTION_HOLD",
  "input_a7as0_decision": "PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G",
  "next_required_step": "A7AL-2H selector repair: filter/reweight candidate pool to allowed mutation/regime roles before replay",
  "policy_counts": {
    "mutation_source_only_control_required": 11,
    "not_authorized_by_a7al1b_baseline": 17,
    "regime_state_or_neutralizer_only": 4
  },
  "required_controls": [
    "one_bar_lag_stress",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random"
  ],
  "selected_candidates_audited": 32
}
```

## Policy Counts

| policy                                |   count |
|:--------------------------------------|--------:|
| not_authorized_by_a7al1b_baseline     |      17 |
| mutation_source_only_control_required |      11 |
| regime_state_or_neutralizer_only      |       4 |

## Candidate Gate Matrix

| candidate_id                | family                       | field_families        | a7al2g_policy                         | direct_rank_allowed   | policy_reason                                                             |
|:----------------------------|:-----------------------------|:----------------------|:--------------------------------------|:----------------------|:--------------------------------------------------------------------------|
| crypto_fg2_e3eeee6c6c128159 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_6f44fa67b5a9ca06 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_3cbd1218eef4d5c7 | oi_price_interaction         | open_interest|price   | regime_state_or_neutralizer_only      | False                 | OI level is stale-control sensitive; no direct alpha rank                 |
| crypto_fg2_ab5daaf2d4bb1b38 | oi_price_interaction         | open_interest|price   | regime_state_or_neutralizer_only      | False                 | OI level is stale-control sensitive; no direct alpha rank                 |
| crypto_fg2_115383654a40dc95 | liquidity_volatility_guarded | liquidity|volatility  | mutation_source_only_control_required | False                 | liquidity/volatility structure needs future and stale wrong-lag dominance |
| crypto_fg2_bc4bfd6a20077e8c | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_2b9c738ec11bacea | oi_price_interaction         | open_interest|price   | regime_state_or_neutralizer_only      | False                 | OI level is stale-control sensitive; no direct alpha rank                 |
| crypto_fg2_18f056370a194b1f | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_19a3f95b8076131b | oi_price_interaction         | open_interest|price   | regime_state_or_neutralizer_only      | False                 | OI level is stale-control sensitive; no direct alpha rank                 |
| crypto_fg2_949d47bb2314fba0 | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_f3ffa3b8cccb6ae4 | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_ed198b8d6c57d771 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_1ed3dccb9ce838ca | taker_flow_state             | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_63b89c2c6cfee9d5 | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_90d8a2600b1cf58f | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_413accdbe82945d8 | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_80f9ad40dcfdd668 | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_5867678edef93f9e | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_1beccf4ae2ec1b40 | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_b4ade21adee157d4 | price_volatility_structure   | price|volatility      | mutation_source_only_control_required | False                 | price/volatility structure needs future and stale wrong-lag dominance     |
| crypto_fg2_3522cd90888d43d7 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_59eb7be56beb98b0 | taker_flow_state             | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_aa3661f8eb8b5435 | basis_funding_crowding       | basis|funding         | not_authorized_by_a7al1b_baseline     | False                 | basis/funding families did not pass A7AL-1 controls                       |
| crypto_fg2_c649a241fed6a55f | liquidity_volatility_guarded | liquidity|volatility  | mutation_source_only_control_required | False                 | liquidity/volatility structure needs future and stale wrong-lag dominance |
| crypto_fg2_4e9ba42b824279e6 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_fdcc4a2b92b3cf1d | taker_flow_state             | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_20696f318b21a836 | positioning_reversal         | positioning|price     | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_d0881b66a8dbe938 | taker_flow_state             | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_19dc36e900ebde39 | taker_flow_state             | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline     | False                 | positioning/taker families did not pass A7AL-1 controls                   |
| crypto_fg2_7035940e742f28d3 | liquidity_volatility_guarded | liquidity|volatility  | mutation_source_only_control_required | False                 | liquidity/volatility structure needs future and stale wrong-lag dominance |
| crypto_fg2_71afa051e89efe97 | liquidity_volatility_guarded | liquidity|volatility  | mutation_source_only_control_required | False                 | liquidity/volatility structure needs future and stale wrong-lag dominance |
| crypto_fg2_6dabc7639d6211d3 | liquidity_volatility_guarded | liquidity|volatility  | mutation_source_only_control_required | False                 | liquidity/volatility structure needs future and stale wrong-lag dominance |

## Control Specs

| control              | construction                                                               | promotion_rule                                                               |
|:---------------------|:---------------------------------------------------------------------------|:-----------------------------------------------------------------------------|
| one_bar_lag_stress   | evaluate same expression with field-native one bar delayed features        | must be materially weaker than original and cannot be return-corr equivalent |
| wrong_lag_future_24h | shift every source feature family by -24h before expression evaluation     | must be materially weaker than original and cannot be return-corr equivalent |
| wrong_lag_stale_168h | shift every source feature family by +168h before expression evaluation    | must be materially weaker than original and cannot be return-corr equivalent |
| time_shuffle         | permute timestamp blocks within split; preserve symbol membership          | must be materially weaker than original and cannot be return-corr equivalent |
| symbol_shuffle       | permute symbols within timestamp and split                                 | must be materially weaker than original and cannot be return-corr equivalent |
| same_family_random   | random expression from same field family / operator motif / horizon bucket | must be materially weaker than original and cannot be return-corr equivalent |

## Boundary

```text
AUTHORIZED:
  A7AL-2H selector repair / candidate pool reweighting only.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
