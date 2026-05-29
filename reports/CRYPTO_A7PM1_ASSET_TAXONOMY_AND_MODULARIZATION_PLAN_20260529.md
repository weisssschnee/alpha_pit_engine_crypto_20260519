# CRYPTO A7PM-1 ASSET TAXONOMY AND MODULARIZATION PLAN

Generated: 2026-05-29T13:53:38Z

## Decision

`PASS_A7PM1_ASSET_TAXONOMY_AND_MODULARIZATION_PLAN_BUILT`

A7PM-1 classifies current code, reports, runtime artifacts, configs, and external data references. It does not move files or execute search.

## Manifest

```json
{
  "authorizes_a7pm2": true,
  "authorizes_a7pm3": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "code_asset_count": 151,
  "config_count": 7,
  "decision": "PASS_A7PM1_ASSET_TAXONOMY_AND_MODULARIZATION_PLAN_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T13:53:38Z",
  "report_count": 148,
  "runtime_artifact_count": 1017,
  "stage": "A7PM-1"
}
```

## Target Layout

```json
{
  "alphafactory_crypto/clustering": "signal-vector and formula-family clustering",
  "alphafactory_crypto/controls": "negative controls, wrong-lag, shuffle, placebo",
  "alphafactory_crypto/data_contracts": "PIT/source/timing/source-of-truth contracts",
  "alphafactory_crypto/experiments": "experiment board and stage registry integration",
  "alphafactory_crypto/features": "typed FeatureFactory and derived feature contracts",
  "alphafactory_crypto/generators": "formula and expression generators",
  "alphafactory_crypto/governance": "source-of-truth registry and authorization matrix",
  "alphafactory_crypto/labels": "label construction and label adequacy",
  "alphafactory_crypto/promotion": "candidate lifecycle and promotion gates",
  "alphafactory_crypto/regimes": "latent and upper-regime state builders",
  "alphafactory_crypto/replay": "materialization, evaluator, replay, parity",
  "alphafactory_crypto/selectors": "role-aware and replay-aware selectors"
}
```

## Refactor Priority

| category            | target_module                      |   asset_count |   min_priority |
|:--------------------|:-----------------------------------|--------------:|---------------:|
| experiment_registry | alphafactory_crypto/governance     |             6 |             10 |
| data_contracts      | alphafactory_crypto/data_contracts |            42 |             20 |
| replay_engine       | alphafactory_crypto/replay         |            17 |             20 |
| feature_factory     | alphafactory_crypto/features       |            12 |             20 |
| label_factory       | alphafactory_crypto/labels         |             4 |             20 |
| selector            | alphafactory_crypto/selectors      |             9 |             30 |
| formula_generator   | alphafactory_crypto/generators     |             4 |             30 |
| controls            | alphafactory_crypto/controls       |             2 |             30 |
| regime_factory      | alphafactory_crypto/regimes        |             1 |             30 |
| clustering          | alphafactory_crypto/clustering     |             3 |             40 |
| promotion           | alphafactory_crypto/promotion      |             1 |             40 |
| stage_entry_or_misc | manual_review                      |            50 |             60 |

## Boundary

```text
cn_reference is reference-only.
scripts/crypto_a7*.py are stage-entry scripts, not long-term services.
runtime artifacts must not be bypassed by future selectors or replay scripts.
```
