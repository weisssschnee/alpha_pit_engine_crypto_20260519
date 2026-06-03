# CRYPTO A7INPUT-0 INPUT APPROVAL PACKAGE

Generated: 2026-06-03T02:29:44Z

## Decision

`PASS_A7INPUT0_INPUT_APPROVAL_PACKAGE_READY`

A7INPUT-0 packages the input approval layer as an independent registry and tag/routing contract. It is not a replay, search, proof, or promotion stage.

## Manifest

```json
{
  "authorizes_a7input1_integration_smoke": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "condition_only_field_count": 4,
  "decision": "PASS_A7INPUT0_INPUT_APPROVAL_PACKAGE_READY",
  "executes_replay": false,
  "executes_search": false,
  "field_count": 36,
  "generated_at": "2026-06-03T02:29:44Z",
  "hard_blocked_field_count": 0,
  "ordinary_alpha_allowed_field_count": 26,
  "rescue_lane_field_count": 6,
  "source_decisions": [
    "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT",
    "PASS_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_BUILT"
  ],
  "source_stages": [
    "A7FF-CORE53IA",
    "A7FF-CORE53IAE"
  ],
  "stage": "A7INPUT-0",
  "tag_count": 7
}
```

## Tag Dictionary

| input_tag                          | meaning                                                                                   | allowed_in                                    | requires_cap   | rescue_lane   |
|:-----------------------------------|:------------------------------------------------------------------------------------------|:----------------------------------------------|:---------------|:--------------|
| A7INPUT_APPROVED_SIGNAL_PRIMARY    | field has enough standalone incremental information for ordinary alpha input              | generator,evaluator,selector,replay           | False          | False         |
| A7INPUT_APPROVED_REDUNDANT_CAP     | field is informative but belongs to high-correlation cluster; cap by info_cluster_id      | generator,evaluator,selector,replay           | True           | False         |
| A7INPUT_CONDITION_NEUTRALIZER_ONLY | field is state/taxonomy/neutralizer; not standalone alpha input                           | regime,neutralizer,condition,interaction_gate | True           | False         |
| A7INPUT_RESCUE_SPARSE_EVENT        | low coverage but high uniqueness/activity; can be tested only in sparse/event rescue lane | rescue_event,diagnostic_interaction           | True           | True          |
| A7INPUT_RESCUE_TS_STATE            | low cross-sectional variation; can be tested only as time-series or market-state variable | rescue_state,market_regime                    | True           | True          |
| A7INPUT_HARD_BLOCKED               | field should not enter alpha generation unless re-audited                                 | none                                          | True           | False         |
| A7INPUT_REVIEW_REQUIRED            | field lacks stable routing decision                                                       | manual_review                                 | True           | False         |

## Package Summary

| semantic_type      | input_tag                          | input_route                       |   field_count |
|:-------------------|:-----------------------------------|:----------------------------------|--------------:|
| basis_premium_like | A7INPUT_APPROVED_REDUNDANT_CAP     | capped_alpha_signal               |             2 |
| basis_premium_like | A7INPUT_APPROVED_SIGNAL_PRIMARY    | ordinary_alpha_signal             |             2 |
| funding_like       | A7INPUT_RESCUE_SPARSE_EVENT        | rescue_event_or_sparse_signal     |             4 |
| liquidity_like     | A7INPUT_APPROVED_SIGNAL_PRIMARY    | ordinary_alpha_signal             |             5 |
| liquidity_like     | A7INPUT_APPROVED_REDUNDANT_CAP     | capped_alpha_signal               |             2 |
| liquidity_like     | A7INPUT_RESCUE_TS_STATE            | rescue_timeseries_or_market_state |             2 |
| positioning_like   | A7INPUT_APPROVED_REDUNDANT_CAP     | capped_alpha_signal               |             4 |
| price_like         | A7INPUT_APPROVED_REDUNDANT_CAP     | capped_alpha_signal               |             6 |
| price_like         | A7INPUT_APPROVED_SIGNAL_PRIMARY    | ordinary_alpha_signal             |             2 |
| state_or_taxonomy  | A7INPUT_CONDITION_NEUTRALIZER_ONLY | condition_neutralizer_only        |             4 |
| volatility_like    | A7INPUT_APPROVED_SIGNAL_PRIMARY    | ordinary_alpha_signal             |             3 |

## Cluster Policy

| info_cluster_id   |   field_count | tags                               | semantic_types     | fields                                                                    |
|:------------------|--------------:|:-----------------------------------|:-------------------|:--------------------------------------------------------------------------|
| ic_000            |             6 | A7INPUT_APPROVED_REDUNDANT_CAP     | price_like         | index_close|mark_close|trade_close|trade_high|trade_low|trade_open        |
| ic_001            |             3 | A7INPUT_CONDITION_NEUTRALIZER_ONLY | state_or_taxonomy  | history_length_hours|listing_age_days|sqrt_listing_age_days               |
| ic_002            |             2 | A7INPUT_RESCUE_SPARSE_EVENT        | funding_like       | age_x_funding_abs|funding_rate_abs_168h                                   |
| ic_003            |             2 | A7INPUT_APPROVED_REDUNDANT_CAP     | positioning_like   | global_long_short_account_ratio_last|global_long_short_account_ratio_mean |
| ic_004            |             2 | A7INPUT_APPROVED_REDUNDANT_CAP     | positioning_like   | open_interest_last|open_interest_mean                                     |
| ic_005            |             2 | A7INPUT_APPROVED_REDUNDANT_CAP     | basis_premium_like | premium_close|premium_close_bps                                           |
| ic_006            |             2 | A7INPUT_APPROVED_REDUNDANT_CAP     | liquidity_like     | taker_buy_quote_volume|trade_quote_volume                                 |
| ic_007            |             1 | A7INPUT_CONDITION_NEUTRALIZER_ONLY | state_or_taxonomy  | age_percentile_active_universe                                            |
| ic_008            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | volatility_like    | age_x_volatility                                                          |
| ic_009            |             1 | A7INPUT_RESCUE_SPARSE_EVENT        | funding_like       | funding_rate                                                              |
| ic_010            |             1 | A7INPUT_RESCUE_SPARSE_EVENT        | funding_like       | funding_rate_mean_168h                                                    |
| ic_011            |             1 | A7INPUT_RESCUE_TS_STATE            | liquidity_like     | gap_hours_recent_168h                                                     |
| ic_012            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | liquidity_like     | kline_taker_buy_quote_share                                               |
| ic_013            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | basis_premium_like | mark_index_basis_bps                                                      |
| ic_014            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | basis_premium_like | mark_trade_basis_bps                                                      |
| ic_015            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | volatility_like    | realized_vol_168h                                                         |
| ic_016            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | volatility_like    | realized_vol_24h                                                          |
| ic_017            |             1 | A7INPUT_RESCUE_TS_STATE            | liquidity_like     | rolling_coverage_168h                                                     |
| ic_018            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | liquidity_like     | taker_buy_sell_volume_ratio_last                                          |
| ic_019            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | liquidity_like     | taker_buy_sell_volume_ratio_mean                                          |
| ic_020            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | liquidity_like     | trade_count                                                               |
| ic_021            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | price_like         | trade_return_1h                                                           |
| ic_022            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | price_like         | trade_return_24h                                                          |
| ic_023            |             1 | A7INPUT_APPROVED_SIGNAL_PRIMARY    | liquidity_like     | trade_volume                                                              |

## Routing Policy

```json
{
  "hard_block": {
    "blocked_tags": [
      "A7INPUT_HARD_BLOCKED",
      "A7INPUT_REVIEW_REQUIRED"
    ],
    "fail_closed": true
  },
  "interaction_alpha": {
    "allowed_tags": [
      "A7INPUT_APPROVED_SIGNAL_PRIMARY",
      "A7INPUT_APPROVED_REDUNDANT_CAP",
      "A7INPUT_CONDITION_NEUTRALIZER_ONLY"
    ],
    "condition_only_formula_forbidden": true,
    "requires_at_least_one_signal_tag": true
  },
  "ordinary_alpha": {
    "allowed_tags": [
      "A7INPUT_APPROVED_SIGNAL_PRIMARY",
      "A7INPUT_APPROVED_REDUNDANT_CAP"
    ],
    "blocked_tags": [
      "A7INPUT_CONDITION_NEUTRALIZER_ONLY",
      "A7INPUT_RESCUE_SPARSE_EVENT",
      "A7INPUT_RESCUE_TS_STATE",
      "A7INPUT_HARD_BLOCKED",
      "A7INPUT_REVIEW_REQUIRED"
    ],
    "max_redundant_cap_share": 0.35,
    "max_same_info_cluster_share": 0.2
  },
  "rescue_lane": {
    "allowed_tags": [
      "A7INPUT_RESCUE_SPARSE_EVENT",
      "A7INPUT_RESCUE_TS_STATE"
    ],
    "cannot_authorize_alpha_search": true,
    "must_be_separately_reported": true,
    "requires_event_or_state_specific_label": true
  }
}
```

## Authorization

```json
{
  "authorized": {
    "A7INPUT-1 generator/evaluator integration smoke": true
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
