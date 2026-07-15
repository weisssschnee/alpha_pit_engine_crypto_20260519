# Crypto CEM Diversity A/B

Status: `CRYPTO_CEM_DIVERSITY_REPAIR_QUALIFIED`

This is a development-only search-instrument A/B. It is not Alpha, OOS proof, promotion, or authorization to expand search.

| Variant | Seed | Proposals | Unique | First evals | Cache hits | Within-lane repeats |
|---|---:|---:|---:|---:|---:|---:|
| baseline_cem_like | 20260715 | 128 | 39 | 38 | 90 | 89 |
| baseline_cem_like | 20260716 | 128 | 66 | 58 | 70 | 62 |
| challenger_cem_diversity_v2 | 20260715 | 128 | 128 | 128 | 0 | 0 |
| challenger_cem_diversity_v2 | 20260716 | 128 | 128 | 128 | 0 | 0 |

- Strict evaluator calls: 256.
- Sealed reads: 0.
- Feedback sensitivity: PASS.
- Unique-candidate pooled top-16 median feedback distance: 0.01617267299897387.
- Tests: 23 new; 127 total passed.

The 38/58 historical first-evaluation counts remain provenance-only because the old run shared a cache with other lanes. The primary matched baseline is 39/66 policy-local unique candidates.
