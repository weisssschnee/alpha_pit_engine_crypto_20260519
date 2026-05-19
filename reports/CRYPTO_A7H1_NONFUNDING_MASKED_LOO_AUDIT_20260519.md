# Crypto A7H-1 Non-Funding Masked LOO Audit

- generated_at: `2026-05-19T14:57:24Z`
- decision: `PASS_A7H1_RESIDUAL_CANDIDATE_AUDIT`
- evidence_level: `candidate_audit_only_not_alpha_proof`
- pass_count: `1`
- candidate_count: `2`

## Scope

- Only A7H-0 pass candidates are audited.
- No search expansion, no formula tuning, no shadow promotion.
- Masked symbol LOO is computed by excluding each held-out symbol from candidate, FundingCore, and Core4 replay before residualization.

## Candidate Summary

| candidate | val residual funding | recent residual funding | May residual funding | May residual Core4 | May raw | recent LOO+ | May LOO+ | pass |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `a7h_flow_rank_taker_imbalance_h6` | 0.4687 | 0.2214 | 0.5604 | 0.5425 | -2.9743 | 1.000 | 0.917 | `True` |
| `a7h_liquidity_size_h12` | 1.0254 | 1.5319 | 0.6827 | 0.1070 | -1.6261 | 1.000 | 0.750 | `False` |

## Decision Boundary

- PASS only means a non-funding residual candidate is robust enough for deeper A7H-2 audit.
- This does not authorize A7.3 generator bakeoff, dry-shadow evidence, paper, live, or production claims.
- If no candidate passes masked LOO, non-funding residual line remains research-only.
