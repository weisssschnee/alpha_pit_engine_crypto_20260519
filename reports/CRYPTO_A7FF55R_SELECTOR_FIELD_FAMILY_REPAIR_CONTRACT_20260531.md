# CRYPTO A7FF-55R SELECTOR FIELD-FAMILY REPAIR CONTRACT

Generated: 2026-05-31T11:35:06Z

## Decision

`PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH`

A7FF-55R converts the A7FF-55F failure into a concrete repair contract. It does not run replay or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_next_contract": true,
  "authorizes_next_execution": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T11:35:06Z",
  "next_allowed": "A7FF-55R1 family-diverse supplemental primary-label input generation, if explicitly executed",
  "repair_action_count": 6,
  "source_blockers": [
    "top_family_share_above_0p30",
    "top_motif_share_above_0p30",
    "top_label_share_above_0p35"
  ],
  "source_decision": "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED",
  "source_stage": "A7FF-55F",
  "stage": "A7FF-55R",
  "supplemental_family_quota_rows": 7,
  "uses_may": false
}
```

## Prior Selected Family Exposure

| semantic_pair                         |   selected_count |   selected_share |
|:--------------------------------------|-----------------:|-----------------:|
| basis_premium_like\|price_return_like |               11 |        0.366667  |
| liquidity_like\|price_return_like     |                1 |        0.0333333 |
| open_interest_like\|price_return_like |                1 |        0.0333333 |
| positioning_like\|price_return_like   |                3 |        0.1       |
| regime_state\|price_return_like       |               12 |        0.4       |
| volatility_like\|basis_premium_like   |                2 |        0.0666667 |

## Prior Selected Motif Exposure

| motif         |   selected_count |   selected_share |
|:--------------|-----------------:|-----------------:|
| safe_div_abs  |                6 |         0.2      |
| signed_spread |                3 |         0.1      |
| spread_rank   |               16 |         0.533333 |
| sub           |                5 |         0.166667 |

## Repair Actions

| repair_id                           | target           | rule                                                                                                                          | reason                                                |
|:------------------------------------|:-----------------|:------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|
| R0_primary_label_balance_keep       | label_family     | keep L0/L1/L3 minimum 4 rows each; L5/L7 remain excluded from alpha-selector queue                                            | A7FF55F solved label absence; retain this constraint  |
| R1_family_anti_concentration        | semantic_pair    | hard cap per selected semantic_pair <= 0.25 until at least 5 families are selected                                            | A7FF55F top semantic pair share was 0.40              |
| R2_motif_anti_concentration         | motif            | hard cap spread_rank <= 0.25 and require at least 5 motifs before any replay-preflight contract                               | A7FF55F spread_rank share was 0.5333                  |
| R3_underrepresented_family_boost    | input_generation | supplemental primary-label inputs must over-sample open_interest, positioning, liquidity, volatility, and taker-flow families | A7FF55F had only 1-3 selected rows in those families  |
| R4_duplicate_economic_core_downrank | selector_score   | down-rank repeated price_return interactions after each family reaches 4 rows                                                 | current selected queue is price-return-core dominated |
| R5_control_margin_preserve          | hard_gate        | keep control_ratio_premay_max < 0.80 and wrong-lag/shuffle weaker than original                                               | do not solve diversity by admitting control-like rows |

## Supplemental Family Quota

| field_family       |   min_primary_candidates | preferred_labels   | allowed_role                 |
|:-------------------|-------------------------:|:-------------------|:-----------------------------|
| open_interest_like |                       12 | L0,L1,L3           | ordinary_or_mixed_alpha_only |
| positioning_like   |                       12 | L0,L1,L3           | ordinary_or_mixed_alpha_only |
| liquidity_like     |                       10 | L0,L1,L3           | ordinary_or_mixed_alpha_only |
| volatility_like    |                       10 | L0,L1,L3           | ordinary_or_mixed_alpha_only |
| taker_flow_like    |                        8 | L0,L1,L3           | ordinary_or_mixed_alpha_only |
| basis_premium_like |                        0 | L0,L1,L3           | cap_only_no_boost            |
| regime_state       |                        0 | L0,L1,L3           | cap_only_no_boost            |

## Candidate Family Evidence

| label_family                       | semantic_pair                         |   candidate_rows |
|:-----------------------------------|:--------------------------------------|-----------------:|
| L3_liquidity_tier_relative_return  | regime_state\|price_return_like       |               14 |
| L1_cross_sectional_relative_return | basis_premium_like\|price_return_like |               13 |
| L3_liquidity_tier_relative_return  | basis_premium_like\|price_return_like |               13 |
| L0_raw_forward_return              | basis_premium_like\|price_return_like |               11 |
| L1_cross_sectional_relative_return | regime_state\|price_return_like       |               11 |
| L0_raw_forward_return              | regime_state\|price_return_like       |                9 |
| L1_cross_sectional_relative_return | positioning_like\|price_return_like   |                3 |
| L0_raw_forward_return              | volatility_like\|basis_premium_like   |                2 |
| L1_cross_sectional_relative_return | volatility_like\|basis_premium_like   |                2 |
| L3_liquidity_tier_relative_return  | volatility_like\|basis_premium_like   |                2 |
| L0_raw_forward_return              | open_interest_like\|price_return_like |                1 |
| L0_raw_forward_return              | positioning_like\|price_return_like   |                1 |
| L1_cross_sectional_relative_return | open_interest_like\|price_return_like |                1 |
| L0_raw_forward_return              | liquidity_like\|price_return_like     |                1 |
| L3_liquidity_tier_relative_return  | open_interest_like\|price_return_like |                1 |
| L3_liquidity_tier_relative_return  | liquidity_like\|price_return_like     |                1 |

## Boundary

```text
contract written: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
