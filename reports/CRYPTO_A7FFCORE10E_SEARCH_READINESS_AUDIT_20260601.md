# CRYPTO A7FF-CORE10E SEARCH READINESS AUDIT

Generated: 2026-06-01T00:04:04Z

## Decision

`PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT`

A7FF-CORE10E audits whether the balanced replay-clean pool is ready for a search contract. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core11_contract": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT",
  "executes_search": false,
  "generated_at": "2026-06-01T00:04:04Z",
  "large_search_contract_ready": false,
  "motif_bucket_count": 6,
  "next_allowed": "A7FF-CORE11 small gate-native formula expansion contract",
  "seed_candidate_count": 23,
  "semantic_bucket_count": 8,
  "small_search_contract_ready": true,
  "source_decision": "PASS_A7FFCORE10R_BALANCED_POOL_READY_FOR_SEARCH_READINESS_AUDIT",
  "source_stage": "A7FF-CORE10R",
  "stage": "A7FF-CORE10E"
}
```

## Readiness Gates

| scope                 | gate                           | pass   |
|:----------------------|:-------------------------------|:-------|
| small_search_contract | seed_count_gte_16              | True   |
| small_search_contract | semantic_buckets_gte_6         | True   |
| small_search_contract | motif_buckets_gte_5            | True   |
| small_search_contract | top_semantic_share_lte_035     | True   |
| small_search_contract | top_motif_share_lte_035        | True   |
| small_search_contract | all_from_gate_native_core_path | True   |
| large_search_contract | seed_count_gte_64              | False  |
| large_search_contract | semantic_buckets_gte_10        | False  |
| large_search_contract | motif_buckets_gte_8            | False  |

## Family Summary

| semantic_bucket                      | motif_bucket       |   candidate_count |   max_tstat |   median_control_ratio |
|:-------------------------------------|:-------------------|------------------:|------------:|-----------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    |                 7 |     2.87115 |               0.395994 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                 4 |     1.94236 |               0.388235 |
| open_interest_like                   | single             |                 3 |     2.73639 |               0.184241 |
| liquidity_like                       | single             |                 2 |     3.03917 |               0.261978 |
| volatility_like                      | single             |                 2 |     2.33048 |               0.438186 |
| open_interest_like\|positioning_like | delta_x_divergence |                 2 |     1.24115 |               0.373554 |
| taker_flow_like                      | single             |                 1 |     2.40812 |               0.275308 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                 1 |     2.38193 |               0.752219 |
| liquidity_like\|volatility_like      | safe_div_abs       |                 1 |     2.30678 |               0.1645   |

## Small Search Contract Preview

```json
{
  "allowed_budget": {
    "bounded_replay": 64,
    "generated_total": 4000,
    "materialization_preflight": 512,
    "numeric_response": 256
  },
  "next_stage": "A7FF-CORE11 small gate-native formula expansion contract",
  "not_authorized": [
    "large_search",
    "alpha_proof",
    "shadow",
    "paper",
    "live"
  ],
  "required_constraints": [
    "use CORE typed AST and subgraph gate only",
    "derive from replay-clean seed semantic/motif families",
    "preserve sign_flip diagnostic-only control policy",
    "primary labels only: L1/L3/L5",
    "no May, no stale artifacts, no direct legacy generator bypass",
    "family/motif cap before replay"
  ],
  "seed_candidate_count": 23,
  "seed_pool": "runtime\\a7ffcore10r_replay_clean_pool_repair\\a7ffcore10r_balanced_replay_clean_pool.csv"
}
```
