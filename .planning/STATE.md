# Crypto AlphaFactory Planning State

**Last updated:** 2026-07-10 19:42 Asia/Hong_Kong
**Status:** A7EFF1 optimized reward flow and A7SOURCE6 exact-subtree validation passed; one incremental interaction and one portfolio-marginal review remain; no deployment authorization

## Current Source Of Truth

- Git status at the previous committed snapshot: `HEAD == origin/main == e7f55b9 planning: update crypto shadow taskflow`.
- Latest completed stage in this update: A7EFF1 search/reward efficiency audit plus A7SOURCE6 exact-subtree incremental validation.
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
  - `reports/CRYPTO_A7EFF1_SEARCH_REWARD_EFFICIENCY_AUDIT_20260710.md`

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

## Historical A7SEARCH7 Search State

- A7SEARCH7 queue decision: `PASS_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_READY`.
- Original H: archive run was abandoned as invalid for execution evidence after filesystem/log corruption and incomplete manifests.
- Active remote run root: `D:\HermesWorker\runtime\a7search7_family_diversified_proxy_65k_r2_20260704`.
- Detached supervisor task id: `job_20260704_131230_9b836a`.
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
- Latest maintenance check on 2026-07-05: 10 proxy workers active, free physical memory about `13.4GB`, D: free about `9.1GB`.
- Completed manifests: at least `s000-s031` (`32/128`).
- Current running shard band: `s032-s041`.
- Supervisor configured with `max_parallel=10`, `min_free_gb=8.0`.
- Full queue and shard outputs stay on the remote D: runtime root; git stores only scripts, reports, manifests, and summaries.

## Latest Efficiency And Incremental-Information State

- A7SOURCE6 focused queue: `53` rows from `8` canonical sources.
- Registry-backed semantic pass:
  - `8` deterministic identities were rewritten to canonical nonconstant expressions;
  - `3` standalone positive-sign subtrees collapsed to constants and were rejected;
  - no valid inner mechanism was removed solely for a redundant wrapper.
- Source-lag survivors: `33`; only `18` exact portfolio-signal representatives entered strict reward.
- Exact signal identity avoided `15 / 33` (`45.5%`) survivor reward evaluations; `41` high-similarity pairs remain review-only.
- Strict reward: `132` rows, `16` accepted rows, `0` eval errors.
- Reward triage feedback: `6` exact signal representatives, not the `16` alias-expanded accepted rows.
- Final A7SOURCE6 incremental feedback: `1` representative; positive A7MEM/CEM/UCB credit is held pending A7INPUT0 coverage for `open_interest_value_last` and `account_position_divergence`.
- Information-source decisions:
  - `1` incremental interaction;
  - `5` OOS-equivalent/non-unique sources;
  - `1` canonical repass failure;
  - `1` portfolio-marginal review.
- Reward determinism:
  - common random controls are invariant to formula spelling, shard assignment, and evaluation order;
  - duplicate formula+horizon groups have zero decision mismatch;
  - old/new accepted set matches exactly (`16 / 16`).
- SafeDiv review:
  - the nested-`Abs` candidate was canonicalized instead of killed;
  - denominator q01/median: `0.020154`;
  - signal abs p99/median: `462.110403`;
  - top 1% absolute signal mass share: `0.743924`;
  - standalone reward remains unchanged, while A7SOURCE6 assigns portfolio-marginal review.
- Efficiency:
  - source-lag survivors are the only strict-reward inputs;
  - one shared manifest-backed numeric cache is loaded through read-only memmaps;
  - stable vectorized IC/RankIC and prepared rank/weight reuse preserve metrics;
  - measured total flow improved from about `1,735s` to `136.688s` (`~12.7x`);
  - measured reward stage improved from about `1,718s` to `120.266s` (`~14.3x`).
- DSL semantic compiler:
  - value domains now propagate from the field registry through the typed AST;
  - constant-conditioner collapse is resampled/rejected at generation;
  - nonconstant redundant wrappers are canonicalized before materialization;
  - a 5,000-row old-atlas sample found `496` canonical rewrites at about `4,460 rows/s`.
- Final local evidence:
  - `G:\Chengbo\runtime\a7pc2_pc1wide_source_lag_reward_20260710_results\strict_reward_optimized_v2_aggregate`;
  - `G:\Chengbo\runtime\a7pc2_pc1wide_source_lag_reward_20260710_results\a7source6_subtree_incremental_validation`.
  - `G:\Chengbo\runtime\a7eff2_semantic_identity_safediv_20260710_v2_results`.
  - PC2-native final Source6 evidence pulled under `G:\Chengbo\runtime\a7eff2_semantic_identity_safediv_20260710_v2_results\pc2_final_sync`; feedback rows: `1`, eval errors: `0`.
  - report: `reports/CRYPTO_A7EFF2_SEMANTIC_IDENTITY_SAFEDIV_INTEGRATION_20260710.md`.
- Git release evidence:
  - `runtime/a7eff2_git_release_20260711/a7eff2_active_field_registry.csv` records the `10` fields actually loaded by the PC2 shared cache and their ontology/value-domain/input-approval state;
  - `runtime/a7eff2_git_release_20260711/a7eff2_train_validation_oos_split_log.csv` records actual selected timestamps and confirms the 2023H2 backfill was not used;
  - `runtime/a7eff2_git_release_20260711/a7eff2_accepted_train_validation_oos_log.csv` records all `16` accepted alias rows and the single final incremental-memory representative;
  - `runtime/a7eff2_git_release_20260711/a7eff2_release_manifest.json` hashes the graph, registries, split sources, and external full evidence.

## Graphify / Architecture Map State

- `.planning/config.json` exists and sets `graphify.enabled: true`.
- Raw graphify artifacts exist under `.planning/graphs/graph.json` and `.planning/graphs/graph.html`.
- Latest raw graph statistics: `17661` nodes, `29739` links, and `0` hyperedges (rebuilt from commit `fb27d14` on 2026-07-11).
- Raw graphify output is explicitly classified as a code/navigation knowledge graph, not the current architecture.
- Curated architecture files:
  - `.planning/graphs/CURRENT_ARCHITECTURE.md`
  - `.planning/graphs/EVOLUTION_MAP.md`
  - `.planning/graphs/ARCHITECTURE_BOUNDARY.md`
- Use `CURRENT_ARCHITECTURE.md` for active system reasoning and `EVOLUTION_MAP.md` for phase history. Use raw graphify files only for navigation/query.

## Immediate Next Taskflow

1. Extend A7INPUT0 decisions to the final incremental formula's `open_interest_value_last` and `account_position_divergence` inputs without auto-rejecting the derived field.
2. After that approval gate, feed only `a7source6_incremental_identity_feedback.csv` into A7MEM/CEM/UCB credit updates.
   - Alias-expanded rows and pre-triage reward representatives remain audit/review evidence, not positive token credit.
3. Add cluster-aware marginal credit for the `41` high-similarity review pairs without hard-killing possible independent information.
4. Run the next broader reward-integrated search through the canonicalization -> lag-first -> identity -> strict-reward flow.
   - Preserve the frozen reward/split/cost contract and checkpoint every shard.
   - Keep the SafeDiv candidate in marginal review until denominator-floor and set-level evidence clears it.

## Blocked Claims

- Alpha proof.
- Shadow book.
- Paper/live trading.
- Production portfolio construction.
- Treating two deduped engineering candidates as a deployable book.
