# CRYPTO A7AL-2X6 SMALL NUMERIC REPLAY CONTRACT

Generated: 2026-05-29T01:07:07Z

## Decision

`PASS_A7AL2X6_SMALL_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AL2X7`

This is a contract stage. It does not run replay, search, training, or proof.

## Candidate Sample Policy

| policy_key      | policy_value                                                                                |
|:----------------|:--------------------------------------------------------------------------------------------|
| input_pool      | A7AL-2X3 selected_for_family_balanced_preflight candidates only                             |
| input_gate      | requires A7AL-2X4M PASS and A7AL-2X5 PASS                                                   |
| candidate_cap   | 56 candidates max                                                                           |
| family_quota    | up to 8 candidates per F0-F6 objective family                                               |
| selection_order | family-balanced; skeleton diversity; production diversity; no May score                     |
| symbol_sample   | strict_full_history symbols, max 96 for X7 preflight                                        |
| frequency       | 1h                                                                                          |
| label           | log trade_close[t+24h] - log trade_close[t]                                                 |
| label_boundary  | label end must remain inside split                                                          |
| cost_proxy      | report 0/2/5/10 bps proxy net spread; no production cost proof                              |
| neutralization  | report original plus state-aware evaluator compatibility; full neutral replay remains later |

## Available Family Counts

| objective_family                   |   selected_available |
|:-----------------------------------|---------------------:|
| F0_OI_delta_price_interaction      |                   32 |
| F1_OI_basis_premium_interaction    |                   24 |
| F2_OI_funding_crowding_interaction |                   24 |
| F3_positioning_divergence          |                   24 |
| F4_OI_taker_flow_interaction       |                   24 |
| F5_OI_upper_regime_interaction     |                   24 |
| F6_OI_latent_state_interaction     |                   24 |

## Replay Metric Contract

| metric_or_variant    | purpose                                                   | requirement   |
|:---------------------|:----------------------------------------------------------|:--------------|
| original             | primary signal spread                                     | required      |
| one_bar_lag          | execution alignment stress                                | required      |
| wrong_lag_future_24h | lookahead/control contamination check                     | required      |
| wrong_lag_stale_168h | stale-lag/control contamination check                     | required      |
| time_shuffle         | time null                                                 | required      |
| symbol_shuffle       | cross-section null                                        | required      |
| same_family_random   | same-family random placebo                                | required      |
| overlap_disclosure   | 24h labels overlap; report naive tstat as diagnostic only | required      |
| non_overlap_offsets  | 24 offset tstats if implemented in X7                     | recommended   |

## Control Policy

| condition                                  | policy                               |
|:-------------------------------------------|:-------------------------------------|
| control_ratio >= 1.00 in any pre-May split | hard_reject                          |
| 0.80 <= control_ratio < 1.00               | warning                              |
| wrong_lag_future stronger than original    | hard_reject                          |
| wrong_lag_stale stronger than original     | hard_reject                          |
| May pass/fail in selector                  | forbidden                            |
| May stress                                 | post-selection veto/attribution only |

## Bias Audit Contract

| audit_item          | contract                                                                                                   |
|:--------------------|:-----------------------------------------------------------------------------------------------------------|
| lookahead           | feature fields must come from A7AL-2X5 materialized fields; no future rank statistics                      |
| survivorship        | X7 preflight uses strict_full_history sample only; universe498 remains current/listing-aware outside proof |
| date_alignment      | signal at t; label t to t+24h; one_bar_lag variant required                                                |
| label_horizon       | 24h overlapping label disclosed; naive tstat not promotion evidence                                        |
| transaction_cost    | bps proxy only; no production cost proof                                                                   |
| turnover            | not a tradable book; report signal turnover proxy if implemented later                                     |
| replay_vs_discovery | X7 is replay preflight from generated pool, not discovery proof                                            |

## Authorization

```json
{
  "authorizes_a7al2x7_small_numeric_replay_preflight": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_generation": false,
  "authorizes_full_numeric_replay": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AL2X6_SMALL_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AL2X7",
  "requires_x5_decision": "PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT",
  "x5_decision": "PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT"
}
```

## Boundary

```text
Authorized next:
  A7AL-2X7 small numeric replay preflight, only within this contract.

Not authorized:
  full numeric replay
  formula generation/search
  alpha proof
  shadow / paper / live
```
