# Crypto Search Engine V2.1 Mechanism Basis

- Status: `PASS_SEARCH_ENGINE_V2_1_TRAIN_GATE_NEGATIVE`; development-only; sealed reads `0`.
- Producer source: `94b016fa7847d5c5b06db1e6144bda7062064151`.
- Strict completed: `10,000` from `14,237` raw attempts.
- Catalog: `184` legacy and `786` expanded mechanisms through the existing AST/compiler/evaluator.
- Checkpoints: `5/5`; exact restore: `True`.
- Train gate: `TRAIN_GATE_NEGATIVE`; terminal validation: `VALIDATION_NOT_RUN_TRAIN_GATE_NEGATIVE`.

| Arm | Strict | Families | Duplicate | Mean search reward | Top-decile | Positive search reward |
|---|---:|---:|---:|---:|---:|---:|
| legacy_mechanism_random_v2 | 2,000 | 2,000 | 0.00% | -0.605092 | -0.132234 | 0.50% |
| expanded_mechanism_random_v2_1 | 4,000 | 3,999 | 0.02% | -0.807706 | -0.158090 | 0.57% |
| mechanism_evolution_v2_1 | 4,000 | 3,757 | 6.07% | -0.386597 | 0.060864 | 8.18% |

Validation-qualified arms: **none**. This run does not create an Alpha,
OOS, challenge, recent, May-stress, forward, or promotion claim and starts no
subsequent Arena.
