# CRYPTO A7FF-CORE41 BOOK CONTROL REPAIR CONTRACT

Generated: 2026-06-01T20:26:38Z

## Decision

`PASS_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE41E`

CORE41 defines control repair after CORE40ER found book-objective control dominance. It does not run generation, search, large search, alpha proof, shadow, paper, or live.

## Source Objective Forensic

| objective_id                  |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio | diagnosis         |
|:------------------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|:------------------|
| B1_cross_sectional_rank_book  |           168 |              88 |                   46 |               0.0040954  |                1.56025 | control_dominated |
| B2_market_beta_residual_book  |           168 |              86 |                   47 |               0.00315561 |                1.58252 | control_dominated |
| B3_vol_adjusted_rank_book     |           168 |              87 |                   47 |               0.14006    |                1.33276 | control_dominated |
| B4_liquidity_cost_capped_book |           168 |              95 |                   50 |               0.0012116  |                1.39518 | control_dominated |

## Control Repair Policy

| policy_id                             | description                                                                                             | allowed   |
|:--------------------------------------|:--------------------------------------------------------------------------------------------------------|:----------|
| C0_stale_dominance_hard_reject        | reject objective/candidate rows where stale control absolute net return >= original absolute net return | True      |
| C1_train_only_orientation             | allow sign orientation only from train split and freeze it before OOS; no OOS/May orientation           | True      |
| C2_sign_flip_indistinguishable_reject | if original and sign_flip both survive similarly, mark as orientation-arbitrary and reject for alpha    | True      |
| C3_objective_family_reweighting       | downweight objectives with median control ratio >= 1.0; do not select solely by positive net return     | True      |
| C4_search                             | new formula generation or large search                                                                  | False     |

## Gate Contract

| gate                        | rule                                                          | hard_gate   |
|:----------------------------|:--------------------------------------------------------------|:------------|
| train_oriented_net_positive | train repaired original net > 0                               | True        |
| train_control_margin        | train repaired control_ratio < 0.8 preferred, <1.0 required   | True        |
| oos_split_balance           | >=2 OOS splits positive and control-clean                     | True        |
| orientation_arbitrary       | reject if sign-flip is equally strong after train orientation | True        |
| stale_dominance             | reject if stale control dominates original in train or OOS    | True        |
| family_breadth              | >=2 families and >=4 candidates before expansion              | True        |

## Execution Scope

| stage        | input                                                                                        | action                                                                                     | executes_new_generation   | executes_search   |
|:-------------|:---------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------|:--------------------------|:------------------|
| A7FF-CORE41E | runtime/a7ffcore40e_book_objective_replay_execution/a7ffcore40e_book_replay_all_variants.csv | apply train-only orientation and control dominance repair to existing book replay variants | False                     | False             |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE41E book control repair execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core41e_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE41E",
  "dominant_failure": "book_objective_control_dominated",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:26:38Z",
  "next_allowed": "A7FF-CORE41E book control repair execution",
  "source_decision": "PASS_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_READY_FOR_CORE41_CONTRACT",
  "source_stage": "A7FF-CORE40ER",
  "stage": "A7FF-CORE41"
}
```
