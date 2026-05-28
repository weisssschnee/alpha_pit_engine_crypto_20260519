# CRYPTO A7AL-2P1T Repaired Pool Rerun Status

Generated: 2026-05-28T02:40:45Z

## Decision

```text
HOLD_A7AL2P1T_REPAIRED_POOL_NO_SELECTOR_ELIGIBLE_CANDIDATES
```

This status record freezes the repaired current A7AL-2K/L/P1/P1R rerun. It supersedes the stale two-candidate P1/P1R selector pool for downstream authorization.

## Manifest

```json
{
  "a7al2k_generated_at": "2026-05-28T01:45:32Z",
  "a7al2k_generated_candidates": 8000,
  "a7al2k_selected_for_replay": 768,
  "a7al2l_clue_count": 3,
  "a7al2l_generated_at": "2026-05-28T02:32:25Z",
  "a7al2l_replay_cap": 64,
  "a7al2p1_candidate_count": 3,
  "a7al2p1_decision_counts": {
    "HOLD_CONTROL_DOMINATED": 2,
    "HOLD_TIMEVARYING_LATENT_FRAGILE": 1
  },
  "a7al2p1_generated_at": "2026-05-28T02:37:26Z",
  "a7al2p1_selector_eligible_count": 0,
  "a7al2p1r_decision": "HOLD_A7AL2P1R_NO_SELECTOR_ELIGIBLE_CANDIDATES",
  "a7al2p1r_diagnostic_pass_count": 0,
  "a7al2p1r_generated_at": "2026-05-28T02:38:13Z",
  "authorizes_a7al2p2": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_selector_eligible_candidates_after_repaired_pool_rerun"
  ],
  "decision": "HOLD_A7AL2P1T_REPAIRED_POOL_NO_SELECTOR_ELIGIBLE_CANDIDATES",
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T02:40:45Z",
  "required_next": "regenerate or adjust non-May selector/generator with time-varying latent survival and control dominance earlier in selection; do not draft A7AL-2P2 from the old P1/P1R pool"
}
```

## Stage Summary

| stage                                                 | decision                                                        | generated_at         |   generated_candidates |   selected_or_replayed_candidates |   candidate_count |   clue_count |   selector_eligible_count |   diagnostic_pass_count | blockers                                               | warnings                              | authorizes_formula_search_execution   | authorizes_alpha_proof   |
|:------------------------------------------------------|:----------------------------------------------------------------|:---------------------|-----------------------:|----------------------------------:|------------------:|-------------:|--------------------------:|------------------------:|:-------------------------------------------------------|:--------------------------------------|:--------------------------------------|:-------------------------|
| A7AL-2K repaired current generated pool               | PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L            | 2026-05-28T01:45:32Z |                   8000 |                               768 |                   |              |                           |                         |                                                        |                                       | False                                 | False                    |
| A7AL-2L repaired current 64-cap replay preflight      | PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD | 2026-05-28T02:32:25Z |                        |                                64 |                   |            3 |                           |                         |                                                        | control_dominated_candidates_rejected | False                                 | False                    |
| A7AL-2P1 selector feature generation on repaired pool | HOLD_A7AL2P1_SELECTOR_FEATURES_BLOCKED                          | 2026-05-28T02:37:26Z |                        |                                   |                 3 |              |                         0 |                         | no_selector_candidate_survives_timevarying_latent_gate | selector_eligible_pool_below_2        | False                                 | False                    |
| A7AL-2P1R selector-reweighted retry                   | HOLD_A7AL2P1R_NO_SELECTOR_ELIGIBLE_CANDIDATES                   | 2026-05-28T02:38:13Z |                        |                                   |                 0 |              |                           |                       0 | no_selector_eligible_candidates                        |                                       | False                                 | False                    |

## Repaired A7AL-2L Clue Pool

| candidate_id            | decision                             | cell                        | family                     | field_families           | fields                                 |   control_dominance_ratio_premay_max |   one_bar_lag_recent_spread |
|:------------------------|:-------------------------------------|:----------------------------|:---------------------------|:-------------------------|:---------------------------------------|-------------------------------------:|----------------------------:|
| a7al2k_0096829c83c908a8 | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE | J4_upper_regime_interaction | derived_upper_regime_proxy | liquidity\|open_interest | open_interest_value_mean\|trade_volume |                             1.05137  |                 -0.00219818 |
| a7al2k_01bdc8d049fffe52 | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE | J4_upper_regime_interaction | derived_upper_regime_proxy | liquidity\|open_interest | open_interest_value_last\|trade_volume |                             1.22977  |                 -0.00266342 |
| a7al2k_01759e5da72c472c | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE | J4_upper_regime_interaction | derived_upper_regime_proxy | basis\|liquidity         | premium_close\|trade_count             |                             0.946342 |                 -0.00191405 |

## P1 Selector Decisions

| candidate_id            | selector_decision               | latent_gate                     | matched_control_gate   |   control_ratio_premay_max_by_split |   latent_positive_premay_splits | field_families           | expression                                                                 |
|:------------------------|:--------------------------------|:--------------------------------|:-----------------------|------------------------------------:|--------------------------------:|:-------------------------|:---------------------------------------------------------------------------|
| a7al2k_01bdc8d049fffe52 | HOLD_CONTROL_DOMINATED          | PASS                            | HOLD_CONTROL_DOMINATED |                            1.22977  |                               3 | liquidity\|open_interest | Mul(Rank(Mean(trade_volume,48)),Rank(Mean(open_interest_value_last,48)))   |
| a7al2k_01759e5da72c472c | HOLD_TIMEVARYING_LATENT_FRAGILE | HOLD_TIMEVARYING_LATENT_FRAGILE | PASS                   |                            0.946342 |                               1 | basis\|liquidity         | Mul(Abs(ZScore(Mean(premium_close,720))),Rank(Mean(trade_count,720)))      |
| a7al2k_0096829c83c908a8 | HOLD_CONTROL_DOMINATED          | PASS                            | HOLD_CONTROL_DOMINATED |                            1.05137  |                               3 | liquidity\|open_interest | Mul(Rank(Mean(trade_volume,168)),Rank(Mean(open_interest_value_mean,504))) |

## Boundary

```text
Authorized:
  none

Not authorized:
  A7AL-2P2 local search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
