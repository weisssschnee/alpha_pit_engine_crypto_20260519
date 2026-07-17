# Crypto AlphaFactory current state

Last updated: 2026-07-18 Asia/Hong_Kong

## Current phase

`LIQUIDATION_SUPPLIER_INGRESS_QUALIFIED_STITCHING_BLOCKED`

The CryptoHFT liquidation history release is content-hash bound and ingress-qualified, but remains quarantined from research. Binance WebSocket history is not present in the current repository or delivery roots, so event-count, notional, and large-liquidation overlap qualification has not run and source stitching remains blocked.

## Current decisions

```text
REPOSITORY_PROVENANCE_CLOSURE_COMPLETED
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED
CRYPTO_COMPOSITIONAL_GRAMMAR_BOTTLENECK_CONFIRMED
CRYPTO_18M_COMPOSITIONAL_SEARCH_LOCALIZED_MECHANISMS_ONLY
INSUFFICIENT_INDEPENDENT_EVIDENCE
CRYPTO_IMMUTABLE_CHALLENGER_NOT_ISSUED
IMPLEMENTATION_SPECIFIC_INFORMATIVE_NEGATIVE
GRAPH_RAW_CURRENT_SEPARATION_ACTIVE
CURRENT_CONTRACT_CAPSULE_ACTIVE
CRYPTO_FIELD_INFORMATION_V0_COMPLETED
CONTEXT_BOUND_CORE_PACK_PROPOSED
LIQUIDATION_SUPPLIER_INGRESS_QUALIFIED_QUARANTINED
LIQUIDATION_STITCHING_BLOCKED_NO_WS_OVERLAP_INPUT
```

## Accepted identities

- Provenance closure: branch `origin/audit/evalreset-collapse-forensics-20260711`, commit `4726795f61052470d56e2d1475e4f6da9d262943`, tag `crypto-frontier-provenance-closure-20260714`.
- Current research branch: `experiment/crypto-explicit-latent-adaptive-v1-20260717`.
- Latest implementation qualification: `7389a36ebb4ee62f57aeb818cf4db7157bd1ea9f`.
- Field Information V0 source: `057e31df71f55f9e3a6e8ea3b48d53293d7d2e13`; run identity SHA256: `623036F48CBC8089CC61E81876F3A1E14199FC781456BF9F39183F8A129E53D6`.
- Latest qualified Graph closure before this maintenance phase: `920e0ad35c07e2e2cee3ed2be8ad0753937f86f4`.
- Accepted closure bundle SHA256: `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.
- 18-month compositional bundle SHA256: `EABBD9B4844A0589A1C409A274688D2D2C41B9793A0B584BE54909C0AC27D492`.
- Localized qualification bundle SHA256: `0C6193E81FEAB8271B8BAE05AD04604D74494EAB2710794C59A7F42919DD68EB`.
- Liquidation ingress implementation: `d64a783dac4c148d1924f76acb7b8a80cbcc7f1a`; evidence commit: `c7ee32e1a4be635a6720cc13ef4a66b3e36f4ca8`; release identity SHA256: `C9717263EC6F97839466A4BC13D8DBA803E3D0D5854AE6E3A005F4C6F0F34D7A`.

## Evidence-qualified position

- Qlib: the historical full/control comparison was `MODEL_FIT_DEGENERATE`. A frozen repair produced different predictions and weights, but 23 development dates fail adequacy requirements. Status: `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED` plus `DATA_ADEQUACY_UNDERPOWERED`.
- DeepDow: parameters and portfolio weights differ from control, so exact comparison, fit, and mapping collapse are not established. Its 156 overlapping windows do not provide enough independent blocks. Status: `DATA_ADEQUACY_UNDERPOWERED`.
- Internal search instrument: qualified only for the frozen finite grammar, deterministic synthetic reachability, mapping, cost, feedback, and survivor retention. It is not market alpha, open-generator recall, or OOS evidence.
- Observed-archive train surface: 2,549,139 rows, 13,200 unique hours, and 276 observed assets across the joined 2023H2/2024 train archive. It is not survivorship-complete; native aggTrades history remains much narrower.
- 18-month compositional run: 41 fields across 12 families, 500,000 proposal audit, 8,192 adaptive matched pairs, and zero sealed reads. Localized mechanisms did not supply independent evidence sufficient to issue a challenger.
- Explicit/latent comparison: 41/41 means cache loadability plus minimum adaptive-surface nonmissing/variance. Arm D is implementation-verified. Arm E is an overlapping field-family grouped structured proxy with shared objectives and zero-out ablation; its configured semantic matched controls were not executed. The result is an implementation-specific development negative after 5 bps cost, not OOS evidence or rejection of latent-state research.
- Field Information V0: the compiled view contains 177 base/registered tokens and 5,211 derived specifications. Census loading succeeded for 41/41 broad fields and 94/94 Core3 aggTrades fields. `census_loaded` is not `current_runtime_member`: only ten broad fields are current-runtime members, while the 94 Core3 fields remain a separate three-asset mechanism context.
- Volume and flow are materially represented: the broad context contains seven quote-volume/activity fields; the Core3 registry contains 19 activity/liquidity, 16 flow, 6 large-trade, and 26 rolling fields. Trade count, quote volume, size-bucket notional, buy/sell quantity, and price-range fields lead the information census.
- Proposed Core Pack: 120 unique tokens = 75 base plus 45 lazy derived; 39 tokens belong to the broad context and 81 to Core3. This is a context-qualified candidate collection, not a claim that all 120 coexist on the 498-asset broad panel.
- Liquidation supplier release: 762 Parquet partitions across 381 dates passed schema, count, primary-key, PIT-delay, and content-identity preflight. Of 500 symbols and 11,138,396 events, 464 linear USDT/USDC symbols with 11,101,810 events are eligible for source comparison. Nineteen inverse/delivery and seventeen unknown-semantics symbols remain notional-quarantined because the supplier's quantity-times-price value is not a qualified common notional for those contracts. This is ingress evidence only, not a research field admission or economic result.

## Active execution plan

1. Keep the liquidation supplier release quarantined; do not join it to any Binance WebSocket capture by filename, symbol, or assumed venue semantics.
2. When an explicit Binance WS landing root is available, rerun `scripts/crypto_liquidation_supplier_ingress.py --ws-root <path>` under the frozen overlap thresholds. A pass only makes stitching eligible for a separate explicit activation decision.
3. After source compatibility, require the existing Data Adequacy Gate before any research use; the 2025-2026 release does not enter the current 2023H2/2024 train surface.
4. Treat the 120-token output as two context-bound candidate surfaces, not one merged training matrix.
5. For a future model comparison, choose exactly one context and materialize only its frozen selected fields; do not expand all 5,211 derived specifications.
6. Keep challenge, recent, May stress, forward, promotion, and cross-sprint memory closed.

No large experiment is authorized merely by this plan.

## Blockers

- Historical aggTrades coverage is not yet equivalent to the 18-month observed-archive surface; the qualified Core3 slice has 3 assets, 4,368 hours, and 13,068 eligible observations.
- Existing external-paradigm samples lack independent evaluation power.
- The localized compositional mechanism remains challenge-unstable.
- The structured-proxy comparison lacks executed semantic matched controls and does not identify independent latent states.
- No canonical Binance WebSocket liquidation history landing was found, so supplier/WS overlap compatibility is not yet qualified and stitching is blocked.

## Source-of-truth order

1. Current user instruction and sealed-data boundaries.
2. Committed source, data contracts, manifests, and real run assets at exact SHA.
3. Accepted closure tag and independent closure attestations.
4. `.planning/PROJECT.md` for mission and this file for current state.
5. `config/architecture_overlay.json` and generated CURRENT for approved architecture authority/contracts.
6. RAW Graphify for navigation only.
7. Historical reports and older status text.

No status code overrides observed runtime or source facts.

## Graph and maintenance

- RAW and CURRENT remain the only two graph layers.
- Lifecycle color, evidence line style, and validation assurance are independent.
- CURRENT never infers authority or lifecycle promotion from RAW presence or test success.
- Use `scripts/maintain_crypto_navigation_graph.ps1 build` after source changes that stale RAW.
- Use `scripts/maintain_crypto_navigation_graph.ps1 maintain` after overlay/profile changes.
- Use `scripts/maintain_crypto_navigation_graph.ps1 check` before closure; it verifies both RAW and CURRENT input hashes.
- Use `scripts/maintain_crypto_navigation_graph.ps1 query -Question "..."` for RAW navigation.
- Lifecycle history not recalled with confidence remains in Git; it is not reconstructed into CURRENT.

## Next action

Run no large experiment. The next liquidation action is only to provide or locate the canonical Binance WS history root and rerun the existing overlap gate; do not stitch or expose the supplier release to research before that result and a separate explicit activation decision.
