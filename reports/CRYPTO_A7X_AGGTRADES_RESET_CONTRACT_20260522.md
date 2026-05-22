# Crypto A7X AggTrades Reset Contract

- generated_at: `2026-05-22T06:46:48Z`
- decision: `PASS_A7X_RESET_CONTRACT_READY`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`

## Summary

A7X freezes the current result as `data-line: PASS` and `signal-line: HOLD`. It does not revive A7V positives. It authorizes only a new objective/horizon/family reset contract for aggTrades.

A7U-0R closes raw-level source trace. A7V-6/A7V-7 still reject the current activity/liquidity clue family for promotion or expanded replay.

## Stage Freeze Matrix

| stage   | decision                                               | blockers                                                                                                                | data_line_status   | signal_line_status   | authorizes_expanded_replay   | authorizes_full_search   | authorizes_alpha_proof   | authorizes_shadow_paper_live   |
|:--------|:-------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|:-------------------|:---------------------|:-----------------------------|:-------------------------|:-------------------------|:-------------------------------|
| A7U-0R  | PASS_A7U0R_SOURCE_TRACE_COMPLETE                       |                                                                                                                         | PASS               |                      | False                        | False                    | False                    | False                          |
| A7W-0   | PASS_A7W0_SOURCE_TRACE_RESOLVED_SIGNAL_LINE_STILL_HOLD | a7v_signal_family_blocked                                                                                               |                    |                      | False                        | False                    | False                    | False                          |
| A7V-5   | PASS_A7V5_SMALL_REPLAY_SMOKE_METHOD_ONLY               |                                                                                                                         |                    |                      | False                        | False                    | False                    | False                          |
| A7V-6   | HOLD_A7V6_NO_POST_MAY_DOMINANT_CANDIDATE               | no_a7v5_positive_survives_may_stress;matched_controls_positive_for_a7v5_positives;pre_may_clues_family_concentrated     |                    | HOLD                 | False                        | False                    | False                    | False                          |
| A7V-7   | HOLD_A7V7_ACTIVITY_LIQUIDITY_CLUES_FAIL_MAY_STRESS     | all_pre_may_clues_fail_may_stress;activity_liquidity_family_concentration;matched_control_contamination_present_in_a7v6 |                    | HOLD                 | False                        | False                    | False                    | False                          |

## Weak-Prior Registry

| registry_id                                         | status                   | family                               | blocked_pattern                      | source_stage   | failure_reason                                                                                                                  | allowed_future_use                                       | disallowed_use                                                       |
|:----------------------------------------------------|:-------------------------|:-------------------------------------|:-------------------------------------|:---------------|:--------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------|:---------------------------------------------------------------------|
| weak_prior_activity_liquidity_self_reproduction_v1  | WEAK_PRIOR_DO_NOT_EXPAND | activity_liquidity_self_reproduction | Decay(agg_notional_bucket,4)         | A7V-6/A7V-7    | pre-May can look good; matched controls can be positive; all pre-May dominance clues fail May stress; family concentration high | regime_state_or_interaction_feature_only                 | standalone alpha family expansion or A7V-5 positive replay expansion |
| weak_prior_activity_liquidity_trade_count_bucket_v1 | WEAK_PRIOR_DO_NOT_EXPAND | activity_liquidity_self_reproduction | Decay(agg_trade_count_bucket,4)      | A7V-6/A7V-7    | same activity-liquidity motif as failed A7V pre-May clues                                                                       | interaction with non-May regime/horizon constraints      | standalone rolling self-reproduction clue                            |
| weak_prior_cross_symbol_activity_bucket_v1          | WEAK_PRIOR_CAPPED        | cross_symbol_activity_liquidity_rank | CrossSymbolRank(agg_notional_bucket) | A7V-6/A7V-7    | one pre-May clue survives controls but fails May; related cross-symbol positives show cost/control issues                       | symbol-tier neutralized diagnostic with matched controls | unconstrained core3 rank alpha                                       |

## New Direction Contract

| direction_id                    | objective                                                                                 | horizons          | execution_lags   | allowed_features                                                                                                                         | blocked_features                                                                                 | required_controls                                                                                       | success_is                                   |
|:--------------------------------|:------------------------------------------------------------------------------------------|:------------------|:-----------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|:---------------------------------------------|
| X2A_horizon_reset_for_aggtrades | test whether slower horizons reduce cost/lag and May-stress fragility                     | 4h;8h;12h;24h;48h | 1bar;2bar;3bar   | slow_decay;persistence;compression_expansion;relative_to_own_history                                                                     | standalone short-horizon activity/liquidity self-reproduction expansion                          | row_shuffle;time_shuffle;wrong_lag;sign_flip;matched_family_controls                                    | diagnostic improvement only, not alpha proof |
| X2B_aggtrades_state_interaction | use aggTrades as state/interactor rather than standalone signal                           | 12h;24h;48h       | 1bar;2bar        | aggTrades_x_basis;aggTrades_x_vol_compression;aggTrades_x_cross_symbol_dispersion;aggTrades_x_funding_neutral;aggTrades_x_trend_reversal | Rank(agg_notional);Decay(agg_trade_count_bucket);CrossSymbolRank(agg_bucket) as standalone alpha | standalone agg ablation;market-only ablation;matched negative controls;FundingCore/Core4 residual check | A7X_RESEARCH_CLUE only                       |
| X2C_symbol_tier_attribution     | test whether A7V failure is symbol-tier exposure mismatch rather than universal agg alpha | 12h;24h;48h       | 1bar;2bar        | major_vs_alt_state;symbol_tier_neutralization;BTC_ETH_SOL tier diagnostics                                                               | May-tuned BTC long / SOL short parameter selection                                               | non-May split validation;symbol leave-one-out;matched controls;forward-locked review before promotion   | failure hypothesis or A7X_RESEARCH_CLUE only |

## Small Experiment Spec

| parameter         | value                                                                                                                                                                                   |
|:------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| experiment_id     | 20260522_crypto_a7x_aggtrades_reset_001                                                                                                                                                 |
| objective         | small controlled diagnostic for aggTrades objective/horizon/family reset                                                                                                                |
| generated_cap     | 5000                                                                                                                                                                                    |
| strict_replay_cap | 256                                                                                                                                                                                     |
| deep_audit_cap    | 64                                                                                                                                                                                      |
| families          | F0_slow_aggtrades_horizon;F1_aggtrades_basis_interaction;F2_aggtrades_vol_compression_interaction;F3_aggtrades_cross_symbol_dispersion;F4_symbol_tier_neutralized_aggtrades;F5_controls |
| primary_cost      | 10bps                                                                                                                                                                                   |
| severe_cost       | 20bps                                                                                                                                                                                   |
| lag_stress        | 1bar;2bar;3bar                                                                                                                                                                          |
| may_policy        | post-selection stress only; not ranking/tuning/generation/allocation                                                                                                                    |
| negative_controls | row_shuffle;time_shuffle;wrong_lag;sign_flip;matched_family_controls                                                                                                                    |
| pass_label_max    | A7X_RESEARCH_CLUE                                                                                                                                                                       |
| forbidden_labels  | ALPHA_PROOF;SHADOW_READY;PAPER_READY;LIVE_READY                                                                                                                                         |
| reproducibility   | must record selected formulas, seeds, input manifests, output hashes                                                                                                                    |

## Authorization

```json
{
  "a7x3_deep_audit_cap": 64,
  "a7x3_generated_cap": 5000,
  "a7x3_strict_replay_cap": 256,
  "authorizes_a7x3_small_controlled_diagnostic": true,
  "authorizes_alpha_proof": false,
  "authorizes_expanded_replay": false,
  "authorizes_full_search": false,
  "authorizes_replay_old_a7v5_positives": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "current_a7v_activity_liquidity_family_promotable": false,
  "data_line_status": "PASS",
  "decision": "PASS_A7X_RESET_CONTRACT_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T06:46:48Z",
  "required_next": [
    "A7X-3 small controlled diagnostic under fixed cap",
    "Use aggTrades as horizon/state/interaction feature, not standalone A7V activity-liquidity expansion",
    "Preserve May stress-only policy"
  ],
  "signal_line_status": "HOLD",
  "source_trace_incomplete_caveat_removed": true
}
```

## Required Next

- Implement A7X-3 only as a small controlled diagnostic under this cap.
- Do not replay old A7V-5 positives as candidates.
- Do not use May for ranking, threshold selection, weight selection, generation, mutation, or allocation.
- Keep source trace PASS separate from signal evidence.
