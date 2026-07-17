# Crypto liquidation supplier ingress

This is source ingress and compatibility evidence only. It is not research, OOS, or economic evidence.

- Source SHA: `d64a783dac4c148d1924f76acb7b8a80cbcc7f1a`
- Release: `CRYPTOHFT_LIQUIDATIONS_20250628_20260713`
- Preflight: `QUALIFIED_QUARANTINED`
- Stitching: `STITCHING_BLOCKED_NO_WS_OVERLAP_INPUT`
- Partition files: 762
- Events: 11,138,396
- Symbols: 500
- Range: 2025-06-28T05:00:00+00:00 through 2026-07-13T23:00:00+00:00

## Contract classes

| contract_class             |   symbols |   hourly_rows |   events |   raw_supplier_notional |   maximum_raw_event_notional | notional_comparable   |
|:---------------------------|----------:|--------------:|---------:|------------------------:|-----------------------------:|:----------------------|
| INVERSE_OR_DELIVERY        |        19 |           634 |     1588 |             8.92139e+09 |                  7.63584e+08 | False                 |
| LINEAR_QUOTE_MARGIN        |       464 |       1292554 | 11101810 |             3.20402e+10 |                  9.81006e+07 | True                  |
| UNKNOWN_CONTRACT_SEMANTICS |        17 |         11662 |    34998 |             1.06076e+08 |                  1.66886e+06 | False                 |

Only symbols matching `^[A-Z0-9]+(?:USDT|USDC)$` are notional-comparable. Inverse, delivery, and unknown contracts remain quarantined until a multiplier contract exists.

## Overlap gate

- Status: `STITCHING_BLOCKED_NO_WS_OVERLAP_INPUT`
- Comparison pass: `False`
- Automatic stitching allowed: `False`

A passing comparison only makes the sources eligible for an explicit activation decision. It never joins them automatically.

## Boundaries

The release contains 2025-2026 observations and is quarantined from research consumers. No challenge, forward, recent, May-stress, promotion, performance-search, or adaptive-memory boundary was opened.
