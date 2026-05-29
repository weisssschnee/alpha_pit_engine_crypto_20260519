# CRYPTO A7AI-F0 FIELD CONTRACT ENFORCEMENT LEDGER

Generated: 2026-05-29T09:38:53Z

## Decision

`PASS_A7AIF0_FIELD_CONTRACT_ENFORCEMENT_LEDGER_READY_FOR_A7AIF1`

A7AI-F0 converts lineage, primitive response roles, timing contracts, and the generator motif pack into a machine-readable enforcement ledger. It does not run search, replay, training, or proof.

## Manifest

```json
{
  "authorizes_a7aif1_engine_enforcement_gap_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AIF0_FIELD_CONTRACT_ENFORCEMENT_LEDGER_READY_FOR_A7AIF1",
  "diagnostic_allowed_motif_fields": 19,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "field_count": 81,
  "generated_at": "2026-05-29T09:38:53Z",
  "hard_blockers": [],
  "input_artifacts": {
    "a7ar2_field_audit": "runtime\\a7ar2_feature_algebra_parity_smoke\\a7ar2_field_contract_audit.csv",
    "feature_role": "runtime\\a7aa2_feature_role_classification\\a7aa2_feature_role_ledger.csv",
    "lineage": "runtime\\a7al0r_code_feature_regime_readiness_audit\\a7al0r_feature_lineage_ledger.csv",
    "motif_pack": "config\\crypto_formula_gen_v2_motif_pack_v1.json",
    "timing": "runtime\\a7al0_top498_alpha_search_contract\\a7al_field_timing_contract.csv"
  },
  "motif_field_count": 28,
  "motif_warning_count": 3,
  "ordinary_alpha_allowed_motif_fields": 1,
  "risk_defense_allowed_motif_fields": 5,
  "stage": "A7AI-F0",
  "uses_may": false
}
```

## Motif Family Enforcement Summary

| motif_field_family   |   field_count |   ordinary_allowed |   diagnostic_allowed |   risk_defense_allowed |   forbidden |   contract_missing |   timing_policy_hold |   weak_or_unclassified |
|:---------------------|--------------:|-------------------:|---------------------:|-----------------------:|------------:|-------------------:|---------------------:|-----------------------:|
| liquidity            |             4 |                  0 |                    2 |                      0 |           0 |                  0 |                    0 |                      2 |
| funding              |             1 |                  0 |                    0 |                      0 |           0 |                  0 |                    0 |                      1 |
| positioning          |             6 |                  0 |                    3 |                      3 |           0 |                  0 |                    0 |                      0 |
| basis                |             4 |                  1 |                    3 |                      0 |           0 |                  0 |                    0 |                      0 |
| open_interest        |             4 |                  0 |                    2 |                      2 |           0 |                  0 |                    0 |                      0 |
| volatility           |             4 |                  0 |                    4 |                      0 |           0 |                  0 |                    0 |                      0 |
| return               |             2 |                  0 |                    2 |                      0 |           0 |                  0 |                    0 |                      0 |
| taker_ratio          |             2 |                  0 |                    2 |                      0 |           0 |                  0 |                    0 |                      0 |
| price                |             1 |                  0 |                    1 |                      0 |           0 |                  0 |                    0 |                      0 |

## Enforcement Status Summary

| in_motif_pack   | enforcement_status             |   count |
|:----------------|:-------------------------------|--------:|
| True            | OK_DIAGNOSTIC_OR_REGIME        |      19 |
| True            | OK_RISK_DEFENSE_OR_NEUTRALIZER |       5 |
| True            | HOLD_WEAK_RESPONSE             |       3 |
| True            | OK_ORDINARY_ALPHA              |       1 |
| False           | HOLD_UNCLASSIFIED              |      31 |
| False           | FORBID                         |      10 |
| False           | HOLD_WEAK_RESPONSE             |       5 |
| False           | OK_DIAGNOSTIC_OR_REGIME        |       4 |
| False           | OK_RISK_DEFENSE_OR_NEUTRALIZER |       3 |

## Generator Field Enforcement

| field_name                           | motif_field_family   | semantic_role                         | feature_role                      | ordinary_alpha_allowed   | diagnostic_allowed   | risk_defense_allowed   | enforcement_status             | enforcement_reason                                  |
|:-------------------------------------|:---------------------|:--------------------------------------|:----------------------------------|:-------------------------|:---------------------|:-----------------------|:-------------------------------|:----------------------------------------------------|
| funding_rate                         | funding              | weak_or_unstable                      | weak_or_unstable                  | False                    | False                | False                  | HOLD_WEAK_RESPONSE             | primitive_response_map_weak_or_unstable             |
| global_long_short_account_ratio_last | positioning          | risk_exposure_or_control_like         | control_like_or_risk_exposure     | False                    | False                | True                   | OK_RISK_DEFENSE_OR_NEUTRALIZER | control_like_or_risk_exposure_not_primary_alpha     |
| global_long_short_account_ratio_mean | positioning          | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| index_close                          | price                | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| mark_close                           | return               | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| mark_high                            | volatility           | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| mark_index_basis_bps                 | basis                | ordinary_signal_candidate             | predictive_signal_candidate       | True                     | False                | False                  | OK_ORDINARY_ALPHA              | ordinary_label_response_and_contract_clean          |
| mark_low                             | volatility           | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| mark_trade_basis_bps                 | basis                | regime_state_or_interaction_input     | regime_state_or_interaction_input | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| open_interest_last                   | open_interest        | risk_exposure_or_control_like         | control_like_or_risk_exposure     | False                    | False                | True                   | OK_RISK_DEFENSE_OR_NEUTRALIZER | control_like_or_risk_exposure_not_primary_alpha     |
| open_interest_mean                   | open_interest        | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| open_interest_value_last             | open_interest        | risk_exposure_or_control_like         | control_like_or_risk_exposure     | False                    | False                | True                   | OK_RISK_DEFENSE_OR_NEUTRALIZER | control_like_or_risk_exposure_not_primary_alpha     |
| open_interest_value_mean             | open_interest        | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| premium_close                        | basis                | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| premium_close_bps                    | basis                | diagnostic_rank_or_nonordinary_signal | predictive_signal_candidate       | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| taker_buy_quote_volume               | liquidity            | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| taker_buy_sell_volume_ratio_last     | taker_ratio          | regime_state_or_interaction_input     | regime_state_or_interaction_input | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| taker_buy_sell_volume_ratio_mean     | taker_ratio          | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| top_long_short_account_ratio_last    | positioning          | risk_exposure_or_control_like         | control_like_or_risk_exposure     | False                    | False                | True                   | OK_RISK_DEFENSE_OR_NEUTRALIZER | control_like_or_risk_exposure_not_primary_alpha     |
| top_long_short_account_ratio_mean    | positioning          | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| top_long_short_position_ratio_last   | positioning          | risk_exposure_or_control_like         | control_like_or_risk_exposure     | False                    | False                | True                   | OK_RISK_DEFENSE_OR_NEUTRALIZER | control_like_or_risk_exposure_not_primary_alpha     |
| top_long_short_position_ratio_mean   | positioning          | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| trade_close                          | return               | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| trade_count                          | liquidity            | weak_or_unstable                      | weak_or_unstable                  | False                    | False                | False                  | HOLD_WEAK_RESPONSE             | primitive_response_map_weak_or_unstable             |
| trade_high                           | volatility           | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| trade_low                            | volatility           | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |
| trade_quote_volume                   | liquidity            | weak_or_unstable                      | weak_or_unstable                  | False                    | False                | False                  | HOLD_WEAK_RESPONSE             | primitive_response_map_weak_or_unstable             |
| trade_volume                         | liquidity            | unclassified_generator_ingredient     |                                   | False                    | True                 | False                  | OK_DIAGNOSTIC_OR_REGIME        | nonordinary_response_or_regime_input_contract_clean |

## Boundary

```text
No formula search is authorized.
Fields can be available to the generator in different modes without being primary ordinary-alpha selector seeds.
Label/future-dependent fields, same-bar fields, fixed-delay stress fields, and missing-contract motif fields are hard blockers.
```
