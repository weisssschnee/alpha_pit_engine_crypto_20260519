# Crypto Search Engine V2.3 Policy Attribution

- Status: `PASS_SEARCH_ENGINE_V2_3_POLICY_ATTRIBUTION_GATE_NEGATIVE` (`FULL_POLICY_ATTRIBUTION_GATE_NEGATIVE`); development-only.
- Producer source: `06512e01876345d9921d56405d8254a82933a9b7`.
- Strict train/continuation: `16,000` from `23,869` attempts; validation candidate-cohort evaluations: `1024`.
- Catalog: `786` unchanged mechanisms; no new data, AST, compiler, evaluator, target, or cost.
- Checkpoints: `8`; exact restore: `True`.

| Arm | Strict | Families | Duplicate | Mean search reward | Top-decile | Positive search reward |
|---|---:|---:|---:|---:|---:|---:|
| expanded_mechanism_random_v2_3 | 8,000 | 7,998 | 0.02% | -0.810748 | -0.147773 | 0.68% |
| mechanism_evolution_v2_3 | 8,000 | 6,676 | 16.55% | -0.304846 | 0.249988 | 21.45% |

Proposal distribution qualified: **False**.
Train ranker qualified: **False**.
Total policy relative effect qualified: **False**.
Evolution train-top absolute kill-line passed: **False**.
Full replicated Evolution policy passed: **False**.

Random is comparator-only and has no profitability survival requirement. This
run creates no Alpha, OOS, challenge, recent, stress, forward, or promotion
claim and starts no subsequent Arena.
