# CRYPTO A7AD-0 RANKED LABEL TRANSLATION CONTRACT

Generated: 2026-05-29T07:31:41Z

## Decision

`PASS_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_READY_FOR_A7AD1`

A7AD-0 defines an audit for whether A7AC ranked-return clues translate into raw or cross-sectional relative PnL proxy. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ad1_ranked_label_translation_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_READY_FOR_A7AD1",
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T07:31:41Z",
  "input_a7ac3_decision": "HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION",
  "source_candidate_count": 6,
  "source_decision_rows": 108,
  "stage": "A7AD-0",
  "uses_may": false
}
```

## Source Label Summary

| label_family                       | neutralization_mode     |   rows |   pass_rows |   candidates |
|:-----------------------------------|:------------------------|-------:|------------:|-------------:|
| L7_ranked_future_return            | meme_multiplier_neutral |     12 |          11 |            6 |
| L7_ranked_future_return            | global_rank             |     12 |          10 |            6 |
| L7_ranked_future_return            | liquidity_tier_neutral  |     12 |          10 |            6 |
| L0_raw_forward_return              | liquidity_tier_neutral  |     12 |           1 |            6 |
| L1_cross_sectional_relative_return | liquidity_tier_neutral  |     12 |           1 |            6 |
| L0_raw_forward_return              | global_rank             |     12 |           0 |            6 |
| L0_raw_forward_return              | meme_multiplier_neutral |     12 |           0 |            6 |
| L1_cross_sectional_relative_return | global_rank             |     12 |           0 |            6 |
| L1_cross_sectional_relative_return | meme_multiplier_neutral |     12 |           0 |            6 |

## Translation Tests

| test                                | definition                                                                           | required   |
|:------------------------------------|:-------------------------------------------------------------------------------------|:-----------|
| matched_label_translation           | for every L7 pass row, compare same candidate/horizon/neutralization under L0 and L1 | True       |
| raw_relative_pnl_proxy              | L0/L1 validation, test, recent oriented spreads must all be positive                 | True       |
| control_dominance_after_translation | translated L0/L1 row must have control_ratio < 1.0; >=0.80 remains warning           | True       |
| neutralization_translation          | translation must hold under at least one non-global neutralization mode              | True       |
| ranked_label_artifact_detection     | if L7 survives but L0/L1 do not, freeze as ranked-label diagnostic clue              | True       |

## Pass Gates

| gate                          | rule                                                                                    |
|:------------------------------|:----------------------------------------------------------------------------------------|
| minimum_translated_candidates | >= 2 candidates translate from L7 to L0/L1                                              |
| minimum_translated_modes      | >= 1 non-global neutralization mode has translated candidates                           |
| control_clean_translation     | translated rows must have control_ratio < 1.0                                           |
| warning_disclosure            | 0.80 <= control_ratio < 1.0 remains diagnostic-only                                     |
| no_search_authorization       | A7AD cannot authorize formula search, large search, alpha proof, shadow, paper, or live |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "contract_only",
  "experiment_id": "20260529_a7ad0_ranked_label_translation_contract",
  "inputs": {
    "a7ac3_decisions": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac3_label_diversification_diagnostic\\a7ac3_label_neutralization_decisions.csv",
    "a7ac3_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac3_label_diversification_diagnostic\\a7ac3_manifest.json"
  },
  "mode": "light_contract",
  "next_action": "A7AD-1 ranked-label translation audit",
  "objective": "Define audit for whether L7 ranked-return clues translate into raw/relative PnL proxy.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AD0_RANKED_LABEL_TRANSLATION_CONTRACT_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ad0_ranked_label_translation_contract"
  },
  "parameters": {
    "May_usage": "not used",
    "source_label": "L7_ranked_future_return",
    "translation_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return"
    ]
  },
  "status": "completed"
}
```
