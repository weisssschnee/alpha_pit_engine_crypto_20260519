# Bitfinex liquidation ingress preflight

## Decision

- File/aggregation integrity: `PASS`
- Ingress status: `FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED`
- Event Data Adequacy: `DATA_ADEQUACY_UNDERPOWERED`
- Research admission: `False`
- Binance/CryptoHFT reference use: `PROHIBITED`

The directory contains all 18 declared monthly bundles and its silver/gold layers reconcile internally. It does not contain a request/page ledger proving that event-free portions of each requested month were queried. Therefore `complete` is accepted only as downloader/file completion, not as verified continuous source coverage.

## Observed data

- Requested period: `2024-01-01` to `2025-06-27` (544 days)
- Files: `127`; bundle SHA256: `750016FF02F26C161F24C510549FEFC57CD803E1C9F4A8AB1279BD094E4762ED`
- Raw rows: `89,273`; silver matched rows: `81,231`
- All-symbol active event dates: `135` (24.8% of requested calendar days)
- USTF0 proxy subset: `55,195` rows, `68` symbols, `135` active dates
- Concentration-adjusted effective months/symbols: `7.14` / `4.39`
- Top-symbol event share: `40.6%`
- Months with at least seven trailing event-free days: `17/18`
- Months with page-boundary-like raw counts: `15/18`

An event-free tail is not by itself proof of a missing download. In combination with absent request receipts and page-boundary-like counts, it prevents a claim of continuous interval coverage.

## Data Adequacy gaps

- `source_interval_completeness`
- `effective_independent_months`
- `effective_cross_sectional_symbols`
- `price_label_match_ratio`
- `turnover_observations`

The package has no linked price/label bridge and no authorized portfolio mapping, so it cannot yet support the proposed large-event return study or turnover/cost evaluation.

## Semantic boundary

Only symbols matching `t...F0:USTF0` are retained as an event-study proxy subset. Even there, quantity-times-price remains a supplier-derived quote proxy, not a universally qualified common USD notional. Test, legacy, cross-quote, and unknown symbols remain quarantined.

Bitfinex historical REST events are venue-specific and cannot validate Binance WebSocket or CryptoHFT coverage. No stitching, research admission, economic evaluation, sealed read, or promotion boundary was opened.

## Reproduction

```powershell
python scripts/crypto_bitfinex_liquidation_ingress.py
```

- Run identity SHA256: `DB8E56C85ABD2008ECF6F97E046ED00A2CCC571B2C517BCACA9F786CEAF5320A`
- Source SHA: `7a5dfee6a7d1097ca37b06d85f3c3882a8ece388` (dirty at execution: `False`)
- Runtime seconds: `7.1`
