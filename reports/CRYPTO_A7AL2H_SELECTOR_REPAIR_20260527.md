# CRYPTO A7AL-2H Selector Repair

Generated: 2026-05-27T09:44:30Z

## Decision

```text
PASS_A7AL2H_SELECTOR_REPAIRED_READY_FOR_REPLAY_PREFLIGHT
```

This stage repairs the pre-replay selector. It does not run replay or formula search.

## Manifest

```json
{
  "authorizes_a7al2_formula_search_execution": false,
  "authorizes_a7al2_replay_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AL2H_SELECTOR_REPAIRED_READY_FOR_REPLAY_PREFLIGHT",
  "executes_formula_generation": false,
  "executes_formula_search": false,
  "executes_replay": false,
  "generated_at": "2026-05-27T09:44:30Z",
  "input_a7al2g_decision": "PASS_A7AL2G_MATCHED_CONTROL_GATE_PREFLIGHT_EXECUTION_HOLD",
  "input_candidates": 32,
  "next_required_step": "A7AL-2I replay preflight: evaluate selected control-gated candidates and matched controls on base v2 with one-bar-lag stress",
  "rejected_not_authorized_candidates": 17,
  "selected_control_gated_candidates": 15,
  "selected_skeleton_count": 15,
  "top_skeleton_share": 0.06666666666666667
}
```

## Selected Policy Counts

| policy                                |   selected_count |
|:--------------------------------------|-----------------:|
| mutation_source_only_control_required |               11 |
| regime_state_or_neutralizer_only      |                4 |

## Selected Family Counts

| field_families       |   selected_count |
|:---------------------|-----------------:|
| price|volatility     |                6 |
| liquidity|volatility |                5 |
| open_interest|price  |                4 |

## Selected Control-Gated Candidates

| candidate_id                | family                       | field_families       | a7al2g_policy                         | required_controls                                                                                           |
|:----------------------------|:-----------------------------|:---------------------|:--------------------------------------|:------------------------------------------------------------------------------------------------------------|
| crypto_fg2_3cbd1218eef4d5c7 | oi_price_interaction         | open_interest|price  | regime_state_or_neutralizer_only      | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_ab5daaf2d4bb1b38 | oi_price_interaction         | open_interest|price  | regime_state_or_neutralizer_only      | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_115383654a40dc95 | liquidity_volatility_guarded | liquidity|volatility | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_2b9c738ec11bacea | oi_price_interaction         | open_interest|price  | regime_state_or_neutralizer_only      | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_18f056370a194b1f | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_19a3f95b8076131b | oi_price_interaction         | open_interest|price  | regime_state_or_neutralizer_only      | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_949d47bb2314fba0 | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_f3ffa3b8cccb6ae4 | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_63b89c2c6cfee9d5 | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_80f9ad40dcfdd668 | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_b4ade21adee157d4 | price_volatility_structure   | price|volatility     | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_c649a241fed6a55f | liquidity_volatility_guarded | liquidity|volatility | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_7035940e742f28d3 | liquidity_volatility_guarded | liquidity|volatility | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_71afa051e89efe97 | liquidity_volatility_guarded | liquidity|volatility | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |
| crypto_fg2_6dabc7639d6211d3 | liquidity_volatility_guarded | liquidity|volatility | mutation_source_only_control_required | one_bar_lag_stress|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random |

## Rejected Not-Authorized Candidates

| candidate_id                | family                 | field_families        | a7al2g_policy                     | policy_reason                                           |
|:----------------------------|:-----------------------|:----------------------|:----------------------------------|:--------------------------------------------------------|
| crypto_fg2_e3eeee6c6c128159 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_6f44fa67b5a9ca06 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_bc4bfd6a20077e8c | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_ed198b8d6c57d771 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_1ed3dccb9ce838ca | taker_flow_state       | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_90d8a2600b1cf58f | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_413accdbe82945d8 | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_5867678edef93f9e | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_1beccf4ae2ec1b40 | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_3522cd90888d43d7 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_59eb7be56beb98b0 | taker_flow_state       | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_aa3661f8eb8b5435 | basis_funding_crowding | basis|funding         | not_authorized_by_a7al1b_baseline | basis/funding families did not pass A7AL-1 controls     |
| crypto_fg2_4e9ba42b824279e6 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_fdcc4a2b92b3cf1d | taker_flow_state       | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_20696f318b21a836 | positioning_reversal   | positioning|price     | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_d0881b66a8dbe938 | taker_flow_state       | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |
| crypto_fg2_19dc36e900ebde39 | taker_flow_state       | liquidity|taker_ratio | not_authorized_by_a7al1b_baseline | positioning/taker families did not pass A7AL-1 controls |

## Boundary

```text
AUTHORIZED:
  A7AL-2I replay preflight only if decision PASS.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
