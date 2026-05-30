# CRYPTO A7FF-46 CANDIDATE FREEZE

Generated: 2026-05-30T18:34:51Z

## Decision

`PASS_A7FF46_CANDIDATE_FREEZE_READY_FOR_A7FF47_NO_SEARCH_AUTH`

A7FF-46 freezes the A7FF-45 bounded replay confirmed rows as research clues only. They are not alpha candidates and do not authorize formula search.

## Manifest

```json
{
  "authorizes_a7ff47_portfolio_microreplay": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FF46_CANDIDATE_FREEZE_READY_FOR_A7FF47_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "frozen_candidate_rows": 7,
  "frozen_family_count": 2,
  "frozen_label_family_count": 1,
  "generated_at": "2026-05-30T18:34:51Z",
  "max_control_ratio": 0.6215343323193879,
  "min_cost10": 0.0467692280739554,
  "min_robust_floor": 1.598196625160734,
  "source_a7ff45_decision": "PASS_A7FF45_BOUNDED_DEEP_REPLAY_CONFIRMED_READY_FOR_A7FF46_NO_SEARCH_AUTH",
  "stage": "A7FF-46",
  "uses_may": false,
  "warnings": [
    "single_label_family_L5_vol_adjusted_only"
  ]
}
```

## Frozen Candidate Pool

| blueprint_id            | expression_r9                                                                                 | semantic_pair                   | motif       | label_family           |   label_horizon_h |   confirmed_control_ratio |   cost10_recent_oriented_confirmed |   one_bar_lag_recent_oriented_confirmed |   robust_min_tstat_floor_confirmed | confirmed_ok   | freeze_status                 | promotion_boundary                | allowed_next_use                                      | forbidden_next_use               |
|:------------------------|:----------------------------------------------------------------------------------------------|:--------------------------------|:------------|:-----------------------|------------------:|--------------------------:|-----------------------------------:|----------------------------------------:|-----------------------------------:|:---------------|:------------------------------|:----------------------------------|:------------------------------------------------------|:---------------------------------|
| a7ff33_43985dd6fcd563f5 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,12))                          | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                  0.204006 |                          0.135148  |                               0.0545467 |                            6.57954 | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_eda87df62c06d036 | Sub(ZScore(funding_rate_state_last_ffill_8h),ZScore(Clip(ZScore(mark_index_basis_bps),-3,3))) | funding_like|basis_premium_like | zspread     | L5_vol_adjusted_return |                 1 |                  0.319537 |                          0.121763  |                               0.0373996 |                            5.82468 | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_c4e35734432be936 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,168))                         | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                  0.594426 |                          0.108484  |                               0.0571994 |                            5.35796 | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_757d3c59e04d21f8 | Sub(funding_rate_state_last_ffill_8h,Delta(mark_index_basis_bps,72))                          | funding_like|basis_premium_like | sub         | L5_vol_adjusted_return |                 1 |                  0.621534 |                          0.10639   |                               0.02988   |                            5.41414 | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_80c2b011fb504ed3 | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,12)))                          | regime_state|price_return_like  | spread_rank | L5_vol_adjusted_return |                 1 |                  0.469258 |                          0.0691669 |                               0.0352078 |                            1.5982  | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_5199304844c4d2af | Sub(rolling_coverage_168h,Delta(trade_return_1h,12))                                          | regime_state|price_return_like  | sub         | L5_vol_adjusted_return |                 1 |                  0.538266 |                          0.0691669 |                               0.0352078 |                            1.5982  | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |
| a7ff33_ab416bf651b9dfeb | Sub(CSRank(rolling_coverage_168h),CSRank(Delta(trade_return_1h,8)))                           | regime_state|price_return_like  | spread_rank | L5_vol_adjusted_return |                 1 |                  0.498355 |                          0.0467692 |                               0.0272127 |                            1.77492 | True           | bounded_replay_confirmed_clue | research_clue_only_no_alpha_proof | portfolio_microreplay_and_label_diversification_audit | formula_search_or_live_promotion |

## Family Freeze Summary

| semantic_pair                   |   frozen_rows |   blueprints |   motifs |   labels |   max_control_ratio |   min_cost10 |   min_robust_floor |
|:--------------------------------|--------------:|-------------:|---------:|---------:|--------------------:|-------------:|-------------------:|
| funding_like|basis_premium_like |             4 |            4 |        2 |        1 |            0.621534 |    0.10639   |            5.35796 |
| regime_state|price_return_like  |             3 |            3 |        2 |        1 |            0.538266 |    0.0467692 |            1.5982  |

## A7FF-45 Family Confirmation

| semantic_pair                   |   target_rows |   confirmed_rows |   found_rows |   motifs |   labels |   max_control_ratio |   median_control_ratio |   min_cost10 |   min_robust_floor |
|:--------------------------------|--------------:|-----------------:|-------------:|---------:|---------:|--------------------:|-----------------------:|-------------:|-------------------:|
| funding_like|basis_premium_like |             4 |                4 |            4 |        2 |        1 |            0.621534 |               0.456982 |    0.10639   |            5.35796 |
| regime_state|price_return_like  |             3 |                3 |            3 |        2 |        1 |            0.538266 |               0.498355 |    0.0467692 |            1.5982  |

## Authorization Matrix

```json
{
  "authorized": {
    "A7FF-47": "portfolio microreplay / label diversification audit on frozen 7-row pool",
    "A7PM maintenance": "source-of-truth refresh"
  },
  "not_authorized": {
    "alpha_proof": "not authorized",
    "formula_search": "frozen clues are not alpha candidates",
    "large_search": "not authorized",
    "shadow_paper_live": "not authorized"
  }
}
```

## Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
