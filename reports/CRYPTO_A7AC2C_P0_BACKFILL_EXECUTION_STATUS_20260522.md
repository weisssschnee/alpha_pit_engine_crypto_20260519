# CRYPTO A7AC-2C P0 Backfill Execution Status

Generated: 2026-05-22 11:52 UTC

## Decision

`PASS_A7AC2C_P0B01_TO_P0B05_BACKFILL_EXECUTED_P0B06_RUNNING`

This is a data-line execution status only. It does not authorize formula search,
large search, alpha proof, shadow, paper, or live trading.

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

The 8 `not_available_404` rows are treated as listing/source availability gaps,
not checksum failures. They must be handled by the later listing/survivorship
policy before replay.

Manifest:

```text
G:\AlphaFactory_CryptoData\manifests\binance_vision_monthly_pool_manifest_a7ac_company_p0b01_b04_monthly_v3_20260522_194402.csv
```

Status:

```text
G:\AlphaFactory_CryptoData\reports\binance_vision_monthly_pool_status_a7ac_company_p0b01_b04_monthly_v3_20260522_194402.json
```

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

Retry status:

```text
G:\AlphaFactory_CryptoData\reports\binance_funding_rate_pool_status_a7ac_company_p0b05_funding_retry_20260522_194314.json
```

Retry manifest:

```text
G:\AlphaFactory_CryptoData\manifests\binance_funding_rate_pool_manifest_a7ac_company_p0b05_funding_retry_20260522_194314.csv
```

## Running

### P0B06 Binance metrics daily

Company machine run:

```text
tag: a7ac_company_top36_metrics_20260522_192315
symbols: 36 primary core48 additions
max_concurrent: 12
status at last check: running 12, pending 24, completed 0, failed 0
```

Local machine run:

```text
tag: a7ac_primary_missing_now_20260522_192428
symbols: 23 non-core39 primary additions
max_concurrent: 8
status at last check: completed 7, failed 1, running 8, pending 7
```

The single local failure is `1INCHUSDT` and should be retried at low concurrency
after the current local pool finishes. This is consistent with the earlier
metrics API/checksum transient failure pattern.

## Code Changes

Committed runners:

```text
5012ba6 add retry-safe binance metrics symbol pool runner
aa55ca0 add expanded universe vision and funding pool runners
798f913 treat vision monthly 404 as listing gap
```

## Remaining Work

1. Let P0B06 metrics complete.
2. Retry any P0B06 transient failures with low concurrency.
3. Build the expanded 1h panel only after P0B06 is closed.
4. Run A7AC-2 full source trace and panel integrity audit.
5. Run A7AC-3 listing/survivorship policy before any replay/search.

## Authorization

```text
authorizes_data_line_continuation: true
authorizes_formula_search: false
authorizes_large_search: false
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false
```
