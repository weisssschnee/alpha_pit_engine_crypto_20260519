# Crypto AlphaFactory Planning State

**Last updated:** 2026-07-04 02:30 Asia/Hong_Kong
**Status:** forward source-lag audit passed for controlled research; final proof checksum still pending; no deployment authorization

## Current Source Of Truth

- Git status at the previous committed snapshot: `HEAD == origin/main == e7f55b9 planning: update crypto shadow taskflow`.
- Latest pending stage in this update: A7LIVE-1 source-lag/checksum audit.
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

## Current Remote Compute State

- No long-running A7 Python worker is required by the current stage.
- Company-machine heavy compute should be used for the next large family-diversified search or source-lag/checksum audits.
- Do not start broad search until the next queue explicitly consumes A7SHADOW-7 overlap rejection memory and caps open-interest concentration.

## Immediate Next Taskflow

1. A7SEARCH7 family-diversified queue build.
   - Consume A7SHADOW-7 selected packet and rejected-overlap map.
   - Keep OI/funding/premium winners as memory priors, not as the only search space.
   - Force non-OI families into the queue: liquidity, taker flow, volatility, CE overlay, regime/event state.
   - Apply caps by expression, skeleton, semantic pair, motif, base field, and economic exposure.
2. A7SEARCH7 proxy run on company machine.
   - Large enough to test family breadth, but checkpointed and restartable.
   - Must write shard manifests and aggregate selected rows.
3. Strict reward and dedupe loop.
   - Train Sortino, validation/test/recent/stress, controls, shuffle, lag/stale, non-overlap, and family diversification all required.

## Blocked Claims

- Alpha proof.
- Shadow book.
- Paper/live trading.
- Production portfolio construction.
- Treating two deduped engineering candidates as a deployable book.
