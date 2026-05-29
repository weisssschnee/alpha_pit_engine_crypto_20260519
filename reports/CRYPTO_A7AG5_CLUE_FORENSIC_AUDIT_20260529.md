# CRYPTO A7AG-5 CLUE FORENSIC AUDIT

Generated: 2026-05-29T08:46:38Z

## Decision

`HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION`

A7AG-5 checks whether A7AG-3/4 clues translate into ordinary labels and whether they are concentration-dominated. It does not generate formulas, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7ag6_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "concentration_blocker_count": 0,
  "cost20_original_survivor_count": 8,
  "decision": "HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION",
  "executes_forensic_audit": true,
  "executes_formula_generation": false,
  "executes_search": false,
  "executes_training": false,
  "full_timestamps_before_subset": 21025,
  "generated_at": "2026-05-29T08:46:38Z",
  "input_a7ag4_decision": "PASS_A7AG4_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AG5",
  "input_clue_count": 24,
  "missing_fields": [],
  "ordinary_label_translation_clue_count": 0,
  "stage": "A7AG-5",
  "symbols_loaded": 96,
  "timestamps": 3481,
  "translation_rows": 120,
  "uses_may": false
}
```

## Label Translation Summary

| clue_role                             | translation_label_family           |   rows |   replay_clues |   median_control_ratio |   cost20_survivors |
|:--------------------------------------|:-----------------------------------|-------:|---------------:|-----------------------:|-------------------:|
| basis_premium_vol_adjusted_diagnostic | L0_raw_forward_return              |      2 |              0 |               1.0177   |                  0 |
| basis_premium_vol_adjusted_diagnostic | L1_cross_sectional_relative_return |      2 |              0 |               1.0177   |                  0 |
| basis_premium_vol_adjusted_diagnostic | L2_BTC_ETH_beta_residual_return    |      2 |              0 |               0.910876 |                  0 |
| basis_premium_vol_adjusted_diagnostic | L5_vol_adjusted_return             |      2 |              2 |               0.909281 |                  2 |
| basis_premium_vol_adjusted_diagnostic | L6_downside_avoidance              |      2 |              0 |               1.40099  |                  0 |
| downside_risk_defense_clue            | L0_raw_forward_return              |     19 |              0 |               6.04742  |                  1 |
| downside_risk_defense_clue            | L1_cross_sectional_relative_return |     19 |              0 |               6.04742  |                  1 |
| downside_risk_defense_clue            | L2_BTC_ETH_beta_residual_return    |     19 |              0 |               8.30753  |                  0 |
| downside_risk_defense_clue            | L5_vol_adjusted_return             |     19 |              0 |              20.1598   |                  9 |
| downside_risk_defense_clue            | L6_downside_avoidance              |     19 |             19 |               0.796129 |                  3 |
| neutralized_vol_adjusted_diagnostic   | L0_raw_forward_return              |      3 |              0 |               0.994262 |                  0 |
| neutralized_vol_adjusted_diagnostic   | L1_cross_sectional_relative_return |      3 |              0 |               0.994262 |                  0 |
| neutralized_vol_adjusted_diagnostic   | L2_BTC_ETH_beta_residual_return    |      3 |              0 |               1.11144  |                  0 |
| neutralized_vol_adjusted_diagnostic   | L5_vol_adjusted_return             |      3 |              3 |               0.624537 |                  3 |
| neutralized_vol_adjusted_diagnostic   | L6_downside_avoidance              |      3 |              0 |               1.96126  |                  0 |

## Concentration Summary

| clue_role                             |   candidates |   concentration_blockers |   max_symbol_share |   max_month_share |   max_raw_latent_state_share |
|:--------------------------------------|-------------:|-------------------------:|-------------------:|------------------:|-----------------------------:|
| basis_premium_vol_adjusted_diagnostic |            2 |                        0 |          0.0344725 |          0.358129 |                     0.379546 |
| downside_risk_defense_clue            |           19 |                        0 |          0.0514509 |          0.395565 |                     0.236836 |
| neutralized_vol_adjusted_diagnostic   |            3 |                        0 |          0.0389001 |          0.356804 |                     0.377245 |

## Ordinary Label Translation Candidates

`<empty>`

## Boundary

```text
A7AG-5 is forensic only.
May is not used.
No formula search, large search, alpha proof, shadow, paper, or live is authorized.
```
