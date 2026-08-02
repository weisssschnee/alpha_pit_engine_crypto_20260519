# Crypto Search Engine V2.2 Evolution Qualification

- Status: `PASS_SEARCH_ENGINE_V2_2_VALIDATION_GATE_NEGATIVE` (`VALIDATION_GATE_NEGATIVE`); development-only.
- Producer source: `e84b35c76a4cfc139f1c351286489b83fce61250`.
- Strict completed: `8,000` from `12,240` raw attempts.
- Catalog: `786` existing V2.1 mechanisms; no new AST/compiler/evaluator.
- Checkpoints: `4`; exact restore: `True`.
- Train gate: `PASS`; validation: `VALIDATION_STAGE_COMPLETE`.

| Arm | Strict | Families | Duplicate | Mean search reward | Top-decile | Positive search reward |
|---|---:|---:|---:|---:|---:|---:|
| expanded_mechanism_random_v2_2 | 4,000 | 4,000 | 0.00% | -0.831556 | -0.161436 | 0.40% |
| mechanism_evolution_v2_2 | 4,000 | 3,779 | 5.53% | -0.363293 | 0.117570 | 10.15% |

Development-qualified policy arms: **none**. The random arm is the
receipt-bound validation control, not the policy being qualified. This run
creates no Alpha, OOS, challenge, recent, May-stress, forward, or promotion
claim and starts no subsequent Arena.
