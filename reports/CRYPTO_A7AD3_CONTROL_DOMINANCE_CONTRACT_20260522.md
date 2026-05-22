# CRYPTO A7AD-3 Control Dominance Contract

Generated: 2026-05-22T14:50:57Z

## Decision

```text
PASS_A7AD3_CONTROL_DOMINANCE_CONTRACT_READY
```

This stage does not run replay and does not run search. It converts A7AD-2 failures into stricter replay rules.

## Summary

```json
{
  "decision": "PASS_A7AD3_CONTROL_DOMINANCE_CONTRACT_READY",
  "executes_replay": false,
  "executes_search": false,
  "families_requiring_redesign_or_quarantine": 3,
  "generated_at": "2026-05-22T14:50:57Z",
  "output_dir": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ad3_control_dominance_contract",
  "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AD3_CONTROL_DOMINANCE_CONTRACT_20260522.md",
  "research_like_controls_from_a7ad2": 38
}
```

## Authorization

```json
{
  "authorizes_a7ad1_rerun_same_contract": false,
  "authorizes_a7ae0_candidate_redesign_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AD3_CONTROL_DOMINANCE_CONTRACT_READY"
}
```

## Family Policy Revision

| family                             | status            | reason                                                                                                    |   next_quota |
|:-----------------------------------|:------------------|:----------------------------------------------------------------------------------------------------------|-------------:|
| F0_low_turnover_price_basis        | allow_limited     | no research-like controls, but broad raw/cost/residual weakness                                           |           32 |
| F1_funding_residual_controls       | benchmark_only    | funding controls have sign/wrong-lag pass; do not promote standalone funding motifs                       |           16 |
| F2_metrics_crowding_oi_interaction | redesign_required | wrong_lag_stale_24h dominates top apparent positives; require delta/persistence/non-stale transformations |           48 |
| F3_cross_symbol_relative_strength  | redesign_required | wrong_lag controls pass at high rate; require change-based or regime-conditional variants                 |           24 |
| F4_volatility_liquidity_capped     | quarantine        | sign-flip and wrong-lag controls pass; previous liquidity/volatility collapse risk remains                |            8 |

## Control Dominance Rules

| rule_id   | rule                                          | threshold                                                                             | effect                                                                                                          |
|:----------|:----------------------------------------------|:--------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| D0        | matched_controls_required_for_every_candidate | all candidates                                                                        | candidate cannot be shortlisted without matched sign_flip,row_shuffle,time_shuffle,wrong_lag_stale_24h controls |
| D1        | wrong_lag_strict_block                        | any matched wrong_lag_stale_24h control passes validation and recent raw 10bps        | candidate and same motif are rejected for the smoke                                                             |
| D2        | sign_flip_orientation_block                   | matched sign_flip passes validation and recent raw 10bps                              | candidate family/motif is orientation-unstable; demote to diagnostic only                                       |
| D3        | control_margin                                | candidate recent robust score > max matched control score + 25pct relative margin     | candidate must materially dominate controls, not merely tie them                                                |
| D4        | stale_sensitive_feature_quarantine            | open_interest_value_zscore_168h x realized_vol/ret motifs with wrong-lag control pass | do not expand stale-sensitive OI x vol/trend motifs until redesigned                                            |

## Next Smoke Contract

| item            | value                                                                                          |
|:----------------|:-----------------------------------------------------------------------------------------------|
| scope           | A7AE-0 contract only, then A7AE-1 <= 96 candidate controlled smoke if contract passes          |
| candidate_focus | change/persistence/regime interaction variants; avoid static OI level x realized_vol dominance |
| cost_lag        | 10bps/20bps and lag0/lag1 required; lag2 diagnostic                                            |
| controls        | matched controls mandatory; wrong-lag strict block; sign-flip orientation block                |
| may_policy      | May still unavailable for core48 common window; future May is stress-only                      |
| authorization   | no formula search, no large search, no alpha proof, no shadow/paper/live                       |

## Evidence Inputs

### A7AD-2 Control Contamination

| family                             | control_mode        |   control_count |   research_like_count |   research_like_rate |
|:-----------------------------------|:--------------------|----------------:|----------------------:|---------------------:|
| F0_low_turnover_price_basis        | row_shuffle         |              42 |                     0 |            0         |
| F0_low_turnover_price_basis        | sign_flip           |              42 |                     0 |            0         |
| F0_low_turnover_price_basis        | time_shuffle        |              42 |                     0 |            0         |
| F0_low_turnover_price_basis        | wrong_lag_stale_24h |              42 |                     0 |            0         |
| F1_funding_residual_controls       | row_shuffle         |              12 |                     0 |            0         |
| F1_funding_residual_controls       | sign_flip           |              12 |                     1 |            0.0833333 |
| F1_funding_residual_controls       | time_shuffle        |              12 |                     0 |            0         |
| F1_funding_residual_controls       | wrong_lag_stale_24h |              12 |                     4 |            0.333333  |
| F2_metrics_crowding_oi_interaction | row_shuffle         |              74 |                     0 |            0         |
| F2_metrics_crowding_oi_interaction | sign_flip           |              74 |                     0 |            0         |
| F2_metrics_crowding_oi_interaction | time_shuffle        |              74 |                     0 |            0         |
| F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |              74 |                    19 |            0.256757  |
| F3_cross_symbol_relative_strength  | row_shuffle         |              12 |                     0 |            0         |
| F3_cross_symbol_relative_strength  | sign_flip           |              12 |                     0 |            0         |
| F3_cross_symbol_relative_strength  | time_shuffle        |              12 |                     0 |            0         |
| F3_cross_symbol_relative_strength  | wrong_lag_stale_24h |              12 |                     5 |            0.416667  |
| F4_volatility_liquidity_capped     | row_shuffle         |              16 |                     0 |            0         |
| F4_volatility_liquidity_capped     | sign_flip           |              16 |                     7 |            0.4375    |
| F4_volatility_liquidity_capped     | time_shuffle        |              16 |                     0 |            0         |
| F4_volatility_liquidity_capped     | wrong_lag_stale_24h |              16 |                     2 |            0.125     |

### Top Research-Like Controls

| control_id                                                                    | base_candidate_id                                        | family                             | control_mode        |   raw_validation_2025H1_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_ann_10bps_lag0 |   raw_recent_2025H2_2026Apr_sharpe_10bps_lag0 |
|:------------------------------------------------------------------------------|:---------------------------------------------------------|:-----------------------------------|:--------------------|---------------------------------------:|-------------------------------------------:|----------------------------------------------:|
| a7ad1_F2_metrics_crowding_oi_interaction_48_c8c698935a31__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_c8c698935a31 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               10.1229  |                                   31.9028  |                                      10.354   |
| a7ad1_F2_metrics_crowding_oi_interaction_48_594bcd22578e__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_594bcd22578e | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               23.7693  |                                   29.9333  |                                      13.6124  |
| a7ad1_F2_metrics_crowding_oi_interaction_48_105456a9a4c3__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_105456a9a4c3 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               10.5559  |                                   28.4878  |                                       9.5523  |
| a7ad1_F2_metrics_crowding_oi_interaction_48_e286a5ba0381__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_e286a5ba0381 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               10.5837  |                                   27.0322  |                                      13.3688  |
| a7ad1_F3_cross_symbol_relative_strength_48_c8a1eca0553f__wrong_lag_stale_24h  | a7ad1_F3_cross_symbol_relative_strength_48_c8a1eca0553f  | F3_cross_symbol_relative_strength  | wrong_lag_stale_24h |                                1.69574 |                                   19.0008  |                                      13.5239  |
| a7ad1_F4_volatility_liquidity_capped_48_c644abec893b__sign_flip               | a7ad1_F4_volatility_liquidity_capped_48_c644abec893b     | F4_volatility_liquidity_capped     | sign_flip           |                                7.16838 |                                   16.2506  |                                      10.6087  |
| a7ad1_F2_metrics_crowding_oi_interaction_48_afc30c00e56f__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_afc30c00e56f | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               14.3073  |                                   15.9591  |                                       9.41688 |
| a7ad1_F4_volatility_liquidity_capped_48_3aa22e494ac3__wrong_lag_stale_24h     | a7ad1_F4_volatility_liquidity_capped_48_3aa22e494ac3     | F4_volatility_liquidity_capped     | wrong_lag_stale_24h |                                4.08706 |                                   14.5302  |                                       9.86562 |
| a7ad1_F2_metrics_crowding_oi_interaction_48_48e6f7e4cc77__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_48e6f7e4cc77 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                9.33969 |                                   13.6303  |                                       8.84497 |
| a7ad1_F2_metrics_crowding_oi_interaction_48_713d50344766__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_713d50344766 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                5.13793 |                                   13.3156  |                                       6.29086 |
| a7ad1_F2_metrics_crowding_oi_interaction_48_2305747e3836__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_2305747e3836 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                3.08391 |                                   13.0513  |                                       5.8813  |
| a7ad1_F2_metrics_crowding_oi_interaction_48_0860c4f1ca07__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_0860c4f1ca07 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                2.895   |                                   12.324   |                                       8.71816 |
| a7ad1_F2_metrics_crowding_oi_interaction_24_594bcd22578e__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_24_594bcd22578e | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                               13.9167  |                                   11.9617  |                                       8.29339 |
| a7ad1_F2_metrics_crowding_oi_interaction_48_a0589f0c7d54__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_a0589f0c7d54 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                3.97905 |                                   11.2811  |                                       8.25121 |
| a7ad1_F3_cross_symbol_relative_strength_48_f6abf388e45c__wrong_lag_stale_24h  | a7ad1_F3_cross_symbol_relative_strength_48_f6abf388e45c  | F3_cross_symbol_relative_strength  | wrong_lag_stale_24h |                                5.88134 |                                   10.9158  |                                      11.3099  |
| a7ad1_F2_metrics_crowding_oi_interaction_24_e286a5ba0381__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_24_e286a5ba0381 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                4.26216 |                                    8.81986 |                                       6.92289 |
| a7ad1_F4_volatility_liquidity_capped_24_c644abec893b__sign_flip               | a7ad1_F4_volatility_liquidity_capped_24_c644abec893b     | F4_volatility_liquidity_capped     | sign_flip           |                                4.12539 |                                    8.38238 |                                       7.74349 |
| a7ad1_F2_metrics_crowding_oi_interaction_48_f10dc23e99f5__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_48_f10dc23e99f5 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                2.62299 |                                    8.27162 |                                       6.00743 |
| a7ad1_F2_metrics_crowding_oi_interaction_24_105456a9a4c3__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_24_105456a9a4c3 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                6.37566 |                                    8.03677 |                                       4.21966 |
| a7ad1_F2_metrics_crowding_oi_interaction_24_c8c698935a31__wrong_lag_stale_24h | a7ad1_F2_metrics_crowding_oi_interaction_24_c8c698935a31 | F2_metrics_crowding_oi_interaction | wrong_lag_stale_24h |                                5.56391 |                                    7.75143 |                                       3.80999 |

## Boundary

- Do not rerun A7AD-1 unchanged.
- Do not expand F2/F3/F4 directly.
- Do not treat static OI-level x volatility/trend motifs as research clues unless they dominate wrong-lag controls.
- A7AE-0 should redesign candidate grammar first; A7AE-1 can be a smaller controlled smoke after that.
