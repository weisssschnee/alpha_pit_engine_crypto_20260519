# Crypto A7K Final Decision Record

- decision: `HOLD_CRYPTO_A7K_NO_NEW_SPACE_AUTHORIZATION`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- shadow_paper_live_status: `NOT_AUTHORIZED`
- A7K-0: `PASS_A7K0_GENERATOR_SPACE_REDESIGN_CONTRACT`
- A7K-1: `HOLD_A7K1_PREFLIGHT_BLOCKED`
- A7K-2: `NOT_AUTHORIZED`

## Confirmed

- A7K correctly inherits the A7J boundary: May 2026 is a known adversarial stress set and remains stress-only.
- A7K-0 freezes the redesigned generator-space contract without running search or replay.
- A7K-1 confirms the proposed feature set has core12 coverage for the allowed non-spot fields.
- A7K-1 confirms May is excluded from preselection gates, score columns, ranking, and selection.
- A7K-1 catches most old-pool weakness: only `11 / 1000` A7I/A7J frozen candidates pass the A7K preselection gates.

## Blockers

- `old_a7j_pool_still_has_candidates_passing_a7k_preselection`
- `old_pool_family_cap_fail`

The `11` old-pool candidates that pass A7K preselection are not acceptable as a research set because they are concentrated in one family:

| family | count | share |
|---|---:|---:|
| `flow_liquidity` | 10 | 90.91% |
| `microstructure_lite` | 1 | 9.09% |

This means A7K has not yet demonstrated a viable redesigned generator space. It only demonstrated that the new gates are directionally stricter and that the old pool still contains family concentration risk.

## Not Confirmed

- no crypto alpha proof
- no A7K research candidates
- no new generator-space smoke authorization
- no shadow / paper / live authorization
- no permission to expand the same generator budget

## Next Valid Work

Two valid paths remain:

1. `A7K-GEN-IMPL`: implement a genuinely new generator-space preflight that enforces family caps before selection, rejects residual-only hedge clues, rejects zero/low-activity candidates, and preserves May stress-only.
2. `FORWARD-WAIT`: freeze the A7J/A7K contracts and wait for new append-only data after the contract freeze.

Do not run A7K-2 until a new-space generator implementation passes a separate preflight. Do not tune gates against May.
