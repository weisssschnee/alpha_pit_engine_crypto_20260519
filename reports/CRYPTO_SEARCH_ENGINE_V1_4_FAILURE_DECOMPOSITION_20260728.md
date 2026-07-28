# Crypto Search Engine V1.4 Failure Decomposition

- Audit source: `16fc1feabc79f711d4b7b728eac2c2b9d00f91e5`.
- Scope: committed V1.4 ledger/archive and aligned-carrier target metadata only; candidate evaluations: `0`.
- Stage-B rows: `1200`; near misses at reward >= `-1.0`: `3`.
- Persisted hierarchical worst-axis attribution: `{'AB_MINUS_A': 261, 'AB_MINUS_B': 174, 'ABC_MINUS_AB': 165}`.
- Final-increment gross positive: `666/1200`; net positive: `26/1200`; cost sign-killed: `640/1200`.
- Target venue shares: `{'bybit': 0.8850256904194997, 'hyperliquid_futures': 0.0740997688591927, 'okx_futures': 0.0408745407213075}`; `126/144` assets use multiple priority venues.
- Target/execution finding: Binance aggTrades is evaluated against a lexicographic first-finite Bybit/Hyperliquid/OKX mark target, with no qualified unified tradable venue or venue-specific 5 bps bridge.
- Persistence finding: V1.4 did not write standalone A/B/AB/ABC economics, component constraint margins, monthly waterfalls, or time-block rewards. These are `NOT_RECONSTRUCTIBLE` without market reevaluation.
- Decision: `HOLD_ADAPTIVE_TARGET_EXECUTION_AND_TURNOVER_REPAIR_FIRST`. Adaptive V1.4b and operator-basis expansion remain unauthorized.

## Bias Audit

- Factor: V1.4 binary and hierarchical candidate population; no candidate is promoted.
- Run/experiment_id: `CRYPTO_SEARCH_ENGINE_V1_4_EXISTING_LEDGER_FAILURE_DECOMPOSITION`.
- Data source and universe: fixed-retrospective aligned OI/mark ranks51-200 plus Binance aggTrades Top200 carrier; dynamic eligible intersection; 144 assets ever eligible.
- Frequency and horizon: hourly signal grid; 1h and 4h labels with t+2 execution delay.
- IS window: 2025-08-29 07:00 UTC through 2026-07-01 00:00 UTC.
- OOS window: none.
- OOS sample grade: `NONE`.
- Cost model: fixed 5 bps full-L1 turnover; venue/execution consistency unqualified.
- Turnover: 1h mean `0.777204`; 4h mean `0.226663`.
- Benchmark: matched A, B, AB and ABC controls under the original evaluator; only partial waterfall persisted.
- Discovery status: post-hoc existing-ledger audit.

### Findings

- Look-ahead: engineering lag contract is explicit; no sealed or forward role was read by this audit.
- Survivorship: fixed delivered cohort and historical PIT-universe limitations remain; unsuitable for promotion.
- Date alignment: signal-to-label lag is explicit, but t+2 mark is not a qualified first tradable execution price.
- Label horizon: 1h/4h overlap was handled by the original Newey-West contract; per-time-block stability was not persisted.
- Costs: 5 bps is generic and is not tied to Bybit, Hyperliquid, OKX, or a Binance execution bridge.
- Turnover: cost sign-killed 640 of 666 gross-positive final increments; 1h is materially worse than 4h.
- Multi-window stability: `NOT_RECONSTRUCTIBLE`; one full-window reward was persisted per candidate.
- Replay vs discovery: post-hoc decomposition only; it cannot count as a new discovery.

### Blocking Issues

- Binance order flow is labelled with a non-Binance, availability-dependent mark target.
- 126/144 assets use more than one priority target venue; some label endpoints cross venues.
- Standalone A/B/AB/ABC economics, component constraint names, and monthly waterfalls are absent.
- The near-miss rate is below the frozen adaptive threshold.

### Decision

`HOLD_RESEARCH`

### Required Next Action

- Freeze a tradable venue-specific target/execution/cost contract.
- Audit mapping, holding period and turnover using that contract before field or operator expansion.
- Do not authorize CEM/Evolution, operator-basis expansion, OOS, or promotion from this audit.
