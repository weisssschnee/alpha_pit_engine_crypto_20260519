# CRYPTO A7FF-CORE38 PORTFOLIO-LABEL OBJECTIVE CONTRACT

Generated: 2026-06-01T19:49:35Z

## Decision

`PASS_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_READY_FOR_CORE38E`

CORE38 defines the executable portfolio-label objective required after CORE37X rejected same-queue rerun and large formula search. It does not execute replay, generation, search, alpha proof, shadow, paper, or live.

## Objective Book Contract

| objective_id                  | role               | description                                                                                                  | allowed_as_primary   | reason                                                                                                 |
|:------------------------------|:-------------------|:-------------------------------------------------------------------------------------------------------------|:---------------------|:-------------------------------------------------------------------------------------------------------|
| B0_legacy_net_spread          | reference_only     | existing per-candidate net spread proxy used in CORE33/34/36                                                 | False                | failed train-to-OOS executable survivor translation                                                    |
| B1_cross_sectional_rank_book  | primary_candidate  | top/bottom cross-sectional rank book with equal-weight and liquidity-capped variants                         | True                 | tests whether numeric rank response converts into book spread without relying on raw return label only |
| B2_market_beta_residual_book  | primary_candidate  | BTC/ETH/market beta residualized return book before spread and control gates                                 | True                 | separates market beta from symbol-specific cross-section structure                                     |
| B3_vol_adjusted_rank_book     | diagnostic_primary | vol-adjusted rank return and downside-normalized book proxy                                                  | True                 | prevents high-vol small symbols from dominating raw spread                                             |
| B4_liquidity_cost_capped_book | primary_candidate  | book proxy with turnover, quote-volume, and cost bucket caps                                                 | True                 | aligns replay objective to executable capacity and cost before selector scoring                        |
| B5_family_role_book           | diagnostic_only    | family-specific book roles: F1a may be hedge/regime-like; F1b/F2a require control-first directional evidence | False                | CORE36ER showed family-specific failure modes, not one universal objective                             |

## Label Contract

| label_id                           | status            | primary   | note                                            |
|:-----------------------------------|:------------------|:----------|:------------------------------------------------|
| L0_raw_forward_return              | allowed_reference | False     | cannot be sole proof label                      |
| L1_cross_sectional_relative_return | allowed_primary   | True      | preferred for cross-sectional book              |
| L2_market_beta_residual_return     | required_primary  | True      | must be tested before search authorization      |
| L3_liquidity_tier_relative_return  | allowed_primary   | True      | controls liquidity-tier distortions             |
| L5_vol_adjusted_return             | allowed_primary   | True      | controls high-vol dominance                     |
| L7_ranked_future_return            | diagnostic_only   | False     | rank labels cannot alone authorize alpha/search |

## Book Constraints

| constraint         | value                                                     | hard_gate   |
|:-------------------|:----------------------------------------------------------|:------------|
| max_symbol_weight  | 2.5% or lower in top498 book                              | True        |
| max_family_weight  | 35% selected queue cap                                    | True        |
| max_cluster_weight | 25% signal-vector/cluster cap                             | True        |
| liquidity_cap      | quote-volume tier cap before spread scoring               | True        |
| cost_buckets       | 2bps/5bps/10bps variants; primary must survive 5bps       | True        |
| controls           | wrong-lag, stale, shuffle, sign-flip weaker than original | True        |
| oos_balance        | validation/test/recent cannot be dominated by one split   | True        |

## Execution Plan

| stage        | action                                                                                  | executes_new_generation   | executes_search   | executes_new_replay   |
|:-------------|:----------------------------------------------------------------------------------------|:--------------------------|:------------------|:----------------------|
| A7FF-CORE38E | recompute book-objective adequacy over existing CORE33E/36E artifacts where possible    | False                     | False             | False                 |
| A7FF-CORE39  | only if CORE38E identifies book-objective survivors, write bounded book-replay contract | False                     | False             | False                 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE38E executable portfolio-label objective adequacy audit": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "same_CORE33_34_36_queue_rerun": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core38e_audit": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_READY_FOR_CORE38E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T19:49:35Z",
  "next_allowed": "A7FF-CORE38E executable portfolio-label objective adequacy audit",
  "source_decision": "PASS_A7FFCORE37X_ROUTE_ARBITRATION_READY_FOR_CORE38_CONTRACT",
  "source_stage": "A7FF-CORE37X",
  "stage": "A7FF-CORE38"
}
```
