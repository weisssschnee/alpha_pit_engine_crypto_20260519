# CRYPTO A7FF-CORE49 FULL-UNIVERSE NULL-VECTOR PREFLIGHT CONTRACT

Generated: 2026-06-01T21:26:27Z

## Decision

`PASS_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_READY_FOR_CORE49E`

CORE49 is a contract-only stage. It defines how CORE49E may build full-universe original/null vectors from the repaired CORE48SE seed queue. It does not execute numeric replay, formula search, large search, alpha proof, promotion, shadow, paper, or live.

## Source Summary

- seeds: `1800`
- semantic families: `39`
- operators: `7`
- preflight shards: `12`

## Input Sources

| input_id                    | path                                                                                              | role                                                             | required   |
|:----------------------------|:--------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------|:-----------|
| I0_core48se_seed_queue      | runtime/a7ffcore48se_repaired_null_first_dry_generation/a7ffcore48se_eligible_seed_queue.csv      | source-of-truth repaired null-first seed queue                   | True       |
| I1_universe498_panel        | G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527                | full-universe feature panel for vector construction              | True       |
| I2_label_contract           | runtime/a7aa0_label_universe/a7aa0_label_contract.csv                                             | label family and horizon contract for preflight bookkeeping only | True       |
| I3_field_enforcement_ledger | runtime/a7aif2_field_enforcement_regression/a7aif2_historical_candidate_role_reclassification.csv | role-aware field/candidate enforcement source                    | True       |
| I4_materialization_parity   | runtime/a7aif3_materialization_evaluator_parity/a7aif3_operator_parity_matrix.csv                 | approved operator materialization parity source                  | True       |

## Shard Plan

| shard_id         |   seed_start_inclusive |   seed_end_exclusive |   max_seed_count | executes_replay   | executes_search   |
|:-----------------|-----------------------:|---------------------:|-----------------:|:------------------|:------------------|
| core49e_shard_00 |                      0 |                  150 |              150 | False             | False             |
| core49e_shard_01 |                    150 |                  300 |              150 | False             | False             |
| core49e_shard_02 |                    300 |                  450 |              150 | False             | False             |
| core49e_shard_03 |                    450 |                  600 |              150 | False             | False             |
| core49e_shard_04 |                    600 |                  750 |              150 | False             | False             |
| core49e_shard_05 |                    750 |                  900 |              150 | False             | False             |
| core49e_shard_06 |                    900 |                 1050 |              150 | False             | False             |
| core49e_shard_07 |                   1050 |                 1200 |              150 | False             | False             |
| core49e_shard_08 |                   1200 |                 1350 |              150 | False             | False             |
| core49e_shard_09 |                   1350 |                 1500 |              150 | False             | False             |
| core49e_shard_10 |                   1500 |                 1650 |              150 | False             | False             |
| core49e_shard_11 |                   1650 |                 1800 |              150 | False             | False             |

## Vector Output Schema

| field                  | required   | description                             |
|:-----------------------|:-----------|:----------------------------------------|
| seed_id                | True       | CORE48SE seed id                        |
| timestamp              | True       | feature timestamp                       |
| symbol                 | True       | symbol                                  |
| original_signal        | True       | materialized candidate signal           |
| stale_signal           | True       | stale/wrong-lag control vector          |
| sign_flip_signal       | True       | sign-flip control vector                |
| time_shuffle_signal    | True       | time-shuffle control vector             |
| symbol_shuffle_signal  | True       | symbol-shuffle control vector           |
| null_margin            | True       | original-vs-null vector margin proxy    |
| role_gate_status       | True       | field/candidate role enforcement status |
| materialization_status | True       | expression materialization status       |

## Quality Gate

| gate                    | threshold   |   observed |
|:------------------------|:------------|-----------:|
| seed_queue_present      | true        |       True |
| seed_count              | >= 1800     |       1800 |
| semantic_family_count   | >= 30       |         39 |
| operator_count          | >= 7        |          7 |
| preflight_shard_count   | >= 12       |         12 |
| executes_numeric_replay | false       |      False |
| executes_formula_search | false       |      False |

## Execution Policy

| policy_id                                 | description                                                                                                                 | hard_requirement   |
|:------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|:-------------------|
| P0_vector_preflight_only                  | CORE49E may materialize original and null vectors but may not calculate portfolio replay, promotion, or alpha proof         | True               |
| P1_full_universe_required                 | preflight must use the full available universe panel, not a hand-picked symbol subset                                       | True               |
| P2_null_vectors_required                  | every retained seed must include stale, sign-flip, time-shuffle, and symbol-shuffle vectors                                 | True               |
| P3_fail_closed_on_role_or_materialization | missing field contracts, role violations, or unsupported operators fail closed                                              | True               |
| P4_external_large_artifacts               | large vector parquet outputs must stay under G:/AlphaFactory_CryptoData/research_runtime and be referenced by manifest only | True               |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE49E full-universe null-vector preflight execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "numeric_replay": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core49e_preflight_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_READY_FOR_CORE49E",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T21:26:27Z",
  "next_allowed": "A7FF-CORE49E full-universe null-vector preflight execution",
  "operator_count": 7,
  "preflight_shard_count": 12,
  "seed_count": 1800,
  "semantic_family_count": 39,
  "source_decision": "PASS_A7FFCORE48SE_REPAIRED_DRY_SEEDS_READY_FOR_CORE49_CONTRACT",
  "source_stage": "A7FF-CORE48SE",
  "stage": "A7FF-CORE49"
}
```
