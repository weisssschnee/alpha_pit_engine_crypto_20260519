# Crypto A7Q-3 Next Stage Definition

- generated_at: `2026-05-21T00:27:34Z`
- decision: `PASS_A7Q3_NEXT_STAGE_DEFINED`
- authorized: `A7S-0`, `A7T-0`, `A7R-0`
- not authorized: `W2`, `full L1`, `L2/L3`, `alpha proof`, `shadow/paper/live`

## Task Registry

| stage   | name                                | type                | executes_search   | executes_replay                                | objective                                                                                           | authorization               |
|:--------|:------------------------------------|:--------------------|:------------------|:-----------------------------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------|
| A7R-0   | horizon reframing contract          | optional_diagnostic | False             | False                                          | Define 4h/8h/24h and slower execution framing test without May tuning.                              | allowed_small_contract_only |
| A7R-1   | horizon reframing small audit       | optional_diagnostic | False             | limited_existing_candidates_or_<=64_cells_only | Check whether slower horizon improves cost/lag and post-May eligible productivity.                  | requires_A7R0_contract      |
| A7S-0   | new data and horizon contract       | primary             | False             | False                                          | Create PIT contracts for OI, liquidation, depth, cross-exchange basis/funding, and longer horizons. | authorized                  |
| A7T-0   | forward-locked observation contract | parallel            | False             | False                                          | Freeze runner/gates and define append-only future observation protocol.                             | authorized                  |

## Boundary

A7S-0 and A7T-0 are contracts, not alpha searches. A7R is optional and diagnostic. May remains stress-only and cannot enter ranking, reward, generation, allocation, mutation, threshold tuning, or surrogate targets.