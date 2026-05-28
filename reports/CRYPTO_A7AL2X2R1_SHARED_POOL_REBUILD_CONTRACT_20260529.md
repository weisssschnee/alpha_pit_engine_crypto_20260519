# CRYPTO A7AL-2X2R1 Shared-Pool Rebuild Contract

Generated: 2026-05-28T16:59:05Z

## Decision

```text
PASS_A7AL2X2R_GENERATOR_AND_SHARED_POOL_REPAIR_CONTRACT_READY_FOR_A7AL2X3_REVIEW
```

This contract fixes the A7AR-7 source-of-truth gap: the next shared pool must be family-balanced and must include F0-F6 coverage where historical fields exist.

## Shared-Pool Ledger Schema

| column_name                            | dtype      | description                              |
|:---------------------------------------|:-----------|:-----------------------------------------|
| candidate_id                           | string     | stable unique id                         |
| expression                             | string     | formula expression                       |
| objective_family                       | enum:F0-F6 | A7AL-2X objective family                 |
| source_stage                           | string     | generator/preflight/shared-pool source   |
| field_families                         | string     | pipe-delimited field families            |
| fields                                 | string     | pipe-delimited concrete fields           |
| operator_signature                     | string     | operator motif                           |
| window_signature                       | string     | lookback windows                         |
| skeleton_key                           | string     | structure dedup key                      |
| production_key                         | string     | family/field/window key                  |
| historical_source_ok                   | bool       | no overlay-only historical proof field   |
| field_lineage_ok                       | bool       | all fields in lineage ledger             |
| pit_policy_ok                          | bool       | field-native latency valid               |
| negative_control_attached              | bool       | matched controls available before replay |
| selected_for_family_balanced_preflight | bool       | quota-based preflight selection          |
| preflight_decision                     | string     | empty before replay                      |
| shared_pool_stage                      | string     | current stage                            |

## Shared-Pool Rebuild Policy

| policy_key          | policy_value                                                                 |
|:--------------------|:-----------------------------------------------------------------------------|
| source_of_truth     | A7AL-2X shared candidate ledger only; no direct single-stage CSV reads       |
| family_min_coverage | F0-F6 must each have shared-pool candidates if generated historically        |
| quota_selection     | family-balanced first, then skeleton/production diversity                    |
| signal_vector_cap   | selected top signal-vector cluster share <= 0.35; max pairwise corr <= 0.80  |
| skeleton_cap        | same skeleton share <= 0.25                                                  |
| production_cap      | same production key share <= 0.20                                            |
| control_gate        | control_ratio >= 1.0 hard reject; 0.80-1.0 warning                           |
| may_policy          | May cannot enter generation/selector/ranking/mutation; veto/attribution only |

## Source-Of-Truth Rules

```text
1. A7AL-2X3 output ledger becomes the only source for any later dry rerank.
2. A7AL-2P2/A7AL-2Q local OI-price pools remain superseded diagnostic artifacts.
3. No direct reads from stale A7AL-2L/P1/P1R/P2 single-stage artifacts are allowed.
4. J5 overlay-only fields cannot enter historical replay/proof paths.
5. May remains post-selection veto / attribution only.
```

## Authorization Boundary

```json
{
  "authorizes_a7al2x3_family_balanced_dry_generation": "READY_FOR_REVIEW_NOT_EXECUTION_AUTHORIZED",
  "authorizes_a7al2y_generation": "NOT_AUTHORIZED",
  "authorizes_alpha_proof": "NOT_AUTHORIZED",
  "authorizes_large_search": "NOT_AUTHORIZED",
  "authorizes_shadow_paper_live": "NOT_AUTHORIZED",
  "decision": "PASS_A7AL2X2R_GENERATOR_AND_SHARED_POOL_REPAIR_CONTRACT_READY_FOR_A7AL2X3_REVIEW",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "requires_before_a7al2x3": [
    "implement family-balanced generator quotas",
    "replace F3 overlay-only positioning with Binance historical positioning fields",
    "add F6 latent-state templates",
    "write shared-pool ledger from family-balanced dry generation output"
  ]
}
```
