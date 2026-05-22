# CRYPTO A7AC-2D Primary Additions 1h Panel Build

Generated: 2026-05-22 13:39 UTC

## Decision

`PASS_A7AC2D_PRIMARY_ADDITIONS_1H_PANEL_BUILT`

This is a data-line panel build result. It does not authorize replay, formula
search, large search, alpha proof, shadow, paper, or live trading.

## Output

```text
G:\AlphaFactory_CryptoData\gold\panels\crypto_primary_core48_additions_1h_v1.parquet
```

Build host:

```text
company machine
task_id: job_20260522_212130_65b6e4
```

Summary:

```text
rows: 733,452
symbols: 36
columns: 84
timestamp_min: 2024-01-01 00:00 UTC
timestamp_max: 2026-04-30 23:00 UTC
duplicate (timestamp, symbol) keys: 0
file_error_count: 0
file size: ~292.82 MB
```

The panel includes the 36 primary core48 additions from A7AC and uses:

```text
P0B01 futures trade klines 1m -> 1h
P0B02 mark price klines 1m -> 1h
P0B03 index price klines 1m -> 1h
P0B04 premium index klines 1m -> 1h
P0B05 funding rate backward-asof join
```

## Expected Caveats

```text
BOMEUSDT has fewer rows because Binance Vision source starts after 2024-02.
2026-05 market/basis monthly data is not included because Binance Vision monthly source is only closed through 2026-04.
Metrics features are built separately at:
G:\AlphaFactory_CryptoData\gold\features\binance_metrics_primary_core48_additions_1h_features_v1.parquet
```

## Runtime Artifacts

```text
runtime/a7ac2d_primary_additions_panel_build/crypto_primary_core48_additions_1h_v1_20260522.json
runtime/a7ac2d_primary_additions_panel_build/crypto_primary_core48_additions_1h_v1_20260522.md
```

## Authorization

```text
authorizes_panel_integrity_audit: true
authorizes_formula_search: false
authorizes_large_search: false
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false
```

## Next

1. Run A7AC-3 listing/survivorship policy for BOMEUSDT and any source-specific availability gaps.
2. Merge or align the primary additions market/basis panel with the metrics feature file.
3. Run expanded panel integrity audit before any replay/search.
