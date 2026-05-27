# CRYPTO A7AL-2P0 Pre-Search Implementation Hardening Audit

Generated: 2026-05-27T15:59:08Z

## Decision

```text
HOLD_A7AL2P0_PRE_SEARCH_HARDENING_BLOCKERS
```

This stage fixes/audits implementation risks before any A7AL-2 search contract. It executes no training, no generation, no search, and no alpha proof.

## Manifest

```json
{
  "a7ar5_contract_decision": "HOLD_A7AR5_REPLAY_SELECTOR_NOT_AUTHORIZED",
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "matched_control_dominance_hard_gate_fail",
    "timevarying_latent_neutralization_fragile"
  ],
  "candidate_count": 4,
  "decision": "HOLD_A7AL2P0_PRE_SEARCH_HARDENING_BLOCKERS",
  "eval_errors": 0,
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-27T15:59:08Z",
  "p0_1_label_alignment": "computed label_t_to_t24, label_t1_to_t25, label_t2_to_t26",
  "p0_2_canonical_alias": "generator code patched; stale generated artifacts audited separately",
  "p0_3_control_gate": "control_ratio >= 1.00 is HOLD by split",
  "p0_4_overlap_stats": "hourly naive, 24h non-overlap offset, Newey-West lag24, block bootstrap block24",
  "p0_5_timevarying_latent": {
    "loaded_rows": 3692531,
    "state_non_missing_share": 0.9703079075817397,
    "state_panel_path": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_latent_state_features_v1_20260527.parquet",
    "state_seen_in_train_share": 0.7661959913546751
  },
  "p0_6_replay_selector": "A7AR-5 dry replay-aware selector contract and score generated without May",
  "warnings": [
    "stale_a7al2k_artifacts_contain_blocked_overlay_aliases_rerun_required_before_j5_use",
    "overlap_adjusted_recent_tstat_below_2_for_some_candidates"
  ]
}
```

## P0-1 Label / Execution Alignment

| candidate_id            | entry_label     |   recent_oos_2026JanApr |   test_2025H2 |   validation_2025H1 |   premay_positive_splits |
|:------------------------|:----------------|------------------------:|--------------:|--------------------:|-------------------------:|
| a7al2k_01298a6b5902f416 | label_t1_to_t25 |              0.00157023 |    0.00175429 |         0.000820954 |                        3 |
| a7al2k_01298a6b5902f416 | label_t2_to_t26 |              0.00153853 |    0.00177241 |         0.000814914 |                        3 |
| a7al2k_01298a6b5902f416 | label_t_to_t24  |              0.00159322 |    0.00174322 |         0.000830232 |                        3 |
| a7al2k_01759e5da72c472c | label_t1_to_t25 |              0.00190364 |    0.00301923 |         0.00122     |                        3 |
| a7al2k_01759e5da72c472c | label_t2_to_t26 |              0.00185833 |    0.00298896 |         0.00121318  |                        3 |
| a7al2k_01759e5da72c472c | label_t_to_t24  |              0.00195588 |    0.00303946 |         0.00123838  |                        3 |
| a7al2k_0cf817ef95787b3d | label_t1_to_t25 |              0.00367393 |    0.00445109 |         0.00209874  |                        3 |
| a7al2k_0cf817ef95787b3d | label_t2_to_t26 |              0.00355462 |    0.00443631 |         0.00211132  |                        3 |
| a7al2k_0cf817ef95787b3d | label_t_to_t24  |              0.00379066 |    0.00449646 |         0.0020818   |                        3 |
| a7al2k_134ec76b5d7444f9 | label_t1_to_t25 |              0.00210217 |    0.00418307 |         0.00214829  |                        3 |
| a7al2k_134ec76b5d7444f9 | label_t2_to_t26 |              0.00204434 |    0.0041909  |         0.00215281  |                        3 |
| a7al2k_134ec76b5d7444f9 | label_t_to_t24  |              0.00218342 |    0.00418491 |         0.00214053  |                        3 |

## P0-2 Canonical Field Alias Audit

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

Stale generated artifacts with blocked aliases:

| candidate_id            | cell                                 | blocked_fields                     | selected_for_replay   | diagnostic_only   |
|:------------------------|:-------------------------------------|:-----------------------------------|:----------------------|:------------------|
| a7al2k_8566908147354507 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_820565a34ebdab62 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_de5587efc438d6df | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_8f72cfa01525b90d | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_f292b2580ce110a3 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_80af3e68820c499c | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_8b759d54f81e8ef3 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_a7516a15ce9426b2 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_bc19b279763b7bd3 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_f9dae4c1827c0906 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_38b06e3de952c815 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_9220b43ce9792266 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_dc65abbb752165a2 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_c11dae05c2a7eb86 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_91214351cced6818 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_0f63fd61590d2597 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_2c059626900976fa | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_cecfe9f8db239732 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_5ee353fbe435526c | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_ea384098e3a385a4 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_0d0564dd5eee506e | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_537ac523a404c318 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_8106b7936c298450 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_4855fcc1806affe7 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_a6bd532222353f35 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_0576a93c243be4a5 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_8bc968c864364152 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_c5a0457d0840119f | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_0d61a4e9741c14b0 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_b29771d39ab5b14c | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_28ad2e60e408781f | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_a09b7c3ed6cc60ae | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_6630271895d080e0 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_2a0c88de489486a4 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_9b7ecc6947166123 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_6dbce834ca25c29e | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_359882248004e102 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |
| a7al2k_7230f83303f16c0c | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_41f69c47f2ae6088 | J5_cross_exchange_overlay_diagnostic | index_spread_bps_okx_minus_binance | False                 | True              |
| a7al2k_5fd980caffdc1e08 | J5_cross_exchange_overlay_diagnostic | mark_basis_bps_okx_minus_binance   | False                 | True              |

## P0-3 Matched-Control Hard Gate

| candidate_id            | entry_label     | split                 |   original_abs_spread |   max_control_abs_spread |   control_ratio | gate                   |
|:------------------------|:----------------|:----------------------|----------------------:|-------------------------:|----------------:|:-----------------------|
| a7al2k_01298a6b5902f416 | label_t1_to_t25 | recent_oos_2026JanApr |           0.00157023  |              0.000635254 |        0.404561 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01298a6b5902f416 | label_t1_to_t25 | test_2025H2           |           0.00175429  |              0.00135868  |        0.774488 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01298a6b5902f416 | label_t1_to_t25 | validation_2025H1     |           0.000820954 |              0.000552273 |        0.672721 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01759e5da72c472c | label_t1_to_t25 | recent_oos_2026JanApr |           0.00190364  |              0.00151136  |        0.793932 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01759e5da72c472c | label_t1_to_t25 | test_2025H2           |           0.00301923  |              0.000833588 |        0.276093 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_01759e5da72c472c | label_t1_to_t25 | validation_2025H1     |           0.00122     |              0.0011763   |        0.964183 | WARN_CONTROL_CLOSE     |
| a7al2k_0cf817ef95787b3d | label_t1_to_t25 | recent_oos_2026JanApr |           0.00367393  |              0.000609805 |        0.165982 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_0cf817ef95787b3d | label_t1_to_t25 | test_2025H2           |           0.00445109  |              0.00377951  |        0.849122 | WARN_CONTROL_CLOSE     |
| a7al2k_0cf817ef95787b3d | label_t1_to_t25 | validation_2025H1     |           0.00209874  |              0.00218032  |        1.03887  | HOLD_CONTROL_DOMINATED |
| a7al2k_134ec76b5d7444f9 | label_t1_to_t25 | recent_oos_2026JanApr |           0.00210217  |              0.00143979  |        0.684905 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_134ec76b5d7444f9 | label_t1_to_t25 | test_2025H2           |           0.00418307  |              0.00330939  |        0.791139 | ELIGIBLE_DIAGNOSTIC    |
| a7al2k_134ec76b5d7444f9 | label_t1_to_t25 | validation_2025H1     |           0.00214829  |              0.00228163  |        1.06207  | HOLD_CONTROL_DOMINATED |

## P0-4 Overlap-Robust Statistics

| candidate_id            | split                 |   n_dates |   mean_spread |   hourly_tstat_naive |   newey_west_tstat_lag24 |   block_bootstrap_tstat_block24 |
|:------------------------|:----------------------|----------:|--------------:|---------------------:|-------------------------:|--------------------------------:|
| a7al2k_01759e5da72c472c | validation_2025H1     |      4319 |   0.00122     |              5.7764  |                  1.47909 |                         1.56412 |
| a7al2k_01759e5da72c472c | test_2025H2           |      4391 |   0.00301923  |             12.5774  |                  3.18004 |                         3.41653 |
| a7al2k_01759e5da72c472c | recent_oos_2026JanApr |      2855 |   0.00190364  |              6.76678 |                  1.74554 |                         1.7696  |
| a7al2k_01759e5da72c472c | known_may2026_stress  |       575 |   0.00336897  |              5.59785 |                  1.43654 |                         1.3422  |
| a7al2k_0cf817ef95787b3d | validation_2025H1     |      4319 |   0.00209874  |              9.52951 |                  2.57942 |                         2.57719 |
| a7al2k_0cf817ef95787b3d | test_2025H2           |      4391 |   0.00445109  |             18.0894  |                  4.6196  |                         4.55516 |
| a7al2k_0cf817ef95787b3d | recent_oos_2026JanApr |      2855 |   0.00367393  |             11.1618  |                  2.80572 |                         2.84888 |
| a7al2k_0cf817ef95787b3d | known_may2026_stress  |       575 |   0.00634339  |             11.9164  |                  3.257   |                         3.15453 |
| a7al2k_134ec76b5d7444f9 | validation_2025H1     |      4319 |   0.00214829  |              8.86527 |                  2.23093 |                         2.26221 |
| a7al2k_134ec76b5d7444f9 | test_2025H2           |      4391 |   0.00418307  |             19.4332  |                  4.91557 |                         4.9673  |
| a7al2k_134ec76b5d7444f9 | recent_oos_2026JanApr |      2855 |   0.00210217  |              7.3161  |                  1.85656 |                         1.73723 |
| a7al2k_134ec76b5d7444f9 | known_may2026_stress  |       575 |   0.00381141  |              8.97568 |                  2.58884 |                         2.52    |
| a7al2k_01298a6b5902f416 | validation_2025H1     |      4319 |   0.000820954 |              3.94194 |                  0.98828 |                         1.04129 |
| a7al2k_01298a6b5902f416 | test_2025H2           |      4391 |   0.00175429  |              9.76583 |                  2.61868 |                         2.86004 |
| a7al2k_01298a6b5902f416 | recent_oos_2026JanApr |      2855 |   0.00157023  |              6.40007 |                  1.63311 |                         1.76816 |
| a7al2k_01298a6b5902f416 | known_may2026_stress  |       575 |   0.00174813  |              5.12639 |                  1.54708 |                         1.59777 |

## P0-5 Time-Varying Latent Neutralization

| candidate_id            | variant                          | entry_label     | split                 |   n_dates |   mean_oriented_spread |   hourly_tstat_naive |   positive_rate |
|:------------------------|:---------------------------------|:----------------|:----------------------|----------:|-----------------------:|---------------------:|----------------:|
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000646225 |            -3.31291  |        0.481593 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00144539  |             7.3808   |        0.545206 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.000103753 |            -0.335747 |        0.520841 |
| a7al2k_01759e5da72c472c | timevarying_latent_state_neutral | label_t1_to_t25 | known_may2026_stress  |         0 |          nan           |           nan        |      nan        |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000862595 |            -4.17606  |        0.50081  |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00167556  |             9.63823  |        0.567752 |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.00118772  |             4.29492  |        0.569177 |
| a7al2k_0cf817ef95787b3d | timevarying_latent_state_neutral | label_t1_to_t25 | known_may2026_stress  |         0 |          nan           |           nan        |      nan        |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |            0.000892006 |             4.03076  |        0.535772 |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |            0.00118454  |             6.95537  |        0.564564 |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |           -0.000192527 |            -0.696498 |        0.49352  |
| a7al2k_134ec76b5d7444f9 | timevarying_latent_state_neutral | label_t1_to_t25 | known_may2026_stress  |         0 |          nan           |           nan        |      nan        |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | validation_2025H1     |      4319 |           -0.000585113 |            -3.32559  |        0.497337 |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | test_2025H2           |      4391 |           -0.000294195 |            -1.51284  |        0.50353  |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | recent_oos_2026JanApr |      2855 |            0.000352243 |             1.35432  |        0.541506 |
| a7al2k_01298a6b5902f416 | timevarying_latent_state_neutral | label_t1_to_t25 | known_may2026_stress  |         0 |          nan           |           nan        |      nan        |

## P0-6 Replay-Aware Selector Dry Components

| candidate_id            |   non_may_original_spread_score | entry_shift_aligned_label   |   one_bar_lag_survival_recent |   control_dominance_margin |   timevarying_latent_positive_premay_splits | family                      | cell                        | field_families   |   replay_aware_selector_score_no_may | uses_may   |
|:------------------------|--------------------------------:|:----------------------------|------------------------------:|---------------------------:|--------------------------------------------:|:----------------------------|:----------------------------|:-----------------|-------------------------------------:|:-----------|
| a7al2k_0cf817ef95787b3d |                      0.00340792 | label_t1_to_t25             |                      0.967108 |                 -0.0388687 |                                           2 | derived_upper_regime_proxy  | J4_upper_regime_interaction | basis\|liquidity |                           0.00366426 | False      |
| a7al2k_134ec76b5d7444f9 |                      0.00281118 | label_t1_to_t25             |                      0.971546 |                 -0.0620673 |                                           2 | derived_liquidity_lifecycle | J2_liquidity_lifecycle      | liquidity\|price |                           0.0030535  | False      |
| a7al2k_01759e5da72c472c |                      0.00204762 | label_t1_to_t25             |                      0.98155  |                  0.0358168 |                                           1 | derived_upper_regime_proxy  | J4_upper_regime_interaction | basis\|liquidity |                           0.00216347 | False      |
| a7al2k_01298a6b5902f416 |                      0.00138182 | label_t1_to_t25             |                      0.984298 |                  0.225512  |                                           1 | derived_oi_price_state      | J0_oi_derived_state         | open_interest    |                           0.00163183 | False      |

## A7AR-5 Replay-Aware Selector Contract

```json
{
  "allowed_use": [
    "diagnostic candidate ordering",
    "pre-search selector implementation audit",
    "A7AL-2P contract drafting input after all hard blockers are cleared"
  ],
  "blockers": [
    "matched_control_dominance_hard_gate_fail",
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
  "generated_at": "2026-05-27T15:59:08Z",
  "hard_gate_status": {
    "candidate_eval": "PASS",
    "canonical_field_alias_code": "PASS",
    "matched_control_dominance": "HOLD",
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
      "candidate_id": "a7al2k_0cf817ef95787b3d",
      "cell": "J4_upper_regime_interaction",
      "control_dominance_margin": -0.0388686504706397,
      "family": "derived_upper_regime_proxy",
      "non_may_original_spread_score": 0.003407917840936718,
      "one_bar_lag_survival_recent": 0.967108310046891,
      "replay_aware_selector_score_no_may": 0.0036642639406307166,
      "timevarying_latent_positive_premay_splits": 2
    },
    {
      "candidate_id": "a7al2k_134ec76b5d7444f9",
      "cell": "J2_liquidity_lifecycle",
      "control_dominance_margin": -0.062067289623535915,
      "family": "derived_liquidity_lifecycle",
      "non_may_original_spread_score": 0.002811178997600509,
      "one_bar_lag_survival_recent": 0.971546179276137,
      "replay_aware_selector_score_no_may": 0.003053504984502102,
      "timevarying_latent_positive_premay_splits": 2
    },
    {
      "candidate_id": "a7al2k_01759e5da72c472c",
      "cell": "J4_upper_regime_interaction",
      "control_dominance_margin": 0.03581679097228696,
      "family": "derived_upper_regime_proxy",
      "non_may_original_spread_score": 0.002047623251922958,
      "one_bar_lag_survival_recent": 0.9815500034166228,
      "replay_aware_selector_score_no_may": 0.0021634700073118705,
      "timevarying_latent_positive_premay_splits": 1
    },
    {
      "candidate_id": "a7al2k_01298a6b5902f416",
      "cell": "J0_oi_derived_state",
      "control_dominance_margin": 0.22551241768568242,
      "family": "derived_oi_price_state",
      "non_may_original_spread_score": 0.0013818245587966403,
      "one_bar_lag_survival_recent": 0.984298095607153,
      "replay_aware_selector_score_no_may": 0.0016318322989801945,
      "timevarying_latent_positive_premay_splits": 1
    }
  ],
  "warnings": [
    "stale_a7al2k_artifacts_contain_blocked_overlay_aliases_rerun_required_before_j5_use",
    "overlap_adjusted_recent_tstat_below_2_for_some_candidates"
  ]
}
```

## Boundary

```text
Not authorized:
  A7AL-2 execution
  formula search execution
  alpha proof
  shadow / paper / live
```
