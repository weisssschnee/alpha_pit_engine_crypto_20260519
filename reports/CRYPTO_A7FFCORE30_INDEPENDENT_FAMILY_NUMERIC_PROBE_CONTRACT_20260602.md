# CRYPTO A7FF-CORE30 INDEPENDENT FAMILY NUMERIC PROBE CONTRACT

Generated: 2026-06-01T18:37:52Z

## Decision

`PASS_A7FFCORE30_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE30E`

CORE30 is a numeric-probe contract. It prepares a balanced 240-row numeric queue but does not execute numeric evaluation, replay, search, large search, alpha proof, shadow, paper, or live.

## Family Summary

| family_id                         |   numeric_queue_count |   motif_count |   operator_count |   window_count |
|:----------------------------------|----------------------:|--------------:|-----------------:|---------------:|
| F1a_aggtrades_flow_microstructure |                    80 |             4 |                5 |              4 |
| F1b_taker_flow_market_panel       |                    80 |             4 |                5 |              4 |
| F2a_basis_funding_independent     |                    80 |             4 |                5 |              4 |

## Label Plan

| label                              | horizons_h   | role                           |
|:-----------------------------------|:-------------|:-------------------------------|
| L0_raw_forward_return              | 4,8,24       | primary_non_ranked             |
| L1_cross_sectional_relative_return | 4,8,24       | primary_non_ranked             |
| L3_liquidity_tier_relative_return  | 8,24         | state_relative                 |
| L5_vol_adjusted_return             | 8,24         | risk_adjusted                  |
| L7_ranked_future_return            | 8,24         | diagnostic_only_not_sufficient |

## Control Plan

| control             | required   |
|:--------------------|:-----------|
| row_shuffle         | True       |
| time_shuffle        | True       |
| wrong_lag_future    | True       |
| wrong_lag_stale     | True       |
| sign_flip           | True       |
| same_family_placebo | True       |

## Gate Plan

| gate              | threshold                                                                            |
|:------------------|:-------------------------------------------------------------------------------------|
| family_balance    | 80 numeric rows per family                                                           |
| preflight_pass    | all 240 selected rows passed CORE29E field preflight                                 |
| non_l7_evidence   | at least one non-L7 primary label family must be positive before any replay contract |
| control_ratio     | median control_ratio < 1.0; preferred < 0.8                                          |
| split_consistency | train/validation/test not all sign-inconsistent                                      |
| single_family_cap | no family can alone authorize replay/search                                          |
| large_search      | false                                                                                |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE30E bounded numeric probe execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "replay_contract": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core30e_numeric_probe": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_replay_contract": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE30_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE30E",
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "generated_at": "2026-06-01T18:37:52Z",
  "next_allowed": "A7FF-CORE30E bounded numeric probe execution",
  "numeric_queue_count": 240,
  "per_family_queue_target": 80,
  "source_decision": "PASS_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_READY_FOR_CORE30_CONTRACT",
  "source_stage": "A7FF-CORE29E",
  "stage": "A7FF-CORE30"
}
```
