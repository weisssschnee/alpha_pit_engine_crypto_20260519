# CRYPTO A7SOURCE-3 Publication Semantics Research

Generated: `2026-07-03`

## Decision

`HOLD_A7SOURCE3_VENDOR_PUBLICATION_SLA_NOT_PROVEN_BUT_SOURCE_LAG_SURVIVES`

This is a source-timing and publication-semantics gate for A7SEARCH6 June survivors. It is not an alpha proof and does not authorize live, paper, shadow, or large formula search.

## Research Question

Whether the remaining non-price fields in current A7SEARCH6 survivors are safe enough to use as feature inputs:

- `open_interest_last`
- `open_interest_value_last`
- `top_long_short_account_ratio_last`
- `funding_rate_delta_state_24h`
- regime/state fields such as `stress_proxy_state`

## Evidence Reviewed

- A7SOURCE-1 field timing proof.
- A7SOURCE-2 source-lag retest.
- Local 2026 recent patch field contract.
- Pre-2024 complete replay builder source semantics.
- Existing A7S1 Binance metrics source trace.
- Binance USD-M Futures public API documentation for open interest statistics and funding-rate history.
- Binance USD-M Futures public API documentation for taker buy/sell volume and top-trader long/short account/position ratios.

Official documentation confirms that Binance statistics endpoints expose event or observation timestamps such as `timestamp` and `fundingTime`, but the docs do not provide a hard publication-delay SLA for the archived/statistics values. Therefore, the correct conservative policy is not "field is invalid"; it is "field requires source-lag enforcement unless publication time is independently carried."

Official source references:

- Binance Open Interest Statistics: `GET /futures/data/openInterestHist`, `period`, and response `timestamp`.
- Binance Funding Rate History: `GET /fapi/v1/fundingRate`, response `fundingTime`.
- Binance Taker Buy/Sell Volume: `GET /futures/data/takerlongshortRatio`, `period`, and response `timestamp`.
- Binance Top Trader Long/Short Account Ratio: `GET /futures/data/topLongShortAccountRatio`, `period`, and response `timestamp`.
- Binance Top Trader Long/Short Position Ratio: `GET /futures/data/topLongShortPositionRatio`, `period`, and response `timestamp`.

## Current Field-Family Classification

| field_family | fields | current_status | reason | next_policy |
|:--|:--|:--|:--|:--|
| basis_premium | `mark_index_basis_bps`, `premium_close_bps` | `PASS_CONTROLLED_EXPERIMENT` | Bar-close fields with controlled experiment pass; final proof still needs official checksum/source trace. | Allowed for controlled research with standard bar-close timing. |
| liquidity | `quote_volume_z_168h` | `PASS_CONTROLLED_CONTRACT` | Derived from bar OHLCV volume with standard bar-close timing. | Allowed for controlled research. |
| taker_flow | `taker_buy_sell_volume_ratio_last` | `PASS_CONTROLLED_CONTRACT` | Current accepted formulas did not show unknown/forbidden use; source still follows statistics semantics. | Allowed with stricter source trace before final proof. |
| open_interest | `open_interest_last`, `open_interest_value_last` | `SOURCE_LAG_REQUIRED` | Binance metrics `create_time`/API `timestamp` is an observation timestamp; vendor publication lag is not proven for full 498 recent patch. | Search/reward must use source-lag variants or prove publication availability. |
| positioning | `top_long_short_account_ratio_last` | `SOURCE_LAG_REQUIRED_AND_FRAGILE` | Same publication-lag problem as metrics. A7SOURCE-2 lag retest failed for the OI/positioning formula. | Do not promote current positioning formula; require source-lag survival before use. |
| funding_state | `funding_rate_delta_state_24h` | `EVENT_PUBLICATION_REQUIRED` | Funding state is mechanically past-only, but funding event publication timestamp is not carried into reward rows. | Use source-lag variant until event publication time is attached. |
| regime_state | `stress_proxy_state` | `THRESHOLD_LINEAGE_REQUIRED` | Current June diagnostic results were empty/NaN and threshold lineage is not proven. | Hold from search until state lineage and non-empty response are proven. |

## A7SOURCE-2 Retest Implications

Two current candidates survive a conservative signal delay:

| formula | source_lag_result | interpretation |
|:--|:--|:--|
| `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` | 1h and 2h source-lag survive; 4h decays but remains positive. | Keep as diagnostic source-lag survivor; not alpha proof. |
| `Mul(open_interest_last,Mean(premium_close_bps,504))` | 1h, 2h, and 4h source-lag are stable but weak. | Keep as weak source-lag survivor. |
| `SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))` | 1h source-lag turns negative. | Treat as source-lag fragile; block from next queue. |

## Bias Audit

- Factor: A7SEARCH6 June survivors using OI, funding state, premium/basis, and positioning fields.
- Run/experiment_id: A7SOURCE-3 publication semantics research.
- Data source and universe: Binance 498 1h research panel plus recent patch and replay builders.
- Frequency and horizon: 1h features, 4h and 24h labels in current survivors.
- IS/OOS windows: Uses previously generated A7SEARCH6 train/OOS/June diagnostics; this report audits source timing only.
- Cost model: Not evaluated here.
- Turnover: Not evaluated here.
- Discovery status: post-hoc audit of discovered candidates.

### Findings

- Look-ahead: No direct future-field proof was found in the current accepted formulas, but OI/positioning/funding publication timing remains unproven.
- Survivorship: Not re-audited in this gate.
- Date alignment: Current builders use 1h bucket timestamps and conservative `timestamp + 1h` availability, but metrics/funding official publication delay is not independently carried.
- Label horizon: Not re-audited in this gate.
- Costs: Not evaluated here.
- Turnover: Not evaluated here.
- Multi-window stability: A7SOURCE-2 source-lag retest is positive for two candidates and negative for the positioning candidate.
- Replay vs discovery: This is a validation/audit step, not new discovery.

### Blocking Issues

- Vendor publication SLA is not proven for Binance metrics/statistics fields.
- Funding event publication timestamp is not carried through the reward rows.
- Recent 498 patch still has official checksum/source-trace pending for final proof.
- Regime/state fields need threshold lineage and non-empty response proof.

### Decision

`HOLD_RESEARCH`

## Required Next Action

1. Add a fail-closed field policy:
   - `SOURCE_LAG_REQUIRED`: OI, OI value, positioning, funding-state fields.
   - `SOURCE_LAG_FRAGILE_BLOCK`: current OI/positioning survivor.
   - `CONTROLLED_ALLOWED`: basis/premium, liquidity, bar-close price/volume fields.
2. Next search queue must use source-lag-enforced versions for OI/funding/positioning fields.
3. Reward gate must record source-lag metrics and reject candidates that only work at same-bar timing.
4. Final proof still requires official checksum/source trace and event-publication lineage.

## Resulting Authorization

Allowed:

- Controlled research using source-lag variants.
- Search/reward experiments that enforce lag policy in the candidate queue.
- Further source-trace/checksum audit.

Blocked:

- Treating OI/positioning/funding-state candidates as proven clean without lag.
- Promoting source-lag-fragile formulas.
- Alpha proof, shadow, paper, or live.
