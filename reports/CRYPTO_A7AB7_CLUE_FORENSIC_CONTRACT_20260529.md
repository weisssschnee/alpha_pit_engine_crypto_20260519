# CRYPTO A7AB-7 CLUE FORENSIC CONTRACT

Generated: 2026-05-29T06:24:35Z

## Decision

`PASS_A7AB7_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AB8`

A7AB-7 is a contract for forensic review of A7AB-6 clues. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ab8_clue_forensic_execution": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "clue_candidate_count": 27,
  "clue_family_count": 4,
  "clue_rows": 33,
  "clue_skeleton_count": 21,
  "decision": "PASS_A7AB7_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AB8",
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:24:35Z",
  "input_a7ab6_decision": "PASS_A7AB6_SMALL_NUMERIC_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD",
  "stage": "A7AB-7",
  "uses_may": false
}
```

## Clue Label Summary

| label_family                       |   horizon_h |   clue_rows |   clue_candidates |   median_control_ratio |   max_control_ratio |
|:-----------------------------------|------------:|------------:|------------------:|-----------------------:|--------------------:|
| L7_ranked_future_return            |           1 |          20 |                20 |               0.884617 |            0.999732 |
| L7_ranked_future_return            |           4 |           7 |                 7 |               0.828236 |            0.986254 |
| L1_cross_sectional_relative_return |           1 |           2 |                 2 |               0.891129 |            0.958687 |
| L0_raw_forward_return              |           1 |           2 |                 2 |               0.891129 |            0.958687 |
| L0_raw_forward_return              |           4 |           1 |                 1 |               0.574381 |            0.574381 |
| L1_cross_sectional_relative_return |           4 |           1 |                 1 |               0.574381 |            0.574381 |

## Clue Family Summary

| family_id                    |   clue_rows |   clue_candidates |   seed_fields |   skeletons |
|:-----------------------------|------------:|------------------:|--------------:|------------:|
| G2_basis_premium_dislocation |          13 |                 9 |             2 |           6 |
| G1_volatility_state_reversal |          10 |                 9 |             2 |           8 |
| G3_seed_pair_interaction     |           8 |                 7 |             4 |           7 |
| G0_price_return_reversal     |           2 |                 2 |             1 |           1 |

## Required Forensic Tests

| test                               | purpose                                                                          |
|:-----------------------------------|:---------------------------------------------------------------------------------|
| full_window_replay                 | rerun clue candidates on full available timestamps, not split-balanced subset    |
| nonoverlap_stats                   | report horizon-aware non-overlap tstats; naive hourly tstats cannot promote      |
| control_dominance_by_split         | wrong-lag/stale/shuffle/random controls must remain weaker in each pre-May split |
| field_native_latency               | one-bar lag survival; no artificial +2h stress policy                            |
| cost_proxy                         | 2bps/5bps/10bps proxy sensitivity                                                |
| symbol_concentration               | no single symbol or symbol tier explains the clue                                |
| month_concentration                | no single month explains the clue                                                |
| return_corr_cluster                | cluster clue return streams and cap single cluster                               |
| skeleton_and_family_diversity      | check whether clues are repeated variants of one skeleton/family                 |
| May_stress_label_only_if_available | May can only be post-selection stress/veto/failure attribution                   |

## Pass Gates

| gate                         | rule                                                                  |
|:-----------------------------|:----------------------------------------------------------------------|
| pre_may_full_window_positive | validation/test/recent oriented spread positive in full-window replay |
| control_ratio_lt_0_80        | control ratio < 0.80 preferred; >=1.00 hard HOLD                      |
| lag_survival                 | one-bar lag remains positive and >=25% of original recent spread      |
| cost_survival                | 2/5/10bps proxy does not erase all pre-May evidence                   |
| cluster_diversity            | no single return-corr cluster >35% of forensic survivors              |
| family_diversity             | no single generation family >50% of forensic survivors                |
| no_may_leakage               | May not used in ranking, threshold, selector, generation, or mutation |
