# Crypto A7M-2C Decision Record

- decision: `PASS_A7M2C_EQUAL_BUDGET_BAKEOFF_AUTHORIZATION_REVISION`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- search_executed: `False`
- replay_executed: `False`
- authorizes_equal_budget_a7m2_bakeoff: `True`
- authorizes_adaptive_large_search: `False`

## Resolved / Reclassified

- E3 AST repair adapter blocker is resolved if A7M-2A passed.
- E4 CEM adaptive grammar blocker is resolved if A7M-2B passed.
- A7M-1B surrogate cross-source HOLD is reclassified as allocation-mode blocker.

## Boundary

- Equal-budget A7M-2, if run later, remains an engine bakeoff and not alpha proof.
- Surrogate cannot allocate budgets until cross-source generalization is fixed.
- No shadow, paper, live, production, or adaptive large search authorization.
