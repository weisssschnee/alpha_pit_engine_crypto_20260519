# Crypto A7M-2E Decision Record

- decision: `HOLD_A7M2E_CLUSTER_CAP_REVEALS_WEAK_POOL`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- search_executed: `False`
- replay_executed: `False`
- fast_replay_parity_pass: `True`
- blockers: `['post_cap_near_miss_clusters_gte_6', 'post_cap_field_families_gte_4', 'post_cap_engines_gte_4']`

## Confirmed

- Fast array replay has been compared against the legacy evaluator on the A7M-2E parity sample.
- A7M-2 labels are split into pre-May, post-May eligible, May-vetoed, cluster-vetoed, and research buckets.
- rc_000 is treated as May-vetoed cluster evidence, not as research survivor evidence.

## Not Authorized

- A7M-3 adaptive large search.
- Alpha proof.
- Shadow, paper, live, or production deployment.
