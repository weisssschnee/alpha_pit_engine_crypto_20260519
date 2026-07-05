# Crypto Deprecated Active Tree Archive

## Decision

PASS_CRYPTO_DEPRECATED_ACTIVE_TREE_ARCHIVE_20260527

## Scope

Deprecated crypto exploration stages were removed from the active `scripts`, `reports`, and `runtime` trees and retained under:

```text
archive/deprecated_crypto_a7_20260527
```

The original 2026-05-27 action was an archive move, not evidence deletion.

Update 2026-07-05: bulky deprecated runtime payloads were removed from the active git checkout under the artifact lifecycle cleanup policy. Deprecated archived scripts and reports remain in `archive/deprecated_crypto_a7_20260527`; removed runtime payloads remain recoverable from git history if needed.

## Counts

```text
scripts archived: 107
reports archived: 181
runtime directories archived: 116
total archived entries: 404
```

Current retained archive payload after 2026-07-05 cleanup:

```text
scripts retained: 107
reports retained: 181
runtime payload retained in active checkout: false
runtime recovery path: git history before cleanup commit
```

## Active Line Retained

```text
A7AJ / A7AK / A7AL:
  universe498, latent state, top498 alpha-search contract

A7AO / A7AP:
  OKX/Binance cross-exchange acceptance and repaired overlay diagnostics

A7AR:
  CN engine inheritance, formula adapter, feature algebra, fresh memory

A7S / A7U:
  data contracts, metrics/source trace, aggTrades source trace

A7T:
  forward telemetry contracts

A7W:
  post-source-trace data-line/signal-line boundary
```

## Archived Families

```text
A1-A6:
  early core12/Core4 method and dry-shadow chain

A7B-A7H:
  funding and non-funding residual negative-result chain

A7I-A7R:
  old small-generator, A7M/A7O/A7P search-space experiments, route reset

A7AA-A7AG:
  pre-top498 core48/core39/core3 source and smoke stages

A7V/A7X/A7Y/A7Z:
  failed aggTrades activity/liquidity and interaction clue chain
```

## Guardrails

```text
CN repo touched: false
CN memory inherited: false
Alpha proof authorized: false
Shadow/paper/live authorized: false
```

The current active execution path is A7AR -> A7AL, with data support from A7AJ/A7AK/A7S/A7U/A7AO/A7AP.
