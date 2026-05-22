# CRYPTO A7AC-2C P0 Backfill Execution Status

Generated: 2026-05-22 13:10 UTC

## Decision

`PASS_A7AC2C_EFFECTIVE_P0_BACKFILL_SOURCE_COVERAGE_COMPLETE_WITH_LISTING_GAPS`

This is a data-line execution/source-coverage status only. It does not authorize
formula search, large search, alpha proof, shadow, paper, or live trading.

## Effective Result

```text
P0B01-P0B04 monthly 1m Binance Vision sources: complete with listing gaps
P0B05 funding rate: complete after retry
P0B06 Binance daily metrics: source trace complete by effective local file coverage
primary additions ready: 36 / 36
blockers: []
```

## Completed

### P0B01-P0B04 Binance Vision monthly 1m sources

Source families:

- `klines`
- `markPriceKlines`
- `indexPriceKlines`
- `premiumIndexKlines`

Scope:

```text
symbols: 36 primary core48 additions
range: 2024-01 through 2026-04
interval: 1m
total jobs: 4,032
runner: run_binance_vision_monthly_pool.py
execution host: company machine
```

Result:

```text
decision: PASS_A7AC2C_BINANCE_VISION_MONTHLY_POOL_COMPLETED_WITH_LISTING_GAPS
completed: 4,032 / 4,032
downloaded_checksum_ok: 2,870
exists_checksum_ok: 1,154
not_available_404: 8
checksum/integrity failures: 0
```

The 8 `not_available_404` rows are `BOMEUSDT` 2024-01/2024-02 across the four
monthly source families. They are listing/source-availability gaps, not checksum
or integrity failures. They must be handled by A7AC-3 listing/survivorship policy
before replay.

### P0B05 funding rate

Scope:

```text
symbols: 36 primary core48 additions
range: 2024-01-01 through 2026-05-21
runner: run_binance_funding_rate_pool.py
execution host: company machine
```

Result:

```text
initial run: 27 ok, 9 transient API errors
retry run: 9 ok, 0 failed
effective result: 36 / 36 ok
```

### P0B06 Binance metrics daily

The final source-trace state is based on effective local raw/silver file
coverage, not stale transient pool-run failures.

Result:

```text
primary additions ready: 36 / 36
silver months: 29 for 35 symbols
BOMEUSDT silver months: 27, listing/metrics availability starts 2024-03
feature-density warnings: 1 symbol, LRCUSDT sparse official vendor rows in 2026-03/04/05
```

The company-machine top36 metrics pool was stopped after redundant transient
failures because local file coverage had already closed the source trace.

## New Gold Metrics Feature File

Built from existing silver 5m metrics, without additional download:

```text
G:\AlphaFactory_CryptoData\gold\features\binance_metrics_primary_core48_additions_1h_features_v1.parquet
rows: 749,934
symbols: 36
timestamp range: 2024-01-01 00:00 UTC through 2026-05-22 00:00 UTC
size: ~168.64 MB
```

Coverage caveats:

```text
BOMEUSDT starts 2024-03-16 12:00 UTC due listing/source availability.
LRCUSDT metrics are sparse from 2026-03 onward and should carry a vendor-density warning.
```

## Audit Artifacts

```text
reports/CRYPTO_A7AC2C_EFFECTIVE_BACKFILL_COVERAGE_AUDIT_20260522.md
runtime/a7ac2c_effective_backfill_coverage/a7ac2c_effective_backfill_manifest.json
runtime/a7ac2c_effective_backfill_coverage/a7ac2c_monthly_source_summary.csv
runtime/a7ac2c_effective_backfill_coverage/a7ac2c_funding_source_summary.csv
runtime/a7ac2c_effective_backfill_coverage/a7ac2c_metrics_source_summary.csv
runtime/a7ac2c_effective_backfill_coverage/a7ac2c_listing_gaps.csv
```

## Authorization

```text
authorizes_panel_build: true
authorizes_formula_search: false
authorizes_large_search: false
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false
```

## Remaining Work

1. Build expanded market/funding 1h panel from P0B01-P0B05 sources.
2. Run A7AC-3 listing/survivorship policy for `BOMEUSDT` source gaps and LRCUSDT metrics density warnings.
3. Run expanded panel integrity audit before replay/search.
