# CRYPTO A7AL-2P0R Repair Rerun Decision

Generated: 2026-05-27T17:41:35Z

## Decision

```text
HOLD_A7AL2P0R_REPAIR_RERUN_BLOCKED
```

This stage reruns the repaired A7AL-2K/L/M/N/O/P0 chain after the J5 canonical overlay and silent-fallback fix. It is a repair rerun only: no training, no search execution, no alpha proof.

## Manifest

```json
{
  "a7al2k_generated_candidates": 8000,
  "a7al2k_selected_for_replay": 768,
  "a7al2l_clue_count": 3,
  "a7al2l_replay_cap": 64,
  "a7al2m_deep_audit_candidate_count": 1,
  "a7al2n_diagnostic_pass_count": 1,
  "a7al2o_diagnostic_pass_count": 1,
  "a7al2p0_decision": "HOLD_A7AL2P0_PRE_SEARCH_HARDENING_BLOCKERS",
  "a7ar5_contract_decision": "HOLD_A7AR5_REPLAY_SELECTOR_NOT_AUTHORIZED",
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "timevarying_latent_neutralization_fragile"
  ],
  "canonical_alias_code_fail": false,
  "decision": "HOLD_A7AL2P0R_REPAIR_RERUN_BLOCKED",
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-27T17:41:35Z",
  "premay_control_hold_count": 0,
  "required_next": "repair selector/neutralization or regenerate candidate pool; do not run A7AL-2 formula search",
  "rerun_scope": "A7AL-2K/L/M/N/O/P0 repaired chain",
  "stale_alias_artifact_count": 0,
  "timevarying_latent_negative_premay_rows": 2,
  "warnings": [
    "overlap_adjusted_recent_tstat_below_2_for_some_candidates"
  ]
}
```

## Stage Summary

| stage                               | decision                                                        | generated_at         | blockers                                  | warnings                                                       | authorizes_formula_search_execution   | authorizes_alpha_proof   |
|:------------------------------------|:----------------------------------------------------------------|:---------------------|:------------------------------------------|:---------------------------------------------------------------|:--------------------------------------|:-------------------------|
| A7AL-2K repaired generator smoke    | PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L            | 2026-05-27T16:45:04Z |                                           |                                                                | False                                 | False                    |
| A7AL-2L fast replay preflight rerun | PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD | 2026-05-27T17:35:24Z |                                           | control_dominated_candidates_rejected                          | False                                 | False                    |
| A7AL-2M clue forensic rerun         | PASS_A7AL2M_DERIVED_CLUE_POOL_READY_FOR_DEEP_AUDIT              | 2026-05-27T17:35:34Z |                                           | stress_divergent_clues_present\|field_family_diversity_below_4 | False                                 | False                    |
| A7AL-2N deep audit rerun            | PASS_A7AL2N_DEEP_AUDIT_DIAGNOSTIC_CANDIDATES_FOUND              | 2026-05-27T17:35:48Z |                                           |                                                                | False                                 | False                    |
| A7AL-2O mini replay rerun           | PASS_A7AL2O_MINI_REPLAY_CANDIDATES_READY_FOR_CONTRACT           | 2026-05-27T17:36:30Z |                                           |                                                                | False                                 | False                    |
| A7AL-2P0 hardening audit rerun      | HOLD_A7AL2P0_PRE_SEARCH_HARDENING_BLOCKERS                      | 2026-05-27T17:38:38Z | timevarying_latent_neutralization_fragile | overlap_adjusted_recent_tstat_below_2_for_some_candidates      | False                                 | False                    |

## Canonical Alias Result

| field_name                                             | field_class                            | present_in_generator_code   | status   |
|:-------------------------------------------------------|:---------------------------------------|:----------------------------|:---------|
| binance_index_close                                    | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| binance_internal_mark_index_basis_bps                  | canonical_allowed_overlay              | True                        | PASS     |
| binance_mark_close                                     | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| binance_trade_close                                    | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| funding_spread_okx_minus_binance                       | canonical_allowed_overlay              | True                        | PASS     |
| index_spread_bps_okx_minus_binance                     | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| mark_basis_bps_okx_minus_binance                       | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| oi_coin_ratio_okx_over_binance                         | canonical_allowed_overlay              | True                        | PASS     |
| oi_usd_ratio_okx_over_binance                          | canonical_allowed_overlay              | True                        | PASS     |
| oi_usd_spread_okx_minus_binance                        | canonical_allowed_overlay              | True                        | PASS     |
| oi_value_ratio_from_crowding_endpoint_okx_over_binance | canonical_allowed_overlay              | True                        | PASS     |
| okx_contracts_taker_buy_sell_ratio                     | canonical_allowed_overlay              | True                        | PASS     |
| okx_contracts_taker_buy_share                          | canonical_allowed_overlay              | True                        | PASS     |
| okx_index_close                                        | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| okx_internal_mark_index_basis_bps                      | canonical_allowed_overlay              | True                        | PASS     |
| okx_mark_close                                         | blocked_direct_or_raw_price_comparison | False                       | PASS     |
| taker_ratio_spread_okx_minus_binance                   | canonical_allowed_overlay              | True                        | PASS     |
| J5_silent_fallback_to_J0                               | silent_fallback                        | False                       | PASS     |

Stale blocked-alias artifacts after rerun:

```text
0
```

## Matched-Control Hard Gate

Premay HOLD rows:

`<empty>`

## Time-Varying Latent Neutralization

Premay negative/zero rows:

| candidate_id            | variant                          | entry_label     | split                 |   n_dates |   mean_oriented_spread |   hourly_tstat_naive |   positive_rate |
|:------------------------|:---------------------------------|:----------------|:----------------------|----------:|-----------------------:|---------------------:|----------------:|
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000646225 |            -3.31291  |        0.481593 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.000103753 |            -0.335747 |        0.520841 |

## A7AR-5 Replay-Aware Selector

```json
{
  "allowed_use": [
    "diagnostic candidate ordering",
    "pre-search selector implementation audit",
    "A7AL-2P contract drafting input after all hard blockers are cleared"
  ],
  "blockers": [
    "timevarying_latent_neutralization_fragile"
  ],
  "contract_name": "A7AR-5 replay-aware selector adapter",
  "decision": "HOLD_A7AR5_REPLAY_SELECTOR_NOT_AUTHORIZED",
  "forbidden_inputs": [
    "May score",
    "May ranking",
    "May threshold tuning",
    "May weight selection",
    "May generator tuning",
    "May selector score",
    "shadow/paper/live promotion labels"
  ],
  "generated_at": "2026-05-27T17:38:38Z",
  "hard_gate_status": {
    "candidate_eval": "PASS",
    "canonical_field_alias_code": "PASS",
    "matched_control_dominance": "PASS",
    "timevarying_latent_neutralization": "HOLD"
  },
  "hard_gates": {
    "canonical_contract_unit_fields_only": true,
    "j5_overlay_silent_fallback_forbidden": true,
    "label_entry_alignment_required": [
      "label_t_to_t24",
      "label_t1_to_t25",
      "label_t2_to_t26"
    ],
    "overlap_robust_stats_required": [
      "newey_west_lag24",
      "block_bootstrap_block24",
      "nonoverlap_offset_tstats"
    ],
    "split_control_ratio_0_80_to_1_00": "WARN_CONTROL_CLOSE",
    "split_control_ratio_gte_1_00": "HOLD_CONTROL_DOMINATED",
    "timevarying_latent_state_neutralization_required": true
  },
  "not_authorized": [
    "A7AL-2 formula search execution",
    "alpha proof",
    "shadow",
    "paper",
    "live"
  ],
  "score_components_no_may": [
    "non_may_original_spread",
    "entry_shift_aligned_spread_label_t1_to_t25",
    "matched_control_dominance_margin_by_split",
    "one_bar_lag_survival_recent",
    "timevarying_latent_neutralization_survival",
    "cost_proxy_placeholder_from_replay_family",
    "family_skeleton_cell_diversity"
  ],
  "status": "DRY_ADAPTER_ONLY",
  "top_dry_selector_candidates": [
    {
      "candidate_id": "a7al2k_01759e5da72c472c",
      "cell": "J4_upper_regime_interaction",
      "control_dominance_margin": 0.03581679097228696,
      "family": "derived_upper_regime_proxy",
      "non_may_original_spread_score": 0.002047623251922958,
      "one_bar_lag_survival_recent": 0.9815500034166228,
      "replay_aware_selector_score_no_may": 0.0021634700073118705,
      "timevarying_latent_positive_premay_splits": 1
    }
  ],
  "warnings": [
    "overlap_adjusted_recent_tstat_below_2_for_some_candidates"
  ]
}
```

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
