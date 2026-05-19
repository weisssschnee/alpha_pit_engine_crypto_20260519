# Alpha Pit Engine Crypto Line

Independent crypto AlphaFactory research repository.

This repo is intentionally separate from the CN-line repository. It contains crypto-specific method configs, scripts, reports, lightweight runtime manifests, and audit tables. It does not contain raw market data, silver/gold parquet panels, or append-only shadow telemetry.

Data root:

`G:\AlphaFactory_CryptoData`

## Current Evidence Status

Crypto line is not at CN-line proof maturity.

Current classification:

- `Core4`: 1h funding/basis/price research proof object.
- `FundingCore`: mandatory simple benchmark and research baseline.
- `A6 dry-shadow`: engineering telemetry only.
- `A7/A7B/A7C`: method validation gates currently hold alpha-shadow promotion.

Main blocking conclusions:

- A7.1 showed only 1 of 4 Core4 clusters beat its component baseline.
- A7.2 showed positive recent OOS but unacceptable drawdown and negative fresh-May behavior.
- A7B showed funding-only dominance risk.
- A7C showed FundingCore is stronger/simpler than Core4 as a benchmark, but still blocked by fresh-May loss and drawdown risk.

Do not promote to:

- paper trading
- live trading
- production strategy
- alpha shadow proof
- generator/reward proof

## Included

- `config/`: crypto AlphaFactory method and motif configs.
- `scripts/`: A1-A7C reproducible scripts.
- `reports/`: decision records and audit reports.
- `runtime/`: lightweight manifests, summaries, and audit tables.
- `cn_reference/`: selected CN-line reference code used only as method scaffolding.

## Excluded

- raw Binance files
- silver/gold parquet panels
- large return panels
- heavy residual time series
- append-only hourly shadow outputs

## Next Correct Work

Do not expand search yet.

Next audit:

`Funding time-semantics audit`

Purpose:

- Confirm `latest_known_funding_rate` availability timing.
- Explain why `wrong_lag_future_24h_diagnostic` is materially stronger than live-lag FundingCore.
- Verify funding payment treatment and feature/label alignment.
- Redesign future crypto reward around residual edge vs FundingCore, not raw funding-wrapper return.

