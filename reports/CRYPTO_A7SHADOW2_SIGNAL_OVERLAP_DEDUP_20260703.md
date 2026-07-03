# CRYPTO A7SHADOW2 Signal Overlap Dedup

Generated: 2026-07-03T15:24:49.121009+00:00

## Decision

`PASS_A7SHADOW2_SIGNAL_OVERLAP_DEDUP_BUILT`

This stage deduplicates the historical shadow-readiness review queue by formula expression, field tokens, operator tokens, semantic family, and horizon. It does not authorize alpha proof, paper trading, shadow trading, or live trading.

## Counts

- input_rows: `9`
- cluster_count: `5`
- dedup_keep_rows: `5`
- hold_overlap_variant_rows: `4`

## Cluster Leaders

| cluster | members | decision | semantic_pairs | leader_expression | min_oos_floor | stress_floor | test_sortino |
|---|---:|---|---|---|---:|---:|---:|
| a7shadow2_cluster_01 | 2 | `KEEP_CLUSTER_LEADER_HOLD_OVERLAP_VARIANTS` | `open_interest|funding_state:1|funding_dense|open_interest:1` | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` | 8.633900693694594 | 2.390686280165006 | 10.216245843420882 |
| a7shadow2_cluster_02 | 3 | `KEEP_CLUSTER_LEADER_HOLD_OVERLAP_VARIANTS` | `open_interest|premium:3` | `Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))` | 1.9038409869878905 | 3.8769944978553337 | 2.9251446047230125 |
| a7shadow2_cluster_03 | 2 | `KEEP_CLUSTER_LEADER_HOLD_OVERLAP_VARIANTS` | `open_interest:2` | `TSRank(open_interest_mean,504)` | 1.781994350944033 | 0.13792916060062388 | 3.891615500928222 |
| a7shadow2_cluster_04 | 1 | `KEEP_UNIQUE_MECHANISM_REVIEW` | `open_interest|premium:1` | `Mul(open_interest_last,Mean(premium_close_bps,504))` | 1.3646549978752314 | 6.105075206711021 | 2.5037565195685585 |
| a7shadow2_cluster_05 | 1 | `KEEP_UNIQUE_MECHANISM_REVIEW` | `basis|premium:1` | `Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))` | 0.8522200631450245 | 6.497715977476842 | 5.510858270897706 |

## Interpretation

The historical review queue is not a broad independent alpha set yet. It is a small set of OI, premium, funding, and basis mechanisms with several parameter or expression-near variants. This points to both a feature-supply bottleneck and a generation/search-space bottleneck: the pipeline can generate many formulas, but the strict gates repeatedly promote the same information families.

## Outputs

- review_queue_dedup: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_review_queue_dedup.csv`
- keep_queue: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_keep_queue.csv`
- hold_overlap_variants: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_hold_overlap_variants.csv`
- pairwise_overlap: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_pairwise_overlap.csv`
- cluster_summary: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_cluster_summary.csv`
- manifest: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow2_signal_overlap_dedup_20260703\a7shadow2_manifest.json`
