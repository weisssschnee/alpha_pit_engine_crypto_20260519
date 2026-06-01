# CRYPTO A7FF-CORE38E PORTFOLIO-LABEL OBJECTIVE AUDIT

Generated: 2026-06-01T19:52:28Z

## Decision

`HOLD_A7FFCORE38E_BOOK_OBJECTIVE_AUDIT_REQUIRES_SYMBOL_LEVEL_REPLAY_INPUT`

CORE38E audits whether the portfolio-label objectives from CORE38 can be computed from existing artifacts. It does not execute replay, generation, search, alpha proof, shadow, paper, or live.

## Main Finding

Current replay artifacts are aggregate candidate summaries. They are enough to re-score legacy B0 net spread, but not enough for B1/B2/B3/B4 portfolio/book objectives because symbol-level score, return, rank, residual label, and position-weight traces are absent.

## Objective Computability Audit

| objective_id                  | required_columns                                                                         | available_status           | missing_columns                                                                       | audit_result                                                       |
|:------------------------------|:-----------------------------------------------------------------------------------------|:---------------------------|:--------------------------------------------------------------------------------------|:-------------------------------------------------------------------|
| B0_legacy_net_spread          | replay_candidate_id, split, label_family, horizon_h, net_spread, control_ratio           | AVAILABLE                  |                                                                                       | available_but_already_failed                                       |
| B1_cross_sectional_rank_book  | timestamp, symbol, candidate_score, forward_return, rank_weight                          | MISSING_SYMBOL_LEVEL_INPUT | timestamp, symbol, candidate_score, forward_return, rank_weight                       | cannot_compute_from_aggregate_replay_rows                          |
| B2_market_beta_residual_book  | timestamp, symbol, forward_return, btc_eth_market_return, beta_residual_return           | MISSING_SYMBOL_LEVEL_INPUT | timestamp, symbol, forward_return, btc_eth_market_return, beta_residual_return        | cannot_compute_from_aggregate_replay_rows                          |
| B3_vol_adjusted_rank_book     | timestamp, symbol, candidate_score, forward_return, realized_vol, vol_adjusted_return    | MISSING_SYMBOL_LEVEL_INPUT | timestamp, symbol, candidate_score, forward_return, realized_vol, vol_adjusted_return | cannot_compute_from_aggregate_replay_rows                          |
| B4_liquidity_cost_capped_book | timestamp, symbol, candidate_score, quote_volume, turnover, cost_bucket, position_weight | PARTIAL_AGGREGATE_ONLY     | timestamp, symbol, candidate_score, quote_volume, cost_bucket, position_weight        | aggregate turnover exists but cannot enforce symbol-level caps     |
| B5_family_role_book           | family_id, split, net_spread, control_ratio, train_oos_diagnosis                         | PARTIAL_DIAGNOSTIC_ONLY    | symbol-level hedge/regime book attribution                                            | can diagnose family role but cannot compute executable family book |

## Label Computability Audit

| label_id                           | status            | primary   | note                                            | symbol_level_required   | computable_from_current_artifacts   | audit_note                                                             |
|:-----------------------------------|:------------------|:----------|:------------------------------------------------|:------------------------|:------------------------------------|:-----------------------------------------------------------------------|
| L0_raw_forward_return              | allowed_reference | False     | cannot be sole proof label                      | False                   | True                                | aggregate proxy exists but cannot be sole proof label                  |
| L1_cross_sectional_relative_return | allowed_primary   | True      | preferred for cross-sectional book              | True                    | False                               | requires symbol-level score/return panel, not aggregate replay summary |
| L2_market_beta_residual_return     | required_primary  | True      | must be tested before search authorization      | True                    | False                               | requires symbol-level score/return panel, not aggregate replay summary |
| L3_liquidity_tier_relative_return  | allowed_primary   | True      | controls liquidity-tier distortions             | True                    | False                               | requires symbol-level score/return panel, not aggregate replay summary |
| L5_vol_adjusted_return             | allowed_primary   | True      | controls high-vol dominance                     | True                    | False                               | requires symbol-level score/return panel, not aggregate replay summary |
| L7_ranked_future_return            | diagnostic_only   | False     | rank labels cannot alone authorize alpha/search | False                   | False                               | requires symbol-level score/return panel, not aggregate replay summary |

## Blocker Matrix

| blocker                           | severity   | impact                                                       | required_fix                                                             |
|:----------------------------------|:-----------|:-------------------------------------------------------------|:-------------------------------------------------------------------------|
| aggregate_replay_summary_only     | HIGH       | B1/B2/B3/B4 portfolio objectives cannot be computed          | build symbol-level candidate score and label/book input packet           |
| missing_position_weight_trace     | HIGH       | cannot enforce max symbol/family/liquidity caps              | emit per-timestamp selected long/short weights before spread aggregation |
| missing_beta_residual_label_panel | MEDIUM     | cannot test B2 market-beta residual objective                | construct BTC/ETH/market residual return labels with PIT split metadata  |
| legacy_net_spread_reference_only  | HIGH       | the only fully computable objective is already known to fail | do not rerun B0 as primary objective                                     |

## Authorization Matrix

| task                                                              | status                   | reason                                                                     |
|:------------------------------------------------------------------|:-------------------------|:---------------------------------------------------------------------------|
| A7FF-CORE39 symbol-level book input packet contract               | AUTHORIZED_CONTRACT_ONLY | CORE38E shows book objectives need symbol-level score/return/weight inputs |
| A7FF-CORE38E book objective execution from current aggregate rows | NOT_AUTHORIZED           | current artifacts are aggregate summaries and cannot compute B1/B2/B3/B4   |
| formula_search                                                    | NOT_AUTHORIZED           | book objective input packet missing                                        |
| large_search                                                      | NOT_AUTHORIZED           | book objective input packet missing                                        |
| alpha_proof / shadow / paper / live                               | NOT_AUTHORIZED           | no proof object                                                            |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core39_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "computable_primary_objectives": 0,
  "decision": "HOLD_A7FFCORE38E_BOOK_OBJECTIVE_AUDIT_REQUIRES_SYMBOL_LEVEL_REPLAY_INPUT",
  "dominant_blocker": "symbol_level_book_input_missing",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:52:28Z",
  "next_allowed": "A7FF-CORE39 symbol-level book input packet contract",
  "reference_objectives_available": 1,
  "source_decision": "PASS_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_READY_FOR_CORE38E",
  "source_stage": "A7FF-CORE38",
  "stage": "A7FF-CORE38E"
}
```
