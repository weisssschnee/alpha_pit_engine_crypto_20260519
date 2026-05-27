# CRYPTO A7AC-2E Primary Additions With Metrics Panel

Generated: 2026-05-22 13:46 UTC

## Decision

`PASS_A7AC2E_PRIMARY_ADDITIONS_WITH_METRICS_PANEL_BUILT`

This is a data-line panel merge result. It does not authorize replay, formula
search, large search, alpha proof, shadow, paper, or live trading.

## Output

```text
G:\AlphaFactory_CryptoData\gold\panels\crypto_primary_core48_additions_1h_with_metrics_v1.parquet
```

Summary:

```text
rows: 733,452
symbols: 36
columns: 119
timestamp_min: 2024-01-01 00:00 UTC
timestamp_max: 2026-04-30 23:00 UTC
duplicate (timestamp, symbol) keys: 0
low open-interest coverage symbols: []
```

The panel left-joins:

```text
market/basis/funding:
  G:\AlphaFactory_CryptoData\gold\panels\crypto_primary_core48_additions_1h_v1.parquet

metrics:
  G:\AlphaFactory_CryptoData\gold\features\binance_metrics_primary_core48_additions_1h_features_v1.parquet
```

Independent metrics source fields:

```text
open_interest
open_interest_value
global_long_short_account_ratio
top_long_short_account_ratio
top_long_short_position_ratio
taker_buy_sell_volume_ratio
```

## Runtime Artifacts

```text
runtime/a7ac2e_primary_additions_with_metrics_panel/crypto_primary_core48_additions_1h_with_metrics_v1_20260522.json
runtime/a7ac2e_primary_additions_with_metrics_panel/crypto_primary_core48_additions_1h_with_metrics_v1_20260522.md
runtime/a7ac2e_primary_additions_with_metrics_panel/crypto_primary_core48_additions_1h_with_metrics_v1_symbol_coverage_20260522.csv
```

## Caveats

```text
BOMEUSDT starts after the 2024-01/02 listing/source gap.
Market/basis monthly source is currently through 2026-04.
This is primary additions only, not yet a full core48 panel with existing core12.
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

1. Build/align the full core48 panel by combining existing core12 with these 36 primary additions.
2. Run listing/survivorship and panel integrity audits.
3. Only then consider controlled replay/search.
