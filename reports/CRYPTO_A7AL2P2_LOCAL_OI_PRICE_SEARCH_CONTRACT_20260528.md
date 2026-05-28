# CRYPTO A7AL-2P2 Local OI-Price Search Contract

Generated: 2026-05-28T07:27:54Z

## Decision

```text
PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q
```

This is a contract only. It does not execute formula search, replay, training, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7al2p2_execution": false,
  "authorizes_a7al2q_local_execution": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "budget": {
    "authorizes_a7al2q_local_execution": true,
    "authorizes_alpha_proof": false,
    "authorizes_large_search": false,
    "deep_audit": 16,
    "generated_total": 4000,
    "scope": "local OI-price seed search only",
    "seed_count": 2,
    "selected_for_fast_replay": 128
  },
  "decision": "PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q",
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T07:27:54Z",
  "input_p1s_decision": "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN",
  "required_next": "Run A7AL-2Q local small formula-search execution only if operator/field implementation matches this contract.",
  "seed_candidates": [
    "a7al2k_046e806368e99c76",
    "a7al2k_0a247ec03472983b"
  ],
  "uses_may_for_selection": false
}
```

## Seed Candidates

| candidate_id            | expression                                                                              | fields                                | field_families       | skeleton_key              | production_key                                                                   | p1r_decision                                 | p1r_decision_from_record                     | warnings      |   control_ratio_premay_max_by_split |   latent_positive_premay_splits |   recent_turnover |
|:------------------------|:----------------------------------------------------------------------------------------|:--------------------------------------|:---------------------|:--------------------------|:---------------------------------------------------------------------------------|:---------------------------------------------|:---------------------------------------------|:--------------|------------------------------------:|--------------------------------:|------------------:|
| a7al2k_046e806368e99c76 | Sub(Abs(ZScore(Mean(open_interest_value_last,48))),Abs(ZScore(Mean(index_close,12))))   | index_close\|open_interest_value_last | open_interest\|price | skeleton-746e1c41665c2005 | a7al2k_derived_generator::derived_oi_price_state::open_interest\|price::12\|48   | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | nan           |                             0.79335 |                               3 |        0.00326183 |
| a7al2k_0a247ec03472983b | Sub(Abs(ZScore(Mean(open_interest_value_last,168))),Abs(ZScore(Mean(index_close,336)))) | index_close\|open_interest_value_last | open_interest\|price | skeleton-746e1c41665c2005 | a7al2k_derived_generator::derived_oi_price_state::open_interest\|price::168\|336 | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS | control_close |                             0.88085 |                               3 |        0.00189813 |

## Allowed Fields

| field                    | family        | role                        |
|:-------------------------|:--------------|:----------------------------|
| open_interest_last       | open_interest | primary                     |
| open_interest_mean       | open_interest | primary                     |
| open_interest_value_last | open_interest | primary                     |
| open_interest_value_mean | open_interest | primary                     |
| trade_close              | price         | primary_price               |
| mark_close               | price         | primary_price               |
| index_close              | price         | primary_price               |
| premium_close            | basis         | diagnostic_interaction_only |
| premium_close_bps        | basis         | diagnostic_interaction_only |
| mark_index_basis_bps     | basis         | diagnostic_interaction_only |
| R3_liquidity_cycle       | upper_regime  | allowed_if_lineage_clean    |
| R4_leverage_crowding     | upper_regime  | allowed_if_lineage_clean    |
| R5_basis_dislocation     | upper_regime  | allowed_if_lineage_clean    |
| R10_stress_proxy         | upper_regime  | allowed_if_lineage_clean    |

## Allowed Transforms

| transform   | status   | constraint                                             |
|:------------|:---------|:-------------------------------------------------------|
| Mean        | allowed  | past-only rolling window                               |
| Delta       | allowed  | past-only difference                                   |
| ZScore      | allowed  | cross-sectional or past-only rolling; lineage required |
| Rank        | allowed  | cross-sectional at timestamp                           |
| CSRank      | allowed  | cross-sectional at timestamp                           |
| Sub         | allowed  | bounded arithmetic                                     |
| Mul         | allowed  | two-term interaction only unless explicitly justified  |
| SafeDiv     | allowed  | finite-denominator guard required                      |
| Clip        | allowed  | fixed non-May bounds                                   |
| Winsor      | allowed  | fixed non-May bounds                                   |
| TSRank      | allowed  | past-only rolling window                               |
| Decay       | allowed  | past-only smoothing                                    |

## Forbidden Items

| item                                       | reason                                  |
|:-------------------------------------------|:----------------------------------------|
| funding-only wrapper                       | would reopen old funding residual route |
| basis/liquidity old families as standalone | A7V/A7P failure family                  |
| activity/liquidity A7V family              | source-trace-clean but signal HOLD      |
| J5 stale overlay aliases                   | canonical contract only                 |
| mark_basis_bps_okx_minus_binance           | blocked direct/raw overlay alias        |
| index_spread_bps_okx_minus_binance         | blocked direct/raw overlay alias        |
| cross-exchange direct raw price comparison | contract-unit unsafe                    |
| May-informed regime mask                   | May remains stress-only                 |
| deep nested conditionals                   | local seed search only                  |
| SignedPower                                | unbounded nonlinear transform           |
| full FormulaGenV2 open grammar             | not authorized for local contract       |

## Pass / Hold Gates

| gate                 | requirement                                          |
|:---------------------|:-----------------------------------------------------|
| no_stale_artifact    | P1S stays PASS                                       |
| control_dominance    | no control ratio >= 1.0 in any pre-May split         |
| timevarying_latent   | positive in all pre-May splits                       |
| label_alignment      | label_t1 and label_t2 positive in all pre-May splits |
| overlap_robust_stats | overlap/non-overlap stats do not collapse            |
| cost_proxy           | 2/5/10bps proxy survives                             |
| concentration        | no single symbol/month/latent state dominates        |
| skeleton_diversity   | no single skeleton > 20%                             |
| negative_controls    | attached and weaker than original                    |
| may_exclusion        | no May in selector/ranking/mutation                  |

## Boundary

```text
Authorized:
  A7AL-2Q local small formula-search execution drafting/execution

Not authorized:
  full FormulaGenV2 open grammar
  large search
  alpha proof
  shadow / paper / live
```
