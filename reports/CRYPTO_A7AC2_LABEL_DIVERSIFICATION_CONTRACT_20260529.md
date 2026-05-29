# CRYPTO A7AC-2 LABEL DIVERSIFICATION CONTRACT

Generated: 2026-05-29T06:55:43Z

## Decision

`PASS_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_READY_FOR_A7AC3`

A7AC-2 defines a bounded label-diversification and neutralization diagnostic for A7AC-1R representatives. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ac3_label_diversification_diagnostic": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_READY_FOR_A7AC3",
  "diagnostic_candidates": 6,
  "diagnostic_clusters": 7,
  "diagnostic_label_families": 1,
  "diagnostic_rows": 7,
  "executes_contract_only": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T06:55:43Z",
  "input_a7ac1r_decision": "PASS_A7AC1R_DIAGNOSTIC_SUBSET_FROZEN_READY_FOR_A7AC2_WITH_WARNINGS",
  "quarantined_rows": 1,
  "required_label_count": 3,
  "required_neutralization_count": 4,
  "stage": "A7AC-2",
  "uses_may": false
}
```

## Source Summary

| source                              | path                                                                                                                                                  |   rows |   candidates |   clusters |   label_families |
|:------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------|-------:|-------------:|-----------:|-----------------:|
| A7AC-1R diagnostic subset           | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ac1r_representative_quarantine_contract\a7ac1r_diagnostic_representative_subset.csv |      7 |            6 |          7 |                1 |
| A7AC-1R quarantined representatives | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ac1r_representative_quarantine_contract\a7ac1r_quarantined_representatives.csv      |      1 |            1 |          1 |                1 |

## Label Family Contract

| label_family                       | role                                              | horizons   | required   | promotion_role                              |
|:-----------------------------------|:--------------------------------------------------|:-----------|:-----------|:--------------------------------------------|
| L0_raw_forward_return              | raw return sanity check                           | 1\|4       | True       | diagnostic_only_unless_neutral_survives     |
| L1_cross_sectional_relative_return | market-mean relative return                       | 1\|4       | True       | minimum non-ranked diversification target   |
| L7_ranked_future_return            | current survivor label; must not be sole evidence | 1\|4       | True       | cannot promote alone                        |
| L2_btc_eth_residual_return         | BTC/ETH beta residual label                       | 1\|4       | False      | secondary if local implementation available |
| L3_liquidity_tier_relative_return  | liquidity-tier relative label                     | 1\|4       | False      | secondary if local implementation available |
| L4_latent_state_relative_return    | time-varying latent-state relative label          | 1\|4       | False      | secondary if local implementation available |

## Neutralization Contract

| neutralization_mode     | required   |   minimum_group_symbols | fallback               | purpose                                                         |
|:------------------------|:-----------|------------------------:|:-----------------------|:----------------------------------------------------------------|
| global_rank             | True       |                      30 | none                   | baseline cross-sectional top/bottom construction                |
| liquidity_tier_neutral  | True       |                       8 | global_rank            | separate signal from liquidity tier bias                        |
| latent_state_neutral    | True       |                       8 | liquidity_tier_neutral | separate signal from listing-age latent-state bias              |
| meme_multiplier_neutral | True       |                       8 | liquidity_tier_neutral | separate signal from meme and contract-multiplier effects       |
| btc_eth_beta_residual   | False      |                      30 | global_rank            | secondary beta residual check where implementation is available |

## Execution Plan

| step                                    | description                                                                                        | executes_search   |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------|:------------------|
| load_diagnostic_subset                  | use only A7AC-1R diagnostic representative subset; quarantined representatives remain excluded     | False             |
| recompute_candidate_signals             | re-evaluate the 7 diagnostic expressions on full timestamps for label/neutralization variants only | False             |
| evaluate_label_matrix                   | evaluate required labels L0/L1/L7 at 1h/4h; optional L2/L3/L4 if local inputs are available        | False             |
| evaluate_neutralization_modes           | global, liquidity-tier, latent-state, meme/multiplier neutral where grouping inputs are available  | False             |
| control_and_lag_audit                   | wrong-lag/stale/shuffle/sign/random controls plus one-bar execution and 2/5/10/20bps cost proxy    | False             |
| decide_label_artifact_vs_real_structure | if evidence exists only in L7 ranked-return, freeze as label artifact and stop                     | False             |

## Pass Gates

| gate                           | rule                                                                                                   |
|:-------------------------------|:-------------------------------------------------------------------------------------------------------|
| quarantine_respected           | no A7AC-1 blocked representatives in A7AC-3 input                                                      |
| non_ranked_label_support       | at least 2 diagnostic candidates survive either L0 or L1 in pre-May splits                             |
| neutralization_support         | at least 2 diagnostic candidates survive one required neutralization mode beyond global rank           |
| control_hard_gate              | control_ratio must remain <1.0 by split and control type                                               |
| control_warning_disclosure     | 0.80 <= control_ratio < 1.0 remains diagnostic-only warning                                            |
| nonoverlap_positive            | nonoverlap min/median tstats must remain positive in validation/test/recent                            |
| lag_cost_positive              | one-bar lag and 20bps proxy must remain positive                                                       |
| label_concentration_resolution | if survivors remain L7-only, do not authorize formula search or replay expansion                       |
| no_may_leakage                 | May is unavailable to selector/ranking/generation/thresholds and remains stress-only if later observed |

## Forbidden Actions

| item                           | reason                                            |
|:-------------------------------|:--------------------------------------------------|
| use_quarantined_representative | blocked by A7AC-1 nonoverlap tstat                |
| formula_search_execution       | A7AC-2 is contract-only                           |
| large_search                   | no label diversification evidence yet             |
| alpha_proof_shadow_paper_live  | diagnostic lineage only                           |
| May_in_selector_or_threshold   | May must remain stress-only                       |
| L7_only_promotion              | current evidence is single label family dominated |

## Experiment Record

```json
{
  "date": "2026-05-29",
  "decision": "contract_only",
  "experiment_id": "20260529_a7ac2_label_diversification_contract",
  "inputs": {
    "a7ac1r_manifest": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1r_representative_quarantine_contract\\a7ac1r_manifest.json",
    "diagnostic_subset": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1r_representative_quarantine_contract\\a7ac1r_diagnostic_representative_subset.csv",
    "quarantined": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac1r_representative_quarantine_contract\\a7ac1r_quarantined_representatives.csv"
  },
  "mode": "light_contract",
  "next_action": "A7AC-3 label diversification and neutralization diagnostic",
  "objective": "Define a bounded label-diversification and neutralization diagnostic for A7AC-1R representatives.",
  "outputs": {
    "report": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\reports\\CRYPTO_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_20260529.md",
    "runtime": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ac2_label_diversification_contract"
  },
  "parameters": {
    "May_usage": "not used",
    "minimum_neutralized_candidates": 2,
    "minimum_non_ranked_candidates": 2,
    "required_horizons": [
      1,
      4
    ],
    "required_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L7_ranked_future_return"
    ]
  },
  "status": "completed"
}
```
