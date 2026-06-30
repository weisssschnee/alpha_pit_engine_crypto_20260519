# CRYPTO A7SEARCH6 Mechanism Memory Seed Proxy Contract 20260630

Generated: `2026-06-30T07:50:39Z`

## Decision

`PASS_A7SEARCH6_MECHANISM_QUEUE_READY`

A7SEARCH6 expands the A7SEARCH5 validation result into a bounded OI/positioning mechanism surface. It is proxy-only and does not authorize alpha proof, shadow, paper, or live.

## Counts

- queue_rows: `65536`
- semantic_pair_count: `13`
- motif_count: `19`
- skeleton_count: `1165`

## Lane Summary

| search_policy                  |   rows |
|:-------------------------------|-------:|
| adjacent_mechanism_cross       |  30866 |
| validated_oi_positioning_scale |  12288 |
| regime_conditioned_mechanism   |  12142 |
| operator_ablation_surface      |  10240 |

## Pair Summary

| semantic_pair               |   rows |
|:----------------------------|-------:|
| open_interest|positioning   |  22528 |
| open_interest|regime        |  10846 |
| positioning|regime          |  10772 |
| funding_dense|open_interest |   3652 |
| open_interest|taker_flow    |   3625 |
| funding_dense|positioning   |   3597 |
| positioning|taker_flow      |   3402 |
| basis|positioning           |   1204 |
| liquidity|open_interest     |   1199 |
| open_interest|premium       |   1196 |
| positioning|premium         |   1182 |
| liquidity|positioning       |   1171 |
| basis|open_interest         |   1162 |

## Motif Summary

| motif                    |   rows |
|:-------------------------|-------:|
| adjacent_mul             |   7220 |
| adjacent_spread_rank     |   6228 |
| adjacent_signed_rank     |   5938 |
| adjacent_safe_div_csrank |   5788 |
| adjacent_safe_div_abs    |   5692 |
| regime_signed            |   4083 |
| regime_rank_mul          |   4066 |
| regime_scaled            |   3993 |
| rank_mul                 |   2048 |
| rank_safe_div            |   2048 |
| safe_div_abs             |   2048 |
| safe_div_abs_csrank      |   2048 |
| safe_div_csrank          |   2048 |
| scaled_spread_abs        |   2048 |
| scaled_spread_no_abs     |   2048 |
| signed_rank_gate         |   2048 |
| spread_rank              |   2048 |
| z_safe_div_abs_csrank    |   2048 |
| z_safe_div_csrank        |   2048 |

## Manifest

```json
{
  "attempts": 276413,
  "authorizes_alpha_proof": false,
  "authorizes_proxy_search": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7SEARCH6_MECHANISM_QUEUE_READY",
  "generated_at": "2026-06-30T07:50:39Z",
  "lane_counts": {
    "adjacent_mechanism_cross": 30866,
    "operator_ablation_surface": 10240,
    "regime_conditioned_mechanism": 12142,
    "validated_oi_positioning_scale": 12288
  },
  "lane_weights": {
    "adjacent_mechanism_cross": 0.16,
    "operator_ablation_surface": 0.18,
    "regime_conditioned_mechanism": 0.08,
    "validated_oi_positioning_scale": 0.58
  },
  "max_parallel": 12,
  "memory_action_counts": {
    "neutral": 65536,
    "reject": 202931
  },
  "memory_prior": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7mem0_search_memory_registry_20260628\\a7mem0_next_search_prior.json",
  "memory_reject_counts": {
    "carry_forward_prior": 4096,
    "neutral_explore": 61440,
    "pair_motif_cap": 146493,
    "skeleton_key_cap": 56438
  },
  "min_free_gb": 16.0,
  "motif_count": 19,
  "queue": "H:\\AlphaFactory_CryptoData_archive\\a7search6_mechanism_memory_seed_proxy_65k_20260630\\a7search6_proxy_queue.csv",
  "queue_rows": 65536,
  "queue_rows_requested": 65536,
  "report": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\reports\\CRYPTO_A7SEARCH6_MECHANISM_MEMORY_SEED_PROXY_CONTRACT_20260630.md",
  "rows_per_shard": 512,
  "runtime": "H:\\AlphaFactory_CryptoData_archive\\a7search6_mechanism_memory_seed_proxy_65k_20260630",
  "seed": 20260630,
  "semantic_pair_count": 13,
  "shard_count": 128,
  "shard_plan": "H:\\AlphaFactory_CryptoData_archive\\a7search6_mechanism_memory_seed_proxy_65k_20260630\\a7search6_proxy_shard_plan.csv",
  "skeleton_count": 1165,
  "stage": "A7SEARCH6",
  "supervisor": "H:\\AlphaFactory_CryptoData_archive\\a7search6_mechanism_memory_seed_proxy_65k_20260630\\a7search6_proxy_supervisor.ps1"
}
```
