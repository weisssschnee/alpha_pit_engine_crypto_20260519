# Crypto AlphaFactory Planning State

**Last updated:** 2026-07-04 02:40 Asia/Hong_Kong
**Status:** A7SEARCH7 family-diversified proxy search running on company machine; no deployment authorization

## Current Source Of Truth

- Git status at the previous committed snapshot: `HEAD == origin/main == e7f55b9 planning: update crypto shadow taskflow`.
- Latest pending stage in this update: A7SEARCH7 family-diversified proxy run.
- Project-level plan: `.planning/PROJECT.md`.
- Project roadmap: `.planning/ROADMAP.md`.
- Active phase plan: `.planning/phases/01-crypto-search-hardening/01-PLAN.md`.
- Current validated reports:
  - `reports/CRYPTO_A7SHADOW5_STRESS_FUNDING_COVERAGE_AUDIT_REPAIRED_20260704.md`
  - `reports/CRYPTO_A7SHADOW6_MAY_FUNDING_REPAIR_20260704.md`
  - `reports/CRYPTO_A7SHADOW4_LIVE_CAPACITY_CORRELATION_R3_20260704.md`
  - `reports/CRYPTO_A7SHADOW7_DEDUP_REVIEW_PACKET_20260704.md`
  - `reports/CRYPTO_A7LIVE0_FORWARD_ADAPTER_PROBE_20260704.md`
  - `reports/CRYPTO_A7LIVE1_SOURCE_LAG_CHECKSUM_AUDIT_20260704.md`
  - `reports/CRYPTO_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_20260704.md`

## Confirmed System Components

- Prior governance and infrastructure phases remain passed: A7PM-0/1/2/3, A7AI-F0/F1/F2/F3/F4, A7AA-0/1/2/3/4, A7MEM-0/1.
- Reward gate rejects headline Sortino artifacts when train orientation, OOS floors, non-overlap floors, controls, shuffle, lag, or stress fail.
- May stress funding coverage was repaired from Binance Vision funding history and merged at hourly timestamps.
- Repaired base panel for stress/correlation work:
  `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704`.
- Forward recent patch for adapter smoke:
  `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612`.

## Latest Data/Stress Repair State

- A7SHADOW-6 decision: `PASS_A7SHADOW6_MAY_FUNDING_REPAIR_PANEL_BUILT`.
- Repaired symbols: `96`.
- Funding repair window: `2026-04-30T00:00:00Z` to `2026-05-26T00:00:00Z`.
- Dense funding-delta stress finite share: `1.0`.
- Fetch errors after Binance Vision fallback: `0`.
- Boundary: authorizes A7SHADOW-5/A7SHADOW-4 reruns only; no alpha proof, shadow, paper, or live.

## Latest Coverage/Correlation State

- A7SHADOW-5 repaired decision: `PASS_A7SHADOW5_STRESS_FUNDING_COVERAGE_OK`.
- Base stress finite shares:
  - funding delta ffill 8h: `1.0`
  - open interest: `1.0`
  - premium: `0.9983361064891847`
- A7SHADOW-4 R3 decision: `PASS_A7SHADOW4_ENGINEERING_REVIEW_PACKET_BUILT`.
- A7SHADOW-4 R3 blockers: none.
- A7SHADOW-4 R3 eval error rows: `0`.
- Recent positive Sortino blueprints:
  - 20bps: `3`
  - 30bps: `3`
- Remaining warnings:
  - `max_signal_corr_gt_0_85`
  - `max_recent_net_return_corr_gt_0_85`
  - `open_interest_family_concentrated`
- Interpretation: capacity/correlation packet is usable as engineering review input, but duplicated exposure must be deduped before any stronger step.

## Latest Dedup Review Packet State

- A7SHADOW-7 decision: `PASS_A7SHADOW7_DEDUP_REVIEW_PACKET_BUILT`.
- Input candidate rows: `4`.
- Selected rows after overlap dedupe: `2`.
- Rejected overlap variants: `2`.
- Overlap clusters: `2`.
- Selected max absolute signal correlation: `0.0100151181711994`.
- Selected max absolute recent net-return correlation: `0.0532733154551249`.
- Selected family counts:
  - open interest: `2`
  - funding: `1`
  - premium/basis: `1`
- Selected formulas:

```text
a7shadow2_c007|h8
SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))

a7shadow2_c002|h24
Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))
```

- Warnings:
  - `selected_packet_open_interest_concentrated`
  - `selected_packet_too_small_for_book`
- Boundary: authorizes live adapter probe only; this is not a book and not a deployment packet.

## Latest Forward Adapter Probe State

- A7LIVE-0 decision: `PASS_A7LIVE0_FORWARD_ADAPTER_PROBE_READY`.
- Candidate count: `2`.
- Loaded symbols: `96`.
- Timestamp range: `2026-05-26T00:00:00` to `2026-06-11T23:00:00`.
- Timestamp count: `408`.
- Eval error count: `0`.
- Missing fields: none.
- Minimum field finite share: `0.9411764705882353`.
- Minimum formula non-null ratio: `0.884446`.
- Minimum formula active ratio: `0.884446`.
- Boundary: adapter/materialization evidence only; no alpha proof, no shadow book, no paper/live, no trading authorization.

## Latest Source-Lag / Checksum Audit State

- A7LIVE-1 decision: `PASS_A7LIVE1_CONTROLLED_RESEARCH_SOURCE_LAG_OK_CHECKSUM_PENDING`.
- Candidate count: `2`.
- Selected fields:
  - `funding_rate_delta_state_24h`
  - `open_interest_mean`
  - `open_interest_value_last`
  - `premium_close_bps`
- Controlled research blockers: none.
- Patch coverage rows: `498`.
- Download manifest rows: `42828`.
- Gold manifest rows: `498`.
- A7LIVE-1 authorizes family-diversified controlled search: `true`.
- Final proof blockers remain:
  - `official_checksum_not_closed`
  - `recent_patch_report_fast_checksum_pending`
  - `rest_source_has_no_exchange_checksum`
- Boundary: this closes the source-lag/PIT concern for controlled research continuation, but still does not authorize alpha proof, shadow book, paper/live, or final proof.

## Current A7SEARCH7 Search State

- A7SEARCH7 queue decision: `PASS_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_READY`.
- Remote run root: `H:\AlphaFactory_CryptoData_archive\a7search7_family_diversified_proxy_65k_20260704`.
- Detached supervisor task id: `job_20260704_023743_eede40`.
- Queue rows: `65536`.
- Shards: `128` x `512`.
- Semantic pair count: `40`.
- Motif count: `22`.
- Skeleton count: `1423`.
- OI touch share: `0.0999908447265625`.
- Non-OI touch share: `0.9000091552734375`.
- Lane counts:
  - `shadow_positive_prior_light`: `6553`
  - `taker_liquidity_mechanism`: `15729`
  - `funding_basis_premium_mechanism`: `14418`
  - `regime_conditioned_non_oi`: `13107`
  - `raw_broad_non_oi`: `15729`
- A7SEARCH7 authorizes proxy search only.
- Latest startup check: 12 proxy workers active, free physical memory about `8.3GB`; supervisor configured with `max_parallel=12`, `min_free_gb=10.0`.
- Full queue and shard outputs stay on H: archive root; git stores only script, report, manifest, and summaries.

## Immediate Next Taskflow

1. Monitor A7SEARCH7 proxy run.
   - Check supervisor task status, active worker count, free memory, completed shard manifests, and duplicate shard groups.
   - Do not add workers unless memory remains above the floor after sustained progress.
2. Aggregate A7SEARCH7 after all expected shard manifests exist.
   - If any shards fail or duplicate, rerun only failed/suspect shards.
3. Strict reward and dedupe loop.
   - Train Sortino, validation/test/recent/stress, controls, shuffle, lag/stale, non-overlap, and family diversification all required.

## Blocked Claims

- Alpha proof.
- Shadow book.
- Paper/live trading.
- Production portfolio construction.
- Treating two deduped engineering candidates as a deployable book.
