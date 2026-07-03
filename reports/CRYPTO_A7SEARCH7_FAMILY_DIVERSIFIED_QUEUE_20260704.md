# CRYPTO A7SEARCH7 Family Diversified Queue

Generated: `2026-07-03T18:36:19Z`

## Decision

`PASS_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_READY`

A7SEARCH7 builds a checkpointable proxy queue after A7SHADOW-7 dedupe and A7LIVE-1 source-lag authorization. It is proxy-only and does not authorize alpha proof, shadow, paper, or live.

## Counts

- queue_rows: `65536` / `65536`
- semantic_pair_count: `40`
- motif_count: `22`
- skeleton_count: `1423`
- oi_touch_share: `0.0999908447265625`
- non_oi_touch_share: `0.9000091552734375`
- blockers: `none`

## Lane Summary

| search_policy                   |   rows |
|:--------------------------------|-------:|
| raw_broad_non_oi                |  15729 |
| taker_liquidity_mechanism       |  15729 |
| funding_basis_premium_mechanism |  14418 |
| regime_conditioned_non_oi       |  13107 |
| shadow_positive_prior_light     |   6553 |

## Semantic Pair Summary

| semantic_pair               |   rows |
|:----------------------------|-------:|
| funding_dense|taker_flow    |   7506 |
| positioning|taker_flow      |   6048 |
| funding_dense|positioning   |   5850 |
| positioning|regime          |   3446 |
| funding_dense|regime        |   2670 |
| premium|taker_flow          |   2533 |
| basis|taker_flow            |   2498 |
| liquidity|taker_flow        |   2464 |
| funding_dense|premium       |   2373 |
| basis|funding_dense         |   2368 |
| funding_dense|liquidity     |   2364 |
| open_interest|positioning   |   2310 |
| regime|taker_flow           |   2059 |
| funding_dense|open_interest |   1889 |
| funding_basis|taker_flow    |   1860 |
| liquidity|regime            |   1454 |
| funding_basis|positioning   |   1439 |
| premium|regime              |   1405 |
| basis|regime                |   1404 |
| positioning|positioning     |   1071 |
| open_interest|premium       |    953 |
| basis|open_interest         |    923 |
| liquidity|positioning       |    891 |
| positioning|premium         |    890 |
| basis|positioning           |    851 |
| funding_dense|funding_dense |    704 |
| funding_basis|regime        |    669 |
| basis|funding_basis         |    603 |
| funding_basis|liquidity     |    593 |
| funding_basis|premium       |    550 |
| funding_basis|open_interest |    478 |
| taker_flow|taker_flow       |    396 |
| basis|premium               |    377 |
| liquidity|premium           |    367 |
| basis|liquidity             |    363 |
| funding_basis|funding_dense |    336 |
| liquidity|liquidity         |    181 |
| premium|premium             |    177 |
| basis|basis                 |    175 |
| funding_basis|funding_basis |     48 |

## Motif Summary

| motif                        |   rows |
|:-----------------------------|-------:|
| regime_conditioned_rank      |   4774 |
| regime_conditioned_scaled    |   4567 |
| flow_shock_gate              |   4336 |
| flow_liquidity_scaled        |   4120 |
| funding_basis_delta_scaled   |   4018 |
| funding_basis_state_mul      |   3993 |
| flow_liquidity_rank_mul      |   3902 |
| regime_conditioned_sign      |   3766 |
| raw_add_rank                 |   3492 |
| flow_liquidity_spread        |   3371 |
| raw_signed_gate              |   3277 |
| funding_basis_signed         |   3208 |
| raw_safe_div_abs             |   3208 |
| funding_basis_spread         |   3199 |
| raw_rank_mul                 |   3081 |
| raw_spread_rank              |   2671 |
| positive_prior_safe_div_rank |   2441 |
| positive_prior_safe_div_abs  |   2204 |
| positive_prior_signed_rank   |   1903 |
| shadow_selected_rank_wrap    |      2 |
| shadow_selected_sign_wrap    |      2 |
| shadow_selected_exact_probe  |      1 |

## Semantic Touch Summary

| semantic      |   touches |
|:--------------|----------:|
| funding_dense |     26764 |
| taker_flow    |     25760 |
| positioning   |     23867 |
| regime        |     13107 |
| premium       |      9802 |
| basis         |      9737 |
| liquidity     |      8858 |
| funding_basis |      6624 |
| open_interest |      6553 |

## Manifest

```json
{
  "attempts": 79484,
  "authorizes_alpha_proof": false,
  "authorizes_proxy_search": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_READY",
  "generated_at": "2026-07-03T18:36:19Z",
  "lane_counts": {
    "funding_basis_premium_mechanism": 14418,
    "raw_broad_non_oi": 15729,
    "regime_conditioned_non_oi": 13107,
    "shadow_positive_prior_light": 6553,
    "taker_liquidity_mechanism": 15729
  },
  "lane_target_shares": {
    "funding_basis_premium_mechanism": 0.22,
    "raw_broad_non_oi": 0.24,
    "regime_conditioned_non_oi": 0.2,
    "shadow_positive_prior_light": 0.1,
    "taker_liquidity_mechanism": 0.24
  },
  "max_parallel": 12,
  "memory_action_counts": {
    "neutral": 65536,
    "reject": 11685
  },
  "memory_prior": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7mem0_search_memory_registry_20260628\\a7mem0_next_search_prior.json",
  "memory_reject_counts": {
    "neutral_explore": 65536,
    "pair_motif_cap": 26,
    "skeleton_key_cap": 11659
  },
  "min_free_gb": 10.0,
  "motif_count": 22,
  "non_oi_touch_share": 0.9000091552734375,
  "oi_touch_share": 0.0999908447265625,
  "overlap_rejection_rows": 2,
  "overlap_rejections": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow7_dedup_review_packet_20260704\\a7shadow7_overlap_rejections.csv",
  "queue": "H:\\AlphaFactory_CryptoData_archive\\a7search7_family_diversified_proxy_65k_20260704\\a7search7_proxy_queue.csv",
  "queue_rows": 65536,
  "queue_rows_requested": 65536,
  "report": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\reports\\CRYPTO_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_20260704.md",
  "rows_per_shard": 512,
  "runtime": "H:\\AlphaFactory_CryptoData_archive\\a7search7_family_diversified_proxy_65k_20260704",
  "seed": 20260704,
  "selected_packet": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow7_dedup_review_packet_20260704\\a7shadow7_selected_review_packet.csv",
  "semantic_pair_count": 40,
  "shard_count": 128,
  "shard_plan": "H:\\AlphaFactory_CryptoData_archive\\a7search7_family_diversified_proxy_65k_20260704\\a7search7_proxy_shard_plan.csv",
  "skeleton_count": 1423,
  "stage": "A7SEARCH7",
  "supervisor": "H:\\AlphaFactory_CryptoData_archive\\a7search7_family_diversified_proxy_65k_20260704\\a7search7_proxy_supervisor.ps1"
}
```
