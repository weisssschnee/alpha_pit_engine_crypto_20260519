# CRYPTO A7FF-CORE53 REPLAY TARGET REPAIR CONTRACT

Generated: 2026-06-02T09:50:25Z

## Decision

`PASS_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_READY_FOR_CORE53E`

CORE53 repairs the replay target contract after CORE52F found L0/L1 top-bottom spread redundancy and thin control margins. It does not execute replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core53e_preflight": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_READY_FOR_CORE53E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T09:50:25Z",
  "required_new_target_count": 5,
  "source_decision": "HOLD_A7FFCORE52F_LABEL_REDUNDANCY_AND_THIN_CONTROL_MARGIN",
  "source_stage": "A7FF-CORE52F",
  "stage": "A7FF-CORE53",
  "target_count": 8
}
```

## Repaired Label Targets

| target_id                         | role                          | status                          | description                                                                                         | independent_for_top_bottom_spread   | promotion_role                |
|:----------------------------------|:------------------------------|:--------------------------------|:----------------------------------------------------------------------------------------------------|:------------------------------------|:------------------------------|
| T0_raw_return                     | baseline                      | allowed_baseline                | raw forward return by horizon                                                                       | True                                | baseline_only                 |
| T1_xs_relative_return             | redundant_for_decile_spread   | blocked_as_independent_evidence | cross-sectional demeaned return; top-bottom spread equals raw spread after common component removal | False                               | diagnostic_only               |
| T2_btc_eth_beta_residual_return   | market_beta_residual          | required_new_target             | future return residual after BTC/ETH or major-beta exposure removal                                 | True                                | primary_candidate_evidence    |
| T3_liquidity_tier_relative_return | liquidity_neutral_relative    | required_new_target             | future return relative to active liquidity tier peers                                               | True                                | primary_candidate_evidence    |
| T4_latent_state_relative_return   | latent_state_neutral_relative | required_new_target             | future return relative to frozen listing-age/liquidity/volatility latent state peers                | True                                | primary_candidate_evidence    |
| T5_vol_adjusted_return            | risk_scaled_return            | required_new_target             | future return divided by ex-ante realized volatility scale                                          | True                                | supporting_candidate_evidence |
| T6_ranked_future_return           | rank_label                    | diagnostic_only                 | future cross-sectional rank; cannot alone promote candidate to alpha pool                           | True                                | diagnostic_only               |
| T7_portfolio_net_spread_proxy     | book_proxy                    | required_new_target             | top-bottom book spread proxy with turnover/cost accounting fields                                   | True                                | promotion_gate                |

## Gate Policy

```json
{
  "diagnostic_clue": {
    "median_control_ratio_max": 1.0,
    "min_clean_horizon_count": 1,
    "min_clean_independent_target_count": 1,
    "requires_forensic_not_search": true
  },
  "forbidden_counting_rules": [
    "T0_raw_return and T1_xs_relative_return cannot be counted as two independent labels for top-bottom spread",
    "ranked_future_return cannot be the only positive target for alpha promotion",
    "control_ratio just below one is not sufficient without positive control margin"
  ],
  "strict_replay_clue": {
    "median_control_ratio_max": 0.9,
    "min_clean_horizon_count": 2,
    "min_clean_independent_target_count": 3,
    "min_control_ratio_max": 0.8,
    "requires_portfolio_net_spread_proxy_positive": true
  }
}
```

## Metric Schema

| column                     | required   | description                                                     |
|:---------------------------|:-----------|:----------------------------------------------------------------|
| target_id                  | True       | repaired replay target id                                       |
| horizon                    | True       | label horizon                                                   |
| original_spread_mean       | True       | top-bottom target spread                                        |
| original_tstat             | True       | hourly or non-overlap robust tstat                              |
| control_ratio              | True       | max absolute control spread divided by original absolute spread |
| control_margin             | True       | 1 - control_ratio                                               |
| independent_target_flag    | True       | whether target counts as independent evidence                   |
| portfolio_net_spread_proxy | False      | book-level net spread proxy where applicable                    |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE53E replay target builder preflight": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "candidate_promotion": true,
    "formula_search": true,
    "large_search": true,
    "shadow_paper_live": true
  }
}
```
