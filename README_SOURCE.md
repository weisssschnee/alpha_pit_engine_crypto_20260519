# AlphaFactory Crypto Workspace

This directory is the isolated crypto alpha research workspace.

It intentionally does not modify the CN equity project. CN files copied under
`cn_reference/` are reference material only.

## Current Data Root

```text
G:\AlphaFactory_CryptoData
```

## Primary Goal

Prepare a crypto alpha factory line using the existing raw Binance data:

- futures core12 Binance Vision klines / mark / index / premium data
- spot core6 Binance Vision klines
- fundingRate core12 long history
- positioning core12 recent 29d 5m data

## Evidence Boundary

Positioning data is recent-only and must not enter 2024-2026 historical
backtests as if it existed historically.

FundingRate and Binance Vision historical files can enter historical backtests
after bronze normalization and timestamp-unit checks.

## Copied CN References

```text
cn_reference/formula_gen_v2/
cn_reference/runtime_refs/
```

These provide structural references:

- role/motif formula generation
- paired ablation
- regime-gated replay concepts
- champion/cluster selection flow

They are not executable crypto production code without adaptation.

## First Commands

Run preflight:

```powershell
py G:\AlphaFactory_CryptoData\alphafactory_crypto\scripts\crypto_alpha_preflight.py
```

Expected outputs:

```text
G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\CRYPTO_ALPHAFACTORY_PREFLIGHT_20260519.md
G:\AlphaFactory_CryptoData\alphafactory_crypto\reports\crypto_alphafactory_preflight_20260519.json
```

Next build step after preflight:

```text
bronze normalization -> silver 1h/5m state panel -> baseline crypto alpha smoke
```
