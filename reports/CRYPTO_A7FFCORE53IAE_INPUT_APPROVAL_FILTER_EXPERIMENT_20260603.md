# CRYPTO A7FF-CORE53IAE INPUT APPROVAL FILTER EXPERIMENT

Generated: 2026-06-03T02:07:55Z

## Decision

`PASS_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_BUILT`

CORE53IAE applies the input approval ledger to the formula index and current selected replay queue. It validates whether the approval layer can screen information sources before candidate construction. It does not execute replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core54_queue_builder": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_BUILT",
  "diagnostic_clue_accepted_count": 24,
  "executes_replay": false,
  "executes_search": false,
  "formula_index_accept_rate": 0.39725229380066995,
  "formula_index_accepted_count": 8183,
  "formula_index_rejected_count": 12416,
  "formula_index_rows": 20599,
  "generated_at": "2026-06-03T02:07:55Z",
  "selected_queue_accepted_count": 295,
  "selected_queue_rejected_count": 89,
  "selected_queue_rows": 384,
  "source_decision": "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT",
  "source_stage": "A7FF-CORE53IA",
  "stage": "A7FF-CORE53IAE",
  "strict_clue_accepted_count": 1
}
```

## System Input Registry Summary

| semantic_type      | system_input_role        |   field_count |
|:-------------------|:-------------------------|--------------:|
| basis_premium_like | signal_primary           |             2 |
| basis_premium_like | signal_redundant_cap     |             2 |
| funding_like       | blocked                  |             4 |
| liquidity_like     | signal_primary           |             5 |
| liquidity_like     | blocked                  |             2 |
| liquidity_like     | signal_redundant_cap     |             2 |
| positioning_like   | signal_redundant_cap     |             4 |
| price_like         | signal_redundant_cap     |             6 |
| price_like         | signal_primary           |             2 |
| state_or_taxonomy  | condition_or_neutralizer |             4 |
| volatility_like    | signal_primary           |             3 |

## Filter Summary

| pool_name                    | filter_decision                          |   formula_count |   semantic_pair_count |   operator_count |   median_input_field_count |
|:-----------------------------|:-----------------------------------------|----------------:|----------------------:|-----------------:|---------------------------:|
| a7ff_v20260530_formula_index | reject_blocked_input                     |           12006 |                     3 |                9 |                          2 |
| a7ff_v20260530_formula_index | accept_primary_incremental_input         |            4198 |                    13 |               10 |                          2 |
| a7ff_v20260530_formula_index | accept_redundant_cap_only                |            3983 |                     9 |               10 |                          1 |
| a7ff_v20260530_formula_index | reject_no_known_input                    |             410 |                     3 |                8 |                          0 |
| a7ff_v20260530_formula_index | accept_redundant_cap_with_condition_only |               2 |                     1 |                2 |                          2 |
| core51px_selected_queue      | accept_primary_incremental_input         |             172 |                    30 |                7 |                          2 |
| core51px_selected_queue      | accept_redundant_cap_only                |             101 |                    13 |                6 |                          2 |
| core51px_selected_queue      | reject_blocked_input                     |              82 |                     9 |                7 |                          2 |
| core51px_selected_queue      | accept_redundant_cap_with_condition_only |              22 |                     4 |                5 |                          2 |
| core51px_selected_queue      | reject_condition_only                    |               7 |                     3 |                3 |                          1 |

## Clue Filter Summary

| arbitration_status   | filter_decision                          |   seed_count |   median_control_ratio |
|:---------------------|:-----------------------------------------|-------------:|-----------------------:|
| diagnostic_clue      | accept_primary_incremental_input         |           14 |               1.00187  |
| diagnostic_clue      | reject_blocked_input                     |            9 |               1.18111  |
| diagnostic_clue      | accept_redundant_cap_only                |            6 |               2.23853  |
| diagnostic_clue      | accept_redundant_cap_with_condition_only |            3 |               1.05459  |
| diagnostic_clue      | reject_condition_only                    |            2 |               4.07641  |
| rejected             | accept_primary_incremental_input         |          157 |               1.39564  |
| rejected             | accept_redundant_cap_only                |           95 |               1.19145  |
| rejected             | reject_blocked_input                     |           73 |               1.09318  |
| rejected             | accept_redundant_cap_with_condition_only |           19 |               1.03333  |
| rejected             | reject_condition_only                    |            5 |               1.39674  |
| strict_replay_clue   | accept_primary_incremental_input         |            1 |               0.882984 |

## Accepted Cluster Usage

| info_cluster_id   |   accepted_formula_count | fields                                                                    | semantic_types     |
|:------------------|-------------------------:|:--------------------------------------------------------------------------|:-------------------|
| ic_003            |                     3404 | global_long_short_account_ratio_last|global_long_short_account_ratio_mean | positioning_like   |
| ic_013            |                     1894 | mark_index_basis_bps                                                      | basis_premium_like |
| ic_005            |                     1633 | premium_close|premium_close_bps                                           | basis_premium_like |
| ic_000            |                     1507 | index_close|mark_close|trade_close|trade_high|trade_low|trade_open        | price_like         |
| ic_015            |                     1102 | realized_vol_168h                                                         | volatility_like    |
| ic_016            |                     1057 | realized_vol_24h                                                          | volatility_like    |
| ic_021            |                     1041 | trade_return_1h                                                           | price_like         |
| ic_014            |                      367 | mark_trade_basis_bps                                                      | basis_premium_like |
| ic_004            |                      288 | open_interest_last|open_interest_mean                                     | positioning_like   |
| ic_008            |                      124 | age_x_volatility                                                          | volatility_like    |
| ic_018            |                      108 | taker_buy_sell_volume_ratio_last                                          | liquidity_like     |
| ic_019            |                      104 | taker_buy_sell_volume_ratio_mean                                          | liquidity_like     |
| ic_022            |                       66 | trade_return_24h                                                          | price_like         |
| ic_006            |                       40 | taker_buy_quote_volume|trade_quote_volume                                 | liquidity_like     |
| ic_020            |                       20 | trade_count                                                               | liquidity_like     |
| ic_023            |                       20 | trade_volume                                                              | liquidity_like     |
| ic_001            |                        6 | history_length_hours|listing_age_days|sqrt_listing_age_days               | state_or_taxonomy  |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE54 input-approval-aware queue builder": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
