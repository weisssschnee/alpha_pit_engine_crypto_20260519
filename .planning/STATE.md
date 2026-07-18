# Crypto AlphaFactory current state

Last updated: 2026-07-18 Asia/Hong_Kong

## Current phase

`BROAD_PURGED_CALIBRATION_REPLAY_COMPLETED_INCREMENT_NOT_ESTABLISHED`

The prior Broad Arena omitted the final 6 hours needed to keep its 2h execution delay plus 4h label inside each role. Those artifacts remain immutable but are superseded for current inference. A same-budget repair split development train into model-fit and held-out calibration roles, purged all four role tails, and passed the bias audit. Twelve of 29 added fields retained stable residual information, but the calibrated sticky comparison reached only 1/4 positive matched arms in selection and 0/4 in stability; one Broad MLP calibration was direction-degenerate and correctly counted as a failure. The result is an implementation-specific development negative, not OOS evidence. Bitfinex file integrity is qualified but source-interval coverage and event-study adequacy are not; the independent Binance `!forceOrder@arr` capture remains raw-only with no dates overlapping CryptoHFT.

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
CORE_PACK_CONTEXT_BOUND_CONSUMPTION_VERIFIED
CORE3_CONSUMPTION_MODEL_FIT_NOT_QUALIFIED
BROAD_CORE_PACK_CONDITIONAL_INFORMATION_VERIFIED
BROAD_CORE_PACK_INFORMATION_INCREMENT_COST_KILLED
BROAD_CORE_PACK_FIXED_MAPPING_REPAIR_NOT_ESTABLISHED
BROAD_CORE_PACK_TURNOVER_AWARE_MAPPING_COST_REDUCTION_ONLY
BROAD_CORE_PACK_DEVELOPMENT_INCREMENT_NOT_ESTABLISHED
BROAD_PREDICTION_SCALE_CALIBRATION_RISK_CONFIRMED
BROAD_UNPURGED_REFERENCE_SUPERSEDED_LABEL_BOUNDARY
BROAD_PURGED_CALIBRATION_BIAS_AUDIT_PASS
BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED
LIQUIDATION_SUPPLIER_INGRESS_QUALIFIED_QUARANTINED
BITFINEX_FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED
BITFINEX_DATA_ADEQUACY_UNDERPOWERED
BINANCE_FORCE_ORDER_FORWARD_CAPTURE_ACTIVE
LIQUIDATION_STITCHING_BLOCKED_NO_OVERLAP_DATES
```

## Accepted identities

- Provenance closure: branch `origin/audit/evalreset-collapse-forensics-20260711`, commit `4726795f61052470d56e2d1475e4f6da9d262943`, tag `crypto-frontier-provenance-closure-20260714`.
- Current research branch: `experiment/crypto-explicit-latent-adaptive-v1-20260717`.
- Explicit/latent implementation qualification: `7389a36ebb4ee62f57aeb818cf4db7157bd1ea9f`.
- Field Information V0 source: `057e31df71f55f9e3a6e8ea3b48d53293d7d2e13`; run identity SHA256: `623036F48CBC8089CC61E81876F3A1E14199FC781456BF9F39183F8A129E53D6`.
- Latest qualified Graph closure before this maintenance phase: `920e0ad35c07e2e2cee3ed2be8ad0753937f86f4`.
- Accepted closure bundle SHA256: `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.
- 18-month compositional bundle SHA256: `EABBD9B4844A0589A1C409A274688D2D2C41B9793A0B584BE54909C0AC27D492`.
- Localized qualification bundle SHA256: `0C6193E81FEAB8271B8BAE05AD04604D74494EAB2710794C59A7F42919DD68EB`.
- Liquidation ingress implementation: `d64a783dac4c148d1924f76acb7b8a80cbcc7f1a`; byte-stable evidence commit: `58ff34e48cb88acc0005e741c8aaa52d3528177e`; release identity SHA256: `C9717263EC6F97839466A4BC13D8DBA803E3D0D5854AE6E3A005F4C6F0F34D7A`.
- Core Pack consumption implementation source: `f01d0d22a40ae9949a027fe138c52998fb23c1ef`; evidence commit: `e3631d31ae5022b6765b0a333fb9c32015312c01`.
- Core Pack identity SHA256: `B6765D5A60B9A348A47A88BB53D503A48E024C1BAF83BCB14B2F4BF06E248D00`; resolved execution-contract identity SHA256: `35E54F79576A6D7A1D94AE697E8066CB9FB49CF9A97979259F39490E3281914E`; run identity SHA256: `7DE0F5FB394970C804AC483D42A63231687C461528AF0947D85855D91000A149`.
- Broad information Arena implementation source: `4aa96ba65a950adca07c4bdb9b0db734f729bdd0`; evidence commit: `edc3cda`; run identity SHA256: `E9DE6B6A98E6986D99E08571322CD66B0E2B5B145D3B392E251587FFDEE619E1`.
- Broad sticky mapping implementation source: `7fee8559c1819a779f4a5fc22e2ee21e4d84e807`; evidence commit: `66bb993`; run identity SHA256: `90FB47E5B54B410AF56B2B985E98AAD8077359E9364E6A233792A5BE66384439`.
- Broad prediction-scale audit source: `172340ac129b9f0ed79bfcbecd5126adfe662c76`; evidence commit: `39751d7`; run identity SHA256: `98493E159D5AA36A5C1BCC7E52F33D47B3C3B8E6D52FEE6BC332B288F66C7C35`.
- Purged Broad calibration replay source: `35546635450cba974457e90c0b0a3d0257689cd4`; evidence commit: `3bd334c7e11dcb3583a0b3ebba3c577242172fef`; run identity SHA256: `154731A3608CB3FFA4765E98F8C167C7776386F6115C51DCF5265D17FCF1035B`.
- Bitfinex liquidation ingress source: `7a5dfee6a7d1097ca37b06d85f3c3882a8ece388`; evidence commit: `2c8086093412a70eaf3694359e7651bfe96f3ce6`; run identity SHA256: `DB8E56C85ABD2008ECF6F97E046ED00A2CCC571B2C517BCACA9F786CEAF5320A`.
- Binance forceOrder forward-capture snapshot source: `3bd334c7e11dcb3583a0b3ebba3c577242172fef`; evidence commit: `949b277845a8ad4945dc14b6b75339b9eb7acbaa`; capture identity SHA256: `22411352F986AB29B4AC2D3E0F5241486D86FA940D7A5C63B5D98FD3E13CB934`.

## Evidence-qualified position

- Qlib: the historical full/control comparison was `MODEL_FIT_DEGENERATE`. A frozen repair produced different predictions and weights, but 23 development dates fail adequacy requirements. Status: `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED` plus `DATA_ADEQUACY_UNDERPOWERED`.
- DeepDow: parameters and portfolio weights differ from control, so exact comparison, fit, and mapping collapse are not established. Its 156 overlapping windows do not provide enough independent blocks. Status: `DATA_ADEQUACY_UNDERPOWERED`.
- Internal search instrument: qualified only for the frozen finite grammar, deterministic synthetic reachability, mapping, cost, feedback, and survivor retention. It is not market alpha, open-generator recall, or OOS evidence.
- Observed-archive train surface: 2,549,139 rows, 13,200 unique hours, and 276 observed assets across the joined 2023H2/2024 train archive. It is not survivorship-complete; native aggTrades history remains much narrower.
- 18-month compositional run: 41 fields across 12 families, 500,000 proposal audit, 8,192 adaptive matched pairs, and zero sealed reads. Localized mechanisms did not supply independent evidence sufficient to issue a challenger.
- Explicit/latent comparison: 41/41 means cache loadability plus minimum adaptive-surface nonmissing/variance. Arm D is implementation-verified. Arm E is an overlapping field-family grouped structured proxy with shared objectives and zero-out ablation; its configured semantic matched controls were not executed. The result is an implementation-specific development negative after 5 bps cost, not OOS evidence or rejection of latent-state research.
- Field Information V0: the compiled view contains 177 base/registered tokens and 5,211 derived specifications. Census loading succeeded for 41/41 broad fields and 94/94 Core3 aggTrades fields. `census_loaded` is not `current_runtime_member`: only ten broad fields are current-runtime members, while the 94 Core3 fields remain a separate three-asset mechanism context.
- Volume and flow are materially represented: the broad context contains seven quote-volume/activity fields; the Core3 registry contains 19 activity/liquidity, 16 flow, 6 large-trade, and 26 rolling fields. Trade count, quote volume, size-bucket notional, buy/sell quantity, and price-range fields lead the information census.
- Core Pack consumption: 120 unique tokens = 75 base plus 45 lazy derived, split into independent Broad (39) and Core3 (81) consumers. The repaired full-context probe verified 120/120 loadability, materialization, tensor exposure, gradient reachability, first-layer update, and prediction sensitivity. A preserved late-window attempt reached 118/120 because `active_universe_size` and `age_percentile_active_universe` were constant in that narrower Broad probe; the full authorized Broad period restored their variation. No 120-channel joint panel was created.
- Model-fit boundary: Broad probe loss decreased from 1.054226 to 1.011711. Core3 probe loss increased from 1.015130 to 1.107231, so Core3 model fit is not qualified even though all 81 channels were genuinely consumed. Neither result is a matched alpha comparison, portfolio result, economic increment, or OOS proof.
- Broad supersession and conditional information: the earlier Arena and sticky artifacts omitted a 6h role-tail purge and are no longer current inference evidence. The repaired run fits normalization and eight fixed models only on 2023-07 through 2023-12, fits eight independent nonnegative calibration coefficients only on 2024-01 through 2024-02, and purges the final 6h from model-fit, calibration, selection, and stability. All boundary and fit-independence checks pass. Stable residual information remains in 12/29 added fields, so the information gate still passes; marginal entropy remains an adequacy diagnostic, not an alpha selector.
- Purged Broad economic boundary: the uncalibrated full-minus-control paired net medians are `-1.02e-04` in selection and `-1.22e-04` in stability. Direct delta and the fixed 4h causal repair remain net-negative in every arm. The sticky mechanism reduces turnover, but the repaired matched Broad differences are `-5.97e-05` and `-9.02e-06`; it is cost-management behavior, not a Broad component increment.
- Held-out calibration qualification: seven of eight slopes are positive and preserve raw candidate weights; one Broad MLP slope is negative before the nonnegative constraint and is marked `CALIBRATION_FIT_DEGENERATE`. Intercepts do not change zero-net sticky weights. Degenerate arms stay in the denominator. Calibrated matched-net and delta-sleeve medians are positive only in selection, with 1/4 positive arms; stability medians are zero with 0/4 positive arms. Bias audit: `PASS`. Economic result: `BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED`.
- Liquidation supplier release: 762 Parquet partitions across 381 dates passed schema, count, primary-key, PIT-delay, and content-identity preflight. Of 500 symbols and 11,138,396 events, 464 linear USDT/USDC symbols with 11,101,810 events are eligible for source comparison. Nineteen inverse/delivery and seventeen unknown-semantics symbols remain notional-quarantined because the supplier's quantity-times-price value is not a qualified common notional for those contracts. This is ingress evidence only, not a research field admission or economic result.
- Bitfinex liquidation ingress: all 18 declared monthly bundles and 127 files reconcile internally, with 89,273 raw rows and 81,231 silver rows. This does not prove continuous source coverage: only 135/544 requested dates contain events, 17/18 months have at least seven trailing event-free days, 15/18 raw counts are page-boundary-like, and no request/page/cursor ledger exists. The USTF0 proxy has 55,195 rows but only 7.14 effective months and 4.39 effective symbols, with no price-label bridge or turnover observations. Status: `FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED` plus `DATA_ADEQUACY_UNDERPOWERED`; it cannot validate Binance/CryptoHFT or enter research.
- Binance raw provenance capture: the official `!forceOrder@arr` forward collector is active at `G:/AlphaFactory_CryptoData/raw/binance_force_order_ws_v1`. The latest committed prefix snapshot contains 887 valid records across 134 symbols and four hourly files with zero parse, hash, source, or forceOrder-contract failures. Capture began on 2026-07-18 after the supplier package ended on 2026-07-13, so current-package overlap is zero and stitching remains blocked.

## Active execution plan

1. Keep the CryptoHFT and Bitfinex releases quarantined and the independent Binance forward capture raw-only; do not join venues or sources by filename, symbol, or assumed notional semantics.
2. Run the existing overlap gate only when an independent historical archive or a supplier extension supplies at least 14 overlapping dates with the active capture. A pass only makes stitching eligible for a separate explicit activation decision.
3. After source compatibility, require the existing Data Adequacy Gate before any research use; the 2025-2026 release does not enter the current 2023H2/2024 train surface.
4. Treat the purged Broad replay as the current evidence. Do not spend more budget tuning its calibration, cost multiplier, or sticky threshold: held-out calibration passed its implementation audit but produced only 1/4 selection and 0/4 stability support. Preserve the information-level positive and report no component development increment.
5. Treat the verified 120-token consumer as two context-bound surfaces, not one merged training matrix; consumption admission does not satisfy Core3 model fit or economic admission.
6. Keep challenge, recent, May stress, forward evaluation, promotion, and cross-sprint memory closed. Raw forward data capture is permitted but does not authorize forward evaluation.

No large experiment is authorized merely by this plan.

## Blockers

- Historical aggTrades coverage is not yet equivalent to the 18-month observed-archive surface; the qualified Core3 slice has 3 assets, 4,368 hours, and 13,068 eligible observations.
- Core3 consumption is verified, but the fixed one-seed probe did not reduce training loss; stable model fit and incremental information remain unqualified.
- Existing external-paradigm samples lack independent evaluation power.
- The localized compositional mechanism remains challenge-unstable.
- The structured-proxy comparison lacks executed semantic matched controls and does not identify independent latent states.
- Broad added-field information is stable, but its gross strength is below tested 5 bps turnover costs under both the original full/control weight difference and two fixed delta-signal mappings.
- The purged, held-out calibration replay is implementation-qualified but economically unsupported: selection is positive in 1/4 matched arms and stability in 0/4, with one direction-degenerate Broad calibration arm.
- Bitfinex source-interval coverage is unverified and its effective months/symbols plus missing price-label and turnover bridges fail event-study Data Adequacy.
- The active Binance forceOrder capture starts after the current supplier release ends, so supplier/WS overlap compatibility is not yet qualified and stitching is blocked.

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

Run no further threshold, calibration, or sticky-mapping search on this Broad stack. Its single held-out calibration repair is complete and did not establish development increment. Mainline research should next use a genuinely lower-frequency or event-driven representation only after its own Data Adequacy preflight and frozen matched contract; this does not open formal performance search. Keep Bitfinex quarantined unless an independently qualified request/page ledger and price-label bridge arrive. Keep the Binance raw collector running independently and run the existing supplier overlap gate only after at least 14 common dates exist; do not stitch or admit any release before a gate pass and separate explicit activation decision.
